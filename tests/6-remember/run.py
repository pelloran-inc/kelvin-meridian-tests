#!/usr/bin/env python3
"""Test 6 · Remember what you were told.

    python3 tests/6-remember/run.py

KELVIN is told 346 real facts (a person's mother or father, from Wikidata), 50 to a request. Later, in new requests that
do not carry them, it is asked each person's parent, with ten names to choose from. Also asked:
- the same questions twice: the answers must be the same, byte for byte;
- people who appear only as a parent, never as someone's child: KELVIN was never told their parents, so it must stay
  silent;
- the same questions in another memory where nothing was told: silent.

The control, in its own memory: the same facts with the parents shuffled among the people. KELVIN must then follow what
it was told, so against the truth it must be right far less often: right where the control is wrong more often than the
other way round (paired, one-sided sign test p < 0.05), or the run does not count.

Needs: MERIDIAN_URL and MERIDIAN_KEYS_FILE with the three memories below.
"""
import collections
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common  # noqa: E402

MEMORIES = ["remember", "remember-shuffled", "remember-other"]
SEED = 0x2002A4
K = 10  # names to choose from


def facts_of(path):
    out = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        rel, _c, _p, child, parent = line.rstrip("\n").split("\t")
        out.append((rel, child, parent))
    return out


def tell(m, memory, facts):
    for i in range(0, len(facts), 50):
        chunk = facts[i:i + 50]
        rel, child, parent = chunk[0]
        state = {"facts": [{"subject": c, "relation": r, "object": p} for r, c, p in chunk]}
        q = {rel: {"type": "choice", "criteria": {parent: None, "nobody": None}}}
        s, a, raw, ms, _ = m.ask({"model": "kelvin", "state": state, "questions": q}, memory=memory)
        if s != 200:
            common.stop(f"{memory}: telling facts {i}–{i + len(chunk)} answered {s}: {raw[:300]!r}")


def ask(m, memory, items):
    out = []
    for rel, subject, opts in items:
        q = {"type": "choice", "instructions": f"Who is the {rel} of the subject?", "criteria": {o: None for o in opts}}
        s, a, raw, ms, _ = m.ask({"model": "kelvin", "state": {"subject": subject}, "questions": {rel: q}}, memory=memory)
        if s != 200:
            common.stop(f"{memory}: asking the {rel} of {subject} answered {s}: {raw[:300]!r}")
        ans = (a.get("answers") or {}).get(rel) or {}
        out.append({"rel": rel, "subject": subject, "silent": bool(ans.get("silent")),
                    "choice": None if ans.get("silent") else ans.get("choice"), "raw": raw.decode("utf-8", "replace"), "ms": ms})
    return out


