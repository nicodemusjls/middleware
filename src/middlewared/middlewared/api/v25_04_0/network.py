from enum import Enum

from middlewared.api.base import BaseModel, Excluded, excluded_field
from pydantic import IPvAnyAddress, Field

__all__ = [
    "NetworkSaveDefaultRouteArgs",
    "NetworkSaveDefaultRouteResult",
    "NetworkInterfaceEntry",
    "NetworkInterfaceCreateArgs",
    "NetworkInterfaceUpdateArgs",
    "NetworkInterfaceCreateResult",
    "NetworkGeneralSummaryArgs",
    "NetworkGeneralSummaryResult"
]

class NetworkSaveDefaultRouteArgs(BaseModel):
    gateway: IPvAnyAddress

class NetworkSaveDefaultRouteResult(BaseModel):
    pass


class NetworkInterfaceTypeEnum(str, Enum):
    BRIDGE = "BRIDGE"
    LINK_AGGREGATION = "LINK_AGGREGATION"
    VLAN = "VLAN"

class NetworkInterfaceAddrTypeEnum(str, Enum):
    INET = "INET"
    INET6 = "INET6"

class NetworkInterfaceLagProtocolEnum(str, Enum):
    LACP = "LACP"
    FAILOVERR = "FAILOVER"
    LOADBALANCE = "LOADBALANCE"
    ROUNDROBIN = "ROUNDROBIN"
    NONE = "NONE"

class XmitHashChoices(str, Enum):
    LAYER2 = "LAYER2"
    LAYER23 = "LAYER2+3"
    LAYER34 = "LAYER3+4"

class LacpduRateChoices(str, Enum):
    SLOW = 'SLOW'
    FAST = 'FAST'

class NetworkInterfaceFailoverAlias(BaseModel):
    type: NetworkInterfaceAddrTypeEnum
    address: IPvAnyAddress

class NetworkInterfaceAlias(NetworkInterfaceFailoverAlias):
    netmask: int

class NetworkInterfaceEntry(BaseModel):
    name: str
    description: str = ''
    type: NetworkInterfaceTypeEnum
    ipv4_dhcp: bool = False
    ipv6_auto: bool = False
    aliases: list[NetworkInterfaceAlias]
    failover_critical: bool = False
    failover_group: int
    failover_vhid: int = Field(ge=1, le=255)
    failover_aliases: list[NetworkInterfaceFailoverAlias]
    failover_virtual_aliases: list[NetworkInterfaceFailoverAlias]
    bridge_members: list
    enable_learning: bool = True
    stp: bool = True
    lag_protocol: NetworkInterfaceLagProtocolEnum
    xmit_hash_policy: XmitHashChoices | None = None
    lacpdu_rate: LacpduRateChoices | None = None
    lag_ports: list[str]
    vlan_parent_interface: str
    vlan_tag: int = Field(ge=1, le=4094)
    vlan_pcp: int = Field(ge=0, le=7)
    mtu: int = Field(None, ge=68, le=9216)

class NetworkInterfaceCreateArgs(BaseModel):
    data: NetworkInterfaceEntry

class NetworkInterfaceCreateResult(BaseModel):
    pass

class NetworkInterfaceUpdateArgs(BaseModel):
    id: Excluded = excluded_field()
    data: NetworkInterfaceEntry



class NetworkGeneralSummaryArgs(BaseModel):
    pass

class NetworkGeneralSummaryEntry(BaseModel):
    ips: dict
    default_routes: list[str]
    nameservers: list[str]

class NetworkGeneralSummaryResult(BaseModel):
    result: NetworkGeneralSummaryEntry
