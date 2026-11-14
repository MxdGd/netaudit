# STATIC-NEXTHOP: Static route with an unusable next hop

## What it catches
A static route whose next hop is not in a connected subnet, is the router's own address, or sits behind a shut-down interface. As a warning: no device in the lab owns the next hop.

## Why it breaks
A router can only use a static route if it can reach the next hop directly, through a connected subnet. If the next hop is outside every connected subnet, is the router's own address, or sits behind a shut-down interface, the route cannot be used and traffic for that network is dropped.

## How to fix it
Use a next hop in a directly connected subnet, owned by the neighbor, and bring the interface up.
