import numpy as np

def generate_time(fs, t_end):
    return np.linspace(0, t_end, int(fs * t_end))
