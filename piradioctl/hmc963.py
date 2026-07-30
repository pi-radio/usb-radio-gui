from pathlib import Path

import numpy as np
import skrf as rf

import matplotlib.pyplot as plt

from scipy.interpolate import CubicSpline

class HMC963:
    datadir = Path(__file__).parent / "data"

    sparams = rf.Network(datadir / "HMC963LC4 De-embedded.s2p")

    gain = CubicSpline(sparams.f / 1e9, 20 * np.log10(np.abs(sparams.s[:,1,0])))
