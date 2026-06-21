#!/usr/bin/env python3
"""
Filterlist generator.
Edit the lists below, then run: python3 generate-update-filterlist.py
Output: filterlist.txt in generated branch
"""

# YOUTUBE/YTM CHANNEL IDs
# Find via: www.youtube.com/channel/<ID>
# Hardcoded, unchangable variable though may want to also use handle and plain-text
CHANNEL_IDS = []

# YOUTUBE/YTM VIDEO IDs
# Cosmetic hide + hard network block. Remove the ||www.youtube.com line in the template below if you only want feed-hiding without blocking direct links.
VIDEO_IDS = [
    "5XwYPQ9Un1A"
]

# YOUTUBE/YTM KEYWORDS
# Format: ("regex_pattern")
# Patterns are matched against both video titles and channel names (other contexts too)
# Use /regex/i syntax (case-insensitive). Consolidate variants into one entry. People loooooove misspelling.
KEYWORDS = [
    ("/Brad Taste/i"),
    ("/Charlie Kirk/i"),
    ("/Clavicular/i"),
    ("/Pirate\\s?Software/i"),
    ("/Scott Galloway/i"),
    ("/Turk(?:ey|y) Tom/i"),
    ("/Omarchy/i"),
    ("/Bill Maher/i"),
    ("/Nerd City/i"),
    ("/Karl Jobst/i"),
    ("/SomeOrdinary(?:Gamers|Podcast)/i"),
    ("/Asmongold/i", "Asmongold"),
    ("/h3(?:h3|\\s*podcast)/i"),
    ("/(?:Hila|Ethan) Klein/i"),
    ("/\\d?kliksphilip/i"),
    ("/Xanderhal/i"),
    ("/mrwhosetheboss/i"),
    ("/Evan Carmichael/i"),
    ("/Vaush/i"),
]

# EXTERNAL FILTER LIST SOURCES
# Full third-party filterlists, fetched fresh on every run and merged into the output verbatim (after blank-line stripping).
# URLs sourced from uBlock Origin's assets.json: https://github.com/gorhill/uBlock/blob/master/assets/assets.json
# Format: ("Human-readble name", "https://url/to/list.txt")
EXTERNAL_SOURCES = [
    ("uBlock filters – Ads", "https://ublockorigin.github.io/uAssets/filters/filters.txt"),                              # ublock-filters
    ("uBlock filters – Badware risks", "https://ublockorigin.github.io/uAssets/filters/badware.txt"),                    # ublock-badware
    ("uBlock filters – Privacy", "https://ublockorigin.github.io/uAssets/filters/privacy.txt"),                          # ublock-privacy
    ("uBlock filters – Quick fixes", "https://ublockorigin.github.io/uAssets/filters/quick-fixes.txt"),                  # ublock-quick-fixes
    ("uBlock filters – Unbreak", "https://ublockorigin.github.io/uAssets/filters/unbreak.txt"),                          # ublock-unbreak
    ("EasyList", "https://ublockorigin.github.io/uAssets/thirdparties/easylist.txt"),                                    # easylist
    ("EasyPrivacy", "https://ublockorigin.github.io/uAssets/thirdparties/easyprivacy.txt"),                              # easyprivacy
    ("AdGuard/uBO – URL Tracking Protection", "https://ublockorigin.github.io/uAssets/filters/privacy-removeparam.txt"), # adguard-spyware-url
    ("Block Outsider Intrusion into LAN", "https://ublockorigin.github.io/uAssets/filters/lan-block.txt"),               # block-lan
    ("Online Malicious URL Blocklist", "https://malware-filter.gitlab.io/urlhaus-filter/urlhaus-filter-ag-online.txt"), # urlhaus-1
    ("Phishing URL Blocklist", "https://malware-filter.gitlab.io/phishing-filter/phishing-filter.txt"),                  # curben-phishing
    ("Peter Lowe's Ad and tracking server list", "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=1&mimetype=plaintext"), # plowe-0
    ("Dan Pollock's hosts file", "https://someonewhocares.org/hosts/hosts"),                                             # dpollock-0
]

# Generator — no need to edit below this line

import os
import sys
import json
import urllib.request
import urllib.error
from urllib.parse import urlparse
from datetime import date

OUTPUT_FILE = "filterlist.txt"
EXTERNAL_SOURCE_TIMEOUT = 15 # seconds, per source

