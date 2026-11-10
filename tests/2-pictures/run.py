#!/usr/bin/env python3
"""Test 2 · A picture: this one, else its kind.

    python3 tests/2-pictures/run.py

KELVIN lives 500 photos and 500 documents, one picture a request, each told with its kind. Then it is asked, one picture
a request, "What kind of picture is it?" over photo / document / screen:
- 24 of the lived pictures again (12 photos, 12 documents): it should answer the kind it was told for that picture;
- 30 photos and 30 documents it never saw: it should answer their kind;
- 30 screens (rendered web pages), a kind it was never told about: it should never answer "screen".
Every request carries state.read = "staircase" (the customer handbook's read for the kind of a picture): KELVIN first
looks among the lived pictures for this very one, and answers what it was told about it; if it finds none, it answers
with the lived kind the picture resembles most.

The control, in its own memory: the same 1 000 pictures, every photo told "document" and every document told "photo",
then the same 114 asks. It must fall below 22 of 24 on the lived pictures and to at most 30 of 60 on the unseen ones,
or the test does not count.

The pictures are not in this repository: pictures.json names each one with its source, licence and sha256. They are
fetched into data/ on the first run, each checked against its sha256, and data/ATTRIBUTION.md names their authors and
licences. A picture that cannot be fetched, or does not match, stops the run with its name; none is replaced.

Both memories must be new: before anything is told, each is asked one picture, and the run stops unless it is silent.

Needs: MERIDIAN_URL and MERIDIAN_KEYS_FILE with the two memories below. Python's standard library only.
"""
import concurrent.futures as cf
import http.client
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common  # noqa: E402
import meridian  # noqa: E402  (common puts the repository's root on the path)

MEMORIES = ["pictures", "pictures-swapped"]
# The read for the kind of a picture, as the customer handbook names it; sent on every request, the tell and the ask.
READ = {"read": "staircase"}
# Fixes each question's option order (shuffled per picture), as in the run that decided this test.
SEED = 2097911
ROWS = "https://datasets-server.huggingface.co/rows"
ROW_PAUSE = 2.0  # seconds between two calls to the rows service, so it is not asked too fast
# What must hold (decided before the first run).
AGAIN_AT_LEAST = 22   # of 24 lived pictures asked again: their kind
UNSEEN_AT_LEAST = 46  # of 60 unseen pictures: their kind
CONTROL_AGAIN_BELOW = 22   # the control must fall below 22 of 24 ...
CONTROL_UNSEEN_AT_MOST = 30  # ... and to at most 30 of 60
# What KELVIN answered when this test was decided (2026-11-04), on an earlier release.
DECIDED = {"again": {"right": 24, "of": 24}, "unseen": {"right": 50, "of": 60},
           "screens": {"photo": 4, "document": 21, "screen": 0, "silent": 5, "of": 30},
           "control": {"again": {"right": 0, "of": 24}, "unseen": {"right": 10, "of": 60}}}


# ---------------------------------------------------------------------------------------------------------------------
# The pictures: fetched from their sources, each checked by its sha256
# ---------------------------------------------------------------------------------------------------------------------

def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "kelvin-meridian-tests"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def _tries(fn, tries=8):
    """Network faults only (a busy service, a cut connection, a timeout) are tried again, slower each time; a sha256 that
    does not match is never tried again (common.fetch stops the run). The rows service is often briefly busy (429, 502,
    503, 504): then its Retry-After is waited, or 30 s, 60 s, … (at most about 14 minutes for one picture)."""
    for i in range(tries):
        try:
            return fn()
        except (urllib.error.URLError, http.client.HTTPException, TimeoutError, ConnectionError) as e:
            if i + 1 == tries:
                raise
            busy = isinstance(e, urllib.error.HTTPError) and e.code in (429, 502, 503, 504)
            after = e.headers.get("Retry-After") if busy and e.headers else None
            time.sleep(float(after) if after and after.isdigit() else 30 * (i + 1) if busy else 5 * (i + 1))


def _row_image(src, offset):
    """The address of one row's image, from the Hugging Face dataset viewer's rows service (signed, valid for a while)."""
    q = urllib.parse.urlencode({"dataset": src["dataset"], "config": src["config"], "split": src["split"], "offset": offset, "length": 1})
    url = json.loads(_get(f"{ROWS}?{q}"))["rows"][0]["row"]["image"]["src"]
    if f"/--/{src['revision']}/--/" not in url:
        print(f"  note: the rows service serves {src['dataset']} at another revision than {src['revision'][:8]}; "
              "the picture is still used only if its sha256 matches", flush=True)
    return url


