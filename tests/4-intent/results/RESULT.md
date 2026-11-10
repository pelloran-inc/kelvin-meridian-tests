# Test 4 · intent, and "none of the above" · result

Address: our test address (a test door of our own, on the published release 5ddaa4fc, reached over the public internet with TLS like any tester's address), release 5ddaa4fc, run record `runs/2026-11-10T10-09-24+0100-intent`; address family: IPv4 only.

KELVIN lived 15100 requests once each (in one request, 159.5 s) and was asked 5500 it had never seen.

| | KELVIN | control (intents shuffled) |
|---|---|---|
| intent right (of 4500) | 3821 (0.8491) | 19 (0.0042) |
| "none of the above" right (of 1000) | 337 (0.3370) | 317 (0.3170) |
| all 5500 | 0.7560 | 0.0611 |
| time per ask, p50 / p90 | 266.6 / 296.8 ms | |

The control breaks: KELVIN right where the control is wrong 3803 times, the other way round 1 times (sign test p < 1e-300).

Times include the network between you and the address.

Requests sent again because their upload broke before the body was whole (the door never received them whole): 0. Each broken attempt is in the run record.

## At the server (measured by the address's operator, release 5ddaa4fc, 2026-11-10 09:09:24–10:00:59 UTC)

The address took each request whole before KELVIN read it, so the server's times below are KELVIN's own, without the upload. Processor, memory and network were sampled once a second over the whole run. The client's 159.5 s per teach is the server's 156.4 s plus the upload and the answer's way back.

| | |
|---|---|
| requests at the server | 11 004, equal to this run's 11 004, all answered 200, none sent again |
| the server busy | 485.4 s of a 51.6 min run (15.7 %) |
| KELVIN's own time, an ask | n 11 000: p50 14.7 ms, p90 23.4 ms, max 65.0 ms |
| KELVIN's own time, a teach (15 100 lived) | 156.4 s for KELVIN's memory and 156.4 s for the control's, one after the other; each memory a file of 12.2 MB |
| processor | 3 439 core-seconds; 16 cores at its busiest second |
| memory | peak 2.23 GB, 1.18 GB after |
| disk after (these memories) | 24.4 MB for the 2 memories |
| network at the address | 90.1 MB received, 101.3 MB sent |
| request / answer bodies | 59.8 MB / 41.2 MB |