def main():
    rng = random.Random(SEED)
    facts = facts_of(os.path.join(HERE, "parents.tsv"))
    rng.shuffle(facts)
    truth = collections.defaultdict(set)
    for r, c, p in facts:
        truth[(r, c)].add(p)
    parents = {r: sorted({p for rr, _, p in facts if rr == r}) for r in ("mother", "father")}
    everyone = sorted({p for _, _, p in facts} | {c for _, c, _ in facts})

    def options(rel, true, extra=()):
        pool = [p for p in (parents[rel] if len(parents[rel]) >= K + 2 else everyone) if p not in true and p not in extra]
        o = list(true) + list(extra) + rng.sample(pool, K - len(true) - len(extra))
        rng.shuffle(o)
        return o

    keys = sorted(truth)
    asked = [(r, c, options(r, sorted(truth[(r, c)]))) for r, c in keys]
    children = set(keys)
    never = [(r, p) for r in ("mother", "father") for p in parents[r] if (r, p) not in children]
    never_items = [(r, p, options(r, [])) for r, p in never]
    shuffled = []
    for rel in ("mother", "father"):
        fs = [f for f in facts if f[0] == rel]
        objs = [p for _, _, p in fs]
        rng.shuffle(objs)
        shuffled += [(rel, c, o) for (_, c, _), o in zip(fs, objs)]
    sh_truth = collections.defaultdict(set)
    for r, c, p in shuffled:
        sh_truth[(r, c)].add(p)
    c1_items = [(r, c, options(r, sorted(truth[(r, c)]), sorted(sh_truth[(r, c)] - truth[(r, c)]))) for r, c in keys]

    m = common.Meridian("remember")
    print(f"Test 6 · remember what you were told · {m.url} · run record {m.dir}", flush=True)
    print(f"  telling {len(facts)} facts, then asking {len(asked)} questions (twice), {len(never_items)} never told, "
          f"and the control", flush=True)
    r0, c0, o0 = asked[0]
    probe = {"model": "kelvin", "state": {"subject": c0},
             "questions": {r0: {"type": "choice", "instructions": f"Who is the {r0} of the subject?", "criteria": {o: None for o in o0}}}}
    for memory in MEMORIES:
        common.require_new(m, memory, probe)
    tell(m, "remember", facts)
    first = ask(m, "remember", asked)
    second = ask(m, "remember", asked)
    never_ans = ask(m, "remember", never_items)
    other = ask(m, "remember-other", asked)
    tell(m, "remember-shuffled", shuffled)
    control = ask(m, "remember-shuffled", c1_items)

    right = [a["choice"] in truth[(r, c)] for a, (r, c, _) in zip(first, asked)]
    c_right = [a["choice"] in truth[(r, c)] for a, (r, c, _) in zip(control, c1_items)]
    c_follows = sum(a["choice"] in sh_truth[(r, c)] for a, (r, c, _) in zip(control, c1_items))
    ok, g, l, p = common.control_breaks(right, c_right)
    ms = sorted(a["ms"] for a in first)
    result = {"test": "remember what you were told", "facts_told": len(facts), "asked": len(asked),
              "right": sum(right), "silent": sum(a["silent"] for a in first),
              "asked_twice_identical": sum(a["raw"] == b["raw"] for a, b in zip(first, second)),
              "never_told": len(never_items), "never_told_silent": sum(a["silent"] for a in never_ans),
              "never_told_answered": sum(not a["silent"] for a in never_ans),
              "another_memory_silent": sum(a["silent"] for a in other),
              "control_follows_what_it_was_told": c_follows, "control_right_against_the_truth": sum(c_right),
              "ask_ms_p50": round(ms[len(ms) // 2], 1), "ask_ms_p90": round(ms[int(len(ms) * 0.9)], 1),
              "control": {"breaks": ok, "kelvin_right_control_wrong": g, "control_right_kelvin_wrong": l, "sign_test_p": p}}
    common.write(m.dir, "answers.json", {"first": first, "second": second, "never_told": never_ans, "another_memory": other, "control": control})
    common.write(m.dir, "result.json", result)
    md = markdown(result, m)
    out = common.publish(HERE, m.dir, result, md)
    print(md)
    print(f"\nresult: {out}")
    if not ok:
        print("THE CONTROL DID NOT BREAK: this run does not count.")
        sys.exit(1)


def markdown(r, m):
    n = r["asked"]
    return "\n".join([
        "# Test 6 · remember what you were told · result", "",
        f"Address {m.url}, release {os.environ.get('MERIDIAN_RELEASE', 'not stated')}, run record `{os.path.relpath(m.dir, common.ROOT)}`.", "",
        f"KELVIN was told {r['facts_told']} facts, then asked in new requests that did not carry them.", "",
        "| | result |", "|---|---|",
        f"| a person's parent, ten names to choose from | **{r['right']} of {n} right** ({r['silent']} silent) |",
        f"| the same questions asked again | {r['asked_twice_identical']} of {n} answers byte for byte the same |",
        f"| people whose parents it was never told | {r['never_told_silent']} of {r['never_told']} silent, {r['never_told_answered']} answered |",
        f"| the same questions in another memory (nothing told there) | {r['another_memory_silent']} of {n} silent |",
        f"| time per ask, p50 / p90 | {r['ask_ms_p50']} / {r['ask_ms_p90']} ms |", "",
        f"The control (parents shuffled among the people): KELVIN followed what it was told {r['control_follows_what_it_was_told']} of {n} times, "
        f"and so was right against the truth only {r['control_right_against_the_truth']} times. "
        f"The control {'breaks' if r['control']['breaks'] else 'DOES NOT BREAK'} (sign test p {common.fmt_p(r['control']['sign_test_p'])}).", "",
        "Times include the network between you and the address."])


if __name__ == "__main__":
    main()
