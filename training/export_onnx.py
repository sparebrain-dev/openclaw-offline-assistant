# -*- coding: utf-8 -*-
"""
OpenClaw 离线助手 INT8 量化导出（在 minimind 仓库根目录运行）
用法: python quantize_export.py
依赖: pip install onnx onnxruntime  (远程机器上用阿里镜像装)
产出: offline_assistant_int8.onnx（约 65MB，U盘运行时用这个）
"""
import json
import time
import torch
import torch.nn as nn
from transformers import AutoTokenizer
from model.model_minimind import MiniMindConfig, MiniMindForCausalLM

WEIGHT = "out/offline_sft_v2_768.pth"
FP32_ONNX = "offline_assistant_fp32.onnx"
INT8_ONNX = "offline_assistant_int8.onnx"
SYSTEM_STATE = "[系统状态] network=offline | cloud_model=unknown | version=2026.7.35"

TEST_QUESTIONS = [
    "网关token在哪找",
    "配置文件在哪个盘找",
    "给我讲个鬼故事",
    "提示18789端口被占是啥意思",
]


class Wrapper(nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m

    def forward(self, input_ids, attention_mask):
        return self.m(input_ids=input_ids, attention_mask=attention_mask).logits


def greedy_generate(session, tokenizer, question, max_new_tokens=60):
    import numpy as np
    conv = [{"role": "system", "content": SYSTEM_STATE},
            {"role": "user", "content": question}]
    text = tokenizer.apply_chat_template(conv, tokenize=False, add_generation_prompt=True, open_thinking=False)
    ids = tokenizer(text, return_tensors="pt")["input_ids"].numpy().astype("int64")
    eos = tokenizer.eos_token_id
    for _ in range(max_new_tokens):
        # 导出的图只保留了 input_ids（全 1 mask 在追踪时被常量折叠），不要传 attention_mask
        logits = session.run(None, {"input_ids": ids})[0]
        next_id = int(logits[0, -1].argmax())
        if next_id == eos:
            break
        ids = np.concatenate([ids, [[next_id]]], axis=1)
    prompt_len = len(tokenizer(text)["input_ids"])
    return tokenizer.decode(ids[0][prompt_len:], skip_special_tokens=True).strip()


def main():
    print("1/5 加载模型……")
    model = MiniMindForCausalLM(MiniMindConfig(hidden_size=768, num_hidden_layers=8, use_moe=False))
    model.load_state_dict(torch.load(WEIGHT, map_location="cpu"), strict=True)
    model = model.float().eval()
    tokenizer = AutoTokenizer.from_pretrained("model")

    print("2/5 预热前向（填充 RoPE 缓冲区）……")
    dummy_ids = torch.randint(0, 1000, (1, 8))
    dummy_mask = torch.ones(1, 8, dtype=torch.int64)
    with torch.no_grad():
        model(input_ids=dummy_ids, attention_mask=dummy_mask)

    print("3/5 导出 FP32 ONNX……")
    wrapped = Wrapper(model)
    torch.onnx.export(
        wrapped, (dummy_ids, dummy_mask), FP32_ONNX,
        input_names=["input_ids", "attention_mask"], output_names=["logits"],
        dynamic_axes={"input_ids": {1: "seq"}, "attention_mask": {1: "seq"}, "logits": {1: "seq"}},
        opset_version=17,
    )

    print("4/5 动态量化到 INT8……")
    from onnxruntime.quantization import quantize_dynamic, QuantType
    quantize_dynamic(FP32_ONNX, INT8_ONNX, weight_type=QuantType.QInt8)

    print("5/5 INT8 抽样验证（4 道真题）……")
    import onnxruntime as ort
    session = ort.InferenceSession(INT8_ONNX, providers=["CPUExecutionProvider"])
    report = []
    for q in TEST_QUESTIONS:
        st = time.time()
        ans = greedy_generate(session, tokenizer, q)
        report.append({"question": q, "answer": ans, "seconds": round(time.time() - st, 2)})
        print(f"  Q: {q}\n  A: {ans}  ({report[-1]['seconds']}s)")

    with open("int8验证报告.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    import os
    print(f"\n✅ 完成：{INT8_ONNX}（{os.path.getsize(INT8_ONNX)/1e6:.0f} MB），验证报告 int8验证报告.json")
    print("请在 JupyterLab 下载这两个文件。")


if __name__ == "__main__":
    main()
