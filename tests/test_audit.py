from pathlib import Path

from netaudit.audit import audit
from netaudit.parsers.frr import parse_frr

SAMPLES = Path(__file__).parent.parent / "samples"


def load(name):
    return parse_frr((SAMPLES / name).read_text())


def test_good_config_has_no_findings():
    assert audit(load("r2.conf")) == []


def test_shutdown_interface_is_found():
    findings = audit(load("broken/r2_shutdown.conf"))
    assert len(findings) == 1
    assert findings[0].device == "r2"
    assert "eth2" in findings[0].message
