from ipaddress import IPv4Address, IPv4Interface, IPv4Network

from netaudit.audit import check_default_route_loops, check_duplicate_router_ids
from netaudit.model import Device, Interface, Ospf, StaticRoute


def _router(name, router_id):
    return Device(hostname=name, ospf=Ospf(router_id=router_id))


def test_duplicate_router_id_is_reported():
    devices = {
        "r1": _router("r1", "1.1.1.1"),
        "r2": _router("r2", "1.1.1.1"),
        "r3": _router("r3", "3.3.3.3"),
    }
    findings = check_duplicate_router_ids(devices)
    assert len(findings) == 1
    assert findings[0].severity == "error"
    assert "1.1.1.1" in findings[0].message
    assert "r1" in findings[0].message and "r2" in findings[0].message


def test_different_router_ids_are_fine():
    devices = {
        "r1": _router("r1", "1.1.1.1"),
        "r2": _router("r2", "2.2.2.2"),
        "r3": _router("r3", "3.3.3.3"),
    }
    assert check_duplicate_router_ids(devices) == []


def _gateway(name, my_ip, default_via):
    routes = []
    if default_via:
        routes.append(StaticRoute(IPv4Network("0.0.0.0/0"), IPv4Address(default_via)))
    return Device(
        hostname=name,
        interfaces={"e0": Interface("e0", ip=IPv4Interface(my_ip))},
        static_routes=routes,
    )


def test_default_routes_pointing_at_each_other_are_a_loop():
    devices = {
        "r1": _gateway("r1", "10.0.0.1/30", "10.0.0.2"),
        "r2": _gateway("r2", "10.0.0.2/30", "10.0.0.1"),
    }
    findings = check_default_route_loops(devices)
    assert len(findings) == 1
    assert findings[0].severity == "error"
    assert "r1" in findings[0].message and "r2" in findings[0].message


def test_default_route_to_outside_is_not_a_loop():
    devices = {
        "r1": _gateway("r1", "10.0.0.1/30", "10.0.0.2"),
        "r2": _gateway("r2", "10.0.0.2/30", "10.0.0.9"),
    }
    assert check_default_route_loops(devices) == []


def test_one_default_route_is_not_a_loop():
    devices = {
        "r1": _gateway("r1", "10.0.0.1/30", "10.0.0.2"),
        "r2": _gateway("r2", "10.0.0.2/30", None),
    }
    assert check_default_route_loops(devices) == []
