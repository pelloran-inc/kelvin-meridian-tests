# Test 1 · typed decisions · result

Address: our test address (a test door of our own, on the published release 5ddaa4fc, reached over the public internet with TLS like any tester's address), release 5ddaa4fc, run record `runs/2026-11-09T23-59-37+0100-typed-decisions`; address family: not recorded (the system's default).

| | accuracy ↑ | KL from gold ↓ | Brier ↓ | ECE ↓ |
|---|---|---|---|---|
| **KELVIN, all four areas** | 0.7060 | 0.1621 | 0.0886 | 0.1313 |
| control: the lived answers shuffled | 0.5075 | 0.3303 | 0.1808 | 0.0558 |
| guessing (every option alike) | 0.2765 | 0.4445 | 0.2382 | 0.0450 |
| the training cases' average answer (no learning) | 0.4810 | 0.3274 | 0.1811 | 0.0361 |

The control breaks: KELVIN right where the control is wrong 509 times, the other way round 112 times (sign test p = 1.2e-61).

| area | KELVIN | control (shuffled) | ask p50 / p90 ms |
|---|---|---|---|
| agent traces | 0.624 | 0.348 | 267.0 / 292.3 |
| customer service | 0.636 | 0.460 | 285.0 / 328.0 |
| invoices | 0.844 | 0.620 | 273.5 / 318.4 |
| security incidents | 0.720 | 0.602 | 262.1 / 286.7 |

Right per question (of 100), by the scorer's own rule:

- **agent traces:** action 57, needs_review 78, outcome 58, risk 64, urgency 55
- **customer service:** action 54, category 85, churn_risk 57, needs_human 71, urgency 51
- **invoices:** discrepancy_severity 82, disposition 78, duplicate 89, matches_order 95, urgency 78
- **security incidents:** credential_compromise 67, disposition 81, severity 64, true_positive 87, urgency 61

Times include the network between you and the address.

## At the server (measured by the address's operator, release 5ddaa4fc, 2026-11-09 22:59:37–23:03:02 UTC)

These figures were measured before the address took each request whole before KELVIN reads it: the server's times below include reading the request as it arrived over our uplink.

| | |
|---|---|
| requests at the server | 816, equal to this run's 816, all answered 200 |
| the server busy | 125.7 s of a 3 min 25 s run (61 %) |
| KELVIN's own time, an ask | n 800: p50 30.5 ms, p90 46.9 ms, max 110 ms |
| KELVIN's own time, a teach (300 cases) | n 8: median 13.6 s, max 23.5 s (the client's longer teach times include waiting for another area's teach: the server answers one request at a time) |
| disk after (these memories) | 16.61 MB |
| request / answer bodies | 5.66 MB / 1.12 MB |
| memory | the server's peak by the end of this run 1.77 GB (1.52 GB then), for everything it held |
| processor, network | not measured for this run |
