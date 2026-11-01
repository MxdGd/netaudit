# Network documentation

## Devices

| Device | OSPF router-id | Interfaces |
|---|---|---|
| r1 | 1.1.1.1 | 2 |
| r2 | 2.2.2.2 | 3 |
| r3 | 3.3.3.3 | 2 |
| sw1 | - | 4 |

## IP addressing

| Device | Interface | IP | Subnet | OSPF area | Config state |
|---|---|---|---|---|---|
| r1 | lo | 1.1.1.1/32 | 1.1.1.1/32 | 0 | up |
| r1 | eth1 | 10.0.12.1/30 | 10.0.12.0/30 | 0 | up |
| r2 | lo | 2.2.2.2/32 | 2.2.2.2/32 | 0 | up |
| r2 | eth1 | 10.0.12.2/30 | 10.0.12.0/30 | 0 | up |
| r2 | eth2 | 10.0.23.1/30 | 10.0.23.0/30 | 0 | up |
| r3 | lo | 3.3.3.3/32 | 3.3.3.3/32 | 0 | up |
| r3 | eth1 | 10.0.23.2/30 | 10.0.23.0/30 | 0 | up |
| sw1 | FastEthernet0/1 | - | - | - | up |
| sw1 | FastEthernet0/2 | - | - | - | up |
| sw1 | GigabitEthernet0/1 | - | - | - | up |
| sw1 | Vlan10 | 192.168.10.2/24 | 192.168.10.0/24 | - | up |

## Links

| End A | End B | Subnet |
|---|---|---|
| r1:eth1 | r2:eth1 | 10.0.12.0/30 |
| r2:eth2 | r3:eth1 | 10.0.23.0/30 |

## OSPF

### r1

- Router ID: 1.1.1.1
- network 1.1.1.1/32 area 0
- network 10.0.12.0/30 area 0

### r2

- Router ID: 2.2.2.2
- network 2.2.2.2/32 area 0
- network 10.0.12.0/30 area 0
- network 10.0.23.0/30 area 0

### r3

- Router ID: 3.3.3.3
- network 3.3.3.3/32 area 0
- network 10.0.23.0/30 area 0

## Static routes

| Device | Prefix | Via |
|---|---|---|
| r1 | 192.168.100.0/24 | 10.0.12.2 |

## VLANs

| Device | VLAN | Name |
|---|---|---|
| sw1 | 10 | SALES |
| sw1 | 20 | HR |

## Switchports

| Device | Interface | Mode | Access VLAN | Trunk allowed | Native VLAN |
|---|---|---|---|---|---|
| sw1 | FastEthernet0/1 | access | 10 | - | - |
| sw1 | FastEthernet0/2 | access | 20 | - | - |
| sw1 | GigabitEthernet0/1 | trunk | - | 10,20 | 1 |

## Not checked

_Every line was understood._

## Audit findings

No problems found.
