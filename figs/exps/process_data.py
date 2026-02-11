""" Transform performance.xlsx: extract level_1, level_2, level_3 from 详细结果 and simplify. """
import pandas as pd
import json
import re

EXCEL_PATH = "figs/exps/performance.xlsx"
OUTPUT_PATH = "figs/exps/performance_clean.xlsx"


def extract_levels(val):
    """Extract level_1, level_2, level_3 from cell value (string/dict/JSON)."""
    if pd.isna(val):
        return None, None, None
    s = str(val).strip()
    if not s or s == "nan":
        return None, None, None

    # Try JSON parse
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return (
                obj.get("level_1"),
                obj.get("level_2"),
                obj.get("level_3"),
            )
    except (json.JSONDecodeError, TypeError):
        pass

    # Try regex extraction for "level_1": 15.84... style
    result = {}
    for key in ["level_1", "level_2", "level_3"]:
        m = re.search(rf'"{key}"\s*:\s*([0-9.]+)', s)
        if m:
            try:
                result[key] = float(m.group(1))
            except ValueError:
                result[key] = None
        else:
            result[key] = None
    return result.get("level_1"), result.get("level_2"), result.get("level_3")


def main():
    df = pd.read_excel(EXCEL_PATH)

    # Find the column containing detailed results (likely named 详细结果 or similar)
    detail_col = None
    for col in df.columns:
        col_str = str(col).strip().lower()
        if "详细" in str(col) or "detail" in col_str or "result" in col_str:
            # Check if it contains level_1
            sample = str(df[col].iloc[0]) if len(df) > 0 else ""
            if "level_1" in sample:
                detail_col = col
                break

    if detail_col is None:
        # Fallback: find any column containing level_1
        for col in df.columns:
            sample = str(df[col].iloc[0]) if len(df) > 0 else ""
            if "level_1" in sample:
                detail_col = col
                break

    if detail_col is None:
        raise ValueError(
            "Could not find column with detailed results (level_1, level_2, level_3). "
            f"Columns: {df.columns.tolist()}"
        )

    # Extract level values
    extracted = df[detail_col].apply(extract_levels)
    df["level_1"] = [e[0] for e in extracted]
    df["level_2"] = [e[1] for e in extracted]
    df["level_3"] = [e[2] for e in extracted]

    # Drop the detailed results column
    df = df.drop(columns=[detail_col])

    df.to_excel(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
