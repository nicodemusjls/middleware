from enum import Enum
from typing_extensions import Literal

from middlewared.api.base import BaseModel, Excluded, excluded_field, ForUpdateMetaclass
from pydantic import IPvAnyAddress, Field

__all__ = [
    "NetworkSaveDefaultRouteArgs", "NetworkSaveDefaultRouteResult",
    "NetworkGeneralSummaryArgs", "NetworkGeneralSummaryResult",
    "NetworkCommitArgs", "NetworkCommitResult",
    "NetworkCheckinWaitingArgs", "NetworkCheckinWaitingResult",
    "NetworkCancelRollbackArgs", "NetworkCancelRollbackResult",
    "NetworkCheckinArgs", "NetworkCheckinResult",
    "NetworkRollbackArgs", "NetworkRollbackResult",
    "NetworkHasPendingChangesArgs", "NetworkHasPendingChangesResult",
    "NetworkDefaultRouteWillBeRemovedArgs", "NetworkDefaultRouteWillBeRemovedResult",
    "NetworkInterfaceIpInUseArgs", "NetworkInterfaceIpInUseResult",
    "NetworkVlanParentInterfaceChoicesArgs", "NetworkVlanParentInterfaceChoicesResult",
    "NetworkLagPortsChoicesArgs", "NetworkLagPortsChoicesResult",
    "NetworkBridgeMembersChoicesArgs", "NetworkBridgeMembersChoicesResult",
    "NetworkChoicesArgs", "NetworkChoicesResult",
    "NetworkLacpduRateChoicesArgs", "NetworkLacpduRateChoicesResult",
    "XmitHashPolicyChoicesArgs", "XmitHashPolicyChoicesResult",
    "NetworkWebsocketInterfaceArgs", "NetworkWebsocketInterfaceResult",
    "NetworkWebsocketLocalIpArgs", "NetworkWebsocketLocalIpResult",
    "NetworkInterfaceCreateArgs", "NetworkInterfaceCreateResult",
    "NetworkInterfaceUpdateArgs", "NetworkInterfaceUpdateResult",
]

class NetworkWebsocketLocalIpArgs(BaseModel):
    pass

class NetworkWebsocketLocalIpResult(BaseModel):
    result: IPvAnyAddress | None


class NetworkWebsocketInterfaceArgs(BaseModel):
    pass

class NetworkWebsocketInterfaceResult(BaseModel):
    result: str | None


class XmitHashPolicyChoicesArgs(BaseModel):
    pass

class XmitHashPolicyChoicesResult(BaseModel):
    result: dict


class NetworkLacpduRateChoicesArgs(BaseModel):
    pass

class NetworkLacpduRateChoicesResult(BaseModel):
    result: dict


class NetworkInterfaceChoicesTypeEnum(str, Enum):
    BRIDGE = "BRIDGE"
    LINK_AGGREGATION = "LINK_AGGREGATION"
    PHYSICAL = "PHYSICAL"
    UNKNOWN = "UNKNOWN"
    VLAN = "VLAN"

class NetworkChoicesArgsData(BaseModel):
    bridge_members: bool = False
    lag_ports: bool = False
    vlan_parent: bool = True
    exclude: list[str] = ["epair", "tap", "vnet"]
    exclude_types: list[NetworkInterfaceChoicesTypeEnum] = []
    include: list = []

class NetworkChoicesArgs(BaseModel):
    options: NetworkChoicesArgsData

class NetworkChoicesResult(BaseModel):
    result: dict


class NetworkBridgeMembersChoicesArgs(BaseModel):
    id: str | None = None

class NetworkBridgeMembersChoicesResult(BaseModel):
    result: dict


class NetworkLagPortsChoicesArgs(BaseModel):
    id: str | None = None

class NetworkLagPortsChoicesResult(BaseModel):
    result: dict


class NetworkVlanParentInterfaceChoicesArgs(BaseModel):
    pass

class NetworkVlanParentInterfaceChoicesResult(BaseModel):
    result: dict


class NetworkInterfaceIpInUseChoices(BaseModel):
    ipv4: bool = True
    ipv6: bool = True
    ipv6_link_local: bool = False
    loopback: bool = False
    any: bool = False
    static: bool = False

