# -*- coding: utf-8 -*-
"""
OpenClaw 离线助手 · 对抗性评估脚本
用法（在 minimind 仓库根目录下）：  python eval_offline.py
依赖文件：./model/（tokenizer）、./out/offline_sft_768.pth、./对抗性评估题集.json
产出：./评估结果.json（逐题记录问题/回答/耗时）
"""
import json
import time
import torch
from transformers import AutoTokenizer
from model.model_minimind import MiniMindConfig, MiniMindForCausalLM

SYSTEM_STATE = "[系统状态] network=offline | cloud_model=unknown | version=2026.7.35"
QUESTION_FILE = "对抗性评估题集.json"
RESULT_FILE = "评估结果.json"
WEIGHT_PATH = "out/offline_sft_768.pth"
MAX_NEW_TOKENS = 120

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained("model")
    model = MiniMindForCausalLM(MiniMindConfig(hidden_size=768, num_hidden_layers=8, use_moe=False))
    model.load_state_dict(torch.load(WEIGHT_PATH, map_location=device), strict=True)
    model = model.half().eval().to(device)
    print(f"✅ 模型加载完成：{WEIGHT_PATH}（device={device}）")

    with open(QUESTION_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    results = []
    for item in questions:
        conversation = [
            {"role": "system", "content": SYSTEM_STATE},
            {"role": "user", "content": item["question"]},
        ]
        inputs_text = tokenizer.apply_chat_template(
            conversation, tokenize=False, add_generation_prompt=True, open_thinking=False
        )
        inputs = tokenizer(inputs_text, return_tensors="pt", truncation=True).to(device)
        st = time.time()
        with torch.no_grad():
            generated_ids = model.generate(
                inputs=inputs["input_ids"], attention_mask=inputs["attention_mask"],
                max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                pad_token_id=tokenizer.pad_token_id, eos_token_id=tokenizer.eos_token_id,
            )
        answer = tokenizer.decode(generated_ids[0][len(inputs["input_ids"][0]):], skip_special_tokens=True)
        elapsed = time.time() - st
        results.append({
            "id": item["id"],
            "category": item["category"],
            "question": item["question"],
            "answer": answer.strip(),
            "seconds": round(elapsed, 2),
            "expect": item.get("expect", ""),
            "must_contain": item.get("must_contain", []),
            "must_not": item.get("must_not", []),
        })
        print(f"[{item['id']}] {item['question']}")
        print(f"    🧠 {answer.strip()}")
        print(f"    ⏱ {elapsed:.1f}s")
        print()

    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ 完成，结果已写入 {RESULT_FILE}，请在 JupyterLab 中下载该文件")

if __name__ == "__main__":
    main()
