import logging
import os
from typing import List

__FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=__FORMAT)
logger = logging.getLogger('flask_api')


class Folder:
    VIEW = 'view'


def get_device_view_path_str(upload_folder: str, device_id: str) -> str:
    return str(os.path.join(upload_folder, Folder.VIEW, device_id))


def get_sorted_views(upload_folder: str, device_id: str) -> List[str]:
    device_view_path_str = get_device_view_path_str(upload_folder, device_id)

    if not os.path.isdir(device_view_path_str):
        return []

    return sorted(os.listdir(device_view_path_str), reverse=True)
