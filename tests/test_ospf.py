from pathlib import Path

from netaudit.audit import audit_network
from netaudit.links import parse_links
from netaudit.parsers.frr import parse_frr

SAMPLES = Path(__file__).parent.parent / "samples"


def lab(r3_file):
    files = {"r1": "r1.conf", "r2": "r2.conf", "r3": r3_file}
    devices = {name: parse_frr((SAMPLES / f).read_text()) for name, f in files.items()}
    links = parse_links((SAMPLES / "links.txt").read_text())
    return devices, links


def test_missing_network_statement_is_found():
    findings = audit_network(*lab("broken/r3_missing_network.conf"))
    assert len(findings) == 1
    assert findings[0].device == "r3"
    assert "not covered by any OSPF network statement" in findings[0].message


def test_area_mismatch_is_found():
    findings = audit_network(*lab("broken/r3_area_mismatch.conf"))
    assert len(findings) == 1
    assert "area mismatch" in findings[0].message


def test_network_type_mismatch_is_found():
    findings = audit_network(*lab("broken/r3_ospf_type.conf"))
    assert len(findings) == 1
    assert "network type mismatch" in findings[0].message
