"""Read performance_parsed.xlsx and output as JSON for leaderboard update."""
import pandas as pd
import json

df = pd.read_excel("figs/exps/performance_parsed.xlsx", sheet_name=None)
for sheet_name, sheet_df in df.items():
    print(f"=== Sheet: {sheet_name} ===")
    print("Columns:", sheet_df.columns.tolist())
    sheet_df.columns = [str(c).strip() for c in sheet_df.columns]
    # Output as JSON-serializable
    records = sheet_df.to_dict(orient="records")
    for r in records:
        print(json.dumps(r, ensure_ascii=False, default=str))
    print()
