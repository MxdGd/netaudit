"""Vendor-neutral description of a network device.

Parsers fill these in; checks read them. Checks never see config syntax.
"""
from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv4Interface, IPv4Network


@dataclass
class Interface:
    name: str
    ip: IPv4Interface | None = None
    ospf_network: str | None = None
    shutdown: bool = False
    switchport_mode: str | None = None  # "access" or "trunk"
    access_vlan: int | None = None  # None means the default, VLAN 1
    trunk_allowed: set[int] | None = None  # None means all VLANs
    native_vlan: int | None = None  # None means the default, VLAN 1
    acl_in: str | None = None  # name or number of the ACL applied inbound
    acl_out: str | None = None  # name or number of the ACL applied outbound


@dataclass
class Ospf:
    router_id: str | None = None
    networks: list[tuple[str, str]] = field(default_factory=list)  # (prefix, area)


@dataclass
class StaticRoute:
    prefix: IPv4Network
    next_hop: IPv4Address | None = None
    interface: str | None = None  # set when the route names an exit interface


@dataclass
class AclRule:
    action: str  # "permit" or "deny"
    protocol: str  # "ip", "tcp", ...; empty for a standard ACL
    source: str  # "any", "host 10.0.0.1" or "10.0.0.0 0.0.0.255"
    destination: str  # same forms; empty for a standard ACL
    line: str  # the rule as written, for messages


@dataclass
class Unparsed:
    """A config line the parser did not understand, so nothing was checked about it."""
    line: str
    context: str = ""  # for example "interface eth1"; empty for a top-level line


@dataclass
class Device:
    hostname: str = ""
    interfaces: dict[str, Interface] = field(default_factory=dict)
    ospf: Ospf | None = None
    static_routes: list[StaticRoute] = field(default_factory=list)
    vlans: dict[int, str] = field(default_factory=dict)  # VLAN id -> name
    unparsed: list[Unparsed] = field(default_factory=list)
    acls: dict[str, list[AclRule]] = field(default_factory=dict)  # ACL name -> rules, in order


@dataclass
class Link:
    a_device: str
    a_iface: str
    b_device: str
    b_iface: str
