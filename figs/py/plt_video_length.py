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
option_individual_wc = {c: [] for c in "ABCDEFGH"}
video_durations = []

for rec in records:
    for q in range(1, 5):
        key = f"question_{q}_word_count"
        if key in rec:
            question_wc[q].append(rec[key])

    for q in range(1, 5):
        for c in "ABCDEFGH":
            key = f"option_{q}_{c}_word_count"
            if key in rec:
                option_individual_wc[c].append(rec[key])

    if "video_duration_seconds" in rec:
        video_durations.append(rec["video_duration_seconds"])

# ── 汇总 DataFrame ───────────────────────────────────────
rows = []

# Questions
for q in range(1, 5):
    for v in question_wc[q]:
        rows.append({"Category": f"Question {q}", "Word Count": v, "Group": "Questions"})

# Answers (只取正确选项的字数)
for rec in records:
    for q in range(1, 5):
        gt_key = f"gt_{q}"
        if gt_key in rec:
            correct_choice = rec[gt_key]
            ans_key = f"option_{q}_{correct_choice}_word_count"
            if ans_key in rec:
                rows.append({"Category": f"Answer {q}", "Word Count": rec[ans_key], "Group": "Answers"})

# Choices (所有选项字数)
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

# 有些类别如果样本数=1，std 会是 NaN；这里补 0，避免误差线/标注丢失
summary["std"] = summary["std"].fillna(0)

def get_group(cat):
    if cat.startswith("Question"):
        return "Questions"
    elif cat.startswith("Answer"):
        return "Answers"
    else:
        return "Choices"

summary["Group"] = summary["Category"].apply(get_group)

# ═══════════════════════════════════════════════════════════
# 🎨 配色
# ═══════════════════════════════════════════════════════════
wc_colors = {
    "Questions": ["#55AFCB", "#6ABDD6", "#80CBE0", "#97DAEA"],
    "Answers":   ["#F0A37A", "#F4B492", "#F7C6AA", "#FAD8C3"],
    "Choices":   ["#B8C0C8", "#C3CAD1", "#CED4DA", "#D9DEE3",
                  "#AEB7C0", "#A4AEB7", "#9AA4AE", "#909AA5"]
}

def get_wc_color(cat):
    if cat.startswith("Question"):
        idx = int(cat.split()[-1]) - 1
        return wc_colors["Questions"][idx % len(wc_colors["Questions"])]
    elif cat.startswith("Answer"):
        idx = int(cat.split()[-1]) - 1
        return wc_colors["Answers"][idx % len(wc_colors["Answers"])]
    else:  # Choice
        letter = cat.split()[-1]
        idx = ord(letter) - ord('A')
        return wc_colors["Choices"][idx % len(wc_colors["Choices"])]

# Video Length 配色
video_palettes = {
    "short":  ["#fae588", "#f9dc76", "#f8d364", "#f7ca52", "#f6c140"],
    "medium": ["#eeb4c3", "#ea9eb1", "#e6889f", "#e2728d", "#de5c7b"],
    "long":   ["#b8cce1", "#a6bdd6", "#94aecb", "#829fc0", "#7090b5"]
}

# ═══════════════════════════════════════════════════════════
# 🎨 绘图设置
# ═══════════════════════════════════════════════════════════
FIG_W, FIG_H = 14, 11
TITLE_FONTSIZE, AXIS_FONTSIZE, TICK_FONTSIZE = 14, 12, 10
ANNOTATION_COLOR = "#444444"
sns.set_theme(style="whitegrid", font_scale=1.0)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(FIG_W, FIG_H))

