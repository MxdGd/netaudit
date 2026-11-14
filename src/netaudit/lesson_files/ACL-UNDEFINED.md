# ACL-UNDEFINED: ACL applied but not defined

## What it catches
An interface uses `ip access-group NAME` but no ACL with that name or number exists. On Cisco IOS an undefined ACL lets all traffic through.

## Why it breaks
On Cisco IOS an interface that applies an ACL which does not exist lets all traffic through. You believe traffic is being filtered, but nothing is, which makes this a security problem and not only a typo.

## How to fix it
Define the ACL, or fix the name on the `ip access-group` line.
