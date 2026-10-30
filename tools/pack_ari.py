#!/usr/bin/env python3
"""Packs a plugin into <id>.ari: a zip of manifest.json, icon.png and either the .cs files (source) or the built plugin (compiled).

  Source plugin:   pack_ari.py --id weather --name Weather --description "..." --version 1.0.0 --source ./weather --out weather.ari
  Compiled plugin: pack_ari.py --id discord --name Discord --description "..." --version 1.0.0 --project ./Discord/ARI.Plugin.Discord.csproj --entry ARI.Plugin.Discord.dll --out discord.ari

Add --icon icon.png for the plugin's picture. Prints the SHA-256 of the result, which the catalog entry carries."""
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile

# Native libraries for these platforms are kept; the rest only make the package bigger.
RIDS = ("osx-", "linux-x64", "linux-arm64", "win-x64", "win-arm64")
KEEP = (".dll", ".json", ".so", ".dylib", ".dat")

def main():
    a = argparse.ArgumentParser()
    for k in ("id", "name", "description", "version", "out"): a.add_argument("--" + k, required=True)
    a.add_argument("--author", default="")
    a.add_argument("--icon")
    a.add_argument("--source", help="folder of .cs files (a source plugin)")
    a.add_argument("--project", help=".csproj of a plugin that must be built")
    a.add_argument("--entry", help="the plugin's .dll name, for a built plugin")
    a.add_argument("--prop", action="append", default=[], help="extra MSBuild property for the build, e.g. AriHost=/path/to/Server (repeatable)")
    a.add_argument("--host", help=".csproj of ARI.LLM (from an ARI checkout): whatever ARI itself ships is left out of the package")
    a = a.parse_args()
    if bool(a.source) == bool(a.project): sys.exit("Give exactly one of --source or --project.")

    manifest = {"id": a.id, "name": a.name, "description": a.description, "author": a.author, "version": a.version}
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as z:
        if a.source:
            for f in sorted(os.listdir(a.source)):
                if f.endswith(".cs"): z.write(os.path.join(a.source, f), f)
        else:
            if not a.entry: sys.exit("A built plugin needs --entry.")
            manifest.update(kind="compiled", entry=a.entry)
            out = tempfile.mkdtemp(prefix="ari-pack-")
            try:
                subprocess.run(["dotnet", "publish", a.project, "-c", "Release", "-o", out, "-p:DebugType=none", "-p:DebugSymbols=false", *[f"-p:{p}" for p in a.prop]], check=True)
                if not os.path.exists(os.path.join(out, a.entry)): sys.exit(f"The build didn't produce {a.entry}.")
                host_files = set()
                if a.host:
                    host_out = tempfile.mkdtemp(prefix="ari-host-")
                    try:
                        subprocess.run(["dotnet", "publish", a.host, "-c", "Release", "-o", host_out, "-p:DebugType=none"], check=True, stdout=subprocess.DEVNULL)
                        for root, _, names in os.walk(host_out):
                            host_files.update(os.path.relpath(os.path.join(root, n), host_out).replace(os.sep, "/") for n in names)
                    finally: shutil.rmtree(host_out, ignore_errors=True)
                for root, _, names in os.walk(out):
                    for n in sorted(names):
                        full = os.path.join(root, n)
                        rel = os.path.relpath(full, out).replace(os.sep, "/")
                        if rel in host_files and n != a.entry: continue                  # ARI has this already
                        if not n.lower().endswith(KEEP) or n.endswith(".staticwebassets.endpoints.json"): continue
                        if rel.startswith("runtimes/") and not rel.split("/")[1].startswith(RIDS): continue
                        if n.endswith(".resources.dll"): continue
                        z.write(full, "plugin/" + rel)
            finally: shutil.rmtree(out, ignore_errors=True)
        if a.icon: z.write(a.icon, "icon.png")
        z.writestr("manifest.json", json.dumps(manifest, indent=2))
    print(f"{a.out}  sha256={hashlib.sha256(open(a.out, 'rb').read()).hexdigest()}  size={os.path.getsize(a.out)}")

main()
