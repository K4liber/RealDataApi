from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Localization:
    lat: float
    lon: float


@dataclass
class Data:
    localization: Localization
    timestamp: Optional[datetime]
    altitude: Optional[float]

    @property
    def timestamp_str(self):
        return self.timestamp.strftime("%m/%d/%Y, %H:%M:%S") if self.timestamp else ''
