# ACL-UNUSED: ACL defined but never applied

## What it catches
An ACL that no interface uses (a warning, because NAT, VTY lines and route maps can use ACLs too and are not checked yet).

## Why it breaks
An ACL does nothing until it is applied somewhere. A list that no interface uses filters nothing, which usually means a forgotten step. It is a warning because NAT, VTY lines and route maps can also use ACLs, and this tool does not read those yet.

## How to fix it
Apply it with `ip access-group NAME in` or `out`, or delete it if it is not needed.
