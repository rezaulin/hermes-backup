---
name: ai-video-marketing-prompts
description: "Craft & iterate two-step AI-generation prompt chains for product marketing videos: (1) DALL-E storyboard prompt, (2) storyboard→video prompt (Omni/Veo/Kling-family generators). Covers no-narration fashion clips, vertical 9:16 social formats, and seamless-loop construction. Load when the user wants to generate marketing/promo videos, storyboards, or ad clips with AI image+video generators — especially fashion/product showcases."
tags: [video, marketing, dalle, storyboard, prompt-engineering, fashion, social-media]
---

# AI Video Marketing Prompts (storyboard → video, two-step)

The user's standard workflow: **product reference photo → Prompt 1 (image gen: DALL-E) produces a numbered storyboard grid → Prompt 2 (video gen, e.g. "Omni") animates it**. The user works in fashion and wants movement-only clips (dance/spin/pose), never narration. Ready-to-fill templates: `templates/storyboard-loop-9x16.txt` (10 s seamless loop, Prompt 1) and `templates/video-loop-9x16.txt` (Prompt 2). Copy, fill the `[...]` slots, adapt panel count to duration.

## Structure of Prompt 1 (storyboard, DALL-E)

Always include, in this order:
1. Grid spec: N-panel storyboard grid, orientation + frame layout, numbered panels.
2. **Hard constraints up front**: no dialogue, no text overlay, no narration — pure movement.
3. Product/model/style/mood slots (product description, model description, setting, campaign mood).
4. Reference-image lock sentence when a product photo is attached: *"The garment design, color, and details MUST match the attached reference image exactly."*
5. Per-panel shot list with explicit camera + movement beats (see duration table).
6. Consistency block: identical lighting/background/lens/model styling across ALL panels.

## Structure of Prompt 2 (video gen)

1. Duration + orientation + source ("from this storyboard").
2. Motion direction: describe the through-line movement (dance routine / one full 360 spin) and per-panel beats.
3. Loop requirements (if seamless loop requested — see below).
4. Camera behavior: push-in on details, tracking on spins, camera RETURNS to start position by final frame.
5. Constraints: no dialogue/voiceover/text, garment 100% consistent, no morphing artifacts, product never obstructed.
6. Style footer: premium campaign, cinematic lighting, platform-ready (TikTok/Reels/Shorts).

## Duration → panel count & beat pacing

| Duration | Panels | Beat pattern |
|---|---|---|
| 10 s | 6 | hero pose → dance start → back-spin → detail close-up → spin complete → return to hero |
| 15 s | 8 | hero → dance → spin back → detail → low-angle dance → full 360 → walk-in → hero |

## Seamless-loop construction (owner-requested 2026-08)

A loop only works if ALL of these are specified in BOTH prompts:
- Panel 1 == final panel: identical pose, position, angle, framing ("loop anchor frame" — say it explicitly).
- The movement must form a closed cycle — **one complete 360° spin is the most reliable return-to-start motion**.
- Velocity at the seam: movement must decelerate to zero (or match) at the loop point; explicitly say "no visible jump, pause, or acceleration spike at the seam".
- Background + lighting static across the full duration.
- Camera returns to its starting position by the final frame.
- Post-generation test: play 3–4× consecutively; if the cut point is invisible, it works.
- If the video generator has a native loop mode, enable it — more reliable than prompt-only looping.

## Pitfalls

- **DALL-E panel inconsistency**: separate panels drift in garment details/lighting. Mitigation: regenerate a few times and cherry-pick panels; emphasize the consistency block; keep the reference image attached.
- **Don't let the camera obstruct the product** — video generators love dramatic angles that cover the garment; state it as an explicit constraint.
- **Text/dialogue leakage**: video generators often invent captions or speech; repeat the no-text/no-dialogue constraint in BOTH prompts.
- Vertical 9:16 must be stated in BOTH prompts (storyboard layout AND video format) or the generator defaults to landscape.
- Leave interpretation room for the generator where the user says "beri ruang AI untuk menganalisa": describe the movement STYLE and beats, not exact keyframe positions.

## Analyzing a reference video first

When the user sends a reference video to imitate: extract frames locally (`ffmpeg -i vid.mp4 -vf fps=1 frame_%02d.jpg`), probe metadata with ffprobe (duration/resolution/fps/audio), then run vision analysis on 3–5 keyframes before writing the prompts. If the vision API is down, fall back to metadata + whatever analysis succeeds and tell the user what couldn't be verified.
