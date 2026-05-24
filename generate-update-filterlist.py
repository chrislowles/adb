#!/usr/bin/env python3
"""
Filterlist generator.
Edit the three lists below, then run: python3 generate-update-filterlist.py
Output: filterlist.txt
"""

# YOUTUBE/YTM CHANNEL IDs
# Find via: www.youtube.com/channel/<ID>
CHANNEL_IDS = []

# YOUTUBE/YTM VIDEO IDs
# Cosmetic hide + hard network block. Remove the ||www.youtube.com line in the template below if you only want feed-hiding without blocking direct links.
VIDEO_IDS = []

# YOUTUBE/YTM KEYWORDS
# Format: ("regex_pattern", "human-readable comment")
# Patterns are matched against both video titles and channel names.
# Use /regex/i syntax (case-insensitive). Consolidate variants into one entry.
KEYWORDS = [
    ("/Charlie Kirk/i", "Charlie Kirk"),
    ("/Pirate\\s?Software/i", "Pirate Software / PirateSoftware"),
    ("/Scott Galloway/i", "Scott Galloway"),
    ("/Turk(?:ey|y) Tom/i", "Turkey Tom / Turky Tom"),
    ("/Omarchy/i", "Omarchy"),
    ("/Bill Maher/i", "Bill Maher"),
    ("/Nerd City/i", "Nerd City"),
    ("/Karl Jobst/i", "Karl Jobst"),
    ("/SomeOrdinary(?:Gamers|Podcast)/i", "SomeOrdinaryGamers / SomeOrdinaryPodcast"),
    ("/Asmongold/i", "Asmongold"),
    ("/h3(?:h3|\\s*podcast)/i", "h3h3 / h3 podcast"),
    ("/(?:Hila|Ethan) Klein/i", "Hila Klein / Ethan Klein"),
    ("/\\d?kliksphilip/i", "kliksphilip / 2kliksphilip / 3kliksphilip"),
    ("/Xanderhal/i", "Xanderhal"),
    ("/mrwhosetheboss/i", "mrwhosetheboss"),
    ("/Evan Carmichael/i", "Evan Carmichael"),
    ("/Vaush/i", "Vaush"),
]

# Generator — no need to edit below this line

import os
import sys
import json
import urllib.request
from urllib.parse import urlparse
from datetime import date

OUTPUT_FILE = "filterlist.txt"

# Standard YouTube Renderers
RENDERERS = [
    "ytd-rich-item-renderer",
    "ytd-video-renderer",
    "ytd-compact-video-renderer",
    "ytd-grid-video-renderer",
    "ytd-playlist-video-renderer",
    "ytd-channel-renderer",
    "ytd-reel-item-renderer",
    "ytd-reel-video-renderer",
]

# YouTube Music Renderers
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
    for pattern, comment in KEYWORDS:
        if pattern in seen_patterns:
            print(f"Warning: duplicate keyword pattern removed: {pattern}", file=sys.stderr)
        else:
            unique_keywords.append((pattern, comment))
            seen_patterns.add(pattern)

    ln(f"! Title: Chris Lowles' Auto Regenerating Filterlist")
    ln(f"! Description: Blocks YouTube & YT Music content via channel id, video id, broad keywords, and static rules")
    ln(f"! Generated: {date.today().isoformat()}")
    ln()

    ln("! YT/YTM CHANNELS")
    ln()
    for cid in unique_channels:
        ln(cosmetic("www.youtube.com", RENDERERS, f':has(a[href*="/channel/{cid}"])'))
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
    for pattern, comment in unique_keywords:
        ln(f"! {comment}")
        ln(cosmetic("www.youtube.com", RENDERERS, f":has(#video-title:has-text({pattern}))"))
        ln(cosmetic("www.youtube.com", RENDERERS, f":has(#channel-name:has-text({pattern}))"))
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
    print(f"Keywords: {len(unique_keywords)} x 3 (YT Title + YT Channel + YTM Formatted String)")

if __name__ == "__main__":
    main()