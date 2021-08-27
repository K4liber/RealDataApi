from abc import abstractmethod
from typing import Optional, List

from api.data.entity import Localization


class DBAdapter:
    @abstractmethod
    def send_localization(self, device_id: str, localization: Localization):
        pass

    def get_localization(self, device_id: str) -> Optional[Localization]:
        pass

    def get_device_ids(self) -> List[str]:
        pass
