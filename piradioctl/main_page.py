from nicegui import ui

from .fr3_1ch import FR3SingleChannel
from .singleton import Singleton

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

    
class GUI(metaclass=Singleton):
    def __init__(self):
        self.devices = []
        
    async def create(self):
        define_styles()
        
        self.tabs = ui.tabs()
        self.tab_panels = ui.tab_panels(self.tabs)
        
        with self.tabs:
            ui.tab("Devices")

        with self.tab_panels:
            self.devices_panel = ui.tab_panel('Devices')

        with self.devices_panel:
            ui.button("Add Single Channel", on_click=self.add_single_channel)
            ui.button("Add Octo LO", on_click=self.add_octo_lo)
            ui.button("Add Unconfigured", on_click=self.add_unconfigured)

    def add_tab(self):
        title = f"{len(self.devices)}"
        
        with self.tabs:
            tab = ui.tab(f"{len(self.devices)}")
            
        with self.tab_panels:
            panel = ui.tab_panel(f"{len(self.devices)}")

        return tab, panel
            
    async def add_single_channel(self):
        tab, panel = self.add_tab()
        
        device = FR3SingleChannel(tab, panel)

        self.devices += [ device ]

        await device.create()

        self.tabs.set_value(tab)

    async def add_octo_lo(self):
        pass

    async def add_unconfigured(self):
        pass
    
        

async def main_page():
    await GUI().create()

    
