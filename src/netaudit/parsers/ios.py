"""Parser for Cisco IOS-style configs (routers and switches) into the neutral model.

Sub-commands must be indented by a space, as in 'show running-config'.
"""
from ipaddress import IPv4Address, IPv4Interface, IPv4Network

from netaudit.model import Device, Interface, Ospf, StaticRoute, Unparsed

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
        elif isinstance(section, str):
            device.unparsed.append(Unparsed(line, section))
        else:
            device.unparsed.append(Unparsed(line, ""))
    return device
