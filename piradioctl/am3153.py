import re

from pathlib import Path

import numpy as np
import skrf as rf

from scipy.interpolate import CubicSpline

from .interval import Interval


class AM3153:
    filter_edges = {
        Interval( 5.1, 7.8): 0x30,
        Interval( 5.2, 8.0): 0x31,
        Interval( 5.3, 8.1): 0x32,
        Interval( 5.3, 8.3): 0x33,
        Interval( 5.4, 8.6): 0x34,
        Interval( 5.5, 8.8): 0x35,
        Interval( 5.7, 9.0): 0x36,
        Interval( 5.9, 9.1): 0x37,
        Interval( 5.8, 9.2): 0x38,
        Interval( 6.0, 9.5): 0x39,
        Interval( 6.3, 9.8): 0x3A,
        Interval( 6.5, 10.1): 0x3B,
        Interval( 6.8, 10.6): 0x3C,
        Interval( 7.3, 11.0): 0x3D,
        Interval( 8.1, 11.6): 0x3E,
        Interval( 9.1, 12.3): 0x3F,
        
        Interval(11.0, 13.8): 0x10,
        Interval(11.1, 13.9): 0x11,
        Interval(11.2, 14.1): 0x12,
        Interval(11.4, 14.4): 0x13,
        Interval(11.4, 14.5): 0x14,
        Interval(11.5, 14.9): 0x15,
        Interval(11.7, 15.2): 0x16,
        Interval(12.0, 15.4): 0x17,
        Interval(11.8, 15.7): 0x18,
        Interval(12.0, 16.0): 0x19,
        Interval(12.3, 16.2): 0x1A,
        Interval(12.7, 16.6): 0x1B,
        Interval(12.8, 16.7): 0x1C,
        Interval(13.4, 17.2): 0x1D,
        Interval(14.2, 18.0): 0x1E,
        Interval(15.8, 19.6): 0x1F,
        
        Interval(15.6, 20.2): 0x20,
        Interval(15.8, 20.3): 0x21,
        Interval(16.0, 20.6): 0x22,
        Interval(16.2, 20.9): 0x23,
        Interval(16.5, 21.0): 0x24,
        Interval(16.7, 21.3): 0x25,
        Interval(17.0, 21.7): 0x26,
        Interval(17.2, 22.1): 0x27,
        Interval(17.5, 21.8): 0x28,
        Interval(17.9, 22.2): 0x29,
        Interval(18.4, 22.7): 0x2A,
        Interval(18.9, 23.2): 0x2B,
        Interval(19.8, 23.7): 0x2C,
        Interval(20.4, 24.4): 0x2D,
        Interval(21.3, 25.3): 0x2E,
        Interval(22.3, 26.4): 0x2F,        
    }

    sparams = { }
    gains = {}

datadir = Path(__file__).parent / "data"

name_re = re.compile(r"AM3153_SN2_5V_6mA_Band(?P<band>[1-3])_(?P<subband>[0-1]{4})")

for path in datadir.glob("AM3153_SN2_5V_6mA_*.s2p"):
    if path.stem == "AM3153_SN2_5V_6mA_Bypass":
        index = 0
    else:    
        m = name_re.match(path.stem)
        
        band_map = { 1: 3, 2: 1, 3: 2 }
        
        band = band_map[int(m.group('band'))]
        subband = int(m.group('subband'), base=2)

        index = (band << 4) | subband
    
    AM3153.sparams[index] = rf.Network(path)
    
    gains = 20 * np.log10(np.abs(AM3153.sparams[index].s[:,1, 0]))

    AM3153.gains[index] = CubicSpline(AM3153.sparams[index].f / 1e9, gains)
