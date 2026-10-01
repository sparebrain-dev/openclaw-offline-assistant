# 权重下载

模型权重（约 287MB）超过 GitHub 单文件限制，不在本仓库内，请从 ModelScope 下载：

| 文件 | 说明 |
|---|---|
| `offline_assistant_fp32.onnx` | 生产用推理权重（FP32 ONNX） |
| `model/` | tokenizer 文件目录 |

## ModelScope 仓库（发布时填实际地址）

> TODO：权重上传后替换为实际链接
> 建议仓库名：`openclaw-offline-assistant`
> 需包含：offline_assistant_fp32.onnx、model/ 目录

下载后目录结构：

```
offline-assistant/
├── server.js
├── package.json
├── offline_assistant_fp32.onnx   ← 放这里
└── model/                        ← tokenizer 放这里
```

然后：

```bash
npm install
node server.js
# 另开终端测试
curl http://127.0.0.1:18795/healthz
```
