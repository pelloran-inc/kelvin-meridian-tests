#!/usr/bin/env python3
"""Test 4 · Intent, and "none of the above".

    python3 tests/4-intent/run.py

KELVIN lives CLINC150's 15 000 training requests once each, every one told with its intent (150 intents), and the
dataset's 100 training requests that belong to none of them, told as "none of the above". All in one request.
Then it is asked the 4 500 test requests and the 1 000 test requests that belong to no intent, in new requests that
carry only the sentence. A silence counts as "none of the above".

The control, in its own memory: the same lived requests with their intents shuffled among them. On the same 4 500
in-scope asks, KELVIN must be right where the control is wrong more often than the other way round (paired, one-sided
sign test p < 0.05), or the run does not count.

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

MEMORIES = ["intent", "intent-shuffled"]
SWITCHES = {"KELVIN-Way": "foam+text:A2", "KELVIN-Silence": "lived"}
NONE = "oos"
SHUFFLE_SEED = 0x2002A5


def cases(split, pairs, intents):
    q = {"intent": {"type": "choice", "instructions": "What does the person want?",
                    "criteria": {**{i: i for i in intents}, NONE: "none of the above"}}}
    return [{"id": f"clinc_{split}_{k:05d}", "state": {"utterance": t}, "questions": q,
             "gold": {"intent": {"type": "choice", "label": lab, "probabilities": {lab: 1.0}}}} for k, (t, lab) in enumerate(pairs)]


def live(m, memory, lived, questions):
    body = {"model": "kelvin", "state": {"lived": [{"state": c["state"], "gold": c["gold"]} for c in lived]}, "questions": questions}
    s, a, raw, ms, _ = m.ask(body, memory=memory, headers=SWITCHES)
    if s != 200:
        common.stop(f"{memory}: living the requests answered {s}: {raw[:300]!r}")
    return ms


def ask_all(m, memory, asked):
    out = []
    for c in asked:
        s, a, raw, ms, _ = m.ask({"model": "kelvin", "state": c["state"], "questions": c["questions"]}, memory=memory, headers=SWITCHES)
        if s != 200:
            common.stop(f"{memory}: asking {c['id']} answered {s}: {raw[:300]!r}")
        ans = (a.get("answers") or {}).get("intent")
        silent = not ans or bool(ans.get("silent"))
        out.append({"id": c["id"], "gold": c["gold"]["intent"]["label"], "answer": NONE if silent else ans.get("choice"),
                    "silent": silent, "ms": ms})
    return out


def summary(rows):
    inn = [r for r in rows if r["gold"] != NONE]
    oos = [r for r in rows if r["gold"] == NONE]
    ms = sorted(r["ms"] for r in rows)
    return {"in_scope_right": sum(r["answer"] == r["gold"] for r in inn), "in_scope": len(inn),
            "none_right": sum(r["answer"] == NONE for r in oos), "none": len(oos),
            "in_scope_accuracy": sum(r["answer"] == r["gold"] for r in inn) / len(inn),
            "none_of_the_above_recall": sum(r["answer"] == NONE for r in oos) / len(oos),
            "overall_accuracy": sum(r["answer"] == r["gold"] for r in rows) / len(rows),
            "ask_ms_p50": round(ms[len(ms) // 2], 1), "ask_ms_p90": round(ms[int(len(ms) * 0.9)], 1)}


def main():
    common.require_own_door('lives 15 100 requests in one request (several minutes)')
    files = common.fetch_all(HERE)
    d = json.load(open(files["data_full.json"]))
    intents = sorted({lab for _, lab in d["train"]})
    lived = cases("train", d["train"], intents) + cases("oos_train", d["oos_train"], intents)
    asked = cases("test", d["test"], intents) + cases("oos_test", d["oos_test"], intents)
    golds = [c["gold"] for c in lived]
    order = list(range(len(golds)))
    random.Random(SHUFFLE_SEED).shuffle(order)
    shuffled = [dict(c, gold=golds[order[i]]) for i, c in enumerate(lived)]
    qs = asked[0]["questions"]
    m = common.Meridian("intent")
    print(f"Test 4 · intent · {m.url} · run record {m.dir}", flush=True)
    print(f"  living {len(lived)} requests in each memory (one request each; this takes minutes), then asking {len(asked)}", flush=True)

    first = {"model": "kelvin", "state": asked[0]["state"], "questions": asked[0]["questions"]}

    one_teach_at_a_time = threading.Lock()  # a door answers one request at a time: two long teaches sent together
    # would make the second wait for the first, past the address's 600 s; the asks then go side by side

    def one(memory, rows):
        common.require_new(m, memory, first, SWITCHES)
        with one_teach_at_a_time:
            t = live(m, memory, rows, qs)
        return t, ask_all(m, memory, asked)

    with cf.ThreadPoolExecutor(2) as pool:
        (t_k, k), (t_c, c) = pool.map(lambda x: one(*x), [("intent", lived), ("intent-shuffled", shuffled)])
    common.write(m.dir, "answers.json", k)
    common.write(m.dir, "answers_shuffled.json", c)
    inn = [i for i, r in enumerate(k) if r["gold"] != NONE]
    ok, g, l, p = common.control_breaks([k[i]["answer"] == k[i]["gold"] for i in inn], [c[i]["answer"] == c[i]["gold"] for i in inn])
    result = {"test": "intent and none of the above", "switches": SWITCHES, "lived": len(lived), "asked": len(asked),
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
    return "\n".join([
        "# Test 4 · intent, and \"none of the above\" · result", "",
        f"Address {m.url}, release {os.environ.get('MERIDIAN_RELEASE', 'not stated')}, run record `{os.path.relpath(m.dir, common.ROOT)}`.", "",
        f"KELVIN lived {r['lived']} requests once each (in one request, {r['live_seconds']} s) and was asked {r['asked']} it had never seen.", "",
        "| | KELVIN | control (intents shuffled) |", "|---|---|---|",
        f"| intent right (of {k['in_scope']}) | {k['in_scope_right']} ({k['in_scope_accuracy']:.4f}) | {c['in_scope_right']} ({c['in_scope_accuracy']:.4f}) |",
        f"| \"none of the above\" right (of {k['none']}) | {k['none_right']} ({k['none_of_the_above_recall']:.4f}) | {c['none_right']} ({c['none_of_the_above_recall']:.4f}) |",
        f"| all {r['asked']} | {k['overall_accuracy']:.4f} | {c['overall_accuracy']:.4f} |",
        f"| time per ask, p50 / p90 | {k['ask_ms_p50']} / {k['ask_ms_p90']} ms | |", "",
        f"The control {'breaks' if r['control']['breaks'] else 'DOES NOT BREAK'}: KELVIN right where the control is wrong "
        f"{r['control']['kelvin_right_control_wrong']} times, the other way round {r['control']['control_right_kelvin_wrong']} times "
        f"(sign test p {common.fmt_p(r['control']['sign_test_p'])}).", "",
        "Times include the network between you and the address."])


if __name__ == "__main__":
    main()
