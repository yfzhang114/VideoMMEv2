import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.patheffects as path_effects
import re
import os

# Use a clean sans-serif font to match modern UI
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['hatch.linewidth'] = 2.5  # Make hatch lines thicker and more solid

# Read data from index.html
html_path = os.path.join(os.path.dirname(__file__), '../../index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

data = {}
# Regex to extract model name, overall (Non-Lin) score, and avg_acc score
pattern = r'name:\s*"([^"]+)",.*?overall:\s*\[([\d\.]+).*?avg_acc:\s*\[([\d\.]+)'
for m in re.finditer(pattern, content):
    data[m.group(1)] = {
        'non_lin': float(m.group(2)), 
        'avg_acc': float(m.group(3))
    }

models = [
    "Human Expert",
    "Gemini-3-Pro",
    "Doubao-Seed-2.0-Pro-260215",
    "Gemini-3-Flash",
    "Qwen3.5-397B-A17B-Think",
    "MiMo-v2-Omni",
    "GPT-5",
    "Kimi-K2.5",
    "InternVL3-5-241B-A28B-Instruct",
    "GLM4.5V-Think",
    "Keye-VL-1-5-8B"
]

non_lin = []
avg_acc = []
for m in models:
    if m in data:
        non_lin.append(data[m]['non_lin'])
        avg_acc.append(data[m]['avg_acc'])
    else:
        print(f"Warning: {m} not found in index.html!")
        non_lin.append(0)
        avg_acc.append(0)

# Reference colors strictly from the provided image (left to right)
model_colors_exact = [
    '#5CA85C',  # 0. Human Expert
    '#1E1E1E',  # 1. Gemini-3-Pro
    '#C48361',  # 2. Doubao
    '#1E1E1E',  # 3. Gemini-3-Flash (Match Gemini-3-Pro)
    '#466BEE',  # 4. Qwen
    '#D33C6D',  # 5. MiMo
    '#EF8733',  # 6. GPT-5
    '#855DF8',  # 7. Kimi
    '#1E1E1E',  # 8. InternVL
    '#466BEE',  # 9. GLM
    '#5CA85C'   # 10. Keye
]

# Reverse the lists to display the highest values at the top
models.reverse()
non_lin.reverse()
avg_acc.reverse()
model_colors_exact.reverse()

# Set up the figure with absolute white background
fig, ax = plt.subplots(figsize=(9.5, 10), facecolor='white')
ax.set_facecolor('white')

y = np.arange(len(models))
height = 0.35  # Thinner bars to fit two per model

# Create horizontal bars
rects_nonlin = ax.barh(y + height/2 + 0.02, non_lin, height, color=model_colors_exact, edgecolor='none')
rects_avgacc = ax.barh(y - height/2 - 0.02, avg_acc, height, color='white', edgecolor='none', hatch='///')

# Apply rounded corners
def style_bars(rects, is_striped=False):
    for i, bar in enumerate(rects):
        x, y_pos = bar.get_xy()
        w, h = bar.get_width(), bar.get_height()
        
        if is_striped:
            facecolor = 'white'
            edgecolor = model_colors_exact[i]
            hatch = '///'
            linewidth = 0  # No border/frame
        else:
            facecolor = bar.get_facecolor()
            edgecolor = 'none'
            hatch = None
            linewidth = 0
        
        # Round the corners
        fancy = mpatches.FancyBboxPatch(
            (x, y_pos), w, h,
            boxstyle=f"Round,pad=0.0,rounding_size={h/2.5}",
            facecolor=facecolor, 
            edgecolor=edgecolor,
            hatch=hatch,
            linewidth=linewidth,
            zorder=bar.get_zorder()
        )
            
        ax.add_patch(fancy)
        bar.set_visible(False)

style_bars(rects_nonlin, is_striped=False)
style_bars(rects_avgacc, is_striped=True)

# Y-axis styling
ax.set_yticks(y)
ax.set_yticklabels(models, fontsize=12, fontweight='bold', color='#2D3436')

# Retain the pad for logo space
ax.tick_params(axis='y', length=0, pad=35)

# X-axis styling
ax.set_xticks([])  
ax.set_xlim(0, 100)

# Spines (borders)
for spine in ['top', 'right', 'bottom']:
    ax.spines[spine].set_visible(False)
ax.spines['left'].set_visible(True)
ax.spines['left'].set_color('#DFE6E9')
ax.spines['left'].set_linewidth(2)

# Add labels inside the bars
def add_labels(rects, is_striped=False):
    for i, bar in enumerate(rects):
        width = bar.get_width()
        is_human = (models[i] == "Human Expert")
        
        if width < 10:
            x_pos = width + 1.0
            ha = 'left'
            text_color = 'black'
        else:
            if is_striped:
                text_color = 'black'
            else:
                text_color = 'black' if is_human else 'white'
            x_pos = width - 1.5
            ha = 'right'
            
        txt = ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
                f'{width:.1f}',
                ha=ha, va='center', zorder=10,
                fontsize=13 if is_human else 11, 
                fontweight='black', 
                color=text_color)
        
        if is_striped:
            # Add a white background box and stroke to make it pop against stripes
            txt.set_bbox(dict(facecolor='white', edgecolor='none', alpha=0.75, boxstyle='round,pad=0.15'))
            txt.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
        elif is_human:
            txt.set_path_effects([path_effects.withStroke(linewidth=4, foreground='white')])
        elif text_color == 'white':
            txt.set_path_effects([path_effects.withStroke(linewidth=2, foreground=model_colors_exact[i])])

add_labels(rects_nonlin, is_striped=False)
add_labels(rects_avgacc, is_striped=True)

# Legend
legend_elements = [
    mpatches.Patch(facecolor='#7F8C8D', edgecolor='none', label='Non-Lin Score (Solid)'),
    mpatches.Patch(facecolor='white', edgecolor='#7F8C8D', hatch='///', linewidth=0, label='Avg Acc (Striped)')
]
ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2, frameon=False, fontsize=11)

# Adjust layout margins 
plt.subplots_adjust(left=0.35, right=0.95, top=0.92, bottom=0.05)

# Save and show the plot
plt.savefig('leaderboard.png', dpi=300, bbox_inches='tight', facecolor='white')
