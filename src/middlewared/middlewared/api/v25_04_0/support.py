from middlewared.api.base import BaseModel
from pydantic import Field, SecretStr, EmailStr
from typing_extensions import Literal

__all__ = [
    "SupportIsAvailableArgs", "SupportIsAvailableResult",
    "SupportIsAvailableAndEnabledArgs", "SupportIsAvailableAndEnabledResult",
    "SupportFieldsArgs", "SupportFieldsResult",
    "SupportSimilarIssuesArgs", "SupportSimilarIssuesResult",
    "SupportNewTicketArgs", "SupportNewTicketResult",
    "SupportAttachTicketArgs", "SupportAttachTicketResult",
    "SupportAttachTicketMaxSizeArgs", "SupportAttachTicketMaxSizeResult"
]

class SupportIsAvailableArgs(BaseModel):
    pass

class SupportIsAvailableResult(BaseModel):
    result: bool

class SupportIsAvailableAndEnabledArgs(BaseModel):
    pass

class SupportIsAvailableAndEnabledResult(BaseModel):
    result: bool

class SupportFieldsArgs(BaseModel):
    pass

class SupportFieldsResult(BaseModel):
    result: list[list[str]]

class SupportSimilarIssuesArgs(BaseModel):
    query: str

class SupportSimilarIssuesResultItem(BaseModel, extra='allow'):
    url: str
    summary: str

class SupportSimilarIssuesResult(BaseModel):
    result: list[SupportSimilarIssuesResultItem]

class SupportNewTicketItem(BaseModel):
    title: str = Field(max_length=200)
    body: str = Field(max_length=20000)
    category: str
    attach_debug: bool = False
    token: SecretStr
    type: Literal["BUG", "FEATURE"]
    criticality: str
    environment: str
    phone: str
    name: str
    email: EmailStr
    cc: list[EmailStr]

class SupportNewTicketArgs(BaseModel):
    data: SupportNewTicketItem


class SupportNewTicketResultItem(BaseModel):
    ticket: int | None
    url: str | None
    has_debug: bool

class SupportNewTicketResult(BaseModel):
    result: SupportNewTicketResultItem


class SupportAttachTicketItem(BaseModel):
    ticket: int
    filename: str
    token: SecretStr

class SupportAttachTicketArgs(BaseModel):
    data: SupportAttachTicketItem

class SupportAttachTicketResult(BaseModel):
    result: None

class SupportAttachTicketMaxSizeArgs(BaseModel):
    pass

class SupportAttachTicketMaxSizeResult(BaseModel):
    result: int

class SupportEntry(BaseModel):
    enabled: bool | None
    name: str
    title: str
    email: EmailStr
    phone: str
    secondary_name: str
    secondary_title: str
    secondary_email: str
    secondary_phone: str
    id: int
