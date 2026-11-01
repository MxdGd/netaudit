from pathlib import Path

from netaudit.audit import audit_network
from netaudit.docgen import generate_doc
from netaudit.parsers.frr import parse_frr
from netaudit.parsers.ios import parse_ios

SAMPLES = Path(__file__).parent.parent / "samples"


def test_good_samples_have_nothing_unparsed():
    for name in ("r1.conf", "r2.conf", "r3.conf"):
        assert parse_frr((SAMPLES / name).read_text()).unparsed == []
    for name in ("sw1.ios", "sw2.ios"):
        assert parse_ios((SAMPLES / name).read_text()).unparsed == []


def test_frr_unsupported_line_is_reported():
    device = parse_frr((SAMPLES / "broken/r1_unsupported.conf").read_text())
    assert [(u.context, u.line) for u in device.unparsed] == [
        ("interface eth1", "ip ospf cost 10")
    ]


def test_ios_unsupported_lines_are_reported():
    device = parse_ios((SAMPLES / "broken/sw1_unsupported.ios").read_text())
    assert [(u.context, u.line) for u in device.unparsed] == [
        ("", "spanning-tree mode rapid-pvst"),
        ("interface FastEthernet0/1", "spanning-tree portfast"),
    ]


def test_document_lists_lines_that_were_not_checked():
    bad = parse_frr((SAMPLES / "broken/r1_unsupported.conf").read_text())
    doc = generate_doc({"r1": bad}, [], audit_network({"r1": bad}, []))
    assert "## Not checked" in doc
    assert "ip ospf cost 10" in doc
    good = parse_frr((SAMPLES / "r1.conf").read_text())
    doc = generate_doc({"r1": good}, [], audit_network({"r1": good}, []))
    assert "Every line was understood." in doc
