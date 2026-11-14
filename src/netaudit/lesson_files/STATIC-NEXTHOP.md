# STATIC-NEXTHOP: Static route with an unusable next hop

## What it catches
A static route whose next hop is not in a connected subnet, is the router's own address, or sits behind a shut-down interface. As a warning: no device in the lab owns the next hop.

## Why it breaks
TODO: write this in your own words (2 to 4 plain sentences).

## How to fix it
Use a next hop in a directly connected subnet, owned by the neighbor, and bring the interface up.
