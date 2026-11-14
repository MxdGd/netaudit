# ACL-UNUSED: ACL defined but never applied

## What it catches
An ACL that no interface uses (a warning, because NAT, VTY lines and route maps can use ACLs too and are not checked yet).

## Why it breaks
TODO: write this in your own words (2 to 4 plain sentences).

## How to fix it
Apply it with `ip access-group NAME in` or `out`, or delete it if it is not needed.
