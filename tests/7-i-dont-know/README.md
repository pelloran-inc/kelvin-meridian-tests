# Test 7 · Say "I don't know"

**What it shows.**
- KELVIN answers only from what it was told.
- Every question offers ten names and an eleventh option, "none of the above".
- KELVIN is told the parents of half of the people (drawn with a fixed seed). Then it is asked four kinds of question:

| question | the right answer |
|---|---|
| a parent it was told | that parent |
| a parent it was told, but that parent is not among the ten names | none of the above |
| the other parent of a person it was told about, which it was never told | none of the above |
| a person it was never told anything about | none of the above |

- For the last two kinds a real answer may exist in the world. KELVIN was not told it, so "none of the above" is right.
- A silence counts as "none of the above".

**The data.** The same 346 Wikidata facts as test 6 (`../6-remember/parents.tsv`), which are CC0.

**The command.**

```sh
export MERIDIAN_URL=https://<your address>
export MERIDIAN_KEYS_FILE=~/meridian-keys.tsv   # memories: dont-know, dont-know-nothing-told
# on your own KELVIN Meridian unit instead: export MERIDIAN_KEY=<your key>   (the client names each memory)
python3 tests/7-i-dont-know/run.py
```

**The control that must break.**
- In a memory of its own, KELVIN is told nothing and asked the same questions.
- On the questions about what it was told, KELVIN must be right where the control is wrong more often than the other way round (a paired sign test, p < 0.05).

**KELVIN's result.** See [`results/RESULT.md`](results/RESULT.md).
