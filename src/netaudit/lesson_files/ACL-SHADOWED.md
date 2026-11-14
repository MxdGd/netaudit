# ACL-SHADOWED: Rules after a match-everything rule never run

## What it catches
A rule that matches all traffic (such as `permit ip any any`) followed by more rules.

## Why it breaks
The router reads an ACL from top to bottom and stops at the first rule that matches. A rule that matches everything, like permit ip any any, therefore makes every rule below it unreachable, so those rules never do anything.

## How to fix it
Move the match-everything rule to the end of the ACL.
