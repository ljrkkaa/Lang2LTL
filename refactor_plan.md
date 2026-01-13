# Lang2LTL项目重构计划

## 当前代码结构分析

基于对项目文件的分析，当前代码组织如下：

### 核心模块
- `lang2ltl.py`: 主要API和grounding系统
- `eval.py`: 评估函数
- `formula_sampler.py`: 公式采样

### 数据处理
- `dataset_lifted.py`: 提升翻译数据集
- `dataset_grounded.py`: grounded数据集
- `dataset_filtered.py`: 过滤数据集
- `dataset_composed.py`: 组合数据集
- `dataset_composed_new.py`: 新组合数据集
- `dataset_corlw.py`: corlw数据集
- `dataset_mlm.py`: MLM数据集
- `data_collection.py`: 数据收集清理

### 模型和训练
- `gpt.py`: GPT模型接口
- `get_embed.py`: 嵌入生成
- `s2s_hf_transformers.py`: HuggingFace transformers微调
- `s2s_pt_transformer.py`: PyTorch transformer
- `s2s_sup_tcd.py`: 监督序列到序列
- `llama_example.py`: LLaMA示例

### 实验脚本
- `exp_full.py`: 完整翻译系统评估
- `exp_lifted.py`: 提升翻译实验
- `exp_nl2ltl.py`: NL到LTL实验
- `exp_robot_demo.py`: 机器人演示
- `exp_baselines.py`: 基线方法

### 分析和可视化
- `analyze_results.py`: 结果分析
- `results_analysis.py`: 结果分析
- `plot_results.py`: 绘图
- `NL2TL_analysis.py`: NL到LTL分析

### 工具函数
- `utils.py`: 通用工具
- `compose.py`: 组合功能
- `prompt_conversion.py`: 提示转换
- `lang2ltl_examples.py`: 示例

### 测试
- `tester.py`: 单元测试

## 提议的新目录结构

```
Lang2LTL/
├── core/                    # 核心系统模块
│   ├── __init__.py
│   ├── lang2ltl.py
│   ├── eval.py
│   └── formula_sampler.py
├── data_processing/         # 数据处理脚本
│   ├── __init__.py
│   ├── dataset_lifted.py
│   ├── dataset_grounded.py
│   ├── dataset_filtered.py
│   ├── dataset_composed.py
│   ├── dataset_composed_new.py
│   ├── dataset_corlw.py
│   ├── dataset_mlm.py
│   └── data_collection.py
├── models/                  # 模型接口和训练
│   ├── __init__.py
│   ├── gpt.py
│   ├── get_embed.py
│   ├── s2s_hf_transformers.py
│   ├── s2s_pt_transformer.py
│   ├── s2s_sup_tcd.py
│   └── llama_example.py
├── experiments/             # 实验脚本
│   ├── __init__.py
│   ├── exp_full.py
│   ├── exp_lifted.py
│   ├── exp_nl2ltl.py
│   ├── exp_robot_demo.py
│   └── exp_baselines.py
├── tools/                   # 工具函数
│   ├── __init__.py
│   ├── utils.py
│   ├── compose.py
│   ├── prompt_conversion.py
│   └── lang2ltl_examples.py
├── analysis/                # 分析和可视化
│   ├── __init__.py
│   ├── analyze_results.py
│   ├── results_analysis.py
│   ├── plot_results.py
│   └── NL2TL_analysis.py
├── tests/                   # 测试
│   ├── __init__.py
│   └── tester.py
├── bash_scripts/            # 保持不变
├── outputs/                 # 保持不变
├── results/                 # 保持不变
├── data/                    # 实际数据文件目录
└── scripts/                 # 其他脚本
```

## Import更新映射

### core/lang2ltl.py
```python
# 当前
from gpt import GPT3, GPT4
from get_embed import generate_embeds
from s2s_sup_tcd import Seq2Seq
from s2s_hf_transformers import HF_MODELS
from formula_sampler import ALL_PROPS
from utils import load_from_file, save_to_file, build_placeholder_map, substitute

# 新
from models.gpt import GPT3, GPT4
from models.get_embed import generate_embeds
from models.s2s_sup_tcd import Seq2Seq
from models.s2s_hf_transformers import HF_MODELS
from core.formula_sampler import ALL_PROPS
from tools.utils import load_from_file, save_to_file, build_placeholder_map, substitute
```

### experiments/exp_full.py
```python
# 当前
from lang2ltl import rer, ground_res, ground_utterances, translate_grounded_utts
from formula_sampler import ALL_PROPS
from gpt import GPT3, GPT4
from s2s_hf_transformers import HF_MODELS
from utils import load_from_file, save_to_file, substitute_single_letter
from eval import evaluate_grounded_ltl, evaluate_lang2ltl, evaluate_plan
from formula_sampler import TYPE2NPROPS
from analyze_results import find_all_formulas

# 新
from core.lang2ltl import rer, ground_res, ground_utterances, translate_grounded_utts
from core.formula_sampler import ALL_PROPS
from models.gpt import GPT3, GPT4
from models.s2s_hf_transformers import HF_MODELS
from tools.utils import load_from_file, save_to_file, substitute_single_letter
from core.eval import evaluate_grounded_ltl, evaluate_lang2ltl, evaluate_plan
from core.formula_sampler import TYPE2NPROPS
from analysis.analyze_results import find_all_formulas
```

## 重构步骤

1. 创建新目录结构
2. 移动文件到相应目录
3. 为每个目录添加 `__init__.py` 文件
4. 更新所有import语句
5. 测试重构后的代码
6. 运行测试套件
7. 更新文档

## 注意事项

- 确保所有相对路径和数据路径保持正确
- 更新任何硬编码的模块路径
- 保持向后兼容性，如果可能
- 更新README.md和AGENTS.md以反映新结构