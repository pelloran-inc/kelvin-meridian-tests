#!/usr/bin/env python3
"""Test 3 · A sound, an object and its name.

    python3 tests/3-sound-object-name/fetch.py mirror      # once: the clips (or `youtube`; see the README)
    python3 tests/3-sound-object-name/run.py [--side-by-side N]

Six lives, each in a memory of its own. In each, KELVIN lives 4 things once: an 8-second clip of each (seconds 0 to 7,
seen and heard), told with its name, one request a thing. Then each ask is its own request, with second 8 of a clip,
which it never lived:
  - from the sound alone, and from the picture alone: what is it called? (of the 9 names: 4 lived, 5 never lived)
  - from the name alone: which of 4 offered clips is it, by the picture, and by the sound?
  - 5 things of kinds it never lived, by sound and by picture: it should not answer with a lived name;
  - their 5 names, which it never heard: it should not answer at all.
Two arms on the same lives: the clips' real names, and made-up names (thing A ... thing I), which must be answered alike.
The control, in memories of its own: the real names rotated among the lived things, each thing told the next one's name.
It must break: each of the four lived-thing asks must fall below 12 of 24, or the test does not count.

Every memory must be new: before anything is lived, each is asked its life's first ask by the name, and the run stops if
any answers. Needs: MERIDIAN_URL, MERIDIAN_KEYS_FILE with the 18 memories below, and the clips (fetch.py). Python's
standard library only.
"""
import argparse
import concurrent.futures as cf
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common  # noqa: E402
import meridian  # noqa: E402

LIVES = [1, 2, 3, 4, 5, 6]
ARMS = ["real", "made-up", "rotated"]  # rotated: the control (the real names, each lived thing told the next one's name)
MEMORIES = [f"sound-{arm}-life{life}" for arm in ARMS for life in LIVES]
SEED = 0x2002A3  # the seed of the recorded run: the made-up names' order and every ask's option order. The strings it is
# combined with below (e.g. "g1", "N1", "g3g2", "N2") are the recorded run's own, kept unchanged so every order is the same.
THINGS = 4
LETTERS = "ABCDEFGHIJKL"
# KELVIN's read for this task: a thing is known from one second only if that second lies within the spread the thing showed
# over its own lived seconds; else it stays silent. Sent in every request, as in the recorded run.
READ = {"read": "own width"}
MAX_BODY = 32 << 20  # the standard's limit for one request
ASKS = ["sound to name", "picture to name", "name to clip by picture", "name to clip by sound",
        "never-lived thing by sound", "never-lived thing by picture", "never-lived name by picture", "never-lived name by sound"]
BAR = 12          # each lived-thing claim: at least 12 of 24 right; the control must fall below 12 on each
NEVER_THING = 29  # a never-lived thing answered with a lived name: at most 29 of 60 (silent on more than half)
NEVER_NAME = 6    # a never-lived name answered: at most 6 of 60
RECORDED = {"sound to name": 14, "picture to name": 18, "name to clip by picture": 23, "name to clip by sound": 18,
            "never-lived thing answered with a lived name": 12, "never-lived name answered": 0}
RECORDED_CONTROL = {"sound to name": 0, "picture to name": 0, "name to clip by picture": 0, "name to clip by sound": 1}


def clip_asset(path):
    """A clip as the request's asset, as the recorded run sent it (type video, format mp4)."""
    return meridian.asset(path, "video", "mp4")  # read when sent: raw in MB1, base64 in JSON


def the_clips():
    """The clips fetch.py put in data/, the route it used, and which clips it could not fetch."""
    src = json.load(open(os.path.join(HERE, "clips.json")))
    rec_path = os.path.join(HERE, "data", "fetch.json")
    if not os.path.exists(rec_path):
        sys.exit("no clips yet: run  python3 tests/3-sound-object-name/fetch.py mirror  (or youtube; see the README)")
    rec = json.load(open(rec_path))
    have, missing = {}, []
    for c in src["clips"]:
        r = rec["clips"].get(c["clip"], {})
        p = os.path.join(HERE, "data", "clips", c["clip"] + ".mp4")
        if "sha256" in r and "refused" not in r and os.path.exists(p):
            have[c["clip"]] = dict(c, path=p, fetched_sha256=r["sha256"])
        else:
            missing.append(c["clip"])
    if rec["route"] in ("mirror", "folder") and missing:
        common.stop(f"{len(missing)} clips are missing; run fetch.py again (route {rec['route']})")
    return src, rec, have, missing


