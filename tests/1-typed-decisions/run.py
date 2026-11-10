#!/usr/bin/env python3
"""Test 1 · Learn typed decisions from cases, scored by the dataset's own scorer.

    python3 tests/1-typed-decisions/run.py

KELVIN lives the 300 training cases of each of the dataset's four areas (each case: a state and its five answers), one
memory per area, in one request. Then it is asked the 100 test cases of that area, which it never saw, in new requests
that carry only the state. The answers are scored by the dataset's own scorer (fetched, pinned, unchanged).

The control, in its own memory per area: the same 300 cases with their answers shuffled among them. On the same 2 000
answers, KELVIN must be right more often where the control is wrong than the other way round (paired, one-sided sign
test p < 0.05), or the run does not count.

Needs: MERIDIAN_URL, MERIDIAN_KEYS_FILE with the eight memories below, and `pip install pyarrow` (the dataset is parquet).
"""
import ast
import concurrent.futures as cf
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common  # noqa: E402

AREAS = ["agent_trace_observability", "customer_service", "invoice_processing", "security_incidents"]
MEMORIES = [f"typed-{a}" for a in AREAS] + [f"typed-{a}-shuffled" for a in AREAS]
# The product's switches for this task, as the customer handbook names them.
SWITCHES = {"KELVIN-Way": "foam+text:N2", "KELVIN-Weigh": "answer", "KELVIN-Sharpness": "lived"}
SHUFFLE_SEED = 0x2002A5


def load(path):
    try:
        import pyarrow.parquet as pq
    except ImportError:
        sys.exit("this test reads the dataset's parquet files: pip install pyarrow")
    return [{"id": r["id"], "state": json.loads(r["state"]), "questions": json.loads(r["questions"]), "gold": json.loads(r["gold"])}
            for r in pq.read_table(path, columns=["id", "state", "questions", "gold"]).to_pylist()]


def dataset_score_one(path):
    """The dataset's own `score_one`, taken from its scorer file unchanged. Only that function is run: the file's main()
    serves a model with vLLM on this machine, which this test does not do."""
    src = open(path).read()
    tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "score_one")
    scope = {"math": math}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), path, "exec"), scope)
    return scope["score_one"]


def as_scored(answer, question):
    """The one named adaptation: a yes/no answer given as `noul` (no probabilities) is read as {true: noul, false: 1 − noul}.
    The scorer's own code expects probabilities. Everything else goes to the scorer as KELVIN gave it."""
    if not isinstance(answer, dict):
        return {"probabilities": {}}
    if question["type"] == "noul" and "probabilities" not in answer:
        if isinstance(answer.get("noul"), (int, float)):
            return dict(answer, probabilities={"true": answer["noul"], "false": 1 - answer["noul"]})
        return dict(answer, probabilities={})
    return answer


def aggregate(results):
    """Means and ECE exactly as the scorer's main() computes them (10 bins of the answer's largest probability)."""
    accs, kls, briers, confs = zip(*results) if results else ((), (), (), ())
    n = len(accs)
    n_bins = 10
    bin_hits, bin_total, bin_conf = [0] * n_bins, [0] * n_bins, [0.0] * n_bins
    for ok, conf in zip(accs, confs):
        b = min(int(conf * n_bins), n_bins - 1)
        bin_total[b] += 1
        bin_hits[b] += int(ok)
        bin_conf[b] += conf
    ece = 0.0
    for b in range(n_bins):
        if bin_total[b]:
            ece += bin_total[b] / n * abs(bin_hits[b] / bin_total[b] - bin_conf[b] / bin_total[b])
    return {"n_decisions": n, "accuracy": sum(accs) / n, "kl_from_gold": sum(kls) / n, "brier": sum(briers) / n, "ece": ece}


def live(m, memory, cases, questions):
    body = {"model": "kelvin", "state": {"lived": [{"state": c["state"], "gold": c["gold"]} for c in cases]}, "questions": questions}
    s, a, raw, ms, _ = m.ask(body, memory=memory, headers=SWITCHES)
    if s != 200:
        common.stop(f"{memory}: living the cases answered {s}: {raw[:300]!r}")
    return ms


def ask_all(m, memory, cases):
    out = {}
    for c in cases:
        s, a, raw, ms, _ = m.ask({"model": "kelvin", "state": c["state"], "questions": c["questions"]}, memory=memory, headers=SWITCHES)
        if s != 200:
            common.stop(f"{memory}: asking case {c['id']} answered {s}: {raw[:300]!r}")
        out[c["id"]] = {"answers": a["answers"], "ms": ms}
    return out


def score(score_one, cases, answers):
    """The scorer's tuple (right, kl, brier, confidence) per answer, in a fixed order (case, then question)."""
    results, per_q = [], {}
    for c in cases:
        for q, gold in c["gold"].items():
            r = score_one(as_scored(answers[c["id"]]["answers"].get(q), c["questions"][q]), gold)
            results.append(r)
            pq = per_q.setdefault(q, [0, 0])
            pq[0] += int(r[0])
            pq[1] += 1
    return results, per_q


def baselines(score_one, train, test):
    """Two plain baselines by the same scorer, computed by us: guessing (every option alike) and the training cases'
    average answer (per area and question, the mean of their answers)."""
    uniform, prior = [], []
    mean = {}
    for c in train:
        for q, g in c["gold"].items():
            acc = mean.setdefault(q, {})
            for o, p in g["probabilities"].items():
                acc[o] = acc.get(o, 0.0) + p / len(train)
    for c in test:
        for q, g in c["gold"].items():
            opts = list(g["probabilities"])
            uniform.append(score_one({"probabilities": {o: 1 / len(opts) for o in opts}}, g))
            prior.append(score_one({"probabilities": {o: mean[q].get(o, 0.0) for o in opts}}, g))
    return uniform, prior


