#!/usr/bin/env python3
"""
Check for newer GitHub releases for all tools defined in shared.yml.

Reads pld_deb, pld_files, pld_downloads, pld_unpack — no extra config.
Non-GitHub URLs (insync CDN, waveterm, gitkraken) are silently skipped.

Usage:
    ./scripts/check_versions.py
    ./scripts/check_versions.py --update             # rewrite URLs in shared.yml
    GITHUB_TOKEN=ghp_... ./scripts/check_versions.py
"""

import sys
sys.dont_write_bytecode = True

import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pyyaml required: pip install pyyaml")

SHARED_VARS = Path(__file__).resolve().parent.parent / "roles/pld/vars/shared.yml"
API_URL = "https://api.github.com/repos/{}/releases/latest"
GH_RE = re.compile(r"https://github\.com/([^/\s]+/[^/\s]+)/releases/download/([^/\s]+)/\S+")


# ---------------------------------------------------------------------------
# GitHub API
# ---------------------------------------------------------------------------

def gh_latest(repo, token=None):
    req = urllib.request.Request(API_URL.format(repo))
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "pld-version-checker/1.0")
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()).get("tag_name")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        print(f"  [{repo}] HTTP {e.code}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  [{repo}] {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Version comparison
# ---------------------------------------------------------------------------

def to_semver(tag):
    """Normalize a tag to a comparable int-tuple, handling all prefix forms."""
    t = urllib.parse.unquote(tag)
    t = re.sub(r"^[a-zA-Z][a-zA-Z0-9_.+]*/", "", t)    # namespace/  (kustomize/v5)
    t = re.sub(r"^[a-zA-Z][a-zA-Z0-9_.+]*-", "", t)    # name-       (gping-v1)
    t = re.sub(r"^v", "", t)
    nums = re.findall(r"\d+", t)
    return tuple(int(n) for n in nums[:4]) if nums else (0,)


# ---------------------------------------------------------------------------
# URL rewriting
# ---------------------------------------------------------------------------

def rewrite(url, old_encoded, new_tag):
    """Replace old_encoded tag with new_tag throughout a GitHub release URL."""
    old_tag = urllib.parse.unquote(old_encoded)
    new_encoded = urllib.parse.quote(new_tag, safe="")

    def bare(tag):
        t = re.sub(r"^[a-zA-Z][a-zA-Z0-9_.+]*/", "", tag)
        t = re.sub(r"^[a-zA-Z][a-zA-Z0-9_.+]*-", "", t)
        return re.sub(r"^v", "", t)

    old_bare = bare(old_tag)
    new_bare = bare(new_tag)

    marker = f"/releases/download/{old_encoded}/"
    if marker in url:
        pre, filename = url.split(marker, 1)
        return pre + f"/releases/download/{new_encoded}/" + filename.replace(old_bare, new_bare)

    # fallback: blind replace (handles single-file downloads without trailing /)
    return url.replace(old_encoded, new_encoded).replace(old_bare, new_bare)


# ---------------------------------------------------------------------------
# YAML entry collection
# ---------------------------------------------------------------------------

def iter_entries(data):
    """
    Yield (changelog_tag, name, url, regex_match) for every GitHub release URL
    across pld_deb, pld_files, pld_downloads, pld_unpack.

    Driven entirely by the existing YAML payload — no separate mapping needed.
    """
    seen = set()

    # pld_deb: plain URL strings
    for url in data.get("pld_deb", []):
        if not isinstance(url, str) or url in seen:
            continue
        m = GH_RE.search(url)
        if not m:
            continue
        seen.add(url)
        # prefer repo name; fall back to filename stem when repo name is generic
        repo_name = m.group(1).split("/")[1]
        if repo_name in ("download", "releases", "package"):
            stem = Path(urllib.parse.unquote(url.split("/")[-1])).stem
            name = re.split(r"[_]", stem)[0].split("-")[0]
        else:
            name = repo_name
        yield "DEB", name, url, m

    # pld_files / pld_downloads / pld_unpack: dicts with a 'url' key
    for list_key in ("pld_files", "pld_downloads", "pld_unpack"):
        for item in data.get(list_key, []):
            url = item.get("url", "") if isinstance(item, dict) else ""
            if not url or url in seen:
                continue
            m = GH_RE.search(url)
            if not m:
                continue
            seen.add(url)
            name = item.get("destination") or item.get("name") or "unknown"
            yield "PACKAGES", name, url, m


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    do_update = "--update" in sys.argv
    token = os.environ.get("GITHUB_TOKEN")
    if "--token" in sys.argv:
        i = sys.argv.index("--token")
        if i + 1 < len(sys.argv):
            token = sys.argv[i + 1]
    if not token:
        try:
            token = subprocess.check_output(
                ["gh", "auth", "token"], stderr=subprocess.DEVNULL, text=True
            ).strip() or None
        except Exception:
            pass

    raw = SHARED_VARS.read_text()
    data = yaml.safe_load(raw)

    repo_cache = {}
    results = []

    for ch_tag, name, url, m in iter_entries(data):
        repo, encoded = m.group(1), m.group(2)
        current = urllib.parse.unquote(encoded)

        if current in ("master", "latest", "HEAD"):
            results.append((ch_tag, name, url, encoded, current, current, "pinned"))
            continue

        if repo not in repo_cache:
            print(f"  {repo} ...", file=sys.stderr)
            repo_cache[repo] = gh_latest(repo, token)
        latest = repo_cache[repo]

        if latest is None:
            results.append((ch_tag, name, url, encoded, current, None, "error"))
        elif to_semver(latest) > to_semver(current):
            results.append((ch_tag, name, url, encoded, current, latest, "outdated"))
        else:
            results.append((ch_tag, name, url, encoded, current, latest, "ok"))

    outdated = [r for r in results if r[6] == "outdated"]
    ok       = [r for r in results if r[6] == "ok"]
    skipped  = [r for r in results if r[6] in ("pinned", "error")]

    W = 24
    print(f"\n{'─' * 72}")
    print(f"  PLD version check — {len(results)} tools — {len(outdated)} outdated")
    print(f"{'─' * 72}\n")

    if outdated:
        print("OUTDATED:")
        for ch_tag, name, url, enc, cur, lat, _ in outdated:
            print(f"  [{name:<{W - 2}}]  {cur:<28} →  {lat}")
        print()

    print(f"UP TO DATE ({len(ok)}):")
    for ch_tag, name, url, enc, cur, lat, _ in ok:
        print(f"  [{name:<{W - 2}}]  {cur}")

    if skipped:
        print(f"\nSKIPPED ({len(skipped)}):")
        for ch_tag, name, url, enc, cur, lat, reason in skipped:
            print(f"  [{name:<{W - 2}}]  {cur:<28}  ({reason})")

    if outdated:
        print("\nCHANGELOG entries:")
        for ch_tag, name, url, enc, cur, lat, _ in outdated:
            print(f"  - [{ch_tag}] upgraded `{name}` to version {lat}")

    if do_update:
        if not outdated:
            print("\nNothing to update.")
            return
        print(f"\nUpdating {SHARED_VARS} ...")
        new_raw = raw
        for ch_tag, name, url, enc, cur, lat, _ in outdated:
            new_url = rewrite(url, enc, lat)
            if new_url != url:
                new_raw = new_raw.replace(url, new_url)
                print(f"  {name}: {cur} → {lat}")
            else:
                print(f"  {name}: URL rewrite failed — check manually", file=sys.stderr)
        SHARED_VARS.write_text(new_raw)
        print(f"\nReview: git diff roles/pld/vars/shared.yml")
    elif outdated:
        print("\nRun with --update to apply URL changes to shared.yml.")


if __name__ == "__main__":
    main()
