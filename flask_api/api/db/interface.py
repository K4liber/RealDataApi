from abc import abstractmethod
from datetime import datetime
from typing import Optional, List, Dict

from api.data.entity import Localization


class DBAdapter:
    @abstractmethod
    def send_localization(self, device_id: str, localization: Localization):
        pass

    def get_localization(self, device_id: str) -> Optional[Localization]:
        pass

    def get_device_ids(self) -> List[str]:
        pass

    def get_device_id_to_timestamp(self) -> Dict[str, datetime]:
        pass

    def get_localizations(self, device_id: str, timestamp_from: Optional[str],
                          timestamp_to: Optional[str]) -> List[Localization]:
        pass
