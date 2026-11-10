# Test 6 · remember what you were told · result

Address: our test address (a test door of our own, on the published release 5ddaa4fc, reached over the public internet with TLS like any tester's address), release 5ddaa4fc, run record `runs/2026-11-09T23-35-32+0100-remember`; address family: not recorded (the system's default).

KELVIN was told 346 facts, then asked in new requests that did not carry them.

| | result |
|---|---|
| a person's parent, ten names to choose from | **345 of 345 right** (0 silent) |
| the same questions asked again | 345 of 345 answers byte for byte the same |
| people whose parents it was never told | 332 of 332 silent, 0 answered |
| the same questions in another memory (nothing told there) | 345 of 345 silent |
| time per ask, p50 / p90 | 252.1 / 271.5 ms |

The control (parents shuffled among the people): KELVIN followed what it was told 345 of 345 times, and so was right against the truth only 4 times. The control breaks (sign test p = 2.2e-103).

Times include the network between you and the address.

## At the server (measured by the address's operator, release 5ddaa4fc, 2026-11-09 22:35:32–22:50:07 UTC)

These figures were measured before the address took each request whole before KELVIN reads it: the server's times below include reading the request as it arrived over our uplink.

| | |
|---|---|
| requests at the server | 1 729, equal to this run's 1 729, all answered 200 |
| the server busy | 29.5 s of a 14 min 35 s run (3.4 %) |
| KELVIN's own time, an ask | n 1 715: p50 17.5 ms, p90 17.9 ms, max 24.9 ms |
| KELVIN's own time, a teach (50 facts) | n 14: p50 497 ms, p90 527 ms, max 533 ms |
| disk after (these memories) | 0.23 MB |
| request / answer bodies | 0.79 MB / 0.67 MB |
| processor, memory, network | not measured for this run |
