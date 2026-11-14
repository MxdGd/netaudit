"""Short lessons that explain each check; they ship as text files inside the package."""
from importlib.resources import files

from netaudit.audit import CHECK_IDS


def known_ids() -> list[str]:
    return sorted(CHECK_IDS.values())


def lesson_text(check_id: str) -> str | None:
    """The lesson for a check ID, or None if the ID is not a real one."""
    if check_id not in CHECK_IDS.values():
        return None
    path = files("netaudit") / "lesson_files" / f"{check_id}.md"
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None
