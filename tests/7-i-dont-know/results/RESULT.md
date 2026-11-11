# Test 7 · say "I don't know" · result

Address: our test address (a test door of our own, on the published release named next, reached over the public internet with TLS like any tester's address), release 5ddaa4fc, run record `runs/2026-11-09T23-50-07+0100-i-dont-know`; address family: not recorded (the system's default).

KELVIN was told 170 facts. Every question offered ten names and "none of the above".

| question | right answer | KELVIN right | KELVIN said "none of the above" | control (nothing told): right |
|---|---|---|---|---|
| told | the parent it was told | 169 of 169 | 0 | 0 of 169 |
| the truth left out | none of the above | 169 of 169 | 169 | 169 of 169 |
| a relation not told | none of the above | 51 of 51 | 51 | 51 of 51 |
| never told | none of the above | 169 of 169 | 169 | 169 of 169 |

On the 389 questions it could not know, KELVIN said "none of the above" 389 times. Right overall: 558 of 558. Time per ask p50 / p90: 249.8 / 268.0 ms.

The control breaks: on the told questions KELVIN was right where the control was wrong 169 times, the other way round 0 times (sign test p = 1.3e-51).

Times include the network between you and the address.

## At the server (measured by the address's operator, release 5ddaa4fc, 2026-11-09 22:50:08–22:59:37 UTC)

These figures were measured before the address took each request whole before KELVIN reads it: the server's times below include reading the request as it arrived over our uplink.

| | |
|---|---|
| requests at the server | 1 122, equal to this run's 1 122, all answered 200 |
| the server busy | 8.2 s of a 9 min 29 s run (1.4 %) |
| KELVIN's own time, an ask | n 1 118: p50 0.2 ms, p90 17.8 ms, max 30.9 ms (half the asks go to the memory told nothing, answered silent at once) |
| KELVIN's own time, a teach (50 facts) | n 4: p50 499 ms, max 531 ms |
| disk after (these memories) | 0.06 MB |
| request / answer bodies | 0.52 MB / 0.47 MB |
| processor, memory, network | not measured for this run |
