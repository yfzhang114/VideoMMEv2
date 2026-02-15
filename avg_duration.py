import json

with open("data_statistics.json", "r", encoding="utf-8") as f:
    data = json.load(f)

records = data if isinstance(data, list) else data.get("statistics", data.get("data", []))
durations = [r["video_duration_seconds"] for r in records if "video_duration_seconds" in r]

avg = sum(durations) / len(durations) if durations else 0
print(f"视频数量: {len(durations)}")
print(f"video_duration_seconds 平均值: {avg:.2f} 秒 ({avg/60:.2f} 分钟)")
