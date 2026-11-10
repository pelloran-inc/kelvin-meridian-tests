# This run is void

One memory at a time. 8 lives went through (320 requests, all answered). Then an ask by the name in the made-up names'
life 3 got no answer: the connection broke after 4 s while it was being sent ("Broken pipe"). The run stopped and does
not count; nothing of it is in the test's results.

A fault of our own script, found here and fixed: the stop ended only the thread it happened in, so the next life
(made-up names, life 4) began and lived two things before its third request broke as well. Since then a stop ends the
whole run at once, every thread with it.

The memories were emptied before the next run.

What the address's own logs show (our test address, read by its operator): both breaks (00:58Z and 01:08Z) were bodies that stopped
arriving a few seconds into the upload; the server kept waiting and closed them after 60 s without data. Nothing on the
server changed or restarted then. The cause between this machine and the address is not known.
