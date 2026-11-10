# Test 2 · a picture: this one, else its kind · result

Address: our test address (a test door of our own, on the published release 5ddaa4fc, reached over the public internet with TLS like any tester's address), release 5ddaa4fc, run record `runs/2026-11-10T00-14-09+0100-pictures`; address family: not recorded (the system's default).

KELVIN lived 500 photos and 500 documents, each told with its kind, then was asked the kind of 114 pictures, one at a time.

| asked | what must hold | KELVIN | holds | control (kinds swapped) | when decided |
|---|---|---|---|---|---|
| 24 lived pictures again | their kind, at least 22 | **24 of 24** | yes | 0 of 24 | 24 of 24 |
| 60 unseen photos and documents | their kind, at least 46 | **50 of 60** | yes | 10 of 60 | 50 of 60 |
| 30 screens, a kind never told | never "screen" | **0 of 30** "screen" | yes | 0 of 30 | 0 of 30 |

**The screens, plainly:** KELVIN was never told what a screen is. Of the 30 it said "photo" for 4, "document" for 21 and "screen" for 0, and stayed silent ("I don't know") for 5. Most screens got the nearest lived kind instead of silence. When decided: 4 photo, 21 document, 5 silent.

**The unseen pictures:** 50 of 60 got their kind, 10 the other kind, 0 silence.

**The lived pictures asked again** got the kind KELVIN was told for that very picture 24 of 24 times. In the control, where each was told the other kind, it answered that other kind 24 of 24 times.

**The control** (every photo told "document" and every document told "photo", in its own memory) must fall below 22 of 24 and at most 30 of 60: 0 of 24 and 10 of 60, so it breaks.

Times: a tell 766.6 / 922.6 ms, an ask 583.3 / 693.8 ms (p50 / p90), including the network between you and the address. Sent: a tell 0.19 MB, an ask 0.17 MB (the picture as base64, p50); an answer 195 bytes.

## At the server (measured by the address's operator, release 5ddaa4fc, 2026-11-09 23:14:10–23:28:13 UTC)

These figures were measured before the address took each request whole before KELVIN reads it: the server's times below include reading the request as it arrived over our uplink. For this test that matters most: the server's busy time is mostly the 439 MB of pictures arriving, not KELVIN's work.

| | |
|---|---|
| requests at the server | 2 230, equal to this run's 2 230, all answered 200 |
| the server busy | 793.5 s of a 14 min 3 s run (94 %), mostly the pictures arriving |
| KELVIN's own time, an ask | n 234: p50 166 ms, p90 433 ms, max 596 ms |
| KELVIN's own time, a picture lived and saved | n 1 996: p50 327 ms, p90 583 ms, max 1.89 s |
| disk after (these memories) | 7.41 MB |
| request / answer bodies | 439.24 MB / 0.55 MB |
| memory | the server's peak by the end of this run 1.96 GB (0.96 GB then), for everything it held |
| processor, network | not measured for this run |
