from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

app = Flask(__name__)

# Function to detect fault type
def detect_fault(v_init, v_final, i_init, i_final, neutral_current=0):
    v_diff = [abs(vf - vi) for vi, vf in zip(v_init, v_final)]
    i_diff = [abs(if_ - ii) for ii, if_ in zip(i_init, i_final)]

    v_thresh = 40   # voltage threshold
    i_thresh = 10   # current threshold
    n_thresh = 5    # neutral current threshold

    fault_type = "Normal Condition"

    # --- Three Phase Fault ---
    if all(v > v_thresh for v in v_diff) and all(i > i_thresh for i in i_diff):
        fault_type = "Three Phase Fault"

    # --- Single Line-to-Ground Fault ---
    elif v_diff[0] > v_thresh and v_diff[1] < v_thresh and v_diff[2] < v_thresh:
        fault_type = "Single Line-to-Ground Fault (Phase A)"
    elif v_diff[1] > v_thresh and v_diff[0] < v_thresh and v_diff[2] < v_thresh:
        fault_type = "Single Line-to-Ground Fault (Phase B)"
    elif v_diff[2] > v_thresh and v_diff[0] < v_thresh and v_diff[1] < v_thresh:
        fault_type = "Single Line-to-Ground Fault (Phase C)"

    # --- Double Line-to-Ground Fault (LL-G) ---
    elif neutral_current > n_thresh:
        if v_diff[0] > v_thresh and v_diff[1] > v_thresh:
            fault_type = "Double Line-to-Ground Fault (AB-G)"
        elif v_diff[1] > v_thresh and v_diff[2] > v_thresh:
            fault_type = "Double Line-to-Ground Fault (BC-G)"
        elif v_diff[0] > v_thresh and v_diff[2] > v_thresh:
            fault_type = "Double Line-to-Ground Fault (CA-G)"

    # --- Double Line Fault ---
    elif v_diff[0] > v_thresh and v_diff[1] > v_thresh and v_diff[2] < v_thresh:
        fault_type = "Double Line Fault (AB)"
    elif v_diff[1] > v_thresh and v_diff[2] > v_thresh and v_diff[0] < v_thresh:
        fault_type = "Double Line Fault (BC)"
    elif v_diff[0] > v_thresh and v_diff[2] > v_thresh and v_diff[1] < v_thresh:
        fault_type = "Double Line Fault (CA)"
    
    # --- Open Circuit Faults ---
    elif (
        (i_final[0] < 0.5 and v_final[0] > 200 and v_final[1] > 200 and v_final[2] > 200)
        or (i_final[1] < 0.5 and v_final[0] > 200 and v_final[1] > 200 and v_final[2] > 200)
        or (i_final[2] < 0.5 and v_final[0] > 200 and v_final[1] > 200 and v_final[2] > 200)
    ):
        if i_final[0] < 0.5 and i_final[1] >= 1 and i_final[2] >= 1:
            fault_type = "Open Circuit Fault (Phase A)"
        elif i_final[1] < 0.5 and i_final[0] >= 1 and i_final[2] >= 1:
            fault_type = "Open Circuit Fault (Phase B)"
        elif i_final[2] < 0.5 and i_final[0] >= 1 and i_final[1] >= 1:
            fault_type = "Open Circuit Fault (Phase C)"
        elif i_final[0] < 0.5 and i_final[1] < 0.5 and i_final[2] >= 1:
            fault_type = "Open Circuit Fault (Phases A & B)"
        elif i_final[0] < 0.5 and i_final[2] < 0.5 and i_final[1] >= 1:
            fault_type = "Open Circuit Fault (Phases A & C)"
        elif i_final[1] < 0.5 and i_final[2] < 0.5 and i_final[0] >= 1:
            fault_type = "Open Circuit Fault (Phases B & C)"
        elif i_final[0] < 0.5 and i_final[1] < 0.5 and i_final[2] < 0.5:
            fault_type = "Three Phase Open Circuit"


    return fault_type, v_diff, i_diff


