from pathlib import Path

from netaudit.audit import audit_network
from netaudit.links import parse_links
from netaudit.parsers.ios import parse_ios

SAMPLES = Path(__file__).parent.parent / "samples"


def lab(sw2_file="sw2.ios"):
    devices = {
        "sw1": parse_ios((SAMPLES / "sw1.ios").read_text()),
        "sw2": parse_ios((SAMPLES / sw2_file).read_text()),
    }
    links = parse_links((SAMPLES / "links_switch.txt").read_text())
    return devices, links


def test_good_trunk_has_no_findings():
    assert audit_network(*lab()) == []


def test_native_vlan_mismatch_is_found():
    findings = audit_network(*lab("broken/sw2_native_mismatch.ios"))
    assert len(findings) == 1
    assert findings[0].severity == "error"
    assert "native VLAN mismatch" in findings[0].message


def test_allowed_vlan_mismatch_is_a_warning():
    findings = audit_network(*lab("broken/sw2_allowed_mismatch.ios"))
    assert len(findings) == 1
    assert findings[0].severity == "warning"
    assert "allowed-VLAN mismatch" in findings[0].message


def test_mode_mismatch_is_found():
    findings = audit_network(*lab("broken/sw2_mode_mismatch.ios"))
    assert len(findings) == 1
    assert "switchport mode mismatch" in findings[0].message