def run_area(m, area, files):
    train, test = load(files[f"{area}/train.parquet"]), load(files[f"{area}/test.parquet"])
    questions = train[0]["questions"]
    golds = [c["gold"] for c in train]
    order = list(range(len(golds)))
    random.Random(SHUFFLE_SEED).shuffle(order)
    shuffled = [dict(c, gold=golds[order[i]]) for i, c in enumerate(train)]
    print(f"  {area}: living {len(train)} cases (and the shuffled control), then asking {len(test)}", flush=True)
    first = {"model": "kelvin", "state": test[0]["state"], "questions": test[0]["questions"]}
    for memory in (f"typed-{area}", f"typed-{area}-shuffled"):
        common.require_new(m, memory, first, SWITCHES)
    t_live = live(m, f"typed-{area}", train, questions)
    t_live_c = live(m, f"typed-{area}-shuffled", shuffled, questions)
    return area, train, test, ask_all(m, f"typed-{area}", test), ask_all(m, f"typed-{area}-shuffled", test), (t_live, t_live_c)


def main():
    common.require_own_door('lives 300 cases in one request (up to a minute each, eight times)')
    files = common.fetch_all(HERE)
    score_one = dataset_score_one(files["score_with_jobs.py"])
    m = common.Meridian("typed-decisions")
    print(f"Test 1 · typed decisions · {m.url} · run record {m.dir}", flush=True)
    with cf.ThreadPoolExecutor(len(AREAS)) as pool:  # one area per thread; each memory has its own key
        done = list(pool.map(lambda a: run_area(m, a, files), AREAS))
    allk, allc, allu, allp, areas = [], [], [], [], {}
    for area, train, test, k, c, (t_live, t_live_c) in done:
        rk, per_q = score(score_one, test, k)
        rc, _ = score(score_one, test, c)
        ru, rp = baselines(score_one, train, test)
        allk += rk
        allc += rc
        allu += ru
        allp += rp
        ms = sorted(v["ms"] for v in k.values())
        areas[area] = {"kelvin": aggregate(rk), "control_shuffled": aggregate(rc), "guessing": aggregate(ru),
                       "average_answer": aggregate(rp), "per_question": {q: {"right": a, "of": n} for q, (a, n) in per_q.items()},
                       "live_ms": round(t_live, 1), "ask_ms_p50": round(ms[len(ms) // 2], 1), "ask_ms_p90": round(ms[int(len(ms) * 0.9)], 1)}
        common.write(m.dir, f"answers_{area}.json", k)
        common.write(m.dir, f"answers_{area}_shuffled.json", c)
    ok, g, l, p = common.control_breaks([r[0] for r in allk], [r[0] for r in allc])
    control = {"breaks": ok, "kelvin_right_control_wrong": g, "control_right_kelvin_wrong": l, "sign_test_p": p}
    result = {"test": "typed decisions", "switches": SWITCHES, "scorer": "the dataset's own score_one, unchanged; yes/no read as {true: noul, false: 1 - noul}; means and ECE as in its main()",
              "all": {"kelvin": aggregate(allk), "control_shuffled": aggregate(allc), "guessing": aggregate(allu), "average_answer": aggregate(allp)},
              "areas": areas, "control": control}
    common.write(m.dir, "result.json", result)
    md = markdown(result, m)
    out = common.publish(HERE, m.dir, result, md)
    print(md)
    print(f"\nresult: {out}/RESULT.md")
    if not control["breaks"]:
        print("THE CONTROL DID NOT BREAK: this run does not count.")
        sys.exit(1)


def markdown(r, m):
    f = lambda d: f"{d['accuracy']:.4f} | {d['kl_from_gold']:.4f} | {d['brier']:.4f} | {d['ece']:.4f}"
    name = {"agent_trace_observability": "agent traces", "customer_service": "customer service",
            "invoice_processing": "invoices", "security_incidents": "security incidents"}
    lines = [f"# Test 1 · typed decisions · result", "",
             f"Address {m.url}, release {os.environ.get('MERIDIAN_RELEASE', 'not stated')}, run record `{os.path.relpath(m.dir, common.ROOT)}`.", "",
             "| | accuracy ↑ | KL from gold ↓ | Brier ↓ | ECE ↓ |", "|---|---|---|---|---|",
             f"| **KELVIN, all four areas** | {f(r['all']['kelvin'])} |",
             f"| control: the lived answers shuffled | {f(r['all']['control_shuffled'])} |",
             f"| guessing (every option alike) | {f(r['all']['guessing'])} |",
             f"| the training cases' average answer (no learning) | {f(r['all']['average_answer'])} |", "",
             f"The control {'breaks' if r['control']['breaks'] else 'DOES NOT BREAK'}: KELVIN right where the control is wrong "
             f"{r['control']['kelvin_right_control_wrong']} times, the other way round {r['control']['control_right_kelvin_wrong']} times "
             f"(sign test p {common.fmt_p(r['control']['sign_test_p'])}).", "",
             "| area | KELVIN | control (shuffled) | ask p50 / p90 ms |", "|---|---|---|---|"]
    for a, v in r["areas"].items():
        lines.append(f"| {name[a]} | {v['kelvin']['accuracy']:.3f} | {v['control_shuffled']['accuracy']:.3f} | {v['ask_ms_p50']} / {v['ask_ms_p90']} |")
    lines += ["", "Right per question (of 100), by the scorer's own rule:", ""]
    for a, v in r["areas"].items():
        lines.append(f"- **{name[a]}:** " + ", ".join(f"{q} {x['right']}" for q, x in v["per_question"].items()))
    lines += ["", "Times include the network between you and the address."]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
