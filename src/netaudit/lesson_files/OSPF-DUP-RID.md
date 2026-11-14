# OSPF-DUP-RID: Duplicate OSPF router ID

## What it catches
Two routers in the lab use the same OSPF router ID.

## Why it breaks
The router ID is the name tag a router puts on everything it announces. If two routers use the same tag, the others cannot tell who announced what, so routes can go missing or keep flapping.

## How to fix it
Give each router its own `router-id`.
