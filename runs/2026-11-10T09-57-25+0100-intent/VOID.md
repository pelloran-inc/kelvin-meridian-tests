# This run is void

Both memories' teach requests (15 100 lived requests each, one request per memory) were sent at 08:57:26Z. The door
answers one request at a time: it lived the control's in 157.7 s, then 'intent' in 155.6 s, and answered it 200 at
09:02:42Z, 316 s after it was sent (the address's own log). That answer never reached this machine: the connection had
been silent for about five minutes while the door worked, and something on the path between this machine and the
address dropped it (nothing was logged on the server, whose limits are 600 s). The client gave up after 600 s with no
answer, did not send it again, and stopped the run; nothing of it is in the test's results. 'intent' had lived
although the client did not see it, so the run is rightly void.

Since then: the two teach requests go one after the other (about 160 s of silence each), and every connection keeps
itself alive (TCP keepalive after 60 s of quiet), so a long wait never looks idle on the way.