# Function to plot waveforms
def plot_waveforms(fault_type):
    t = np.linspace(0, 0.04, 1000)
    freq = 50
    w = 2 * np.pi * freq

    # Base healthy signals
    Va = 230 * np.sin(w * t)
    Vb = 230 * np.sin(w * t - 2*np.pi/3)
    Vc = 230 * np.sin(w * t + 2*np.pi/3)

    Ia = 5 * np.sin(w * t)
    Ib = 5 * np.sin(w * t - 2*np.pi/3)
    Ic = 5 * np.sin(w * t + 2*np.pi/3)

    # ---- Apply effects based on detected fault ----

    # 1️⃣ Three-phase fault
    if "Three Phase" in fault_type:
        # Severe symmetrical drop on all phases
        Va *= 0.2; Vb *= 0.2; Vc *= 0.2   # 20% voltage remains
        Ia *= 4; Ib *= 4; Ic *= 4         # currents rise 4×


    # 2️⃣ Double Line-to-Ground faults (must come before normal Double Line)
    elif "Double Line-to-Ground" in fault_type or "LL-G" in fault_type:
        if "AB-G" in fault_type:
            Va *= 0.1; Vb *= 0.1; Vc *= 1.0
            Ia *= 5; Ib *= 5; Ic *= 1.0
        elif "BC-G" in fault_type:
            Va *= 1.0; Vb *= 0.1; Vc *= 0.1
            Ia *= 1.0; Ib *= 5; Ic *= 5
        elif "CA-G" in fault_type:
            Va *= 0.1; Vb *= 1.0; Vc *= 0.1
            Ia *= 5; Ib *= 1.0; Ic *= 5

    # 3️⃣ Double Line Fault (without ground)
    elif "Double Line Fault" in fault_type:
        if "(AB)" in fault_type:
            Va *= 0.3; Vb *= 0.3; Ia *= 3; Ib *= 3
        elif "(BC)" in fault_type:
            Vb *= 0.3; Vc *= 0.3; Ib *= 3; Ic *= 3
        elif "(CA)" in fault_type:
            Va *= 0.3; Vc *= 0.3; Ia *= 3; Ic *= 3

    # 4️⃣ Single Line-to-Ground Faults
    elif "Single Line" in fault_type or "Line-to-Ground" in fault_type:
        if "(Phase A)" in fault_type or "A-G" in fault_type:
            Va *= 0.2; Ia *= 4
        elif "(Phase B)" in fault_type or "B-G" in fault_type:
            Vb *= 0.2; Ib *= 4
        elif "(Phase C)" in fault_type or "C-G" in fault_type:
            Vc *= 0.2; Ic *= 4

    # 5️⃣ Open Circuit Faults
    elif "Open Circuit" in fault_type:
        if "(Phase A)" in fault_type:
            Ia *= 0.05
        elif "(Phase B)" in fault_type:
            Ib *= 0.05
        elif "(Phase C)" in fault_type:
            Ic *= 0.05

    # ---- Plot section ----
    plt.figure(figsize=(10, 6))

    plt.subplot(2, 1, 1)
    plt.plot(t, Va, label='Va')
    plt.plot(t, Vb, label='Vb')
    plt.plot(t, Vc, label='Vc')
    plt.title(f'Voltage Waveforms ({fault_type})')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(t, Ia, label='Ia')
    plt.plot(t, Ib, label='Ib')
    plt.plot(t, Ic, label='Ic')
    plt.title('Current Waveforms')
    plt.legend()

    plt.tight_layout()

    if not os.path.exists('static'):
        os.makedirs('static')
    plot_path = os.path.join('static', 'plot.png')
    plt.savefig(plot_path)
    plt.close()
    return plot_path




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/detect', methods=['POST'])
def detect():
    try:
        def get_val(key):
            try:
                return float(request.form.get(key, 0))
            except:
                return 0

        v_init = [get_val('v1_initial'), get_val('v2_initial'), get_val('v3_initial')]
        v_final = [get_val('v1_final'), get_val('v2_final'), get_val('v3_final')]
        i_init = [get_val('i1_initial'), get_val('i2_initial'), get_val('i3_initial')]
        i_final = [get_val('i1_final'), get_val('i2_final'), get_val('i3_final')]
        neutral_current = get_val('neutral_current')

        fault_type, v_diff, i_diff = detect_fault(v_init, v_final, i_init, i_final, neutral_current)
        plot_path = plot_waveforms(fault_type)

        return render_template(
            'result.html',
            fault=fault_type,
            v_init=v_init, v_final=v_final,
            i_init=i_init, i_final=i_final,
            voltage_diff=[round(v, 2) for v in v_diff],
            current_diff=[round(i, 2) for i in i_diff],
            neutral_current=neutral_current,
            plot_path=plot_path
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
