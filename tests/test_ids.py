import sys
from pathlib import Path

from netaudit.__main__ import main
from netaudit.audit import CHECK_IDS, audit
from netaudit.lessons import lesson_text
from netaudit.parsers import parse_file

SAMPLE = Path(__file__).resolve().parent.parent / "samples" / "broken" / "acl_mistakes.ios"


def test_findings_carry_the_id_of_their_check():
    device = parse_file(str(SAMPLE))
    ids = {f.check for f in audit(device)}
    assert ids == {"ACL-UNDEFINED", "ACL-UNUSED", "ACL-SHADOWED", "ACL-MASK"}


def test_every_check_has_a_lesson():
    assert len(CHECK_IDS) == 14
    for check_id in CHECK_IDS.values():
        assert lesson_text(check_id), check_id


def test_explain_prints_the_lesson(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["netaudit", "--explain", "ACL-MASK"])
    assert main() == 0
    assert "ACL-MASK" in capsys.readouterr().out


def test_explain_unknown_id_fails_and_lists_ids(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["netaudit", "--explain", "NOPE"])
    assert main() == 2
    assert "ACL-MASK" in capsys.readouterr().err
