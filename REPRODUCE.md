# Reproduce

This file lists every number that this repository's README cites. For each one it gives the run record it stands in,
the field, and the command that produces it. Run the commands from the repository root, with your address and your
keys set (see the README). Every run record is under `runs/`; each test's `results/RESULT.md` is its readable form.

All runs: release `5ddaa4fc` (test 2's latest run: `b0984839`, the release that added MB1), on our test address (a test door of our own, reached over the public internet with TLS
like any tester's address), 2026-11-09 and 2026-11-10, Central European Time as in the run records' names.

## The eight tests

| Number | What it is | Run record · field | Command |
|---|---|---|---|
| **0.706** · 0.162 · 0.089 · 0.131 | Test 1: accuracy, KL from gold, Brier, ECE over 2 000 answers, by the dataset's own scorer | `runs/2026-11-09T23-59-37+0100-typed-decisions/result.json` · `all.kelvin` | `python3 tests/1-typed-decisions/run.py` |
| 0.508 | Test 1's control, the answers shuffled | the same · `all.control_shuffled.accuracy` (0.5075) | the same |
| **24 of 24** | Test 2: lived pictures asked again, answered as told | `runs/2026-11-10T18-23-27+0100-pictures/result.json` · `kelvin.again.as_told` | `python3 tests/2-pictures/run.py` |
| **50 of 60** | Test 2: unseen photos and documents, named by their kind | the same · `kelvin.unseen.right` | the same |
| 25 of 30 · 5 | Test 2: screens given a lived kind (21 document, 4 photo) · silent | the same · `kelvin.screens` | the same |
| 0 of 24 · 10 of 60 | Test 2's control, the kinds swapped | the same · `control_swapped.again.right`, `control_swapped.unseen.right` | the same |
| **23 of 24** | Test 3: a thing's clip picked by its name, by the picture | `runs/2026-11-10T07-00-50+0100-sound-object-name/result.json` · `real names.claims.name to clip by picture` | `python3 tests/3-sound-object-name/fetch.py`, then `python3 tests/3-sound-object-name/run.py` |
| **14 of 24** | Test 3: its name from the sound alone | the same · `real names.claims.sound to name` | the same |
| **0 of 60** | Test 3: a name never heard, answered | the same · `real names.claims.never-lived name answered` | the same |
| **216 of 216** | Test 3: made-up names answered as the real ones | the same · `made-up answered like real.equal` | the same |
| 0 · 0 · 0 · 1 of 24 | Test 3's control, the names rotated | the same · `control: names rotated.claims` | the same |
| 4 of 216 | Test 3: answers that differ from an earlier release's run, each named in its README | the same · `equal to the recorded run` (212 of 216) | the same |
| **3 821 of 4 500** | Test 4: intent right | `runs/2026-11-10T10-09-24+0100-intent/result.json` · `kelvin.in_scope_right` | `python3 tests/4-intent/run.py` |
| 337 of 1 000 | Test 4: "none of the above" where no intent fits | the same · `kelvin.none_right` | the same |
| 19 of 4 500 | Test 4's control, the intents shuffled | the same · `control_shuffled.in_scope_right` | the same |
| **816 of 1 216** | Test 5: the right reaction | `runs/2026-11-10T00-03-02+0100-when-to-call-a-tool/result.json` · `kelvin.right` | `python3 tests/5-when-to-call-a-tool/run.py` |
| 430 of 1 216 | Test 5's control, the reactions shuffled | the same · `control_shuffled.right` | the same |
| **345 of 345** | Test 6: a told fact answered later | `runs/2026-11-10T17-19-53+0100-remember/result.json` · `right` | `python3 tests/6-remember/run.py` |
| 345 · 332 of 332 | Test 6: asked twice, the same bytes · never told, silent | the same · `asked_twice_identical`, `never_told_silent` | the same |
| 4 of 345 | Test 6's control, the facts shuffled: right against the truth | the same · `control_right_against_the_truth` | the same |
| **558 of 558** · 389 of 389 | Test 7: right overall · "none of the above" where it could not know | `runs/2026-11-09T23-50-07+0100-i-dont-know/result.json` · `right_overall`, `not_known_none_of_the_above` | `python3 tests/7-i-dont-know/run.py` |
| 0 of 169 | Test 7's control, nothing told: the told questions right | the same · `control_nothing_told.told.right` | the same |
| **50 of 50** · **50 of 50** · 50 of 50 | Test 8: forward right · reverse right (every child held; 10 parents with several) · no one's parent silent | `runs/2026-11-11T15-05-09+0100-reversal/result.json` · `forward.right`, `reverse.right`, `no_ones_parent.silent` | `python3 tests/8-the-reversal/run.py` |
| 0 of 50 | Test 8's control, the relation swapped: the same children given | the same · `control.swapped_relation_gave_the_same_children` | the same |

## Speed

| Number | What it is | Where it stands |
|---|---|---|
| 104 ms · 17.7 ms | A text question with one kept connection: what you wait (p50) · the server's own time (test 6) | `runs/2026-11-10T17-19-53+0100-remember/result.json` (`ask_ms_p50`: 103.6) · `tests/6-remember/results/RESULT.md`, "At the server" |
| 252 ms | The same, with a new connection for every request (the earlier client) | `runs/2026-11-09T23-35-32+0100-remember/result.json` (`ask_ms_p50`: 252.1) |
| 245 – 285 ms · 12.0 – 30.5 ms | A text question with a new connection each time (tests 5, 4, 1, the earlier client) · the server's own time (p50; test 6's earlier run 17.5) | each run's `result.json` (`ask_ms_p50`) · each test's `results/RESULT.md`, "At the server" |
| 20.6 s · 156 s | The server's time to teach 1 835 examples (test 5) and 15 100 (test 4), once | the same sections |
| 594 ms · 225 ms | A picture lived and saved, one kept connection, MB1: what you wait (p50) · the server's own time (test 2) | `runs/2026-11-10T18-23-27+0100-pictures/` · `tests/2-pictures/results/RESULT.md` |
| 440 ms · 63 ms | A picture asked, one kept connection, MB1: what you wait (p50) · the server's own time (test 2) | the same |
| 663 ms · 479 ms | The same tell and ask with a kept connection as JSON (test 2's earlier run) | `runs/2026-11-10T17-34-26+0100-pictures/result.json` (`times_ms`) |
| 583 ms | The same ask with a new connection for every request, as JSON (test 2's first run) | `runs/2026-11-10T00-14-09+0100-pictures/` |
| 0.13 MB · 0.17 MB | A picture ask's request as MB1 · as JSON (p50) | the two runs' `requests.jsonl.gz` (`bytes_sent`) |
| 24.6 s · 638 ms | A clip asked by its name: what you wait (p50) · the server's own time for any ask (test 3) | `tests/3-sound-object-name/results/RESULT.md` |

The earlier runs of tests 6 and 2 stay under `runs/`: their answers equal the latest runs', and their times are the
earlier clients' (a new connection for every request; for test 2 also a kept connection as JSON).

The server's times are its operator's measurement, from the server's own log and samples; they cannot be re-run from
this repository. Your own run records your side of every request, so you can set your times beside ours.

## Not reproducible from this repository alone

- **The server's side** (its own times, busy share, processor, memory, disk, network): measured by the operator of
  our test address, as named above.
- **The void runs** under `runs/`, each with its `VOID.md`: they broke before they could count, and their causes were
  fixed. They are kept as records, not results.
