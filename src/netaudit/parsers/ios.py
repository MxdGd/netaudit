"""Parser for Cisco IOS-style switch configs into the neutral model.

Sub-commands must be indented by a space, as in 'show running-config'.
"""
from ipaddress import IPv4Interface

from netaudit.model import Device, Interface


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


def parse_ios(text: str) -> Device:
    device = Device()
    section = None  # a VLAN id (int) or an Interface
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
        elif isinstance(section, int):
            if words[0] == "name":
                device.vlans[section] = words[1]
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
            elif line == "shutdown":
                section.shutdown = True
            elif line == "no shutdown":
                section.shutdown = False
    return device