def fetch_pictures(listing):
    """Every picture of pictures.json into data/<kind>/, each checked against its sha256. Returns {id: local path}."""
    pics, sources = listing["pictures"], listing["sources"]
    paths, fetched = {}, 0
    for it in pics:
        dest = os.path.join(HERE, "data", it["kind"], it["file"])
        there = os.path.exists(dest)
        try:
            if it["kind"] == "photo" or there:
                url = it.get("url", "")  # a file already there is only checked, not fetched again
                _tries(lambda: common.fetch(url, dest, it["sha256"], quiet=True))
            else:
                time.sleep(ROW_PAUSE)
                _tries(lambda: common.fetch(_row_image(sources[it["kind"]], it["offset"]), dest, it["sha256"], quiet=True))
        except Exception as e:  # noqa: BLE001 (any fault: the picture is named and the run stops)
            where = it.get("url") or f"{sources[it['kind']]['dataset']} row {it['offset']}"
            common.stop(f"the picture {it['id']} ({where}) could not be fetched: {e}\nThe run stops; no other picture is put in its place.")
        fetched += not there
        if fetched and not there and fetched % 100 == 0:
            print(f"  {fetched} pictures fetched", flush=True)
        paths[it["id"]] = dest
    if fetched:
        print(f"  {fetched} pictures fetched, {len(pics)} checked by their sha256", flush=True)
    write_attribution(listing)
    return paths


