"""
Thinking vs Instruct + effect of subtitle on Video-MME v2.
Style: Scientific & Aesthetic Stacked Bar Chart.
Logic: Base Bar = Instruct; Stacked Layer = Think Effect (Gain or Regression).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# --- Scientific Publication Style ---
STYLE_CONFIG = {
    "font_family": "Arial",  # Preferred for papers
    "base_color": "#BDC3C7", # Light Gray (Instruct Baseline)
    "gain_color": "#2E86C1", # Strong Blue (Thinking Improvement)
    "loss_color": "#E74C3C", # Soft Red (Thinking Regression)
    "sub_bar_alpha": 1.0,    # Transparency for distinction
    "no_sub_hatch": "///",   # Pattern for "No Subtitle" to distinguish visually
    "font_size": 14,
    "annotation_fontsize": 11,
}

def apply_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [STYLE_CONFIG["font_family"], "DejaVu Sans", "Helvetica"],
        "font.size": STYLE_CONFIG["font_size"],
        "axes.linewidth": 1.5,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.labelsize": STYLE_CONFIG["font_size"] + 1,
        "axes.titlesize": STYLE_CONFIG["font_size"] + 2,
        "legend.frameon": False,
        "legend.fontsize": STYLE_CONFIG["font_size"],
        "xtick.direction": "out",
        "ytick.direction": "out",
        "savefig.bbox": "tight",
        "savefig.dpi": 300,
    })

def plot_stacked_effect(ax, model_names, data_instruct, data_think, title):
    """
    data_instruct: shape (N_models, 2) -> [w_sub, wo_sub]
    data_think:    shape (N_models, 2) -> [w_sub, wo_sub]
    """
    n_models = len(model_names)
    indices = np.arange(n_models)
    
    # Dimensions
    bar_width = 0.35
    spacing = 0.05
    
    # Metrics indices: 0 = w_sub (With Subtitle), 1 = wo_sub (Without Subtitle)
    # But usually strictly speaking w_sub is better. 
    # Let's organize as: Group 1 (No Sub), Group 2 (With Sub) per model
    
    # We will plot "No Sub" on the left (offset -width/2 - small_gap)
    # We will plot "With Sub" on the right (offset +width/2 + small_gap)
    
    modes = [("Wo/ Subtitle", 1, STYLE_CONFIG["no_sub_hatch"]), 
             ("W/ Subtitle", 0, None)]
    
    for i, (mode_label, col_idx, hatch) in enumerate(modes):
        # Calculate positions
        offset = (i - 0.5) * (bar_width + spacing)
        x = indices + offset
        
        # Extract values
        val_inst = np.array([row[col_idx] for row in data_instruct])
        val_think = np.array([row[col_idx] for row in data_think])
        
        # Calculate Delta
        delta = val_think - val_inst
        
        # 1. Plot Base (Instruct)
        # We plot the full Instruct height first
        ax.bar(x, val_inst, width=bar_width, 
               color=STYLE_CONFIG["base_color"], edgecolor='white', linewidth=0.8,
               label="Instruct (Base)" if i==1 else "", hatch=hatch, alpha=0.9)
        
        # 2. Plot Effect (Thinking)
        # Case A: Gain (Think > Instruct) -> Stack ON TOP of Instruct
        # Case B: Regression (Think < Instruct) -> Stack DOWNWARDS from Instruct top (overlay)
        
        # Separate gains and losses for cleaner plotting
        gains = np.maximum(delta, 0)
        losses = np.minimum(delta, 0) # Negative values
        
        # Plot Gains (Blue) on top of Instruct
        ax.bar(x, gains, bottom=val_inst, width=bar_width,
               color=STYLE_CONFIG["gain_color"], edgecolor='white', linewidth=0.8,
               label="Think Gain" if i==1 else "", hatch=hatch)
        
        # Plot Losses (Red) starting from Instruct height downwards
        # height=losses (negative), bottom=val_inst
        ax.bar(x, losses, bottom=val_inst, width=bar_width,
               color=STYLE_CONFIG["loss_color"], edgecolor='white', linewidth=0.8,
               label="Think Loss" if i==1 else "", hatch=hatch)

        # 3. Annotate change above the bar top (bar top = max(instruct, think) for this cluster)
        for j, (v_inst, v_think, d) in enumerate(zip(val_inst, val_think, delta)):
            if abs(d) < 0.01:
                continue  # skip near-zero
            if d >= 0:
                text = f"+{d:.1f}"
                color = '#1a5276'
            else:
                text = f"{d:.1f}"
                color = '#922b21'
            bar_top = max(v_inst, v_think)
            label_y = bar_top + 0.5
            ax.text(x[j], label_y, text, ha='center', va='bottom',
                    fontsize=STYLE_CONFIG["annotation_fontsize"], fontweight='bold', color=color)

    ax.set_xticks(indices)
    ax.set_xticklabels(model_names, fontweight='medium', rotation=25, ha='right')
    ax.set_title(title, loc='left', pad=15, fontweight='bold', color='#2C3E50')
    
    # Aesthetic Grid
    ax.grid(axis='y', linestyle='--', alpha=0.3, color='gray', zorder=0)
    ax.set_axisbelow(True)

def create_custom_legend(fig):
    """Create a global aesthetic legend."""
    handles = [
        mpatches.Patch(facecolor=STYLE_CONFIG["base_color"], label='Instruct Baseline (w. subtitle)'),
        mpatches.Patch(facecolor=STYLE_CONFIG["gain_color"], label='Thinking Gain'),
        mpatches.Patch(facecolor=STYLE_CONFIG["loss_color"], label='Thinking Regression'),
        mpatches.Patch(facecolor='white', edgecolor='gray', hatch=STYLE_CONFIG["no_sub_hatch"], label='wo. subtitle'),
    ]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, 0.02), 
               ncol=4, frameon=False, fontsize=STYLE_CONFIG["font_size"])

# ---------------------------------------------------------------------------
# Data Preparation
# ---------------------------------------------------------------------------

# Group names
GROUPS = ["Qwen3-VL-8B", "Qwen3-VL-235B", "Kimi-VL-16B", "MiMo-VL-7B"]

# Raw Data (Pairs of [w_sub, wo_sub])
# Order in lists: Qwen8B-Inst, Qwen8B-Think, Qwen235B-Inst, Qwen235B-Think...
# Qwen8B: wo_sub L1/L2 has delta=0 (no stack); w_sub L1=+1.1, L2=+3.3 (blue stack)
RAW_L1 = [[23.0, 14.9], [24.1, 14.9], [32.6, 23.3], [30.3, 18.8],
          [22.8, 20.4], [22.0, 17.7], [18.1, 12.5], [23.2, 15.2]]
RAW_L2 = [[16.9, 12.5], [20.2, 12.5], [25.4, 17.7], [27.0, 16.5],
          [17.0, 13.0], [15.5, 11.9], [12.7, 10.0], [18.5, 11.9]]
RAW_L3 = [[15.7, 10.8], [18.1, 10.5], [23.4, 15.8], [22.3, 13.3],
          [18.2, 13.6], [12.6, 8.5], [13.1, 8.0], [16.1, 9.5]]
RAW_ALL= [[17.9, 12.4], [20.3, 12.2], [26.3, 18.3], [25.8, 15.7],
          [19.0, 15.1], [15.9, 11.9], [14.3, 9.8], [18.6, 11.7]]

def parse_data(raw_list):
    """
    Separates Instruct and Think data into model groups.
    Returns: data_instruct (N, 2), data_think (N, 2)
    """
    instruct_data = []
    think_data = []
    # Loop steps of 2: (Inst, Think)
    for i in range(0, len(raw_list), 2):
        instruct_data.append(raw_list[i])
        think_data.append(raw_list[i+1])
    return instruct_data, think_data

def main():
    apply_style()
    
    # Setup Figure: four plots in one row, shared y-axis
    fig, axes = plt.subplots(1, 4, figsize=(20, 6), sharey=True)
    fig.subplots_adjust(bottom=0.22, wspace=0.12)
    
    metrics = [
        (RAW_L1, "Level 1"),
        (RAW_L2, "Level 2"),
        (RAW_L3, "Level 3"),
        (RAW_ALL, "Overall Performance"),
    ]
    
    global_max = 0
    for ax, (raw_data, title) in zip(axes, metrics):
        inst_data, think_data = parse_data(raw_data)
        plot_stacked_effect(ax, GROUPS, inst_data, think_data, title)
        all_vals = np.array(inst_data + think_data).flatten()
        global_max = max(global_max, all_vals.max())
    for ax in axes:
        ax.set_ylim(0, global_max * 1.15)
    
    # Only leftmost plot keeps y-axis and ticks
    axes[0].set_ylabel("Score")
    for ax in axes[1:]:
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)

    create_custom_legend(fig)
    
    # Save
    out_dir = Path(__file__).resolve().parent
    out_path = out_dir / "scientific_think_effect_v2.png"
    print(f"Saving scientific figure to {out_path} ...")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Done.")

if __name__ == "__main__":
    main()