#!/usr/bin/env python3
"""Test 5 · When to call a tool.

    python3 tests/5-when-to-call-a-tool/run.py

Each item of When2Call's test set is a request, the tools at hand, and four candidate replies: call a tool, ask for
what is missing, say it cannot, or answer directly. The same request appears several times with other tools; all its
items are one family, and a family is either lived or asked, never both. The families are shuffled with a fixed seed
and half of them are lived; of the other half, the last two thirds are asked (the first third is set aside).
KELVIN lives its half in one request, each item told with its right reaction, then answers the asked items it never saw.

The control, in its own memory: the same lived items with their reactions shuffled among them. KELVIN must be right
where the control is wrong more often than the other way round (paired, one-sided sign test p < 0.05), or the run
does not count.

Needs: MERIDIAN_URL and MERIDIAN_KEYS_FILE with the two memories below.
"""
import concurrent.futures as cf
import json
import os
import random
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common  # noqa: E402

MEMORIES = ["tools", "tools-shuffled"]
SWITCHES = {"KELVIN-Way": "foam+text:A2+rel", "KELVIN-Weigh": "lived"}
OPTS = ("tool_call", "request_for_info", "cannot_answer", "direct")
FAMILY_SEED, SHUFFLE_SEED = 0x2002B2, 0x2002A5
NAMES = {"tool_call": "call a tool", "request_for_info": "ask for what is missing", "cannot_answer": "say it cannot",
         "direct": "answer directly"}


def case(x):
    q = {"reaction": {"type": "choice", "instructions": "How should the assistant react to this request, given these tools?",
                      "criteria": {o: x["answers"][o] for o in OPTS}}}
    return {"id": x["uuid"], "state": {"question": x["question"], "tools": [json.loads(t) for t in x["tools"]]}, "questions": q,
            "gold": {"reaction": {"type": "choice", "label": x["correct_answer"], "probabilities": {x["correct_answer"]: 1.0}}}}


def draw(items):
    fam = {}
    for x in items:
        fam.setdefault(x.get("orig_question") or x["question"], []).append(x)
    keys = sorted(fam)
    random.Random(FAMILY_SEED).shuffle(keys)
    half = len(keys) // 2
    lived = [dict(case(x), group=k) for k in keys[:half] for x in fam[k]]  # each lived item keeps its family
    third = (len(keys) - half) // 3
    asked = [case(x) for k in keys[half + third:] for x in fam[k]]
    return lived, asked


def live(m, memory, lived):
    entries = [dict({"state": c["state"], "gold": c["gold"]}, group=c["group"]) for c in lived]
    body = {"model": "kelvin", "state": {"lived": entries}, "questions": lived[0]["questions"]}
    s, a, raw, ms, _ = m.ask(body, memory=memory, headers=SWITCHES)
    if s != 200:
        common.stop(f"{memory}: living the items answered {s}: {raw[:300]!r}")
    return ms


def ask_all(m, memory, asked):
    out = []
    for c in asked:
        s, a, raw, ms, _ = m.ask({"model": "kelvin", "state": c["state"], "questions": c["questions"]}, memory=memory, headers=SWITCHES)
        if s != 200:
            common.stop(f"{memory}: asking {c['id']} answered {s}: {raw[:300]!r}")
        ans = (a.get("answers") or {}).get("reaction")
        silent = not ans or bool(ans.get("silent"))
        out.append({"id": c["id"], "gold": c["gold"]["reaction"]["label"], "answer": None if silent else ans.get("choice"),
                    "silent": silent, "ms": ms})
    return out


