"""The one client every demo scene and every benchmark section uses. Python's standard library only.

- The address comes from MERIDIAN_URL (https://<your address>, given with your key).
- The key comes from MERIDIAN_KEY, or, for a benchmark that keeps several memories, from the file MERIDIAN_KEYS_FILE
  (one line a memory: `name<TAB>key`, the file readable by you only). A key is never printed, logged or written.
- One kept HTTPS connection per key (TCP keepalive on), reused for the key's next request; a connection idle for a
  minute, or closed by the server, is replaced before anything is sent. Every record line says "new" or "reused".
- The busy and limit rule: one request in flight per key, at most 120 a minute per key (paced here, so the limit is
  rarely met); 503 and 429 wait the server's Retry-After and ask again, up to five times; 413 (the memory is full) is
  returned as it is. Tests may ask several memories side by side, each on its own key.
- Every request and its answer go into the run's record (runs/<date>-<name>/requests.jsonl): when it was sent (UTC), the status, the time,
  the bytes each way and the answer exactly as the server sent it. A request's pictures, clips and sounds are recorded
  by their sha256, not their bytes.
"""
import datetime
import hashlib
import http.client
import json
import os
import select
import socket
import ssl
import stat
import sys
import threading
import time
import urllib.parse

RETRIES = 5
PER_MINUTE = 120  # a tester key's limit
SEND_BROKE_RETRIES = 3  # a request whose upload broke before it was whole (see _send_broke)


def _keepalive(sock):
    """TCP keepalive on a request's connection (a probe after 60 s of quiet, then every 30 s): a teach can keep the
    connection silent for minutes while the door works, and some routers drop a connection that looks idle that long."""
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    for name, value in (("TCP_KEEPALIVE", 60), ("TCP_KEEPIDLE", 60), ("TCP_KEEPINTVL", 30), ("TCP_KEEPCNT", 8)):
        opt = getattr(socket, name, None)
        if opt is not None:
            try:
                sock.setsockopt(socket.IPPROTO_TCP, opt, value)
            except OSError:
                pass


class _KeepAliveHTTPS(http.client.HTTPSConnection):
    def connect(self):
        super().connect()
        _keepalive(self.sock)


class _KeepAliveHTTP(http.client.HTTPConnection):
    def connect(self):
        super().connect()
        _keepalive(self.sock)


IDLE_REUSE_S = 60  # a connection idle longer than this is not reused: servers close idle ones (nginx after about 75 s)


def _dropped(conn):
    """True when a kept connection was closed by the server while it was idle: nothing is expected on an idle HTTP/1.1
    connection, so anything readable on it (its close) means it cannot carry the next request."""
    sock = getattr(conn, "sock", None)
    if sock is None:
        return True
    try:
        readable, _, _ = select.select([sock], [], [], 0)
    except (OSError, ValueError):
        return True
    return bool(readable)


def _pin_family():
    """MERIDIAN_FAMILY=4 or 6 sends every request over IPv4 or IPv6 only (an option to try if large uploads break on your
    path); the run's record names which family it used."""
    want = {"4": socket.AF_INET, "6": socket.AF_INET6}.get(os.environ.get("MERIDIAN_FAMILY", ""))
    if want is None or getattr(socket.getaddrinfo, "_pinned", False):
        return
    real = socket.getaddrinfo

    def pinned(host, *a, **k):
        return [x for x in real(host, *a, **k) if x[0] == want]
    pinned._pinned = True
    socket.getaddrinfo = pinned


def _local():
    """A check against a door on this machine (MERIDIAN_LOCAL=1, address http://127.0.0.1:…): there the memory is named
    by the KELVIN-Memory header instead of being chosen by a key. For our own checks before a run; a tester never needs it."""
    return os.environ.get("MERIDIAN_LOCAL") == "1" and os.environ.get("MERIDIAN_URL", "").startswith("http://127.0.0.1")


def _keys():
    """The memory names and their keys: one key (MERIDIAN_KEY) or a file (MERIDIAN_KEYS_FILE)."""
    if _local():
        return {}
    path = os.environ.get("MERIDIAN_KEYS_FILE")
    if path:
        mode = os.stat(path).st_mode
        if mode & (stat.S_IRWXG | stat.S_IRWXO):
            sys.exit(f"the keys file {path} must be readable by you only (chmod 600)")
        keys = {}
        for line in open(path):
            if line.strip() and not line.startswith("#"):
                name, key = line.rstrip("\n").split("\t", 1)
                keys[name] = key.strip()
        return keys
    key = os.environ.get("MERIDIAN_KEY")
    if not key:
        sys.exit("set MERIDIAN_KEY (your key) or MERIDIAN_KEYS_FILE, and MERIDIAN_URL (your address)")
    return {None: key}


