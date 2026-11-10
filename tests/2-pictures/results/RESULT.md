# Test 2 · a picture: this one, else its kind · result

Address: our test address (a test door of our own, on the published release 5ddaa4fc, reached over the public internet with TLS like any tester's address), release 5ddaa4fc, run record `runs/2026-11-10T17-34-26+0100-pictures`; address family: IPv4 only.

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

Times: a tell 662.6 / 1022.5 ms, an ask 479.1 / 828.9 ms (p50 / p90), including the network between you and the address. Sent: a tell 0.19 MB, an ask 0.17 MB (the picture as base64, p50); an answer 195 bytes.

Requests sent again because their upload broke before the body was whole (the door never received them whole): 0. Each broken attempt is in the run record.

## At the server (measured by the address's operator, release 5ddaa4fc, 2026-11-10 16:34:27–16:48:26 UTC)

The address took each request whole before KELVIN read it, so the server's times below are KELVIN's own, without the upload. The client kept one connection per key and reused it (each request's record says "new" or "reused"). The test's earlier run, with a new connection for every request, is kept under runs/ as well.

| | |
|---|---|
| requests at the server | 2 230, equal to this run's 2 230, all answered 200 |
| the server busy | 478.2 s of a 14 min run (57 %) |
| KELVIN's own time, a picture lived and saved | n 1 996: p50 244 ms, p90 311 ms, max 362 ms |
| KELVIN's own time, a picture that saved nothing | n 234 (228 asks, 2 checks that the memories were new, and 4 pictures that gave it nothing to keep): p50 65 ms, p90 123 ms, max 172 ms |
| processor (sampled, the whole run) | 474.6 core-seconds; at its busiest second 1.01 cores (a picture is read on one core) |
| memory | peak 1.35 GB, 1.35 GB after, for everything the server held |
| disk after (these memories) | 7.41 MB |
| network at the address | 450.1 MB received, 9.9 MB sent |
| what you wait, split | of a p50 tell of 663 ms the server's share is 244 ms, of a p50 ask of 479 ms it is 65 ms; the rest, about 0.4 s, is sending the picture (0.17–0.19 MB as base64) |
