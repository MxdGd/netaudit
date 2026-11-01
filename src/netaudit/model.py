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
class Device:
    hostname: str = ""
    interfaces: dict[str, Interface] = field(default_factory=dict)
    ospf: Ospf | None = None
    static_routes: list[StaticRoute] = field(default_factory=list)


@dataclass
class Link:
    a_device: str
    a_iface: str
    b_device: str
    b_iface: str
