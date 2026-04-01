"""
Radar chart for Video-MME v2 second_head_rating.

Data policy:
- Open-source models are loaded from figs/exps/performance.xlsx.
- Proprietary models fall back to explicit values because their per-dimension
  second_head_rating is not present in the checked-in workbook.
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np


CATEGORIES = [
    "Frame-Only",
    "Frames & Audio",
    "Action & Motion",
    "Order",
    "Change",
    "Temporal Reasoning",
    "Complex Plot\nComprehension",
    "Video-Based\nKnowledge Acquisition",
    "Social Behavior\nAnalysis",
    "Physical World\nReasoning",
]

XLSX_CATEGORY_KEYS = [
    "Frame-Only",
    "Frames & Audio",
    "Action & Motion",
    "Order",
    "Change",
    "Temporal Reasoning",
    "Complex Plot Comprehension",
    "Video-Based Knowledge Acquisition",
    "Social Behavior Analysis",
    "Physical World Reasoning",
]

LEVEL_COLORS = ["#A2D2D2"] * 2 + ["#F9B664"] * 4 + ["#C0BCB5"] * 4
MODEL_COLORS = ["#B67A6B", "#E7C191", "#B5BE9A", "#5E827F", "#7D3C98", "#6B7B8C"]

REPO_ROOT = Path(__file__).resolve().parents[2]
PERFORMANCE_XLSX = REPO_ROOT / "figs" / "exps" / "performance.xlsx"
OUT_PATH = REPO_ROOT / "figs" / "exps" / "radar_second_head.png"

# Current page-consistent lineup.
# Open-source models use workbook rows that match the current index.html naming.
MODEL_SPECS = [
    {"label": "Gemini-3-Pro", "row_name": None},
    {"label": "GPT-5", "row_name": None},
    {"label": "Doubao-Seed-2.0-Pro-260215", "row_name": None},
    {"label": "Qwen3-Omni-30B-A3B-Instruct", "row_name": "Qwen3-Omni-30B-A3B-Instruct-sub"},
    {"label": "Qwen3-VL-235B-A22B-Instruct", "row_name": "Qwen3-VL-235B-A22B-Instruct-w-sub"},
    {"label": "InternVL3-5-241B-A28B-Instruct", "row_name": "InternVL3_5-241B-A28B-Instruct-sub"},
]

# Proprietary fallback values kept explicit until their second_head_rating is
# exported into the workbook. These are the values currently reflected by the
# published radar figure text in index.html.
FALLBACK_MODELS = {
    "Gemini-3-Pro": [47.10, 68.26, 24.14, 55.41, 43.63, 43.17, 36.53, 44.26, 36.43, 20.94],
    "GPT-5": [27.34, 32.65, 15.22, 29.78, 31.73, 26.66, 22.24, 26.44, 19.83, 15.05],
    "Doubao-Seed-2.0-Pro-260215": [53.48, 55.31, 27.24, 65.83, 45.43, 46.79, 37.19, 43.07, 36.52, 21.63],
}


def _xlsx_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    return [
        "".join(node.text or "" for node in si.findall(".//a:t", ns))
        for si in root.findall("a:si", ns)
    ]


def _first_sheet_target(zf: zipfile.ZipFile) -> str:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    wb_root = ET.fromstring(zf.read("xl/workbook.xml"))
    rel_root = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rid_to_target = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rel_root}
    first_sheet = wb_root.find("a:sheets/a:sheet", ns)
    rid = first_sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
    return f"xl/{rid_to_target[rid]}"


def load_second_head_ratings(path: Path) -> dict[str, list[float]]:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as zf:
        shared = _xlsx_shared_strings(zf)
        sheet_root = ET.fromstring(zf.read(_first_sheet_target(zf)))

    ratings: dict[str, list[float]] = {}
    for row in sheet_root.findall(".//a:sheetData/a:row", ns):
        values: dict[str, str] = {}
        for cell in row.findall("a:c", ns):
            col = re.match(r"([A-Z]+)", cell.attrib["r"]).group(1)
            cell_type = cell.attrib.get("t")
            value_node = cell.find("a:v", ns)
            if value_node is None:
                values[col] = ""
                continue
            values[col] = shared[int(value_node.text)] if cell_type == "s" else value_node.text

        model_name = values.get("A", "")
        detail = values.get("H", "")
        if not model_name or not detail.startswith("{"):
            continue

        payload = json.loads(detail)
        second_head = payload.get("second_head_rating")
        if not second_head:
            continue

        ratings[model_name] = [float(second_head[key]) for key in XLSX_CATEGORY_KEYS]
    return ratings


def build_models() -> dict[str, list[float]]:
    workbook_ratings = load_second_head_ratings(PERFORMANCE_XLSX)
    models: dict[str, list[float]] = {}
    for spec in MODEL_SPECS:
        row_name = spec["row_name"]
        label = spec["label"]
        if row_name is None:
            models[label] = FALLBACK_MODELS[label]
            continue
        if row_name not in workbook_ratings:
            raise KeyError(f"Missing second_head_rating row: {row_name}")
        models[label] = workbook_ratings[row_name]
    return models


def main() -> None:
    models = build_models()

    num_axes = len(CATEGORIES)
    angles = np.linspace(0, 2 * np.pi, num_axes, endpoint=False).tolist()
    angles += angles[:1]

    plt.rcParams["font.family"] = "serif"

    fig = plt.figure(figsize=(13.5, 11.5), facecolor="white")
    ax = fig.add_subplot(111, polar=True)
    ax.set_facecolor("none")

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    bar_width = (2 * np.pi / num_axes) * 0.92
    ring_bottom = 78
    ax.bar(
        angles[:-1],
        10,
        width=bar_width,
        bottom=ring_bottom,
        color=LEVEL_COLORS,
        alpha=0.8,
        edgecolor="none",
        zorder=10,
    )

    for i, (name, data) in enumerate(models.items()):
        data_closed = data + data[:1]
        color = MODEL_COLORS[i % len(MODEL_COLORS)]
        ax.plot(angles, data_closed, color=color, linewidth=2.5, label=name, zorder=i + 1)
        ax.fill(angles, data_closed, color=color, alpha=0.1)

    ax.set_ylim(0, 92)
    ax.set_yticks([10, 30, 50, 70])
    ax.grid(True, axis="y", color="#E0E0E0", linestyle="--", linewidth=0.8, alpha=1, zorder=0)
    ax.grid(False, axis="x")
    ax.spines["polar"].set_visible(False)

    ax.set_rlabel_position(270)
    for label in ax.get_yticklabels():
        label.set_color("#888888")
        label.set_fontsize(10)
        label.set_path_effects([path_effects.withStroke(linewidth=2, foreground="white")])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(CATEGORIES)
    ax.tick_params(pad=24)

    for label, angle in zip(ax.get_xticklabels(), angles[:-1]):
        label.set_fontsize(11.5)
        label.set_fontweight("bold")
        label.set_color("#222222")
        label.set_bbox(
            dict(
                facecolor="white",
                edgecolor="#CCCCCC",
                linewidth=0.6,
                boxstyle="round,pad=0.18",
                alpha=1.0,
                zorder=15,
            )
        )
        ha = "left" if 0 < angle < np.pi else "right"
        if abs(angle) < 0.01 or abs(angle - np.pi) < 0.01:
            ha = "center"
        label.set_horizontalalignment(ha)

    fig.subplots_adjust(left=0.10, right=0.90, top=0.84, bottom=0.18)

    handles, labels = ax.get_legend_handles_labels()
    legend_models = fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.04),
        ncol=3,
        frameon=True,
        fontsize=10.5,
        labelspacing=1.0,
        columnspacing=1.8,
        handlelength=1.8,
    )
    legend_models.get_frame().set_boxstyle("round,pad=0.6")

    level_patches = [
        mpatches.Patch(
            facecolor="#A2D2D2",
            edgecolor="#888888",
            linewidth=0.8,
            label="Level 1: Retrieval & Aggregation",
        ),
        mpatches.Patch(
            facecolor="#F9B664",
            edgecolor="#888888",
            linewidth=0.8,
            label="Level 2: Temporal Understanding",
        ),
        mpatches.Patch(
            facecolor="#C0BCB5",
            edgecolor="#888888",
            linewidth=0.8,
            label="Level 3: Complex Reasoning",
        ),
    ]

    legend_levels = fig.legend(
        handles=level_patches,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.98),
        ncol=3,
        frameon=True,
        fontsize=10.5,
        title="Capability Levels",
        title_fontsize=12,
        labelspacing=0.8,
        handlelength=1.5,
        handleheight=1.2,
        columnspacing=1.8,
    )
    legend_levels.get_frame().set_boxstyle("round,pad=0.5")
    legend_levels.get_frame().set_edgecolor("#CCCCCC")
    legend_levels.get_frame().set_facecolor("white")
    legend_levels.get_frame().set_alpha(0.95)

    fig.add_artist(legend_models)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
