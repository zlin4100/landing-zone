# Sample Run Output

## 单指标运行

```bash
$ python runner.py --only GDP_REAL_YOY

[1/1] GDP_REAL_YOY — 中国:GDP:不变价:当季同比
  Round 1...
  Round 2...
  -> final_indicator_id=GDP_REAL_YOY  consistency=high  confidence=high

JSON saved: outputs/reverse_results.json
CSV  saved: outputs/reverse_results.csv

--- Summary ---
  ✓ GDP_REAL_YOY                          -> GDP_REAL_YOY                    [high]
```

## JSON 输出示例（单条）

```json
{
  "raw_indicator_code": "GDP_REAL_YOY",
  "current_meaning": "中国:GDP:不变价:当季同比",
  "indicator_name": "中国:GDP:不变价:当季同比",
  "unit": "%",
  "adjustment": "YoY",
  "source": "NBS",
  "data_type": "Growth",
  "remark": "",
  "round1_indicator_id": "GDP_REAL_YOY",
  "round1_alternatives": ["GDP_CONST_YOY", "REAL_GDP_YOY"],
  "round1_confidence": "high",
  "round1_raw_response": "{...}",
  "round2_indicator_id": "GDP_REAL_YOY",
  "round2_alternatives": ["GDP_CONST_QOQ_YOY"],
  "round2_confidence": "high",
  "consistency": "high",
  "final_indicator_id": "GDP_REAL_YOY",
  "final_confidence": "high",
  "notes": ""
}
```

## Dry-run 模式

```bash
$ python runner.py --dry-run --only DR007

[1/1] DR007 — DR007
  [DRY-RUN] Round 1 system prompt: 892 chars
  [DRY-RUN] User message:
Raw indicator code: DR007
Chinese meaning: DR007
Unit: %
Adjustment type: Level
Data source: CFETS
Data category: Rate
Note: This indicator is originally 由日度转月度. This is a frequency processing detail — do NOT encode it in the indicator_id.
  [DRY-RUN] Round 2 system prompt: 654 chars

JSON saved: outputs/reverse_results.json
CSV  saved: outputs/reverse_results.csv
```
