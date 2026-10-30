# ARI Plugins

The plugin catalog for [ARI](https://github.com/ari-labz/A.R.I). ARI's Plugins page reads `catalog.json` from this repo and lets you browse, search and install what's listed.

The catalog holds no plugin code. Each entry points at a `.ari` file (a zip: `manifest.json`, `icon.png`, and the plugin's scripts or built files) attached to a release in the plugin's own repo, with a SHA-256 so ARI can check the download.

## Add a plugin
1. Put your plugin in its own repo. Release it by tagging a version (`v1.0.0`); `.github/workflows/release-plugin.yml` here builds `<id>.ari` and attaches it to the release (see the comment at the top of that file for the three lines to call it).
2. Open a pull request here adding an entry to `catalog.json`:

```json
{
  "id": "weather",
  "name": "Weather",
  "description": "Current weather for Ari.",
  "author": "someone",
  "icon": "https://raw.githubusercontent.com/someone/ari-plugin-weather/main/icon.png",
  "repo": "https://github.com/someone/ari-plugin-weather",
  "versions": [
    { "version": "1.0.0", "url": "https://github.com/someone/ari-plugin-weather/releases/download/v1.0.0/weather.ari", "sha256": "…", "changelog": "First release" }
  ]
}
```

   Newest version first. `tools/pack_ari.py` prints the sha256 of the file it makes.
3. A check downloads each file, confirms the checksum, the id and the version, and a person reads the code before merging. A plugin runs with full access to someone's ARI, so nothing is listed unread.

`"featured": true` puts a plugin at the top of the Browse tab.

## Make a `.ari` by hand
```
python3 tools/pack_ari.py --id weather --name Weather --description "…" --version 1.0.0 --source ./weather --icon icon.png --out weather.ari
python3 tools/pack_ari.py --id discord --name Discord --description "…" --version 1.0.0 --project ./Plugin.csproj --entry ARI.Plugin.Discord.dll --host ../A.R.I/Server/ARI.LLM/ARI.LLM.csproj --out discord.ari
```
Add another catalog in ARI under Plugins → Browse → Catalogs… to run your own list.
