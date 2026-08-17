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

def pilabel(*args, **kwargs):
    ui.label(*args, **kwargs).classes('piradio-label')

def pititle(*args, **kwargs):
    ui.label(*args, **kwargs).classes('piradio-card-title')

class ValueNumber(ui.number):
    def __init__(self, panel, unit, lo, hi):
        self._panel = panel
        self._lo = lo
        self._hi = hi
        self._unit = unit

        super().__init__(label=None,
                         value=lo,
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
    def __init__(self, name, unit, lo, hi, callback):
        self._callback = callback
        
        with ui.row(align_items="center") as row:
            row.classes("w-fill items-center vertical-middle")
            pilabel(f"{name}")
            ui.space()
            self._freq_input = ValueNumber(self, unit, lo, hi)
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

class FrequencyPlanPlot:
    def __init__(self, radio):
        self.fig = go.Figure()
        self.radio = radio

        names = [
            "LO Leakage",
            "Input Signal",
            "Desired Sideband",
            "Undesired Sideband",
            "Filter Gain"
        ]

        colors = [
            "#F584B6",
            "#C584F6",
            "#60FF60",
            "#FF6060",
            "#EBC284"
        ]
        
        for i in range(5):
            self.fig.add_trace(go.Scatter(name=names[i],
                                          mode='lines',
                                          line=dict(color=colors[i]),
                                          x=[0, 30],
                                          y=[-110, -110]))

        self.fig.update_xaxes(range=[0, 30])        
        self.fig.update_yaxes(range=[-120, 30])
        
        self.fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        
        self.plotly = ui.plotly(self.fig)

    def output_chain_power(self, power_in, f_out):
        total = power_in

        total += MMIQ0626.conversion_gain(f_out)

        return self.tx_amp_chain_power(total, f_out)
        

    def tx_amp_chain_power(self, power_in, f_out):
        total = power_in
        
        total += AM3153.gains[self.radio.filter_select.value](f_out)

        total += HMC963.gain(f_out)

        total += ADL9006.gain(f_out)

        if total > ADL9006.psat(f_out):
            # TODO -- Propagate to GUI
            print(f"Saturating ADL9006")
            total = ADL9006.psat(f_out)
        
        return total
        

    def band_graph(self, data, band, level, nf=-114.23):
        beta = 0.5


        if not isinstance(band, Interval) or band.width == 0:
            if isinstance(band, Interval):
                band = band.center
                
            data.x = [0, band - 1e-3, band, band + 1e-3, 30]
            data.y = [ nf, nf, level, nf, nf ]
        else:
            data.x = np.linspace(band.start - band.width, band.end + band.width, 1001)

            d = 2 * np.abs(band.center - data.x) / band.width

            sf1 = (1 - beta)
            sf2 = (1 + beta)

            y = np.zeros(data.x.shape)
            y[d <= sf1] = 1

            idx = (sf1 < d) & (d <= sf2)

            y[idx] = (1 + np.cos(np.pi * (d[idx] - sf1) / beta / 2)) / 2

            y = (1 - y) * nf + y * level

            y[y < nf] = nf
            
            data.y = y
            
            
    def update(self):
        if not self.radio.running:
            return
        
        f_in = self.radio.input_signal
        
        f_lo = self.radio.lo_freq

        desired_sideband = self.radio.desired_sideband
        undesired_sideband = self.radio.undesired_sideband

        filter_sparams = AM3153.sparams[self.radio.filter_select.value]

        bw = max(self.radio.bandwidth, 1e-3)
        bw_db = 10 * np.log10(bw * 1e3)
        
        input_level = self.radio.input_power - bw_db

        # Compute total power
        if_power = self.radio.input_power + ADL5545.gain(f_in.center)

        if if_power > ADL5545.psat(f_in.center):
            print("Saturating ADL5545")
            if_power = ADL5545.psat(f_in.center)
        
        desired_level = self.output_chain_power(if_power, desired_sideband.center)

        desired_level -= bw_db

        undesired_level = self.output_chain_power(if_power + QCH392.sideband_suppression(f_in.center),
                                                  undesired_sideband.center)

        undesired_level -= bw_db

        self.band_graph(self.fig.data[0],
                        f_lo,
                        self.tx_amp_chain_power(13 + MMIQ0626.lo_leakage(f_lo),
                                                f_lo))

        self.band_graph(self.fig.data[1],
                        f_in,
                        input_level)
        
        
        self.band_graph(self.fig.data[2],
                        self.radio.desired_sideband,
                        desired_level)
        
        self.band_graph(self.fig.data[3],
                        self.radio.undesired_sideband,
                        undesired_level)

        
        amp = 20 * np.log10(np.abs(filter_sparams.s[:,1,0]))

        self.fig.data[4].x = filter_sparams.f / 1e9
        self.fig.data[4].y = amp
        
        self.plotly.update()
            
class FR3SingleChannel:
    def __init__(self, tab, panel):
        self.tab = tab
        self.panel = panel
        self._running = False

    @property
    def running(self):
        return self._running
        
    def create_input_card(self):
        pititle("Input Signal")
        
        self._in_freq = ValuePanel("Input Center Frequency", "GHz", 0.4, 4, self.on_in_freq_change)
        self._in_power = ValuePanel("Total Input Power", "dBm", -60, -5, self.on_power_change)
        self._bandwidth = ValuePanel("Bandwidth", "GHz", 0, 1, self.on_bandwidth_change)

    def create_conversion_card(self):
        pititle("Frequency Conversion")

        self._output_sideband = ui.toggle(["LSB", "USB"], value="USB", on_change=self.on_sideband_change)
        
        self._lo_freq = ValuePanel("LO", "GHz", 4, 24, self.on_lo_freq_change)
        self._carrier_freq = ValuePanel("Output Center Frequency", "GHZ", 6, 24, self.on_carrier_freq_change)

    def create_filter_card(self):
        pititle("Filtering")

        select_labels = { v: f"{k.start}-{k.end} GHz" for k, v in AM3153.filter_edges.items() }
        #select_labels[0] = "Bypass"

        self.filter_slider = ui.slider(value=0x10,
                                       min=0x10,
                                       max=0x3F,
                                       step=1,
                                       on_change=self.on_filter_slider_change)

        self.filter_slider.props("dense borderless")
        
        self.filter_select = ui.select(select_labels, value=0x30, on_change=self.on_filter_change)
        
    def create_frequency_panels(self):
        with ui.grid(columns=2):
            with ui.column():
                with ui.card():
                    self.create_input_card()
                    
                with ui.card():
                    self.create_conversion_card()

                with ui.card():
                    self.create_filter_card()
                    
            with ui.card():
                self.freq_plan_plot = FrequencyPlanPlot(self)

    @property
    def sideband(self):
        return self._output_sideband.value

    @property
    def bandwidth(self):
        return self._bandwidth.value

    @property
    def in_freq(self):
        return self._in_freq.value

    @property
    def input_power(self):
        return self._in_power.value
    
    @property
    def lo_freq(self):
        return self._lo_freq.value
    
    @property
    def carrier_freq(self):
        return self._carrier_freq.value

    @property
    def input_signal(self):
        return Interval(self.in_freq - self.bandwidth / 2, self.in_freq + self.bandwidth / 2)

    @property
    def desired_sideband(self):
        if self.sideband == "USB":
            return self.lo_freq + self.input_signal
        else:
            return self.lo_freq - self.input_signal

    @property
    def undesired_sideband(self):
        if self.sideband == "USB":
            return self.lo_freq - self.input_signal
        else:
            return self.lo_freq + self.input_signal
        
        
    async def create(self):
        with self.panel:
            with ui.row():
                self.create_frequency_panels()

        self._in_freq.value = 2
        self._lo_freq.value = 8
        self._in_power.value = -20
        self._carrier_freq.value = 10
        self._bandwidth.value = 1

        self._running = True

        self.freq_plan_plot.update()
                
    async def on_in_freq_change(self, f):
        if self.sideband == "USB":
            self._lo_freq.value = self._carrier_freq.value - f
        else:
            self._lo_freq.value = self._carrier_freq.value + f
            
        self.freq_plan_plot.update()
        
    async def on_bandwidth_change(self, f):
        self.freq_plan_plot.update()
            
    async def on_lo_freq_change(self, f):
        if self.sideband == "USB":
            self._carrier_freq.value = f + self._in_freq.value
        else:
            self._carrier_freq.value = f - self._in_freq.value
            
        self.freq_plan_plot.update()

    async def on_carrier_freq_change(self, f):
        if self.sideband == "USB":
            self._lo_freq.value = f - self._in_freq.value
        else:
            self._lo_freq.value = f + self._in_freq.value

        self.freq_plan_plot.update()


        
    async def on_filter_slider_change(self, e):
        band_map = { 1: 3, 2: 1, 3: 2 }

        v = (band_map[e.value >> 4] << 4) | (e.value & 0xF)
        
        print(v)

        self.filter_select.value = v
        
            
    async def on_filter_change(self, e):
        print(e.value)
        self.freq_plan_plot.update()

    async def on_power_change(self, v):
        self.freq_plan_plot.update()

    async def on_sideband_change(self, v):
        if self.sideband == "USB":
            self._carrier_freq.value = self._lo_freq.value + self._in_freq.value
        else:
            self._carrier_freq.value = self._lo_freq.value - self._in_freq.value
            
        self.freq_plan_plot.update()
        
