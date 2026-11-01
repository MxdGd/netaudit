"""Pick the right parser for a config file based on its suffix."""
from pathlib import Path

from netaudit.model import Device
from netaudit.parsers.frr import parse_frr
from netaudit.parsers.ios import parse_ios


def parse_file(path: str) -> Device:
    text = Path(path).read_text()
    return parse_ios(text) if path.endswith(".ios") else parse_frr(text)
