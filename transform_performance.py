from pathlib import Path
import re
import json
import pandas as pd


IN_PATH = Path(r"figs\exps\performance.xlsx")
OUT_PATH = IN_PATH.with_name(IN_PATH.stem + "_parsed.xlsx")


def _normalize_json_cell(x: object) -> str | None:
    """把 Excel 单元格里的“详细结果”清洗成可 json.loads 的字符串；不合法则返回 None。"""
    if x is None:
        return None
    if not isinstance(x, str):
        return None

    s = x.strip()
    if not s:
        return None

    # 一些单元格可能写“在推”等非 JSON 标记
    if s in {"在推", "NA", "N/A", "-", "—"}:
        return None

    # 有的内容前面会多一个字符（例如 'a{...}'），取第一个 '{' 到最后一个 '}'
    m = re.search(r"\{", s)
    if not m:
        return None
    s = s[m.start():]
    last = s.rfind("}")
    if last == -1:
        return None
    s = s[: last + 1]

    # 你示例里有很多 ""final_rating"" 这种双引号重复（Excel/导出造成），统一替换
    s = s.replace('""', '"')

    # 若整段又被额外包了一层引号，去掉（尽量保守）
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1].strip()

    return s


def _extract_levels(detail_cell: object) -> tuple[float | None, float | None, float | None]:
    """从详细结果里抽 level_1/2/3。失败返回 (None, None, None)。"""
    s = _normalize_json_cell(detail_cell)
    if s is None:
        return None, None, None

    try:
        obj = json.loads(s)
    except Exception:
        return None, None, None

    fr = obj.get("final_rating", {}) if isinstance(obj, dict) else {}
    l1 = fr.get("level_1")
    l2 = fr.get("level_2")
    l3 = fr.get("level_3")

    def to_float(v):
        try:
            return float(v)
        except Exception:
            return None

    return to_float(l1), to_float(l2), to_float(l3)


def _extract_relevance_logic(detail_cell: object) -> tuple[float | None, float | None]:
    """从详细结果里抽 relevance_score、logic_score。失败返回 (None, None)。"""
    
    s = _normalize_json_cell(detail_cell)
    
    if s is None:
        return None, None

    try:
        obj = json.loads(s)
    except Exception:
        return None, None

    if not isinstance(obj, dict):
        return None, None
    # import pdb; pdb.set_trace()
    fr = obj.get("final_rating", {}) if isinstance(obj, dict) else {}
    rel = fr.get("relevance_score")
    logic = fr.get("logic_score")

    def to_float(v):
        try:
            return float(v)
        except Exception:
            return None

    return to_float(rel), to_float(logic)


def process_sheet(df: pd.DataFrame) -> pd.DataFrame:
    # 列名去空格，避免 “总Acc ” 这种匹配不到
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    if "总Acc" not in df.columns:
        raise KeyError("未找到列：总Acc（请检查表头是否一致）")
    if "详细结果" not in df.columns:
        # 没有该列就原样返回
        return df

    # 用详细结果中的 relevance_score、logic_score 覆盖 相关性Acc、逻辑链Acc
    # import pdb; pdb.set_trace()
    scores = df["详细结果"].apply(_extract_relevance_logic)
    if "相关性Acc" in df.columns:
        df["相关性Acc"] = scores.apply(lambda t: t[0])
    if "逻辑链Acc" in df.columns:
        df["逻辑链Acc"] = scores.apply(lambda t: t[1])

    levels = df["详细结果"].apply(_extract_levels)
    df["Level 1"] = levels.apply(lambda t: t[0])
    df["Level 2"] = levels.apply(lambda t: t[1])
    df["Level 3"] = levels.apply(lambda t: t[2])

    # 插入到 “总Acc” 后面
    insert_at = df.columns.get_loc("总Acc") + 1
    for col in ["Level 1", "Level 2", "Level 3"]:
        series = df.pop(col)
        df.insert(insert_at, col, series)
        insert_at += 1

    # 删除详细结果列
    df = df.drop(columns=["详细结果"])
    return df


def main():
    xls = pd.ExcelFile(IN_PATH, engine="openpyxl")

    with pd.ExcelWriter(OUT_PATH, engine="openpyxl") as writer:
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, engine="openpyxl")
            out_df = process_sheet(df)
            out_df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()