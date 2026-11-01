import sys
from pathlib import Path

from netaudit.audit import audit
from netaudit.parsers.frr import parse_frr


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python -m netaudit CONFIG_FILE [CONFIG_FILE ...]")
        return 2
    problems = 0
    for path in sys.argv[1:]:
        device = parse_frr(Path(path).read_text())
        findings = audit(device)
        for f in findings:
            print(f"[{f.severity.upper()}] {f.device}: {f.message}")
        problems += len(findings)
    print(f"\n{problems} problem(s) found.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
