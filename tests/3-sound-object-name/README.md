# Test 3 · A sound, an object and its name

**What it shows.**
- KELVIN meets a thing once: an 8-second clip of it, seen and heard, told with its name. This is the only teaching; there is no training run.
- Then it is asked with a second it never lived (second 8 of the same clip):
  - from the sound alone, what is it called?
  - from the picture alone, what is it called?
- From the name alone, it picks the thing's clip among 4 offered, once by the picture and once by the sound.
- It is also shown things of kinds it never lived, and asked names it never heard. It should not give them a lived name, and it should not answer a name it never heard. Where it is not sure, it stays silent.
- The same lives run again under made-up names (`thing A` … `thing I`). KELVIN must answer exactly as under the real names, because a name is only a name to it.

**The data.**
- The source is [VGGSound](https://www.robots.ox.ac.uk/~vgg/data/vggsound/): 10-second clips of YouTube videos, each with a label. Its annotations are licensed CC BY 4.0, for research use. Each clip belongs to its YouTube uploader.
- **No clip is stored in this repository.** `clips.json` names the 54 clips the test uses. For each clip it gives:
  - its YouTube id and start second;
  - its VGGSound label;
  - the sha256 of the exact file our recorded run used.
- It also names the 6 lives. Each life has 4 lived things and 5 never-lived things:
  - the lived things are 4 of 9 animal kinds, drawn per life: dog barking, cattle mooing, horse neighing, sheep bleating, duck quacking, chicken crowing, frog croaking, lions roaring, elephant trumpeting;
  - the never-lived things are one each of pig oinking, goat bleating, donkey/ass braying, turkey gobbling and owl hooting.
- `fetch.py` fetches the clips into `data/`, which is never committed: **no clip goes into this repository.**
- **The default is the mirror.** You stream about 17 GB once and keep about 159 MB, the 54 clips. These are exactly the bytes of our recorded run, so the result reproduces.
- YouTube is the fallback. The route is recorded, and every result names it.

| route | command | what you get |
|---|---|---|
| 1 · the mirror (the default) | `fetch.py` or `fetch.py mirror` | The exact bytes our recorded run used. They come from one archive of the Hugging Face mirror [Loie/VGGSound](https://huggingface.co/datasets/Loie/VGGSound), at a pinned revision. The archive is about 17 GB. It is read once as a stream and never stored; it stops once it has all 54 clips, which lie near its end. Only those clips are kept (159 MB), and each must match its sha256. |
| 2 · YouTube (the fallback) | `fetch.py youtube` | Each clip from its YouTube video, by id and start second. This needs `yt-dlp` and `ffmpeg`. The bytes cannot be pinned, because YouTube re-encodes and videos are taken down. A clip that cannot be fetched is named. `run.py` then says how many asks the run lost, and the run is shown but not judged. Results may differ from ours. |
| a copy you hold | `fetch.py folder <DIR>` | Route 1's bytes from VGGSound files you already have, named `<youtube_id>_<start>.mp4`. Each must match its sha256. |

- **Route 2 on 2026-11-09:** 17 of the 54 videos were no longer on YouTube (unavailable, private, or their account terminated).
  - A life with a lived clip gone cannot be lived, so only lives 1, 2 and 5 could run.
  - Each arm would lose 120 of its 216 asks.

**The command.**

```sh
python3 tests/3-sound-object-name/fetch.py                # once: the mirror (about 17 GB streamed, 159 MB kept); or: youtube
export MERIDIAN_URL=https://<your address>
export MERIDIAN_KEYS_FILE=~/meridian-keys.tsv   # one line per memory: name<TAB>key (chmod 600)
python3 tests/3-sound-object-name/run.py
```

It needs 18 memories, and each must start empty:
- `sound-real-life1` … `sound-real-life6`, the real names;
- `sound-made-up-life1` … `sound-made-up-life6`, the made-up names;
- `sound-rotated-life1` … `sound-rotated-life6`, the control.

A memory keeps what it lived, so a second run into the same memories would add to the first and change its answers. Before anything is lived, `run.py` therefore asks each memory its life's first ask by the name. A memory that lived this life before always answers that ask, while a new one stays silent. If any memory answers, the run stops before anything is lived. Use new keys for each run.

There are 738 requests in all: per life and arm, the check above, 4 requests to live the things and 36 asks. One memory is asked at a time (`--side-by-side N` asks N at once; more than one sends several 20 MB uploads at the same time, and a door that reads one request at a time can stall them until the address gives up). Each request is under the standard's 32 MiB; an ask by the name carries its 4 clips, about 21 MB at most.

**The requests.** These are exactly as in our recorded run:
- **Every request** carries `state.read = "own width"`. That tells KELVIN to take a thing as known from one second only when that second lies within the spread the thing showed over its own 8 lived seconds. Otherwise it stays silent.
- **To live a thing:** `state.things = [{"thing", "clip", "name"}]`. The clip is the request's `video` asset (mp4), and KELVIN lives its seconds 0 to 7. There is one thing per request.
- **To ask by a sense:** `state.clip` names the asked clip (an asset), and `state.sense` is `sound` or `picture`. The question's options are the life's 9 names (4 lived, 5 never lived), in an order drawn per ask.
- **To ask by the name:** `state.name` and `state.sense`. The question's options are the 4 offered clips: each option names one of the request's own clip assets, and the offers are the life's 4 lived clips, in an order drawn per ask.
- An asked or offered clip is read at its second 8.

**How it is scored.** Each arm has 216 asks. The bars were set before our recorded run, and they are judged on the real names; the made-up names are shown beside them.

| ask | asks | bar |
|---|---|---|
| a lived thing's sound → its name | 24 | at least 12 right |
| its picture → its name | 24 | at least 12 right |
| its name → its clip by the picture (of 4) | 24 | at least 12 right |
| its name → its clip by the sound (of 4) | 24 | at least 12 right |
| a never-lived thing, by sound or by picture, answered with a lived name | 60 | at most 29 (silent on more than half) |
| a never-lived name answered | 60 | at most 6 |

- A silence is never counted right.
- **Made-up names against real names:** the two arms are compared ask for ask, up to the name. An ask counts as the same when both arms gave the same thing or the same clip, or both were silent.
- **Against our recorded run:** every answer is also compared, ask for ask, with `recorded.json`. That file holds our recorded run's 648 answers.

**Where to run it.**
- This test keeps a door busy for a long time, and a door answers one request at a time. On a shared tester door it would hold up every other tester.
- Until a limit for tester doors is set, it runs only on a door of one's own: set `MERIDIAN_OWN_DOOR=1` to say so.
- Our own result below comes from such a door. Its full run record, every request and every answer, is in this repository.

**The control that must break.**
- In memories of their own, the same lives are lived with the real names rotated: each lived thing is told the next thing's name.
- Each of the four lived-thing asks must then fall below 12 of 24. If one does not, the run does not count, and `run.py` says so.

**Our recorded result.** This was on our own KELVIN server on 2026-11-04, with route 1's bytes, before the first Meridian release.

| | bar | real names | made-up names | control |
|---|---|---|---|---|
| sound → name | ≥ 12 of 24 | **14** (1 wrong, 9 silent) | 14 | 0 |
| picture → name | ≥ 12 of 24 | **18** (0 wrong, 6 silent) | 18 | 0 |
| name → clip by the picture | ≥ 12 of 24 | **23** | 23 | 0 |
| name → clip by the sound | ≥ 12 of 24 | **18** | 18 | 1 |
| never-lived thing given a lived name | ≤ 29 of 60 | **12** | 12 | 12 |
| never-lived name answered | ≤ 6 of 60 | **0** | 0 | 0 |

- The made-up names were answered like the real names on 216 of 216 asks.
- **What to expect on today's release.** Two things changed after that run, and each was compared old against new on the real names' 216 asks before it was released:
  - KELVIN's way of seeing pictures was refined. One answer changed: in life 4, the dog's picture → its name was right and is now silent.
  - The server reads the clips itself now, so the sound of three clips comes out slightly different, by one step in a share of their samples. Three answers changed: in life 3, the cattle's sound → its name was silent and is now right; in life 4, the duck's sound → its name was right and is now silent; and in life 4, the never-lived turkey's sound was given the lived name "duck" and is now silent.
  - So on the release: sound → name 14, picture → name 17, a never-lived thing given a lived name 11, the rest as recorded. `run.py` lists every answer that differs from the record.

**KELVIN's result.** See [`results/RESULT.md`](results/RESULT.md), from a fresh run on our test address. Every request and its answer from that run are in the run record named there. The clips themselves are recorded only by their sha256.
