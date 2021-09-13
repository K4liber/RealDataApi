import logging

__FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=__FORMAT)
logger = logging.getLogger('flask_api')


class Folder:
    VIEW = 'view'
