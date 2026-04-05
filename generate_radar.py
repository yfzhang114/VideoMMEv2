import matplotlib.pyplot as plt
import numpy as np

# Data
models = ["Human Expert", "Gemini-3-Pro", "Qwen3.5-397B-A17B-Think", "GPT-5", "Qwen3-Omni-30B-A3B-Instruct"]
categories = [
    "Frame-Only", "Frames & Audio", "Action & Motion", "Order", "Change",
    "Temporal\nReasoning", "Complex Plot\nComprehension",
    "Video-Based\nKnowledge Acquisition", "Social Behavior\nAnalysis",
    "Physical World\nReasoning"
]

data = {
    "Human Expert": [96.1589, 93.6332, 89.0858, 92.9444, 95.1923, 87.2727, 87.0929, 89.9665, 91.6111, 84.1246],
    "Gemini-3-Pro": [47.1, 68.26, 24.14, 55.41, 43.63, 43.17, 36.53, 44.26, 36.43, 20.94],
    "Qwen3.5-397B-A17B-Think": [26.17, 41.70, 18.56, 52.58, 34.74, 37.60, 24.12, 40.15, 25.88, 15.87],
    "GPT-5": [27.34, 32.65, 15.22, 29.78, 31.73, 26.66, 22.24, 26.44, 19.83, 15.05],
    "Qwen3-Omni-30B-A3B-Instruct": [19.28, 23.8, 11.38, 19.16, 11.18, 17.2, 17.65, 18.3, 18.02, 10.92]
}

colors = {
    "Human Expert": "#8E9EAB",
    "Gemini-3-Pro": "#7C9885",
    "Qwen3.5-397B-A17B-Think": "#B59E75",
    "GPT-5": "#D9A05B",
    "Qwen3-Omni-30B-A3B-Instruct": "#798A9F"
}

labels = {
    "Human Expert": "Human Expert",
    "Gemini-3-Pro": "Gemini-3-Pro",
    "Qwen3.5-397B-A17B-Think": "Qwen3.5-397B-A17B\nThink",
    "GPT-5": "GPT-5",
    "Qwen3-Omni-30B-A3B-Instruct": "Qwen3-Omni-30B-A3B\nInstruct"
}

num_vars = len(categories)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]  # Complete the loop

# Rotate to start at the top
angles = [a + np.pi/2 for a in angles]
angles = [(a % (2 * np.pi)) for a in angles] # Normalize

fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))

# Setup grids
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1) # Clockwise
ax.set_rgrids([20, 40, 60, 80, 100], angle=0, fontsize=9, color="grey", zorder=1)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=10, zorder=5)

# Style grid
ax.grid(color='#E5E7EB', linewidth=1, linestyle='--', zorder=0)
ax.spines['polar'].set_color('#E5E7EB')
ax.spines['polar'].set_linewidth(1.5)


for model in models:
    values = data[model]
    values += values[:1]
    
    lw = 2.5 if model == "Human Expert" else 1.5
    zorder = 4 if model == "Human Expert" else 3
    
    ax.plot(angles, values, color=colors[model], linewidth=lw, label=labels[model], zorder=zorder)
    ax.fill(angles, values, color=colors[model], alpha=0.1, zorder=zorder-1)
    ax.scatter(angles[:-1], values[:-1], color=colors[model], s=30, zorder=zorder+1)

# Legend
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=10)
plt.title("Capability Radar", size=14, y=1.05)

plt.tight_layout()
plt.savefig("radar_plot.png", dpi=300, bbox_inches='tight')
print("Successfully generated radar_plot.png")