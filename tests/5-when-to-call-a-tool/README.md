# Test 5 · When to call a tool

**What it shows.**
- An assistant gets a request and a set of tools. It must choose one of four reactions:
  - call a tool;
  - ask for what is missing;
  - say it cannot;
  - answer directly.
- KELVIN lives half of the request families of a public test set, each item told with its right reaction.
- It is then asked items from families it has never met.

**The data.**
- The source is [When2Call](https://huggingface.co/datasets/nvidia/When2Call) by NVIDIA, at revision `0582f774`, licensed CC BY 4.0.
- `sources.json` pins the multiple-choice test file and the card by sha256.
- Each request appears several times, each time with other tools, and all its items form one family. A family is either lived or asked, never both.
- The families are shuffled with a fixed seed:
  - half are lived (1 835 items);
  - of the other half, the last two thirds are asked (1 216 items);
  - the first third is set aside and never used.

**The command.**

```sh
export MERIDIAN_URL=https://<your address>
export MERIDIAN_KEYS_FILE=~/meridian-keys.tsv   # memories: tools, tools-shuffled
# on your own KELVIN Meridian unit instead: export MERIDIAN_KEY=<your key>   (the client names each memory)
python3 tests/5-when-to-call-a-tool/run.py
```

The product's switches for this task are sent as headers: `KELVIN-Way: foam+text:A2+rel` and `KELVIN-Weigh: lived`.

**Where to run it.**
- This test lives a lot in one request, and a door answers one request at a time. On a shared tester door it would hold up every other tester for that long.
- Until a limit for tester doors is set, it runs only on a door of one's own: set `MERIDIAN_OWN_DOOR=1` to say so.
- Our own result below comes from such a door. Its full run record, every request and every answer, is in this repository.

**The control that must break.**
- In a memory of its own, KELVIN lives the same items with their reactions shuffled among them.
- KELVIN must be right where the control is wrong more often than the other way round (a paired sign test, p < 0.05).
- If it is not, the run does not count.

**KELVIN's result.** See [`results/RESULT.md`](results/RESULT.md), with the result for each of the four reactions.
