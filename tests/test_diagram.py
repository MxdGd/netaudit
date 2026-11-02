from pathlib import Path

from netaudit.audit import audit_network
from netaudit.docgen import generate_doc
from netaudit.links import parse_links
from netaudit.parsers import parse_file

SAMPLES = Path(__file__).parent.parent / "samples"


def report(files, links_file):
    devices = {}
    for name in files:
        device = parse_file(str(SAMPLES / name))
        devices[device.hostname] = device
    links = parse_links((SAMPLES / links_file).read_text())
    return generate_doc(devices, links, audit_network(devices, links))


def test_router_diagram():
    text = report(["r1.conf", "r2.conf", "r3.conf"], "links.txt")
    assert "```mermaid" in text
    assert 'n_r1["r1"]' in text
    assert "eth2 - eth1 (10.0.23.0/30)" in text
    assert "linkStyle" not in text


def test_broken_link_is_drawn_red():
    text = report(["r1.conf", "r2.conf", "broken/r3_wrong_subnet.conf"], "links.txt")
    assert "(MISMATCH)" in text
    assert "linkStyle 1 stroke:#d00" in text


def test_switches_are_hexagons():
    text = report(["sw1.ios", "sw2.ios"], "links_switch.txt")
    assert 'n_sw1{{"sw1"}}' in text
    assert "GigabitEthernet0/1 - GigabitEthernet0/1" in text
