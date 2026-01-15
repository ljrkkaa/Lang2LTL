# NBA Pruning Implementation Plan - Draft

## 1. Objective
Implement a robust, modular NBA (Nondeterministic Büchi Automaton) pruning tool based on the research patterns in `nba_cut.md`. The goal is to reduce the complexity of the automaton for multi-agent system task planning by removing redundant and infeasible transitions.

## 2. Core Components

### 2.1 NBA Parser (`parser.py`)
- **Input**: Promela "never claim" format (from `nba_output.txt`).
- **Logic**: Extract states, transitions, and guard conditions.
- **Data Structure**: `BuchiAutomaton` class with an adjacency list of `Transition` objects.

### 2.2 Pruning Engine (`pruner.py`)
Implement the three-stage pruning pipeline:
1.  **Infeasibility Pruning**:
    - Filter edges based on agent capabilities.
    - Identify mutual exclusivity (e.g., `wash` and `mow` at the same location).
2.  **Reachability Pruning**:
    - Forward BFS/DFS from initial states.
    - Backward BFS/DFS from accepting states (or sink states for co-safe LTL).
    - Intersection identifies the "live" portion of the graph.
3.  **Decomposability Pruning**:
    - Identify edges $q_i \xrightarrow{A \land B} q_j$ that can be replaced by $q_i \xrightarrow{A} q_k \xrightarrow{B} q_j$.
    - Logic: If $Guard(i \to j) \implies Guard(i \to k) \land Guard(k \to j)$, remove the direct edge.

### 2.3 Configuration Module (`config.py`)
- Support external capability definitions (JSON/YAML).
- Default capability set for UAV, UGV, and Mobile Manipulator.

## 3. Implementation Steps

1.  **Modularization**: Convert the monolithic code in `nba_cut.md` into a structured Python package.
2.  **Robustness**: Improve boolean expression parsing (handle more complex Promela syntax if necessary).
3.  **Verification**: Implement a reporting mechanism to show % reduction in states and edges.
4.  **CLI Interface**: Create `main.py` to orchestrate the process.

## 4. Evaluation
- Test against the provided `nba_output.txt`.
- Target: >80% reduction in edge count as per the research report.
