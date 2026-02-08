import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

# ── 读取数据 ──────────────────────────────────────────────
with open("data_statistics.json", "r", encoding="utf-8") as f:
    data = json.load(f)

records = data if isinstance(data, list) else data.get("statistics", data.get("data", []))

# ── 提取统计量 ────────────────────────────────────────────
question_wc = {i: [] for i in range(1, 5)}
option_total_wc = {i: [] for i in range(1, 5)}        # 整道题所有选项总字数
option_individual_wc = {c: [] for c in "ABCDEFGH"}    # 单个选项字数（跨所有题目汇总）
video_durations = []

for rec in records:
    # question word counts
    for q in range(1, 5):
        key = f"question_{q}_word_count"
        if key in rec:
            question_wc[q].append(rec[key])

    # per-choice word counts (A-H) & per-question option total
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

    # video duration
    if "video_duration_seconds" in rec:
        video_durations.append(rec["video_duration_seconds"])

# ── 汇总 DataFrame ───────────────────────────────────────
rows = []
for q in range(1, 5):
    for v in question_wc[q]:
        rows.append({"Category": f"Question {q}", "Word Count": v, "Group": "Questions"})

# 用 gt_X 找到正确选项并统计 answer word count
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
# 定义排序
order = [f"Question {i}" for i in range(1, 5)] + \
        [f"Answer {i}" for i in range(1, 5)] + \
        [f"Choice {c}" for c in "ABCDEFGH"]
summary["Category"] = pd.Categorical(summary["Category"], categories=order, ordered=True)
summary = summary.sort_values("Category").dropna(subset=["Category"])

# 给 group 染色
def get_group(cat):
    if cat.startswith("Question"):
        return "Questions"
    elif cat.startswith("Answer"):
        return "Answers"
    else:
        return "Choices"

summary["Group"] = summary["Category"].apply(get_group)

# ═══════════════════════════════════════════════════════════
# 🎨  图 1 – 柱状图：均值 + 方差 (error bar)
# ═══════════════════════════════════════════════════════════
sns.set_theme(style="whitegrid", font_scale=1.15)

palette_map = {
    "Questions": "#4C72B0",
    "Answers": "#DD8452",
    "Choices": "#55A868",
}

fig1, ax1 = plt.subplots(figsize=(18, 7))

colors = [palette_map[g] for g in summary["Group"]]
x_pos = np.arange(len(summary))

bars = ax1.bar(
    x_pos,
    summary["mean"],
    yerr=summary["std"],
    color=colors,
    edgecolor="white",
    linewidth=1.2,
    capsize=5,
    error_kw=dict(elinewidth=1.5, capthick=1.5, color="#333333"),
    width=0.65,
    zorder=3,
)

# 在柱顶标注数值
for i, (m, s) in enumerate(zip(summary["mean"], summary["std"])):
    ax1.text(
        i, m + s + 0.3, f"{m:.1f}±{s:.1f}",
        ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#333333",
    )

ax1.set_xticks(x_pos)
ax1.set_xticklabels(summary["Category"], rotation=40, ha="right", fontsize=11)
ax1.set_ylabel("Word Count", fontsize=13, fontweight="bold")
ax1.set_title(
    "Word Count Statistics: Questions / Answers / Choices  (Mean ± Std)",
    fontsize=16, fontweight="bold", pad=15,
)

# 图例
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=v, edgecolor="white", label=k) for k, v in palette_map.items()]
ax1.legend(handles=legend_elements, loc="upper right", fontsize=12, frameon=True, fancybox=True)

ax1.set_xlim(-0.6, len(summary) - 0.4)
ax1.grid(axis="y", alpha=0.4)
sns.despine(left=True, bottom=True)

fig1.tight_layout()
fig1.savefig("fig1_word_count_stats.png", dpi=200, bbox_inches="tight")
plt.show()

# ═══════════════════════════════════════════════════════════
# 🎨  图 2 – 视频时长分布直方图
# ═══════════════════════════════════════════════════════════
durations = np.array(video_durations)
dur_min, dur_max = durations.min(), durations.max()

# 均匀分 ~10 个 bin（向下/上取整到 10 秒整数边界，更美观）
bin_start = int(np.floor(dur_min / 30) * 30)
bin_end   = int(np.ceil(dur_max / 30) * 30) + 1
n_bins    = 10
bins = np.linspace(bin_start, bin_end, n_bins + 1)

fig2, ax2 = plt.subplots(figsize=(14, 6))

# KDE + 直方图
sns.histplot(
    durations,
    bins=bins,
    kde=True,
    color="#6A89CC",
    edgecolor="white",
    linewidth=1.2,
    alpha=0.75,
    line_kws=dict(linewidth=2.5, color="#E55039"),
    ax=ax2,
    stat="count",
)

# 在每个柱上标注数量
counts, bin_edges = np.histogram(durations, bins=bins)
for i, cnt in enumerate(counts):
    if cnt > 0:
        ax2.text(
            (bin_edges[i] + bin_edges[i + 1]) / 2,
            cnt + 0.5,
            str(cnt),
            ha="center", va="bottom", fontsize=11, fontweight="bold", color="#333333",
        )

# 加均值竖线
mean_dur = durations.mean()
ax2.axvline(mean_dur, color="#E55039", linestyle="--", linewidth=2, label=f"Mean = {mean_dur:.1f}s")

ax2.set_xlabel("Video Duration (seconds)", fontsize=13, fontweight="bold")
ax2.set_ylabel("Number of Videos", fontsize=13, fontweight="bold")
ax2.set_title(
    f"Video Duration Distribution  (N={len(durations)},  "
    f"range {dur_min:.0f}s – {dur_max:.0f}s)",
    fontsize=16, fontweight="bold", pad=15,
)
ax2.legend(fontsize=12, frameon=True, fancybox=True)
ax2.grid(axis="y", alpha=0.35)
sns.despine(left=True, bottom=True)

fig2.tight_layout()
fig2.savefig("fig2_video_duration_distribution.png", dpi=200, bbox_inches="tight")
plt.show()

print("✅  两张图已保存: fig1_word_count_stats.png  /  fig2_video_duration_distribution.png")