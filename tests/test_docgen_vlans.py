from pathlib import Path

from netaudit.audit import audit_network
from netaudit.docgen import generate_doc
from netaudit.parsers.ios import parse_ios

SAMPLES = Path(__file__).parent.parent / "samples"


def test_switch_document_lists_vlans_and_ports():
    sw = parse_ios((SAMPLES / "sw1.ios").read_text())
    devices = {"sw1": sw}
    doc = generate_doc(devices, [], audit_network(devices, []))
    assert "## VLANs" in doc
    assert "SALES" in doc
    assert "## Switchports" in doc
    assert "10,20" in doc
    assert "No problems found." in doc
