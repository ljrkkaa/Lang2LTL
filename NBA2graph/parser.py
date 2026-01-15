"""
parser.py - Promela "never claim" parser for Büchi Automata.
"""

from __future__ import annotations
import re
from typing import Set, Tuple

from nba_graph import BuchiAutomaton


STATE_PATTERN = re.compile(r'^(\w+):$')
TRANSITION_PATTERN = re.compile(r'::\s*\((.+?)\)\s*->\s*goto\s+(\w+)')
SKIP_PATTERN = re.compile(r'::\s*skip')


def parse_guard(guard_str: str) -> Tuple[Set[str], Set[str]]:
    """Parse a Promela guard condition into positive and negative propositions.
    
    Args:
        guard_str: A boolean expression like "(!washp21 && mowp21)".
        
    Returns:
        A tuple of (positive_props, negative_props).
    """
    clean = guard_str.replace('(', '').replace(')', '').strip()
    
    if clean == '1' or clean.lower() == 'true':
        return set(), set()

    parts = [p.strip() for p in clean.split('&&')]
    pos_props: Set[str] = set()
    neg_props: Set[str] = set()

    for part in parts:
        if not part:
            continue
        if part.startswith('!'):
            neg_props.add(part[1:].strip())
        else:
            pos_props.add(part.strip())

    return pos_props, neg_props


def parse_nba_file(filepath: str) -> BuchiAutomaton:
    """Parse a Promela never claim file into a BuchiAutomaton.
    
    Args:
        filepath: Path to the nba_output.txt file.
        
    Returns:
        A populated BuchiAutomaton instance.
    """
    ba = BuchiAutomaton()
    current_state: str | None = None

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    is_parsing = False
    for line in lines:
        line = line.strip()

        if line.startswith('never {'):
            is_parsing = True
            continue
        if not is_parsing:
            continue
        if line == '}':
            break

        state_match = STATE_PATTERN.match(line)
        if state_match:
            current_state = state_match.group(1)
            ba.add_state(current_state)
            continue

        if current_state is None:
            continue

        if SKIP_PATTERN.match(line):
            ba.add_state(current_state)
            continue

        trans_match = TRANSITION_PATTERN.match(line)
        if trans_match:
            guard = trans_match.group(1)
            target = trans_match.group(2)
            pos_props, neg_props = parse_guard(guard)
            ba.add_transition(current_state, target, guard, pos_props, neg_props)

    return ba


if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "nba_output.txt"
    automaton = parse_nba_file(input_file)
    states, edges = automaton.stats()
    print(f"Parsed: {states} states, {edges} transitions")
    print(f"Initial: {automaton.initial_state}")
    print(f"Accepting: {automaton.accepting_states}")
