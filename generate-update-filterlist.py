#!/usr/bin/env python3
"""
Filterlist generator.
Edit the lists below, then run: python3 generate-update-filterlist.py
Output: filterlist.txt in generated branch
"""

# YOUTUBE/YTM CHANNEL IDs
# Each entry can be:
#   "UCxxxxxxxxxxxxxxxxxxxxxx"                                -> channel ID only (old format, still works)
#   ("UCxxxxxxxxxxxxxxxxxxxxxx", "@Handle")                   -> ID + handle
#   ("UCxxxxxxxxxxxxxxxxxxxxxx", "@Handle", "/Channel Name/i") -> ID + handle + name regex
#   (None, "@Handle", None)                                   -> handle only, no ID known yet
#   (None, None, "/Channel Name/i")                           -> name regex only (weakest option -
#                                                                 no href to match, relies on visible text)
# Any field can be omitted from the tuple (it's padded with None) or set to None explicitly.
# Whichever of id/handle/pattern are present are all used to build rules - more fields = more
# robust blocking (a channel that renames itself is still caught by ID; a channel whose ID you
# don't have yet is still caught by handle or name).
CHANNEL_IDS = [
    "UCJ9AFB3thzz2nPJqJGhNjjA",
    "UChwbfG8UvnLOJ_WgRiAaPBA",
    # ("UCxxxxxxxxxxxxxxxxxxxxxx", "@SomeHandle", "/Some Channel/i"),
]

# YOUTUBE/YTM VIDEO IDs
# Cosmetic hide + hard network block (watch, shorts, embed, and youtu.be forms).
# Remove specific ||...^ lines below in the template if you only want feed-hiding without
# blocking direct/embedded links.
VIDEO_IDS = [
    "5XwYPQ9Un1A"
]

# YOUTUBE/YTM KEYWORDS
# Format (or format I hope to achieve: ("Human readable text", "regex_pattern")
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
    ("/Asmongold/i"),
    ("/h3(?:h3|\\s*podcast)/i"),
    ("/(?:Hila|Ethan) Klein/i"),
    ("/\\d?kliksphilip/i"),
    ("/Xanderhal/i"),
    ("/mrwhosetheboss/i"),
    ("/Evan Carmichael/i"),
    ("/Vaush/i"),
    ("/Graham Platner/i"),
    ("/Platner/i"),
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

# Channel/playlist page header containers, used for whole-page hiding
CHANNEL_PAGE_HEADERS = [
    "ytd-c4-tabbed-header-renderer",
    "ytd-page-header-renderer",
]


def cosmetic(domain, renderers, selector):
    # Each renderer on its own line — uBlock Origin does not support comma-separated
    # procedural cosmetic filters (those using :has-text(), etc.). A single long
    # comma-joined line works for plain CSS selectors but is silently broken for
    # procedural ones, causing keyword filters to do nothing.
    return "\n".join(f"{domain}##{r}{selector}" for r in renderers)


def normalize_channel(entry):
    """Accepts a plain channel-ID string (old format) or a (id, handle, pattern)
    tuple/list with any field set to None or omitted, and returns a dict with
    keys id/handle/pattern."""
    if isinstance(entry, str):
        return {"id": entry, "handle": None, "pattern": None}
    if isinstance(entry, (tuple, list)):
        vals = list(entry) + [None] * (3 - len(entry))
        return {"id": vals[0], "handle": vals[1], "pattern": vals[2]}
    raise ValueError(f"Invalid CHANNEL_IDS entry: {entry!r}")


