"""Audit checks: each one asks a question about a parsed device."""
from dataclasses import dataclass

from netaudit.model import Device


@dataclass
class Finding:
    device: str
    severity: str  # "error" or "warning"
    message: str


def check_shutdown_interfaces(device: Device) -> list[Finding]:
    """Report interfaces that are administratively shut down."""
    return [
        Finding(device.hostname, "error", f"{name} is shut down")
        for name, iface in device.interfaces.items()
        if iface.shutdown
    ]


CHECKS = [check_shutdown_interfaces]


def audit(device: Device) -> list[Finding]:
    findings = []
    for check in CHECKS:
        findings.extend(check(device))
    return findings
