# STATIC-RETURN: Missing return route

## What it catches
A static route toward a router that has no route back to the networks behind the sender (a warning, because OSPF is not simulated).

## Why it breaks
A ping needs two trips: the request and the reply. If the far router has no route back to the sender's network, the request arrives but the reply is dropped, so the ping fails. This is a warning because OSPF might teach the far router that route, and this tool does not simulate OSPF.

## How to fix it
Add a route back on the far router, or a default route, or let OSPF teach it.
