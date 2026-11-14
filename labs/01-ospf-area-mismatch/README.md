# Lab 01: OSPF area mismatch

## Goal

Two routers (built in Packet Tracer, saved with `show running-config`) must
become OSPF neighbors. This lab shows what netaudit says when one of them is
configured with a different OSPF area than the other.

## Files

- `r1.ios`: router 1.
- `r2-fixed.ios`: router 2, correct.
- `r2.ios`: router 2 with one planted mistake.
- `links.txt`: which interfaces are cabled together.

## The planted mistake

The only difference between the correct and the broken router 2:

```diff
--- r2-fixed.ios
+++ r2.ios
@@ -20,3 +20,3 @@
  network 2.2.2.2 0.0.0.0 area 0
- network 10.0.12.0 0.0.0.3 area 0
+ network 10.0.12.0 0.0.0.3 area 1
  network 192.168.100.0 0.0.0.255 area 0
```

## Run it

First the correct lab. It should be clean:

```
$ netaudit --links links.txt r1.ios r2-fixed.ios
0 problem(s) found.
```

Now the broken one:

```
$ netaudit --links links.txt --doc report.md r1.ios r2.ios
[ERROR] R1<->R2: OSPF area mismatch: R1 GigabitEthernet0/0 is in area 0, R2 GigabitEthernet0/0 is in area 1  (OSPF-LINK)

1 problem(s) found.
Run 'netaudit --explain OSPF-LINK' for a short lesson on a check.
Wrote report.md
```

`report.md` is the generated documentation. GitHub draws its topology diagram
by itself, with the broken link in red: [report.md](report.md).

## Why it breaks

Run `netaudit --explain OSPF-LINK` for the short lesson. In short: two OSPF
neighbors only form an adjacency if their hellos agree, and the area is part of
that agreement.

## What to try next

Fix the mistake in `r2.ios` and run the tool again. It should print
`0 problem(s) found.`
