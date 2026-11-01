"""Generate a Markdown document describing a lab."""
from netaudit.audit import Finding, ospf_area_for
from netaudit.model import Device, Link


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return lines


def generate_doc(
    devices: dict[str, Device], links: list[Link], findings: list[Finding]
) -> str:
    out = ["# Network documentation", ""]

    out += ["## Devices", ""]
    rows = []
    for name in sorted(devices):
        d = devices[name]
        router_id = d.ospf.router_id if d.ospf and d.ospf.router_id else "-"
        rows.append([name, router_id, str(len(d.interfaces))])
    out += _table(["Device", "OSPF router-id", "Interfaces"], rows) + [""]

    out += ["## IP addressing", ""]
    rows = []
    for name in sorted(devices):
        d = devices[name]
        for iname, iface in d.interfaces.items():
            ip = str(iface.ip) if iface.ip else "-"
            subnet = str(iface.ip.network) if iface.ip else "-"
            area = ospf_area_for(d, iface)
            rows.append([
                name, iname, ip, subnet,
                area if area is not None else "-",
                "shutdown" if iface.shutdown else "up",
            ])
    out += _table(
        ["Device", "Interface", "IP", "Subnet", "OSPF area", "Config state"], rows
    ) + [""]

    out += ["## Links", ""]
    if not links:
        out += ["_No links were provided._", ""]
    else:
        rows = []
        for link in links:
            a = devices.get(link.a_device)
            b = devices.get(link.b_device)
            ia = a.interfaces.get(link.a_iface) if a else None
            ib = b.interfaces.get(link.b_iface) if b else None
            if ia and ib and ia.ip and ib.ip:
                subnet = str(ia.ip.network) if ia.ip.network == ib.ip.network else "MISMATCH"
            else:
                subnet = "-"
            rows.append([f"{link.a_device}:{link.a_iface}", f"{link.b_device}:{link.b_iface}", subnet])
        out += _table(["End A", "End B", "Subnet"], rows) + [""]

    out += ["## OSPF", ""]
    any_ospf = False
    for name in sorted(devices):
        d = devices[name]
        if d.ospf is None:
            continue
        any_ospf = True
        out += [f"### {name}", "", f"- Router ID: {d.ospf.router_id or '-'}"]
        out += [f"- network {prefix} area {area}" for prefix, area in d.ospf.networks]
        out.append("")
    if not any_ospf:
        out += ["_No device runs OSPF._", ""]

    out += ["## Static routes", ""]
    rows = []
    for name in sorted(devices):
        for r in devices[name].static_routes:
            via = str(r.next_hop) if r.next_hop else (r.interface or "-")
            rows.append([name, str(r.prefix), via])
    if rows:
        out += _table(["Device", "Prefix", "Via"], rows) + [""]
    else:
        out += ["_No static routes._", ""]

    out += ["## VLANs", ""]
    rows = []
    for name in sorted(devices):
        for vid in sorted(devices[name].vlans):
            rows.append([name, str(vid), devices[name].vlans[vid] or "-"])
    if rows:
        out += _table(["Device", "VLAN", "Name"], rows) + [""]
    else:
        out += ["_No VLANs defined._", ""]

    out += ["## Switchports", ""]
    rows = []
    for name in sorted(devices):
        for iname, iface in devices[name].interfaces.items():
            if iface.switchport_mode is None:
                continue
            if iface.switchport_mode == "access":
                rows.append([name, iname, "access", str(iface.access_vlan or 1), "-", "-"])
            else:
                if iface.trunk_allowed is None:
                    allowed = "all"
                elif not iface.trunk_allowed:
                    allowed = "none"
                else:
                    allowed = ",".join(str(v) for v in sorted(iface.trunk_allowed))
                rows.append([name, iname, "trunk", "-", allowed, str(iface.native_vlan or 1)])
    if rows:
        out += _table(
            ["Device", "Interface", "Mode", "Access VLAN", "Trunk allowed", "Native VLAN"], rows
        ) + [""]
    else:
        out += ["_No switchports._", ""]

    out += ["## Audit findings", ""]
    if findings:
        out += [f"- **{f.severity.upper()}** {f.device}: {f.message}" for f in findings]
    else:
        out.append("No problems found.")
    return "\n".join(out) + "\n"