def write_attribution(listing):
    s = listing["sources"]
    by = {k: [p for p in listing["pictures"] if p["kind"] == k] for k in ("photo", "document", "screen")}
    lines = ["# The pictures in this folder: their sources, authors and licences", "",
             "Fetched by `tests/2-pictures/run.py` from the sources below; nothing of them is in the repository.",
             "Each file was checked against the sha256 in `pictures.json`. The pictures are used unchanged.", "",
             f"## Photos ({len(by['photo'])}): {s['photo']['name']}", "",
             f"From the COCO dataset ({s['photo']['home']}), each from its own address at images.cocodataset.org. "
             f"{s['photo']['terms']} Each photo is under the licence named beside it, as COCO states it. "
             "COCO records each photo's page on Flickr, where its author is named; that page is given beside it.", "",
             "| file | licence | the photo on Flickr (its author) |", "|---|---|---|"]
    lines += [f"| {p['file']} | [{p['licence']}]({p['licence_url']}) | {p['flickr_page']} |" for p in by["photo"]]
    for k, title in (("document", "Documents"), ("screen", "Screens")):
        x = s[k]
        lines += ["", f"## {title} ({len(by[k])}): {x['name']}", "",
                  f"From the dataset [{x['dataset']}]({x['home']}) at revision `{x['revision']}` (config `{x['config']}`, split "
                  f"`{x['split']}`), licensed [{x['licence']}]({x['licence_url']}). Each file is one row of the dataset, its "
                  "image as the Hugging Face dataset viewer serves it.", "", "| file | row |", "|---|---|"]
        lines += [f"| {p['file']} | {p['offset']} |" for p in by[k]]
    with open(os.path.join(HERE, "data", "ATTRIBUTION.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------------------------------------------------
# Telling and asking
# ---------------------------------------------------------------------------------------------------------------------

def question(seed):
    """The one question, its options in an order shuffled per picture by the seed."""
    opts = ["photo", "document", "screen"]
    random.Random(seed).shuffle(opts)
    return {"kind": {"type": "choice", "instructions": "What kind of picture is `picture`?", "criteria": {o: None for o in opts}}}


def picture(path):
    """A picture as the API's image asset, with its format named as the standard's form does."""
    with open(path, "rb") as f:
        png = f.read(8) == b"\x89PNG\r\n\x1a\n"
    a = meridian.asset(path, "image")
    return {"type": "image", "format": "png" if png else "jpg", "data_base64": a["data_base64"]}


def ask_body(it, paths):
    ref = f"pic-{it['id']}"
    return {"model": "kelvin", "state": {"picture": ref, **READ}, "assets": {ref: picture(paths[it["id"]])},
            "questions": question(f"{SEED}:ask:{it['id']}")}


def run_memory(m, memory, lived, told_as, asks, paths):
    """Tell every lived picture once, then ask each picture of `asks`, in this order, in one memory."""
    tells = []
    for n, it in enumerate(lived):
        ref = f"pic-{it['id']}"
        body = {"model": "kelvin", "state": {"pictures": [{"picture": ref, "kind": told_as[it["id"]]}], **READ},
                "assets": {ref: picture(paths[it["id"]])}, "questions": question(f"{SEED}:tell:{it['id']}")}
        s, a, raw, ms, sent = m.ask(body, memory=memory)
        if s != 200:
            common.stop(f"{memory}: telling {it['id']} answered {s}: {raw[:300]!r}")
        tells.append({"id": it["id"], "told": told_as[it["id"]], "ms": ms, "bytes_sent": sent})
        if (n + 1) % 250 == 0:
            print(f"  {memory}: {n + 1} of {len(lived)} pictures told", flush=True)
    out = []
    for part, it in asks:
        body = ask_body(it, paths)
        q = body["questions"]
        s, a, raw, ms, sent = m.ask(body, memory=memory)
        choice, confidence, silent = meridian.answer_of(a, "kind") if s == 200 else (None, None, False)
        out.append({"part": part, "id": it["id"], "kind": it["kind"], "told": told_as.get(it["id"]), "status": s,
                    "choice": choice, "confidence": confidence, "silent": silent, "options": list(q["kind"]["criteria"]),
                    "ms": round(ms, 1), "bytes_sent": sent, "bytes_received": len(raw)})
        if s != 200:
            print(f"  {memory}: asking {it['id']} answered {s}: {raw[:200]!r}", flush=True)
    print(f"  {memory}: {len(lived)} told, {len(out)} asked", flush=True)
    return {"tells": tells, "asks": out}


def count(asks):
    def part(p):
        rs = [r for r in asks if r["part"] == p]
        return {"of": len(rs), "right": sum(r["choice"] == r["kind"] for r in rs), "silent": sum(r["silent"] for r in rs),
                "wrong": sum(r["choice"] is not None and r["choice"] != r["kind"] for r in rs),
                "no_answer": sum(r["status"] != 200 for r in rs), "as_told": sum(r["told"] is not None and r["choice"] == r["told"] for r in rs)}
    screens = [r for r in asks if r["part"] == "screen"]
    return {"again": part("again"), "unseen": part("unseen"),
            "screens": {"of": len(screens), **{k: sum(r["choice"] == k for r in screens) for k in ("photo", "document", "screen")},
                        "silent": sum(r["silent"] for r in screens), "no_answer": sum(r["status"] != 200 for r in screens)}}


def pct(xs, p):
    xs = sorted(xs)
    return round(xs[min(int(len(xs) * p), len(xs) - 1)], 1) if xs else None


def main():
    common.require_own_door("makes about 2 230 requests, close together (about 9 minutes of a door's time)")
    listing = json.load(open(os.path.join(HERE, "pictures.json")))
    print("Test 2 · a picture: this one, else its kind · fetching and checking the pictures", flush=True)
    paths = fetch_pictures(listing)
    pics = listing["pictures"]
    lived = [p for p in pics if p["role"] == "lived"]  # photos, then documents, in the list's order
    asks = ([("again", p) for p in lived if p.get("asked_again")] + [("unseen", p) for p in pics if p["role"] == "unseen"] +
            [("screen", p) for p in pics if p["role"] == "screen"])
    told = {p["id"]: p["kind"] for p in lived}
    swapped = {i: {"photo": "document", "document": "photo"}[k] for i, k in told.items()}
    m = common.Meridian("pictures")
    print(f"Test 2 · {m.url} · run record {m.dir}", flush=True)
    for memory in MEMORIES:  # both memories must have lived nothing yet: the first ask, sent before anything is told, is silent
        common.require_new(m, memory, ask_body(asks[0][1], paths))
    print(f"  living {len(lived)} pictures in each of {MEMORIES} (one picture a request), then asking {len(asks)}", flush=True)
    with cf.ThreadPoolExecutor(2) as pool:  # each memory has its own key
        k = pool.submit(run_memory, m, "pictures", lived, told, asks, paths)
        c = pool.submit(run_memory, m, "pictures-swapped", lived, swapped, asks, paths)
        k, c = k.result(), c.result()
    common.write(m.dir, "answers_pictures.json", k["asks"])
    common.write(m.dir, "answers_pictures-swapped.json", c["asks"])
    rk, rc = count(k["asks"]), count(c["asks"])
    holds = {"again": rk["again"]["right"] >= AGAIN_AT_LEAST, "unseen": rk["unseen"]["right"] >= UNSEEN_AT_LEAST,
             "screen_never_named": rk["screens"]["screen"] == 0}
    breaks = rc["again"]["right"] < CONTROL_AGAIN_BELOW and rc["unseen"]["right"] <= CONTROL_UNSEEN_AT_MOST
    tell_ms = [t["ms"] for t in k["tells"]]
    ask_ms = [a["ms"] for a in k["asks"]]
    result = {"test": "a picture: this one, else its kind", "read": READ, "seed": SEED,
              "kelvin": rk, "control_swapped": rc,
              "predictions": {"again": f"at least {AGAIN_AT_LEAST} of 24", "unseen": f"at least {UNSEEN_AT_LEAST} of 60", "screen_never_named": "0 of 30"},
              "holds": holds, "control": f"below {CONTROL_AGAIN_BELOW} of 24 and at most {CONTROL_UNSEEN_AT_MOST} of 60", "control_breaks": breaks,
              "when_decided": DECIDED,
              "times_ms": {"tell_p50": pct(tell_ms, 0.5), "tell_p90": pct(tell_ms, 0.9), "ask_p50": pct(ask_ms, 0.5), "ask_p90": pct(ask_ms, 0.9)},
              "bytes": {"tell_sent_p50": pct([t["bytes_sent"] for t in k["tells"]], 0.5), "ask_sent_p50": pct([a["bytes_sent"] for a in k["asks"]], 0.5),
                        "answer_received_p50": pct([a["bytes_received"] for a in k["asks"]], 0.5)}}
    common.write(m.dir, "result.json", result)
    md = markdown(result, m)
    out = common.publish(HERE, m.dir, result, md)
    print(md)
    print(f"\nresult: {out}/RESULT.md" if out != m.dir else f"\nresult: {m.dir}/result.json (a local check, not published)")
    if not breaks:
        print("THE CONTROL DID NOT BREAK: this run does not count.")
        sys.exit(1)


def markdown(r, m):
    k, c, d = r["kelvin"], r["control_swapped"], r["when_decided"]
    yes = lambda b: "yes" if b else "**no**"
    s = k["screens"]
    lines = ["# Test 2 · a picture: this one, else its kind · result", "",
             f"Address {m.url}, release {os.environ.get('MERIDIAN_RELEASE', 'not stated')}, run record `{os.path.relpath(m.dir, common.ROOT)}`.", "",
             "KELVIN lived 500 photos and 500 documents, each told with its kind, then was asked the kind of 114 pictures, one at a time.", "",
             "| asked | what must hold | KELVIN | holds | control (kinds swapped) | when decided |", "|---|---|---|---|---|---|",
             f"| 24 lived pictures again | their kind, at least {AGAIN_AT_LEAST} | **{k['again']['right']} of 24** | {yes(r['holds']['again'])} | {c['again']['right']} of 24 | {d['again']['right']} of 24 |",
             f"| 60 unseen photos and documents | their kind, at least {UNSEEN_AT_LEAST} | **{k['unseen']['right']} of 60** | {yes(r['holds']['unseen'])} | {c['unseen']['right']} of 60 | {d['unseen']['right']} of 60 |",
             f"| 30 screens, a kind never told | never \"screen\" | **{s['screen']} of 30** \"screen\" | {yes(r['holds']['screen_never_named'])} | {c['screens']['screen']} of 30 | {d['screens']['screen']} of 30 |", "",
             f"**The screens, plainly:** KELVIN was never told what a screen is. Of the 30 it said \"photo\" for {s['photo']}, \"document\" for "
             f"{s['document']} and \"screen\" for {s['screen']}, and stayed silent (\"I don't know\") for {s['silent']}"
             + (". Most screens got the nearest lived kind instead of silence." if s["silent"] * 2 < s["of"] else ".")
             + f" When decided: {d['screens']['photo']} photo, {d['screens']['document']} document, {d['screens']['silent']} silent.", "",
             f"**The unseen pictures:** {k['unseen']['right']} of 60 got their kind, {k['unseen']['wrong']} the other kind, "
             f"{k['unseen']['silent']} silence.", "",
             f"**The lived pictures asked again** got the kind KELVIN was told for that very picture {k['again']['as_told']} of 24 times. "
             f"In the control, where each was told the other kind, it answered that other kind {c['again']['as_told']} of 24 times.", "",
             f"**The control** (every photo told \"document\" and every document told \"photo\", in its own memory) must fall {r['control']}: "
             f"{c['again']['right']} of 24 and {c['unseen']['right']} of 60, so it {'breaks' if r['control_breaks'] else '**does not break: this run does not count**'}.", ""]
    no = k["again"]["no_answer"] + k["unseen"]["no_answer"] + k["screens"]["no_answer"]
    if no:
        lines += [f"{no} asks got no answer (a status other than 200); they are in the run record.", ""]
    t, b = r["times_ms"], r["bytes"]
    lines += [f"Times: a tell {t['tell_p50']} / {t['tell_p90']} ms, an ask {t['ask_p50']} / {t['ask_p90']} ms (p50 / p90), including the network "
              f"between you and the address. Sent: a tell {b['tell_sent_p50'] / 1e6:.2f} MB, an ask {b['ask_sent_p50'] / 1e6:.2f} MB "
              f"(the picture as base64, p50); an answer {b['answer_received_p50']:.0f} bytes."]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
