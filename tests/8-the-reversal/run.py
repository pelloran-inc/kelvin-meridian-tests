#!/usr/bin/env python3
"""Test 8 · The reversal: told one way, asked both ways.

    python3 tests/8-the-reversal/run.py

KELVIN is told 346 real facts in one direction only: a person's mother or father (Wikidata, CC0; test 6's parents.tsv),
50 to a request. Then, in new requests that do not carry them, it is asked:
- forward: who is this person's mother or father (`state.subject`), 50 questions;
- reverse: whose mother or father is this person (`state.object`), 50 questions, among them every parent with several
  children: every child must be held, and no one else;
- about people who are no one's parent: KELVIN was never told a child of theirs, so it must stay silent, 50 questions.
Each question has ten names to choose from. Every check prints right, wrong or silent, and its time.

The control, in the same memory: the reverse questions asked again with the relation swapped (mother <-> father). KELVIN
was told each child under one relation only, so under the other it must not give that parent's children: right on the
told relation where the swapped relation is "right" (the same children held) less often than the other way round
(paired, one-sided sign test p < 0.05), or the run does not count. One memory, so one key is enough.

Needs: MERIDIAN_URL and MERIDIAN_KEY (your key), or MERIDIAN_KEYS_FILE with the memory below.
"""
import collections
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common  # noqa: E402

MEMORIES = ["reversal"]
SEED = 0x2002A8
K = 10  # names to choose from
EACH = 50  # questions of each kind
FACTS = os.path.join(os.path.dirname(HERE), "6-remember", "parents.tsv")


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
        rel, _, parent = chunk[0]
        state = {"facts": [{"subject": c, "relation": r, "object": p} for r, c, p in chunk]}
        q = {rel: {"type": "choice", "criteria": {parent: None, "nobody": None}}}
        s, a, raw, ms, _ = m.ask({"model": "kelvin", "state": state, "questions": q}, memory=memory)
        if s != 200:
            common.stop(f"{memory}: telling facts {i}–{i + len(chunk)} answered {s}: {raw[:300]!r}")


def ask(m, memory, items, way):
    """items: (relation, name, options); way: "subject" (forward) or "object" (reverse). Each answer with its held names."""
    out = []
    for rel, name, opts in items:
        text = f"Who is the {rel} of the subject?" if way == "subject" else f"Whose {rel} is the object?"
        q = {"type": "choice", "instructions": text, "criteria": {o: None for o in opts}}
        s, a, raw, ms, _ = m.ask({"model": "kelvin", "state": {way: name}, "questions": {rel: q}}, memory=memory)
        if s != 200:
            common.stop(f"{memory}: asking ({way} {name}, {rel}) answered {s}: {raw[:300]!r}")
        ans = (a.get("answers") or {}).get(rel) or {}
        silent = bool(ans.get("silent"))
        held = [] if silent else sorted(o for o, p in (ans.get("probabilities") or {}).items() if p and p > 0)
        out.append({"rel": rel, way: name, "silent": silent, "held": held, "ms": ms})
    return out


