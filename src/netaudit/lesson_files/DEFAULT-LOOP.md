# DEFAULT-LOOP: Default routes pointing at each other

## What it catches
Two routers whose default routes (0.0.0.0/0) each point at the other one.

## Why it breaks
A default route means: if you do not know where this goes, give it to that neighbor. If two routers each give unknown traffic to the other, the packet bounces between them. Each hop lowers its TTL by one and at zero the packet is dropped, so the ping fails and the link is briefly flooded.

## How to fix it
Point only one router's default route at the other, and send the other's toward the real exit.
