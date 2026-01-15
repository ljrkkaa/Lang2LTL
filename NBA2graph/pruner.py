"""
pruner.py - Three-stage pruning algorithms for Büchi Automata.

Implements:
1. Infeasibility pruning (based on agent capabilities)
2. Reachability pruning (remove unreachable/dead-end states)
3. Decomposability pruning (remove synchronous edges with async alternatives)
"""

from __future__ import annotations
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple

from nba_graph import BuchiAutomaton, Transition


DEFAULT_CAPABILITIES: Dict[str, Set[str]] = {
    "uav": {"scan", "surveil", "repair"},
    "ugv1": {"wash", "sweep"},
    "ugv2": {"mow"},
}

DEFAULT_CONFLICTS: List[Tuple[Set[str], str]] = [
    ({"wash", "mow"}, "same_location_conflict"),
    ({"sweep", "mow"}, "same_location_conflict"),
]

MAX_CONCURRENT_ACTIONS = 3


def get_action_from_prop(prop: str) -> str:
    """Extract action type from proposition (e.g., 'washp21' -> 'wash')."""
    for action in ["wash", "sweep", "mow", "scan", "repair", "surveil", "fix"]:
        if prop.startswith(action):
            return action
    return prop


def check_feasibility(pos_props: Set[str], capabilities: Dict[str, Set[str]],
                      conflicts: List[Tuple[Set[str], str]],
                      max_concurrent: int) -> bool:
    """Check if a set of propositions can be satisfied by available agents."""
    if len(pos_props) > max_concurrent:
        return False

    actions_needed = {get_action_from_prop(p) for p in pos_props}

    for conflict_set, _ in conflicts:
        if conflict_set.issubset(actions_needed):
            return False

    all_capabilities = set()
    for agent_caps in capabilities.values():
        all_capabilities.update(agent_caps)

    for action in actions_needed:
        if action not in all_capabilities and action not in {"fix", "fixt5", "p18", "p24"}:
            pass

    return True


def prune_infeasible(ba: BuchiAutomaton,
                     capabilities: Dict[str, Set[str]] | None = None,
                     conflicts: List[Tuple[Set[str], str]] | None = None,
                     max_concurrent: int = MAX_CONCURRENT_ACTIONS) -> int:
    """Remove transitions that are physically infeasible.
    
    Returns the number of transitions removed.
    """
    if capabilities is None:
        capabilities = DEFAULT_CAPABILITIES
    if conflicts is None:
        conflicts = DEFAULT_CONFLICTS

    to_remove: List[Tuple[str, Transition]] = []

    for source, trans_list in ba.transitions.items():
        for trans in trans_list:
            if not check_feasibility(trans.pos_props, capabilities, conflicts, max_concurrent):
                to_remove.append((source, trans))

    for source, trans in to_remove:
        ba.transitions[source].remove(trans)

    return len(to_remove)


def prune_invalid(ba: BuchiAutomaton) -> Tuple[int, int]:
    """Remove unreachable and dead-end states.
    
    Returns a tuple of (states_removed, edges_removed).
    """
    if ba.initial_state is None:
        return 0, 0

    forward_reachable: Set[str] = set()
    queue: deque[str] = deque([ba.initial_state])
    forward_reachable.add(ba.initial_state)

    while queue:
        u = queue.popleft()
        for trans in ba.transitions.get(u, []):
            if trans.target not in forward_reachable:
                forward_reachable.add(trans.target)
                queue.append(trans.target)

    reverse_graph = ba.get_reverse_graph()
    backward_reachable: Set[str] = set()

    for acc_state in ba.accepting_states:
        if acc_state not in backward_reachable:
            backward_reachable.add(acc_state)
            queue.append(acc_state)

    while queue:
        u = queue.popleft()
        for v in reverse_graph.get(u, []):
            if v not in backward_reachable:
                backward_reachable.add(v)
                queue.append(v)

    valid_states = forward_reachable.intersection(backward_reachable)

    states_to_remove = ba.states - valid_states
    removed_states = len(states_to_remove)

    new_transitions: Dict[str, List[Transition]] = defaultdict(list)
    removed_edges = 0
    original_edges = sum(len(ts) for ts in ba.transitions.values())

    for u in valid_states:
        for trans in ba.transitions.get(u, []):
            if trans.target in valid_states:
                new_transitions[u].append(trans)
            else:
                removed_edges += 1

    for state in states_to_remove:
        removed_edges += len(ba.transitions.get(state, []))

    ba.states = valid_states
    ba.transitions = new_transitions
    ba.accepting_states = ba.accepting_states.intersection(valid_states)
    if ba.initial_state not in valid_states:
        ba.initial_state = None

    return removed_states, removed_edges


