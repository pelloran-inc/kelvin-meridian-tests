# Test 4 · Intent, and "none of the above"

**What it shows.**
- KELVIN hears 15 000 short requests once each, every one told with what the person wanted, out of 150 intents such as "transfer money" or "book a flight".
- It also hears 100 requests that fit none of them, told as "none of the above".
- Then it is asked 5 500 requests it has never seen. 1 000 of them fit no intent at all, and there the right answer is "none of the above".
- KELVIN either names the intent or stays silent. A silence counts as "none of the above".

**The data.**
- The source is [CLINC150](https://github.com/clinc/oos-eval) (Larson et al., 2019) at commit `828f8093`, licensed CC BY 3.0.
- `sources.json` pins `data_full.json` and the licence by sha256. The run fetches them and stores nothing of them here.
- What is lived: all of `train` (15 000) and all of `oos_train` (100).
- What is asked: all of `test` (4 500) and all of `oos_test` (1 000).

**The command.**

```sh
export MERIDIAN_URL=https://<your address>
export MERIDIAN_KEYS_FILE=~/meridian-keys.tsv   # memories: intent, intent-shuffled
python3 tests/4-intent/run.py
```

- The product's switches for this task are sent as headers: `KELVIN-Way: foam+text:A2` and `KELVIN-Silence: lived`.
- All 15 100 lived requests go in one request, and forming the memory takes a few minutes.
- At 120 asks a minute, the 5 500 asks take about 46 minutes. The control's memory is asked at the same time on its own key.

**Where to run it.**
- This test lives a lot in one request, and a door answers one request at a time. On a shared tester door it would hold up every other tester for that long.
- Until a limit for tester doors is set, it runs only on a door of one's own: set `MERIDIAN_OWN_DOOR=1` to say so.
- Our own result below comes from such a door. Its full run record, every request and every answer, is in this repository.

**The control that must break.**
- In a memory of its own, KELVIN lives the same requests with their intents shuffled among them.
- On the 4 500 in-scope asks, KELVIN must be right where the control is wrong more often than the other way round (a paired sign test, p < 0.05).
- If it is not, the run does not count.

**KELVIN's result.** See [`results/RESULT.md`](results/RESULT.md).
