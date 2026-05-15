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
    "ytmusic-responsive-list-item-renderer"
]

def yt_cosmetic(selector):
    parts = [f"{r}{selector}" for r in RENDERERS]
    return "www.youtube.com##" + ", ".join(parts)

def ytm_cosmetic(selector):
    parts = [f"{r}{selector}" for r in YTM_RENDERERS]
    return "music.youtube.com##" + ", ".join(parts)

def main():
    out = []
    def ln(s=""): out.append(s)

    # Deduplicate and sort lists to prevent duplicate rules and maintain order
    unique_channels = sorted(set(CHANNEL_IDS))
    unique_videos = sorted(set(VIDEO_IDS))
    
    # Remove duplicate keywords while preserving order
    unique_keywords = []
    seen_patterns = set()
    for pattern, comment in KEYWORDS:
        if pattern not in seen_patterns:
            unique_keywords.append((pattern, comment))
            seen_patterns.add(pattern)

    ln(f"! Title: Chris Lowles' Auto Regenerating Filterlist")
    ln(f"! Description: Blocks YouTube & YT Music content via channel id, video id, broad keywords, and static rules")
    ln(f"! Generated: {date.today().isoformat()}")
    ln()

    ln("! CHANNELS")
    ln()
    for cid in unique_channels:
        # Standard YouTube
        ln(yt_cosmetic(f':has(a[href*="/channel/{cid}"])'))
        # YT Music
        ln(ytm_cosmetic(f':has(a[href*="{cid}"])'))
    ln()

    ln("! VIDEOS")
    ln()
    for vid in unique_videos:
        # Standard YouTube
        ln(yt_cosmetic(f':has(a[href*="{vid}"])'))
        ln(f"||www.youtube.com/watch?v={vid}^")
        # YT Music
        ln(ytm_cosmetic(f':has(a[href*="{vid}"])'))
        ln(f"||music.youtube.com/watch?v={vid}^")
    ln()

    ln("! BLOCKED KEYWORDS (title + channel name)")
    ln()
    for pattern, comment in unique_keywords:
        ln(f"! {comment}")
        # Standard YouTube
        ln(yt_cosmetic(f":has(#video-title:has-text({pattern}))"))
        ln(yt_cosmetic(f":has(#channel-name:has-text({pattern}))"))
        # YT Music uses yt-formatted-string heavily for titles and artist names
        ln(ytm_cosmetic(f":has(yt-formatted-string:has-text({pattern}))"))
        ln()

    # Append static filters if the file exists
    if os.path.exists("static.txt"):
        ln("! ------------------------------------------")
        ln("! --- Included from static.txt  ---")
        ln("! ------------------------------------------")
        ln()
        try:
            with open("static.txt", "r", encoding="utf-8") as pf:
                for line in pf:
                    # Strip newline characters so we don't end up with double spacing
                    out.append(line.rstrip('\n'))
        except IOError as e:
            print(f"Error reading static.txt: {e}", file=sys.stderr)

    result = "\n".join(out)
    
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(result)
    except IOError as e:
        print(f"Error writing to {OUTPUT_FILE}: {e}", file=sys.stderr)
        sys.exit(1)

    # Re-calculated the total to include all viable rules (including from static.txt)
    total = sum(1 for l in out if l.startswith("www.youtube.com##") or l.startswith("music.youtube.com##") or l.startswith("||") or ("##" in l and not l.startswith("!")))

    print(f"Written {OUTPUT_FILE} ({total} rules)")
    print(f"Channels: {len(unique_channels)} (Applied to YT & YTM)")
    print(f"Videos:   {len(unique_videos)} x 4 (YT/YTM Cosmetic + YT/YTM Network)")
    print(f"Keywords: {len(unique_keywords)} x 3 (YT Title + YT Channel + YTM Formatted String)")

if __name__ == "__main__":
    main()