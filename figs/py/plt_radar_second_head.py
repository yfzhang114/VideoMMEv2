"""
Radar chart: second_head_rating.
优化重点：压缩标签与圆环间距，提升布局紧凑度。
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.patches as mpatches

# ----------------------------------------
# 1. 数据准备
# ----------------------------------------
categories = [
    'Frame-Only', 'Frames & Audio',
    'Action & Motion', 'Order', 'Change', 'Temporal Reasoning',
    'Complex Plot\nComprehension', 'Video-Based\nKnowledge Acquisition',
    'Social Behavior\nAnalysis', 'Physical World\nReasoning'
]

level_colors = ['#A2D2D2'] * 2 + ['#F9B664'] * 4 + ['#C0BCB5'] * 4

models = {
    'Gemini-3-Pro': [47.10, 68.26, 24.14, 55.41, 43.63, 43.17, 36.53, 44.26, 36.43, 20.94],
    'GPT-5': [27.34, 32.65, 15.22, 29.78, 31.73, 26.66, 22.24, 26.44, 19.83, 15.05],
    'Doubao-Seed-1.6-Vision': [35.32, 26.71, 16.51, 36.75, 35.22, 21.24, 28.26, 21.79, 17.55, 13.13],
    'Qwen3-VL-235B': [26.10, 38.32, 15.17, 32.08, 25.00, 29.22, 27.93, 29.03, 23.29, 14.40],
    'InternVL3-5-241B': [20.30, 30.37, 12.96, 28.61, 16.83, 30.47, 23.62, 21.67, 20.30, 12.45],
    'Qwen3-Omni-30B': [20.54, 26.00, 10.57, 20.03, 12.38, 16.87, 15.85, 17.76, 16.47, 12.90],
}

# ----------------------------------------
# 2. 基础设置
# ----------------------------------------
N = len(categories)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]

plt.rcParams['font.family'] = 'serif'

fig = plt.figure(figsize=(12, 10), facecolor='white')
ax = fig.add_subplot(111, polar=True)
ax.set_facecolor('none')

ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

# ----------------------------------------
# 3. 绘制层级圆环
# ----------------------------------------
bar_width = (2 * np.pi / N) * 0.92
ring_bottom = 78
ax.bar(angles[:-1], 10, width=bar_width, bottom=ring_bottom,
       color=level_colors, alpha=0.8, edgecolor='none', zorder=10)

# ----------------------------------------
# 4. 绘制模型数据
# ----------------------------------------
model_colors = ['#B67A6B', '#E7C191', '#B5BE9A', '#5E827F', '#7D3C98', '#6B7B8C']

for i, (name, data) in enumerate(models.items()):
    data_closed = data + data[:1]
    color = model_colors[i % len(model_colors)]
    ax.plot(angles, data_closed, color=color, linewidth=2.5, label=name, zorder=i + 1)
    ax.fill(angles, data_closed, color=color, alpha=0.1)

# ----------------------------------------
# 5. 坐标轴与紧凑标签
# ----------------------------------------
ax.set_ylim(0, 92)
ax.set_yticks([10, 30, 50, 70])

ax.grid(True, axis='y', color='#E0E0E0', linestyle='--', linewidth=0.8, alpha=1, zorder=0)
ax.grid(False, axis='x')
ax.spines['polar'].set_visible(False)

ax.set_rlabel_position(270)
for label in ax.get_yticklabels():
    label.set_color('#888888')
    label.set_fontsize(10)
    label.set_path_effects([path_effects.withStroke(linewidth=2, foreground='white')])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)

ax.tick_params(pad=32)

for label, angle in zip(ax.get_xticklabels(), angles[:-1]):
    label.set_fontsize(13)
    label.set_fontweight('bold')
    label.set_color('#222222')
    label.set_bbox(dict(facecolor='white', edgecolor='#CCCCCC', linewidth=0.6,
                        boxstyle='round,pad=0.25', alpha=1.0, zorder=15))

    ha = 'left' if 0 < angle < np.pi else 'right'
    if abs(angle) < 0.01 or abs(angle - np.pi) < 0.01:
        ha = 'center'
    label.set_horizontalalignment(ha)

# ----------------------------------------
# 6. 图例布局微调 — 模型图例（左侧）
# ----------------------------------------
fig.subplots_adjust(left=0.22, right=0.98, top=0.92, bottom=0.08)

handles, labels = ax.get_legend_handles_labels()
legend_models = fig.legend(handles, labels, loc='center left', bbox_to_anchor=(0.02, 0.5),
                           ncol=1, frameon=True, fontsize=11, labelspacing=1.4)
legend_models.get_frame().set_boxstyle('round,pad=0.6')

# ----------------------------------------
# 7. Level 图例（右上角）— 新增
# ----------------------------------------
level_patches = [
    mpatches.Patch(facecolor='#A2D2D2', edgecolor='#888888', linewidth=0.8, label='Level 1: Retrieval & Aggregation'),
    mpatches.Patch(facecolor='#F9B664', edgecolor='#888888', linewidth=0.8, label='Level 2: Temporal Understanding'),
    mpatches.Patch(facecolor='#C0BCB5', edgecolor='#888888', linewidth=0.8, label='Level 3: Complex Reasoning'),
]

legend_levels = fig.legend(
    handles=level_patches,
    loc='upper right',
    bbox_to_anchor=(0.25, 0.84),
    ncol=1,
    frameon=True,
    fontsize=11,
    title='Capability Levels',
    title_fontsize=12,
    labelspacing=0.8,
    handlelength=1.5,
    handleheight=1.2,
)
legend_levels.get_frame().set_boxstyle('round,pad=0.5')
legend_levels.get_frame().set_edgecolor('#CCCCCC')
legend_levels.get_frame().set_facecolor('white')
legend_levels.get_frame().set_alpha(0.95)

# 需要手动把模型图例重新添加回去，因为 fig.legend 会覆盖
fig.add_artist(legend_models)

out_path = "radar_second_head.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.show()