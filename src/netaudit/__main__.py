import argparse
import sys
from pathlib import Path

from netaudit.audit import audit_network
from netaudit.docgen import generate_doc
from netaudit.links import parse_links
from netaudit.parsers.frr import parse_frr


def main() -> int:
    ap = argparse.ArgumentParser(prog="netaudit", description="Audit network device configs.")
    ap.add_argument("configs", nargs="+", help="device config files")
    ap.add_argument("--links", help="file listing which interfaces are cabled together")
    ap.add_argument("--doc", help="also write a Markdown report to this file")
    args = ap.parse_args()

    devices = {}
    for path in args.configs:
        device = parse_frr(Path(path).read_text())
        devices[device.hostname] = device
    links = parse_links(Path(args.links).read_text()) if args.links else []

    findings = audit_network(devices, links)
    for f in findings:
        print(f"[{f.severity.upper()}] {f.device}: {f.message}")
    print(f"\n{len(findings)} problem(s) found.")

    if args.doc:
        Path(args.doc).write_text(generate_doc(devices, links, findings))
        print(f"Wrote {args.doc}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
