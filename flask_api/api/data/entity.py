from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase

from datetime import datetime
from typing import Optional

from api.data.utils import Default


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Localization:
    lat: float
    lon: float
    timestamp_str: str


@dataclass
class Data:
    device_id: str
    localization: Localization
    timestamp: Optional[datetime] = None
    altitude: Optional[float] = None

    @property
    def timestamp_str(self):
        return self.timestamp.strftime(Default.DATETIME_FORMAT) if self.timestamp else ''
