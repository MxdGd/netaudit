"""Read the cabling file: one link per line, like 'r1:eth1 r2:eth1'."""
from netaudit.model import Link


def parse_links(text: str) -> list[Link]:
    links = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        a, b = line.split()
        a_device, a_iface = a.split(":")
        b_device, b_iface = b.split(":")
        links.append(Link(a_device, a_iface, b_device, b_iface))
    return links