def summary(rows):
    per = {}
    for r in rows:
        pc = per.setdefault(r["gold"], [0, 0])
        pc[0] += int(r["answer"] == r["gold"])
        pc[1] += 1
    ms = sorted(r["ms"] for r in rows)
    return {"right": sum(r["answer"] == r["gold"] for r in rows), "n": len(rows),
            "accuracy": sum(r["answer"] == r["gold"] for r in rows) / len(rows), "silent": sum(r["silent"] for r in rows),
            "per_reaction": {k: {"right": a, "of": n} for k, (a, n) in sorted(per.items())},
            "ask_ms_p50": round(ms[len(ms) // 2], 1), "ask_ms_p90": round(ms[int(len(ms) * 0.9)], 1)}


def main():
    common.require_own_door('lives 1 835 items in one request (about a minute)')
    files = common.fetch_all(HERE)
    items = [json.loads(line) for line in open(files["when2call_test_mcq.jsonl"])]
    lived, asked = draw(items)
    golds = [c["gold"] for c in lived]
    order = list(range(len(golds)))
    random.Random(SHUFFLE_SEED).shuffle(order)
    shuffled = [dict(c, gold=golds[order[i]]) for i, c in enumerate(lived)]
    m = common.Meridian("when-to-call-a-tool")
    print(f"Test 5 · when to call a tool · {m.url} · run record {m.dir}", flush=True)
    print(f"  living {len(lived)} items in each memory (one request each), then asking {len(asked)}", flush=True)

    first = {"model": "kelvin", "state": asked[0]["state"], "questions": asked[0]["questions"]}

    one_teach_at_a_time = threading.Lock()  # a door answers one request at a time: two long teaches sent together
    # would make the second wait for the first, past the address's 600 s; the asks then go side by side

    def one(memory, rows):
        common.require_new(m, memory, first, SWITCHES)
        with one_teach_at_a_time:
            t = live(m, memory, rows)
        return t, ask_all(m, memory, asked)

    with cf.ThreadPoolExecutor(2) as pool:
        (t_k, k), (t_c, c) = pool.map(lambda x: one(*x), [("tools", lived), ("tools-shuffled", shuffled)])
    common.write(m.dir, "answers.json", k)
    common.write(m.dir, "answers_shuffled.json", c)
    ok, g, l, p = common.control_breaks([r["answer"] == r["gold"] for r in k], [r["answer"] == r["gold"] for r in c])
    result = {"test": "when to call a tool", "switches": SWITCHES, "lived": len(lived), "asked": len(asked),
              "kelvin": summary(k), "control_shuffled": summary(c), "live_seconds": round(t_k / 1000, 1),
              "control": {"breaks": ok, "kelvin_right_control_wrong": g, "control_right_kelvin_wrong": l, "sign_test_p": p}}
    common.write(m.dir, "result.json", result)
    md = markdown(result, m)
    out = common.publish(HERE, m.dir, result, md)
    print(md)
    print(f"\nresult: {out}")
    if not ok:
        print("THE CONTROL DID NOT BREAK: this run does not count.")
        sys.exit(1)


def markdown(r, m):
    k, c = r["kelvin"], r["control_shuffled"]
    lines = ["# Test 5 · when to call a tool · result", "",
             f"Address {m.url}, release {os.environ.get('MERIDIAN_RELEASE', 'not stated')}, run record `{os.path.relpath(m.dir, common.ROOT)}`.", "",
             f"KELVIN lived {r['lived']} items (in one request, {r['live_seconds']} s) and was asked {r['asked']} items of request families it never met.", "",
             "| | KELVIN | control (reactions shuffled) |", "|---|---|---|",
             f"| right (of {k['n']}) | {k['right']} ({k['accuracy']:.4f}) | {c['right']} ({c['accuracy']:.4f}) |"]
    for o in OPTS:
        if o in k["per_reaction"]:
            a, b = k["per_reaction"][o], c["per_reaction"].get(o, {"right": 0, "of": 0})
            lines.append(f"| … where the right reaction is \"{NAMES[o]}\" (of {a['of']}) | {a['right']} | {b['right']} |")
    lines += [f"| silent | {k['silent']} | {c['silent']} |",
              f"| time per ask, p50 / p90 | {k['ask_ms_p50']} / {k['ask_ms_p90']} ms | |", "",
              f"The control {'breaks' if r['control']['breaks'] else 'DOES NOT BREAK'}: KELVIN right where the control is wrong "
              f"{r['control']['kelvin_right_control_wrong']} times, the other way round {r['control']['control_right_kelvin_wrong']} times "
              f"(sign test p {common.fmt_p(r['control']['sign_test_p'])}).", "",
              "Times include the network between you and the address."]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
