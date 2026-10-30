#!/usr/bin/env python3
"""Checks catalog.json: every entry is well formed, and every version's download exists and matches its SHA-256.
Run by the pull-request check, and by hand: validate_catalog.py [catalog.json]. Exits non-zero on the first problem found."""
import hashlib, json, re, sys, urllib.request, zipfile, io

ID = re.compile(r"^[a-z][a-z0-9_]{1,40}$")

def fail(msg): print("FAIL:", msg); sys.exit(1)

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "catalog.json"
    cat = json.load(open(path))
    seen = set()
    for p in cat.get("plugins", []):
        pid = p.get("id", "")
        if not ID.match(pid): fail(f"bad id {pid!r}")
        if pid in seen: fail(f"{pid} is listed twice")
        seen.add(pid)
        for k in ("name", "description", "versions"):
            if not p.get(k): fail(f"{pid}: missing {k}")
        for v in p["versions"]:
            if not v.get("version") or not v.get("url") or not v.get("sha256"): fail(f"{pid}: a version needs version, url and sha256")
            if not v["url"].startswith("https://"): fail(f"{pid} {v['version']}: the download must be an https address")
            data = urllib.request.urlopen(v["url"], timeout=120).read()
            if hashlib.sha256(data).hexdigest() != v["sha256"].lower(): fail(f"{pid} {v['version']}: the download doesn't match its sha256")
            try: z = zipfile.ZipFile(io.BytesIO(data))
            except zipfile.BadZipFile: fail(f"{pid} {v['version']}: not a zip")
            m = json.loads(z.read("manifest.json"))
            if m.get("id") != pid: fail(f"{pid} {v['version']}: the package says its id is {m.get('id')!r}")
            if m.get("version") != v["version"]: fail(f"{pid}: the package says version {m.get('version')!r}, the catalog says {v['version']!r}")
            print(f"ok  {pid} {v['version']}")
    print(f"{len(seen)} plugin(s) checked")

main()
