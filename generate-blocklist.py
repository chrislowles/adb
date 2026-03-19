#!/usr/bin/env python3
"""
YouTube uBO filterlist generator.
Edit the three lists below, then run:  python3 generate-blocklist.py
Output: youtube-blocklist.txt
"""

# CHANNEL IDs
# Find via: www.youtube.com/channel/<ID>
CHANNEL_IDS = [
    "UCyV8SuQd21sFoPCiB0RgcrA",
    "UCxsQFG_8Dbt1sZhLReL2mUw",
    "UClCmqa3I2zBYoiNgM_CvA2g",
    "UC3ltptWa0xfrDweghW94Acg",
    "UCtMVHI3AJD4Qk4hcbZnI9ZQ",
    "UCx6B1qITFfLp_q3MeO--zWQ",
    "UCizwyb402SKTC8S58w-BvnA",
    "UCQeRaTukNYft1_6AZPACnog",
    "UCLtREJY21xRfCuEKvdki1Kw",
    "UCZZHPXsg6LopvdOKF7qM6cQ",
    "UC7pp40MU_6rLK5pvJYG3d0Q",
    "UC0woBco6Dgcxt0h8SwyyOmw",
    "UCQ-hpFPF4nOKoKPEAZM_THw",
    "UC64UiPJwM_e9AqAd7RiD7JA",
    "UCT3v6vL2H5HK4loLMc8pmCw",
    "UClnDI2sdehVm1zm_LmUHsjQ",
    "UCHKRfxkMTqiiv4pF99qGKIw",
    "UCnb-VTwBHEV3gtiB9di9DZQ",
    "UCYY5GWf7MHFJ6DZeHreoXgw",
    "UC3Wn3dABlgESm8Bzn8Vamgg",
    "UCp1tsmksyf6TgKFMdt8-05Q",
    "UCZdWrz8pF6B5Y_c6Zi6pmdQ",
    "UCf-U0uPVQZtcqXUWa_Hl4Mw",
    "UC9h8BDcXwkhZtnqoQJ7PggA",
    "UC3uUuK_UQvteUCXnEHNNG6Q",
    "UCCfJK7-sMQiZjGH_bqsJBgw",
    "UCO0akufu9MOzyz3nvGIXAAw",
    "UCa2MXjBtWn91WPHWRBCLI6Q",
    "UCnw5I-wliudW8YO1vr5O4IQ",
    "UCXIJgqnII2ZOINSWNOGFThA",
    "UCrvhNP_lWuPIP6QZzJmM-bw",
    "UCLCtfaPS59szuaLerQkLkKg",
    "UCDuhTmjTK_SXauI-YXV8lQQ",
    "UCbRP3c757lWg9M-U7TyEkXA",
    "UCplQ6jBcw_rFBjRA-Ta0Zyg",
    "UC0a8nteER_pU4Aj6hmEyJAQ",
    "UCEKJKJ3FO-9SFv5x5BzyxhQ",
    "UCmu9PVIZBk-ZCi-Sk2F2utA",
    "UCcWkShE9dqAw8uM1RJC99fQ",
    "UCV6mNrW8CrmWtcxWfQXy11g",
    "UCSIKKd_AkoV3c4F5CI4JAnQ",
    "UCqQUH9wOCH8h85yjk5HOALw",
    "UCnCtsHZBBrYxojm0IMSu3Xg",
    "UCMiJRAwDNSNzuYeN2uWa0pA",
    "UCovndCJjH4fO1DW_ZnM0cZw",
    "UCUXybwy3R514eWOZedrlBdg",
    "UCKmkpoEqg1sOMGEiIysP8Tw",
    "UCR9_QviDbej3B5vTn3WdYiA",
    "UCGA2OgjW608QEaGwxA7aRTg",
    "UCc30Q1bAxLtfzeS_jh7J5wQ",
    "UCl1E5-Fm5q7VB4dKbbDyIOA",
    "UCAG1ABZP-c7wuNt0fziHtsA",
    "UCMnULQ6F6kLDAHxofDWIbrw",
    "UCMwJJL5FJFuTRT55ksbQ4GQ",
    "UC0aanx5rpr7D1M7KCFYzrLQ",
    "UC1jYOomx7yjGx-TFqgIYybg",
    "UCWtOcQKcrIGkCCLjqT6p70A",
    "UCSNPNe6E2EL2iDSg_DDA6iQ",
    "UCNvsIonJdJ5E4EXMa65VYpA",
    "UCGh4KSR8TZZlyq3qQDBsBLA",
]

