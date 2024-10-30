from middlewared.api.base import BaseModel
from typing import Literal
from datetime import datetime

__all__ = [
    "AtaSelfTest", "NvmeSelfTest", "ScsiSelfTest",
    "SmartQueryForDiskArgs", "SmartQueryForDiskResult",
    "SmartDiskChoicesArgs", "SmartDiskChoicesResult",
    "SmartDiskCreateArgs", "SmartDiskCreateResult",
    "SmartManualTestArgs", "SmartManualTestResult"
]

class SmartManualTestDiskRun(BaseModel):
    identifier: str
    mode: Literal["FOREGROUND", "BACKGROUND"] = "BACKGROUND"
    type: Literal["LONG", "SHORT", "CONVEYANCE", "OFFLINE"]

class SmartManualTestArgs(BaseModel):
    disks: list[SmartManualTestDiskRun]

class SmartManualTestResultItem(BaseModel):
    disk: str
    identifier: str
    error: str | None
    expected_result_time: datetime
    job: int

class SmartManualTestResult(BaseModel):
    result: SmartManualTestResultItem

class SmartDiskCronSchedule(BaseModel):
    hour: str = "*"
    dom: str = "*"
    month: str = "*"
    dow: str = "*"

class SmartDiskCreateArgs(BaseModel):
    schedule: SmartDiskCronSchedule
    desc: str | None
    all_disks: bool = False
    disks: list[str] = []
    type: Literal["LONG", "SHORT", "CONVEYANCE", "OFFLINE"]

class SmartDiskCreateResult(BaseModel):
    result: dict # update to smart query result

class SmartDiskChoicesArgs(BaseModel):
    full_disk: bool = False

class SmartDiskChoicesResult(BaseModel):
    result: dict # update this to disk query result when its written

class SmartQueryForDiskArgs(BaseModel):
    disk: str

class SmartQueryForDiskResult(BaseModel):
    result: list[dict | None]

class AtaSelfTest(BaseModel):
    num: int
    description: str
    status: str
    status_verbose: str
    remaining: float
    lifetime: int
    power_on_hours_ago: int
    lba_of_first_error: int | None = None


class NvmeSelfTest(BaseModel):
    num: int
    description: str
    status: str
    status_verbose: str
    power_on_hours: int
    power_on_hours_ago: int
    failing_lba: int | None = None
    nsid: int | None = None
    seg: int | None = None
    sct: int | None = 0x0
    code: int | None = 0x0


class ScsiSelfTest(BaseModel):
    num: int
    description: str
    status: str
    status_verbose: str
    power_on_hours_ago: int
    segment_number: int | None = None
    lifetime: int | None = None
    lba_of_first_error: int | None = None