class Meridian:
    """One address, its keys, and the run's record."""

    def __init__(self, name, record=True):
        self.url = os.environ.get("MERIDIAN_URL", "").rstrip("/")
        if not self.url.startswith("https://") and not self.url.startswith("http://127.0.0.1"):
            sys.exit("set MERIDIAN_URL to your address: https://<your address>, given with your key")
        self.keys = _keys()
        _pin_family()
        self.record = None
        self._lock = threading.Lock()  # the run record is shared by every memory's thread
        self._key_locks = {}  # one request in flight per key
        self._last = {}  # the time of each key's last request, for pacing
        self._conns = {}  # one kept connection per key, and when it was last used
        u = urllib.parse.urlsplit(self.url)
        self._host, self._port, self._https = u.hostname, u.port, u.scheme == "https"
        self._tls = ssl.create_default_context() if self._https else None
        if record:
            stamp = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H-%M-%S%z")
            runs = "runs-local" if _local() else "runs"  # a local check never mixes with the published runs
            self.dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), runs, f"{stamp}-{name}")
            os.makedirs(self.dir, exist_ok=False)
            self.record = open(os.path.join(self.dir, "requests.jsonl"), "w")
            meta = {"run": name, "started": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                    "address_family": {"4": "IPv4 only", "6": "IPv6 only"}.get(os.environ.get("MERIDIAN_FAMILY", ""), "any"),
                    "address": self.url, "release": os.environ.get("MERIDIAN_RELEASE", "not stated"), "memories": len(self.keys)}
            json.dump(meta, open(os.path.join(self.dir, "run.json"), "w"), indent=1)

    def key(self, memory=None):
        if _local():
            return "local"
        if memory in self.keys:
            return self.keys[memory]
        if None in self.keys and len(self.keys) == 1:
            return self.keys[None]
        sys.exit(f"no key for the memory '{memory}' in MERIDIAN_KEYS_FILE")

    def request(self, method, path, body=None, memory=None, headers=None):
        """One request with the busy and limit rule. Returns (status, answer as JSON or None, raw bytes, ms, bytes sent)."""
        data = None if body is None else json.dumps(body).encode()
        key = self.key(memory)
        hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", **(headers or {})}
        if _local():
            hdr["KELVIN-Memory"] = memory or "demo"
            key = memory or "demo"
        with self._lock:
            key_lock = self._key_locks.setdefault(key, threading.Lock())
        with key_lock:
            return self._request(method, path, body, data, hdr, memory, headers, key)

    def _connection(self, key):
        """The key's kept connection when it can carry the next request; else a new one, connected now, before anything
        of the request is sent. Returns (connection, "new" or "reused")."""
        kept = self._conns.get(key)
        if kept and time.monotonic() - kept[1] < IDLE_REUSE_S and not _dropped(kept[0]):
            return kept[0], "reused"
        if kept:
            kept[0].close()
        cls = _KeepAliveHTTPS if self._https else _KeepAliveHTTP
        conn = cls(self._host, self._port, timeout=600, **({"context": self._tls} if self._https else {}))
        conn.connect()
        self._conns[key] = (conn, time.monotonic())
        return conn, "new"

    def _forget(self, key):
        kept = self._conns.pop(key, None)
        if kept:
            kept[0].close()

    def _record_line(self, line):
        if self.record:
            with self._lock:
                self.record.write(json.dumps(line, ensure_ascii=False) + "\n")
                self.record.flush()

    def _request(self, method, path, body, data, hdr, memory, headers, key):
        broke = 0
        attempt = 0
        while attempt <= RETRIES:
            attempt += 1
            wait_for = 0 if _local() else self._last.get(key, 0) + 60 / PER_MINUTE - time.monotonic()
            if wait_for > 0:
                time.sleep(wait_for)
            self._last[key] = time.monotonic()
            sent_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")
            t0 = time.perf_counter()
            base = {"at": sent_at, "method": method, "path": path, "memory": memory, "headers": dict(headers or {}),
                    "body": _without_media(body)}
            try:
                conn, how = self._connection(key)
            except OSError as e:
                # The connection could not be made: nothing of the request was sent, so it may be sent on a new one.
                ms = (time.perf_counter() - t0) * 1e3
                again = broke < SEND_BROKE_RETRIES
                self._record_line({**base, "status": None, "ms": round(ms, 2), "connection": "not made",
                                   "error": f"{type(e).__name__}: {e}", "sent_again": again})
                if again:
                    broke += 1
                    attempt -= 1
                    time.sleep(5 * broke)
                    continue
                stop(f"No connection to the address for the memory '{memory}' ({type(e).__name__}: {e}). Nothing was sent; "
                     f"this run stops here.")
            try:
                conn.request(method, path, body=data, headers=hdr)
                resp = conn.getresponse()
                status, raw, wait = resp.status, resp.read(), resp.getheader("Retry-After")
                if resp.will_close:
                    self._forget(key)
                else:
                    self._conns[key] = (conn, time.monotonic())
            except (OSError, http.client.HTTPException) as e:
                ms = (time.perf_counter() - t0) * 1e3
                self._forget(key)
                again = _send_broke(e) and broke < SEND_BROKE_RETRIES
                self._record_line({**base, "status": None, "ms": round(ms, 2), "connection": how,
                                   "error": f"{type(e).__name__}: {e}", "sent_again": again})
                if again:
                    # The upload broke before the body was whole, so the door cannot have read it (a door refuses a body
                    # that is not whole): sending it again cannot live anything twice.
                    broke += 1
                    attempt -= 1
                    time.sleep(5 * broke)
                    continue
                # Any other request without an answer (a timeout, a connection lost while waiting for the answer): the
                # door may have lived it, so it is never sent again, and the run stops here and is void.
                stop(f"No answer to a request for the memory '{memory}' after {ms / 1000:.0f} s ({type(e).__name__}: {e}). "
                     f"It may have been lived anyway, so it is not sent again and this run is void. Start again from "
                     f"new memories (on our test address: ask for them fresh).")
            ms = (time.perf_counter() - t0) * 1e3
            if status in (429, 503) and attempt <= RETRIES:
                time.sleep(float(wait or 5))
                continue
            break
        try:
            answer = json.loads(raw)
        except ValueError:
            answer = None
        self._record_line({**base, "status": status, "ms": round(ms, 2), "connection": how,
                           "bytes_sent": len(data or b""), "bytes_received": len(raw), "answer": answer})
        return status, answer, raw, ms, len(data or b"")

    def ask(self, body, memory=None, headers=None):
        return self.request("POST", "/v1/systemone", body, memory, headers)

    def models(self):
        return self.request("GET", "/v1/models")


