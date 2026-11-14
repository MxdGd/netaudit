# VLAN-UNDEFINED: VLAN used but not defined

## What it catches
An access port in a VLAN that is not defined on the switch, or (as a warning) a trunk that allows an undefined VLAN.

## Why it breaks
A VLAN has to exist on the switch before ports can use it. As far as I know, depending on the switch model, a port in a missing VLAN is either inactive or the VLAN is created silently. Either way the config does not do what was intended. A trunk that allows an undefined VLAN is only a warning, because that VLAN simply carries nothing.

## How to fix it
Create the VLAN with `vlan N`, or move the port to a VLAN that exists.
