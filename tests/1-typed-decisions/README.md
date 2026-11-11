# Test 1 · Learn typed decisions from cases

**What it shows.**
- KELVIN is given 300 solved cases of a business task, each a situation together with the five right answers. This is the only teaching; there is no training run.
- Then it answers 100 new cases it has never seen, from what it kept.
- It does this for each of the four areas of a public dataset: agent traces, customer service, invoices and security incidents.
- The answers are scored by the dataset's own scorer.

**The data.**
- The source is [Typed Decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions) at revision `c9e8c416`, licensed Apache-2.0 (as its card states).
- `sources.json` names each file with its sha256. The run fetches them and refuses any file that does not match. Nothing of the dataset is stored in this repository.
- Of each area, all 300 training cases are lived and all 100 test cases are asked.

**The command.**

```sh
pip install pyarrow                       # the dataset comes as parquet files
export MERIDIAN_URL=https://<your address>
export MERIDIAN_KEYS_FILE=~/meridian-keys.tsv   # one line per memory: name<TAB>key (chmod 600)
# on your own KELVIN Meridian unit instead: export MERIDIAN_KEY=<your key>   (the client names each memory)
python3 tests/1-typed-decisions/run.py
```

It needs eight memories:
- `typed-<area>`, one for each of the four areas;
- `typed-<area>-shuffled`, one for each area's control.

The product's switches for this task are sent as headers on every request:
- `KELVIN-Way: foam+text:N2`
- `KELVIN-Weigh: answer`
- `KELVIN-Sharpness: lived`

**How it is scored.**
- Each answer goes through the dataset's own `score_one`, taken unchanged from its scorer file `bench/score_with_jobs.py`, which is fetched and pinned like the data.
- One step is named: KELVIN answers a yes/no question with a single number. That number is read as {true: n, false: 1 − n}, because the scorer expects two probabilities.
- Accuracy, KL from gold, Brier and ECE are averaged exactly as the scorer's own `main()` averages them.
- Two plain baselines are computed by us with the same scorer:
  - guessing, with every option alike;
  - the training cases' average answer.

**Where to run it.**
- This test lives a lot in one request, and a door answers one request at a time. On a shared tester door it would hold up every other tester for that long.
- Until a limit for tester doors is set, it runs only on a door of one's own: set `MERIDIAN_OWN_DOOR=1` to say so.
- Our own result below comes from such a door. Its full run record, every request and every answer, is in this repository.

**The control that must break.**
- In a memory of its own, KELVIN lives the same 300 cases with their answers shuffled among them.
- On the same 2 000 answers, KELVIN must be right where the control is wrong more often than the other way round (a paired sign test, p < 0.05).
- If it is not, the run does not count, and `run.py` says so.

**KELVIN's result.** See [`results/RESULT.md`](results/RESULT.md), from a fresh run on our test address. Every request and its answer from that run are in the run record named there.
