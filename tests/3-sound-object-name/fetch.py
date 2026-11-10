#!/usr/bin/env python3
"""Test 3 · fetch the 54 clips named in clips.json into data/clips/. No clip is ever stored in this repository.

    python3 tests/3-sound-object-name/fetch.py                 # the default: route 1, the mirror
    python3 tests/3-sound-object-name/fetch.py mirror          # route 1: the clips' exact bytes, from a public mirror
    python3 tests/3-sound-object-name/fetch.py youtube         # route 2, the fallback: from YouTube by id and start second
    python3 tests/3-sound-object-name/fetch.py folder <DIR>    # route 1's bytes from a copy you already hold

Route 1 · the mirror, the default. The clips come out of one archive of the Hugging Face mirror Loie/VGGSound (pinned
revision). You stream about 17 GB once; the archive is never stored, and only the 54 clips are kept (about 159 MB), as
they are, bit for bit, each equal to its pinned sha256 or removed. These are the bytes our recorded run used, so the
result reproduces. The clips belong to their YouTube uploaders.

Route 2 · YouTube. Each clip is fetched from its YouTube video (yt-dlp, then ffmpeg cuts the 10 seconds from the start
second). The bytes cannot be pinned: YouTube re-encodes, and videos are taken down. A clip that cannot be fetched is named
as gone, and run.py says how many asks the run lost. Its results may differ from the recorded ones.

Folder · route 1's bytes from a folder you already hold, files named <youtube_id>_<start>.mp4 (as VGGSound names them);
each is checked by its pinned sha256 and copied.

The route is written to data/fetch.json, and run.py names it in every result. One route per data/ folder: to change the
route, remove tests/3-sound-object-name/data/ first. Python's standard library only (route 2 also needs yt-dlp and ffmpeg).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
CLIPS = os.path.join(DATA, "clips")
RECORD = os.path.join(DATA, "fetch.json")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load():
    return json.load(open(os.path.join(HERE, "clips.json")))


def start_record(route):
    """One route per data/ folder."""
    os.makedirs(CLIPS, exist_ok=True)
    if os.path.exists(RECORD):
        old = json.load(open(RECORD))
        if old.get("route") != route:
            sys.exit(f"data/ holds clips fetched by the route '{old.get('route')}'. To use '{route}', remove {DATA} first.")
        return old
    return {"route": route, "clips": {}}


def save(rec):
    rec["fetched"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    with open(RECORD + ".part", "w") as f:
        json.dump(rec, f, indent=1)
    os.replace(RECORD + ".part", RECORD)


def present(c):
    """A clip already in data/clips/ with its pinned bytes."""
    p = os.path.join(CLIPS, c["clip"] + ".mp4")
    return os.path.exists(p) and sha256_of(p) == c["sha256"]


class Resuming:
    """A read-only HTTP stream that reconnects at its offset (a Range request) after a dropped connection."""

    def __init__(self, url):
        self.url, self.pos, self.r, self.reconnects, self.total = url, 0, None, 0, None

    def _open(self):
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-", "User-Agent": "kelvin-meridian-tests"})
        self.r = urllib.request.urlopen(req, timeout=120)
        rng = self.r.headers.get("Content-Range", "")
        if self.pos and not rng.startswith(f"bytes {self.pos}-"):
            raise IOError(f"the server did not resume at {self.pos} ({rng!r})")
        if self.total is None and "/" in rng:
            self.total = int(rng.rsplit("/", 1)[1])

    def read(self, n=-1):
        for attempt in range(30):
            try:
                if self.r is None:
                    self._open()
                b = self.r.read(n)
                if not b and n != 0 and self.total is not None and self.pos < self.total:
                    raise IOError("connection closed early")
                self.pos += len(b)
                return b
            except Exception as e:  # noqa: BLE001 -- any network error: reconnect where we were
                self.reconnects += 1
                print(f"  reconnecting at byte {self.pos} ({e!r})", file=sys.stderr, flush=True)
                self.r = None
                time.sleep(min(60, 2 ** attempt))
        raise IOError("the stream failed after 30 reconnects")


def route_mirror(src):
    m = src["mirror"]
    rec = start_record("mirror")
    rec["source"] = {k: m[k] for k in ("repo", "revision", "file", "url", "bytes", "sha256")}
    want = {c["clip"]: c for c in src["clips"] if not present(c)}
    for c in src["clips"]:
        if c["clip"] not in want:
            rec["clips"][c["clip"]] = {"sha256": c["sha256"], "equal_to_pinned": True}
    if not want:
        save(rec)
        print(f"all {len(src['clips'])} clips are here, each equal to its pinned sha256")
        return
    print(f"streaming {m['file']} ({m['bytes'] / 1e9:.1f} GB, never stored) for {len(want)} clips; it stops when it has them all", flush=True)
    stream, t0, next_report = Resuming(m["url"]), time.time(), 1 << 30
    tmp = os.path.join(DATA, "tmp")
    os.makedirs(tmp, exist_ok=True)
    with tarfile.open(fileobj=stream, mode="r|gz") as tar:
        for member in tar:
            if stream.pos >= next_report:
                print(f"  {stream.pos / 2**30:.1f} GiB read, {len(src['clips']) - len(want)} of {len(src['clips'])} clips kept, {time.time() - t0:.0f} s", flush=True)
                next_report += 1 << 30
            base = os.path.basename(member.name)
            if not member.isreg() or not base.endswith(".mp4") or base[:-4] not in want:
                continue
            c = want[base[:-4]]
            part = os.path.join(tmp, base)
            h = hashlib.sha256()
            with tar.extractfile(member) as fin, open(part, "wb") as fout:
                for block in iter(lambda: fin.read(1 << 20), b""):
                    h.update(block)
                    fout.write(block)
            if h.hexdigest() != c["sha256"]:
                os.remove(part)
                rec["clips"][c["clip"]] = {"sha256": h.hexdigest(), "equal_to_pinned": False, "refused": "its sha256 is not the pinned one; removed"}
                print(f"  {c['clip']}: sha256 differs from the pinned one; removed and not used", flush=True)
            else:
                os.replace(part, os.path.join(CLIPS, base))
                rec["clips"][c["clip"]] = {"sha256": c["sha256"], "equal_to_pinned": True}
            del want[c["clip"]]
            save(rec)
            if not want:
                break
    shutil.rmtree(tmp, ignore_errors=True)
    for clip in want:
        rec["clips"][clip] = {"gone": f"not found in {m['file']}"}
    rec["stream"] = {"bytes_read": stream.pos, "seconds": round(time.time() - t0), "reconnects": stream.reconnects}
    save(rec)
    report(rec, src)


def route_folder(src, folder):
    rec = start_record("folder")
    rec["source"] = {"folder": os.path.abspath(folder), "note": "route 1's bytes from a copy held locally, each checked by its pinned sha256"}
    for c in src["clips"]:
        dest = os.path.join(CLIPS, c["clip"] + ".mp4")
        if not present(c):
            p = os.path.join(folder, c["clip"] + ".mp4")
            if not os.path.exists(p):
                rec["clips"][c["clip"]] = {"gone": f"not in {folder}"}
                continue
            got = sha256_of(p)
            if got != c["sha256"]:
                rec["clips"][c["clip"]] = {"sha256": got, "equal_to_pinned": False, "refused": "its sha256 is not the pinned one; not copied"}
                continue
            shutil.copyfile(p, dest + ".part")
            os.replace(dest + ".part", dest)
        rec["clips"][c["clip"]] = {"sha256": c["sha256"], "equal_to_pinned": True}
    save(rec)
    report(rec, src)


# Route 2: the closest YouTube form to the recorded clips (H.264 picture at 720 lines, AAC sound at 44 100 Hz), else the
# nearest the video offers. KELVIN refuses a sound not at 44 100 Hz; run.py counts such a clip's requests as not answered.
YT_FORMAT = ("bv*[vcodec^=avc1][height=720]+ba[acodec^=mp4a][asr=44100]/"
             "bv*[vcodec^=avc1][height<=720]+ba[acodec^=mp4a]/b[ext=mp4]")


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,sample_rate,duration",
                          "-of", "json", path], capture_output=True, text=True)
    try:
        return json.loads(out.stdout).get("streams", [])
    except ValueError:
        return []


def route_youtube(src):
    for tool in ("yt-dlp", "ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            sys.exit(f"route 2 needs {tool} on your PATH")
    rec = start_record("youtube")
    version = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True).stdout.strip()
    rec["source"] = {"youtube": "https://www.youtube.com/watch?v=<youtube_id>", "yt-dlp": version, "format": YT_FORMAT,
                     "cut": "ffmpeg: from the start second, 10 seconds; the picture re-encoded as H.264 (ffmpeg's default quality), the sound copied as it came",
                     "note": "the bytes cannot be pinned; results may differ from the recorded run"}
    tmp = os.path.join(DATA, "tmp")
    os.makedirs(tmp, exist_ok=True)
    for i, c in enumerate(src["clips"]):
        clip, dest = c["clip"], os.path.join(CLIPS, c["clip"] + ".mp4")
        if os.path.exists(dest) and "sha256" in rec["clips"].get(clip, {}):
            continue
        print(f"  [{i + 1}/{len(src['clips'])}] {clip}", flush=True)
        whole = os.path.join(tmp, clip + ".whole.mp4")
        r = subprocess.run(["yt-dlp", "-q", "--no-warnings", "--no-playlist", "-f", YT_FORMAT, "--merge-output-format", "mp4",
                            "-o", whole, f"https://www.youtube.com/watch?v={c['youtube_id']}"], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(whole):
            rec["clips"][clip] = {"gone": (r.stderr.strip().splitlines() or ["yt-dlp gave no file"])[-1][:300]}
            save(rec)
            continue
        r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(c["start"]), "-i", whole, "-t", "10",
                            "-map", "0:v:0", "-map", "0:a:0", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "copy",
                            "-movflags", "+faststart", dest + ".part.mp4"], capture_output=True, text=True)
        os.remove(whole)
        if r.returncode != 0:
            rec["clips"][clip] = {"gone": "ffmpeg could not cut it: " + r.stderr.strip()[-300:]}
            save(rec)
            continue
        os.replace(dest + ".part.mp4", dest)
        rec["clips"][clip] = {"sha256": sha256_of(dest), "equal_to_pinned": sha256_of(dest) == c["sha256"], "streams": probe(dest)}
        save(rec)
    shutil.rmtree(tmp, ignore_errors=True)
    save(rec)
    report(rec, src)


def report(rec, src):
    got = [c for c in src["clips"] if "sha256" in rec["clips"].get(c["clip"], {}) and "refused" not in rec["clips"][c["clip"]]]
    pinned = sum(1 for c in got if rec["clips"][c["clip"]].get("equal_to_pinned"))
    gone = [c["clip"] for c in src["clips"] if c not in got]
    print(f"route {rec['route']}: {len(got)} of {len(src['clips'])} clips fetched, {pinned} equal to their pinned sha256")
    for clip in gone:
        print(f"  not fetched: {clip} ({rec['clips'].get(clip, {}).get('gone') or rec['clips'].get(clip, {}).get('refused')})")
    print(f"the route is recorded in {RECORD}")


def main():
    args = sys.argv[1:]
    src = load()
    if not args or args[:1] == ["mirror"]:
        route_mirror(src)
    elif args[:1] == ["youtube"]:
        route_youtube(src)
    elif args[:1] == ["folder"] and len(args) == 2:
        route_folder(src, args[1])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