def _send_broke(e):
    """True when the connection broke while the request was still being sent ("Broken pipe"): the body never arrived
    whole. A break while waiting for the answer (a reset, a timeout) is not this, and never sent again."""
    reason = getattr(e, "reason", e)
    return isinstance(reason, BrokenPipeError) or getattr(reason, "errno", None) == 32


def stop(message, code=1):
    """Stop the whole run at once, every thread with it. A void run must not send one more request, and an exit raised in
    one thread would let the others go on."""
    print(message, file=sys.stderr, flush=True)
    sys.stdout.flush()
    os._exit(code)


def _without_media(body):
    """The request as recorded: every base64 asset replaced by its sha256 and size."""
    if not isinstance(body, dict) or "assets" not in body:
        return body
    out = dict(body)
    out["assets"] = {}
    for name, a in body["assets"].items():
        a = dict(a)
        if "data_base64" in a:
            raw = a.pop("data_base64").encode()
            a["sha256_of_base64"] = hashlib.sha256(raw).hexdigest()
            a["base64_bytes"] = len(raw)
        out["assets"][name] = a
    return out


def asset(path, kind, fmt=None):
    """A file as the API's asset: kind "image" (a picture) or "video" (an mp4 clip); fmt, if given, its format (e.g. "mp4",
    "jpg"). The API also takes "sound" (flac or wav), which none of these tests sends."""
    import base64
    out = {"type": kind, "data_base64": base64.b64encode(open(path, "rb").read()).decode()}
    if fmt:
        out["format"] = fmt
    return out


def answer_of(answer, question):
    """KELVIN's answer to one question: (choice or None, confidence, silent)."""
    a = ((answer or {}).get("answers") or {}).get(question) or {}
    silent = bool(a.get("silent"))
    return (None if silent else a.get("choice")), a.get("confidence"), silent
