import heapq
import copy
import time
from typing import List, Dict, Set, Tuple, Optional

# ==========================================
# 基础数据结构定义
# ==========================================

class Action:
    """
    定义动作的基本属性
    name: 动作名称
    duration: 预计执行耗时 (秒)
    collaborative: 是否为协作任务
    required_agents: 需要的智能体数量 (如果是协作任务)
    """
    def __init__(self, name: str, duration: float, collaborative: bool = False, required_agents: int = 1):
        self.name = name
        self.duration = duration
        self.collaborative = collaborative
        self.required_agents = required_agents

    def __repr__(self):
        return f"{self.name}({self.duration}s)"

class Agent:
    """
    定义智能体
    id: 唯一标识
    capabilities: 该智能体能执行的动作名称集合
    """
    def __init__(self, agent_id: int, capabilities: List[str]):
        self.id = agent_id
        self.capabilities = set(capabilities)
        # schedule 记录: [(start_time, end_time, task_name),...]
        self.schedule: List = []

    def can_perform(self, action: Action) -> bool:
        return action.name in self.capabilities

class Subtask:
    """
    偏序集中的子任务节点
    """
    def __init__(self, task_id: int, action: Action, predecessors: Set[int]):
        self.id = task_id
        self.action = action
        self.predecessors = predecessors  # 前驱任务ID集合 (Precedence Relation <=)
        self.conflicts = set()            # 冲突任务ID集合 (Conflict Relation!=)

    def __repr__(self):
        return f"T{self.id}:{self.action.name}"

class Poset:
    """
    偏序集 (Partially Ordered Set)
    存储任务及其依赖关系图
    """
    def __init__(self, subtasks: Dict):
        self.subtasks = subtasks
        # 构建邻接表: task_id -> list of successor task_ids
        self.adjacency = {tid: [] for tid in subtasks}
        for tid, task in subtasks.items():
            for pid in task.predecessors:
                if pid in self.adjacency:
                    self.adjacency[pid].append(tid)

# ==========================================
# 算法 1: 偏序集生成 (模拟逻辑)
# ==========================================

def compute_poset_from_run(accepting_run: List[Action]) -> Poset:
    """
    对应论文 Algorithm 1: 从自动机的接受路径生成偏序集。
    
    注：真实的LTL规划需要调用形式化方法库来验证语言包含性。
    此处我们模拟该过程：
    1. 初始化为全序序列 (0->1->2...)。
    2. 执行松弛 (Relaxation)：如果相邻任务动作类型完全不同，假设它们可以并行（移除依赖）。
    """
    subtasks = {}
    
    # 第一步：初始化为线性全序依赖
    previous_id = None
    for idx, action in enumerate(accepting_run):
        task_id = idx
        predecessors = set()
        if previous_id is not None:
            predecessors.add(previous_id)
        
        subtasks[task_id] = Subtask(task_id, action, predecessors)
        previous_id = task_id

    # 第二步：松弛 (Relaxation) - 模拟 "Swapping" 检查
    # 论文逻辑：尝试交换相邻任务 w_i, w_{i+1}，如果自动机仍接受，则移除 w_i -> w_{i+1} 的边。
    
    for i in range(len(accepting_run) - 1):
        curr_task = subtasks[i]
        next_task = subtasks[i+1]
        
        # 启发式松弛规则 (模拟)：
        # 如果是不同类型的任务，且不是"Repair"（假设Repair强依赖于前置任务），
        # 则尝试移除直接依赖。
        if curr_task.action.name!= next_task.action.name:
            # 特殊规则演示：假设 Repair 必须在前序任务后执行，不能松弛
            if next_task.action.name == "repair":
                continue
                
            # 否则，解除直接依赖
            if i in next_task.predecessors:
                next_task.predecessors.remove(i)
                # 重要：移除直接依赖后，必须继承前驱的前驱，以防止破坏更早的依赖链
                for grand_parent in curr_task.predecessors:
                    next_task.predecessors.add(grand_parent)

    return Poset(subtasks)

# ==========================================
# 算法 2 & 3: 分支定界 (Branch and Bound)
# ==========================================

