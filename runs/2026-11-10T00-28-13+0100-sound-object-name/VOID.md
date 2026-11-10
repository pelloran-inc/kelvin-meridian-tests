# This run is void

Three asks by the name (about 20.7 MB each, four clips) got no answer: the connection broke while they were being sent
(86–89 s, "Broken pipe"). They lived nothing, but by the rule no request without an answer is sent again, so the run
stopped and does not count. Nothing of it is in the test's results.

Why (found in the address's own logs): six memories were asked side by side, so up to six 20 MB uploads shared one
uplink. The door reads one request at a time and reads a body as it arrives; a slow upload held it, the other uploads
stalled behind it, and the address closes an upload after 60 s without progress. The memories were emptied, and the
test was run again with one memory at a time (`--side-by-side 1`).
