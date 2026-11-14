# ACL-UNDEFINED: ACL applied but not defined

## What it catches
An interface uses `ip access-group NAME` but no ACL with that name or number exists. On Cisco IOS an undefined ACL lets all traffic through.

## Why it breaks
TODO: write this in your own words (2 to 4 plain sentences).

## How to fix it
Define the ACL, or fix the name on the `ip access-group` line.
