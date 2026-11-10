# Changelog

All notable changes to these tests are listed here, newest first. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). A release's version is its git tag. How a release is
made: [RELEASING.md](RELEASING.md).

## [Unreleased]

## [0.0.3] - 2026-11-10

### Changed

- **The client keeps its connection.** `meridian.py` keeps one HTTPS connection per key, with TCP keepalive, and reuses
  it for the key's next request.
  - A connection idle for a minute, or closed by the server, is replaced before anything of the request is sent.
  - A connection that cannot be made, where nothing was sent, is tried again on a new one, at most three times.
  - Every other request without an answer still stops the run as void, as before.
  - Every request's record says `"connection": "new"` or `"reused"`.
- **Tests 6 and 2 were run again with it,** on fresh memories of the same release, `5ddaa4fc`:
  - test 6: all 1 712 answers byte for byte those of the earlier run. A text question now takes 104 ms instead of
    252 ms (p50, network included); the server's own time is 17.7 ms.
  - test 2: all 114 answers in each memory equal to the earlier run's. A picture asked takes 479 ms instead of 583 ms,
    a picture lived 663 ms instead of 767 ms; the server's own time is 65 ms and 244 ms.
  - Their `results/` are now these runs. The earlier runs stay under `runs/`, as the earlier client's.
- **README, "Speed, on both sides",** and REPRODUCE.md: the new times beside the earlier client's, named as such, and
  "Keep your connection".

### Added

- Tests 6 and 2's "At the server" now give processor, memory and network too, sampled over their whole runs.

## [0.0.2] - 2026-11-10

### Fixed

- **`tests/keys_needed.py` on Python 3.10,** the oldest Python the tests support. It failed with a `NameError` where a
  test builds its memory names in a list comprehension (tests 1 and 3), so v0.0.1's CI was red. The tests, their
  results and their records are unchanged.

### Changed

- RELEASING.md: the gate runs on Python 3.10.

## [0.0.1] - 2026-11-10

### Added

- **The first public release:** a demo and seven tests of KELVIN Meridian's API, each with a control that must break,
  and our own result of each on release `5ddaa4fc`.
- **The demo,** `demo.py`: eight short scenes with `--autoplay` or `--step`. Each run makes up its own names.
- **The seven tests,** one command each, under `tests/`:
  - 1 · typed decisions, scored by the dataset's own scorer, fetched unchanged
  - 2 · a picture: this one, else its kind (1 000 told; the server kept 998)
  - 3 · a sound, an object and its name, with a fetch script for its clip list
  - 4 · intent, and "none of the above"
  - 5 · when to call a tool
  - 6 · remember what you were told, on 346 CC0 facts from Wikidata
  - 7 · say "I don't know"
- **The client,** `meridian.py`, Python's standard library only:
  - one key per memory, from a file readable by you only; a key is never printed or written
  - 120 requests a minute per key, and the server's Retry-After on 429 and 503
  - a request with no answer is never sent again, and the run stops as void; only an upload that broke before the
    request was whole is sent again, at most three times, and recorded
  - TCP keepalive on every connection, so a long wait never looks idle on the way
  - `MERIDIAN_FAMILY=4|6` to send over IPv4 or IPv6 only
  - every request and answer recorded in the run's record, pictures and clips only as their sha256
- **The run guards:** every test checks that its memories are new before it teaches anything; tests 1 to 5 run only
  on a door of one's own (`MERIDIAN_OWN_DOOR=1`).
- **Our results:** each test's `results/RESULT.md`, with the server's side as its operator measured it, and every run
  record under `runs/`, the four void runs with their causes.
- **REPRODUCE.md:** every number the README cites, with its run record, field and command.
- **CI:** `.github/workflows/ci.yml`, the same checks as `ci/gates.sh`, and a secret scan of every commit.

[Unreleased]: https://github.com/pelloran-inc/kelvin-meridian-tests/compare/v0.0.3...HEAD
[0.0.3]: https://github.com/pelloran-inc/kelvin-meridian-tests/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/pelloran-inc/kelvin-meridian-tests/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/pelloran-inc/kelvin-meridian-tests/releases/tag/v0.0.1
