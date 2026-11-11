"""Parser for Cisco IOS-style configs (routers and switches) into the neutral model.

Sub-commands must be indented by a space, as in 'show running-config'.
"""
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Interface, IPv4Network

from netaudit.model import AclRule, Device, Interface, Ospf, StaticRoute, Unparsed

# Top-level lines that are harmless boilerplate, not network behavior.
IGNORED_PREFIXES = ("version ", "service ", "no service ")


def _parse_vlan_list(text: str) -> set[int]:
    vlans = set()
    for part in text.split(","):
        if "-" in part:
            low, high = part.split("-")
            vlans.update(range(int(low), int(high) + 1))
        else:
            vlans.add(int(part))
    return vlans


def _trunk_allowed(iface: Interface, words: list[str], line: str) -> None:
    what = words[4]
    if what == "all":
        iface.trunk_allowed = None
    elif what == "none":
        iface.trunk_allowed = set()
    elif what == "add":
        if iface.trunk_allowed is not None:  # adding to "all" changes nothing
            iface.trunk_allowed |= _parse_vlan_list(words[5])
    elif what in ("remove", "except"):
        raise ValueError(f"unsupported command: {line}")
    else:
        iface.trunk_allowed = _parse_vlan_list(what)


def _wildcard_to_prefix(address: str, wildcard: str) -> str:
    """'10.0.12.0' + '0.0.0.3' -> '10.0.12.0/30'."""
    bits = int(IPv4Address(wildcard))
    if bits & (bits + 1):  # a usable wildcard looks like 0...01...1
        raise ValueError(f"unsupported wildcard mask: {wildcard}")
    return str(IPv4Network(f"{address}/{32 - bits.bit_length()}", strict=False))


def _static_route(words: list[str]) -> StaticRoute | None:
    """'ip route NETWORK MASK TARGET'; None for forms we do not support."""
    if len(words) != 5:
        return None
    prefix = IPv4Network(f"{words[2]}/{words[3]}", strict=False)
    try:
        return StaticRoute(prefix, next_hop=IPv4Address(words[4]))
    except ValueError:
        return StaticRoute(prefix, interface=words[4])


@dataclass
class _AclSection:
    """Marks 'we are inside ip access-list ...' while reading its indented rules."""
    name: str
    extended: bool


def _operand(words: list[str], i: int) -> tuple[str, int] | None:
    """Read 'any', 'host A' or 'A WILDCARD' at words[i]; return (text, next index)."""
    if i >= len(words):
        return None
    if words[i] == "any":
        return "any", i + 1
    if words[i] == "host" and i + 1 < len(words):
        return f"host {words[i + 1]}", i + 2
    try:
        IPv4Address(words[i])
    except ValueError:
        return None
    if i + 1 < len(words):
        try:
            IPv4Address(words[i + 1])
            return f"{words[i]} {words[i + 1]}", i + 2
        except ValueError:
            pass
    return words[i], i + 1  # a lone address in a standard ACL means that one host


def _skip_ports(words: list[str], i: int) -> int:
    """Step over a port test such as 'eq 80' or 'range 20 21'; ports are not checked yet."""
    if i < len(words) and words[i] in ("eq", "neq", "gt", "lt"):
        return i + 2
    if i < len(words) and words[i] == "range":
        return i + 3
    return i


def _acl_rule(words: list[str], extended: bool) -> AclRule | None:
    """'permit|deny ...' -> AclRule; None for forms we do not support."""
    if words and words[0].isdigit():
        words = words[1:]  # drop a sequence number
    if len(words) < 2 or words[0] not in ("permit", "deny"):
        return None
    first = _operand(words, 2 if extended else 1)
    if first is None:
        return None
    source, i = first
    protocol, destination = "", ""
    if extended:
        protocol = words[1]
        second = _operand(words, _skip_ports(words, i))
        if second is None:
            return None
        destination, i = second
        i = _skip_ports(words, i)
    if any(w not in ("log", "established") for w in words[i:]):
        return None
    return AclRule(words[0], protocol, source, destination, " ".join(words))


