from netaudit.lessons import known_ids, lesson_text


def test_no_lesson_still_has_a_todo():
    for check_id in known_ids():
        assert "TODO" not in lesson_text(check_id), check_id
