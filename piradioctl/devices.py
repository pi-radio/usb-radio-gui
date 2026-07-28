from ctypes import POINTER

import usb.core
import usb.util

from .singleton import Singleton

class DeviceList(metaclass=Singleton):
    def __init__(self):
        devices = usb.core.find()

        for dev in devices:
            pass
        
devices = DeviceList()

