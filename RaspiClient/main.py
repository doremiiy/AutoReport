from ctypes import c_int
import logging
from multiprocessing.managers import SyncManager
import signal

from can_manager import CanManager
from db_manager import DBManager
from nfc_manager import NFCManager
from session_manager import SessionManager
from settings import LOG_FILE, LOG_FORMAT
from upload_manager import UploadManager


class Main(object):

    def __init__(self):
        pass

    def run(self):
        logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, filemode='w', level=logging.INFO)

        SyncManager.register('SessionManager', SessionManager)
        SyncManager.register('DBManager', DBManager)
        manager = SyncManager()
        manager.start()

        db_manager = manager.DBManager()
        odometer_value = manager.Value(c_int, 0)
        vin = manager.Queue(1)
        session_manager = manager.SessionManager(odometer_value)

        can_manager = CanManager(session_manager, odometer_value, vin)
        nfc_manager = NFCManager(session_manager, db_manager)
        upload_manager = UploadManager(session_manager, db_manager)

        signal.pause()


if __name__ == '__main__':
    Main().run()