def main():
    out = []
    def ln(s=""): out.append(s)

    # --- Normalize + validate channels ---
    normalized_channels = [normalize_channel(e) for e in CHANNEL_IDS]

    for ch in normalized_channels:
        if not any((ch["id"], ch["handle"], ch["pattern"])):
            print(f"Warning: channel entry has no id/handle/pattern, skipping: {ch}", file=sys.stderr)
            continue
        if ch["id"] and (not ch["id"].startswith("UC") or len(ch["id"]) != 24):
            print(f"Warning: channel ID may be malformed: {ch['id']}", file=sys.stderr)
        if ch["handle"] and not ch["handle"].startswith("@"):
            print(f"Warning: handle should start with '@': {ch['handle']}", file=sys.stderr)
        if ch["pattern"] and not (ch["pattern"].startswith("/") and ch["pattern"].rstrip("i").endswith("/")):
            print(f"Warning: pattern doesn't look like /regex/i: {ch['pattern']}", file=sys.stderr)

    # Validate video IDs (YouTube video IDs are 11 chars)
    for vid in VIDEO_IDS:
        if len(vid) != 11:
            print(f"Warning: video ID may be malformed: {vid}", file=sys.stderr)

    # Dedupe channels: prefer ID as the identity key, fall back to handle, then pattern
    seen_channel_keys = set()
    unique_channels = []
    for ch in normalized_channels:
        if not any((ch["id"], ch["handle"], ch["pattern"])):
            continue
        key = ch["id"] or ch["handle"] or ch["pattern"]
        if key in seen_channel_keys:
            print(f"Warning: duplicate channel entry removed (key={key}): {ch}", file=sys.stderr)
            continue
        seen_channel_keys.add(key)
        unique_channels.append(ch)
    unique_channels.sort(key=lambda c: c["id"] or c["handle"] or c["pattern"])

    # Dedupe and sort videos, warning on any duplicates found
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
    ln(f"! Description: Blocks YouTube & YT Music content via channel id/handle/name, video id, broad keywords. Also blocks static rules.")
    ln(f"! Generated: {date.today().isoformat()}")
    ln()

    ln("! YT/YTM CHANNELS")
    ln()
    for ch in unique_channels:
        href_frags = []
        if ch["id"]:
            href_frags.append(f'/channel/{ch["id"]}')
        if ch["handle"]:
            href_frags.append(f'/{ch["handle"]}')

        # Feed-level hiding: any renderer linking to this channel's ID or handle.
        # "i" flag makes the attribute match case-insensitive (handles are case-preserved
        # in links but not meaningfully case-sensitive on YouTube's end).
        for frag in href_frags:
            ln(cosmetic("www.youtube.com", RENDERERS, f':has(a[href*="{frag}" i])'))
            ln(cosmetic("music.youtube.com", YTM_RENDERERS, f':has(a[href*="{frag}" i])'))

        # Feed-level hiding by channel name regex - also catches re-uploads/mirror
        # channels using a name pattern even when you don't have their ID/handle.
        if ch["pattern"]:
            ln(cosmetic("www.youtube.com", RENDERERS, f":has(#channel-name:has-text({ch['pattern']}))"))
            ln(cosmetic("www.youtube.com", RENDERERS, f":has(yt-formatted-string#channel-name:has-text({ch['pattern']}))"))
            ln(cosmetic("music.youtube.com", YTM_RENDERERS, f":has(yt-formatted-string:has-text({ch['pattern']}))"))

        # Whole channel/playlist page hiding
        for header in CHANNEL_PAGE_HEADERS:
            for frag in href_frags:
                ln(cosmetic("www.youtube.com", ["ytd-browse[page-subtype='channels']"], f':has({header} a[href*="{frag}" i])'))
            if ch["pattern"]:
                ln(cosmetic("www.youtube.com", ["ytd-browse[page-subtype='channels']"], f":has({header}:has-text({ch['pattern']}))"))
        if ch["pattern"]:
            ln(cosmetic("www.youtube.com", ["ytd-browse[page-subtype='playlist']"], f":has(ytd-playlist-header-renderer:has-text({ch['pattern']}))"))
        for frag in href_frags:
            ln(cosmetic("www.youtube.com", ["ytd-browse[page-subtype='playlist']"], f':has(ytd-playlist-header-renderer a[href*="{frag}" i])'))
    ln()

    ln("! YT/YTM VIDEOS")
    ln()
    for vid in unique_videos:
        ln(cosmetic("www.youtube.com", RENDERERS, f':has(a[href*="{vid}"])'))
        ln(f"||www.youtube.com/watch?v={vid}^")
        ln(f"||www.youtube.com/shorts/{vid}^")
        ln(f"||www.youtube.com/embed/{vid}^")
        ln(f"||youtu.be/{vid}^")
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
    print(f"Channels: {len(unique_channels)} (rule count per channel varies with id/handle/pattern fields present)")
    print(f"Videos:   {len(unique_videos)} x 8 (YT/YTM cosmetic + watch/shorts/embed/youtu.be network, x2 domains)")
    print(f"Keywords: {len(unique_keywords)} x 8 (Various Title/Channel combinations)")

if __name__ == "__main__":
    main()