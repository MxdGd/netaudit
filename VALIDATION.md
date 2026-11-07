# Validation

What netaudit checks, how it is tested, and what it does NOT do.

## How it is tested

- Every check has automated tests (run `pytest`). Each test feeds the tool a
  sample config and asserts the exact result: the good sample must produce no
  findings, and each file in `samples/broken/` carries one deliberate mistake
  and must produce the expected finding.
- The sample configs are small and hand-written. The tool has not been run on
  large or real-world configs.
- The FRR sample lab (r1, r2, r3) was run once in a Containerlab lab early in
  the project: OSPF neighbors reached Full and r1 could ping r3. The static
  route on r1 and the IOS switch samples (sw1, sw2) were never run on real or
  virtual devices; they are tested only as text files.

## Checks implemented

| Area | Check | Severity |
|---|---|---|
| Interfaces | Interface with an IP address that is shut down | error |
| Links (routed) | Two ends of a cable in different subnets | error |
| Links (routed) | Same IP on both ends of a cable | error |
| OSPF | Interface with an IP not covered by any `network` statement | error |
| OSPF | Area mismatch between the two ends of a link | error |
| OSPF | Network type mismatch between the two ends of a link | error |
| Static routes | Next hop not in any connected subnet | error |
| Static routes | Next hop is the device's own address | error |
| Static routes | Interface toward the next hop is shut down | error |
| Static routes | Next hop address not owned by any device in the lab | warning |
| VLANs | Access port in a VLAN that is not defined on the switch | error |
| VLANs | Trunk allows a VLAN that is not defined on the switch | warning |
| Trunks | Switchport mode mismatch between the two ends of a link | error |
| Trunks | Access VLAN mismatch between the two ends of a link | error |
| Trunks | Native VLAN mismatch between the two ends of a link | error |
| Trunks | Allowed-VLAN list mismatch between the two ends of a link | warning |

## Known limits and blind spots

- Static analysis only. The tool reads config files. It never connects to a
  device, so it cannot see live state: a link that is physically down, a
  neighbor that failed to form, or the real routing table. The "Config state"
  column in the generated document shows what the config says, not what the
  device is doing.
- Unknown lines are ignored silently. A misspelled or unsupported command is
  not reported, and the tool will behave as if it were absent.
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

## Not implemented yet

Return routes for static routes, a VLAN defined on one switch but missing on
the other, DTP negotiation, VLAN pruning, ACLs, NAT, DHCP, STP, EtherChannel,
port security, and reading configs live from devices.