class BnBNode:
    """
    搜索树节点，代表一个部分指派
    """
    def __init__(self, assigned_tasks: Set[int], agent_free_times: Dict[int, float], cost: float):
        self.assigned_tasks = assigned_tasks  # 已分配的任务ID集合
        self.agent_free_times = agent_free_times  # 每个智能体何时空闲
        self.cost = cost  # 当前 Makespan (max(agent_free_times))
        self.assignment_history = []  # 用于回溯路径: [(task_id, agent_id),...]

    def __lt__(self, other):
        # 优先队列比较器：Lower Bound 越小越优先 (A* 策略)
        return self.cost < other.cost

def calculate_lower_bound(node: BnBNode, poset: Poset, agents: List[Agent]) -> float:
    """
    下界计算 (Lower Bound Estimation) - 对应论文 Section V-C
    结合两种松弛策略：
    1. 关键路径 (Critical Path): 忽略智能体数量限制，只看任务依赖链长度。
    2. 负载均衡 (Load Balancing): 忽略依赖，看总工作量平均值。
    """
    remaining_tasks = [t for tid, t in poset.subtasks.items() if tid not in node.assigned_tasks]
    
    if not remaining_tasks:
        return node.cost

    # 策略 1: 关键路径松弛
    memo = {}
    def get_longest_chain(tid):
        if tid in memo: return memo[tid]
        duration = poset.subtasks[tid].action.duration
        
        # 寻找未分配的后继
        successors = [nxt for nxt in poset.adjacency.get(tid, []) if nxt not in node.assigned_tasks]
        
        max_succ_len = 0
        for succ in successors:
            max_succ_len = max(max_succ_len, get_longest_chain(succ))
            
        memo[tid] = duration + max_succ_len
        return memo[tid]

    critical_path_len = 0
    for t in remaining_tasks:
        # 对所有剩余任务求最长链
        critical_path_len = max(critical_path_len, get_longest_chain(t.id))
    
    lb_critical_path = critical_path_len # 实际上应加上当前最早可用时间，这里做相对估算

    # 策略 2: 负载均衡松弛
    total_remaining_work = sum(t.action.duration for t in remaining_tasks)
    avg_load = total_remaining_work / len(agents)
    
    min_current_free = min(node.agent_free_times.values())
    lb_load_balancing = min_current_free + avg_load

    # 最终下界：两者取大
    estimated_finish = max(min_current_free + critical_path_len, lb_load_balancing)
    return max(node.cost, estimated_finish)

def calculate_upper_bound(node: BnBNode, poset: Poset, agents: List[Agent]) -> Tuple[float, List]:
    """
    算法 2: 贪婪上界 (Greedy Upper Bound)
    快速将剩余任务分配给最早空闲的智能体，得到一个可行解的 Makespan。
    返回: (makespan, assignment_history)
    """
    sim_assigned = copy.deepcopy(node.assigned_tasks)
    sim_times = copy.deepcopy(node.agent_free_times)
    current_makespan = node.cost
    assignment_history = list(node.assignment_history)  # Copy existing history
    
    # 简单的拓扑排序循环
    while len(sim_assigned) < len(poset.subtasks):
        # 找就绪任务
        ready_tasks = []
        for tid, task in poset.subtasks.items():
            if tid not in sim_assigned and task.predecessors.issubset(sim_assigned):
                ready_tasks.append(task)
        
        if not ready_tasks:
            break # 出现死锁或逻辑错误
            
        # 贪婪策略：取第一个就绪任务
        task = ready_tasks[0]
        
        # 找完成时间最早的智能体
        best_agent_id = None
        min_finish_time = float('inf')
        
        for agent in agents:
            if agent.can_perform(task.action):
                start_t = sim_times[agent.id]
                finish_t = start_t + task.action.duration
                if finish_t < min_finish_time:
                    min_finish_time = finish_t
                    best_agent_id = agent.id
        
        if best_agent_id is not None:
            sim_times[best_agent_id] = min_finish_time
            sim_assigned.add(task.id)
            current_makespan = max(current_makespan, min_finish_time)
            assignment_history.append((task.id, best_agent_id))
        else:
            return float('inf'), [] # 无可行解
            
    return current_makespan, assignment_history