# Standard YouTube Renderers
RENDERERS = [
    # Video renderers
    "ytd-rich-item-renderer",
    "ytd-video-renderer",
    "ytd-compact-video-renderer",
    "ytd-grid-video-renderer",
    "ytd-playlist-video-renderer",
    "ytd-reel-item-renderer",
    "ytd-reel-video-renderer",
    "ytd-video-card-renderer",
    "ytd-watch-card-compact-video-renderer",
    
    # Playlist renderers
    "ytd-playlist-renderer",
    "ytd-grid-playlist-renderer",
    "ytd-compact-playlist-renderer",
    "ytd-playlist-panel-video-renderer",
    
    # Channel renderers
    "ytd-channel-renderer",
    "ytd-grid-channel-renderer",
    "ytd-mini-channel-renderer",
    "ytd-compact-channel-renderer",
    
    # Mix / Radio renderers
    "ytd-radio-renderer",
    "ytd-grid-radio-renderer",
    "ytd-compact-radio-renderer",
    
    # Sections and new view models
    "ytd-shelf-renderer",
    "ytd-rich-shelf-renderer",
    "ytd-channel-featured-video-renderer",
    "ytd-channel-video-player-renderer",
    "yt-lockup-view-model",
    "yt-video-with-context-renderer"
]

# YT Music Renderers
YTM_RENDERERS = [
    "ytmusic-two-row-item-renderer",
    "ytmusic-responsive-list-item-renderer",
]

def cosmetic(domain, renderers, selector):
    # Each renderer on its own line — uBlock Origin does not support comma-separated
    # procedural cosmetic filters (those using :has-text(), etc.). A single long
    # comma-joined line works for plain CSS selectors but is silently broken for
    # procedural ones, causing keyword filters to do nothing.
    return "\n".join(f"{domain}##{r}{selector}" for r in renderers)

def fetch_external_filterlist(name, url, timeout=EXTERNAL_SOURCE_TIMEOUT):
    """
    Download a single external filterlist.
    Returns a list of non-empty, newline-stripped lines, or None if the
    fetch/decode failed. Failures are logged as warnings, not raised —
    one dead source shouldn't break the whole build.
    """
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; filterlist-generator)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except (urllib.error.URLError, OSError) as e:
        print(f"Warning: failed to fetch external source '{name}' ({url}): {e}", file=sys.stderr)
        return None

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        print(f"Warning: failed to decode external source '{name}' ({url}): {e}", file=sys.stderr)
        return None

    lines = [l.rstrip('\r\n') for l in text.splitlines() if l.strip()]
    if not lines:
        print(f"Warning: external source '{name}' ({url}) returned no usable lines", file=sys.stderr)
        return None

    return lines

