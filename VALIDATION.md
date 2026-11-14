# Validation

What netaudit checks, how it is tested, and what it does NOT do.

## How it is tested

- Every check has automated tests (run `pytest`). Each test feeds the tool a
  sample config and asserts the exact result: the good sample must produce no
  findings, and each file in `samples/broken/` carries one deliberate mistake
  and must produce the expected finding.
- The sample configs are small and hand-written. The tool has not been run on
  large or real-world configs.
- A test fails if any check ID has no lesson, or if a lesson still has a `TODO`.
- The HTML report is tested for escaping (a hostile hostname cannot inject
  markup), for containing no scripts and no external links, and for the
  `--html` option writing a file. How it looks in a browser was checked by hand.
- A clean install (`python3 -m venv /tmp/fresh && /tmp/fresh/bin/pip install .`)
  was run to confirm the lesson files ship with the package.
- The FRR sample lab (r1, r2, r3) was run once in a Containerlab lab early in
  the project: OSPF neighbors reached Full and r1 could ping r3. The static
  route on r1 and the IOS switch samples (sw1, sw2) were never run on real or
  virtual devices; they are tested only as text files.

## Checks implemented

Every check has an ID. `netaudit --explain ID` prints a short lesson on it.

| ID | Check | Severity |
|---|---|---|
| `SHUTDOWN-IP` | Interface with an IP address that is shut down | error |
| `LINK-SUBNET` | Two ends of a cable in different subnets | error |
| `LINK-SUBNET` | Same IP on both ends of a cable | error |
| `LINK-SUBNET` | A cable end that is missing from the configs | error |
| `LINK-SUBNET` | One end of a cable has no IP address | warning |
| `OSPF-COVERAGE` | Interface with an IP not covered by any `network` statement | error |
| `OSPF-LINK` | Area mismatch between the two ends of a link | error |
| `OSPF-LINK` | Network type mismatch between the two ends of a link | error |
| `OSPF-DUP-RID` | Two routers with the same OSPF router ID | error |
| `STATIC-NEXTHOP` | Next hop not in any connected subnet | error |
| `STATIC-NEXTHOP` | Next hop is the device's own address | error |
| `STATIC-NEXTHOP` | Interface toward the next hop is shut down | error |
| `STATIC-NEXTHOP` | Next hop address not owned by any device in the lab | warning |
| `STATIC-RETURN` | Static route via a router that has no route back to the sender's networks | warning |
| `DEFAULT-LOOP` | Two routers whose default routes point at each other | error |
| `VLAN-UNDEFINED` | Access port in a VLAN that is not defined on the switch | error |
| `VLAN-UNDEFINED` | Trunk allows a VLAN that is not defined on the switch | warning |
| `TRUNK-MISMATCH` | Switchport mode mismatch between the two ends of a link | error |
| `TRUNK-MISMATCH` | Access VLAN mismatch between the two ends of a link | error |
| `TRUNK-MISMATCH` | Native VLAN mismatch between the two ends of a link | error |
| `TRUNK-MISMATCH` | Allowed-VLAN list mismatch between the two ends of a link | warning |
| `ACL-UNDEFINED` | Interface applies an ACL that is not defined | error |
| `ACL-UNUSED` | ACL defined but not applied to any interface | warning |
| `ACL-SHADOWED` | Rules after a rule that matches all traffic | warning |
| `ACL-MASK` | Subnet mask written where a wildcard mask belongs | error |

## Known limits and blind spots

- Static analysis only. The tool reads config files. It never connects to a
  device, so it cannot see live state: a link that is physically down, a
  neighbor that failed to form, or the real routing table. The "Config state"
  column in the generated document shows what the config says, not what the
  device is doing.
- Lines the parser does not understand are reported as `[NOT CHECKED]` and
  appear in the generated reports, so nothing is ignored silently. But a line
  that is understood and then misjudged can still give a wrong finding.
- Cabling comes from a hand-written links file. The tool does not verify that
  the file matches reality.
- IPv4 only. IPv6 is not parsed or checked.
- OSPF is understood only through `network` statements and the interface
  `ip ospf network` command. OSPF enabled per interface (`ip ospf area`),
  passive interfaces, timers and authentication are not understood, so a
  config that uses them can produce false findings or miss real ones.
- A duplicate IP is detected only between the two ends of one cable, not
  across the whole network.
- Static routes that name an exit interface instead of a next hop are parsed
  but not checked.
- IOS parser: `interface range`, `allowed vlan remove` and `allowed vlan
  except` stop with an error on purpose. Secondary IP addresses are not
  supported. Normal-range VLANs that a real switch keeps in `vlan.dat` do not
  appear in `show running-config`, so a config copied from such a switch can
  show a VLAN as undefined when it actually exists.
- One mistake can produce several findings (for example, a wrong subnet also
  leaves the address outside its OSPF network statement).
- Severity levels are a judgement call, not a standard.
- Shut-down interfaces without an IP address are not reported, because unused
  interfaces are shut down on purpose. A cabled interface without an IP that is
  shut down is not caught yet.
- An interface that no OSPF network statement covers is reported as an error
  even when it was left out on purpose (for example a LAN reached by a static
  route).
- IOS routers: OSPF is read from `router ospf N` (router-id and network
  statements). Passive interfaces, costs, timers and other options, and static
  routes with an administrative distance or other extra options, are reported
  as NOT CHECKED. Unused-port boilerplate such as `duplex auto` is ignored.

- `STATIC-RETURN` is a warning, not an error, and only looks one hop away: at
  the router that owns the next hop. It skips networks that the sender
  advertises in OSPF when the far router also runs OSPF, because OSPF may teach
  the route and the tool does not simulate OSPF. A default route on the far
  router counts as a way back.
- `DEFAULT-LOOP` only finds two routers pointing at each other. A loop through
  three or more routers is not found. Only static default routes are read.
- `OSPF-DUP-RID` only compares router IDs written in the config. A router that
  picks its ID automatically is not compared, because that needs OSPF
  simulation.
- ACL checks work on IOS syntax only; the FRR parser does not read ACLs. Named
  and numbered ACLs are read. A rule with options the parser does not know
  (for example `dscp`) is reported as NOT CHECKED, and the rest of the ACL is
  still read. Port tests such as `eq 80` are skipped, not evaluated.
- `ACL-UNUSED` is a warning because NAT, VTY lines and route maps can also use
  an ACL, and the tool does not read those yet.
- `ACL-SHADOWED` only looks for rules that match all traffic. It does not find
  a narrower rule hiding an even narrower one.
- `ACL-MASK` flags any ACL address whose second part looks like a subnet mask
  (ones then zeros, for example 255.255.255.0). A real wildcard of that shape,
  such as 255.0.0.0, is legal and would be flagged by mistake, but it is rare.

## Not implemented yet

A VLAN defined on one switch but missing on the other, DTP negotiation, VLAN
pruning, NAT, DHCP, STP, EtherChannel, port security, plain-text password and
SSH checks, ACLs on FRR, ACLs used by NAT, route maps or VTY lines, and reading
configs live from devices.
