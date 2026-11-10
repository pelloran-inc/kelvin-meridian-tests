# Test 3 · a sound, an object and its name · result

Address: our test address (a test door of our own, on the published release 5ddaa4fc, reached over the public internet with TLS like any tester's address), release 5ddaa4fc, run record `runs/2026-11-10T07-00-50+0100-sound-object-name`; address family: IPv4 only.

The clips: route `mirror` (the recorded run's exact bytes, from the mirror); 54 of 54 fetched, 54 equal to the recorded run's bytes.

| | bar | real names | made-up names | control: names rotated | recorded (real names) |
|---|---|---|---|---|---|
| from the sound alone → its name | ≥ 12 of 24 | **14** | 14 | 0 | 14 |
| from the picture alone → its name | ≥ 12 of 24 | **17** | 17 | 0 | 18 |
| from the name → its clip by the picture (of 4) | ≥ 12 of 24 | **23** | 23 | 0 | 23 |
| from the name → its clip by the sound (of 4) | ≥ 12 of 24 | **18** | 18 | 1 | 18 |
| a never-lived thing answered with a lived name | ≤ 29 of 60 | **11** | 11 | 11 | 12 |
| a never-lived name answered | ≤ 6 of 60 | **0** | 0 | 0 | 0 |

- **The claims hold (real names):** yes.
- **The control breaks** (with the names rotated, each lived-thing ask falls below 12 of 24): yes.
- **Made-up names answered like real names**, ask for ask (the same thing or the same clip, or silent in both): 216 of 216.
- **Equal to the recorded run**, ask for ask: real names 212 of 216, made-up names 212 of 216, control 212 of 216.
  - real names, life 3, sound to name, thing 3.0: now cattle mooing, recorded silent
  - real names, life 4, picture to name, thing 4.1: now silent, recorded dog barking
  - real names, life 4, sound to name, thing 4.3: now silent, recorded duck quacking
  - real names, life 4, never-lived thing by sound, stranger 4.3: now silent, recorded duck quacking
  - made-up names, life 3, sound to name, thing 3.0: now thing D, recorded silent
  - made-up names, life 4, picture to name, thing 4.1: now silent, recorded thing C
  - made-up names, life 4, sound to name, thing 4.3: now silent, recorded thing A
  - made-up names, life 4, never-lived thing by sound, stranger 4.3: now silent, recorded thing A
  - control, life 3, sound to name, thing 3.0: now elephant trumpeting, recorded silent
  - control, life 4, picture to name, thing 4.1: now silent, recorded elephant trumpeting
  - control, life 4, sound to name, thing 4.3: now silent, recorded chicken crowing
  - control, life 4, never-lived thing by sound, stranger 4.3: now silent, recorded chicken crowing

Of the asks by one sense (real names), the answers given and the silences:

- sound to name: 14 right, 1 wrong, 9 silent (of 24)
- picture to name: 17 right, 0 wrong, 7 silent (of 24)

| request (real names) | p50 ms | p90 ms | bytes sent p50 | bytes sent max |
|---|---|---|---|---|
| tell | 6003.6 | 8553.0 | 4481377 | 9216778 |
| by a sense | 5610.5 | 8988.7 | 4177106 | 9216733 |
| by the name | 24601.3 | 35669.8 | 16734660 | 20742758 |
| a never-lived name | 23392.4 | 34700.8 | 16734656 | 20742766 |

Times include the network between you and the address (one memory was asked at a time).

Requests sent again because their upload broke before the body was whole (the door never received them whole): 0. Each broken attempt is in the run record.

## At the server (measured by the address's operator, release 5ddaa4fc, 2026-11-10 06:01:13–08:57:25 UTC)

The address took each request whole before KELVIN read it, so the server's times below are KELVIN's own, without the upload. Processor, memory and network were sampled once a second from 06:19:43 UTC, 89.5 % of the run.

| | |
|---|---|
| requests at the server | 738, equal to this run's 738, all answered 200, none sent again |
| the server busy | 466.8 s of a 2 h 56 min run (4.4 %): the rest of the time was the clips arriving |
| KELVIN's own time, an ask | n 666: p50 638 ms, p90 1.83 s, max 2.27 s |
| KELVIN's own time, a thing lived and saved | n 72: p50 947 ms, p90 1.04 s, max 1.10 s |
| processor (sampled part) | 4 209 core-seconds; about 16 cores at its busiest second (the clips are read on many threads) |
| memory (sampled part) | peak 2.10 GB, 0.86 GB after |
| disk after (these memories) | 10.1 MB for the 18 memories |
| network at the address (sampled part) | 6.30 GB received, 94 MB sent |
| request / answer bodies | 6.97 GB / 0.27 MB |
