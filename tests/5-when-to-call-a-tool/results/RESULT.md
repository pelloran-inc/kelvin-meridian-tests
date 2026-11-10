# Test 5 · when to call a tool · result

Address: our test address (a test door of our own, on the published release 5ddaa4fc, reached over the public internet with TLS like any tester's address), release 5ddaa4fc, run record `runs/2026-11-10T00-03-02+0100-when-to-call-a-tool`; address family: not recorded (the system's default).

KELVIN lived 1835 items (in one request, 50.2 s) and was asked 1216 items of request families it never met.

| | KELVIN | control (reactions shuffled) |
|---|---|---|
| right (of 1216) | 816 (0.6711) | 430 (0.3536) |
| … where the right reaction is "call a tool" (of 432) | 298 | 170 |
| … where the right reaction is "ask for what is missing" (of 352) | 208 | 95 |
| … where the right reaction is "say it cannot" (of 432) | 310 | 165 |
| silent | 0 | 0 |
| time per ask, p50 / p90 | 244.8 / 260.5 ms | |

The control breaks: KELVIN right where the control is wrong 502 times, the other way round 116 times (sign test p = 2e-58).

Times include the network between you and the address.

## At the server (measured by the address's operator, release 5ddaa4fc, 2026-11-09 23:03:03–23:14:09 UTC)

These figures were measured before the address took each request whole before KELVIN reads it: the server's times below include reading the request as it arrived over our uplink.

| | |
|---|---|
| requests at the server | 2 436, equal to this run's 2 436, all answered 200 |
| the server busy | 80.8 s of an 11 min 6 s run (12 %) |
| KELVIN's own time, an ask | n 2 432: p50 12.0 ms, p90 19.0 ms, max 71.7 ms |
| KELVIN's own time, a teach (1 835 items) | 20.6 s (KELVIN's memory) and 29.3 s (the control's) |
| disk after (these memories) | 21.62 MB |
| request / answer bodies | 19.67 MB / 0.72 MB |
| processor, memory, network | not measured for this run |
