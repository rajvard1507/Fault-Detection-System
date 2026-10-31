import matplotlib.pyplot as plt
import os

def plot_waveforms(t, Va, Vb, Vc, Ia, Ib, Ic, fault_type):
    plt.figure(figsize=(10, 6))

    # Voltage plot
    plt.subplot(2, 1, 1)
    plt.plot(t, Va, label='Va', color='#ff6f61', linewidth=1.2)
    plt.plot(t, Vb, label='Vb', color='#1f77b4', linewidth=1.2)
    plt.plot(t, Vc, label='Vc', color='#2ca02c', linewidth=1.2)
    plt.title(f"Voltage Waveforms ({fault_type})", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()

    # Current plot
    plt.subplot(2, 1, 2)
    plt.plot(t, Ia, label='Ia', color='#ff9999', linewidth=1.2)
    plt.plot(t, Ib, label='Ib', color='#aec7e8', linewidth=1.2)
    plt.plot(t, Ic, label='Ic', color='#98df8a', linewidth=1.2)
    plt.title("Current Waveforms", fontsize=12)
    plt.xlabel("Time (s)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()

    plt.tight_layout()

    os.makedirs("static", exist_ok=True)
    plot_path = "static/plot.png"
    plt.savefig(plot_path, dpi=120, bbox_inches='tight')
    plt.close()
    return plot_path
