# Test 2 · A picture: this one, else its kind

**What it shows.**
- KELVIN is shown 500 photos and 500 documents, one picture a request, each told with its kind ("photo" or "document"). On the server's own count it kept 998 of them: two give it nothing to keep. This is the only teaching; there is no training run.
- Asked again about 24 of these pictures, it should answer the kind it was told for that very picture.
- Asked about 30 photos and 30 documents it has never seen, it should answer their kind.
- Asked about 30 screens (pictures of web pages), a kind it was never told about, it should never answer "screen".

**The data.**
- Photos: [COCO 2017](https://cocodataset.org/#download), train split. Only photos under CC BY 2.0 or CC BY-SA 2.0 (COCO's licence ids 4 and 5), each fetched from its own address at images.cocodataset.org.
- Documents: [DocLayNet v1.1](https://huggingface.co/datasets/docling-project/DocLayNet-v1.1), val split, at revision `5e893923`, licensed CDLA-Permissive-1.0: pages of reports, manuals, articles, laws, patents and tenders.
- Screens: [WebSight v0.1](https://huggingface.co/datasets/HuggingFaceM4/WebSight) at revision `b11f8172`, licensed CC BY 4.0: rendered web pages.
- `pictures.json` names each of the 1 090 pictures with its source, its licence and its sha256, in the order they are told and asked. The pictures were drawn once, by a fixed seed, and their roles fixed then.
- Nothing of the pictures is stored in this repository. The first run fetches them into `data/` (about 160 MB) and refuses any file that does not match its sha256. A picture that cannot be fetched stops the run with its name; no other picture is put in its place.
- The run writes `data/ATTRIBUTION.md`: every picture with its source and licence, and for each photo its page on Flickr, where its author is named.
- The pinned bytes are the bytes of the run that decided this test. Documents and screens come one row at a time through the Hugging Face dataset viewer, which serves each row's image (the documents as JPEG). If it ever serves other bytes, the run stops at the first one. It is asked at most every two seconds and sometimes answers busy, so the first fetch takes about 45 minutes.

**The command.**

```sh
export MERIDIAN_URL=https://<your address>
export MERIDIAN_KEYS_FILE=~/meridian-keys.tsv   # one line per memory: name<TAB>key (chmod 600)
python3 tests/2-pictures/run.py
```

It needs two memories:
- `pictures`;
- `pictures-swapped`, for the control.

Both must be new. Before anything is told, the run asks each memory one of its questions; if the answer is anything but silence, the run stops. A second run needs new keys, so it never adds to the first.

Python's standard library is all it needs.

**How it asks.**
- One picture a request, sent as an `image` asset.
- A tell: `state.pictures = [{picture, kind}]`. An ask: `state.picture`, with one `choice` question, "What kind of picture is `picture`?", over photo, document and screen. The options' order is shuffled per picture by a fixed seed.
- Every request, the tell and the ask, carries `state.read = "staircase"`, the read the customer handbook names for the kind of a picture:
  - KELVIN first looks among the pictures it lived for this very one. If it finds exactly one, it answers the kind it was told for that picture.
  - Otherwise it answers with the lived kind the picture resembles most.
  - A picture in which it sees nothing at all gets silence.
- No switch headers are sent.

**How it is scored.**
- A lived picture asked again is right when KELVIN answers the kind it was told for it.
- An unseen photo or document is right when KELVIN answers its kind.
- A silence is never right.
- For the screens, each answer is counted as photo, document, screen or silence.

**What must hold.** These were decided before the first run:
- the lived pictures asked again: at least 22 of 24 right;
- the unseen pictures: at least 46 of 60 right;
- the screens: "screen" is never answered (0 of 30).

**Where to run it.**
- This test keeps a door busy for a long time, and a door answers one request at a time. On a shared tester door it would hold up every other tester.
- Until a limit for tester doors is set, it runs only on a door of one's own: set `MERIDIAN_OWN_DOOR=1` to say so.
- Our own result below comes from such a door. Its full run record, every request and every answer, is in this repository.

**The control that must break.**
- In a memory of its own, KELVIN is told the same 1 000 pictures, with every photo told "document" and every document told "photo" (on the server's own count it kept 998 there too). It is then asked the same 114 pictures.
- It must fall below 22 of 24 on the lived pictures and to at most 30 of 60 on the unseen ones. If it does not, the run does not count, and `run.py` says so.

**What KELVIN answered when this test was decided** (2026-11-04, on an earlier release):
- **The lived pictures asked again:** 24 of 24 got the kind they were told. In the control, all 24 got the wrong kind they had been told. KELVIN answers what it was told about that very picture.
- **The unseen pictures:** 50 of 60 got their kind: 22 of 30 photos and 28 of 30 documents. 8 photos were called documents, and 2 documents photos.
- **The screens, the weak part of this test:**
  - KELVIN never answered "screen", as it must not.
  - But it called 21 screens a document and 4 a photo, and was silent for only 5.
  - So with this read, KELVIN does not say "I don't know" about a kind it was never told about. It gives the nearest kind it knows.
- **The control:** 0 of 24 and 10 of 60. It broke.

**KELVIN's result today.** See [`results/RESULT.md`](results/RESULT.md), from a fresh run on our test address. The release has changed since this test was decided. Every request and its answer from that run are in the run record named there.
