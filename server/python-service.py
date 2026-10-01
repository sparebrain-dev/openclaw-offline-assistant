# -*- coding: utf-8 -*-
"""
OpenClaw 离线助手 · 本地推理服务
- OpenAI 兼容接口 POST /v1/chat/completions（监听 127.0.0.1，只给本机 openclaw 用）
- 程序管事实：系统状态由本服务注入（state.json），模型只负责措辞
- 输出做 {usb_drive} -> 实际盘符 的替换
- 护栏：回答若不含任何中文，判定为乱码，替换为兜底话术
用法: python offline_service.py [--port 18795]
"""
import argparse
import json
import os
import re
import threading
import time

import numpy as np
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from transformers import AutoTokenizer
import onnxruntime as ort

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ONNX_PATH = os.path.join(BASE_DIR, "offline_assistant_fp32.onnx")
TOKENIZER_DIR = os.path.join(BASE_DIR, "model")
STATE_PATH = os.path.join(BASE_DIR, "state.json")

FALLBACK_ANSWER = "我是离线应急助手，能力有限，没能理解你的问题。恢复网络后可以获得完整帮助。"
MAX_NEW_TOKENS_CAP = 128

DEFAULT_STATE = {
    "network": "offline",
    "cloud_model": "unknown",
    "version": "2026.7.35",
    "usb_drive": "E:",
}

state = dict(DEFAULT_STATE)
if os.path.exists(STATE_PATH):
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state.update(json.load(f))

tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_DIR)
session = ort.InferenceSession(ONNX_PATH, providers=["CPUExecutionProvider"])
lock = threading.Lock()
app = FastAPI(title="OpenClaw Offline Assistant")

CJK = re.compile(r"[\u4e00-\u9fff]")


def build_system() -> str:
    return (f"[系统状态] network={state['network']} | cloud_model={state['cloud_model']}"
            f" | version={state['version']}")


def generate(question: str, max_new_tokens: int = 64) -> str:
    # 与训练/评估完全一致的 ChatML 模板（手动拼装，免 jinja2 依赖）
    text = (f"<|im_start|>system\n{build_system()}<|im_end|>\n"
            f"<|im_start|>user\n{question}<|im_end|>\n"
            f"<|im_start|>assistant\n")
    ids = np.array([tokenizer(text)["input_ids"]], dtype="int64")
    prompt_len = ids.shape[1]
    eos = tokenizer.eos_token_id
    with lock:
        for _ in range(min(max_new_tokens, MAX_NEW_TOKENS_CAP)):
            logits = session.run(None, {"input_ids": ids})[0]
            nxt = int(logits[0, -1].argmax())
            if nxt == eos:
                break
            ids = np.concatenate([ids, [[nxt]]], axis=1)
    answer = tokenizer.decode(ids[0][prompt_len:], skip_special_tokens=True).strip()
    # 程序管事实：占位符替换 + 乱码护栏
    answer = answer.replace("{usb_drive}", state["usb_drive"])
    if not CJK.search(answer):
        answer = FALLBACK_ANSWER.replace("{usb_drive}", state["usb_drive"])
    return answer


@app.post("/v1/chat/completions")
async def chat_completions(req: Request):
    body = await req.json()
    messages = body.get("messages", [])
    user_msg = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
    max_tokens = int(body.get("max_tokens", 64) or 64)
    st = time.time()
    answer = generate(user_msg, max_tokens)
    return JSONResponse({
        "id": "chatcmpl-offline",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "offline-assistant",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": answer},
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "elapsed_seconds": round(time.time() - st, 2),
        },
    })


@app.get("/healthz")
async def healthz():
    return {"ok": True, "state": state}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18795)
    args = parser.parse_args()
    print(f"离线助手服务启动：http://127.0.0.1:{args.port}  state={state}")
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
