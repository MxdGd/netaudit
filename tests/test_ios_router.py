from ipaddress import IPv4Address, IPv4Network
from pathlib import Path

from netaudit.audit import audit_network
from netaudit.links import parse_links
from netaudit.parsers.ios import parse_ios

SAMPLES = Path(__file__).parent.parent / "samples"


def lab(patch=None):
    """Load the two sample routers; patch = (router, old, new) edits one config's text."""
    texts = {
        "R1": (SAMPLES / "pt_r1.ios").read_text(),
        "R2": (SAMPLES / "pt_r2.ios").read_text(),
    }
    if patch:
        router, old, new = patch
        assert texts[router].count(old) == 1
        texts[router] = texts[router].replace(old, new)
    devices = {name: parse_ios(text) for name, text in texts.items()}
    links = parse_links((SAMPLES / "links_pt.txt").read_text())
    return devices, links


def messages(patch=None):
    return [f.message for f in audit_network(*lab(patch))]


def test_router_config_is_parsed():
    devices, _ = lab()
    r1 = devices["R1"]
    assert str(r1.interfaces["GigabitEthernet0/0"].ip) == "10.0.12.1/30"
    assert r1.ospf.router_id == "1.1.1.1"
    assert ("1.1.1.1/32", "0") in r1.ospf.networks
    assert ("10.0.12.0/30", "0") in r1.ospf.networks
    route = r1.static_routes[0]
    assert route.prefix == IPv4Network("192.168.100.0/24")
    assert route.next_hop == IPv4Address("10.0.12.2")


def test_good_routers_have_no_findings_and_nothing_unparsed():
    devices, links = lab()
    assert audit_network(devices, links) == []
    assert all(d.unparsed == [] for d in devices.values())


def test_wrong_subnet_is_found():
    patch = ("R2", "ip address 10.0.12.2 255.255.255.252", "ip address 10.0.13.2 255.255.255.252")
    assert any("subnet mismatch" in m for m in messages(patch))


def test_missing_network_statement_is_found():
    patch = ("R2", " network 10.0.12.0 0.0.0.3 area 0\n", "")
    assert any("not covered by any OSPF network statement" in m for m in messages(patch))


def test_area_mismatch_is_found():
    patch = ("R2", " network 10.0.12.0 0.0.0.3 area 0", " network 10.0.12.0 0.0.0.3 area 1")
    assert any("area mismatch" in m for m in messages(patch))


def test_unreachable_next_hop_is_found():
    patch = ("R1", "ip route 192.168.100.0 255.255.255.0 10.0.12.2",
             "ip route 192.168.100.0 255.255.255.0 10.0.99.2")
    assert any("not in any connected subnet" in m for m in messages(patch))


def test_shut_interface_with_an_ip_is_found():
    patch = ("R2", "ip address 10.0.12.2 255.255.255.252\n",
             "ip address 10.0.12.2 255.255.255.252\n shutdown\n")
    assert any("but is shut down" in m for m in messages(patch))


def test_wildcard_masks_become_prefixes():
    text = (
        "hostname X\n!\nrouter ospf 1\n"
        " network 0.0.0.0 255.255.255.255 area 0\n"
        " network 10.1.1.0 0.0.0.255 area 0\n"
        " network 10.9.9.9 0.0.0.0 area 0\n"
    )
    assert parse_ios(text).ospf.networks == [
        ("0.0.0.0/0", "0"), ("10.1.1.0/24", "0"), ("10.9.9.9/32", "0"),
    ]


def test_unsupported_router_lines_are_reported():
    text = (
        "hostname X\n!\ninterface GigabitEthernet0/0\n"
        " ip address 10.0.0.1 255.255.255.0\n"
        " ip ospf cost 10\n"
        "!\nrouter ospf 1\n passive-interface GigabitEthernet0/0\n"
        "!\nip route 10.5.0.0 255.255.0.0 10.0.0.2 200\n"
    )
    device = parse_ios(text)
    assert [(u.context, u.line) for u in device.unparsed] == [
        ("interface GigabitEthernet0/0", "ip ospf cost 10"),
        ("router ospf", "passive-interface GigabitEthernet0/0"),
        ("", "ip route 10.5.0.0 255.255.0.0 10.0.0.2 200"),
    ]
