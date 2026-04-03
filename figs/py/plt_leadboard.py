import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

# Use a clean sans-serif font to match modern UI
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']

# Filtered Data (Top 10 models) - ONLY Non-Lin remains
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
model_colors_exact.reverse()

# Set up the figure with absolute white background
# ** KEY CHANGE: Reduced figsize width from 14 to 11 to solve the "too long" issue **
fig, ax = plt.subplots(figsize=(11, 8), facecolor='white')
ax.set_facecolor('white')

y = np.arange(len(models))
height = 0.55

# Create horizontal bars using the exact SAME colors
rects_nonlin = ax.barh(y, non_lin, height, color=model_colors_exact, edgecolor='none')

# Apply rounded corners
def style_bars(rects):
    for bar in rects:
        x, y_pos = bar.get_xy()
        w, h = bar.get_width(), bar.get_height()
        color = bar.get_facecolor()
        
        # Round the corners. rounding_size dictates the radius.
        fancy = mpatches.FancyBboxPatch(
            (x, y_pos), w, h,
            boxstyle=f"Round,pad=0.0,rounding_size={h/2.5}",
            facecolor=color, edgecolor='none', zorder=bar.get_zorder()
        )
            
        ax.add_patch(fancy)
        # Hide the original sharp-cornered rectangular bar
        bar.set_visible(False)

# Apply styling to our single set of bars
style_bars(rects_nonlin)

# Y-axis styling
ax.set_yticks(y)
ax.set_yticklabels(models, fontsize=13, fontweight='bold', color='#2D3436')

# Retain the pad for logo space
ax.tick_params(axis='y', length=0, pad=35)

# X-axis styling
ax.set_xticks([])  # Remove x-axis completely
# ** KEY CHANGE: Start the X-axis (value axis) from 10 instead of 0 **
ax.set_xlim(left=10)

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
        
        # Calculate how long the bar actually appears since it starts at 10
        visible_width = width - 10
        
        # If the visible part of the bar is too short, place text outside and use dark text
        if visible_width < 6:
            x_pos = width + 0.5
            ha = 'left'
            text_color = '#2D3436'
        else:
            text_color = 'white'
            x_pos = width - 1.0
            ha = 'right'
            
        ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
                f'{width:.1f}',
                ha=ha, va='center', zorder=10,
                fontsize=12, fontweight='bold', color=text_color)

add_labels(rects_nonlin)

# Adjust layout margins 
# Left margin adjusted slightly to maintain logo space with the new smaller figure width
plt.subplots_adjust(left=0.35, right=0.96, top=0.95, bottom=0.05)

# Save and show the plot
plt.savefig('leaderboard.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