# ═══════════════════════════════════════════════════════════
# 📊（现在在上面）子图 1：Video Length Distribution
# ═══════════════════════════════════════════════════════════
durations = np.array(video_durations)
if len(durations) > 0:
    start_min = 3
    end_merge = 20
    step = 1

    edges_sec = []
    current_val = start_min
    while current_val < end_merge:
        edges_sec.append(current_val * 60)
        current_val += step
    edges_sec.append(end_merge * 60)

    max_val = durations.max()
    edges_sec.append(max(max_val + 1, (end_merge + 1) * 60))
    bin_edges = np.array(edges_sec)

    valid_durations = durations[durations >= start_min * 60]
    counts, _ = np.histogram(valid_durations, bins=bin_edges)
    n_bars = len(counts)

    final_bar_colors = []
    threshold_medium = 6
    threshold_long = 12

    for i in range(n_bars):
        current_min = start_min + i * step
        if current_min < threshold_medium:
            final_bar_colors.append(video_palettes["short"][i % len(video_palettes["short"])])
        elif current_min < threshold_long:
            j = i - (threshold_medium - start_min)
            final_bar_colors.append(video_palettes["medium"][j % len(video_palettes["medium"])])
        else:
            k = i - (threshold_long - start_min)
            final_bar_colors.append(video_palettes["long"][k % len(video_palettes["long"])])

    x_positions = np.arange(n_bars)
    ax1.bar(
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
            ax1.text(
                i, cnt + max(counts) * 0.01, str(int(cnt)),
                ha="center", va="bottom", fontsize=9,
                color=ANNOTATION_COLOR, family='serif', fontweight="bold"
            )

    x_labels = []
    for i in range(n_bars - 1):
        s = start_min + i * step
        e = s + step
        x_labels.append(f"({s}, {e}]")
    x_labels.append(f">{end_merge} min")

    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(x_labels, rotation=45, ha="right",
                        fontsize=TICK_FONTSIZE, family='serif')

    ax1.set_xlabel("Video Length (min)", fontsize=AXIS_FONTSIZE, fontweight="bold", family='serif')
    ax1.set_ylabel("Number of Videos", fontsize=AXIS_FONTSIZE, fontweight="bold", family='serif')
    ax1.set_title("Video Length Distribution", fontsize=TITLE_FONTSIZE, fontweight="bold", pad=12, family='serif')

    ax1.grid(axis="y", alpha=0.3, linestyle='--')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

# ═══════════════════════════════════════════════════════════
# 📊（现在在下面）子图 2：Word Count Statistics（均值±标准差）
# ═══════════════════════════════════════════════════════════
bar_colors_wc = [get_wc_color(cat) for cat in summary["Category"]]
x_pos = np.arange(len(summary))

ax2.bar(
    x_pos,
    summary["mean"],
    yerr=summary["std"],
    color=bar_colors_wc,
    edgecolor="#666666",
    linewidth=0.7,
    capsize=4,
    error_kw=dict(elinewidth=1.2, capthick=1.2, color="#666666"),
    width=0.75,
    zorder=3,
)

for i, (m, s) in enumerate(zip(summary["mean"], summary["std"])):
    ax2.text(
        i,
        m + s + 0.6,
        f"{m:.1f}±{s:.1f}",
        ha="center",
        va="bottom",
        fontsize=8.5,
        color=ANNOTATION_COLOR,
        family="serif",
        fontweight="bold",
    )

ax2.set_xticks(x_pos)
ax2.set_xticklabels(summary["Category"], rotation=45, ha="right",
                    fontsize=TICK_FONTSIZE, family='serif')
ax2.set_ylabel("Word Count", fontsize=AXIS_FONTSIZE, fontweight="bold", family='serif')
ax2.set_title(
    "Word Count Statistics: Questions / Answers / Choices  (Mean ± Std)",
    fontsize=TITLE_FONTSIZE, fontweight="bold", pad=12, family='serif',
)

legend_patches = [
    Patch(facecolor=wc_colors["Questions"][1], edgecolor="gray", label="Questions"),
    Patch(facecolor=wc_colors["Answers"][1], edgecolor="gray", label="Answers"),
    Patch(facecolor=wc_colors["Choices"][1], edgecolor="gray", label="Choices"),
]
ax2.legend(handles=legend_patches, loc="upper right",
           fontsize=TICK_FONTSIZE, frameon=True, fancybox=True)

ax2.set_xlim(-0.8, len(summary) - 0.2)
ax2.grid(axis="y", alpha=0.3, linestyle="--")
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# ═══════════════════════════════════════════════════════════
# 💾 保存 / 显示
# ═══════════════════════════════════════════════════════════
plt.tight_layout()
fig.savefig("figs/exps/data_sta.png", dpi=200, bbox_inches="tight")
# plt.show()

print("✅ 已输出：上-Video Length，下-Word Count，均值±标准差标注已保留")