"""Generate one self-contained HTML report: no scripts, no internet needed."""
import math
from html import escape

from netaudit.audit import Finding, ospf_area_for
from netaudit.model import Device, Link

CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--muted:#666;--line:#ccc;--err:#c62828;--warn:#b26a00;
--node:#e8f0fe;--sw:#fff3e0}
@media (prefers-color-scheme:dark){:root{--bg:#111;--fg:#eee;--muted:#aaa;--line:#444;
--err:#ff6b6b;--warn:#ffb74d;--node:#1e2a44;--sw:#3a2d14}}
body{font-family:system-ui,sans-serif;background:var(--bg);color:var(--fg);
max-width:960px;margin:2rem auto;padding:0 1rem;line-height:1.5}
h1{margin-bottom:.2rem}h2{margin-top:2rem;border-bottom:1px solid var(--line)}
.summary{color:var(--muted)}.sev-error strong,.summary .sev-error{color:var(--err)}
.sev-warning strong,.summary .sev-warning{color:var(--warn)}
ul.findings{list-style:none;padding:0}ul.findings li{padding:.4rem 0;border-bottom:1px solid var(--line)}
code{background:var(--line);padding:0 .3rem;border-radius:3px}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%}
th,td{text-align:left;padding:.3rem .6rem;border-bottom:1px solid var(--line)}
svg{width:100%;height:auto}svg text{fill:var(--fg);font-size:13px}
svg .small{font-size:11px;fill:var(--muted)}
.node{stroke:var(--fg);stroke-width:1.5}.router{fill:var(--node)}.switch{fill:var(--sw)}
.link{stroke:var(--muted);stroke-width:2}.link.bad{stroke:var(--err);stroke-width:4}
.note{color:var(--muted)}
"""


def _table(headers: list[str], rows: list[list[str]], empty: str) -> str:
    if not rows:
        return f'<p class="note">{escape(empty)}</p>'
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(c))}</td>" for c in row) + "</tr>"
        for row in rows
    )
    return f'<div class="scroll"><table><tr>{head}</tr>{body}</table></div>'


def _is_switch(device: Device | None) -> bool:
    return device is not None and any(i.switchport_mode for i in device.interfaces.values())


def _svg(devices: dict[str, Device], links: list[Link], findings: list[Finding]) -> str:
    """The topology as plain SVG: devices on a circle, broken links in red."""
    broken = {f.device for f in findings}
    names = sorted(set(devices) | {n for l in links for n in (l.a_device, l.b_device)})
    pos = {}
    for i, name in enumerate(names):
        angle = 2 * math.pi * i / len(names) - math.pi / 2
        pos[name] = (300 + 150 * math.cos(angle), 220 + 150 * math.sin(angle))
    parts = ['<svg viewBox="0 0 600 440" role="img" aria-label="Network topology">']
    for link in links:
        (x1, y1), (x2, y2) = pos[link.a_device], pos[link.b_device]
        bad = f"{link.a_device}<->{link.b_device}" in broken
        parts.append(
            f'<line class="link{" bad" if bad else ""}" '
            f'x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}"/>'
        )
        parts.append(
            f'<text class="small" x="{(x1 + x2) / 2:.0f}" y="{(y1 + y2) / 2 - 6:.0f}" '
            f'text-anchor="middle">{escape(link.a_iface)} - {escape(link.b_iface)}</text>'
        )
    for name in names:
        x, y = pos[name]
        switch = _is_switch(devices.get(name))
        parts.append(
            f'<rect class="node {"switch" if switch else "router"}" x="{x - 45:.0f}" '
            f'y="{y - 18:.0f}" width="90" height="36" rx="{4 if switch else 18}"/>'
        )
        parts.append(f'<text x="{x:.0f}" y="{y + 5:.0f}" text-anchor="middle">{escape(name)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def generate_html(
    devices: dict[str, Device], links: list[Link], findings: list[Finding]
) -> str:
    errors = sum(1 for f in findings if f.severity == "error")
    warnings = len(findings) - errors
    unchecked = sum(len(d.unparsed) for d in devices.values())
    out = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>netaudit report</title><style>{CSS}</style></head><body>",
        "<h1>netaudit report</h1>",
        f'<p class="summary"><span class="sev-error">{errors} error(s)</span>, '
        f'<span class="sev-warning">{warnings} warning(s)</span>, '
        f"{unchecked} line(s) not checked</p>",
        "<h2>Topology</h2>",
        _svg(devices, links, findings),
        "<h2>Findings</h2>",
    ]
    if findings:
        out.append('<ul class="findings">')
        for f in findings:
            out.append(
                f'<li class="sev-{escape(f.severity)}"><strong>{escape(f.severity.upper())}'
                f"</strong> {escape(f.device)}: {escape(f.message)} <code>{escape(f.check)}</code></li>"
            )
        out.append('</ul><p class="note">Run <code>netaudit --explain ID</code> '
                   "for a short lesson on any check.</p>")
    else:
        out.append('<p class="note">No problems found.</p>')

    rows = [[n, devices[n].ospf.router_id if devices[n].ospf and devices[n].ospf.router_id else "-",
             str(len(devices[n].interfaces)), "switch" if _is_switch(devices[n]) else "router"]
            for n in sorted(devices)]
    out += ["<h2>Devices</h2>", _table(["Device", "OSPF router-id", "Interfaces", "Type"], rows, "No devices.")]

    rows = []
    for n in sorted(devices):
        d = devices[n]
        for iname, iface in d.interfaces.items():
            area = ospf_area_for(d, iface)
            rows.append([n, iname, str(iface.ip) if iface.ip else "-",
                         area if area is not None else "-",
                         "shutdown" if iface.shutdown else "up"])
    out += ["<h2>IP addressing</h2>",
            _table(["Device", "Interface", "IP", "OSPF area", "State"], rows, "No interfaces.")]

    rows = []
    for link in links:
        a, b = devices.get(link.a_device), devices.get(link.b_device)
        ia = a.interfaces.get(link.a_iface) if a else None
        ib = b.interfaces.get(link.b_iface) if b else None
        if ia and ib and ia.ip and ib.ip:
            subnet = str(ia.ip.network) if ia.ip.network == ib.ip.network else "MISMATCH"
        else:
            subnet = "-"
        rows.append([f"{link.a_device}:{link.a_iface}", f"{link.b_device}:{link.b_iface}", subnet])
    out += ["<h2>Links</h2>", _table(["End A", "End B", "Subnet"], rows, "No links were provided.")]

    rows = [[n, str(r.prefix), str(r.next_hop) if r.next_hop else (r.interface or "-")]
            for n in sorted(devices) for r in devices[n].static_routes]
    out += ["<h2>Static routes</h2>", _table(["Device", "Prefix", "Via"], rows, "No static routes.")]

    rows = [[n, u.context or "-", u.line] for n in sorted(devices) for u in devices[n].unparsed]
    out += ["<h2>Not checked</h2>", _table(["Device", "Where", "Line"], rows, "Every line was understood.")]
    out.append("</body></html>")
    return "\n".join(out) + "\n"
