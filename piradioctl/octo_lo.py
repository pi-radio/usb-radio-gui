import asyncio

from inspect import isawaitable

import numpy as np
import plotly.graph_objects as go

from nicegui import ui

from .interval import Interval
from .am3153 import AM3153
from .mmiq0626 import MMIQ0626
from .hybrid import QCH392
from .adl5545 import ADL5545
from .hmc963 import HMC963
from .adl9006 import ADL9006

from .controls import pilabel, pititle, ValuePanel, ValuePower

class OctoLO:
    def __init__(self, tab, panel):
        self.panel = panel
        self.tab = tab
        self.driver = 1
    async def create(self):
        with self.panel:
            with ui.row():
                self.create_input_card()
                
        self._running = True

    @property
    def running(self):
        return self._running
    
    
    def create_input_card(self):
        pititle("Ocoto_LO")
        
        self.lo_freq = ValuePanel("Frequency", "GHz", 6, 22.6, self.on_lo_freq_change)
        self.lo_power = ValuePower("Lo power","power", 1, 7, self.on_lo_power_change)
        self.lo_power.value = 2
        self.lo_freq.value = 10.0
    async def on_lo_power_change(self, f):
        print(self.lo_power.value)

    async def on_lo_freq_change(self, f):
        print(self.lo_freq.value)

        self._running = True
        
