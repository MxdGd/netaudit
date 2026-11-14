import sys
from pathlib import Path

from netaudit.__main__ import main
from netaudit.audit import audit
from netaudit.htmlgen import generate_html
from netaudit.model import Device
from netaudit.parsers import parse_file

SAMPLES = Path(__file__).resolve().parent.parent / "samples"


def _acl_report() -> str:
    device = parse_file(str(SAMPLES / "broken" / "acl_mistakes.ios"))
    return generate_html({device.hostname: device}, [], audit(device))


def test_report_shows_findings_with_their_ids():
    html = _acl_report()
    assert "4 warning(s)" not in html and "2 error(s)" in html and "2 warning(s)" in html
    for check_id in ("ACL-UNDEFINED", "ACL-UNUSED", "ACL-SHADOWED", "ACL-MASK"):
        assert check_id in html
    assert "<svg" in html


def test_report_is_self_contained():
    html = _acl_report()
    assert "http" not in html
    assert "<script" not in html.lower()


def test_hostnames_are_escaped():
    evil = "<script>alert(1)</script>"
    html = generate_html({evil: Device(hostname=evil)}, [], [])
    assert "<script" not in html.lower()
    assert "&lt;script&gt;" in html


def test_html_option_writes_a_file(monkeypatch, tmp_path):
    out = tmp_path / "report.html"
    monkeypatch.setattr(sys, "argv", [
        "netaudit", "--links", str(SAMPLES / "links_pt.txt"), "--html", str(out),
        str(SAMPLES / "pt_r1.ios"), str(SAMPLES / "pt_r2.ios"),
    ])
    assert main() == 0
    text = out.read_text(encoding="utf-8")
    assert "<svg" in text and "0 error(s)" in text
