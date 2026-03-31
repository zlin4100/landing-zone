"""
评测流程配置

所有可调参数集中于此文件。
"""
import os

# ============================================================
# 智能体模型（被评测方）
# ============================================================

QWEN_API_KEY  = os.environ.get("QWEN_API_KEY", "")
QWEN_BASE_URL = os.environ.get(
    "QWEN_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
)
QWEN_MODEL = os.environ.get("QWEN_MODEL", "qwen3-235b-a22b-instruct-2507")

# ============================================================
# 评测器模型配置（EVALUATOR_CONFIGS）
# ============================================================
# 字段说明：
#   enabled       : True/False，是否参与本次评测
#   provider      : "anthropic" | "openai_compat"
#   model         : 模型名称（与服务商接口一致）
#   api_key_env   : 读取 API Key 的环境变量名
#   base_url      : OpenAI 兼容接口地址（anthropic 类型不需要）
#   use_json_mode : 是否启用 response_format=json_object（默认 True）
#                   DeepSeek-R1 不支持，须设为 False
#   weight        : 在集成评分中的权重（默认 1.0，同等权重）
# ============================================================

EVALUATOR_CONFIGS: dict[str, dict] = {

    # ── Anthropic Claude（主评测器，高精度）──────────────────
    "claude": {
        "enabled":     True,
        "provider":    "anthropic",
        "model":       "claude-opus-4-6",
        "api_key_env": "ANTHROPIC_API_KEY",
        "weight":      1.0,
    },

    # ── 豆包 Doubao（火山引擎）────────────────────────────────
    # 申请地址: https://console.volcengine.com/ark
    # 注意: model 填写推理接入点 ID（endpoint id），形如 ep-xxxxxxxx
    "doubao": {
        "enabled":       False,           # 设为 True 后生效
        "provider":      "openai_compat",
        "model":         os.environ.get("DOUBAO_MODEL", "doubao-seed-2-0-pro-260215"),
        "api_key_env":   "DOUBAO_API_KEY",
        "base_url":      "https://ark.cn-beijing.volces.com/api/v3",
        "use_json_mode": True,
        "weight":        1.0,
    },

    # ── DeepSeek-V3（chat，支持 JSON 模式）────────────────────
    # 申请地址: https://platform.deepseek.com
    "deepseek_v3": {
        "enabled":       False,
        "provider":      "openai_compat",
        "model":         "deepseek-chat",
        "api_key_env":   "DEEPSEEK_API_KEY",
        "base_url":      "https://api.deepseek.com/v1",
        "use_json_mode": True,
        "weight":        1.0,
    },

    # ── DeepSeek-R1（推理模型，含思维链，不支持 JSON 模式）────
    "deepseek_r1": {
        "enabled":       False,
        "provider":      "openai_compat",
        "model":         "deepseek-reasoner",
        "api_key_env":   "DEEPSEEK_API_KEY",
        "base_url":      "https://api.deepseek.com/v1",
        "use_json_mode": False,           # R1 不支持 json_object
        "weight":        1.0,
    },

    # ── 阿里千问 Qwen-Max ─────────────────────────────────────
    # 注意: 此处使用单独的环境变量 QWEN_EVAL_API_KEY
    #       以避免与智能体侧 QWEN_API_KEY 冲突（可设同一个值）
    "qwen_max": {
        "enabled":       False,
        "provider":      "openai_compat",
        "model":         "qwen-max",
        "api_key_env":   "QWEN_EVAL_API_KEY",
        "base_url":      "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "use_json_mode": True,
        "weight":        1.0,
    },

    # ── 阿里千问 Qwen-Plus（性价比更高）──────────────────────
    "qwen_plus": {
        "enabled":       False,
        "provider":      "openai_compat",
        "model":         "qwen-plus",
        "api_key_env":   "QWEN_EVAL_API_KEY",
        "base_url":      "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "use_json_mode": True,
        "weight":        0.8,             # 权重略低于 qwen-max
    },
}

# 兼容旧字段（evaluator.py 内部仍可引用）
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
EVALUATOR_MODEL   = "claude-opus-4-6"
OPTIMIZER_MODEL   = "claude-opus-4-6"

# ============================================================
# 流程参数
# ============================================================

SCORE_THRESHOLD = 7.5    # 加权均分达到该值则停止迭代
MAX_ITERATIONS  = 5      # 最大迭代轮次

# 各评分维度权重（须合计 1.0）
DIMENSION_WEIGHTS = {
    "structure_completeness": 0.20,
    "data_accuracy":          0.20,
    "analysis_depth":         0.20,
    "conclusion_clarity":     0.15,
    "actionability":          0.10,
    "professionalism":        0.10,
    "risk_disclosure":        0.05,
}

# 测试查询集
TEST_QUERIES = [
    "请对今日A股市场进行综合解读，重点关注科技板块的轮动信号与北向资金异动",
    "当前宏观环境下，北向资金持续流出与人民币汇率波动意味着什么？如何布局后市？",
    "基于今日全球市场联动数据，给出明日A股操作建议，需标注具体支撑位和阻力位，以及主要风险事件",
]

RESULTS_DIR = "eval_results"

# ============================================================
# 启动校验
# ============================================================

def validate_config():
    """
    检查必要的环境变量：
    - 智能体侧 QWEN_API_KEY 必须存在
    - 至少有一个已启用的评测器的 API Key 存在
    """
    missing_agent = []
    if not QWEN_API_KEY:
        missing_agent.append("QWEN_API_KEY")

    # 检查已启用评测器的 key
    enabled_evals = [
        (name, cfg)
        for name, cfg in EVALUATOR_CONFIGS.items()
        if cfg.get("enabled", False)
    ]
    if not enabled_evals:
        raise EnvironmentError(
            "没有启用任何评测器。\n"
            "请在 eval_config.EVALUATOR_CONFIGS 中将至少一个评测器的 enabled 设为 True。"
        )

    eval_keys_ok = any(
        os.environ.get(cfg["api_key_env"], "")
        for _, cfg in enabled_evals
    )
    if not eval_keys_ok:
        keys_needed = [cfg["api_key_env"] for _, cfg in enabled_evals]
        raise EnvironmentError(
            f"已启用的评测器均缺少 API Key。\n"
            f"请设置以下环境变量中的至少一个：{keys_needed}"
        )

    if missing_agent:
        raise EnvironmentError(
            f"缺少智能体 API Key: {missing_agent}\n"
            "请设置: export QWEN_API_KEY=your_key"
        )

    # 提示：未设置 key 的已启用评测器会在运行时自动跳过
    for name, cfg in enabled_evals:
        if not os.environ.get(cfg["api_key_env"], ""):
            print(f"  [警告] 评测器 {name!r} 已启用但 {cfg['api_key_env']} 未设置，运行时将自动跳过")
