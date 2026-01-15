"""
nba_graph.py - Core data structures for Büchi Automaton representation.

This module defines the Transition and BuchiAutomaton classes used for
representing and manipulating Nondeterministic Büchi Automata (NBA).
"""

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class Transition:
    """Represents a single transition in the Büchi Automaton.
    
    Attributes:
        source: The source state name.
        target: The target state name.
        guard_str: The original guard condition string from Promela.
        pos_props: Set of positive propositions (must be true).
        neg_props: Set of negative propositions (must be false).
    """
    source: str
    target: str
    guard_str: str
    pos_props: Set[str] = field(default_factory=set)
    neg_props: Set[str] = field(default_factory=set)

    def __repr__(self) -> str:
        return f"{self.source} -> {self.target} [{self.guard_str}]"

    def __hash__(self) -> int:
        return hash((self.source, self.target, self.guard_str))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transition):
            return False
        return (self.source == other.source and 
                self.target == other.target and 
                self.guard_str == other.guard_str)


class BuchiAutomaton:
    """Represents a Nondeterministic Büchi Automaton as an adjacency list.
    
    Attributes:
        states: Set of all state names.
        initial_state: The initial state name (contains 'init').
        accepting_states: Set of accepting state names (contain 'accept').
        transitions: Adjacency list mapping source state to list of Transitions.
        alphabet: Set of all atomic propositions encountered.
    """

    def __init__(self) -> None:
        self.states: Set[str] = set()
        self.initial_state: Optional[str] = None
        self.accepting_states: Set[str] = set()
        self.transitions: Dict[str, List[Transition]] = defaultdict(list)
        self.alphabet: Set[str] = set()

    def add_state(self, state_name: str) -> None:
        """Add a state to the automaton, detecting initial/accepting states."""
        self.states.add(state_name)
        if "init" in state_name.lower():
            self.initial_state = state_name
        if "accept" in state_name.lower():
            self.accepting_states.add(state_name)

    def add_transition(self, source: str, target: str, guard_str: str,
                       pos_props: Set[str], neg_props: Set[str]) -> Transition:
        """Add a transition to the automaton.
        
        Args:
            source: Source state name.
            target: Target state name.
            guard_str: Original guard condition string.
            pos_props: Set of positive propositions.
            neg_props: Set of negative propositions.
            
        Returns:
            The created Transition object.
        """
        self.add_state(source)
        self.add_state(target)

        trans = Transition(
            source=source,
            target=target,
            guard_str=guard_str,
            pos_props=pos_props,
            neg_props=neg_props
        )
        self.transitions[source].append(trans)

        self.alphabet.update(pos_props)
        self.alphabet.update(neg_props)

        return trans

    def remove_transition(self, trans: Transition) -> bool:
        """Remove a transition from the automaton.
        
        Args:
            trans: The transition to remove.
            
        Returns:
            True if the transition was found and removed, False otherwise.
        """
        if trans.source in self.transitions:
            try:
                self.transitions[trans.source].remove(trans)
                return True
            except ValueError:
                return False
        return False

    def remove_state(self, state: str) -> int:
        """Remove a state and all associated transitions.
        
        Args:
            state: The state name to remove.
            
        Returns:
            The number of transitions removed.
        """
        removed_count = 0

        if state in self.transitions:
            removed_count += len(self.transitions[state])
            del self.transitions[state]

        for source in list(self.transitions.keys()):
            original_len = len(self.transitions[source])
            self.transitions[source] = [
                t for t in self.transitions[source] if t.target != state
            ]
            removed_count += original_len - len(self.transitions[source])

        self.states.discard(state)
        self.accepting_states.discard(state)
        if self.initial_state == state:
            self.initial_state = None

        return removed_count

    def get_neighbors(self, state: str) -> List[str]:
        """Get all states reachable from the given state in one step."""
        return [t.target for t in self.transitions.get(state, [])]

    def get_reverse_graph(self) -> Dict[str, List[str]]:
        """Build and return the transposed graph (reversed edges).
        
        Returns:
            A dict mapping each state to its predecessors.
        """
        reverse: Dict[str, List[str]] = defaultdict(list)
        for source, trans_list in self.transitions.items():
            for trans in trans_list:
                reverse[trans.target].append(source)
        return reverse

    def stats(self) -> Tuple[int, int]:
        """Return the number of states and transitions.
        
        Returns:
            A tuple of (state_count, transition_count).
        """
        edge_count = sum(len(ts) for ts in self.transitions.values())
        return len(self.states), edge_count

    def copy(self) -> BuchiAutomaton:
        """Create a deep copy of the automaton."""
        new_ba = BuchiAutomaton()
        new_ba.states = set(self.states)
        new_ba.initial_state = self.initial_state
        new_ba.accepting_states = set(self.accepting_states)
        new_ba.alphabet = set(self.alphabet)

        for source, trans_list in self.transitions.items():
            for t in trans_list:
                new_ba.transitions[source].append(Transition(
                    source=t.source,
                    target=t.target,
                    guard_str=t.guard_str,
                    pos_props=set(t.pos_props),
                    neg_props=set(t.neg_props)
                ))

        return new_ba

    def __repr__(self) -> str:
        s, e = self.stats()
        return f"BuchiAutomaton(states={s}, transitions={e}, init={self.initial_state}, accept={len(self.accepting_states)})"
