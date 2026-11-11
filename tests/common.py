"""What every test shares: fetching its data pinned by sha256, the options of a question, and writing its result.
Python's standard library only.

KELVIN is asked through `meridian.Meridian` (one key per memory, from MERIDIAN_KEYS_FILE). Every test names its memories
in a list MEMORIES in its run.py; `python3 tests/keys_needed.py` prints all of them, so the keys file can be filled.
"""
import hashlib
import json
import math
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from meridian import Meridian, answer_of, stop  # noqa: E402,F401


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def fetch(url, dest, sha256, quiet=False):
    """Download `url` to `dest` once and check it against its pinned sha256. A file already there is checked, not
    fetched again. A file that does not match is removed and never used."""
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    if not os.path.exists(dest):
        if not quiet:
            print(f"  fetching {url}", flush=True)
        req = urllib.request.Request(url, headers={"User-Agent": "kelvin-meridian-tests"})
        tmp = dest + ".part"
        with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as f:
            for block in iter(lambda: r.read(1 << 20), b""):
                f.write(block)
        os.replace(tmp, dest)
    got = sha256_of(dest)
    if got != sha256:
        os.remove(dest)
        stop(f"{dest}: sha256 {got} is not the pinned {sha256}; the file was removed and is not used")
    return dest


def fetch_all(test_dir, quiet=False):
    """Every file named in the test's sources.json, into the test's data/ folder, each checked by its sha256.
    Returns {name: local path}."""
    sources = json.load(open(os.path.join(test_dir, "sources.json")))
    data = os.path.join(test_dir, "data")
    return {s["name"]: fetch(s["url"], os.path.join(data, s["name"]), s["sha256"], quiet) for s in sources["files"]}


def options(q):
    """A question's options, as the systemone standard defines them."""
    t = q.get("type")
    if t == "choice":
        return list(q["criteria"].keys())
    if t == "score":
        return [str(i) for i in range(len(q["criteria"]))]
    if t == "noul":
        return ["true", "false"]
    return []


def require_own_door(what):
    """A test that lives a lot in one request holds the whole door for that time, and a tester's door is shared. Until a
    limit for tester doors is set, such a test runs only on a door of one's own: MERIDIAN_OWN_DOOR=1 says it is."""
    if os.environ.get("MERIDIAN_OWN_DOOR") != "1" and os.environ.get("MERIDIAN_LOCAL") != "1":
        stop(f"This test {what}, and a door answers one request at a time: on a shared tester door it would stop every "
                 f"other tester for that long. Run it only on a door of your own, and say so with MERIDIAN_OWN_DOOR=1.")


def require_new(m, memory, body, headers=None):
    """A run must start from a memory that has lived nothing: a second run into the same memory would add to the first
    and change every answer. Asked one of the test's own questions before anything is lived, a new memory stays silent
    on every question; if it answers anything, the run stops here and names the memory."""
    s, a, raw, ms, _ = m.ask(body, memory=memory, headers=headers)
    if s != 200:
        stop(f"{memory}: the first question answered {s}: {raw[:300]!r}")
    answered = [q for q, x in ((a or {}).get("answers") or {}).items() if not (x or {}).get("silent")]
    if answered:
        stop(f"the memory '{memory}' has already lived something (it answered {', '.join(answered)} instead of staying "
                 f"silent). Every run needs new memories, so a second run never adds to the first: use new keys.")
    require_keeps(m)


_KEEPS_CHECKED = set()


