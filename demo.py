#!/usr/bin/env python3
"""KELVIN Meridian in eight short scenes, against your own tester address and key.

    export MERIDIAN_URL=https://<your address>     # given with your key
    export MERIDIAN_KEY=...                                         # your key; never printed
    python3 demo.py --autoplay          # runs by itself, a pause before each scene (for filming)
    python3 demo.py --step              # waits for Enter before each scene

Optional: MERIDIAN_KEY_2, a second tester's key, shows that the second memory never sees the first one's facts.
Every run is recorded in runs/<date>-demo/ (the answers exactly as the server sent them; the keys never).
Each run invents its own names, so a run always starts from something KELVIN has not been told.

(For us: a scene that ever shows a photo shows its credit line with it, the author's name from the photo's page and its
licence, as in the marketing video and the whitepaper.)
"""
import argparse
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meridian import Meridian, answer_of  # noqa: E402

BOLD, DIM, END = "\033[1m", "\033[2m", "\033[0m"
SURNAMES = ["kestrel", "varo", "lindqvist", "okafor", "marsh", "tavernier", "quill", "brandt", "seyrek", "holloway", "ibarra", "nakamura"]


def caption(n, text, args):
    print(f"\n{BOLD}{'─' * 72}\n Scene {n} · {text}\n{'─' * 72}{END}")
    if args.step:
        input(f"{DIM}  (Enter){END}")
    else:
        time.sleep(args.pause)


def show(label, status, answer, ms, question=None):
    if question:
        choice, conf, silent = answer_of(answer, question)
        said = "— silent: KELVIN does not know" if silent else f"{choice}   (confidence {conf})"
        print(f"  {label}: {BOLD}{said}{END}   {DIM}[{status}, {ms:.0f} ms]{END}")
    else:
        detail = (answer or {}).get("detail") or (answer or {}).get("error") or answer
        print(f"  {label}: {BOLD}{status}{END} {detail}   {DIM}[{ms:.0f} ms]{END}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--autoplay", action="store_true", help="run by itself, with a pause before each scene")
    ap.add_argument("--step", action="store_true", help="wait for Enter before each scene")
    ap.add_argument("--pause", type=float, default=4.0, help="seconds before each scene in autoplay (default 4)")
    args = ap.parse_args()
    if not (args.autoplay or args.step):
        args.autoplay = True
    m = Meridian("demo")
    if os.environ.get("MERIDIAN_KEY_2"):
        m.keys["second"] = os.environ["MERIDIAN_KEY_2"]
    rng = random.Random()
    person = f"anna-{rng.choice(SURNAMES)}-{rng.randrange(1000, 9999)}"
    stranger = f"lena-{rng.choice(SURNAMES)}-{rng.randrange(1000, 9999)}"
    mother = {"mother": {"type": "choice", "criteria": {"maria": None, "nobody": None}}}
    times = []

    caption(1, "Your address and your key (the key stays hidden)", args)
    print(f"  address: {m.url}\n  key:     set in MERIDIAN_KEY (not shown)")
    s, a, _, ms, _ = m.models()
    show("GET /v1/models", s, a, ms)

    caption(2, f"Who is {person}'s mother? Nothing has been taught yet.", args)
    s, a, _, ms, _ = m.ask({"model": "kelvin", "state": {"subject": person}, "questions": mother})
    show("answer", s, a, ms, "mother")
    times.append(ms)

    caption(3, f"Teach one fact: {person}'s mother is maria.", args)
    fact = {"subject": person, "relation": "mother", "object": "maria"}
    s, a, _, ms, _ = m.ask({"model": "kelvin", "state": {"facts": [fact]}, "questions": mother})
    print(f"  taught: {fact}   {DIM}[{s}, {ms:.0f} ms]{END}")
    times.append(ms)

    caption(4, "Ask again, in a new request that does not carry the fact.", args)
    s, a, _, ms, _ = m.ask({"model": "kelvin", "state": {"subject": person}, "questions": mother})
    show("answer", s, a, ms, "mother")
    times.append(ms)

    caption(5, f"A name never taught: {stranger}. KELVIN does not guess.", args)
    s, a, _, ms, _ = m.ask({"model": "kelvin", "state": {"subject": stranger}, "questions": mother})
    show("answer", s, a, ms, "mother")
    times.append(ms)

    caption(6, "Your memory is yours.", args)
    if "second" in m.keys:
        s, a, _, ms, _ = m.ask({"model": "kelvin", "state": {"subject": person}, "questions": mother}, memory="second")
        show("the same question, a second tester's memory", s, a, ms, "mother")
    else:
        s, a, _, ms, _ = m.ask({"model": "kelvin", "state": {"subject": person}, "questions": mother}, headers={"KELVIN-Memory": "someone-elses-memory"})
        show("naming another memory", s, a, ms)
    times.append(ms)

    caption(7, "Several facts and several questions in one request.", args)
    facts = [{"subject": person, "relation": "father", "object": "tomas"}, {"subject": person, "relation": "city", "object": "lisbon"}]
    s, a, _, ms, _ = m.ask({"model": "kelvin", "state": {"facts": facts}, "questions": mother})
    print(f"  taught: {len(facts)} facts   {DIM}[{s}, {ms:.0f} ms]{END}")
    qs = {"mother": mother["mother"], "father": {"type": "choice", "criteria": {"tomas": None, "nobody": None}},
          "city": {"type": "choice", "criteria": {"lisbon": None, "oslo": None, "nobody": None}},
          "employer": {"type": "choice", "criteria": {"acme": None, "nobody": None}}}
    s, a, _, ms, _ = m.ask({"model": "kelvin", "state": {"subject": person}, "questions": qs})
    for q in qs:
        show(q, s, a, ms, q)
    times.append(ms)

    caption(8, "What it took", args)
    times.sort()
    print(f"  {len(times)} answers, time per request (your network included): median {times[len(times) // 2]:.0f} ms, slowest {times[-1]:.0f} ms")
    print(f"  the run's record: {m.dir}")


if __name__ == "__main__":
    main()
