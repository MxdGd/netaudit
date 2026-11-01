# Coverage

What netaudit checks today, what is planned, and what a config file cannot
tell you. The areas follow the CCNA exam topics as I understand them; check
Cisco's current exam topics for the official list.

Status: **done** (a tested check exists), **partial** (some checks, known
gaps), **planned**, **chat only** (concepts that cannot be judged from a
config file).

| Area | Topic | Status | Notes |
|---|---|---|---|
| Network fundamentals | IPv4 addressing on a link (same subnet, duplicate IP) | partial | only the two ends of one cable are compared |
| Network fundamentals | IPv6 addressing | planned | |
| Network fundamentals | Speed and duplex mismatch | planned | such lines are reported as NOT CHECKED today |
| Network fundamentals | OSI, TCP/UDP, subnetting theory | chat only | |
| Network access | VLANs defined and used | done | |
| Network access | Trunks: mode, native VLAN, allowed VLANs | done | DTP and pruning are not covered |
| Network access | STP | planned | |
| Network access | EtherChannel | planned | |
| Network access | CDP and LLDP | planned | |
| Network access | Wireless architecture and controllers | chat only | |
| IP connectivity | Static routes | partial | no return-route check; routes naming an exit interface are not checked |
| IP connectivity | OSPF (single area) | partial | network statements, area, network type; no passive interfaces, timers or authentication |
| IP connectivity | Default routes | planned | |
| IP connectivity | First-hop redundancy (HSRP) | planned | |
| IP connectivity | Routing table theory (metric, administrative distance) | chat only | |
| IP services | NAT | planned | |
| IP services | DHCP | planned | |
| IP services | NTP, SNMP, syslog | planned | |
| IP services | SSH, QoS | planned | |
| Security | ACLs | planned | |
| Security | Port security | planned | |
| Security | DHCP snooping, DAI | planned | |
| Security | Passwords, AAA, VPN concepts | chat only | password checks may come later |
| Automation | REST, JSON, controllers | chat only | |

## How coverage grows

1. **Notice gaps.** Every config line the tool does not understand is reported
   as NOT CHECKED (done).
2. **Log gaps.** The tool keeps a local count of the lines it keeps meeting, so
   the most frequent gaps show what to build next (planned).
3. **Propose.** An AI model drafts a check, a broken sample config and a test
   for a gap and saves them in a `proposals/` folder where nothing runs
   (planned, needs the chat).
4. **Review together.** A proposal becomes a real check only after a person has
   read it, understood it, and confirmed that the good sample passes, the broken
   sample produces the expected finding, and the behavior matches the CCNA
   material. Nothing is added automatically.

## Planned order

1. A local browser window next to the lab tool: loaded configs, findings
   labeled VERIFIED, NOT CHECKED lines, and later AI answers labeled
   AI EXPLANATION.
2. IOS router parser, so Packet Tracer labs work.
3. Gap log.
4. Chat with a free-tier model.
5. Check proposals, drafted by AI and reviewed by a person.
6. Live reading from GNS3.
7. One topic group at a time from the table above.