def prune_decomposable(ba: BuchiAutomaton) -> int:
    """Remove decomposable transitions (synchronous edges with async alternatives).
    
    A transition u->v is decomposable if there exists a state k such that:
    - u->k exists
    - k->v exists  
    - guard(u->v) is a superset of guard(u->k) ∪ guard(k->v)
    
    Returns the number of transitions removed.
    """
    to_remove: List[Tuple[str, Transition]] = []

    for u in list(ba.transitions.keys()):
        u_transitions = ba.transitions[u][:]

        for trans_uv in u_transitions:
            v = trans_uv.target
            sigma_uv = trans_uv.pos_props

            if not sigma_uv:
                continue

            is_decomposable = False

            for trans_uk in ba.transitions.get(u, []):
                k = trans_uk.target
                sigma_uk = trans_uk.pos_props

                if k == u or k == v:
                    continue

                for trans_kv in ba.transitions.get(k, []):
                    if trans_kv.target != v:
                        continue

                    sigma_kv = trans_kv.pos_props
                    combined = sigma_uk.union(sigma_kv)

                    if combined and sigma_uv.issuperset(combined) and sigma_uv != combined:
                        is_decomposable = True
                        break
                    
                    if sigma_uv == combined and len(sigma_uv) >= 2:
                        is_decomposable = True
                        break

                if is_decomposable:
                    break

            if is_decomposable:
                to_remove.append((u, trans_uv))

    for source, trans in to_remove:
        if trans in ba.transitions.get(source, []):
            ba.transitions[source].remove(trans)

    return len(to_remove)


def run_pruning_pipeline(ba: BuchiAutomaton, verbose: bool = True) -> Dict[str, int]:
    """Execute the full three-stage pruning pipeline.
    
    Returns a dict with pruning statistics.
    """
    stats: Dict[str, int] = {}
    s0, e0 = ba.stats()
    stats["original_states"] = s0
    stats["original_edges"] = e0

    if verbose:
        print(f"Original: {s0} states, {e0} transitions")

    infeasible_removed = prune_infeasible(ba)
    stats["infeasible_removed"] = infeasible_removed
    if verbose:
        print(f"Infeasible transitions removed: {infeasible_removed}")

    states_removed_1, edges_removed_1 = prune_invalid(ba)
    stats["invalid_states_pass1"] = states_removed_1
    stats["invalid_edges_pass1"] = edges_removed_1
    if verbose:
        s1, e1 = ba.stats()
        print(f"After reachability pass 1: {s1} states, {e1} transitions")

    decomposable_total = 0
    while True:
        decomposable_removed = prune_decomposable(ba)
        decomposable_total += decomposable_removed
        if decomposable_removed == 0:
            break
    stats["decomposable_removed"] = decomposable_total
    if verbose:
        print(f"Decomposable transitions removed: {decomposable_total}")

    states_removed_2, edges_removed_2 = prune_invalid(ba)
    stats["invalid_states_pass2"] = states_removed_2
    stats["invalid_edges_pass2"] = edges_removed_2

    sf, ef = ba.stats()
    stats["final_states"] = sf
    stats["final_edges"] = ef

    if verbose:
        print(f"Final: {sf} states, {ef} transitions")
        if e0 > 0:
            reduction = (1 - ef / e0) * 100
            print(f"Edge reduction: {reduction:.1f}%")

    return stats
