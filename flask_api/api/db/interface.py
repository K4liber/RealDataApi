from abc import abstractmethod

from api.data.entity import Localization


class DBAdapter:
    @abstractmethod
    def send_location(self, device_id: str, localization: Localization):
        pass