def plan(life, label, have, arm):
    """One life of one arm: who is lived, their names, and what each is told (as the recorded run drew them). Each thing
    comes with its fetched clip, or None if it could not be fetched."""
    li = life["life"]
    real = arm in ("real", "rotated")
    order = random.Random(f"{SEED}:life{li}:letters").sample(range(THINGS), THINGS)
    lived = [(f"thing {li}.{i}", (label[c] if real else f"thing {LETTERS[order[i]]}"), have.get(c)) for i, c in enumerate(life["lived"])]
    never = [(f"stranger {li}.{i}", (label[c] if real else f"thing {LETTERS[THINGS + i]}"), have.get(c)) for i, c in enumerate(life["never"])]
    told = {t: n for t, n, _ in lived}
    if arm == "rotated":
        ns = [n for _, n, _ in lived]
        told = {t: ns[(i + 1) % len(ns)] for i, (t, _, _) in enumerate(lived)}
    return lived, never, told


def run_life(m, life, label, have, arm):
    """Tell the life's 4 things, then ask, in the recorded run's order. Returns one record per request."""
    li = life["life"]
    memory = f"sound-{arm}-life{li}"
    lived, never, told = plan(life, label, have, arm)
    names = [n for _, n, _ in lived] + [n for _, n, _ in never]
    lived_names = [n for _, n, _ in lived]
    recs = []

    def send(body, ask, thing, truth):
        size = meridian.encoded_size(body)  # the body as it is sent (MB1 or JSON)
        if size > MAX_BODY:
            recs.append({"arm": arm, "life": li, "ask": ask, "thing": thing, "truth": truth, "status": None, "lost": f"the request is {size} bytes, over 32 MiB; not sent"})
            return None
        status, answer, raw, ms, sent = m.ask(body, memory=memory)
        choice, _, silent = meridian.answer_of(answer, "q") if status == 200 else (None, None, False)
        rec = {"arm": arm, "life": li, "ask": ask, "thing": thing, "truth": truth, "choice": choice, "silent": silent,
               "status": status, "ms": round(ms, 1), "bytes_sent": sent}
        if status != 200:
            rec["error"] = raw[:300].decode("utf-8", "replace")
        recs.append(rec)
        return rec

    # tell: each thing once, its clip and its name
    for t, n, c in lived:
        ref = f"clip-{c['clip']}"
        body = {"model": "kelvin", "state": {"things": [{"thing": t, "clip": ref, "name": told[t]}], **READ}, "assets": {ref: clip_asset(c["path"])},
                "questions": {"q": {"type": "choice", "instructions": "What is it called?", "criteria": {x: None for x in names}}}}
        send(body, "tell", t, told[t])
    # by a sense: second 8 of the clip, by its sound and by its picture -> its name, of the 9 names
    for part, items in (("lived", lived), ("never", never)):
        for t, n, c in items:
            for sense in ("sound", "picture"):
                ask = f"{sense} to name" if part == "lived" else f"never-lived thing by {sense}"
                if c is None:  # route 2: a never-lived thing's clip that could not be fetched
                    recs.append({"arm": arm, "life": li, "ask": ask, "thing": t, "truth": n, "status": None, "lost": "its clip could not be fetched"})
                    continue
                opts = list(names)
                random.Random(f"{SEED}:{li}:{'g1' if part == 'lived' else 'N1'}:{sense}:{c['clip']}").shuffle(opts)
                ref = f"ask-{c['clip']}"
                body = {"model": "kelvin", "state": {"clip": ref, "sense": sense, **READ}, "assets": {ref: clip_asset(c["path"])},
                        "questions": {"q": {"type": "choice", "instructions": "What is it called?", "criteria": {x: None for x in opts}}}}
                r = send(body, ask, t, n)
                if r:
                    r.update(right=r["choice"] == n, lived_name=r["choice"] in lived_names, first=r["choice"] == opts[0], last=r["choice"] == opts[-1])
    # by the name: which of the 4 offered clips (the life's 4 lived clips, second 8) is it, by the picture and by the sound
    for part, items in (("lived", lived), ("never", never)):
        for t, n, c in items:
            for sense in ("picture", "sound"):
                ask = f"name to clip by {sense}" if part == "lived" else f"never-lived name by {sense}"
                body, refs, own = by_name(li, lived, n, c if part == "lived" else None, sense)
                r = send(body, ask, t, n)
                if r:
                    r.update(right=r["choice"] is not None and r["choice"] == own, first=r["choice"] == refs[0], last=r["choice"] == refs[-1])
    return recs


