# SHUTDOWN-IP: Interface with an IP address is shut down

## What it catches
An interface that has an IP address but is administratively shut down.

## Why it breaks
TODO: write this in your own words (2 to 4 plain sentences).

## How to fix it
Run `no shutdown` on the interface, or remove the IP address if the port is meant to be unused.
