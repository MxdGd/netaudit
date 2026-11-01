import argparse
import sys
from pathlib import Path

from netaudit.audit import audit_network
from netaudit.docgen import generate_doc
from netaudit.links import parse_links
from netaudit.parsers import parse_file


def main() -> int:
    ap = argparse.ArgumentParser(prog="netaudit", description="Audit network device configs.")
    ap.add_argument("configs", nargs="+", help="device config files (.ios = IOS syntax, else FRR)")
    ap.add_argument("--links", help="file listing which interfaces are cabled together")
    ap.add_argument("--doc", help="also write a Markdown report to this file")
    args = ap.parse_args()

    devices = {}
    for path in args.configs:
        device = parse_file(path)
        devices[device.hostname] = device
    links = parse_links(Path(args.links).read_text()) if args.links else []

    findings = audit_network(devices, links)
    for f in findings:
        print(f"[{f.severity.upper()}] {f.device}: {f.message}")

    unchecked = 0
    for name in sorted(devices):
        d = devices[name]
        if not d.unparsed:
            continue
        unchecked += len(d.unparsed)
        print(f"\n[NOT CHECKED] {name}: {len(d.unparsed)} line(s) the tool does not understand")
        for u in d.unparsed:
            where = f"{u.context}: " if u.context else ""
            print(f"    {where}{u.line}")

    print(f"\n{len(findings)} problem(s) found.")
    if unchecked:
        print(f"{unchecked} line(s) not checked.")

    if args.doc:
        Path(args.doc).write_text(generate_doc(devices, links, findings))
        print(f"Wrote {args.doc}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