def main():
    rng = random.Random(SEED)
    facts = facts_of(FACTS)
    rng.shuffle(facts)
    up = collections.defaultdict(set)    # (relation, child) -> parents
    down = collections.defaultdict(set)  # (relation, parent) -> children
    for r, c, p in facts:
        up[(r, c)].add(p)
        down[(r, p)].add(c)
    everyone = sorted({p for _, _, p in facts} | {c for _, c, _ in facts})
    parents_any = {p for _, _, p in facts}

    def options(true):
        o = list(true) + rng.sample([x for x in everyone if x not in true], K - len(true))
        rng.shuffle(o)
        return o

    fwd_keys = rng.sample(sorted(up), EACH)
    several = sorted(k for k, v in down.items() if len(v) > 1)
    rev_keys = several + rng.sample(sorted(k for k in down if k not in several), EACH - len(several))
    never = rng.sample([(r, x) for r in ("mother", "father") for x in everyone if x not in parents_any], EACH)
    forward = [(r, c, options(sorted(up[(r, c)]))) for r, c in fwd_keys]
    reverse = [(r, p, options(sorted(down[(r, p)]))) for r, p in rev_keys]
    silent_items = [(r, x, options([])) for r, x in never]
    swap = {"mother": "father", "father": "mother"}
    swapped = [(swap[r], p, opts) for r, p, opts in reverse]  # the same parents and names, the other relation

    m = common.Meridian("reversal")
    print(f"Test 8 · the reversal · {m.url} · run record {m.dir}", flush=True)
    print(f"  telling {len(facts)} facts one way (child -> parent), then {EACH} forward, {EACH} reverse "
          f"({len(several)} of them parents with several children) and {EACH} about people who are no one's parent", flush=True)
    r0, c0, o0 = forward[0]
    probe = {"model": "kelvin", "state": {"subject": c0},
             "questions": {r0: {"type": "choice", "instructions": f"Who is the {r0} of the subject?", "criteria": {o: None for o in o0}}}}
    for memory in MEMORIES:
        common.require_new(m, memory, probe)
    tell(m, "reversal", facts)
    f_ans = ask(m, "reversal", forward, "subject")
    r_ans = ask(m, "reversal", reverse, "object")
    s_ans = ask(m, "reversal", silent_items, "object")
    c_ans = ask(m, "reversal", swapped, "object")

    def verdict(a, true):
        return "silent" if a["silent"] else ("right" if set(a["held"]) == set(true) else "wrong")

    rows = []
    for kind, ans, items, truth in (("forward", f_ans, forward, up), ("reverse", r_ans, reverse, down)):
        for a, (r, name, _) in zip(ans, items):
            v = verdict(a, truth[(r, name)])
            rows.append({"kind": kind, "rel": r, "name": name, "verdict": v, "held": a["held"], "true": sorted(truth[(r, name)]), "ms": round(a["ms"], 1)})
    for a, (r, name, _) in zip(s_ans, silent_items):
        rows.append({"kind": "no one's parent", "rel": r, "name": name, "verdict": "silent" if a["silent"] else "answered", "held": a["held"], "true": [], "ms": round(a["ms"], 1)})
    for row in rows:
        print(f"  {row['kind']:16s} {row['rel']:6s} {row['name'][:38]:38s} {row['verdict']:8s} {row['ms']:7.1f} ms", flush=True)

    right = [x["verdict"] == "right" for x in rows if x["kind"] == "reverse"]
    # the control "right": under the swapped relation the same children as the told relation's
    c_right = [(not a["silent"]) and set(a["held"]) == down[(r, p)] for a, (r, p, _) in zip(c_ans, reverse)]
    ok, g, l, pval = common.control_breaks(right, c_right)
    count = lambda kind, v: sum(1 for x in rows if x["kind"] == kind and x["verdict"] == v)
    ms = lambda kind: sorted(x["ms"] for x in rows if x["kind"] == kind)
    p50 = lambda v: round(v[len(v) // 2], 1)
    result = {"test": "the reversal", "facts_told": len(facts), "told_one_way": "child -> parent",
              "forward": {"asked": EACH, "right": count("forward", "right"), "wrong": count("forward", "wrong"), "silent": count("forward", "silent")},
              "reverse": {"asked": EACH, "right": count("reverse", "right"), "wrong": count("reverse", "wrong"), "silent": count("reverse", "silent"),
                          "parents_with_several_children": len(several),
                          "several_children_all_held": sum(1 for x in rows if x["kind"] == "reverse" and len(x["true"]) > 1 and x["verdict"] == "right")},
              "no_ones_parent": {"asked": EACH, "silent": count("no one's parent", "silent"), "answered": count("no one's parent", "answered")},
              "ask_ms_p50": {"forward": p50(ms("forward")), "reverse": p50(ms("reverse")), "no_ones_parent": p50(ms("no one's parent"))},
              "control": {"breaks": ok, "kelvin_right_control_wrong": g, "control_right_kelvin_wrong": l, "sign_test_p": pval,
                          "swapped_relation_gave_the_same_children": sum(c_right), "swapped_relation_silent": sum(a["silent"] for a in c_ans)}}
    common.write(m.dir, "answers.json", {"rows": rows, "control": c_ans})
    common.write(m.dir, "result.json", result)
    md = markdown(result, m)
    out = common.publish(HERE, m.dir, result, md)
    print(md)
    print(f"\nresult: {out}")
    if not ok:
        print("THE CONTROL DID NOT BREAK: this run does not count.")
        sys.exit(1)


def markdown(r, m):
    f, v, s = r["forward"], r["reverse"], r["no_ones_parent"]
    return "\n".join([
        "# Test 8 · the reversal · result", "",
        f"Address {m.url}, release {os.environ.get('MERIDIAN_RELEASE', 'not stated')}, run record `{os.path.relpath(m.dir, common.ROOT)}`.", "",
        f"KELVIN was told {r['facts_told']} facts one way only (child → parent), then asked both ways in new requests that did not carry them.", "",
        "| | right | wrong | silent | time per ask, p50 |", "|---|---|---|---|---|",
        f"| forward: whose mother or father is asked (`state.subject`) | **{f['right']} of {f['asked']}** | {f['wrong']} | {f['silent']} | {r['ask_ms_p50']['forward']} ms |",
        f"| reverse: whose child is asked (`state.object`), every child held and no one else | **{v['right']} of {v['asked']}** | {v['wrong']} | {v['silent']} | {r['ask_ms_p50']['reverse']} ms |",
        f"| people who are no one's parent | — | {s['answered']} answered | **{s['silent']} of {s['asked']}** | {r['ask_ms_p50']['no_ones_parent']} ms |", "",
        f"Of the reverse questions, {v['parents_with_several_children']} ask about a parent with several children; all children were held in {v['several_children_all_held']} of them.", "",
        f"The control (the reverse questions asked with the relation swapped, mother ↔ father): the same children given {r['control']['swapped_relation_gave_the_same_children']} of {v['asked']} times, "
        f"silent {r['control']['swapped_relation_silent']} times. "
        f"The control {'breaks' if r['control']['breaks'] else 'DOES NOT BREAK'} (sign test p {common.fmt_p(r['control']['sign_test_p'])}).", "",
        "Times include the network between you and the address."])


if __name__ == "__main__":
    main()
