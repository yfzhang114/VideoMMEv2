import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# 统一使用 serif 字体（学术风格）
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'serif']
plt.rcParams['mathtext.fontset'] = 'stix'

# ── 读取数据 ──────────────────────────────────────────────
with open("data_statistics.json", "r", encoding="utf-8") as f:
    data = json.load(f)

records = data if isinstance(data, list) else data.get("statistics", data.get("data", []))

# ── 提取统计量 ────────────────────────────────────────────
question_wc = {i: [] for i in range(1, 5)}
option_total_wc = {i: [] for i in range(1, 5)}
option_individual_wc = {c: [] for c in "ABCDEFGH"}
video_durations = []

for rec in records:
    for q in range(1, 5):
        key = f"question_{q}_word_count"
        if key in rec:
            question_wc[q].append(rec[key])

    for q in range(1, 5):
        total = 0
        for c in "ABCDEFGH":
            key = f"option_{q}_{c}_word_count"
            if key in rec:
                val = rec[key]
                option_individual_wc[c].append(val)
                total += val
        if total > 0:
            option_total_wc[q].append(total)

    if "video_duration_seconds" in rec:
        video_durations.append(rec["video_duration_seconds"])

# ── 汇总 DataFrame ───────────────────────────────────────
rows = []
for q in range(1, 5):
    for v in question_wc[q]:
        rows.append({"Category": f"Question {q}", "Word Count": v, "Group": "Questions"})

for rec in records:
    for q in range(1, 5):
        gt_key = f"gt_{q}"
        if gt_key in rec:
            correct_choice = rec[gt_key]
            ans_key = f"option_{q}_{correct_choice}_word_count"
            if ans_key in rec:
                rows.append({"Category": f"Answer {q}", "Word Count": rec[ans_key], "Group": "Answers"})

for c in "ABCDEFGH":
    for v in option_individual_wc[c]:
        rows.append({"Category": f"Choice {c}", "Word Count": v, "Group": "Choices"})

df = pd.DataFrame(rows)

# ── 计算均值 & 标准差 ─────────────────────────────────────
summary = df.groupby("Category")["Word Count"].agg(["mean", "std"]).reset_index()
order = [f"Question {i}" for i in range(1, 5)] + \
        [f"Answer {i}" for i in range(1, 5)] + \
        [f"Choice {c}" for c in "ABCDEFGH"]
summary["Category"] = pd.Categorical(summary["Category"], categories=order, ordered=True)
summary = summary.sort_values("Category").dropna(subset=["Category"])

def get_group(cat):
    if cat.startswith("Question"):
        return "Questions"
    elif cat.startswith("Answer"):
        return "Answers"
    else:
        return "Choices"

summary["Group"] = summary["Category"].apply(get_group)

# ═══════════════════════════════════════════════════════════
# 🎨  合并图：上下布局 (2 行 1 列)
# ═══════════════════════════════════════════════════════════
FIG_W, FIG_H = 12, 11  # 🔹 总高度约为单图的 2 倍
TITLE_FONTSIZE, AXIS_FONTSIZE, TICK_FONTSIZE = 14, 12, 10
ANNOTATION_COLOR = "#999999"
sns.set_theme(style="whitegrid", font_scale=1.0)

blue_colors = ["#3a5f7d", "#6b9ac4", "#8fb3d9", "#b3d1ee"]
orange_colors = ["#d98c6c", "#e1a287", "#ebc0ab", "#f2d5c5"]
light_blue_colors = ["#c9e0f5", "#dbe9f7", "#b3d1ee", "#c0daf2", "#d5e6f8", "#a3c6eb", "#8fb3d9", "#6b9ac4"]

def get_color(cat):
    if cat.startswith("Question"):
        q_num = int(cat.split()[-1])
        return blue_colors[(q_num - 1) % len(blue_colors)]
    elif cat.startswith("Answer"):
        a_num = int(cat.split()[-1])
        return orange_colors[(a_num - 1) % len(orange_colors)]
    else:
        choice_letter = cat.split()[-1]
        idx = ord(choice_letter) - ord('A')
        return light_blue_colors[idx % len(light_blue_colors)]

palette_map = {
    "Questions": "#6b9ac4",
    "Answers": "#d98c6c",
    "Choices": "#8fb3d9",
}

# 🔹 创建 2 行 1 列的子图
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(FIG_W, FIG_H))

# ═══════════════════════════════════════════════════════════
# 📊 子图 1：Word Count Statistics
# ═══════════════════════════════════════════════════════════
colors = [get_color(cat) for cat in summary["Category"]]
x_pos = np.arange(len(summary))

bars = ax1.bar(
    x_pos,
    summary["mean"],
    yerr=summary["std"],
    color=colors,
    edgecolor="white",
    linewidth=1.2,
    capsize=5,
    error_kw=dict(elinewidth=1.5, capthick=1.5, color=ANNOTATION_COLOR),
    width=0.80,
    zorder=3,
)

