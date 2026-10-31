import numpy as np
from utils import generate_time

def generate_three_phase_waveforms(t, omega, Vm, Im):
    Va = Vm * np.sin(omega * t)
    Vb = Vm * np.sin(omega * t - 2*np.pi/3)
    Vc = Vm * np.sin(omega * t + 2*np.pi/3)

    Ia = Im * np.sin(omega * t - np.deg2rad(30))
    Ib = Im * np.sin(omega * t - 2*np.pi/3 - np.deg2rad(30))
    Ic = Im * np.sin(omega * t + 2*np.pi/3 - np.deg2rad(30))
    return Va, Vb, Vc, Ia, Ib, Ic


def inject_fault(Va, Vb, Vc, Ia, Ib, Ic, fault_type, fault_time, fs, fault_res):
    fault_index = int(fault_time * fs)
    Va, Vb, Vc = Va.copy(), Vb.copy(), Vc.copy()
    Ia, Ib, Ic = Ia.copy(), Ib.copy(), Ic.copy()

    # default parameters
    post_scale_v = 1.0
    post_scale_i = 1.0

    # --- Fault Behaviour Models ---
    if "Three Phase" in fault_type:
        # All voltages collapse, all currents rise heavily
        Va[fault_index:] *= 0.05
        Vb[fault_index:] *= 0.05
        Vc[fault_index:] *= 0.05
        Ia[fault_index:] *= 3
        Ib[fault_index:] *= 3
        Ic[fault_index:] *= 3

    elif "Line-to-Line" in fault_type:
        # Two phases shorted
        phases = extract_phases(fault_type)
        for ph in phases:
            if ph == "A": Va[fault_index:] *= 0.2; Ia[fault_index:] *= 2.5
            if ph == "B": Vb[fault_index:] *= 0.2; Ib[fault_index:] *= 2.5
            if ph == "C": Vc[fault_index:] *= 0.2; Ic[fault_index:] *= 2.5

    elif "Double Line-to-Ground" in fault_type:
        # Two lines + ground, heavy unbalance
        phases = extract_phases(fault_type)
        for ph in phases:
            if ph == "A": Va[fault_index:] *= 0.1; Ia[fault_index:] *= 3
            if ph == "B": Vb[fault_index:] *= 0.1; Ib[fault_index:] *= 3
            if ph == "C": Vc[fault_index:] *= 0.1; Ic[fault_index:] *= 3
        Va[fault_index:] += 0.02 * np.random.randn(len(Va[fault_index:]))

    elif "Single Line-to-Ground" in fault_type:
        ph = fault_type.split()[-1]  # e.g., "Phase A"
        if "A" in ph:
            Va[fault_index:] *= 0.1; Ia[fault_index:] *= 2.5
        elif "B" in ph:
            Vb[fault_index:] *= 0.1; Ib[fault_index:] *= 2.5
        elif "C" in ph:
            Vc[fault_index:] *= 0.1; Ic[fault_index:] *= 2.5
        # small neutral disturbance
        Va[fault_index:] += 0.01 * np.random.randn(len(Va[fault_index:]))

    elif "Open Circuit" in fault_type:
        # One line disconnected → current zero, voltage rises slightly
        ph = fault_type.split()[-1]  # Phase A/B/C
        if "A" in ph:
            Ia[fault_index:] = 0; Va[fault_index:] *= 1.2
        elif "B" in ph:
            Ib[fault_index:] = 0; Vb[fault_index:] *= 1.2
        elif "C" in ph:
            Ic[fault_index:] = 0; Vc[fault_index:] *= 1.2

    elif "Overload" in fault_type:
        # All currents high, voltages sag slightly
        Ia[fault_index:] *= 1.8
        Ib[fault_index:] *= 1.8
        Ic[fault_index:] *= 1.8
        Va[fault_index:] *= 0.9
        Vb[fault_index:] *= 0.9
        Vc[fault_index:] *= 0.9

    elif "Voltage Imbalance" in fault_type:
        # Slight asymmetry in phase voltages
        Va[fault_index:] *= 1.0
        Vb[fault_index:] *= 0.85
        Vc[fault_index:] *= 0.95
        Ia[fault_index:] *= 1.1
        Ib[fault_index:] *= 0.9
        Ic[fault_index:] *= 1.0

    else:
        # No fault / unknown — keep waveforms same
        pass

    return Va, Vb, Vc, Ia, Ib, Ic


def extract_phases(fault_type):
    # Helper to extract phase letters from fault_type string
    phases = []
    for ph in ["A", "B", "C"]:
        if ph in fault_type:
            phases.append(ph)
    if not phases:
        phases = ["A", "B"]  # default for generic L-L
    return phases


def run_simulation(fault_type, fault_time, Vm=325, Im=14.14, f=50, fs=10000, t_end=1.0, fault_res=1.0):
    t = generate_time(fs, t_end)
    omega = 2 * np.pi * f
    Va, Vb, Vc, Ia, Ib, Ic = generate_three_phase_waveforms(t, omega, Vm, Im)
    Va, Vb, Vc, Ia, Ib, Ic = inject_fault(Va, Vb, Vc, Ia, Ib, Ic, fault_type, fault_time, fs, fault_res)
    return t, Va, Vb, Vc, Ia, Ib, Ic
