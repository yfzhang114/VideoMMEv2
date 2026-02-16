"""
Radar chart: second_head_rating. 风格：浅灰底、衬线体、白底气泡标签、层级圆环.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from pathlib import Path

# ----------------------------------------
# 1. 数据准备
# ----------------------------------------
categories = [
    'Frame-Only', 'Frames & Audio',
    'Action & Motion', 'Order', 'Change', 'Temporal Reasoning',
    'Complex Plot\nComprehension', 'Video-Based\nKnowledge Acquisition',
    'Social Behavior\nAnalysis', 'Physical World\nReasoning'
]

# 对应原图配色
level_colors = ['#A2D2D2'] * 2 + ['#F9B664'] * 4 + ['#C0BCB5'] * 4

# second_head_rating: Frame-Only, Frames & Audio, Action & Motion, Order, Change, Temporal Reasoning,
# Complex Plot Comprehension, Video-Based Knowledge Acquisition, Social Behavior Analysis, Physical World Reasoning
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

# 原图背景：淡淡灰蓝/浅灰
fig = plt.figure(figsize=(11, 11), facecolor='#D6DBDF')
ax = fig.add_subplot(111, polar=True)
ax.set_facecolor('#D6DBDF')

ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

# ----------------------------------------
# 3. 绘制层级圆环（圆角间隔）
# ----------------------------------------
bar_width = (2 * np.pi / N) * 0.95
ax.bar(angles[:-1], 15, width=bar_width, bottom=75,
       color=level_colors, alpha=0.9, edgecolor='none', zorder=10)

# ----------------------------------------
# 4. 绘制模型数据
# ----------------------------------------
# 棕红、橙黄、草绿、深青、紫、蓝灰
model_colors = ['#B67A6B', '#E7C191', '#B5BE9A', '#5E827F', '#7D3C98', '#6B7B8C']

for i, (name, data) in enumerate(models.items()):
    data_closed = data + data[:1]
    color = model_colors[i % len(model_colors)]
    ax.plot(angles, data_closed, color=color, linewidth=3, label=name, zorder=i + 1)
    ax.fill(angles, data_closed, color=color, alpha=0.1)

# ----------------------------------------
# 5. 坐标轴与标签美化
# ----------------------------------------
ax.set_ylim(0, 90)
ax.set_yticks([10, 30, 50, 70])

# 只画圈层内的网格线，不画径向线（圈层之外的线）
ax.grid(True, axis='y', color='white', linestyle='--', linewidth=1, alpha=0.8, zorder=0)
ax.grid(False, axis='x')
ax.spines['polar'].set_visible(False)

# Y 轴数字
ax.set_rlabel_position(270)
for label in ax.get_yticklabels():
    label.set_color('#555555')
    label.set_fontsize(11)
    label.set_fontweight('bold')
    label.set_path_effects([path_effects.withStroke(linewidth=2, foreground='white')])

# X 轴：白底圆角“气泡”标签
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)
ax.tick_params(pad=40)

for label, angle in zip(ax.get_xticklabels(), angles[:-1]):
    label.set_bbox(dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.3', alpha=0.9))
    label.set_color('#333333')
    label.set_fontsize(12)
    label.set_fontweight('medium')
    if angle in (0, np.pi):
        label.set_horizontalalignment('center')
    elif 0 < angle < np.pi:
        label.set_horizontalalignment('left')
    else:
        label.set_horizontalalignment('right')

# ----------------------------------------
# 6. 图例：放到图最下方，一行显示
# ----------------------------------------
fig.subplots_adjust(bottom=0.15)
handles, labels = ax.get_legend_handles_labels()
legend = fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, 0.05),
                   ncol=6, frameon=True, fontsize=11)
legend.get_frame().set_facecolor('white')
legend.get_frame().set_edgecolor('#CCCCCC')
legend.get_frame().set_boxstyle('round,pad=0.5')

plt.tight_layout()

out_dir = Path(__file__).resolve().parent.parent
out_path = out_dir / "radar_second_head.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='#D6DBDF', edgecolor='none')
plt.close()
print(f"Saved to {out_path}")