def by_name(li, lived, n, c, sense):
    """An ask by the name n (c: its lived clip, None for a never-lived name). The offers are the life's 4 lived clips at
    second 8, in an order drawn per ask; they are the question's options, each naming one of the request's own clip assets."""
    offers = {f"offer-{x['clip']}": x for _, _, x in lived}
    rng = random.Random(f"{SEED}:{li}:{'g3g2' if c else 'N2'}:{sense}:{n}")
    own = f"offer-{c['clip']}" if c else None
    others = [x for x in offers if x != own]
    refs = ([own] if own else []) + rng.sample(others, 4 - (1 if own else 0))
    rng.shuffle(refs)
    body = {"model": "kelvin", "state": {"name": n, "sense": sense, **READ}, "assets": {ref: clip_asset(offers[ref]["path"]) for ref in refs},
            "questions": {"q": {"type": "choice", "instructions": f"Which clip is {n}?", "criteria": {x: None for x in refs}}}}
    return body, refs, own


def require_new(m, life, label, have, arm):
    """Before anything is lived: the memory must have lived nothing. It is asked the life's first ask by the name (the
    first lived thing's name, by the picture, exactly as it is asked later). A memory that lived this life before always
    answers it; a new memory stays silent. Otherwise the run stops here, before anything is lived."""
    lived, _, _ = plan(life, label, have, arm)
    t, n, c = lived[0]
    body, _, _ = by_name(life["life"], lived, n, c, "picture")
    common.require_new(m, f"sound-{arm}-life{life['life']}", body)


def lost_life(life, arm, why):
    """Route 2: a life with a lived clip that could not be fetched is not run; its 36 asks are lost."""
    out = []
    for i in range(THINGS):
        out += [{"arm": arm, "life": life["life"], "ask": a, "thing": f"thing {life['life']}.{i}", "status": None, "lost": why} for a in ASKS[:4]]
    for i in range(len(life["never"])):
        out += [{"arm": arm, "life": life["life"], "ask": a, "thing": f"stranger {life['life']}.{i}", "status": None, "lost": why} for a in ASKS[4:]]
    return out


def p(xs, q):
    xs = sorted(xs)
    return round(xs[min(len(xs) - 1, int(len(xs) * q))], 1) if xs else None


