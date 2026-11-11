# Test 8 · The reversal: told one way, asked both ways

**What it shows.**
- KELVIN is told 346 real facts in one direction only: a well-known person's mother or father (child → parent), 50
  facts to a request.
- Later, in new requests that do not carry the facts, it is asked both ways, with ten names to choose from:
  - **forward**, the way it was told: who is this person's mother or father (`"state": {"subject": …}`), 50 questions;
  - **reverse**, the other way: whose mother or father is this person (`"state": {"object": …}`), 50 questions. Among
    them are every parent with several children. Right means every child is held and no one else;
  - **about people who are no one's parent:** it was never told a child of theirs, so it must stay silent, 50
    questions.
- Each check prints right, wrong or silent, and its time.

**The data.**
- The facts are test 6's [`parents.tsv`](../6-remember/parents.tsv): 346 parent facts from
  [Wikidata](https://www.wikidata.org) (CC0).
- The people are the well-known names listed by Berglund et al. 2024.
- The questions and their ten names are drawn with a fixed seed.

**The command.**

```sh
export MERIDIAN_URL=https://<your address>
export MERIDIAN_KEY=<your key>          # one memory; it must be empty when the test starts
python3 tests/8-the-reversal/run.py
```

No switches are needed: this is KELVIN's plain way.

**The control that must break.**
- In the same memory, the reverse questions are asked again with the relation swapped (mother ↔ father).
- KELVIN was told each child under one relation only, so under the other it must not give that parent's children.
- It must be right on the told relation, where the swapped relation gives the same children, more often than the
  other way round (a paired sign test, p < 0.05).

**Context, not a comparison.** Berglund et al. (ICLR 2024, "The Reversal Curse", arXiv 2309.12288) measured that large
language models trained on "A is B" often fail at "B is A". That is their measurement, with their models and their truth;
this test does not compare against it.

**KELVIN's result.** See [`results/RESULT.md`](results/RESULT.md).
