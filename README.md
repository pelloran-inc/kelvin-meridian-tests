# KELVIN Meridian · see it, test it

KELVIN learns from what it lives. It keeps what it was told, and it answers from what it kept. Where it was told nothing, it says so instead of guessing.

This repository shows that in two ways:
- **a short demo** that runs by itself;
- **seven tests** that anyone with a tester key can run against KELVIN's public API. These are the tests we ran, with the same data and the same controls.

## What you need

- Python 3.10 or newer. The tests use only its standard library, except test 1, which needs `pip install pyarrow` to read its dataset's files.
- Your address and your key, both given with your tester account.

```sh
export MERIDIAN_URL=https://<your address>
export MERIDIAN_KEY=<your key>          # never printed, never written to a file by these scripts
```

## The demo

```sh
python3 demo.py --autoplay        # eight short scenes, a pause before each
python3 demo.py --step            # waits for Enter before each scene
```

In the demo, KELVIN:
1. is asked about a person before it was told anything, and stays silent;
2. is told one fact;
3. answers it in a new request that does not carry the fact;
4. stays silent on a name it was never told;
5. keeps your memory yours;
6. takes several facts and several questions in one request.

Each run makes up its own names, so it always starts from something KELVIN has not been told.

## The seven tests

| | test | what it shows | data (fetched and checked by sha256) |
|---|---|---|---|
| 1 | [Learn typed decisions from cases](tests/1-typed-decisions/) | 300 solved cases per business area are its only teaching; it answers 100 new cases, scored by the dataset's own scorer | Typed Decisions, Apache-2.0 |
| 2 | [A picture: this one, else its kind](tests/2-pictures/) | after living 1 000 pictures, it knows each one again, and names the kind of a picture it never saw | COCO, DocLayNet, WebSight (CC BY / CDLA) |
| 3 | [A sound, an object and its name](tests/3-sound-object-name/) | each thing is lived once as a short clip with its name; it then names it from the sound or the picture alone, and picks its clip by the name | VGGSound clip list (CC BY 4.0 annotations); the clips are fetched, never stored |
| 4 | [Intent, and "none of the above"](tests/4-intent/) | it names the intent of a new request among 150, and says "none of the above" where none fits | CLINC150, CC BY 3.0 |
| 5 | [When to call a tool](tests/5-when-to-call-a-tool/) | it chooses whether to call a tool, ask, refuse or answer, for requests it never met | When2Call, CC BY 4.0 |
| 6 | [Remember what you were told](tests/6-remember/) | facts told once are answered later, in requests that do not carry them | Wikidata parents, CC0 (in the folder) |
| 7 | [Say "I don't know"](tests/7-i-dont-know/) | asked what it was never told, it chooses "none of the above" | the same facts |

**Each test is one command.** For example: `python3 tests/6-remember/run.py`.
- Tests 1 to 5 keep a door busy for a long time: single requests of up to several minutes, or long runs of heavy requests.
- A door answers one request at a time, so on a shared tester door these five would hold everyone else up.
- Until a limit for tester doors is set, they run only on a door of one's own (`MERIDIAN_OWN_DOOR=1`).
- Their results and full run records from our own door are in their folders.
- Tests 6 and 7 are light, and run with a tester key.

**Memories and keys.**
- A test keeps several memories, one key each: KELVIN's own memory, and its control's.
- `python3 tests/keys_needed.py` lists the names they need.
- Put them with your keys into a file readable by you only, one line each: `name<TAB>key`.
- Set `MERIDIAN_KEYS_FILE` to that file.
- **Every run needs new memories.** A second run into the same memory would add to the first and change every answer. Before it teaches anything, each test asks one of its own questions in each of its memories. If any memory answers instead of staying silent, the test stops. That question lives nothing; where a test sends switches, the door only records them with the empty memory.

**Every test has a control that must break.**
- The control is the same test in a memory of its own, with the thing that should matter taken away: the answers shuffled, the names rotated, or nothing told.
- KELVIN must clearly beat its control on the same questions. Each test's README names the exact rule: a paired sign test (p < 0.05), or the bar that was set before our first run. If KELVIN does not beat the control, the run says so and does not count.

**Every run is recorded.**
- `runs/<date>-<test>/requests.jsonl.gz` holds each request and KELVIN's answer exactly as it came back.
- Pictures and clips appear in that record only as their sha256.
- Each test folder's `results/RESULT.md` is our own latest run, on our test address.

**If large uploads break** ("Broken pipe"), you can try the other address family: `MERIDIAN_FAMILY=4` (or `6`) sends everything over IPv4 (or IPv6) only. Each run records which it used.

**What the times mean.** Every time includes the network between you and your address. The limit is 120 requests a minute per key; the scripts keep to it.

**No dataset is stored here,** except the 346 CC0 facts of tests 6 and 7. Each test fetches its files from their source at a pinned revision and refuses any file whose sha256 does not match. Their licences are named in each test's README.

## Licence

The code here (the client, the demo and the tests) is Apache-2.0 © Pelloran Inc.; see [LICENSE](LICENSE). The datasets
keep their own licences, named in each test's README; they are fetched from their sources and not stored here, except
the 346 CC0 facts of tests 6 and 7.
