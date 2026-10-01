# 训练与导出复现

## 1. 环境

- GPU：任意一张 N 卡即可（我们在 RTX 5090 上几分钟跑完；H800 亦可）
- 镜像要求：**CUDA 12.8+**（Blackwell 架构显卡如 5090 必须，12.4 会报 "no kernel image"）
- 依赖（精简安装，**不要**跑官方 requirements.txt 全量装，`ujson==5.1.0` 在 Python 3.12 无预编译包会卡死）：

```bash
pip install datasets==3.6.0 transformers==4.57.6 modelscope sentencepiece ujson -i https://mirrors.aliyun.com/pypi/simple/
pip install torch --index-url https://download.pytorch.org/whl/cu128
```

## 2. 基座权重

从 ModelScope 下载（注意仓库名，搞错会 404）：

- PyTorch 原生权重（训练用）：`gongjy/minimind-3-pytorch` → `full_sft_768.pth`
- transformers 格式（tokenizer 用）：`gongjy/minimind-3`

## 3. 训练

在 minimind 仓库根目录（trainer/ 的上一级）执行：

```bash
cd trainer   # 必须从 trainer/ 目录内跑，脚本的 ../model、../out 是相对 trainer/ 的
python train_full_sft.py \
  --data_path ../dataset/sft_offline.jsonl \
  --from_weight full_sft \
  --save_weight offline_sft \
  --epochs 3 --batch_size 32 --learning_rate 1e-5 --max_seq_len 512
```

- 764 条 ÷ batch 32 = 每轮 24 步，3 轮共 72 步
- 验收：loss 从 2~3 降到 1 以下；产出 `out/offline_sft_768.pth`（约 130MB）

## 4. 评估（可选，导出前自检）

```bash
# 在 minimind 仓库根目录，放好 对抗性评估题集-r2.json
python eval_offline.py   # 逐题推理，产出 评估结果.json
```

## 5. 导出 ONNX（部署用）

```bash
# 在 minimind 仓库根目录
pip install onnx onnxruntime
python export_onnx.py    # 本仓库 training/export_onnx.py
# 产出 offline_assistant_fp32.onnx（约 287MB）
```

导出要点（export_onnx.py 已处理）：

- 只暴露 `input_ids` 一个输入（attention_mask 被常量折叠进去，推理端不要传）
- ChatML 模板手动拼：`<|im_start|>system\n...<|im_end|>\n<|im_start|>user\n...`，eos = `<|im_end|>`（id=2），tokenizer 不自动加 BOS
- **INT8 动态量化已实验证明不可用**（64M 模型太小，量化后乱码/答案错绑），生产用 FP32。对比数据见 dataset/quant-report.json

## 6. tokenizer 文件

导出后把 `gongjy/minimind-3`（transformers 格式）仓库里的 tokenizer 相关文件（tokenizer.json、tokenizer_config.json、special_tokens_map.json、vocab 等）放进 `model/` 目录，与 ONNX 一起部署。
