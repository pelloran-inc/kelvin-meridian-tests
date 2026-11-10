#!/usr/bin/env python3
"""Test 7 · Say "I don't know".

    python3 tests/7-i-dont-know/run.py

KELVIN answers only from what it was told. Every question here offers ten names and an eleventh option, "none of the
above". KELVIN is told the parents of half of the people in the facts file (drawn with a fixed seed), then asked:
- told:              a parent it was told                       → the right answer is that parent
- the truth left out: a parent it was told, but that parent is not among the ten names → "none of the above"
- a relation not told: a person it was told about, asked the other parent, which it was never told → "none of the above"
- never told:         a person it was never told anything about → "none of the above"
A real answer may exist in the world for the last two; KELVIN was not told it, so "none of the above" is right.
A silence counts as "none of the above".

The control, in its own memory: nothing told at all. On the "told" questions KELVIN must be right where the control is
wrong more often than the other way round (paired, one-sided sign test p < 0.05), or the run does not count.

Needs: MERIDIAN_URL and MERIDIAN_KEYS_FILE with the two memories below. The facts file is test 6's (parents.tsv).
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common  # noqa: E402

MEMORIES = ["dont-know", "dont-know-nothing-told"]
FACTS = os.path.join(os.path.dirname(HERE), "6-remember", "parents.tsv")
SEED = 0x2002D7
K = 10
NONE = "none of the above"
KINDS = [("told", "told"), ("truth_left_out", "the truth left out"), ("relation_not_told", "a relation not told"),
         ("never_told", "never told")]


def facts_of(path):
    out = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        rel, _c, _p, child, parent = line.rstrip("\n").split("\t")
        out.append((child, rel, parent))
    return out


def options(level, subject, rel, true, pool):
    rng = random.Random(f"{SEED}:{level}:{subject}:{rel}")
    o = sorted(true) + rng.sample(sorted(p for p in pool[rel] if p not in true), K - len(true))
    rng.shuffle(o)
    return o


def items(facts):
    people = sorted({s for s, _, _ in facts})
    random.Random(SEED).shuffle(people)
    told_people = set(people[: len(people) // 2])
    told = [f for f in facts if f[0] in told_people]
    pool = {r: sorted({o for _, rr, o in facts if rr == r}) for r in ("mother", "father")}
    truth = {}
    for s, r, o in told:
        truth.setdefault((s, r), set()).add(o)
    out = []
    for (s, r) in sorted(truth):
        out.append(("told", s, r, options("told", s, r, truth[(s, r)], pool) + [NONE], set(truth[(s, r)])))
    for (s, r) in sorted(truth):
        cands = [o for o in options("left-out", s, r, set(), pool) if o not in truth[(s, r)]]
        while len(cands) < K:
            cands.append(next(p for p in pool[r] if p not in cands and p not in truth[(s, r)]))
        out.append(("truth_left_out", s, r, cands[:K] + [NONE], {NONE}))
    for s in sorted(told_people):
        for r in ("mother", "father"):
            if (s, r) not in truth:
                out.append(("relation_not_told", s, r, options("not-told", s, r, set(), pool) + [NONE], {NONE}))
    never = sorted({(s, r) for s, r, _ in facts if s not in told_people})[: len(truth)]
    for s, r in never:
        out.append(("never_told", s, r, options("never", s, r, set(), pool) + [NONE], {NONE}))
    return told, out


def tell(m, memory, facts):
    for i in range(0, len(facts), 50):
        chunk = facts[i:i + 50]
        s0, r0, o0 = chunk[0]
        state = {"facts": [{"subject": s, "relation": r, "object": o} for s, r, o in chunk]}
        q = {r0: {"type": "choice", "criteria": {o0: None, "nothing": None}}}
        st, a, raw, ms, _ = m.ask({"model": "kelvin", "state": state, "questions": q}, memory=memory)
        if st != 200:
            common.stop(f"{memory}: telling facts {i}–{i + len(chunk)} answered {st}: {raw[:300]!r}")


def ask(m, memory, its):
    out = []
    for kind, s, r, opts, right in its:
        q = {"type": "choice", "instructions": f"What is the {r} of the subject?", "criteria": {o: None for o in opts}}
        st, a, raw, ms, _ = m.ask({"model": "kelvin", "state": {"subject": s}, "questions": {r: q}}, memory=memory)
        if st != 200:
            common.stop(f"{memory}: asking the {r} of {s} answered {st}: {raw[:300]!r}")
        ans = (a.get("answers") or {}).get(r) or {}
        choice = NONE if ans.get("silent") else ans.get("choice")
        out.append({"kind": kind, "subject": s, "rel": r, "choice": choice, "silent": bool(ans.get("silent")),
                    "right": choice in right, "ms": ms})
    return out


def table(recs):
    t = {}
    for kind, _ in KINDS:
        rs = [x for x in recs if x["kind"] == kind]
        t[kind] = {"n": len(rs), "right": sum(x["right"] for x in rs), "none_of_the_above": sum(x["choice"] == NONE for x in rs)}
    return t


def main():
    facts = facts_of(FACTS)
    told, its = items(facts)
    m = common.Meridian("i-dont-know")
    print(f"Test 7 · say \"I don't know\" · {m.url} · run record {m.dir}", flush=True)
    print(f"  telling {len(told)} facts, then asking {len(its)} questions; the control asks the same with nothing told", flush=True)
    kind, s0, r0, o0, _ = its[0]
    probe = {"model": "kelvin", "state": {"subject": s0},
             "questions": {r0: {"type": "choice", "instructions": f"What is the {r0} of the subject?", "criteria": {o: None for o in o0}}}}
    for memory in MEMORIES:
        common.require_new(m, memory, probe)
    tell(m, "dont-know", told)
    k = ask(m, "dont-know", its)
    c = ask(m, "dont-know-nothing-told", its)
    t_idx = [i for i, x in enumerate(its) if x[0] == "told"]
    ok, g, l, p = common.control_breaks([k[i]["right"] for i in t_idx], [c[i]["right"] for i in t_idx])
    not_known = [x for x in k if x["kind"] != "told"]
    ms = sorted(x["ms"] for x in k)
    result = {"test": "say I don't know", "facts_told": len(told), "asked": len(its), "kelvin": table(k), "control_nothing_told": table(c),
              "not_known": len(not_known), "not_known_none_of_the_above": sum(x["choice"] == NONE for x in not_known),
              "right_overall": sum(x["right"] for x in k), "ask_ms_p50": round(ms[len(ms) // 2], 1), "ask_ms_p90": round(ms[int(len(ms) * 0.9)], 1),
              "control": {"breaks": ok, "kelvin_right_control_wrong": g, "control_right_kelvin_wrong": l, "sign_test_p": p}}
    common.write(m.dir, "answers.json", {"kelvin": k, "control_nothing_told": c})
    common.write(m.dir, "result.json", result)
    md = markdown(result, m)
    out = common.publish(HERE, m.dir, result, md)
    print(md)
    print(f"\nresult: {out}")
    if not ok:
        print("THE CONTROL DID NOT BREAK: this run does not count.")
        sys.exit(1)


def markdown(r, m):
    lines = ["# Test 7 · say \"I don't know\" · result", "",
             f"Address {m.url}, release {os.environ.get('MERIDIAN_RELEASE', 'not stated')}, run record `{os.path.relpath(m.dir, common.ROOT)}`.", "",
             f"KELVIN was told {r['facts_told']} facts. Every question offered ten names and \"none of the above\".", "",
             "| question | right answer | KELVIN right | KELVIN said \"none of the above\" | control (nothing told): right |", "|---|---|---|---|---|"]
    for kind, label in KINDS:
        a, b = r["kelvin"][kind], r["control_nothing_told"][kind]
        want = "the parent it was told" if kind == "told" else "none of the above"
        lines.append(f"| {label} | {want} | {a['right']} of {a['n']} | {a['none_of_the_above']} | {b['right']} of {b['n']} |")
    lines += ["", f"On the {r['not_known']} questions it could not know, KELVIN said \"none of the above\" {r['not_known_none_of_the_above']} times. "
              f"Right overall: {r['right_overall']} of {r['asked']}. Time per ask p50 / p90: {r['ask_ms_p50']} / {r['ask_ms_p90']} ms.", "",
              f"The control {'breaks' if r['control']['breaks'] else 'DOES NOT BREAK'}: on the told questions KELVIN was right where the control was wrong "
              f"{r['control']['kelvin_right_control_wrong']} times, the other way round {r['control']['control_right_kelvin_wrong']} times "
              f"(sign test p {common.fmt_p(r['control']['sign_test_p'])}).", "",
              "Times include the network between you and the address."]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
