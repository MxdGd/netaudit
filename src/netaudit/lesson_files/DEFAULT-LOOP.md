# DEFAULT-LOOP: Default routes pointing at each other

## What it catches
Two routers whose default routes (0.0.0.0/0) each point at the other one.

## Why it breaks
TODO: write this in your own words (2 to 4 plain sentences).

## How to fix it
Point only one router's default route at the other, and send the other's toward the real exit.
