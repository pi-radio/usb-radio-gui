from inspect import isawaitable

from nicegui import ui

class FrequencyNumber(ui.number):
    def __init__(self, panel, flo, fhi):
        self._panel = panel
        self._flo = flo
        self._fhi = fhi

        super().__init__(label=None,
                         placeholder="XXX",
                         min=flo,
                         max=fhi,
                         precision=3,
                         format="%.3f",
                         step=0.001,
                         suffix="GHz",
                         on_change=self.on_change)

        self.props("dense borderless")

    async def on_change(self, e):
        if e.sender.value is None:
            return
        
        f = e.sender.value
        
        print(f"Changing frequency: {f} {type(f)}")

        if self._flo <= f <= self._fhi:
            await self._panel.on_change(f)

class FrequencySlider(ui.slider):
    def __init__(self, panel, flo, fhi):
        self._panel = panel
        super().__init__(min=flo, max=fhi, step=0.001)


            
class FrequencyPanel:
    def __init__(self, name, flo, fhi, callback):
        self._callback = callback
        
        with ui.row(align_items="stretch") as row:
            row.classes("w-fill items-center")
            ui.label(f"{name} Frequency").classes('piradio-label')
            ui.space()
            self._freq_input = FrequencyNumber(self, flo, fhi)
            self._freq_slider = FrequencySlider(self, flo, fhi)

            self._freq_input.bind_value(self._freq_slider)

    def set_value(self, f):
        self._freq_input.value = f
            
    async def on_change(self, f):
        r = self._callback(f)

        if isawaitable(r):
            await r

filter_edges = {
    (5.1, 7.8): 0x30,
    (5.2, 8.0): 0x30,
    (5.3, 8.1): 0x30,
    (5.3, 8.3): 0x30,
    (5.4, 8.6): 0x30,
    (5.5, 8.8): 0x30,
    (5.7, 9): 0x30,
    (5.9, 9.1): 0x30,
    (5.8, 9.2): 0x30,
    (6, 9.5): 0x30,
    (6.3, 9.8): 0x30,
    (6.5, 10.1): 0x30,
    (6.8, 10.6): 0x30,
    (7.3, 11): 0x30,
    (8.1, 11.6): 0x30,
    (9.1, 12.3): 0x30,
    
    (11, 13.8): 0x10,
}

class FR3SingleChannel:
    def __init__(self, tab, panel):
        self.tab = tab
        self.panel = panel

    async def create(self):
        with self.panel:
            with ui.row():
                ui.label(f"LSB").classes('piradio-label')
                self._sideband = ui.switch()
                ui.label(f"USB").classes('piradio-label')
                
            self._in_freq = FrequencyPanel("Low", 0.4, 4, self.on_in_freq_change)
            self._lo_freq = FrequencyPanel("LO", 4, 24, self.on_lo_freq_change)
            self._carrier_freq = FrequencyPanel("Carrier", 6, 24, self.on_carrier_freq_change)

            self._in_freq.set_value(2)
            self._lo_freq.set_value(8)           
            self._carrier_freq.set_value(6)

    async def on_in_freq_change(self, f):
        if self.
        pass

    async def on_lo_freq_change(self, f):
        pass

    async def on_carrier_freq_change(self, f):
        pass
