d"""
Rule-based fault detection logic (lightweight, fast, no ML).
This version analyzes voltage and current changes to classify the fault type.
"""

import numpy as np

def detect_fault(initial_v, final_v, initial_i, final_i, neutral_current):
    """
    Automatically detects the fault type based on before/after readings.

    Parameters:
        initial_v: [Va1, Vb1, Vc1]
        final_v: [Va2, Vb2, Vc2]
        initial_i: [Ia1, Ib1, Ic1]
        final_i: [Ia2, Ib2, Ic2]
        neutral_current: float

    Returns:
        fault_type (str), confidence (float)
    """
    Va1, Vb1, Vc1 = np.array(initial_v, dtype=float)
    Va2, Vb2, Vc2 = np.array(final_v, dtype=float)
    Ia1, Ib1, Ic1 = np.array(initial_i, dtype=float)
    Ia2, Ib2, Ic2 = np.array(final_i, dtype=float)

    # Compute per-phase voltage & current changes
    dV = np.array([Va1 - Va2, Vb1 - Vb2, Vc1 - Vc2])
    dI = np.array([Ia2 - Ia1, Ib2 - Ib1, Ic2 - Ic1])

    # Normalize values to avoid large scale differences
    v_drop_ratio = np.abs(dV) / (np.maximum(np.abs([Va1, Vb1, Vc1]), 1e-3))
    i_rise_ratio = np.abs(dI) / (np.maximum(np.abs([Ia1, Ib1, Ic1]), 1e-3))

    avg_vdrop = np.mean(v_drop_ratio)
    avg_irise = np.mean(i_rise_ratio)

    # thresholds (tuned empirically for realism)
    v_fault_thresh = 0.3  # >30% voltage drop → fault
    i_fault_thresh = 0.4  # >40% current rise → fault

    # Identify which phases are affected
    affected_v = v_drop_ratio > v_fault_thresh
    affected_i = i_rise_ratio > i_fault_thresh
    affected = affected_v | affected_i

    num_affected = np.sum(affected)

    fault_type = "No Fault"
    confidence = 90.0

    # ---- RULES ----
    if num_affected == 0 and avg_irise < 0.2:
        fault_type = "No Fault"
        confidence = 98.0

    elif num_affected == 3:
        if avg_vdrop > 0.5 and avg_irise > 0.6:
            fault_type = "Three Phase Fault"
            confidence = 97.0
        elif avg_irise < 0.2:
            fault_type = "Voltage Imbalance"
            confidence = 75.0
        else:
            fault_type = "Overload"
            confidence = 80.0

    elif num_affected == 2:
        # Check which two phases
        phases = ["A", "B", "C"]
        affected_phases = [phases[i] for i, val in enumerate(affected) if val]

        if neutral_current > 5:
            fault_type = f"Double Line-to-Ground Fault ({'-'.join(affected_phases)}-G)"
            confidence = 93.0
        else:
            fault_type = f"Line-to-Line Fault ({'-'.join(affected_phases)})"
            confidence = 95.0

    elif num_affected == 1:
        phase = ["A", "B", "C"][np.argmax(affected)]
        if neutral_current > 5:
            fault_type = f"Single Line-to-Ground Fault on Phase {phase}"
            confidence = 96.0
        elif avg_vdrop > 0.4 and avg_irise < 0.1:
            fault_type = f"Open Circuit (Phase {phase})"
            confidence = 92.0
        else:
            fault_type = f"Single Line Fault on Phase {phase}"
            confidence = 85.0

    else:
        fault_type = "Unknown/Complex Fault"
        confidence = 70.0

    # clip confidence between 60–100
    confidence = float(np.clip(confidence, 60, 100))

    return fault_type, confidence
