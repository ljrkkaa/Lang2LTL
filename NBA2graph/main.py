#!/usr/bin/env python3
"""
main.py - CLI interface for NBA pruning tool.

Usage:
    python main.py [input_file] [--max-concurrent N] [--export-dot FILE]
"""

from __future__ import annotations
import argparse
import sys

from parser import parse_nba_file
from pruner import run_pruning_pipeline, DEFAULT_CAPABILITIES, DEFAULT_CONFLICTS
from nba_graph import BuchiAutomaton


def export_to_dot(ba: BuchiAutomaton, filepath: str) -> None:
    """Export the automaton to Graphviz DOT format."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("digraph NBA {\n")
        f.write("  rankdir=LR;\n")
        f.write("  node [shape=circle];\n")

        for state in ba.accepting_states:
            f.write(f'  "{state}" [shape=doublecircle];\n')

        if ba.initial_state:
            f.write(f'  __start__ [shape=point];\n')
            f.write(f'  __start__ -> "{ba.initial_state}";\n')

        for source, trans_list in ba.transitions.items():
            for trans in trans_list:
                label = trans.guard_str.replace('"', '\\"')
                f.write(f'  "{source}" -> "{trans.target}" [label="{label}"];\n')

        f.write("}\n")


def main() -> int:
    arg_parser = argparse.ArgumentParser(
        description="Prune a Büchi Automaton from Promela never claim format."
    )
    arg_parser.add_argument(
        "input_file",
        nargs="?",
        default="nba_output.txt",
        help="Input file in Promela never claim format (default: nba_output.txt)"
    )
    arg_parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Maximum concurrent actions for infeasibility check (default: 3)"
    )
    arg_parser.add_argument(
        "--export-dot",
        metavar="FILE",
        help="Export pruned automaton to Graphviz DOT format"
    )
    arg_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose output"
    )

    args = arg_parser.parse_args()

    try:
        ba = parse_nba_file(args.input_file)
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found.", file=sys.stderr)
        return 1

    stats = run_pruning_pipeline(ba, verbose=not args.quiet)

    if args.export_dot:
        export_to_dot(ba, args.export_dot)
        if not args.quiet:
            print(f"Exported to: {args.export_dot}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
