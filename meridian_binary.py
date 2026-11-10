#!/usr/bin/env python3
"""Meridian Binary 1 (MB1): a request with its files as raw bytes, instead of base64 inside JSON.

    python3 meridian_binary.py pack request.json > request.mb1
    python3 meridian_binary.py unpack request.mb1 > request.json
    python3 meridian_binary.py from-files --state state.json --questions questions.json \\
        --asset p=photo.jpg:image:jpg [--asset c=clip.mp4:video:mp4 ...] [--model kelvin] > request.mb1

    curl --data-binary @request.mb1 -H 'Content-Type: application/x-meridian-binary' \\
         -H "Authorization: Bearer $MERIDIAN_KEY" "$MERIDIAN_URL/v1/systemone"

The form (an envelope; the request inside is the JSON request as always):

    bytes 0-3          MB1\\n  (0x4D 0x42 0x31 0x0A), the magic and the version
    bytes 4-7          H, the header's length, an unsigned 32-bit integer, big-endian
    bytes 8 to 8+H     the header: the request as UTF-8 JSON, exactly as the JSON form, except that an asset carries
                       "data_ref": [offset, length] instead of "data_base64"
    bytes 8+H to end   the data region: the files' raw bytes; each offset counts from the data region's start

An asset carries exactly one of "data_base64" and "data_ref"; a request may mix them. The answer is the same JSON as
the JSON form's, byte for byte. A malformed MB1 body is answered 400 ("binary_form: ...") before anything is read or
taught. The body limit (32 MiB) is the same as for JSON, so MB1 carries about a third more media.

Python 3.10 or newer, its standard library only.
"""
import argparse
import base64
import json
import struct
import sys

MAGIC = b"MB1\n"
CONTENT_TYPE = "application/x-meridian-binary"


def pack(request, files=None):
    """An MB1 body from a request. Every asset with "data_base64" is moved into the data region as raw bytes; an asset
    named in `files` ({asset name: raw bytes}) takes those bytes. Assets that already carry "data_ref" are refused here,
    since their bytes are not at hand."""
    files = dict(files or {})
    header = dict(request)
    assets = {}
    region = bytearray()
    for name, asset in (request.get("assets") or {}).items():
        a = dict(asset)
        if name in files:
            raw = files[name]
            a.pop("data_base64", None)
        elif "data_base64" in a:
            raw = base64.b64decode(a.pop("data_base64"), validate=True)
        else:
            raise ValueError(f"the asset {name!r} carries no data to pack")
        if "data_ref" in a:
            raise ValueError(f"the asset {name!r} already carries a data_ref")
        a["data_ref"] = [len(region), len(raw)]
        region += raw
        assets[name] = a
    if assets:
        header["assets"] = assets
    head = json.dumps(header, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return MAGIC + struct.pack(">I", len(head)) + head + bytes(region)


def unpack(body):
    """The JSON request an MB1 body carries, each data_ref's bytes back as "data_base64". Raises ValueError, naming the
    fault, where the body is not a whole MB1 (the same faults the door answers with 400)."""
    if len(body) < 8 or body[:4] != MAGIC:
        raise ValueError("not MB1: it needs the 8-byte head starting MB1\\n")
    (h,) = struct.unpack(">I", body[4:8])
    if 8 + h > len(body):
        raise ValueError("the header's length runs past the body")
    try:
        request = json.loads(body[8:8 + h].decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        raise ValueError(f"the header is not JSON: {e}") from None
    region = body[8 + h:]
    for name, a in (request.get("assets") or {}).items():
        has_ref, has_b64 = "data_ref" in a, "data_base64" in a
        if has_ref == has_b64:
            raise ValueError(f"the asset {name!r} must carry exactly one of data_ref and data_base64")
        if has_ref:
            ref = a.pop("data_ref")
            if (not isinstance(ref, list) or len(ref) != 2 or not all(isinstance(x, int) and not isinstance(x, bool) and x >= 0 for x in ref)
                    or ref[0] + ref[1] > len(region)):
                raise ValueError(f"the asset {name!r} has a data_ref that is not two whole numbers within the data region")
            a["data_base64"] = base64.b64encode(region[ref[0]:ref[0] + ref[1]]).decode("ascii")
    return request


def from_files(state, questions, assets, model="kelvin"):
    """An MB1 body straight from files, with no base64 step: assets is [(name, path, type, format)]."""
    request = {"model": model, "state": state, "questions": questions,
               "assets": {name: {"type": kind, **({"format": fmt} if fmt else {})} for name, _, kind, fmt in assets}}
    files = {}
    for name, path, _, _ in assets:
        with open(path, "rb") as f:
            files[name] = f.read()
    return pack(request, files)


def _asset_arg(text):
    """name=path:type[:format]"""
    name, rest = text.split("=", 1)
    parts = rest.rsplit(":", 2) if rest.count(":") >= 2 else rest.rsplit(":", 1)
    if len(parts) == 3:
        return name, parts[0], parts[1], parts[2]
    return name, parts[0], parts[1], None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pack", help="a JSON request (assets with data_base64) to MB1")
    p.add_argument("request")
    u = sub.add_parser("unpack", help="an MB1 body back to the JSON request")
    u.add_argument("body")
    f = sub.add_parser("from-files", help="an MB1 request from a state, its questions and files")
    f.add_argument("--state", required=True, help="a JSON file with the request's state")
    f.add_argument("--questions", required=True, help="a JSON file with the request's questions")
    f.add_argument("--asset", action="append", default=[], type=_asset_arg, metavar="NAME=PATH:TYPE[:FORMAT]")
    f.add_argument("--model", default="kelvin")
    a = ap.parse_args()
    out = sys.stdout.buffer
    try:
        if a.cmd == "pack":
            out.write(pack(json.load(open(a.request, encoding="utf-8"))))
        elif a.cmd == "unpack":
            out.write(json.dumps(unpack(open(a.body, "rb").read()), ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
        else:
            state = json.load(open(a.state, encoding="utf-8"))
            questions = json.load(open(a.questions, encoding="utf-8"))
            out.write(from_files(state, questions, a.asset, a.model))
    except (OSError, ValueError) as e:
        sys.exit(f"meridian_binary: {e}")


if __name__ == "__main__":
    main()