# VIDEO IDs
# Cosmetic hide + hard network block. Remove the ||www.youtube.com line in the
# template below if you only want feed-hiding without blocking direct links.
VIDEO_IDS = [
    "bhq0GzA1yXw",
    "kXRlOMEkC9o",
    "B2-3InWE9zM",
    "QjvABe1rEck",
    "MCYGITyaJdw",
    "qNqL-SIcovU",
    "8o_9xG7D3yY",
    "0u_xm5vTZ9A",
    "gBk0n_FGp0k",
    "eAAtM3JkIrM",
    "P5lvwQHZJ4U",
    "c-4JsutGwAY",
    "gKj7gmKdJEw",
    "UQGP24qEfBc",
    "Cj6UrGQqmbA",
    "f57ZOnZfrT4",
    "e1YIMtvamNc",
    "SBHx8Nj25AY",
    "rKR6as6CXhw",
    "SlAA4gZScCQ",
    "-9CmFvGEXXk",
    "tHeVxwPaPYM",
    "aNGwKOm3rjo",
    "wOzGAsMRHyI",
    "Uu2FQ2hW4_o",
    "IoA_84VrMt8",
    "h_LB43VP1ko",
    "c-01g6O0g3E",
    "yOkTk1Exlqo",
    "Ga7FWlBiqh8",
    "9Khoa3lcx0Y",
    "QR2aSM62EQA",
    "EP5JpA0bGzU",
    "psH--Qo-MwQ",
    "2TqOn0XUzq4",
    "Fxfgi1YnXeY",
    "d1pdxekzD9Q",
    "e75fLoT2JHw",
    "TuAvg6FEB5E",
    "iOK5zyyCyMw",
    "aKMIkgNbqmc",
    "2dQ18lVaEug",
    "-0MD3Jn60fw",
    "u9nvW_-KApA",
    "ru-29iQz8jk",
    "wrbyP7y5z80",
    "AGSHBa17sLM",
    "DPNlF-keekc",
    "EL6HcvBFTDw",
    "0NJ-WZtqeeE",
    "FM6qzVpbUuU",
    "a6h15ewjLwM",
    "vF0EN5AkULY",
    "LGCJefnJkG4",
    "4ZlwTtgbgVA",
    "QITiC4v0Tf8",
]

# KEYWORD PATTERNS
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
    #("/penguinz0/i", "penguinz0"),
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

from datetime import date

OUTPUT_FILE = "youtube-blocklist.txt"

RENDERERS = [
    "ytd-rich-item-renderer",
    "ytd-video-renderer",
    "ytd-compact-video-renderer",
    "ytd-grid-video-renderer",
    "ytd-playlist-video-renderer",
]

def cosmetic(selector):
    parts = [f"{r}{selector}" for r in RENDERERS]
    return "www.youtube.com##" + ", ".join(parts)

out = []
def ln(s=""): out.append(s)

ln(f"! Title: YouTube Personal Blocklist")
ln(f"! Description: Converted from BlockTube backup — blocks channels, videos, and title keywords")
ln(f"! Generated: {date.today().isoformat()}")
ln(f"! DO NOT EDIT — regenerate by running: python3 generate-blocklist.py")
ln()

ln("! BLOCKED CHANNELS")
ln()
for cid in sorted(set(CHANNEL_IDS)):
    ln(cosmetic(f':has(a[href*="/channel/{cid}"])'))
ln()

ln("! BLOCKED VIDEOS")
ln()
for vid in VIDEO_IDS:
    ln(cosmetic(f':has(a[href*="{vid}"])'))
    ln(f"||www.youtube.com/watch?v={vid}^")
    ln(f"||youtu.be/{vid}^")
ln()

ln("! BLOCKED KEYWORDS (title + channel name)")
ln()
for pattern, comment in KEYWORDS:
    ln(f"! {comment}")
    ln(cosmetic(f":has(#video-title:has-text({pattern}))"))
    ln(cosmetic(f":has(#channel-name:has-text({pattern}))"))
    ln()

result = "\n".join(out)
with open(OUTPUT_FILE, "w") as f:
    f.write(result)

total = sum(1 for l in out if l.startswith("www.youtube.com##") or l.startswith("||"))
print(f"Written {OUTPUT_FILE}  ({total} rules)")
print(f"  Channels: {len(set(CHANNEL_IDS))}")
print(f"  Videos:   {len(VIDEO_IDS)} x 2 (cosmetic + network)")
print(f"  Keywords: {len(KEYWORDS)} x 2 (title + channel name)")