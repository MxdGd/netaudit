from netaudit.audit import check_duplicate_router_ids
from netaudit.model import Device, Ospf


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
