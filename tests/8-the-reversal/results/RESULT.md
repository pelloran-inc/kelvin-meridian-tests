# Test 8 · the reversal · result

Address: our test address (a test door of our own, on the published release named next, reached over the public internet with TLS like any tester's address), release 8f2d6cdb, run record `runs/2026-11-11T15-05-09+0100-reversal`; address family: any.

KELVIN was told 346 facts one way only (child → parent), then asked both ways in new requests that did not carry them.

| | right | wrong | silent | time per ask, p50 |
|---|---|---|---|---|
| forward: whose mother or father is asked (`state.subject`) | **50 of 50** | 0 | 0 | 99.5 ms |
| reverse: whose child is asked (`state.object`), every child held and no one else | **50 of 50** | 0 | 0 | 117.4 ms |
| people who are no one's parent | — | 0 answered | **50 of 50** | 109.4 ms |

Of the reverse questions, 10 ask about a parent with several children; all children were held in 10 of them.

The control (the reverse questions asked with the relation swapped, mother ↔ father): the same children given 0 of 50 times, silent 50 times. The control breaks (sign test p = 8.9e-16).

Times include the network between you and the address.

Requests sent again because their upload broke before the body was whole (the door never received them whole): 0. Each broken attempt is in the run record.
