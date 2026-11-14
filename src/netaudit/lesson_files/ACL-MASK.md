# ACL-MASK: Subnet mask written where a wildcard belongs

## What it catches
An ACL rule that uses a subnet mask (like 255.255.255.0) where a wildcard mask (like 0.0.0.255) belongs.

## Why it breaks
TODO: write this in your own words (2 to 4 plain sentences).

## How to fix it
Write the wildcard mask, which is the subnet mask flipped.
