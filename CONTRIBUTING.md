# Contributing

Thank you for helping. Adding a check takes about ten minutes.

## Setup

    git clone https://github.com/MxdGd/netaudit.git
    cd netaudit
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e . pytest
    pytest

## Rules for a check

- Plain deterministic Python, no AI and no network access. The same input must
  always give the same findings.
- It reads the model in `src/netaudit/model.py`, never raw config text.
- Use `error` when the config is wrong for certain. Use `warning` when the tool
  cannot be sure (for example because it does not simulate OSPF).
- A config line the parser does not understand must go to `Unparsed`, never be
  silently ignored.

## Adding a check

1. **Write the test first** in `tests/`. Build a small config as text, parse it
   with `parse_ios` or `parse_frr`, call your check, and assert the finding. Add
   a second test where the config is fine and nothing is reported. Run `pytest`
   and watch it fail.
2. **Write the check** in `src/netaudit/audit.py`. It returns a list of
   `Finding(device, severity, message)`.
   - Looks at one device: `def check_x(device)`, then add it to the `CHECKS` list.
   - Compares devices: `def check_x(devices, links)`, then call it from
     `audit_network` as `findings.extend(_tag(check_x, check_x(devices, links)))`.
3. **Give it an ID**: add `check_x: "MY-ID"` to `CHECK_IDS` in `audit.py`.
4. **Write the lesson**: create `src/netaudit/lesson_files/MY-ID.md` with the
   sections `What it catches`, `Why it breaks` and `How to fix it`. Use plain
   words. Copy any existing lesson as a template. No `TODO` may be left in it.
5. **Update the count** in `tests/test_ids.py` (`len(CHECK_IDS) == 14`) and the
   checks table in `README.md`.
6. Run `pytest` and make sure everything passes.

## Parser changes

If your check needs data the model does not hold yet, extend `model.py` and the
parser first, with tests that prove the new lines are read, as `tests/test_acl_parser.py` does.
