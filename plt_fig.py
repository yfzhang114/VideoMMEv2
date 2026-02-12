import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib import cm

# 统一使用 serif 字体（学术风格）
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'serif']
plt.rcParams['mathtext.fontset'] = 'stix'

# ── 读取数据 ──────────────────────────────────────────────
try:
    with open("data_statistics.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data if isinstance(data, list) else data.get("statistics", data.get("data", []))
except FileNotFoundError:
    print("Warning: 'data_statistics.json' not found. Using dummy data.")
    records = []
    for _ in range(100):
        rec = {"video_duration_seconds": np.random.randint(180, 1500)}
        for q in range(1, 5):
            rec[f"question_{q}_word_count"] = np.random.randint(10, 50)
            rec[f"gt_{q}"] = "A"
            for c in "ABCDEFGH":
                rec[f"option_{q}_{c}_word_count"] = np.random.randint(5, 20)
        records.append(rec)

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
# 🎨  配色方案定义 (中等饱和度 Medium Colors)
# ═══════════════════════════════════════════════════════════

# 1. Word Count 配色 — 类似风格的不同方案：柔和冷/暖/中性，统一饱和度
# -----------------------------------------------------------
# 方案：柔青蓝 / 柔琥珀 / 暖灰（各一类一色，图例清晰）
wc_colors = {
    "Questions": "#5B8A9E",   # 柔青蓝 (soft teal)
    "Answers":   "#C4956A",   # 柔琥珀 (soft amber)
    "Choices":   "#7D7D7D",   # 暖中灰 (warm mid-gray)
}

def get_wc_color(cat):
    if cat.startswith("Question"):
        return wc_colors["Questions"]
    elif cat.startswith("Answer"):
        return wc_colors["Answers"]
    else:
        return wc_colors["Choices"]

# 2. Video Length 配色 (保持 Yellow -> Pink -> Blue)
# -----------------------------------------------------------
video_palettes = {
    "short":  ["#fae588", "#f9dc76", "#f8d364", "#f7ca52", "#f6c140"], # 黄色系
    "medium": ["#eeb4c3", "#ea9eb1", "#e6889f", "#e2728d", "#de5c7b"], # 粉色系
    "long":   ["#b8cce1", "#a6bdd6", "#94aecb", "#829fc0", "#7090b5"]  # 灰蓝系
}

# ═══════════════════════════════════════════════════════════
# 🎨  绘图设置
# ═══════════════════════════════════════════════════════════
FIG_W, FIG_H = 12, 11
TITLE_FONTSIZE, AXIS_FONTSIZE, TICK_FONTSIZE = 14, 12, 10
ANNOTATION_COLOR = "#333333" # 字体颜色稍微加深一点，匹配中等背景色
sns.set_theme(style="whitegrid", font_scale=1.0)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(FIG_W, FIG_H))

# ═══════════════════════════════════════════════════════════
# 📊 子图 1：Word Count Statistics (中等颜色)
# ═══════════════════════════════════════════════════════════
bar_colors_wc = [get_wc_color(cat) for cat in summary["Category"]]
x_pos = np.arange(len(summary))

bars = ax1.bar(
    x_pos,
    summary["mean"],
    yerr=summary["std"],
    color=bar_colors_wc,
    edgecolor="#666666", # 边框颜色
    linewidth=0.7,
    capsize=4,
    error_kw=dict(elinewidth=1.2, capthick=1.2, color="#555555"),
    width=0.75,
    zorder=3,
)

# 添加数值标签
for i, (m, s) in enumerate(zip(summary["mean"], summary["std"])):
    ax1.text(
        i, m + s + 0.5, f"{m:.1f}",
        ha="center", va="bottom", fontsize=8,
        color=ANNOTATION_COLOR, family='serif'
    )

ax1.set_xticks(x_pos)
ax1.set_xticklabels(summary["Category"], rotation=45, ha="right", fontsize=TICK_FONTSIZE, family='serif')
ax1.set_ylabel("Word Count", fontsize=AXIS_FONTSIZE, fontweight="bold", family='serif')
ax1.set_title(
    "Word Count Statistics (Questions / Answers / Choices)",
    fontsize=TITLE_FONTSIZE, fontweight="bold", pad=12, family='serif',
)

