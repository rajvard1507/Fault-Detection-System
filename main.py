# main.py
from simulation import run_simulation
from detection import detect_fault
from config import FS

def simulate_and_detect(fault_type, fault_time, voltage=230, current=10, frequency=50, duration=1.0, fault_res=1.0):
    Vm = voltage * (2 ** 0.5)      # Convert RMS to peak
    Im = current * (2 ** 0.5)
    t, Va, Vb, Vc, Ia, Ib, Ic = run_simulation(
        fault_type, fault_time, Vm=Vm, Im=Im, f=frequency, fs=FS, t_end=duration, fault_res=fault_res
    )

    fault_detected, det_time, fault_class = detect_fault(Va, Vb, Vc, FS)
    return {
        "t": t,
        "Va": Va, "Vb": Vb, "Vc": Vc,
        "Ia": Ia, "Ib": Ib, "Ic": Ic,
        "fault_detected": fault_detected,
        "fault_time": det_time,
        "fault_class": fault_class
    }
