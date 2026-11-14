import argparse
import sys
from pathlib import Path

from netaudit.audit import audit_network
from netaudit.docgen import generate_doc
from netaudit.htmlgen import generate_html
from netaudit.links import parse_links
from netaudit.lessons import known_ids, lesson_text
from netaudit.parsers import parse_file


def main() -> int:
    ap = argparse.ArgumentParser(prog="netaudit", description="Audit network device configs.")
    ap.add_argument("configs", nargs="*", help="device config files (.ios = IOS syntax, else FRR)")
    ap.add_argument("--links", help="file listing which interfaces are cabled together")
    ap.add_argument("--doc", help="also write a Markdown report to this file")
    ap.add_argument("--html", help="also write a self-contained HTML report to this file")
    ap.add_argument("--explain", metavar="ID", help="print the lesson for a check ID and exit")
    args = ap.parse_args()

    if args.explain:
        text = lesson_text(args.explain.upper())
        if text is None:
            print(f"Unknown check ID {args.explain!r}. Valid IDs: {', '.join(known_ids())}",
                  file=sys.stderr)
            return 2
        print(text)
        return 0
    if not args.configs:
        ap.error("give at least one config file, or use --explain ID")

    devices = {}
    for path in args.configs:
        device = parse_file(path)
        devices[device.hostname] = device
    links = parse_links(Path(args.links).read_text(encoding="utf-8")) if args.links else []

    findings = audit_network(devices, links)
    for f in findings:
        print(f"[{f.severity.upper()}] {f.device}: {f.message}  ({f.check})")

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
    if findings:
        print(f"Run 'netaudit --explain {findings[0].check}' for a short lesson on a check.")

    if args.doc:
        Path(args.doc).write_text(generate_doc(devices, links, findings), encoding="utf-8")
        print(f"Wrote {args.doc}")
    if args.html:
        Path(args.html).write_text(generate_html(devices, links, findings), encoding="utf-8")
        print(f"Wrote {args.html}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
