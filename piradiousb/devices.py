import platform

from pathlib import Path

import usb.core
import usb.util

from .singleton import Singleton

class DeviceList(metaclass=Singleton):
    def __init__(self):
        system = platform.system()
        if system == "Linux":
            sys_usb_path = Path("/sys/bus/usb/devices")

            for p in sys_usb_path.glob("*"):
                try:
                    with open(p / "idVendor", "r") as f:
                        vendor_id = int(f.read(), 16)

                    if vendor_id != 0x0483:
                        continue
                        
                    with open(p / "idProduct", "r") as f:
                        product_id = int(f.read(), 16) 

                    with open(p / "manufacturer", "r") as f:
                        manufacturer = f.read().strip()

                    if manufacturer != "Pi Radio":
                        continue
                    
                    with open(p / "product", "r") as f:
                        product = f.read().strip()

                    print(f"{p}:")
                    print(f"{vendor_id:04x}:{product_id:04x} {manufacturer} {product}")
                except FileNotFoundError:
                    continue
                except Exception as e:
                    print(f"{p}: {e} {type(e)}")
            pass
        else:
            devices = usb.core.find(find_all=True)
            
            for dev in devices:
                if dev.idVendor != 0x0483:
                    continue

                print(dev)
                
                print(f"Found: {dev.idVendor:04x}:{dev.idProduct:04x}")
                dev.set_configuration()
                #dev._langids = (0,)
                print(f"Manufacturer: {dev.manufacturer}")
                
        print(f"Initialized")
