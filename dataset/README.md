# 数据集说明

本目录是离线助手的全部数据资产，采用"小核心 + 程序生成"的管线：

## 文件清单

| 文件 | 说明 |
|---|---|
| `prompt-pack.md` | 生产管线：给大模型（DeepSeek/GPT 等）的完整提示词包，包含事实库（产品说明书要点）、四条铁律、分批生成指令。换产品/换说明书只需改事实库重跑 |
| `sft-train-v1.jsonl` | **训练实际使用的数据集**（764 条，五字段：id/category/question/answer/system_state） |
| `eval-questions-r2.json` | 对抗性评估题集（R2，训练时未见过的问法） |
| `eval-results-r2.json` | R2 评估结果：总分 21.5/30（同义改写 6/6、事实问答 5/6、兜底 4/4、拒答 4/6） |
| `quant-report.json` | INT8 动态量化 vs FP32 的对比结论（64M 模型量化后乱码/错绑，**生产用 FP32**） |

## 设计要点

1. **事实库唯一来源**：所有答案事实来自产品说明书原文（prompt-pack 里的【产品身份】块），生成时要求逐条标注出处（basis 字段），拒绝编造
2. **程序管事实，模型管话术**：`system_state`（network/cloud_model/version/usb_drive）由程序注入，模型只转述不许改；`{usb_drive}` 占位符由服务端替换成真实盘符
3. **能力边界是训练目标**：拒答类样本教模型"什么时候不要回答"，兜底类教"什么时候承认自己没听懂"
4. **system_state 里 `cloud_model=unknown` 是刻意的**：离线时读不到云端模型名
