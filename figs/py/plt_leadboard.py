import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

# Use a clean sans-serif font to match modern UI
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']

# Set the hatch line width to make the pattern thicker and more visible
plt.rcParams['hatch.linewidth'] = 2.0

# Filtered Data (Top 10 models)
models = [
    "Gemini-3-Pro",
    "Doubao-Seed-2.0-Pro",
    "Gemini-3-Flash",
    "Qwen3.5-397B-A17B-Think",
    "MiMo-v2-Omni",
    "GPT-5",
    "Kimi-K2.5",
    "InternVL3-5-241B-A28B",
    "GLM4.5V-Think",
    "Keye-VL-1-5-8B"
]

non_lin = [49.4, 43.3, 42.5, 39.1, 38.6, 37.0, 36.1, 23.1, 21.8, 14.1]
avg_acc = [66.1, 60.5, 61.1, 55.9, 56.1, 55.6, 54.4, 41.4, 39.2, 31.1]

# Extract EXACT sequence of colors from the reference image from left to right
model_colors_exact = [
    '#5CA85C',  # 1. Green
    '#1E1E1E',  # 2. Black
    '#C48361',  # 3. Brown
    '#C48361',  # 4. Light Brown (same in ref image)
    '#466BEE',  # 5. Royal Blue
    '#D33C6D',  # 6. Pink
    '#EF8733',  # 7. Orange
    '#855DF8',  # 8. Purple
    '#2A2A2A',  # 9. Dark Gray (to differentiate slightly from #2)
    '#4868EE'   # 10. Bright Blue
]

# Reverse the lists to display the highest values at the top
models.reverse()
non_lin.reverse()
avg_acc.reverse()
model_colors_exact.reverse()

# Set up the figure with absolute white background
fig, ax = plt.subplots(figsize=(14, 9), facecolor='white')
ax.set_facecolor('white')

y = np.arange(len(models))
height = 0.38
offset = 0.20

# Create horizontal bars using the exact SAME colors for both Non-Lin and Acc
rects_nonlin = ax.barh(y + offset, non_lin, height, color=model_colors_exact, edgecolor='none')
rects_acc = ax.barh(y - offset, avg_acc, height, color=model_colors_exact, edgecolor='none')

# Apply rounded corners and selectively add hatch patterns
def style_bars(rects, pattern=None):
    for bar in rects:
        x, y_pos = bar.get_xy()
        w, h = bar.get_width(), bar.get_height()
        color = bar.get_facecolor()
        
        # To make the hatch visible, it uses the 'edgecolor'. 
        # We use a white edgecolor with a thin line to let the pattern pop against the solid color.
        edge_color = 'white' if pattern else 'none'
        lw = 0.5 if pattern else 0
        
        # Round the corners. rounding_size dictates the radius.
        fancy = mpatches.FancyBboxPatch(
            (x, y_pos), w, h,
            boxstyle=f"Round,pad=0.0,rounding_size={h/2.5}",
            facecolor=color, edgecolor=edge_color, linewidth=lw,
            hatch=pattern, zorder=bar.get_zorder()
        )
            
        ax.add_patch(fancy)
        # Hide the original sharp-cornered rectangular bar
        bar.set_visible(False)

# Non-Lin gets no pattern, Acc gets diagonal lines ('///')
style_bars(rects_nonlin, pattern=None)
style_bars(rects_acc, pattern='///')

# Y-axis styling
ax.set_yticks(y)
ax.set_yticklabels(models, fontsize=13, fontweight='bold', color='#2D3436')
ax.tick_params(axis='y', length=0, pad=15)

# X-axis styling
ax.set_xticks([])  # Remove x-axis completely

# Spines (borders)
for spine in ['top', 'right', 'bottom']:
    ax.spines[spine].set_visible(False)
ax.spines['left'].set_visible(True)
ax.spines['left'].set_color('#DFE6E9')
ax.spines['left'].set_linewidth(2)

# Add labels inside the bars
def add_labels(rects):
    for bar in rects:
        width = bar.get_width()
        
        # Since we use identical solid colors, white text is best for both.
        text_color = 'white'
        x_pos = width - 1.5
        ha = 'right'
        
        # If the bar is too short, place text outside and use dark text
        if width < 5:
            x_pos = width + 0.5
            ha = 'left'
            text_color = '#2D3436'
            
        ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
                f'{width:.1f}',
                ha=ha, va='center', zorder=10,
                fontsize=12, fontweight='bold', color=text_color)

add_labels(rects_nonlin)
add_labels(rects_acc)

# Elegant Legend at the top center
legend_elements = [
    mpatches.Patch(facecolor='#868E96', edgecolor='white', hatch='///', linewidth=1, label='Avg Acc (Striped)'),
    mpatches.Patch(facecolor='#868E96', edgecolor='none', label='Non-Lin (Solid)')
]
ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.08),
          ncol=2, frameon=False, fontsize=13, labelcolor='#2D3436')

# Adjust layout margins (removed titles, so top margin can be tighter)
plt.subplots_adjust(left=0.28, right=0.96, top=0.92, bottom=0.05)

# Save and show the plot
plt.savefig('leaderboard.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
