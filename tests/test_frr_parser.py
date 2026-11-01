from pathlib import Path

from netaudit.parsers.frr import parse_frr

SAMPLES = Path(__file__).parent.parent / "samples"


def test_parse_r1():
    device = parse_frr((SAMPLES / "r1.conf").read_text())
    assert device.hostname == "r1"
    assert str(device.interfaces["eth1"].ip) == "10.0.12.1/30"
    assert device.ospf.router_id == "1.1.1.1"
    assert ("10.0.12.0/30", "0") in device.ospf.networks
