from pathlib import Path

from netaudit.audit import audit
from netaudit.parsers.ios import parse_ios

SAMPLES = Path(__file__).parent.parent / "samples"


def load(name):
    return parse_ios((SAMPLES / name).read_text())


def test_ios_parser_reads_vlans_and_ports():
    sw = load("sw1.ios")
    assert sw.hostname == "sw1"
    assert sw.vlans == {10: "SALES", 20: "HR"}
    assert sw.interfaces["FastEthernet0/1"].access_vlan == 10
    trunk = sw.interfaces["GigabitEthernet0/1"]
    assert trunk.switchport_mode == "trunk"
    assert trunk.trunk_allowed == {10, 20}
    assert str(sw.interfaces["Vlan10"].ip) == "192.168.10.2/24"


def test_good_switch_has_no_findings():
    assert audit(load("sw1.ios")) == []


def test_undefined_access_vlan_is_found():
    findings = audit(load("broken/sw1_missing_vlan.ios"))
    assert len(findings) == 1
    assert findings[0].severity == "error"
    assert "FastEthernet0/2" in findings[0].message


def test_trunk_allowing_undefined_vlan_is_a_warning():
    findings = audit(load("broken/sw1_trunk_vlan.ios"))
    assert len(findings) == 1
    assert findings[0].severity == "warning"