def summarise(recs):
    asks = [r for r in recs if r["ask"] != "tell"]
    per = {}
    for a in ASKS:
        rs = [r for r in asks if r["ask"] == a]
        done = [r for r in rs if r.get("status") == 200]
        per[a] = {"asks": len(rs), "answered_200": len(done), "right": sum(bool(r.get("right")) for r in done),
                  "silent": sum(r["silent"] for r in done), "answered": sum(r["choice"] is not None for r in done),
                  "answered_a_lived_name": sum(bool(r.get("lived_name")) for r in done),
                  "first_option": sum(bool(r.get("first")) for r in done), "last_option": sum(bool(r.get("last")) for r in done)}
    claims = {"sound to name": per["sound to name"]["right"], "picture to name": per["picture to name"]["right"],
              "name to clip by picture": per["name to clip by picture"]["right"], "name to clip by sound": per["name to clip by sound"]["right"],
              "never-lived thing answered with a lived name": per["never-lived thing by sound"]["answered_a_lived_name"] + per["never-lived thing by picture"]["answered_a_lived_name"],
              "never-lived name answered": per["never-lived name by picture"]["answered"] + per["never-lived name by sound"]["answered"]}
    holds = {k: (v >= BAR) for k, v in list(claims.items())[:4]}
    holds["never-lived thing answered with a lived name"] = claims["never-lived thing answered with a lived name"] <= NEVER_THING
    holds["never-lived name answered"] = claims["never-lived name answered"] <= NEVER_NAME
    tells = [r for r in recs if r["ask"] == "tell"]
    kinds = {"tell": tells, "by a sense": [r for r in asks if "to name" in r["ask"] or "never-lived thing" in r["ask"]],
             "by the name": [r for r in asks if "to clip" in r["ask"]], "a never-lived name": [r for r in asks if "never-lived name" in r["ask"]]}
    speed = {k: {"ms_p50": p([r["ms"] for r in v if "ms" in r], 0.5), "ms_p90": p([r["ms"] for r in v if "ms" in r], 0.9),
                 "bytes_sent_p50": p([r["bytes_sent"] for r in v if "bytes_sent" in r], 0.5),
                 "bytes_sent_max": max([r["bytes_sent"] for r in v if "bytes_sent" in r], default=None)} for k, v in kinds.items()}
    return {"asks": len(asks), "answered_200": sum(r.get("status") == 200 for r in asks),
            "lost": sum(r.get("status") is None for r in asks), "not_200": sum(r.get("status") not in (None, 200) for r in recs),
            "per_ask": per, "claims": claims, "holds": holds, "speed": speed}


def key(r):
    return (r["life"], r["ask"], r["thing"])


def as_thing(r, arm_plans):
    """An answer up to the name: a name is read as the thing it names in that arm; an offered clip stays itself."""
    if r.get("silent") or r.get("choice") is None:
        return ("silent" if r.get("silent") else None)
    names = arm_plans[r["life"]]
    return names.get(r["choice"], r["choice"])


def compare_arms(a, b, plans_a, plans_b):
    """How many asks two arms answered alike, up to the name (same thing or same offered clip, or both silent)."""
    rb = {key(r): r for r in b if r["ask"] != "tell"}
    equal = total = 0
    for r in a:
        if r["ask"] == "tell" or r.get("status") != 200 or rb.get(key(r), {}).get("status") != 200:
            continue
        total += 1
        equal += as_thing(r, plans_a) == as_thing(rb[key(r)], plans_b)
    return equal, total


def compare_recorded(arm, recs):
    rec = {key(r): r for r in json.load(open(os.path.join(HERE, "recorded.json")))["arms"][arm]}
    equal = total = 0
    differ = []
    for r in recs:
        if r["ask"] == "tell" or r.get("status") != 200 or key(r) not in rec:
            continue
        total += 1
        x = rec[key(r)]
        if (r["choice"], r["silent"]) == (x["choice"], x["silent"]):
            equal += 1
        else:
            differ.append({"life": r["life"], "ask": r["ask"], "thing": r["thing"], "now": r["choice"] or ("silent" if r["silent"] else None),
                           "recorded": x["choice"] or ("silent" if x["silent"] else None)})
    return equal, total, differ


def name_map(src, label, arm):
    """Per life, each name of the arm -> the thing it names (for comparing arms up to the name)."""
    out = {}
    for life in src["lives"]:
        lived, never, _ = plan(life, label, {}, arm)
        out[life["life"]] = {n: t for t, n, _ in lived + never}
    return out


