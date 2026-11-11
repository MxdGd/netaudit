"""Audit checks: each one asks a question about parsed devices."""
from dataclasses import dataclass
from ipaddress import ip_network

from netaudit.model import Device, Interface, Link


@dataclass
class Finding:
    device: str
    severity: str  # "error" or "warning"
    message: str


def ospf_area_for(device: Device, iface: Interface) -> str | None:
    """Area of the OSPF network statement covering this interface, or None."""
    if device.ospf is None or iface.ip is None:
        return None
    best = None  # (prefix length, area): the most specific statement wins
    for prefix, area in device.ospf.networks:
        net = ip_network(prefix, strict=False)
        if iface.ip.ip in net and (best is None or net.prefixlen > best[0]):
            best = (net.prefixlen, area)
    return best[1] if best else None


def check_shutdown_interfaces(device: Device) -> list[Finding]:
    """Report interfaces that have an IP address but are administratively shut down.

    Unused interfaces are shut down on purpose, so an interface without an
    address is not reported.
    """
    return [
        Finding(
            device.hostname, "error",
            f"{name} has the IP address {iface.ip} but is shut down",
        )
        for name, iface in device.interfaces.items()
        if iface.shutdown and iface.ip is not None
    ]


def check_ospf_coverage(device: Device) -> list[Finding]:
    """With OSPF configured, every active interface with an IP needs a covering network statement."""
    if device.ospf is None:
        return []
    return [
        Finding(
            device.hostname, "error",
            f"{name} ({iface.ip}) is not covered by any OSPF network statement, "
            f"so OSPF does not run on it",
        )
        for name, iface in device.interfaces.items()
        if iface.ip is not None and not iface.shutdown
        and ospf_area_for(device, iface) is None
    ]


CHECKS = [check_shutdown_interfaces, check_ospf_coverage]


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
        if a.switchport_mode or b.switchport_mode:
            continue  # layer-2 links are checked by check_trunk_links
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


def check_ospf_links(devices: dict[str, Device], links: list[Link]) -> list[Finding]:
    """Both ends of a link must run OSPF in the same area with the same network type."""
    findings = []
    for link in links:
        da, db = devices.get(link.a_device), devices.get(link.b_device)
        a = _find_interface(devices, link.a_device, link.a_iface)
        b = _find_interface(devices, link.b_device, link.b_iface)
        if da is None or db is None or a is None or b is None:
            continue
        area_a, area_b = ospf_area_for(da, a), ospf_area_for(db, b)
        if area_a is None or area_b is None:
            continue  # an uncovered interface is reported by check_ospf_coverage
        name = f"{link.a_device}<->{link.b_device}"
        if area_a != area_b:
            findings.append(Finding(
                name, "error",
                f"OSPF area mismatch: {link.a_device} {link.a_iface} is in area {area_a}, "
                f"{link.b_device} {link.b_iface} is in area {area_b}",
            ))
        if a.ospf_network != b.ospf_network:
            findings.append(Finding(
                name, "error",
                f"OSPF network type mismatch: {link.a_device} {link.a_iface} is "
                f"{a.ospf_network or 'default'}, {link.b_device} {link.b_iface} is "
                f"{b.ospf_network or 'default'}",
            ))
    return findings


def check_duplicate_router_ids(devices: dict[str, Device]) -> list[Finding]:
    """No two routers in the lab may use the same OSPF router ID."""
    users: dict[str, list[str]] = {}
    for device in devices.values():
        if device.ospf and device.ospf.router_id:
            users.setdefault(device.ospf.router_id, []).append(device.hostname)
    return [
        Finding(
            ", ".join(names), "error",
            f"duplicate OSPF router ID {rid} on {', '.join(names)}",
        )
        for rid, names in users.items()
        if len(names) > 1
    ]


def audit_network(devices: dict[str, Device], links: list[Link]) -> list[Finding]:
    findings = []
    for device in devices.values():
        findings.extend(audit(device))
    findings.extend(check_links(devices, links))
    findings.extend(check_ospf_links(devices, links))
    findings.extend(check_static_routes(devices))
    findings.extend(check_trunk_links(devices, links))
    findings.extend(check_duplicate_router_ids(devices))
    return findings


