# Test 2 · a picture: this one, else its kind · result

Address: our test address (a test door of our own, on the published release named next, reached over the public internet with TLS like any tester's address), release b0984839, run record `runs/2026-11-10T18-23-27+0100-pictures`; address family: IPv4 only.

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

Times: a tell 593.5 / 938.5 ms, an ask 440.2 / 719.6 ms (p50 / p90), including the network between you and the address. Sent: a tell 0.14 MB, an ask 0.13 MB (the picture as raw bytes in MB1, p50); an answer 195 bytes.

Requests sent again because their upload broke before the body was whole (the door never received them whole): 0. Each broken attempt is in the run record.

## At the server (measured by the address's operator, release b0984839, 2026-11-10 17:23:27–17:36:29 UTC)

The address took each request whole before KELVIN read it, so the server's times below are KELVIN's own, without the upload. The client kept one connection per key and sent each picture as raw bytes (Meridian Binary 1). The test's earlier runs, as JSON with a kept connection and as JSON with a new connection for every request, are kept under runs/.

| | |
|---|---|
| requests at the server | 2 230, equal to this run's 2 230, all answered 200, all sent as MB1 |
| the server busy | 436.8 s of a 13 min 2 s run (56 %) |
| KELVIN's own time, a picture lived and saved | n 1 996: p50 225 ms, p90 282 ms, max 650 ms |
| KELVIN's own time, a picture that saved nothing | n 234 (228 asks, 2 checks that the memories were new, and 4 pictures that gave it nothing to keep): p50 63 ms, p90 114 ms, max 163 ms |
| disk after (these memories) | 7.41 MB |
| request / answer bodies | 329.6 MB / 0.55 MB (the same requests as JSON: 439.2 MB) |
| processor, memory, network | not attributable to this test: another user's clip requests ran on the same server in the same window |
| what you wait, split | of a p50 tell of 594 ms the server's share is 225 ms, of a p50 ask of 440 ms it is 63 ms; the rest is sending the picture (about 0.13–0.14 MB as raw bytes) |
