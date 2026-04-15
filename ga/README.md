# GA 参数索引

本目录存储遗传算法 (genetic_optimize.py) 的候选基因配置和参数模板。

## 文件说明

| 文件 | 说明 |
|------|------|
| `genes.json` | 活跃基因配置 — genetic_optimize.py 实际使用的参数空间和权重 |
| `templates/base.json` | 基础模板（4 参数：min_score / sl / tp / vol） |
| `templates/advanced.json` | 进阶模板（8 参数：含 momentum、cooldown、margin 等） |
| `history/` | 每次 GA 运行的结果快照（自动保存） |

## 基因扩展历史

| 版本 | 基因数 | 新增维度 | 日期 |
|------|--------|----------|------|
| v1 | 4 | min_score, sl_pct, tp_pct, min_vol_m | 原始 |
| v2 | 8 | momentum_window, cooldown_ticks, margin_range, direction_penalty | 2025-04-16 |

## 使用方式

GA 启动时读取 `genes.json` 中的 `GENES` 数组初始化基因空间：
```json
{
  "GENES": [
    { "name": "min_score", "lo": 15, "hi": 55, "step": 1 },
    ...
  ]
}
```
