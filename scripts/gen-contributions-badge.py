#!/usr/bin/env python3
"""Write metrics/contributions.json, a shields.io endpoint badge holding the
public contribution total for the last year.

Read straight from GitHub's own public contributions fragment, so the number
always matches what a visitor sees on the profile. This exists because the
third-party contribution APIs cache aggressively and served a stale "10" for
hours after private contributions were made visible.
"""
import json, pathlib, re, urllib.request

USER = "eclipseagency"
URL = f"https://github.com/users/{USER}/contributions"

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode()

days = [int(n.replace(",", "")) for n in re.findall(r"([0-9,]+) contributions? on", html)]
if not days:
    raise SystemExit("could not parse the contributions fragment; markup changed")

total = sum(days)
badge = {
    "schemaVersion": 1,
    "label": "contributions (last year)",
    "message": f"{total:,}",
    "color": "F59E0B",
    "namedLogo": "github",
    "logoColor": "white",
}
out = pathlib.Path(__file__).resolve().parent.parent / "metrics" / "contributions.json"
out.write_text(json.dumps(badge, indent=2) + "\n")
print(f"wrote {out}: {total:,} contributions over {len(days)} active days")
