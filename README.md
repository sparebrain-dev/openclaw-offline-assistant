# OpenClaw Offline Assistant（OpenClaw 离线应急助手）

让便携版 OpenClaw（U 盘运行环境）在**断网时不会"死掉"**：自动降级为一个 64M 参数的本地小模型，继续提供基础交互与故障引导；网络恢复后交还云端大模型。

> English abstract: A MiniMind-based (64M) local fallback assistant for portable OpenClaw setups. When the cloud LLM becomes unreachable, OpenClaw's native fallback chain routes to this OpenAI-compatible local service, which explains the situation and guides users — no GPU, no Python, pure CPU on the USB stick.

## 架构：双层 AI + 程序管事实

```
在线:  用户 → OpenClaw → 云端大模型（DeepSeek / Kimi / GPT...）  ← 完整能力
                        ↓ 请求失败（断网）
离线:  用户 → OpenClaw → MiniMind 64M 本地模型（本仓库）        ← 应急话术
```

设计铁律：**程序负责事实，模型负责话术**。

- 网络状态、当前模型、版本号、盘符由程序注入（`system_state`），模型只转述、不许编造
- `{usb_drive}` 占位符由服务端替换为真实盘符
- 模型答不出中文 → 兜底话术兜底
- 对超出能力的问题（天气/新闻/写程序…）→ 明确拒答并引导恢复网络

## 特性

- **超轻量**：64M 参数，CPU 推理，约 1 秒/题；首次加载约 4 秒（从 U 盘读入内存后常驻）
- **零依赖部署**：Node.js 单进程（U 盘自带 Node v24），无 Python、无 GPU
- **OpenAI 兼容**：`/v1/chat/completions` + SSE 流式，任何支持自定义 OpenAI 端点的 Agent 框架可直接接入
- **懒加载**：OpenClaw 原生 `localService` 机制——断网接管时才启动，闲置 5 分钟自动关停释放内存
- **盘符自适应**：U 盘插任何 Windows 电脑、任何盘符都能工作

## 快速开始

```bash
cd server
npm install
# 下载权重（见 scripts/WEIGHTS.md，托管于 ModelScope：sparebrain/openclaw-offline-assistant）：offline_assistant_fp32.onnx + model/ 放到本目录
node server.js
```

```bash
curl -X POST http://127.0.0.1:18795/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"minimind-64m-offline","messages":[{"role":"user","content":"怎么切换模型"}]}'
```

OpenClaw 接入：见 [docs/openclaw-integration.md](docs/openclaw-integration.md)（约 20 行配置 + 一条命令）。

## 评测结果（对抗性，训练时未见过的问法）

| 维度 | 得分 | 说明 |
|---|---|---|
| 同义改写识别 | 6/6 | 错别字/断句乱/老人式表达都能认 |
| 事实问答 | 5/6 | 端口占用、切换模型、token 位置等 |
| 兜底识别 | 4/4 | 乱码/无语义输入不乱答 |
| 拒答边界 | 4/6 | 不会编新闻、不会假装联网 |
| **总分** | **21.5/30** | 明细见 dataset/eval-results-r2.json |

整机实测：断网 → 新对话自动接管 ✅ / 联网 → 手动切回 ⚠️（见 roadmap）

## 仓库结构

```
├── server/           # Node 推理服务（生产方案）+ OpenClaw 路径同步脚本
│   └── python-service.py   # Python 版服务（备选，需 Python 环境）
├── training/         # 训练复现 + ONNX 导出 + 评估脚本
├── dataset/          # 提示词管线、SFT 数据、评测集与结果
├── docs/             # OpenClaw 集成指南（含踩坑）
└── scripts/WEIGHTS.md# 权重下载
```

## 已知边界（v1.0）

1. 网络恢复后**不自动切回**云端模型（OpenClaw 兜底链只顶班不交还），需手动 `/model` 切换
2. 这是 64M 参数的"备用小脑"，不是离线版 GPT——它的价值是知道自己不会什么

## Roadmap

- [ ] 状态机：程序层网络检测 → 判定恢复 → 自动切回云端 + 释放本地模型内存
- [ ] v3 数据微补：清理偶发的 `<think>` 标签输出、placeholder 路径题强化
- [ ] 模型服务加载失败时的静态降级提示页
- [ ] 权重托管（ModelScope）与一键下载脚本

## 训练数据从哪来

全部自产：人工写 63 条核心问答 → 用大模型按提示词包扩写同义表达与干扰样本（764 条）。提示词包（含事实库与四条数据铁律）在 `dataset/prompt-pack.md`，换成你自己的产品说明书即可复用整条管线。

## 致谢与许可

- 基座模型 [MiniMind](https://github.com/jingyaogong/minimind)（Apache 2.0），微调权重为其衍生作品，沿用同许可证，详见 [NOTICE](NOTICE)
- 本项目与 OpenClaw 官方无关，"OpenClaw" 仅用于描述兼容性
- 训练/评估代码与数据集：Apache 2.0

## 免责声明

本助手输出的事实性指引（端口、路径、命令）基于特定版本说明书训练，仅供应急参考；请以你所用版本的官方文档为准。