def require_keeps(m):
    """The counterpart of `require_new` (0.0.6): the address must keep what a request teaches for the next request. Where
    each request names its memory (a customer unit), one made-up fact is told in a memory of its own,
    `meridian-tests-keeps-check`, and asked in a new request; if it is not answered, the run stops here with what to do,
    instead of running every test into silence. On a tester pool the key holds the memory, so there is nothing to check.
    Once a run."""
    if m.naming != "header" or id(m) in _KEEPS_CHECKED or os.environ.get("MERIDIAN_LOCAL") == "1":
        return
    _KEEPS_CHECKED.add(id(m))
    import random as _r
    tag = "".join(_r.choice("bcdfghjklmnpqrstvwz") for _ in range(10))
    subject, obj = f"keeps-{tag}", f"kept-{tag}"
    q = {"keeps": {"type": "choice", "criteria": {obj: None, "nobody": None}}}
    s1, _, raw1, _, _ = m.ask({"model": "kelvin", "state": {"facts": [{"subject": subject, "relation": "keeps", "object": obj}]}, "questions": q},
                              memory="meridian-tests-keeps-check")
    s2, a2, raw2, _, _ = m.ask({"model": "kelvin", "state": {"subject": subject}, "questions": q}, memory="meridian-tests-keeps-check")
    got = ((a2 or {}).get("answers") or {}).get("keeps") or {}
    if s1 != 200 or s2 != 200 or got.get("silent") or got.get("choice") != obj:
        stop("this address does not keep what a request teaches for the next request: a fact told in one request was "
             f"not answered in the next (answers {s1}, {s2}). On a KELVIN Meridian unit every request must name its memory "
             "(the header KELVIN-Memory), which this client does; if your address is a tester pool, set MERIDIAN_MEMORY=key. "
             "Nothing of the test was taught.")


def sign_p(gained, lost):
    """One-sided sign test: the chance of at least `gained` wins among `gained + lost` paired differences, if each were a
    coin toss."""
    n = gained + lost
    return 1.0 if n == 0 else sum(math.comb(n, i) for i in range(gained, n + 1)) / 2 ** n


def fmt_p(p):
    """A sign test's p as written in a result; one too small for a float is written as below 1e-300, never as 0."""
    return "< 1e-300" if p == 0 else f"= {p:.2g}"


def control_breaks(kelvin_right, control_right):
    """The rule every control follows: on the same asks, KELVIN is right more often where the control is wrong than the
    other way round, paired, one-sided sign test p < 0.05. Returns (breaks, gained, lost, p)."""
    g = sum(1 for k, c in zip(kelvin_right, control_right) if k and not c)
    l = sum(1 for k, c in zip(kelvin_right, control_right) if c and not k)
    p = sign_p(g, l)
    return p < 0.05, g, l, p


def write(run_dir, name, obj):
    path = os.path.join(run_dir, name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    return path


def sent_again(run_dir):
    """How many requests of a run were sent again because their upload broke before the body was whole (the record
    keeps every broken attempt with "sent_again": true)."""
    path = os.path.join(run_dir, "requests.jsonl")
    if not os.path.exists(path):
        return 0
    return sum(1 for line in open(path) if '"sent_again": true' in line)


def publish(test_dir, run_dir, result, markdown):
    """A finished run's result into the test's own folder (results/), naming the run record it came from. A local check
    (MERIDIAN_LOCAL=1) stays in its run record and is never published. Every result states how many requests were sent
    again after a broken upload."""
    n = sent_again(run_dir)
    result = dict(result, requests_sent_again_after_a_broken_upload=n)
    # 0.0.6: the run record names the memories the run used (before: the keys in the keys file) and how each was named
    try:
        lines = [json.loads(l) for l in open(os.path.join(run_dir, "requests.jsonl"))]
        used = sorted({l["memory"] for l in lines if l.get("memory") and l["memory"] != "meridian-tests-keeps-check"})
        named = sorted({l.get("memory_named_by") for l in lines if l.get("status") == 200 and l.get("memory_named_by")})
        meta = json.load(open(os.path.join(run_dir, "run.json")))
        meta.pop("memories", None)
        meta["memories_used"] = used
        meta["memory_named_by"] = named
        json.dump(meta, open(os.path.join(run_dir, "run.json"), "w"), indent=1)
    except (OSError, ValueError, KeyError):
        pass
    markdown = (markdown.rstrip() + f"\n\nRequests sent again because their upload broke before the body was whole "
                f"(the door never received them whole): {n}. Each broken attempt is in the run record.")
    if os.environ.get("MERIDIAN_LOCAL") == "1":
        with open(os.path.join(run_dir, "RESULT.md"), "w") as f:
            f.write(markdown.rstrip() + "\n")
        return run_dir
    out = os.path.join(test_dir, "results")
    os.makedirs(out, exist_ok=True)
    result = dict(result, run_record=os.path.relpath(run_dir, ROOT))
    with open(os.path.join(out, "result.json"), "w") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    with open(os.path.join(out, "RESULT.md"), "w") as f:
        f.write(markdown.rstrip() + "\n")
    return out