def bnb_solve(poset: Poset, agents: List[Agent], time_budget: float) -> Tuple[float, List, int]:
    """
    算法 3: Anytime Branch and Bound 主循环
    """
    start_time = time.time()
    
    # 根节点：无任务分配，所有智能体在时刻0空闲
    root = BnBNode(set(), {a.id: 0.0 for a in agents}, 0.0)
    
    # 优先队列: 存储 (LowerBound, Node)
    pq = [(0.0, root)]
    
    best_solution_cost = float('inf')
    best_solution_history = []
    nodes_expanded = 0
    
    print(f"开始 BnB 搜索，时间预算: {time_budget}s...")
    
    while pq and (time.time() - start_time) < time_budget:
        lb, current_node = heapq.heappop(pq)
        nodes_expanded += 1
        
        # 剪枝
        if lb >= best_solution_cost:
            continue
            
        # 如果是叶子节点 (所有任务已分配)
        if len(current_node.assigned_tasks) == len(poset.subtasks):
            if current_node.cost < best_solution_cost:
                best_solution_cost = current_node.cost
                best_solution_history = current_node.assignment_history
                print(f"  [Update] 找到更优解: {best_solution_cost}s (Expanded: {nodes_expanded})")
            continue
            
        # 计算上界
        ub, ub_history = calculate_upper_bound(current_node, poset, agents)
        if ub < best_solution_cost:
            best_solution_cost = ub
            best_solution_history = ub_history
            print(f"  [Heuristic] 贪婪发现潜在解: {best_solution_cost}s")
            
        # 分支扩展 (Branching)
        # 1. 找出所有"就绪"任务
        ready_tasks = []
        for tid, task in poset.subtasks.items():
            if tid not in current_node.assigned_tasks:
                if task.predecessors.issubset(current_node.assigned_tasks):
                    ready_tasks.append(task)
        
        if not ready_tasks: continue
        
        # 策略：为了避免重复，我们只扩展第一个就绪任务
        next_task = ready_tasks[0]
        
        # 2. 尝试分配给每一个能干活的智能体
        candidate_agents = [a for a in agents if a.can_perform(next_task.action)]
        
        for agent in candidate_agents:
            # 创建子节点
            new_assigned = current_node.assigned_tasks.copy()
            new_assigned.add(next_task.id)
            
            new_free_times = current_node.agent_free_times.copy()
            
            # 简化版：Start = agent_free_time
            start_t = new_free_times[agent.id]
            finish_t = start_t + next_task.action.duration
            
            new_free_times[agent.id] = finish_t
            new_cost = max(current_node.cost, finish_t)
            
            child_node = BnBNode(new_assigned, new_free_times, new_cost)
            child_node.assignment_history = current_node.assignment_history + [(next_task.id, agent.id)]
            
            # 计算子节点下界
            child_lb = calculate_lower_bound(child_node, poset, agents)
            
            if child_lb < best_solution_cost:
                heapq.heappush(pq, (child_lb, child_node))

    return best_solution_cost, best_solution_history, nodes_expanded

# ==========================================
# 模拟运行
# ==========================================

if __name__ == "__main__":
    # 1. 定义异构智能体
    # UAVs: 速度快，能扫描 (scan)
    agents = [
        Agent(1, ["scan", "inspect"]), 
        Agent(2, ["scan", "inspect"]),
        # UGVs: 能维修 (repair), 割草 (mow)
        Agent(3, ["mow", "repair"]),
        Agent(4, ["mow", "repair"])
    ]
    
    # 2. 定义来自自动机的一条路径 (模拟)
    # 逻辑：先扫描区域A，再割草A，然后维修B
    actions = [
        Action("scan", 5.0),
        Action("mow", 10.0),
        Action("repair", 8.0)
    ]
    
    print(f"任务序列长度: {len(actions)}")
    
    # 3. 生成偏序集 (模拟松弛)
    poset = compute_poset_from_run(actions)
    print("生成的偏序依赖关系:")
    for tid, t in poset.subtasks.items():
        print(f"  {t} -> Predecessors: {t.predecessors}")
        
    # 4. 执行 BnB 规划
    cost, history, nodes = bnb_solve(poset, agents, time_budget=5.0)
    
    print("\n" + "="*30)
    print(f"最优 Makespan: {cost} 秒")
    print(f"扩展节点数: {nodes}")
    print("指派方案:")
    for tid, aid in history:
        task_name = poset.subtasks[tid].action.name
        print(f"  任务 {tid} [{task_name}] -> 智能体 {aid}")