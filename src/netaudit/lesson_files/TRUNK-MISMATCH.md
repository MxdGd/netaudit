# TRUNK-MISMATCH: The two ends of a switch link disagree

## What it catches
A switch-to-switch link where the ends differ in port mode, access VLAN or native VLAN, or (as a warning) in the allowed VLANs.

## Why it breaks
Both ends of a switch link must be set up the same way. If one end is a trunk and the other an access port, tagged traffic breaks. If the native VLANs differ, untagged traffic lands in a different VLAN on each side. If a VLAN is allowed on only one end, it does not cross the link.

## How to fix it
Configure both ends of the link the same way.
