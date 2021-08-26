from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase

from datetime import datetime
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Localization:
    lat: float
    lon: float
    timestamp: datetime


@dataclass
class Data:
    device_id: str
    localization: Localization
    timestamp: Optional[datetime] = None
    altitude: Optional[float] = None

    @property
    def timestamp_str(self):
        return self.timestamp.strftime("%m/%d/%Y, %H:%M:%S") if self.timestamp else ''
