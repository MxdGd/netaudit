# SHUTDOWN-IP: Interface with an IP address is shut down

## What it catches
An interface that has an IP address but is administratively shut down.

## Why it breaks
A shut-down interface is switched off: no traffic goes in or out and the link shows as down, even though an IP address is configured. Routes that use it disappear and OSPF neighbors behind it are lost. It is often a leftover from troubleshooting.

## How to fix it
Run `no shutdown` on the interface, or remove the IP address if the port is meant to be unused.
