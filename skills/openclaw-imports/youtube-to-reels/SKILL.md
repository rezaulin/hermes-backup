---
name: youtube-to-reels
description: Advanced YouTube to Reels/TikTok converter. Downloads video, uses AI to detect hooks, clips specific segments, converts to 9:16 vertical format with face detection, supports split screen for multiple speakers, and auto-generates captions. Use when user wants to create short-form vertical content from long YouTube videos, especially podcasts or talking head videos for Reels, TikTok, or Shorts.
---

# YouTube to Reels

## Primary Workflow: Hook Analysis First

**When user gives a YouTube link, the first and most important step is:**

### Phase 1: Hook Analysis (Priority)
1. Download video + subtitles
2. Analyze the entire video for **strong hooks**
3. Output in this exact format:

**🎣 Hook Analysis Result:**

- **Hook 1**: `00:15 - 00:42` → "Strong visual + surprising statement about X"
- **Hook 2**: `01:55 - 02:28` → "Question that creates curiosity + good energy"
- **Hook 3**: `04:10 - 04:55` → "Emotional story + relatable problem"

**Recommendation**: Best hook is #2 (highest retention potential)

---

### Phase 2: Clipping & Processing
After user chooses which hook(s) to use:
- Cut the selected time ranges
- Convert to 9:16 vertical
- Use face detection + split screen (if 2-3 faces)
- Generate and burn captions
- Output final Reels-ready videos

**Trigger this skill when user:**
- Gives a YouTube link and wants hook analysis
- Says "analisa hook", "cari hook", "buat reels dari video ini"
- Wants to turn long video into multiple shorts

## How to Use

1. Provide YouTube link
2. Specify target segments OR ask for hook analysis
3. Confirm which clips to process
4. Skill will output vertical videos ready for TikTok/Reels

See `references/workflow.md` for detailed step-by-step and `scripts/` for processing tools.
