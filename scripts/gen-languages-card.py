#!/usr/bin/env python3
"""Render metrics/languages.svg from language bytes across every repo the
authenticated `gh` user owns, public and private.

Generated HTML/CSS assets are excluded: several repos are static site mirrors
or vendored CMS checkouts whose HTML is build output, not authored code.
Run:  python3 scripts/gen-languages-card.py
"""
import collections, html, json, subprocess, pathlib

EXCLUDE = {"HTML", "CSS"}
COLORS = {
    "TypeScript": "#3178C6", "JavaScript": "#F1E05A", "Go": "#00ADD8",
    "Python": "#3572A5", "PHP": "#4F5D95", "C#": "#178600",
    "PLpgSQL": "#336790", "Blade": "#F7523F", "Shell": "#89E051",
    "SCSS": "#C6538C", "Dockerfile": "#384D54", "Ruby": "#701516",
}
FALLBACK = "#F59E0B"


def collect():
    repos = json.loads(subprocess.run(
        ["gh", "repo", "list", "--limit", "300", "--json", "nameWithOwner,isFork"],
        capture_output=True, text=True, check=True).stdout)
    totals, seen = collections.Counter(), 0
    for r in repos:
        if r["isFork"]:
            continue
        out = subprocess.run(["gh", "api", f"repos/{r['nameWithOwner']}/languages"],
                             capture_output=True, text=True)
        if out.returncode:
            continue
        data = json.loads(out.stdout or "{}")
        if data:
            seen += 1
        for lang, size in data.items():
            if lang not in EXCLUDE:
                totals[lang] += size
    return seen, totals


def render(repo_count, totals, limit=8):
    top = totals.most_common(limit)
    grand = sum(totals.values())
    W, ROW, TOP = 480, 26, 96
    H = TOP + ROW * len(top) + 16
    bar_x, bar_w = 148, 250

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Segoe UI,Ubuntu,Helvetica,sans-serif">',
         f'<rect width="{W}" height="{H}" rx="10" fill="#1d2021" stroke="#3c3836"/>',
         '<text x="22" y="34" fill="#F59E0B" font-size="15" font-weight="600">'
         'Languages by code volume</text>',
         f'<text x="22" y="54" fill="#a89984" font-size="11">across {repo_count} '
         f'repositories, public and private &#183; {grand/1e6:.0f} MB indexed by GitHub</text>',
         '<text x="22" y="71" fill="#7c6f64" font-size="9.5">generated HTML/CSS '
         'build output excluded</text>']

    for i, (lang, size) in enumerate(top):
        y = TOP + i * ROW
        pct = size / grand * 100
        color = COLORS.get(lang, FALLBACK)
        fill_w = max(2.0, bar_w * size / top[0][1])
        p.append(f'<text x="22" y="{y+11}" fill="#ebdbb2" font-size="12">'
                 f'{html.escape(lang)}</text>')
        p.append(f'<rect x="{bar_x}" y="{y+2}" width="{bar_w}" height="11" rx="5.5" '
                 f'fill="#32302f"/>')
        p.append(f'<rect x="{bar_x}" y="{y+2}" width="{fill_w:.1f}" height="11" '
                 f'rx="5.5" fill="{color}"/>')
        p.append(f'<text x="{bar_x+bar_w+12}" y="{y+11}" fill="#a89984" '
                 f'font-size="11">{pct:.1f}%</text>')

    p.append('</svg>')
    return "\n".join(p)


if __name__ == "__main__":
    count, totals = collect()
    out = pathlib.Path(__file__).resolve().parent.parent / "metrics" / "languages.svg"
    out.write_text(render(count, totals))
    print(f"wrote {out} from {count} repositories")