for i, (m, s) in enumerate(zip(summary["mean"], summary["std"])):
    ax1.text(
        i, m + s + 0.3, f"{m:.1f}±{s:.0f}",
        ha="center", va="bottom", fontsize=9, fontweight="bold",
        color=ANNOTATION_COLOR,
        family='serif',
    )

ax1.set_xticks(x_pos)
ax1.set_xticklabels(summary["Category"], rotation=40, ha="right", fontsize=TICK_FONTSIZE, family='serif')
ax1.set_ylabel("Word Count", fontsize=AXIS_FONTSIZE, fontweight="bold", family='serif')
ax1.set_title(
    "Word Count Statistics: Questions / Answers / Choices  (Mean ± Std)",
    fontsize=TITLE_FONTSIZE, fontweight="bold", pad=12, family='serif',
)

legend_elements = [Patch(facecolor=v, edgecolor="white", label=k) for k, v in palette_map.items()]
ax1.legend(handles=legend_elements, loc="upper right", fontsize=TICK_FONTSIZE, frameon=True, fancybox=True, prop={'family': 'serif'})

ax1.set_xlim(-0.6, len(summary) - 0.4)
ax1.grid(axis="y", alpha=0.4)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_color('gray')
ax1.spines['bottom'].set_color('gray')

# ═══════════════════════════════════════════════════════════
# 📊 子图 2：Video Length Distribution
# ═══════════════════════════════════════════════════════════
durations = np.array(video_durations)
dur_min, dur_max = durations.min(), durations.max()

start_min = 2.9
merge_start_min = 20.5
step_min = 1.0

edges_sec = [start_min * 60]
t = start_min
while t + step_min <= merge_start_min:
    t += step_min
    edges_sec.append(t * 60)
edges_sec.append(merge_start_min * 60)
edges_sec.append(dur_max * 1.001)
bin_edges = np.array(edges_sec)

counts, _ = np.histogram(durations[durations >= start_min * 60], bins=bin_edges)

n_bars = len(counts)
cmap_colors = [
    "#3a5f7d", "#6b9ac4", "#8fb3d9", "#b3d1ee", "#c9e0f5",
    "#7fa5d6", "#a3c6eb", "#c0daf2", "#d98c6c", "#e1a287",
    "#ebc0ab", "#f2d5c5", "#55a868", "#7bc090", "#9ed4b4",
]
bar_colors = [cmap_colors[i % len(cmap_colors)] for i in range(n_bars)]

x_positions = []
for i in range(n_bars - 1):
    x_positions.append((bin_edges[i] + bin_edges[i + 1]) / 2)
last_pos = x_positions[-1] + (step_min * 60)
x_positions.append(last_pos)

fixed_bar_width_sec = (step_min * 60) * 0.75

for i in range(n_bars):
    ax2.bar(
        x_positions[i],
        counts[i],
        width=fixed_bar_width_sec,
        color=bar_colors[i],
        edgecolor='lightgray',
        linewidth=0.5,
        alpha=0.9,
    )

for i, cnt in enumerate(counts):
    if cnt > 0:
        ax2.text(
            x_positions[i],
            cnt + max(counts) * 0.01,
            str(int(cnt)),
            ha="center", va="bottom",
            fontsize=TICK_FONTSIZE,
            fontweight="bold",
            color=ANNOTATION_COLOR,
            family='serif',
        )

x_labels = []
for i in range(n_bars - 1):
    start, end = bin_edges[i] / 60, bin_edges[i + 1] / 60
    x_labels.append(f"({start:.1f}, {end:.1f}]")
x_labels.append(">20.5 min")

ax2.set_xticks(x_positions)
ax2.set_xlim(left=bin_edges[0] - 30, right=x_positions[-1] + 60)
ax2.set_xticklabels(x_labels, rotation=40, ha="right", fontsize=TICK_FONTSIZE, family='serif')

ax2.set_xlabel("Video Length (min)", fontsize=AXIS_FONTSIZE, fontweight="bold", family='serif')
ax2.set_ylabel("Number of Videos", fontsize=AXIS_FONTSIZE, fontweight="bold", family='serif')
ax2.set_ylim(0, (max(counts) * 1.15) if len(counts) else 10)
ax2.set_title(
    "Video Length Distribution",
    fontsize=TITLE_FONTSIZE,
    fontweight="bold",
    pad=12,
    family='serif',
)

ax2.grid(axis="y", alpha=0.3, linestyle='--', linewidth=0.5)
ax2.set_axisbelow(True)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color('gray')
ax2.spines['bottom'].set_color('gray')

# ═══════════════════════════════════════════════════════════
# 💾 保存合并图
# ═══════════════════════════════════════════════════════════
plt.tight_layout()
fig.savefig("combined_statistics.png", dpi=200, bbox_inches="tight")
plt.show()

print("✅  合并图已保存: combined_statistics.png")