def main():
    common.require_own_door("makes 738 requests of up to 21 MB, each taking seconds (about 40 minutes of a door's time)")
    ap = argparse.ArgumentParser(description="Test 3 · a sound, an object and its name")
    ap.add_argument("--side-by-side", type=int, default=1, help="how many memories are asked at the same time (each has its own key); "
                    "more than 1 sends several 20 MB uploads at once, and a door that reads one request at a time can then stall them")
    a = ap.parse_args()
    src, fetched, have, missing = the_clips()
    label = {c["clip"]: c["label"] for c in src["clips"]}
    m = common.Meridian("sound-object-name")
    route = fetched["route"]
    pinned = sum(1 for c in have.values() if c["fetched_sha256"] == c["sha256"])
    print(f"Test 3 · a sound, an object and its name · {m.url} · run record {m.dir}", flush=True)
    print(f"  the clips: route '{route}', {len(have)} of {len(src['clips'])} fetched, {pinned} equal to the recorded run's bytes", flush=True)
    jobs = []
    lost = []
    for arm in ARMS:
        for life in src["lives"]:
            gone = [c for c in life["lived"] if c not in have]
            if gone:
                lost += lost_life(life, arm, f"a lived clip could not be fetched ({', '.join(gone)}); the life is not run")
            else:
                jobs.append((arm, life))
    # every clip still holds the bytes fetch.py recorded, before any life is told
    for c in have.values():
        if common.sha256_of(c["path"]) != c["fetched_sha256"]:
            common.stop(f"{c['path']} changed since it was fetched; fetch it again")
    # every memory has lived nothing, before any life is told in any of them
    print(f"  checking that the {len(jobs)} memories are new", flush=True)
    with cf.ThreadPoolExecutor(max(1, a.side_by_side)) as pool:
        list(pool.map(lambda x: require_new(m, x[1], label, have, x[0]), jobs))

    def job(x):
        arm, life = x
        recs = run_life(m, life, label, have, arm)
        print(f"  {arm} names, life {life['life']}: {sum(r.get('status') == 200 for r in recs)} of {len(recs)} requests answered", flush=True)
        return arm, recs

    out = {arm: [r for r in lost if r["arm"] == arm] for arm in ARMS}
    with cf.ThreadPoolExecutor(max(1, a.side_by_side)) as pool:  # each memory has its own key
        for arm, recs in pool.map(job, jobs):
            out[arm] += recs
    for arm in ARMS:
        out[arm].sort(key=lambda r: (r["life"], 0))  # lives in order; within a life, the order they were sent
        common.write(m.dir, f"asks_{arm}.json", out[arm])
    s = {arm: summarise(out[arm]) for arm in ARMS}
    maps = {arm: name_map(src, label, arm) for arm in ARMS}
    same, same_of = compare_arms(out["real"], out["made-up"], maps["real"], maps["made-up"])
    recorded = {arm: compare_recorded(arm, out[arm]) for arm in ARMS}
    complete = all(s[arm]["lost"] == 0 and s[arm]["not_200"] == 0 for arm in ARMS)
    control_breaks = all(s["rotated"]["claims"][k] < BAR for k in list(RECORDED_CONTROL))
    result = {"side_by_side": max(1, a.side_by_side),
        "test": "a sound, an object and its name",
        "clips": {"route": route, "fetched": len(have), "of": len(src["clips"]), "equal_to_the_recorded_bytes": pinned, "not_fetched": missing},
        "complete": complete,
        "real names": s["real"], "made-up names": s["made-up"], "control: names rotated": s["rotated"],
        "made-up answered like real": {"equal": same, "of": same_of},
        "equal to the recorded run": {arm: {"equal": e, "of": t, "differ": d} for arm, (e, t, d) in recorded.items()},
        "claims hold (real names)": all(s["real"]["holds"].values()),
        "control breaks": control_breaks,
        "bars": {"each lived-thing ask": f">= {BAR} of 24", "never-lived thing answered with a lived name": f"<= {NEVER_THING} of 60",
                 "never-lived name answered": f"<= {NEVER_NAME} of 60", "control": f"each lived-thing ask < {BAR} of 24"},
        "recorded": {"real names": RECORDED, "control": RECORDED_CONTROL, "made-up answered like real": "216 of 216"},
    }
    common.write(m.dir, "result.json", result)
    md = markdown(result, m)
    where = common.publish(HERE, m.dir, result, md)
    print(md)
    print(f"\nresult: {where}/RESULT.md")
    if not complete:
        print(f"THIS RUN LOST ASKS ({sum(s[x]['lost'] for x in ARMS)} not sent, {sum(s[x]['not_200'] for x in ARMS)} not answered 200): "
              "it is shown, not judged; the bars are set for all 216 asks of each arm.")
        sys.exit(1)
    if not control_breaks:
        print("THE CONTROL DID NOT BREAK: with the names rotated, a lived-thing ask still reached 12 of 24. This run does not count.")
        sys.exit(1)


