#!/usr/bin/env python3
"""The repository's own check, with no network and no key (Python's standard library only):

1. every test folder holds its README, its run.py and its results (RESULT.md, result.json);
2. every pinned file in the tests' lists names a sha256 of 64 hex digits;
3. every relative link in a Markdown file leads to a file or folder that exists;
4. every number the README cites still stands in its run record (the claims below, as REPRODUCE.md lists them);
5. every run record has its run.json and its requests (plain or gzipped), and no file is over 95 MB;
6. meridian_binary.py packs and unpacks a request unchanged, and refuses a malformed body.

    python3 ci/check_repo.py          exit 0: all hold · 1: something does not (each named)
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
faults = []

# 1 · the test folders
tests = sorted(d for d in glob.glob("tests/*-*") if os.path.isdir(d))
if len(tests) != 8:
    faults.append(f"expected 8 test folders, found {len(tests)}")
for t in tests:
    for need in ("README.md", "run.py", "results/RESULT.md", "results/result.json"):
        if not os.path.exists(os.path.join(t, need)):
            faults.append(f"{t}: {need} is missing")

# 2 · the pins
HEX = re.compile(r"^[0-9a-f]{64}$")


def pins(obj, where):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "sha256" and isinstance(v, str) and not HEX.match(v):
                faults.append(f"{where}: sha256 {v!r} is not 64 hex digits")
            pins(v, where)
    elif isinstance(obj, list):
        for v in obj:
            pins(v, where)


for p in glob.glob("tests/*/*.json"):
    try:
        pins(json.load(open(p)), p)
    except ValueError as e:
        faults.append(f"{p}: not JSON ({e})")

# 3 · the links
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
for md in glob.glob("*.md") + glob.glob("tests/*/*.md") + glob.glob("tests/*/results/*.md"):
    for target in LINK.findall(open(md, encoding="utf-8").read()):
        if re.match(r"^[a-z]+:", target):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(md), target))):
            faults.append(f"{md}: the link {target} leads nowhere")

# 4 · the README's numbers in their run records
CLAIMS = [
    ("runs/2026-11-09T23-59-37+0100-typed-decisions/result.json", "all.kelvin.accuracy", 0.706, 0.0005),
    ("runs/2026-11-09T23-59-37+0100-typed-decisions/result.json", "all.kelvin.kl_from_gold", 0.162, 0.0005),
    ("runs/2026-11-09T23-59-37+0100-typed-decisions/result.json", "all.kelvin.brier", 0.089, 0.0005),
    ("runs/2026-11-09T23-59-37+0100-typed-decisions/result.json", "all.kelvin.ece", 0.131, 0.0005),
    ("runs/2026-11-09T23-59-37+0100-typed-decisions/result.json", "all.control_shuffled.accuracy", 0.508, 0.0006),
    ("runs/2026-11-10T18-23-27+0100-pictures/result.json", "kelvin.again.as_told", 24, 0),
    ("runs/2026-11-10T18-23-27+0100-pictures/result.json", "kelvin.unseen.right", 50, 0),
    ("runs/2026-11-10T18-23-27+0100-pictures/result.json", "control_swapped.again.right", 0, 0),
    ("runs/2026-11-10T18-23-27+0100-pictures/result.json", "control_swapped.unseen.right", 10, 0),
    ("runs/2026-11-10T07-00-50+0100-sound-object-name/result.json", "real names.claims.name to clip by picture", 23, 0),
    ("runs/2026-11-10T07-00-50+0100-sound-object-name/result.json", "real names.claims.sound to name", 14, 0),
    ("runs/2026-11-10T07-00-50+0100-sound-object-name/result.json", "real names.claims.never-lived name answered", 0, 0),
    ("runs/2026-11-10T07-00-50+0100-sound-object-name/result.json", "made-up answered like real.equal", 216, 0),
    ("runs/2026-11-10T10-09-24+0100-intent/result.json", "kelvin.in_scope_right", 3821, 0),
    ("runs/2026-11-10T10-09-24+0100-intent/result.json", "kelvin.none_right", 337, 0),
    ("runs/2026-11-10T10-09-24+0100-intent/result.json", "control_shuffled.in_scope_right", 19, 0),
    ("runs/2026-11-10T00-03-02+0100-when-to-call-a-tool/result.json", "kelvin.right", 816, 0),
    ("runs/2026-11-10T00-03-02+0100-when-to-call-a-tool/result.json", "control_shuffled.right", 430, 0),
    ("runs/2026-11-10T17-19-53+0100-remember/result.json", "right", 345, 0),
    ("runs/2026-11-10T17-19-53+0100-remember/result.json", "never_told_silent", 332, 0),
    ("runs/2026-11-10T17-19-53+0100-remember/result.json", "control_right_against_the_truth", 4, 0),
    ("runs/2026-11-09T23-50-07+0100-i-dont-know/result.json", "right_overall", 558, 0),
    ("runs/2026-11-09T23-50-07+0100-i-dont-know/result.json", "not_known_none_of_the_above", 389, 0),
    ("runs/2026-11-09T23-50-07+0100-i-dont-know/result.json", "control_nothing_told.told.right", 0, 0),
    ("runs/2026-11-11T15-05-09+0100-reversal/result.json", "forward.right", 50, 0),
    ("runs/2026-11-11T15-05-09+0100-reversal/result.json", "reverse.right", 50, 0),
    ("runs/2026-11-11T15-05-09+0100-reversal/result.json", "reverse.several_children_all_held", 10, 0),
    ("runs/2026-11-11T15-05-09+0100-reversal/result.json", "no_ones_parent.silent", 50, 0),
    ("runs/2026-11-11T15-05-09+0100-reversal/result.json", "control.swapped_relation_gave_the_same_children", 0, 0),
]
for path, field, want, tol in CLAIMS:
    try:
        v = json.load(open(path))
        for k in field.split("."):
            v = v[k]
        if abs(v - want) > tol:
            faults.append(f"{path} · {field} = {v}, but the README cites {want}")
    except (OSError, KeyError, ValueError, TypeError) as e:
        faults.append(f"{path} · {field}: cannot be read ({type(e).__name__})")

# 5 · the run records and sizes
for d in sorted(glob.glob("runs/*/")):
    if not os.path.exists(os.path.join(d, "run.json")):
        faults.append(f"{d}: run.json is missing")
    if not (os.path.exists(os.path.join(d, "requests.jsonl")) or os.path.exists(os.path.join(d, "requests.jsonl.gz"))):
        faults.append(f"{d}: its requests are missing")
for root, dirs, names in os.walk("."):
    dirs[:] = [x for x in dirs if x not in (".git", "data", "runs-local", "matrix", "internal")]
    for n in names:
        p = os.path.join(root, n)
        if os.path.getsize(p) > 95 * 1024 * 1024:
            faults.append(f"{p}: over 95 MB")

# 6 · Meridian Binary 1: the tool round-trips, and refuses what the door refuses
sys.path.insert(0, ROOT)
import base64 as _b64  # noqa: E402
import meridian_binary as _mb  # noqa: E402
_req = {"model": "kelvin", "state": {"picture": "x"}, "questions": {"q": {"type": "choice", "criteria": {"a": None}}},
        "assets": {"x": {"type": "image", "format": "jpg", "data_base64": _b64.b64encode(bytes(range(256)) * 20).decode()},
                   "y": {"type": "image", "format": "png", "data_base64": _b64.b64encode(b"\x89PNG").decode()}}}
_body = _mb.pack(_req)
if _body[:4] != b"MB1\n" or _mb.unpack(_body) != _req:
    faults.append("meridian_binary: unpack(pack(request)) is not the request")
for _bad in (b"MB1\n\0\0", b"MB1\n" + (99).to_bytes(4, "big") + b"{}", b"MB1\n" + (3).to_bytes(4, "big") + b"xyz"):
    try:
        _mb.unpack(_bad)
        faults.append(f"meridian_binary: a malformed body was accepted: {_bad[:12]!r}")
    except ValueError:
        pass

if faults:
    print("check_repo: NOT all hold")
    for f in faults:
        print("  -", f)
    sys.exit(1)
print(f"check_repo: all hold · {len(tests)} tests · {len(CLAIMS)} cited numbers found in their run records")
