# Lang2LTL项目Python文件说明

本文档解释了Lang2LTL项目中每个Python文件的作用和功能。

## 核心模块

### `lang2ltl.py`
Lang2LTL语言 grounding 系统的模块和API。包含指称表达式识别、命题解析和符号翻译的核心功能。

### `utils.py`
工具函数库，包含字符串操作、文件I/O和数据处理等辅助函数。提供构建占位符映射、替换等关键功能。

### `eval.py`
评估函数，包含翻译和规划的评估功能。

### `formula_sampler.py`
根据公式类型和命题数量采样提升的LTL公式。

## 数据处理

### `dataset_lifted.py`
构造用于评估提升翻译模块的训练和测试集。

### `dataset_grounded.py`
使用OSM或CleanUp地标构造 grounded 训练和测试集，用于评估完整翻译系统。

### `dataset_filtered.py`
从Gopalan等人18和Berg等人20导入测试集。

### `dataset_composed.py`
构造组合数据集的训练和测试集。

### `dataset_composed_new.py`
构造新组合数据集的训练和测试集。

### `dataset_corlw.py`
处理corlw数据集相关功能。

### `dataset_mlm.py`
处理MLM（Masked Language Modeling）数据集。

### `data_collection.py`
清理收集的提升数据集中的话语和LTL公式。

## 模型和训练

### `gpt.py`
GPT-3和GPT-4模型的接口。支持文本生成、翻译、实体提取和嵌入获取。

### `get_embed.py`
GPT-3嵌入的接口，用于生成地标和对象的语义嵌入。

### `s2s_hf_transformers.py`
使用HuggingFace微调预训练的transformer模型（如T5）。

### `s2s_pt_transformer.py`
从头训练PyTorch实现的transformer编码器-解码器模型。

### `s2s_sup_tcd.py`
监督序列到序列模型（可能用于TCD相关任务）。

### `llama_example.py`
LLaMA模型的使用示例。

## 实验脚本

### `exp_full.py`
评估完整翻译系统的主体函数，包括RER、命题解析和符号翻译。

### `exp_lifted.py`
提升翻译模块的实验。

### `exp_nl2ltl.py`
自然语言到LTL的实验。

### `exp_robot_demo.py`
机器人演示实验。

### `exp_baselines.py`
基线方法的实验。

## 分析和可视化

### `analyze_results.py`
分析结果的脚本，如混淆矩阵、错误分类等。

### `results_analysis.py`
结果分析功能。

### `plot_results.py`
绘制结果图表。

### `NL2TL_analysis.py`
自然语言到LTL的分析。

## 其他工具

### `compose.py`
组合相关功能。

### `prompt_conversion.py`
提示转换工具。

### `lang2ltl_examples.py`
Lang2LTL的使用示例。

### `tester.py`
单元测试文件。

## 总结

这个项目主要包含：
- **核心系统**：`lang2ltl.py` 提供主要API
- **数据处理**：多个`dataset_*.py`文件处理不同类型的数据集
- **模型接口**：`gpt.py`, `get_embed.py`, `s2s_*.py`等处理各种AI模型
- **实验评估**：`exp_*.py`文件运行不同类型的实验
- **分析工具**：`analyze_*.py`, `plot_*.py`等分析和可视化结果
- **工具函数**：`utils.py`, `eval.py`等提供通用功能</content>
