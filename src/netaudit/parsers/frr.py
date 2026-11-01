"""Parser for FRRouting configs (IOS-like syntax) into the neutral model."""
from ipaddress import IPv4Address, IPv4Interface, IPv4Network

from netaudit.model import Device, Interface, Ospf, StaticRoute


def _parse_static_route(words: list[str]) -> StaticRoute:
    prefix = IPv4Network(words[2], strict=False)
    target = words[3]
    try:
        return StaticRoute(prefix, next_hop=IPv4Address(target))
    except ValueError:
        return StaticRoute(prefix, interface=target)


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
        elif isinstance(section, Ospf):
            if line.startswith("ospf router-id "):
                section.router_id = words[2]
            elif line.startswith("network "):
                section.networks.append((words[1], words[3]))
    return device
