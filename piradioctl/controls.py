import asyncio

from inspect import isawaitable

import numpy as np
import plotly.graph_objects as go

from nicegui import ui

def pilabel(*args, **kwargs):
    ui.label(*args, **kwargs).classes('piradio-label')

def pititle(*args, **kwargs):
    ui.label(*args, **kwargs).classes('piradio-card-title')

class ValueNumber(ui.number):
    def __init__(self, panel, unit, lo, hi, value):
        self._panel = panel
        self._lo = lo
        self._hi = hi
        self._unit = unit

        super().__init__(label=None,
                         value=value,
                         placeholder="XXX",
                         min=lo,
                         max=hi,
                         precision=3,
                         format="%.3f",
                         step=0.001,
                         suffix=self._unit,
                         on_change=self.on_change)

        self.props("dense borderless")

    async def on_change(self, e):
        if e.sender.value is None:
            return
        
        f = e.sender.value
        
        if self._lo <= f <= self._hi:
            await self._panel.on_change(f)

class ValueSlider(ui.slider):
    def __init__(self, panel, lo, hi):
        self._panel = panel
        super().__init__(min=lo, max=hi, step=0.001)
            
class ValuePanel:
    def __init__(self, name, unit, lo, hi, callback, value):
        self._callback = callback
        
        with ui.row(align_items="center") as row:
            row.classes("w-fill items-center vertical-middle")
            pilabel(f"{name}")
            ui.space()
            self._freq_input = ValueNumber(self, unit, lo, hi, value)
            self._freq_slider = ValueSlider(self, lo, hi)

            self._freq_input.bind_value(self._freq_slider)

    @property
    def value(self):
        return self._freq_input.value

    @value.setter
    def value(self, f):
        self._freq_input.value = f

            
    async def on_change(self, f):
        r = self._callback(f)

        if isawaitable(r):
            await r


class PowerSlider(ui.slider):
    def __init__(self, panel, lo, hi):
        self._panel = panel
        super().__init__(min=lo, max=hi, step=1)
            
class ValuePower:
    def __init__(self, name, unit, lo, hi, callback):
        self._callback = callback
        
        with ui.row(align_items="center") as row:
            row.classes("w-fill items-center vertical-middle")
            pilabel(f"{name}")
            ui.space()
            self._freq_input = ValueNumber(self, unit, lo, hi)
            self._freq_slider = PowerSlider(self, lo, hi)

            self._freq_input.bind_value(self._freq_slider)
    @property
    def value(self):
        return self._freq_input.value        
            
    @value.setter
    def value(self, f):
        self._freq_input.value = f

            
    async def on_change(self, f):
        r = self._callback(f)

        if isawaitable(r):
            await r  
