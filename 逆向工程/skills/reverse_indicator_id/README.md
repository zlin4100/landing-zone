# Reverse Indicator ID Skill

批量逆向工程宏观/市场指标代码：给定中文指标信息，通过 Qwen 235B 推理出最合适的英文 `indicator_id`。

## 核心机制：两轮独立推理 + 一致性校验

### 为什么要两轮？

单次模型输出可能受 prompt 措辞、采样随机性影响。两轮独立调用（Round 1 和 Round 2 使用不同系统 prompt、完全独立的上下文）可以验证命名建议的稳定性：

- **Round 1**：完整推理，输出推荐 ID + 备选 + 命名理由
- **Round 2**：新上下文，仅输出推荐 ID + 备选（不带 Round 1 结果）
- **比较**：两轮结果一致性 → high / medium / low

如果两轮独立给出相同答案，该命名的可信度显著提升。

### indicator_id 命名原则

| 原则 | 说明 |
|------|------|
| 语义清晰 | 金融分析师一眼能看出指标含义 |
| 贴近金融研究习惯 | CPI_YOY, PMI_MANU, DR007 等 |
| adjustment 体现在 ID 中 | 同比 → `_YOY`，累计同比 → `_CUM_YOY` |
| 不编码频率转换信息 | "由日度转月度" 是处理方式，不是指标本体 |
| 适合 LLM 理解 | 不是数据库短码，也不是 Wind/Choice 原始代码 |

### 为什么"由日度转月度"不进入 indicator_id？

`indicator_id` 定义的是"这个指标是什么"，而非"这个指标怎么来的"。频率转换（日→月）属于 ETL 处理层面的元数据，应通过 `source_tag` 或单独字段记录，不应污染指标的语义命名。

### 为什么 adjustment 应体现在 indicator_id 中？

同一个指标的不同 adjustment（同比、环比、累计值、水平值）在分析中含义完全不同。`CPI_YOY` 和 `CPI_MOM` 是两个不同的分析对象，必须通过 ID 区分。

## 环境配置

```bash
# 安装依赖
pip install -r requirements.txt

# 设置 API Key（二选一）
export DASHSCOPE_API_KEY="sk-your-key-here"
# 或在 .env 文件中：
# DASHSCOPE_API_KEY=sk-your-key-here

# 可选：指定模型
export QWEN_MODEL="qwen3-235b-a22b-instruct-2507"
```

## 使用方式

```bash
# 进入 skill 目录
cd skills/reverse_indicator_id

# Dry-run：查看 prompt 但不调用 API
python runner.py --dry-run

# 跑单个指标
python runner.py --only GDP_REAL_YOY

# 全量批量跑
python runner.py

# 自定义输入/输出
python runner.py --input my_indicators.yaml --csv ../../data-type.csv --output-dir my_outputs
```

### 命令行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--input` | `input_indicators.yaml` | 输入指标 YAML |
| `--csv` | `../../data-type.csv` | CSV 元数据文件 |
| `--supplemental` | `supplemental_metadata.yaml` | 补充元数据 YAML |
| `--output-dir` | `outputs/` | 输出目录 |
| `--only` | 无 | 只处理指定指标 |
| `--dry-run` | false | 不调用 API，仅打印 prompt |

## 输入文件

### input_indicators.yaml

```yaml
indicators:
  - raw_indicator_code: GDP_REAL_YOY
    current_meaning: "中国:GDP:不变价:当季同比"
    remark: ""
```

### data-type.csv

提供 indicator_name, unit, adjustment, source, data_type 等元数据。如果 CSV 中缺失某个指标，自动从 `supplemental_metadata.yaml` 补齐。

## 输出

### reverse_results.json

完整结果，包含两轮原始 response、一致性评估、最终推荐 ID。

### reverse_results.csv

精简表格，适合快速浏览和人工复核。

### 输出示例

```
[1/16] GDP_REAL_YOY — 中国:GDP:不变价:当季同比
  Round 1...
  Round 2...
  -> final_indicator_id=GDP_REAL_YOY  consistency=high  confidence=high

--- Summary ---
  ✓ GDP_REAL_YOY                          -> GDP_REAL_YOY                    [high]
  ~ BRENT_CRUDE                           -> BRENT_OIL                       [medium]
  ✗ SOME_INDICATOR                        -> NEEDS_REVIEW                    [low]
```

## 扩展

添加新指标：编辑 `input_indicators.yaml`，添加新条目即可。如果 CSV 中没有对应元数据，在 `supplemental_metadata.yaml` 中补充。
