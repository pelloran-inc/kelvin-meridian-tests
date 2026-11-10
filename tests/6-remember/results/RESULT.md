# Test 6 · remember what you were told · result

Address: our test address (a test door of our own, on the published release 5ddaa4fc, reached over the public internet with TLS like any tester's address), release 5ddaa4fc, run record `runs/2026-11-10T17-19-53+0100-remember`; address family: IPv4 only.

KELVIN was told 346 facts, then asked in new requests that did not carry them.

| | result |
|---|---|
| a person's parent, ten names to choose from | **345 of 345 right** (0 silent) |
| the same questions asked again | 345 of 345 answers byte for byte the same |
| people whose parents it was never told | 332 of 332 silent, 0 answered |
| the same questions in another memory (nothing told there) | 345 of 345 silent |
| time per ask, p50 / p90 | 103.6 / 113.2 ms |

The control (parents shuffled among the people): KELVIN followed what it was told 345 of 345 times, and so was right against the truth only 4 times. The control breaks (sign test p = 2.2e-103).

Times include the network between you and the address.

Requests sent again because their upload broke before the body was whole (the door never received them whole): 0. Each broken attempt is in the run record.

## At the server (measured by the address's operator, release 5ddaa4fc, 2026-11-10 16:19:54–16:34:25 UTC)

The address took each request whole before KELVIN read it, so the server's times below are KELVIN's own, without the upload. The client kept one connection per key and reused it (each request's record says "new" or "reused"). The test's earlier run, with a new connection for every request, is kept under runs/ as well.

| | |
|---|---|
| requests at the server | 1 729, equal to this run's 1 729, all answered 200 |
| the server busy | 30.7 s of a 14 min 31 s run (3.5 %) |
| KELVIN's own time, an ask | n 1 715: p50 17.7 ms, p90 18.0 ms, max 25.8 ms |
| KELVIN's own time, a teach (50 facts) | n 14: p50 579 ms, p90 584 ms, max 606 ms |
| processor (sampled, 99.3 % of the run) | 28.7 core-seconds; at its busiest second 0.92 cores |
| memory | peak 1.32 GB, 1.32 GB after, for everything the server held |
| disk after (these memories) | 0.23 MB |
| network at the address | 1.53 MB received, 1.31 MB sent |
| what you wait, split | a p50 ask of 103.6 ms here is the server's 17.7 ms plus about 86 ms of network |
