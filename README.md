<div align="center">

# KELVIN Meridian · tests

### Learns from one experience. Answers from what it kept. Says so when it was never told.

<p>
  <img src="https://img.shields.io/badge/license-Apache--2.0-blue.svg" alt="License: Apache-2.0">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10 or newer">
  <img src="https://img.shields.io/badge/dependencies-standard%20library-brightgreen.svg" alt="Dependencies: the standard library">
  <img src="https://img.shields.io/badge/tests-7%20passed%20%C2%B7%207%20controls%20broke-brightgreen.svg" alt="7 tests passed, 7 controls broke">
  <img src="https://img.shields.io/badge/release%20tested-5ddaa4fc-lightgrey.svg" alt="Release tested: 5ddaa4fc">
</p>

**Get a key, run one command, read every answer.**

</div>

---

KELVIN Meridian is an API. Your programs teach KELVIN at an address of your own, with a key only they hold, and ask it
later. It keeps what it was told, answers from what it kept, and where it was told nothing it says so instead of
guessing. It needs no training run and no graphics unit.

This repository holds:
- **a demo** that runs by itself, for a first look;
- **seven tests** that anyone with a tester key can run, with the same data and the same controls we used;
- **our own result of each test** on the published release `5ddaa4fc`, with every request and every answer recorded.

## Seven claims, each with a control that must break

Every test also runs a **control**: the same test in a memory of its own, with the thing that should matter taken
away. KELVIN must clearly beat it, or the run does not count, and the script says so.

