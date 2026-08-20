import sys

from nicegui import ui

print(sys.path)

from piradiousb import Singleton, DeviceList

from .fr3_1ch import FR3SingleChannel
from .octo_lo import OctoLO

def define_styles():
    ui.add_head_html('''
    <style type="text/tailwindcss">
      @layer components {
        .piradio-label {
          @apply font-bold object-center;
        }

        .piradio-page-title {
          @apply w-full text-center text-xl font-bold
        }
    
        .piradio-card-title {
          @apply w-full text-center text-xl font-bold
        }
      }

      .current-display {
        input[type="number"]::-webkit-outer-spin-button, input[type="number"]::-webkit-inner-spin-button {
          -webkit-appearance: none;
          margin: 0;
        }
        input[type="number"] {
            -moz-appearance: textfield;
        }
      }

    </style>
    ''')

class RadioButton(ui.button):
    def __init__(self, gui, dev_entry, *args, **kwargs):
        self._gui = gui
        self._open = False
        self._dev_entry = dev_entry
        super().__init__(f'{dev_entry.model}: {dev_entry.serial}', *args, **kwargs)
        self.on('click', self.toggle)

    async def toggle(self):
        if self._open:
            await self._gui.delete_tab(self._dev_entry)
            self._open = False
        else:
            await self._gui.open_tab(self._dev_entry)
            self._open = True
            
        self.update()

    def update(self):
        with self.props.suspend_updates():
            self.props(f'color={"green" if self._open else "blue"}')
            super().update()
        
class GUI(metaclass=Singleton):
    def __init__(self):
        self.devices = {}

        self.dev_list = DeviceList()
        
    async def create(self):
        define_styles()

        self.radio_tabs = {}
        self.radio_tab_panels = {}
        
        self.tabs = ui.tabs()
        self.tab_panels = ui.tab_panels(self.tabs)
        
        with self.tabs:
            self.device_tab = ui.tab("Devices")

        with self.tab_panels:
            self.devices_panel = ui.tab_panel('Devices')

        with self.devices_panel:
            import piradio

            self.device_list = piradio.DeviceList()

            self.radio_buttons = {}
            
            for dev in self.device_list.get_devices():
                self.radio_buttons[dev.tty] = RadioButton(self, dev)
            
            ui.button("Add Single Channel", on_click=self.add_single_channel)
            ui.button("Add Octo LO", on_click=self.add_octo_lo)
            ui.button("Add Unconfigured", on_click=self.add_unconfigured)

        self.tabs.set_value(self.device_tab)

    def add_tab(self, dev_entry):
        title = f"{dev_entry.model} {dev_entry.serial}"
        
        with self.tabs:
            tab = ui.tab(title)
            
        with self.tab_panels:
            panel = ui.tab_panel(title)

        return tab, panel

    async def open_tab(self, dev_entry):
        radio = self.device_list.get_device(dev_entry.tty)

        radio.connect()
        
        tab, panel = self.add_tab(dev_entry)

        if dev_entry.model == "FR3_1CH":
            device = FR3SingleChannel(radio, tab, panel)

            self.devices[dev_entry.tty] = device

        await device.create()

        self.tabs.set_value(tab)
    
    def delete_tab(self, dev_entry):
        self.tabs.remove(f"{dev_entry.model} {dev_entry.serial}")
        
            
    async def add_single_channel(self):
        class MockSingleChannel:
            def __init__(self, gui):
                self.tty = len(gui.devices)
                self.model = "Mock FR3 1CH"
                self.serial = f"{len(gui.devices)}"
                
                self.LO = 10e9
                self.I_V = 0.1
                self.Q_V = -0.1

        radio = MockSingleChannel()
                
        tab, panel = self.add_tab(radio)
                
        device = FR3SingleChannel(radio, tab, panel)

        self.devices[radio.tty] = device

        await device.create()

        self.tabs.set_value(tab)

    async def add_octo_lo(self):
        tab, panel = self.add_tab()
        
        device = OctoLO(tab, panel)

        self.devices += [ device ]

        await device.create()

        self.tabs.set_value(tab)

    async def add_unconfigured(self):
        pass
    
        

async def main_page():
    await GUI().create()

    
