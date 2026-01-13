#!/usr/bin/env python3
"""加载 pickle，格式化并把第一条写入输出文件。"""

import argparse
import os
import pickle
import pprint
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Dump first item from a pickle to a text file"
    )
    parser.add_argument("pickle_path", help="path to pickle file")
    parser.add_argument("out_path", help="output text file path")
    args = parser.parse_args()

    if not os.path.exists(args.pickle_path):
        print(f"ERROR: pickle not found: {args.pickle_path}")
        sys.exit(2)

    with open(args.pickle_path, "rb") as f:
        data = pickle.load(f)

    # Determine first item
    first = None
    if isinstance(data, (list, tuple)) and len(data) > 0:
        first = data[0]
    elif isinstance(data, dict):
        # take first key's value
        keys = list(data.keys())
        if keys:
            first = (keys[0], data[keys[0]])
    else:
        first = data

    os.makedirs(os.path.dirname(args.out_path) or ".", exist_ok=True)
    with open(args.out_path, "w", encoding="utf-8") as out:
        out.write("--- FIRST ITEM ---\n")
        out.write(f"type: {type(first)}\n\n")
        try:
            out.write(pprint.pformat(first, width=120))
        except Exception:
            out.write(repr(first))

    print(f"Wrote first item to: {args.out_path}")


if __name__ == "__main__":
    main()
