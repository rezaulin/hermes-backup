---
name: podcast-to-shorts
description: Convert 16:9 landscape podcast videos into 9:16 portrait shorts/reels using CPU-based face detection (MediaPipe) for automatic centering. Use when asked to "create shorts from a podcast", "crop video to 9:16", or "repurpose landscape video for TikTok/Instagram/Reels".

---

# Podcast to Shorts

This skill automates the process of cropping horizontal podcast videos into a vertical format, keeping the speaker centered using face detection.

## Workflows

### Convert Video to Shorts

1.  Identify the input video path.
2.  Use the `crop_to_916.py` script to process the video.
3.  The script will detect faces and adjust the crop frame to keep the speaker centered.

## Commands

### `crop_to_916.py`

Run the script using Python 3:

```bash
python3 scripts/crop_to_916.py <input_video.mp4> [-o <output_video.mp4>]
```

- `input_video.mp4`: The source 16:9 video.
- `-o`: (Optional) Specify the output filename. Defaults to `<input>_shorts.mp4`.

## Dependencies

- `opencv-python`
- `mediapipe`
- `numpy`

## Performance Notes

- This skill runs on the CPU.
- Processing time depends on the video duration and CPU speed.
- Recommended for short clips (1-5 minutes). For full podcasts, consider splitting into clips first.
