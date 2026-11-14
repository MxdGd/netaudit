# STATIC-RETURN: Missing return route

## What it catches
A static route toward a router that has no route back to the networks behind the sender (a warning, because OSPF is not simulated).

## Why it breaks
TODO: write this in your own words (2 to 4 plain sentences).

## How to fix it
Add a route back on the far router, or a default route, or let OSPF teach it.