class NetworkInterfaceIpInUseArgs(BaseModel):
    data: NetworkInterfaceIpInUseChoices = NetworkInterfaceIpInUseChoices()

class NetworkInterfaceIpInUseResultItem(BaseModel):
    type: str
    address: IPvAnyAddress
    netmask: int
    broadcast: str

class NetworkInterfaceIpInUseResult(BaseModel):
    result: list[NetworkInterfaceIpInUseResultItem]


class NetworkDefaultRouteWillBeRemovedArgs(BaseModel):
    pass

class NetworkDefaultRouteWillBeRemovedResult(BaseModel):
    result: bool


class NetworkHasPendingChangesArgs(BaseModel):
    pass

class NetworkHasPendingChangesResult(BaseModel):
    result: bool


class NetworkRollbackArgs(BaseModel):
    pass

class NetworkRollbackResult(BaseModel):
    result: None


class NetworkCheckinArgs(BaseModel):
    pass

class NetworkCheckinResult(BaseModel):
    result: None


class NetworkCancelRollbackArgs(BaseModel):
    pass

class NetworkCancelRollbackResult(BaseModel):
    result: None


class NetworkCheckinWaitingResultItem(BaseModel):
    remaining_seconds: int | None

class NetworkCheckinWaitingResult(BaseModel):
    result: NetworkCheckinWaitingResultItem

class NetworkCheckinWaitingArgs(BaseModel):
    pass

class NetworkCommitOptions(BaseModel):
    rollback: bool = True
    checkin_timeout: int = 60


class NetworkCommitArgs(BaseModel):
    options: NetworkCommitOptions

class NetworkCommitResult(BaseModel):
    result: None


class NetworkSaveDefaultRouteArgs(BaseModel):
    gateway: IPvAnyAddress

class NetworkSaveDefaultRouteResult(BaseModel):
    result: None


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
    SLOW = "SLOW"
    FAST = "FAST"

class NetworkInterfaceFailoverAlias(BaseModel):
    type: NetworkInterfaceAddrTypeEnum | None = None
    address: IPvAnyAddress | None = None

class NetworkInterfaceAlias(NetworkInterfaceFailoverAlias):
    netmask: int

class NetworkInterfaceEntry(BaseModel):
    description: str = ''
    ipv4_dhcp: bool = False
    ipv6_auto: bool = False
    aliases: list[NetworkInterfaceAlias] = []
    failover_critical: bool = False
    failover_group: int | None = None
    failover_vhid: int | None = Field(None, ge=1, le=255)
    failover_aliases: list[NetworkInterfaceFailoverAlias] = []
    failover_virtual_aliases: list[NetworkInterfaceFailoverAlias] = []
    bridge_members: list = []
    enable_learning: bool = True
    stp: bool = True
    lag_protocol: str | None = None
    xmit_hash_policy: XmitHashChoices | None = None
    lacpdu_rate: LacpduRateChoices | None = None
    lag_ports: list[str] = []
    vlan_parent_interface: str | None = None
    vlan_tag: int | None = Field(None, ge=1, le=4094)
    vlan_pcp: int | None = Field(None, ge=0, le=7)
    mtu: int = Field(None, ge=68, le=9216)
    options: str = ""

class NetworkInterfaceCreate(NetworkInterfaceEntry):
    name: str
    type: Literal["BRIDGE", "LINK_AGGREGATION", "VLAN"]

class NetworkInterfaceCreateArgs(BaseModel):
    data: NetworkInterfaceCreate

class NetworkInterfaceCreateResult(BaseModel):
    result: NetworkInterfaceEntry | None

class NetworkInterfaceUpdateResult(BaseModel):
    result: NetworkInterfaceEntry | None

class NetworkInterfaceUpdate(NetworkInterfaceEntry, metaclass=ForUpdateMetaclass):
    pass

class NetworkInterfaceUpdateArgs(BaseModel):
    id: str
    data: NetworkInterfaceUpdate


class NetworkGeneralSummaryArgs(BaseModel):
    pass

class NetworkGeneralSummaryEntry(BaseModel):
    ips: dict
    default_routes: list[str]
    nameservers: list[str]

class NetworkGeneralSummaryResult(BaseModel):
    result: NetworkGeneralSummaryEntry
