from ipaddress import IPv4Address, IPv4Interface, IPv4Network
from pathlib import Path

from netaudit.audit import audit_network
from netaudit.links import parse_links
from netaudit.model import Device, Interface, StaticRoute
from netaudit.parsers.frr import parse_frr

SAMPLES = Path(__file__).parent.parent / "samples"


def lab(r1_file):
    files = {"r1": r1_file, "r2": "r2.conf", "r3": "r3.conf"}
    devices = {name: parse_frr((SAMPLES / f).read_text()) for name, f in files.items()}
    links = parse_links((SAMPLES / "links.txt").read_text())
    return devices, links


def test_good_lab_static_route_is_parsed_and_clean():
    devices, links = lab("r1.conf")
    route = devices["r1"].static_routes[0]
    assert route.prefix == IPv4Network("192.168.100.0/24")
    assert route.next_hop == IPv4Address("10.0.12.2")
    assert audit_network(devices, links) == []


def test_next_hop_not_connected_is_found():
    findings = audit_network(*lab("broken/r1_bad_nexthop.conf"))
    assert len(findings) == 1
    assert "not in any connected subnet" in findings[0].message


def test_own_address_as_next_hop_is_found():
    findings = audit_network(*lab("broken/r1_own_nexthop.conf"))
    assert len(findings) == 1
    assert "own address" in findings[0].message


def test_next_hop_interface_down_is_found():
    findings = audit_network(*lab("broken/r1_nexthop_iface_down.conf"))
    assert any("interface toward it" in f.message for f in findings)


def test_next_hop_nobody_owns_is_only_a_warning():
    device = Device(hostname="edge")
    device.interfaces["eth0"] = Interface("eth0", ip=IPv4Interface("10.0.50.1/24"))
    device.static_routes.append(
        StaticRoute(IPv4Network("0.0.0.0/0"), next_hop=IPv4Address("10.0.50.9"))
    )
    findings = audit_network({"edge": device}, [])
    assert len(findings) == 1
    assert findings[0].severity == "warning"
