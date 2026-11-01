"""Parser for FRRouting configs (IOS-like syntax) into the neutral model."""
from ipaddress import IPv4Address, IPv4Interface, IPv4Network

from netaudit.model import Device, Interface, Ospf, StaticRoute, Unparsed

# Top-level lines that are harmless boilerplate, not network behavior.
IGNORED_PREFIXES = ("frr ", "log ", "service ", "line ")


def _parse_static_route(words: list[str]) -> StaticRoute:
    prefix = IPv4Network(words[2], strict=False)
    target = words[3]
    try:
        return StaticRoute(prefix, next_hop=IPv4Address(target))
    except ValueError:
        return StaticRoute(prefix, interface=target)


def _context(section) -> str:
    if isinstance(section, Interface):
        return f"interface {section.name}"
    if isinstance(section, Ospf):
        return "router ospf"
    return ""


def parse_frr(text: str) -> Device:
    device = Device()
    section = None  # the block we are currently inside
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("!"):  # '!' ends a block, like in IOS
            section = None
            continue
        words = line.split()
        known = True
        if words[0] == "hostname":
            device.hostname = words[1]
        elif words[0] == "interface":
            section = Interface(name=words[1])
            device.interfaces[section.name] = section
        elif line == "router ospf":
            device.ospf = Ospf()
            section = device.ospf
        elif line.startswith("ip route "):
            section = None
            device.static_routes.append(_parse_static_route(words))
        elif isinstance(section, Interface):
            if line.startswith("ip address "):
                section.ip = IPv4Interface(words[2])
            elif line.startswith("ip ospf network "):
                section.ospf_network = words[3]
            elif line == "shutdown":
                section.shutdown = True
            elif line == "no shutdown":
                section.shutdown = False
            elif line.startswith("description "):
                pass
            else:
                known = False
        elif isinstance(section, Ospf):
            if line.startswith("ospf router-id "):
                section.router_id = words[2]
            elif line.startswith("network "):
                section.networks.append((words[1], words[3]))
            else:
                known = False
        else:
            known = line == "end" or line.startswith(IGNORED_PREFIXES)
        if not known:
            device.unparsed.append(Unparsed(line, _context(section)))
    return device
