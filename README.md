# netaudit

A config auditor and auto-documenter for small networks.
It reads device configs, reports what is wrong or missing, and generates documentation.

**Status:** work in progress. It currently parses FRRouting configs
(interfaces, IP addresses, OSPF) and reports interfaces that are shut down.

## Try it

    python3 -m venv .venv
    source .venv/bin/activate
    pip install pytest
    pytest
    PYTHONPATH=src python -m netaudit samples/broken/r2_shutdown.conf

## Example output

Documentation generated for the sample lab: [docs/example-report.md](docs/example-report.md)

## Validation

What is tested and what is not: [VALIDATION.md](VALIDATION.md)
