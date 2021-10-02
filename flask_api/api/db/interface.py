from abc import abstractmethod
from typing import Optional, List, Set

from api.data.entity import Localization, DeviceTimestampsRange


class DBAdapter:
    @abstractmethod
    def send_localization(self, device_id: str, localization: Localization):
        pass

    def get_localization(self, device_id: str) -> Optional[Localization]:
        pass

    def get_device_ids(self) -> List[str]:
        pass

    def get_device_timestamps_range(self, id_starts_with: Optional[str] = None, limit: int = 10) \
            -> Set[DeviceTimestampsRange]:
        pass

    def get_localizations(self, device_id: str, timestamp_from: Optional[str],
                          timestamp_to: Optional[str]) -> List[Localization]:
        pass
