#!/usr/bin/env python3
"""Print every memory the tests use, one a line, as the first column of a keys file (name<TAB>key).

    python3 tests/keys_needed.py > ~/meridian-keys.tsv && chmod 600 ~/meridian-keys.tsv   # then add each key after a tab

The names are read from each test's run.py (its MEMORIES list), without running it.
"""
import ast
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def memories(path):
    tree = ast.parse(open(path).read())
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            try:
                consts[name] = ast.literal_eval(node.value)
            except ValueError:
                if name == "MEMORIES":  # a list built from another constant, e.g. one memory per area
                    return eval(compile(ast.Expression(node.value), path, "eval"), {}, dict(consts))
    return consts.get("MEMORIES", [])


for t in sorted(os.listdir(HERE)):
    run = os.path.join(HERE, t, "run.py")
    if os.path.isfile(run):
        print(f"# {t}")
        for name in memories(run):
            print(f"{name}\t")
