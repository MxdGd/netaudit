"""Vendor-neutral description of a network device.

Parsers fill these in; checks read them. Checks never see config syntax.
"""
from dataclasses import dataclass, field
from ipaddress import IPv4Interface


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
class Device:
    hostname: str = ""
    interfaces: dict[str, Interface] = field(default_factory=dict)
    ospf: Ospf | None = None
