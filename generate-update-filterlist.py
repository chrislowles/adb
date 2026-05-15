#!/usr/bin/env python3
"""
Filterlist generator.
Edit the three lists below, then run:  python3 generate-update-filterlist.py
Output: filterlist.txt
"""

# YOUTUBE CHANNEL IDs
# Find via: www.youtube.com/channel/<ID>
CHANNEL_IDS = []

# YOUTUBE VIDEO IDs
# Cosmetic hide + hard network block. Remove the ||www.youtube.com line in the template below if you only want feed-hiding without blocking direct links.
VIDEO_IDS = []

# YOUTUBE KEYWORDS
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
from datetime import date

OUTPUT_FILE = "filterlist.txt"

RENDERERS = [
    "ytd-rich-item-renderer",
    "ytd-video-renderer",
    "ytd-compact-video-renderer",
    "ytd-grid-video-renderer",
    "ytd-playlist-video-renderer",
    "ytd-channel-renderer",
]

def cosmetic(selector):
    parts = [f"{r}{selector}" for r in RENDERERS]
    return "www.youtube.com##" + ", ".join(parts)

out = []
def ln(s=""): out.append(s)

ln(f"! Title: Chris Lowles' Auto Regenerating Filterlist")
ln(f"! Description: Blocks YouTube content via channel id, video id, broad keywords, among other things (in the future)")
ln(f"! Generated: {date.today().isoformat()}")
ln()

ln("! CHANNELS")
ln()
for cid in sorted(set(CHANNEL_IDS)):
    ln(cosmetic(f':has(a[href*="/channel/{cid}"])'))
ln()

ln("! VIDEOS")
ln()
for vid in VIDEO_IDS:
    ln(cosmetic(f':has(a[href*="{vid}"])'))
    ln(f"||www.youtube.com/watch?v={vid}^")
ln()

ln("! BLOCKED KEYWORDS (title + channel name)")
ln()
for pattern, comment in KEYWORDS:
    ln(f"! {comment}")
    ln(cosmetic(f":has(#video-title:has-text({pattern}))"))
    ln(cosmetic(f":has(#channel-name:has-text({pattern}))"))
    ln()

# Append static filters if the file exists
if os.path.exists("static.txt"):
    ln("! ------------------------------------------")
    ln("! --- Included from static.txt  ---")
    ln("! ------------------------------------------")
    ln()
    with open("static.txt", "r", encoding="utf-8") as pf:
        for line in pf:
            # Strip newline characters so we don't end up with double spacing
            out.append(line.rstrip('\n'))

result = "\n".join(out)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(result)

# Re-calculated the total to include all viable rules (including from static.txt)
total = sum(1 for l in out if l.startswith("www.youtube.com##") or l.startswith("||") or ("##" in l and not l.startswith("!")))

print(f"Written {OUTPUT_FILE} ({total} rules)")
print(f"Channels: {len(set(CHANNEL_IDS))}")
print(f"Videos:   {len(VIDEO_IDS)} x 2 (cosmetic + network)")
print(f"Keywords: {len(KEYWORDS)} x 2 (title + channel name)")