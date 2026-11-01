from pathlib import Path

from netaudit.audit import audit_network
from netaudit.docgen import generate_doc
from netaudit.links import parse_links
from netaudit.parsers.frr import parse_frr

SAMPLES = Path(__file__).parent.parent / "samples"


def doc_for(r3_file):
    files = {"r1": "r1.conf", "r2": "r2.conf", "r3": r3_file}
    devices = {name: parse_frr((SAMPLES / f).read_text()) for name, f in files.items()}
    links = parse_links((SAMPLES / "links.txt").read_text())
    return generate_doc(devices, links, audit_network(devices, links))


def test_good_lab_document():
    doc = doc_for("r3.conf")
    assert doc.startswith("# Network documentation")
    assert "10.0.12.1/30" in doc
    assert "10.0.23.0/30" in doc
    assert "192.168.100.0/24" in doc
    assert "No problems found." in doc


def test_broken_lab_document_shows_the_problem():
    doc = doc_for("broken/r3_wrong_subnet.conf")
    assert "MISMATCH" in doc
    assert "subnet mismatch" in doc