| | What KELVIN does | Our result, release `5ddaa4fc` | The control that must break |
|---|---|---|---|
| [**1 · Typed decisions**](tests/1-typed-decisions/) | Its only teaching is 300 solved cases per business area. It then answers 100 new cases, scored by the dataset's own scorer. | accuracy **0.706** · KL 0.162 · Brier 0.089 · ECE 0.131 | the answers shuffled: 0.508 |
| [**2 · A picture**](tests/2-pictures/) | It is told 1 000 photos and documents, each with its kind (on the server's own count it kept 998: two of them give it nothing to keep). It knows each again, and names the kind of pictures it never saw. | **24 of 24** known as told · **50 of 60** unseen named by kind | the kinds swapped: 0 of 24 · 10 of 60 |
| [**3 · A sound, an object and its name**](tests/3-sound-object-name/) | Each thing is lived once, an 8-second clip with its name. It names it from the sound or the picture alone, and picks its clip by the name. | clip by name **23 of 24** · sound → name **14 of 24** · a never-heard name answered **0 of 60** · made-up names answered as real ones **216 of 216** | the names rotated: 0 · 0 · 0 · 1 of 24 |
| [**4 · Intent**](tests/4-intent/) | It hears 15 100 requests once each: 15 000 told with their intent (150 intents), 100 told as fitting none. Then it names the intent of new ones, or "none of the above". | **3 821 of 4 500** (0.849) · "none of the above" 337 of 1 000 | the intents shuffled: 19 of 4 500 |
| [**5 · When to call a tool**](tests/5-when-to-call-a-tool/) | For requests of families it never met, it chooses: call a tool, ask for what is missing, or say it cannot. | **816 of 1 216** (0.671) | the reactions shuffled: 430 of 1 216 |
| [**6 · Remember**](tests/6-remember/) | It is told 346 real facts. Later, in requests that do not carry them, it is asked each one. | **345 of 345** · asked twice, the same bytes · never told: 332 of 332 silent | the facts shuffled: right against the truth 4 of 345 |
| [**7 · "I don't know"**](tests/7-i-dont-know/) | Asked what it was never told, with "none of the above" offered, it says so. | **558 of 558** right · 389 of 389 it could not know: "none of the above" | nothing told: 0 of 169 |

Each number stands in the test's `results/RESULT.md`, from our own run. [`REPRODUCE.md`](REPRODUCE.md) lists every
number this README cites, with its run record and its command.

## Quick start

```sh
git clone https://github.com/pelloran-inc/kelvin-meridian-tests
cd kelvin-meridian-tests
export MERIDIAN_URL=https://<your address>    # given with your key
export MERIDIAN_KEY=<your key>                # never printed, never written to a file
python3 demo.py --autoplay                    # eight short scenes; --step waits for Enter instead
```

In the demo, KELVIN:
1. is asked about a person before it was told anything, and stays silent;
2. is told one fact;
3. answers it in a new request that does not carry the fact;
4. stays silent on a name it was never told;
5. keeps your memory yours: another memory knows nothing of it;
6. takes several facts and several questions in one request.

Each run makes up its own names, so it always starts from something KELVIN has never been told.

## Run a test

```sh
python3 tests/keys_needed.py > ~/meridian-keys.tsv && chmod 600 ~/meridian-keys.tsv   # then add each key after a tab
export MERIDIAN_KEYS_FILE=~/meridian-keys.tsv
python3 tests/6-remember/run.py
```

- **One key per memory.** A test keeps KELVIN's own memory and its control's; `tests/keys_needed.py` lists the names.
- **Every run needs new memories.** A second run into the same memory would add to the first and change every answer.
  Before it teaches anything, each test asks one of its own questions in each memory, and stops if any memory is not
  silent. That question lives nothing; where a test sends switches, the door only records them with the empty memory.
- **Tests 6 and 7 are light,** and run with a tester key. **Tests 1 to 5** keep a door busy for a long time, with
  single requests of up to several minutes or long runs of large uploads. A door answers one request at a time, so
  they run only on a door of your own: set `MERIDIAN_OWN_DOOR=1` to say so.
- **The limit is 120 requests a minute per key;** the scripts keep to it.
- **If large uploads break** ("Broken pipe"), you can try the other address family: `MERIDIAN_FAMILY=4` (or `6`)
  sends everything over IPv4 (or IPv6) only. Each run records which it used.
- **Python 3.10 or newer,** its standard library only. Test 1 also needs `pip install pyarrow` to read its dataset.

## How a run is kept honest

- **A control that must break,** in every test, judged by a rule fixed before our first run.
- **New memories only,** checked before anything is taught.
- **No answer, no second try.** A request that gets no answer may have been taught anyway, so it is never sent
  again, and the run stops as void. The one exception is an upload that broke before the request was whole: the
  server never received it, so it is sent again, at most three times, and recorded.
- **Every request and every answer is recorded,** exactly as it came back, in `runs/<date>-<test>/requests.jsonl.gz`.
  Pictures and clips appear there only as their sha256.
- **The data is pinned.** Each test fetches its files from their source at a fixed revision, and refuses any file
  whose sha256 does not match. No dataset is stored here, except the 346 CC0 facts of tests 6 and 7.
- **Void runs stay in the record.** Four of our runs broke before they could count: on the network path, on how the
  server then read slow uploads (since changed), and on our own script. Each keeps its record and a `VOID.md` with its
  cause, and the run that counted came after each was dealt with.

## Speed, on both sides

| | What you wait, network included | The server's own time |
|---|---|---|
| a text question (tests 1, 4, 5, 6) | **245 – 285 ms** (p50) | **12.0 – 30.5 ms** (p50) |
| teaching 1 835 examples, once (test 5) | 50 s, 29 s of it waiting behind the control's teach | **20.6 s** |
| teaching 15 100 examples, once (test 4) | 160 s | **156 s** |
| a picture asked (test 2) | 583 ms | 166 ms |
| a clip asked by its name, 4 clips sent (test 3) | 24.6 s, almost all of it the upload | 638 ms for any ask of test 3 |

The server's times are its operator's measurement. For tests 1, 2, 5, 6 and 7 they include the request arriving,
because the server then read a request as it came: small for text, large for pictures. Each test's
`results/RESULT.md` also gives the server's busy share, processor, memory, disk and network, where they were measured.

## What we do *not* claim

- **No comparison with other models here.** This repository runs KELVIN alone.
- **Not every result is a strength.** Screens, a kind KELVIN was never shown, got the nearest kind it knew 25 of 30
  times and silence only 5 times (test 2). One answer in three is wrong on when to call a tool (test 5). Where no
  intent fits, it said "none of the above" 337 of 1 000 times (test 4).
- **Not fixed across releases.** The results are release `5ddaa4fc`'s. Against an earlier release, test 3 changed 4
  of its 216 answers; its README names each one.
- **Not your network's time.** What you wait depends on your path to your address.

## Layout

| Path | What |
|---|---|
| `meridian.py` | the one client: keys, pacing, the busy rule, the run record |
| `demo.py` | the demo, with `--autoplay` or `--step` |
| `tests/<n>-<name>/` | one test: its README, `run.py`, its data's pins, and `results/` |
| `tests/common.py` | fetching pinned files, the control rule, the result |
| `tests/keys_needed.py` | the memories every test needs |
| `runs/` | our runs: every request and answer, each result; void runs with their `VOID.md` |
| `ci/` | the checks [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs, runnable on any host |

## Citation

GitHub's "Cite this repository" button gives the reference, from [`CITATION.cff`](CITATION.cff). Each release's
changes are listed in [`CHANGELOG.md`](CHANGELOG.md).

## Scope

KELVIN Meridian is a service by Pelloran Inc.: [pelloran.com/products/meridian](https://pelloran.com/products/meridian/).
This repository holds its public tests and our results; KELVIN itself is not in it.

## License

The code here is Apache-2.0 © Pelloran Inc.; see [LICENSE](LICENSE) and [NOTICE](NOTICE). The datasets keep their own
licences, named in each test's README; they are fetched from their sources and not stored here, except the 346 CC0
facts of tests 6 and 7.
