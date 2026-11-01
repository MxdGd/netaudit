"""Audit checks: each one asks a question about parsed devices."""
from dataclasses import dataclass

from netaudit.model import Device, Interface, Link


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


def _find_interface(devices: dict[str, Device], dev: str, iface: str) -> Interface | None:
    device = devices.get(dev)
    return device.interfaces.get(iface) if device else None


def check_links(devices: dict[str, Device], links: list[Link]) -> list[Finding]:
    """For each cable, both ends must share a subnet and have different IPs."""
    findings = []
    for link in links:
        name = f"{link.a_device}<->{link.b_device}"
        a = _find_interface(devices, link.a_device, link.a_iface)
        b = _find_interface(devices, link.b_device, link.b_iface)
        missing = False
        for dev, iface, found in ((link.a_device, link.a_iface, a), (link.b_device, link.b_iface, b)):
            if found is None:
                findings.append(Finding(name, "error", f"{dev}:{iface} not found in the configs"))
                missing = True
        if missing:
            continue
        if a.ip is None or b.ip is None:
            findings.append(Finding(name, "warning", "one end of the link has no IP address"))
        elif a.ip.network != b.ip.network:
            findings.append(Finding(
                name, "error",
                f"subnet mismatch: {link.a_device} {link.a_iface} {a.ip} vs "
                f"{link.b_device} {link.b_iface} {b.ip}",
            ))
        elif a.ip.ip == b.ip.ip:
            findings.append(Finding(name, "error", f"duplicate IP {a.ip.ip} on both ends"))
    return findings


def audit_network(devices: dict[str, Device], links: list[Link]) -> list[Finding]:
    findings = []
    for device in devices.values():
        findings.extend(audit(device))
    findings.extend(check_links(devices, links))
    return findings
