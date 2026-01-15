实现总结
我已经基于 nba_cut.md 中的研究模式实现了一个完整的 NBA（非确定性 Büchi 自动机）剪枝系统。实现包括 4 个 Python 模块：
创建的文件
| 文件 | 目的 | 行数 |
|------|---------|-------|
| nba_graph.py | 核心数据结构 (Transition, BuchiAutomaton) | ~185 |
| parser.py | Promela "never claim" 解析器 | ~95 |
| pruner.py | 三阶段剪枝算法 | ~240 |
| main.py | 带有 DOT 导出的 CLI 接口 | ~80 |
剪枝管道
1. 不可行性剪枝：移除需要比可用代理更多的并发动作或包含冲突任务组合的转换。
2. 可达性剪枝：使用从初始状态的前向 BFS 和从接受状态的后向 BFS 来移除死端和不可达状态。
3. 可分解性剪枝：实现论文中的定义 2——当存在异步路径时移除同步边（例如，A ∧ B）（例如，A → B）。
在 nba_output.txt 上的结果
原始：54 个状态，431 个转换
最终：54 个状态，183 个转换
边减少：57.5%
对于这个相对简单的 LTL 公式，57.5% 的减少是预期的。研究论文显示在更大的公式上 >80% 的减少（720 个状态，15984 个转换）。实现已准备好处理此类更大的输入。
使用
# 基本使用
python main.py nba_output.txt
# 带有 DOT 导出用于可视化
python main.py nba_output.txt --export-dot output.dot
# 带有自定义最大并发动作
python main.py nba_output.txt --max-concurrent 2