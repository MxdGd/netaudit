# ACL-MASK: Subnet mask written where a wildcard belongs

## What it catches
An ACL rule that uses a subnet mask (like 255.255.255.0) where a wildcard mask (like 0.0.0.255) belongs.

## Why it breaks
ACLs use wildcard masks, where a 0 bit must match and a 1 bit is ignored. A subnet mask such as 255.255.255.0 does the opposite: the router ignores the first three parts of the address and only looks at the last one, so the rule matches the wrong addresses.

## How to fix it
Write the wildcard mask, which is the subnet mask flipped.