def markdown(r, m):
    real, made, ctl = r["real names"], r["made-up names"], r["control: names rotated"]
    yes = lambda b: "yes" if b else "**NO**"
    c = r["clips"]
    route = {"mirror": "the recorded run's exact bytes, from the mirror", "folder": "the recorded run's exact bytes, from a folder held locally",
             "youtube": "fetched from YouTube; the bytes are not the recorded run's"}[c["route"]]
    lines = ["# Test 3 · a sound, an object and its name · result", "",
             f"Address {m.url}, release {os.environ.get('MERIDIAN_RELEASE', 'not stated')}, run record `{os.path.relpath(m.dir, common.ROOT)}`.", "",
             f"The clips: route `{c['route']}` ({route}); {c['fetched']} of {c['of']} fetched, {c['equal_to_the_recorded_bytes']} equal to the recorded run's bytes.", "",
             "| | bar | real names | made-up names | control: names rotated | recorded (real names) |", "|---|---|---|---|---|---|"]
    rows = [("from the sound alone → its name", "sound to name", f"≥ {BAR} of 24"),
            ("from the picture alone → its name", "picture to name", f"≥ {BAR} of 24"),
            ("from the name → its clip by the picture (of 4)", "name to clip by picture", f"≥ {BAR} of 24"),
            ("from the name → its clip by the sound (of 4)", "name to clip by sound", f"≥ {BAR} of 24"),
            ("a never-lived thing answered with a lived name", "never-lived thing answered with a lived name", f"≤ {NEVER_THING} of 60"),
            ("a never-lived name answered", "never-lived name answered", f"≤ {NEVER_NAME} of 60")]
    for label, k, bar in rows:
        lines.append(f"| {label} | {bar} | **{real['claims'][k]}** | {made['claims'][k]} | {ctl['claims'][k]} | {RECORDED[k]} |")
    e = r["equal to the recorded run"]
    mu = r["made-up answered like real"]
    lines += ["",
              f"- **The claims hold (real names):** {yes(r['claims hold (real names)'])}.",
              f"- **The control breaks** (with the names rotated, each lived-thing ask falls below {BAR} of 24): {yes(r['control breaks'])}.",
              f"- **Made-up names answered like real names**, ask for ask (the same thing or the same clip, or silent in both): {mu['equal']} of {mu['of']}.",
              f"- **Equal to the recorded run**, ask for ask: real names {e['real']['equal']} of {e['real']['of']}, made-up names {e['made-up']['equal']} of {e['made-up']['of']}, control {e['rotated']['equal']} of {e['rotated']['of']}.",
              ]
    for arm, label in (("real", "real names"), ("made-up", "made-up names"), ("rotated", "control")):
        for d in e[arm]["differ"]:
            lines.append(f"  - {label}, life {d['life']}, {d['ask']}, {d['thing']}: now {d['now']}, recorded {d['recorded']}")
    lines += ["", "Of the asks by one sense (real names), the answers given and the silences:", ""]
    for k in ("sound to name", "picture to name"):
        x = real["per_ask"][k]
        lines.append(f"- {k}: {x['right']} right, {x['answered'] - x['right']} wrong, {x['silent']} silent (of {x['asks']})")
    sp = real["speed"]
    lines += ["", "| request (real names) | p50 ms | p90 ms | bytes sent p50 | bytes sent max |", "|---|---|---|---|---|"]
    for k, v in sp.items():
        lines.append(f"| {k} | {v['ms_p50']} | {v['ms_p90']} | {v['bytes_sent_p50']} | {v['bytes_sent_max']} |")
    lines += ["", "Times include the network between you and the address" + (
        ", and waiting while other memories of this run are asked." if r.get("side_by_side", 1) > 1 else " (one memory was asked at a time).")]
    if not r["complete"]:
        lines += ["", f"**This run lost asks** (real {real['lost'] + real['not_200']}, made-up {made['lost'] + made['not_200']}, control {ctl['lost'] + ctl['not_200']}): it is shown, not judged."]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