def parse_ios(text: str) -> Device:
    device = Device()
    # section: a VLAN id (int), an Interface, an Ospf, or the header (str) of a block we skip
    section = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("!"):
            continue
        words = line.split()
        if not raw.startswith(" "):  # a top-level line ends the previous block
            section = None
            if words[0] == "hostname":
                device.hostname = words[1]
            elif words[0] == "vlan" and len(words) == 2:
                section = int(words[1])
                device.vlans.setdefault(section, "")
            elif words[0] == "interface":
                if words[1] == "range":
                    raise ValueError(
                        "'interface range' is not supported; use the running-config, "
                        "which lists interfaces one by one"
                    )
                section = Interface(name=words[1])
                device.interfaces[section.name] = section
            elif words[:2] == ["router", "ospf"]:
                device.ospf = Ospf()
                section = device.ospf
            elif words[:2] == ["ip", "access-list"] and len(words) == 4 and words[2] in ("standard", "extended"):
                section = _AclSection(words[3], words[2] == "extended")
                device.acls.setdefault(section.name, [])
            elif words[0] == "access-list" and len(words) >= 4 and words[1].isdigit():
                if words[2] != "remark":
                    number = int(words[1])
                    extended = 100 <= number <= 199 or 2000 <= number <= 2699
                    rule = _acl_rule(words[2:], extended)
                    if rule is None:
                        device.unparsed.append(Unparsed(line, ""))
                    else:
                        device.acls.setdefault(words[1], []).append(rule)
            elif words[:2] == ["ip", "route"]:
                try:
                    route = _static_route(words)
                except ValueError:
                    route = None
                if route is None:
                    device.unparsed.append(Unparsed(line, ""))
                else:
                    device.static_routes.append(route)
            elif words[0] == "line":
                section = line  # inner lines are filed under this header
            elif line == "end" or line.startswith(IGNORED_PREFIXES):
                pass
            else:
                device.unparsed.append(Unparsed(line, ""))
                section = line  # indented lines below are filed under this header
        elif isinstance(section, int):
            if words[0] == "name":
                device.vlans[section] = words[1]
            else:
                device.unparsed.append(Unparsed(line, f"vlan {section}"))
        elif isinstance(section, Interface):
            if line.startswith("switchport mode "):
                section.switchport_mode = words[2]
            elif line.startswith("switchport access vlan "):
                section.access_vlan = int(words[3])
            elif line.startswith("switchport trunk native vlan "):
                section.native_vlan = int(words[4])
            elif line.startswith("switchport trunk allowed vlan "):
                _trunk_allowed(section, words, line)
            elif line.startswith("ip address ") and len(words) == 4:
                section.ip = IPv4Interface(f"{words[2]}/{words[3]}")
            elif line == "no ip address":
                section.ip = None
            elif line.startswith("ip ospf network "):
                section.ospf_network = words[3]
            elif line == "shutdown":
                section.shutdown = True
            elif line == "no shutdown":
                section.shutdown = False
            elif line.startswith("ip access-group ") and len(words) == 4 and words[3] in ("in", "out"):
                if words[3] == "in":
                    section.acl_in = words[2]
                else:
                    section.acl_out = words[2]
            elif line in ("duplex auto", "speed auto"):
                pass  # the defaults
            elif line.startswith("description "):
                pass
            else:
                device.unparsed.append(Unparsed(line, f"interface {section.name}"))
        elif isinstance(section, Ospf):
            known = True
            if words[0] == "router-id" or line.startswith("ospf router-id "):
                section.router_id = words[-1]
            elif words[0] == "network" and len(words) == 5 and words[3] == "area":
                try:
                    prefix = _wildcard_to_prefix(words[1], words[2])
                    section.networks.append((prefix, words[4]))
                except ValueError:
                    known = False
            elif line.startswith("log-adjacency-changes"):
                pass
            else:
                known = False
            if not known:
                device.unparsed.append(Unparsed(line, "router ospf"))
        elif isinstance(section, _AclSection):
            if words[0] != "remark":
                rule = _acl_rule(words, section.extended)
                if rule is None:
                    device.unparsed.append(Unparsed(line, f"ip access-list {section.name}"))
                else:
                    device.acls[section.name].append(rule)
        elif isinstance(section, str):
            device.unparsed.append(Unparsed(line, section))
        else:
            device.unparsed.append(Unparsed(line, ""))
    return device
