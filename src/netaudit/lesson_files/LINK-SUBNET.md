# LINK-SUBNET: The two ends of a cable do not agree

## What it catches
Both ends of a routed link must be in the same subnet and have different IPs. Reports a subnet mismatch, a duplicate IP, and a link end that is missing or has no IP.

## Why it breaks
Two devices on one cable only talk directly when their addresses are in the same subnet. If the subnets differ, each side thinks the other is far away and sends traffic to a gateway instead, so the ping fails. If both ends have the same IP, the two devices conflict and neither works reliably.

## How to fix it
Give both ends addresses from the same subnet (for example 10.0.0.1/30 and 10.0.0.2/30), each one different.
