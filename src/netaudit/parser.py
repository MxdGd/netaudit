"""Read an FRR config file into simple Python data."""
from dataclasses import dataclass, field
from ipaddress import IPv4Interface


@dataclass
class Interface:
    name: str
    ip: IPv4Interface | None = None
    ospf_network: str | None = None
    shutdown: bool = False


@dataclass
class Ospf:
    router_id: str | None = None
    networks: list[tuple[str, str]] = field(default_factory=list)  # (prefix, area)


@dataclass
class Device:
    hostname: str = ""
    interfaces: dict[str, Interface] = field(default_factory=dict)
    ospf: Ospf | None = None


def parse_config(text: str) -> Device:
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
