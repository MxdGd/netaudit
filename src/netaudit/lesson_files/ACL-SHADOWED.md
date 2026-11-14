# ACL-SHADOWED: Rules after a match-everything rule never run

## What it catches
A rule that matches all traffic (such as `permit ip any any`) followed by more rules.

## Why it breaks
TODO: write this in your own words (2 to 4 plain sentences).

## How to fix it
Move the match-everything rule to the end of the ACL.