def check_static_routes(devices: dict[str, Device]) -> list[Finding]:
    """Each static route's next hop must be reachable through a connected, active interface."""
    owned = {i.ip.ip for d in devices.values() for i in d.interfaces.values() if i.ip}
    findings = []
    for device in devices.values():
        mine = {i.ip.ip for i in device.interfaces.values() if i.ip}
        for route in device.static_routes:
            if route.next_hop is None:
                continue  # routes that name an exit interface are not checked yet
            label = f"static route {route.prefix} via {route.next_hop}"
            if route.next_hop in mine:
                findings.append(Finding(
                    device.hostname, "error",
                    f"{label}: the next hop is this device's own address"))
                continue
            egress = [
                (name, iface) for name, iface in device.interfaces.items()
                if iface.ip and route.next_hop in iface.ip.network
            ]
            if not egress:
                findings.append(Finding(
                    device.hostname, "error",
                    f"{label}: the next hop is not in any connected subnet, "
                    f"so the route cannot be used"))
            elif all(iface.shutdown for _, iface in egress):
                findings.append(Finding(
                    device.hostname, "error",
                    f"{label}: the interface toward it ({egress[0][0]}) is shut down"))
            elif route.next_hop not in owned:
                findings.append(Finding(
                    device.hostname, "warning",
                    f"{label}: no device in the lab owns the next hop (external device?)"))
    return findings


DEFAULT_VLANS = {1, 1002, 1003, 1004, 1005}


def check_vlans_defined(device: Device) -> list[Finding]:
    """Every VLAN a port uses must be defined on the switch."""
    defined = DEFAULT_VLANS | set(device.vlans)
    findings = []
    for name, iface in device.interfaces.items():
        if iface.switchport_mode == "access":
            vlan = iface.access_vlan if iface.access_vlan is not None else 1
            if vlan not in defined:
                findings.append(Finding(
                    device.hostname, "error",
                    f"{name} is in access VLAN {vlan}, which is not defined on this switch"))
        elif iface.switchport_mode == "trunk" and iface.trunk_allowed is not None:
            for vlan in sorted(iface.trunk_allowed - defined):
                findings.append(Finding(
                    device.hostname, "warning",
                    f"trunk {name} allows VLAN {vlan}, which is not defined on this switch"))
    return findings


CHECKS.append(check_vlans_defined)


def _allowed_text(allowed: set[int] | None) -> str:
    if allowed is None:
        return "all"
    return ",".join(str(v) for v in sorted(allowed)) or "none"


def check_trunk_links(devices: dict[str, Device], links: list[Link]) -> list[Finding]:
    """Both ends of a switch-to-switch link must agree on mode, native VLAN and allowed VLANs."""
    findings = []
    for link in links:
        a = _find_interface(devices, link.a_device, link.a_iface)
        b = _find_interface(devices, link.b_device, link.b_iface)
        if a is None or b is None or not (a.switchport_mode or b.switchport_mode):
            continue
        name = f"{link.a_device}<->{link.b_device}"
        end_a = f"{link.a_device} {link.a_iface}"
        end_b = f"{link.b_device} {link.b_iface}"
        if a.switchport_mode != b.switchport_mode:
            findings.append(Finding(
                name, "error",
                f"switchport mode mismatch: {end_a} is {a.switchport_mode or 'not a switchport'}, "
                f"{end_b} is {b.switchport_mode or 'not a switchport'}"))
        elif a.switchport_mode == "access":
            if (a.access_vlan or 1) != (b.access_vlan or 1):
                findings.append(Finding(
                    name, "error",
                    f"access VLAN mismatch: {end_a} is in VLAN {a.access_vlan or 1}, "
                    f"{end_b} is in VLAN {b.access_vlan or 1}"))
        elif a.switchport_mode == "trunk":
            native_a, native_b = a.native_vlan or 1, b.native_vlan or 1
            if native_a != native_b:
                findings.append(Finding(
                    name, "error",
                    f"native VLAN mismatch: {end_a} is {native_a}, {end_b} is {native_b}"))
            if a.trunk_allowed != b.trunk_allowed:
                findings.append(Finding(
                    name, "warning",
                    f"allowed-VLAN mismatch: {end_a} allows {_allowed_text(a.trunk_allowed)}, "
                    f"{end_b} allows {_allowed_text(b.trunk_allowed)}; "
                    f"a VLAN missing on either end does not cross the link"))
    return findings