def main():
    out = []
    def ln(s=""): out.append(s)

    # Validate channel IDs (YouTube channel IDs start with UC and are 24 chars)
    for cid in CHANNEL_IDS:
        if not cid.startswith("UC") or len(cid) != 24:
            print(f"Warning: channel ID may be malformed: {cid}", file=sys.stderr)

    # Validate video IDs (YouTube video IDs are 11 chars)
    for vid in VIDEO_IDS:
        if len(vid) != 11:
            print(f"Warning: video ID may be malformed: {vid}", file=sys.stderr)

    # Deduplicate and sort, warning on any duplicates found
    seen_channels = set()
    unique_channels = []
    for cid in sorted(CHANNEL_IDS):
        if cid in seen_channels:
            print(f"Warning: duplicate channel ID removed: {cid}", file=sys.stderr)
        else:
            unique_channels.append(cid)
            seen_channels.add(cid)

    seen_videos = set()
    unique_videos = []
    for vid in sorted(VIDEO_IDS):
        if vid in seen_videos:
            print(f"Warning: duplicate video ID removed: {vid}", file=sys.stderr)
        else:
            unique_videos.append(vid)
            seen_videos.add(vid)

    unique_keywords = []
    seen_patterns = set()
    for pattern in KEYWORDS:
        if pattern in seen_patterns:
            print(f"Warning: duplicate keyword pattern removed: {pattern}", file=sys.stderr)
        else:
            unique_keywords.append((pattern))
            seen_patterns.add(pattern)

    ln(f"! Title: Chris Lowles' Auto Regenerating Filterlist")
    ln(f"! Description: Blocks YouTube & YT Music content via channel id, video id, broad keywords. Blocks static rules and imports preferred sources.")
    ln(f"! Generated: {date.today().isoformat()}")
    ln()

    ln("! YT/YTM CHANNELS")
    ln()
    for cid in unique_channels:
        ln(cosmetic("www.youtube.com", RENDERERS, f':has(a[href*="/channel/{cid}"])'))
        # Hide whole channel/playlist pages if they explicitly link to the blocked ID in their headers
        ln(cosmetic("www.youtube.com", ["ytd-browse[page-subtype='channels']"], f':has(ytd-c4-tabbed-header-renderer a[href*="{cid}"])'))
        ln(cosmetic("www.youtube.com", ["ytd-browse[page-subtype='channels']"], f':has(ytd-page-header-renderer a[href*="{cid}"])'))
        ln(cosmetic("music.youtube.com", YTM_RENDERERS, f':has(a[href*="{cid}"])'))
    ln()

    ln("! YT/YTM VIDEOS")
    ln()
    for vid in unique_videos:
        ln(cosmetic("www.youtube.com", RENDERERS, f':has(a[href*="{vid}"])'))
        ln(f"||www.youtube.com/watch?v={vid}^")
        ln(cosmetic("music.youtube.com", YTM_RENDERERS, f':has(a[href*="{vid}"])'))
        ln(f"||music.youtube.com/watch?v={vid}^")
    ln()

    ln("! YT/YTM KEYWORDS (title + channel name)")
    ln()
    for pattern in unique_keywords:
        ln(cosmetic("www.youtube.com", RENDERERS, f":has(#video-title:has-text({pattern}))"))
        ln(cosmetic("www.youtube.com", RENDERERS, f":has(#title:has-text({pattern}))"))
        ln(cosmetic("www.youtube.com", RENDERERS, f":has(#channel-name:has-text({pattern}))"))
        ln(cosmetic("www.youtube.com", RENDERERS, f":has(yt-formatted-string:has-text({pattern}))"))
        ln(cosmetic("www.youtube.com", RENDERERS, f":has(.yt-core-attributed-string:has-text({pattern}))"))
        
        # Block whole channel/playlist pages if their header matches the keyword
        ln(cosmetic("www.youtube.com", ["ytd-browse[page-subtype='channels']"], f":has(ytd-c4-tabbed-header-renderer:has-text({pattern}))"))
        ln(cosmetic("www.youtube.com", ["ytd-browse[page-subtype='channels']"], f":has(ytd-page-header-renderer:has-text({pattern}))"))
        ln(cosmetic("www.youtube.com", ["ytd-browse[page-subtype='playlist']"], f":has(ytd-playlist-header-renderer:has-text({pattern}))"))

        # YT Music uses yt-formatted-string heavily for titles and artist names
        ln(cosmetic("music.youtube.com", YTM_RENDERERS, f":has(yt-formatted-string:has-text({pattern}))"))
        ln()

    # Append static filters if the file exists
    if os.path.exists("static.txt"):
        ln("! ------------------------------------------")
        ln("! --- Included from static.txt           ---")
        ln("! ------------------------------------------")
        ln()
        try:
            with open("static.txt", "r", encoding="utf-8") as pf:
                for line in pf:
                    out.append(line.rstrip('\r\n'))
        except IOError as e:
            print(f"Error reading static.txt: {e}", file=sys.stderr)

    # Fetch and append external filter list sources
    fetched_count = 0
    external_line_count = 0
    if EXTERNAL_SOURCES:
        ln("! ------------------------------------------")
        ln("! --- External sources                    ---")
        ln("! ------------------------------------------")
        ln()
        for name, url in EXTERNAL_SOURCES:
            lines = fetch_external_filterlist(name, url)
            if lines is None:
                ln(f"! --- {name} ({url}) — FAILED TO FETCH, skipped ---")
                ln()
                continue
            ln(f"! --- {name} ({url}) — {len(lines)} lines ---")
            out.extend(lines)
            ln()
            fetched_count += 1
            external_line_count += len(lines)

    result = "\n".join(out) + "\n"

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(result)
    except IOError as e:
        print(f"Error writing to {OUTPUT_FILE}: {e}", file=sys.stderr)
        sys.exit(1)

    # Count all active (non-comment, non-blank) rules
    total = sum(1 for l in result.splitlines() if l and not l.startswith("!"))

    print(f"Written {OUTPUT_FILE} ({total} rules)")
    print(f"Channels: {len(unique_channels)} (Applied to YT & YTM)")
    print(f"Videos:   {len(unique_videos)} x 4 (YT/YTM Cosmetic + YT/YTM Network)")
    print(f"Keywords: {len(unique_keywords)} x 8 (Various Title/Channel combinations)")
    if EXTERNAL_SOURCES:
        print(f"External: {fetched_count}/{len(EXTERNAL_SOURCES)} source(s) fetched ({external_line_count} lines)")

if __name__ == "__main__":
    main()