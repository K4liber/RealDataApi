from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase

from datetime import datetime
from typing import Optional

from api.data.utils import Default


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass(frozen=True)
class DeviceTimestampsRange:
    device_id: str
    timestamp_from: str
    timestamp_to: str


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class Localization:
    lat: Optional[float] = None
    lon: Optional[float] = None
    timestamp_str: Optional[str] = None


@dataclass
class Data:
    device_id: str
    localization: Localization
    timestamp: Optional[datetime] = None
    altitude: Optional[float] = None

    @property
    def timestamp_str(self):
        return self.timestamp.strftime(Default.DATETIME_FORMAT) if self.timestamp else ''
