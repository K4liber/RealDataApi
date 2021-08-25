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
