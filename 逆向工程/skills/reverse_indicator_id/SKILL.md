---
name: reverse-indicator-id
description: Reverse-engineer English indicator_id names for Chinese macro/market indicators using two-round Qwen 235B inference with consistency checking. Use when the user wants to: name new indicators, add entries to input_indicators.yaml, run the reverse engineering pipeline, review or interpret results from outputs/reverse_results.csv, or check which indicators have low/medium consistency and need manual review.
tools: Read, Edit, Write, Bash
---

# Reverse Indicator ID

批量逆向工程宏观/市场指标命名。给定中文指标信息，通过 Qwen 235B 两轮独立推理出最合适的英文 `indicator_id`，并进行一致性校验。

**Skill 根目录**：`逆向工程/skills/reverse_indicator_id/`（后文简称 `SKILL_DIR`）

---

## 触发场景与任务分类

| 用户意图 | 本 Skill 的任务 |
|----------|----------------|
| 给新指标命名（提供中文名/原始代码） | Phase 1 → 添加到 YAML → Phase 3 |
| 跑批量推理 | Phase 3 |
| 查看/解读结果 | Phase 4 |
| 复核 low/medium 结果 | Phase 4 + 提出建议 |

---

## Phase 1 — 收集指标信息

如果用户提供了新指标，确认以下字段（缺失的可留空，但 `raw_indicator_code` 和 `current_meaning` 必填）：

| 字段 | 说明 | 示例 |
|------|------|------|
| `raw_indicator_code` | 当前使用的英文代码（暂定名）| `MANU_PMI` |
| `current_meaning` | 中文含义（Choice 导出名或自然语言）| `中国:制造业PMI` |
| `remark` | 频率转换备注（如"由日度转月度"）| `由日度转月度` |

如需补充元数据（unit、adjustment、source、data_type），先查 `../../data-type.csv`；若 CSV 中没有，在 `supplemental_metadata.yaml` 中补充。

---

## Phase 2 — 更新 input_indicators.yaml

读取 `SKILL_DIR/input_indicators.yaml`，将新指标追加到 `indicators` 列表末尾。格式：

```yaml
  - raw_indicator_code: MANU_PMI
    current_meaning: "中国:制造业PMI"
    remark: ""
```

- `remark` 非空时填写频率处理说明（如 `由日度转月度`）
- 已存在同一 `raw_indicator_code` 的条目时，询问用户是否覆盖

---

## Phase 3 — 运行推理

进入 skill 目录后运行 runner.py。

**检查 API Key 是否已设置：**
```bash
echo $DASHSCOPE_API_KEY | head -c 10
```
若未设置，提示用户先 `export DASHSCOPE_API_KEY="sk-..."` 再继续。

**Dry-run（调试，不消耗 API）：**
```bash
cd 逆向工程/skills/reverse_indicator_id && python runner.py --dry-run
```

**跑单个指标：**
```bash
cd 逆向工程/skills/reverse_indicator_id && python runner.py --only <RAW_CODE>
```

**全量批量：**
```bash
cd 逆向工程/skills/reverse_indicator_id && python runner.py
```

等待所有指标处理完毕（每个指标约 2 次 API 调用）。

---

## Phase 4 — 解读结果

读取 `SKILL_DIR/outputs/reverse_results.csv`，重点关注：

### 一致性等级说明

| 等级 | 符号 | 处理建议 |
|------|------|----------|
| `high` | ✓ | 直接采用 `final_indicator_id` |
| `medium` | ~ | 检查 R1/R2 差异，程序已自动择优，建议人工确认 |
| `low` | ✗ | **必须人工复核**，参考 `round1_indicator_id` / `round2_indicator_id` 及 `notes` 字段 |

### 汇报格式

向用户展示结果摘要：

```
=== 逆向工程结果 ===
总计: N 个指标

✓ high (N 个):
  GDP_REAL_YOY        -> GDP_REAL_YOY
  BRENT_CRUDE         -> BRENT_CRUDE
  ...

~ medium (N 个) — 建议确认:
  FOO_BAR             -> FOO_BAR  (R1: FOO_BAR_INDEX, R2: FOO_BAR)

✗ low (N 个) — 必须人工复核:
  BAZ_QUX             -> (冲突: R1=BAZ_QUX_YOY, R2=BAZ_GROWTH_YOY)
```

对每个 `low` 结果，对比 R1/R2 差异，结合命名原则（见下方）提出推荐方案供用户确认。

---

## 命名原则速查

| 原则 | 示例 |
|------|------|
| 语义清晰，2~5 个 token | `CPI_YOY`、`PMI_MANU` |
| 公认缩写直接采用 | `DR007`、`XAUUSD`、`BRENT_CRUDE` |
| adjustment 体现在 ID 中 | 同比→`_YOY`，累计同比→`_CUM_YOY`，年度目标→`_ANNUAL` |
| 频率转换不进入 ID | "由日度转月度" 是 ETL 元数据，不是指标定义 |
| 词序：主体 + 细分 + 调整 | `LOCAL_SPECIAL_BOND_TARGET_ANNUAL` |

---

## 常见问题处理

**依赖未安装**：
```bash
cd 逆向工程/skills/reverse_indicator_id && pip install -r requirements.txt
```

**CSV 中找不到指标元数据**：在 `supplemental_metadata.yaml` 中补充，格式：
```yaml
indicators:
  NEW_CODE:
    indicator_name: "..."
    unit: "%"
    adjustment: "YoY"
    source: "NBS"
    data_type: "..."
```

**模型返回解析失败（`_parse_error: true`）**：检查 `notes` 字段的原始响应，重新对该指标单独跑一次。
