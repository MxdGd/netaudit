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

## Plan

**Rule: anyone can run it.** The core needs only Python 3.10+ and config
files. Reading a GNS3 lab live and the chat are optional extras, and the tool
says clearly when they are not set up. Nothing is specific to one computer. A
clean install is tested for every release, and CI will run the tests on Linux,
macOS and Windows.

**v1**

1. Installable package with a `netaudit` command (done)
2. Topology diagram in the generated report (done)
3. IOS router parser, so Packet Tracer labs work
4. Check groups in order of CCNA weight: routing, ACLs, NAT and DHCP, layer 2
   extras, basics. Each check comes with a short lesson.
5. Local read-only window (`netaudit serve`): reads a GNS3 lab directly, or
   configs pasted from Packet Tracer. Shows the diagram, findings labeled
   VERIFIED, NOT CHECKED lines, and a chat labeled AI EXPLANATION (optional
   free-tier key).
6. README that leads with the networking problems it catches, a `labs/` folder
   of lab write-ups, demo GIF, tagged release

**After v1**

- AI-drafted check proposals, reviewed by a person
- Intent file, then snapshots and config diff
- Reachability trace
- Live Packet Tracer connection (Packet Tracer has no simple outside interface)
