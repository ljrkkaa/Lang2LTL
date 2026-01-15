# NBA Pruning Implementation Plan

## 1. Overview
This plan outlines the implementation of a professional-grade NBA (Nondeterministic Büchi Automaton) pruning module. It is designed to optimize automata generated from LTL formulas for multi-agent planning by removing infeasible, unreachable, and logically redundant (decomposable) transitions.

## 2. Technical Specifications

### 2.1 Core Modules
1.  **`nba_graph.py`**: Defines `Transition` and `BuchiAutomaton` classes.
    - `Transition`: Stores source, target, guard string, and parsed proposition sets (positive/negative).
    - `BuchiAutomaton`: Adjacency list representation with methods for adding states, transitions, and calculating graph statistics.
2.  **`parser.py`**:
    - Implements a regex-based Promela parser for "never claim" blocks.
    - Extracts `initial_state`, `accepting_states`, and all transitions.
    - Handles basic boolean logic (AND, NOT) in guards.
3.  **`pruner.py`**:
    - **Infeasibility Filter**: Removes edges requiring more resources than available or conflicting actions.
    - **Reachability Filter**: Performs forward and backward traversal to keep only states on a path from `init` to an `accept` state.
    - **Decomposability Filter**: Implements the "Definition 2" logic to replace synchronous edges with asynchronous paths where logically equivalent.
4.  **`main.py`**: CLI interface for the tool.

### 2.2 Data Models
- **Capabilities Config**: A dictionary mapping agents to their task capabilities.
  - Example: `{"uav": ["scan", "surveil"], "ugv": ["mow", "sweep"]}`
- **Conflict Sets**: Pairs of tasks that cannot be performed simultaneously.

## 3. Detailed Work Plan

### Phase 1: Foundation (Parser & Data Structures)
- [ ] Implement `BuchiAutomaton` class with stats reporting.
- [ ] Implement `PromelaParser` to handle `nba_output.txt`.
- [ ] **Verification**: Ensure the parsed graph matches the state/edge counts in the input file log.

### Phase 2: Pruning Algorithms
- [ ] **Task 1: Infeasibility Pruning**. 
  - Define a default resource model (1 UAV, 1 UGV, 1 Manipulator).
  - Implement the `prune_infeasible` function.
- [ ] **Task 2: Reachability Pruning**.
  - Implement forward BFS and backward BFS on transposed graph.
  - Remove "dead" states and their associated edges.
- [ ] **Task 3: Decomposability Pruning**.
  - Implement the triple-nested loop for $q_i \to q_k \to q_j$ detection.
  - Optimize the boolean implication check (`issuperset`).

### Phase 3: Integration & Testing
- [ ] Create a CLI that takes an input file and outputs the pruned graph.
- [ ] Add a "Dry Run" mode to show reduction statistics without writing files.
- [ ] **Final Check**: Run against `nba_output.txt` and verify >80% edge reduction.

## 4. Maintenance & Extensions
- Support for Export to Graphviz (DOT) for visual debugging.
- Integration with `ltl2ba.py` for a single-command LTL-to-Pruned-Graph workflow.
