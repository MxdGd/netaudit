# OSPF-COVERAGE: Interface not covered by an OSPF network statement

## What it catches
An active interface with an IP address that no `network` statement covers, so OSPF does not run on it.

## Why it breaks
TODO: write this in your own words (2 to 4 plain sentences).

## How to fix it
Add a `network` statement whose address and wildcard mask include the interface's IP, in the right area.
