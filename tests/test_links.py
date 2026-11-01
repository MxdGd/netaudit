from pathlib import Path

from netaudit.audit import audit_network
from netaudit.links import parse_links
from netaudit.parsers.frr import parse_frr

SAMPLES = Path(__file__).parent.parent / "samples"


def lab(r3_file="r3.conf"):
    files = {"r1": "r1.conf", "r2": "r2.conf", "r3": r3_file}
    devices = {name: parse_frr((SAMPLES / f).read_text()) for name, f in files.items()}
    links = parse_links((SAMPLES / "links.txt").read_text())
    return devices, links


def test_good_lab_has_no_findings():
    assert audit_network(*lab()) == []


def test_wrong_subnet_is_found():
    findings = audit_network(*lab("broken/r3_wrong_subnet.conf"))
    assert len(findings) == 1
    assert "subnet mismatch" in findings[0].message


def test_wrong_mask_is_found():
    findings = audit_network(*lab("broken/r3_wrong_mask.conf"))
    assert len(findings) == 1
    assert "subnet mismatch" in findings[0].message


def test_duplicate_ip_is_found():
    findings = audit_network(*lab("broken/r3_dup_ip.conf"))
    assert len(findings) == 1
    assert "duplicate IP" in findings[0].message