# 自定义图例
legend_patches = [
    Patch(facecolor=wc_colors["Questions"], edgecolor="gray", label="Questions"),
    Patch(facecolor=wc_colors["Answers"], edgecolor="gray", label="Answers"),
    Patch(facecolor=wc_colors["Choices"], edgecolor="gray", label="Choices"),
]
ax1.legend(handles=legend_patches, loc="upper right", fontsize=TICK_FONTSIZE, frameon=True, fancybox=True)

ax1.set_xlim(-0.8, len(summary) - 0.2)
ax1.grid(axis="y", alpha=0.3, linestyle="--")
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# ═══════════════════════════════════════════════════════════
# 📊 子图 2：Video Length Distribution (整数分桶)
# ═══════════════════════════════════════════════════════════
durations = np.array(video_durations)
if len(durations) > 0:
    # 1. 设置整数分桶 (Integer Bins)
    start_min = 3   # 从3分钟开始
    end_merge = 20  # 到20分钟后合并
    step = 1        # 步长为1分钟

    edges_sec = []
    current_val = start_min
    while current_val < end_merge:
        edges_sec.append(current_val * 60)
        current_val += step
    edges_sec.append(end_merge * 60)
    
    max_val = durations.max() if len(durations) > 0 else (end_merge + 1) * 60
    edges_sec.append(max(max_val + 1, (end_merge + 1) * 60))
    
    bin_edges = np.array(edges_sec)
    valid_durations = durations[durations >= start_min * 60]
    counts, _ = np.histogram(valid_durations, bins=bin_edges)
    n_bars = len(counts)

    # 2. 生成对应配色 (Yellow -> Pink -> Blue)
    final_bar_colors = []
    threshold_medium = 6
    threshold_long = 12

    for i in range(n_bars):
        current_min = start_min + i * step
        if current_min < threshold_medium:
            c_idx = i % len(video_palettes["short"])
            final_bar_colors.append(video_palettes["short"][c_idx])
        elif current_min < threshold_long:
            c_idx = (i - (threshold_medium - start_min)) % len(video_palettes["medium"])
            final_bar_colors.append(video_palettes["medium"][c_idx])
        else:
            c_idx = (i - (threshold_long - start_min)) % len(video_palettes["long"])
            final_bar_colors.append(video_palettes["long"][c_idx])

    # 3. 绘制
    x_positions = np.arange(n_bars)
    ax2.bar(
        x_positions,
        counts,
        width=0.65,
        color=final_bar_colors,
        edgecolor="#888888",
        linewidth=0.8,
        alpha=0.95,
        zorder=3
    )

    for i, cnt in enumerate(counts):
        if cnt > 0:
            ax2.text(
                i, cnt + max(counts)*0.01, str(int(cnt)),
                ha="center", va="bottom", fontsize=9,
                color=ANNOTATION_COLOR, family='serif'
            )

    x_labels = []
    for i in range(n_bars - 1):
        s = start_min + i * step
        e = s + step
        x_labels.append(f"({s}, {e}]")
    x_labels.append(f">{end_merge} min")

    ax2.set_xticks(x_positions)
    ax2.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=TICK_FONTSIZE, family='serif')
    
    ax2.set_xlabel("Video Length (min)", fontsize=AXIS_FONTSIZE, fontweight="bold", family='serif')
    ax2.set_ylabel("Number of Videos", fontsize=AXIS_FONTSIZE, fontweight="bold", family='serif')
    ax2.set_title("Video Length Distribution", fontsize=TITLE_FONTSIZE, fontweight="bold", pad=12, family='serif')
    
    legend_patches_v = [
        Patch(facecolor=video_palettes["short"][2], label="Short Videos"),
        Patch(facecolor=video_palettes["medium"][2], label="Medium Videos"),
        Patch(facecolor=video_palettes["long"][2], label="Long Videos"),
    ]
    ax2.legend(handles=legend_patches_v, loc="upper right", fontsize=TICK_FONTSIZE)

    ax2.grid(axis="y", alpha=0.3, linestyle='--')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

# ═══════════════════════════════════════════════════════════
# 💾 保存
# ═══════════════════════════════════════════════════════════
plt.tight_layout()
fig.savefig("combined_statistics_medium.png", dpi=200, bbox_inches="tight")
plt.show()

print("✅ 图表已更新: Word Count 使用中等颜色")