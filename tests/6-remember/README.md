# Test 6 · Remember what you were told

**What it shows.**
- KELVIN is told 346 real facts, each a well-known person's mother or father, 50 facts to a request.
- Later it is asked each person's parent in new requests that do not carry the facts, with ten names to choose from.
- Three more things are checked:
  - asked twice, it gives the same answer byte for byte;
  - asked about people whose parents it was never told, it stays silent;
  - another memory, where nothing was told, stays silent on the same questions. Your memory is yours.

**The data.**
- `parents.tsv` is in this folder. It holds 346 parent facts from [Wikidata](https://www.wikidata.org), which is CC0.
- The people are the well-known names listed by Berglund et al. 2024 ("The Reversal Curse", arXiv 2309.12288). A name was kept when exactly one person on Wikidata carries it.
- The order of the facts and the ten names of each question are drawn with a fixed seed.

**The command.**

```sh
export MERIDIAN_URL=https://<your address>
export MERIDIAN_KEYS_FILE=~/meridian-keys.tsv   # memories: remember, remember-shuffled, remember-other
python3 tests/6-remember/run.py
```

No switches are needed: this is KELVIN's plain way.

**The control that must break.**
- In a memory of its own, KELVIN is told the same facts with the parents shuffled among the people.
- It must follow what it was told there, so against the truth it is right far less often.
- KELVIN's own memory must be right where the control is wrong more often than the other way round (a paired sign test, p < 0.05).

**KELVIN's result.** See [`results/RESULT.md`](results/RESULT.md).
