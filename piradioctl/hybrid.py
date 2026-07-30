from pathlib import Path

import numpy as np
import skrf as rf

import matplotlib.pyplot as plt

from scipy.interpolate import CubicSpline

class QCH392:
    datadir = Path(__file__).parent / "data"

    sparams = rf.Network(datadir / "QCH-392+_UNIT_3_+105C.S4P")

    gain_imbalance = np.abs(sparams.s[:,2,0])/np.abs(sparams.s[:,3,0])

    phase_imbalance = np.abs(np.unwrap(np.angle(sparams.s[:,3,0]) - np.angle(sparams.s[:,2,0]))) - np.pi / 2

    __a = (gain_imbalance**2 - 2 * gain_imbalance * np.cos(phase_imbalance) + 1)
    __a /= (gain_imbalance**2 + 2 * gain_imbalance * np.cos(phase_imbalance) + 1)
    
    sideband_suppression = CubicSpline(sparams.f/1e9, 10 * np.log10(__a))
