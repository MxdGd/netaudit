# VLAN-UNDEFINED: VLAN used but not defined

## What it catches
An access port in a VLAN that is not defined on the switch, or (as a warning) a trunk that allows an undefined VLAN.

## Why it breaks
TODO: write this in your own words (2 to 4 plain sentences).

## How to fix it
Create the VLAN with `vlan N`, or move the port to a VLAN that exists.
