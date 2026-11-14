# OSPF-COVERAGE: Interface not covered by an OSPF network statement

## What it catches
An active interface with an IP address that no `network` statement covers, so OSPF does not run on it.

## Why it breaks
OSPF only runs on interfaces that a network statement matches. If none matches, the interface sends no hellos, forms no neighbors, and its network is not advertised, so other routers never learn about it.

## How to fix it
Add a `network` statement whose address and wildcard mask include the interface's IP, in the right area.
