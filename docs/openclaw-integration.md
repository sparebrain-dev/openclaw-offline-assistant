# OpenClaw 集成指南

把本地推理服务注册为 OpenClaw 的一个模型 provider，断网时由 OpenClaw 原生兜底链自动接管。

在 `openclaw.json`（`OPENCLAW_HOME/.openclaw/openclaw.json`）的 `models.providers` 下添加：

```json
"offline-assistant": {
  "baseUrl": "http://127.0.0.1:18795/v1",
  "api": "openai-completions",
  "apiKey": "offline-assistant-local-key",
  "auth": "api-key",
  "models": [{
    "id": "minimind-64m-offline",
    "name": "MiniMind 离线应急助手",
    "reasoning": false,
    "input": ["text"],
    "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
    "contextWindow": 131072,
    "maxTokens": 128,
    "compat": { "maxTokensField": "max_tokens" }
  }],
  "localService": {
    "command": "<U盘>:/runtime/node/node.exe",
    "args": ["server.js"],
    "cwd": "<U盘>:/offline-assistant",
    "healthUrl": "http://127.0.0.1:18795/healthz",
    "readyTimeoutMs": 120000,
    "idleStopMs": 300000
  }
}
```

然后挂进兜底链（主模型排第一，离线助手链尾）：

```bash
openclaw models fallbacks add offline-assistant/minimind-64m-offline
```

## 关键机制（OpenClaw 原生支持）

- **`localService` 懒加载**：请求到来才 spawn 服务、探活 `healthUrl`、闲置 `idleStopMs` 毫秒后自动杀进程释放内存。不需要常驻
- **兜底链**：主模型请求失败自动切兜底模型，聊天不中断
- `localService.command` 必须是**绝对路径**——U 盘盘符会变，用 `server/patch-path.cjs` 在启动脚本里同步（用法：`node patch-path.cjs "<U盘根目录>"`，写配置前先跑它）

## 踩坑记录（2026.7.35 实测）

1. **必须支持 SSE 流式**：OpenClaw 发 `stream: true`，服务要回 `text/event-stream`（一次性吐完 + `data: [DONE]` 即可）
2. **contextWindow 要配大**（131072）：OpenClaw 的 agent 系统提示词约 9000 token，且会话带历史；precheck 按 contextWindow 拦请求。模型实际只用最后一条 user 消息，配大无副作用
3. **messages.content 可能是数组** `[{type:"text",text:...}]`，要兼容
4. **baseUrl 必须带 `/v1`**：OpenClaw 自己拼 `chat/completions`
5. 端口号避开网关的 18789，服务用 18795

## 已知边界（v1.0）

- 断网接管是自动的（兜底链）；**网络恢复后不会自动切回**主模型，需手动 `/model` 切换。自动切回需要程序层网络检测（状态机），见 README roadmap
- 在云端长历史会话里直接用本模型，OpenClaw 可能因历史过长触发压缩/重试，开新会话（`/new`）最稳
