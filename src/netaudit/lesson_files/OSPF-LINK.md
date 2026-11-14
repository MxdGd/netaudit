# OSPF-LINK: OSPF settings differ across a link

## What it catches
The two ends of a link run OSPF in different areas, or with different network types.

## Why it breaks
Two OSPF neighbors only form an adjacency if their hellos agree. Different areas make the hellos get rejected. A different network type changes the timers and how the designated router is chosen, so the neighbors may never become fully adjacent.

## How to fix it
Put both ends in the same area and set the same `ip ospf network` type on both.
