from pathlib import Path

from netaudit.audit import audit
from netaudit.parsers import parse_file

SAMPLE = Path(__file__).resolve().parent.parent / "samples" / "broken" / "acl_mistakes.ios"


def test_acl_sample_reports_exactly_the_four_planted_mistakes():
    device = parse_file(str(SAMPLE))
    assert device.unparsed == []
    messages = [f.message for f in audit(device)]
    assert len(messages) == 4
    assert any("GHOST" in m and "no ACL" in m for m in messages)
    assert any("UNUSED" in m and "not applied" in m for m in messages)
    assert any("BLOCK_WEB" in m and "never run" in m for m in messages)
    assert any("255.255.255.0" in m and "wildcard" in m for m in messages)
