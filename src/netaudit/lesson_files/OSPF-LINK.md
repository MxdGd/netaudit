# OSPF-LINK: OSPF settings differ across a link

## What it catches
The two ends of a link run OSPF in different areas, or with different network types.

## Why it breaks
TODO: write this in your own words (2 to 4 plain sentences).

## How to fix it
Put both ends in the same area and set the same `ip ospf network` type on both.
