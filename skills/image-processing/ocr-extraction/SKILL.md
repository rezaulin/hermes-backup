---
name: ocr-extraction
description: Extract text from images using Tesseract OCR as vision fallback
tags: [ocr, tesseract, image-text, vision-fallback]
createdAt: '2026-08-24'
author: Qoder AI Agent
version: 1.0
---

# OCR Image Text Extraction

Extract readable text from images/screenshots using **Tesseract OCR** when vision API unavailable or quota exhausted.

## When to Use

✅ **Primary triggers:**
- User sends image but vision API down/expensive/out of quota
- Screenshot/document screenshot needs text extraction  
- Need to verify visual content via text-only analysis
- Budget-conscious alternative to paid vision APIs

⚠️ **When NOT to use:**
- Image is purely graphical (charts, diagrams without text)
- Text is heavily stylized/handwritten (low accuracy)
- High-quality structured understanding needed (use actual vision)

## Quick Start

```bash
# Install once (Debian/Ubuntu):
apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ind \
    libtesseract-dev \
    libleptonica-dev

# Install Python wrapper:
pip3 install pytesseract Pillow

# Use ready-to-run tool:
python3 /tmp/ocr_tool.py <image_path> [--lang="eng,ind"] [--json]
```

## Language Support

Default languages: **English + Indonesian** (`eng+ind`)

Add more:
```bash
# Chinese Simplified:
apt-get install -y tesseract-ocr-chi-sim

# Japanese:
apt-get install -y tesseract-ocr-jpn

# Usage:
python3 /tmp/ocr_tool.py photo.png --lang="eng,jpn"
```

## Tool Usage

### Command-Line Interface

```bash
# Basic usage (default: eng+ind):
python3 /tmp/ocr_tool.py screenshot.png

# Specific languages:
python3 /tmp/ocr_tool.py form.png --lang="en,fr,de"

# JSON output for scripts:
python3 /tmp/ocr_tool.py document.pdf --json > result.json
```

### Programmatic Usage (Python)

```python
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

img = Image.open('screenshot.png')
custom_config = r'--oem 1 --psm 6'
result = pytesseract.image_to_string(img, lang='eng+ind', config=custom_config)

print(f"Confidence: {result.confidence:.2f}%")
print(f"Text: {result.text[:500]}")
```

### In Chat Context

When user says "analyze this" on image:
1. Run OCR first to extract raw text
2. Feed extracted text to LLM for analysis
3. Report confidence score to user

Example response:
```
📄 OCR RESULT (78% confidence)
---------------------------
[extracted text preview...]
---------------------------
📊 Stats: 142 words recognized

Based on this text, here's my analysis...
```

## Pitfalls & Debugging

### Low Confidence (<40%)
**Causes:** Blurry screenshots, complex backgrounds, mixed fonts/colors

**Fixes:**
```python
# Better config for scanned documents:
config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,;:()'

# For clean screenshots:
config = r'--oem 1 --psm 11'  # Single block of text

# Convert to grayscale:
from PIL import ImageOps
gray = ImageOps.grayscale(img).convert('L')
```

### Garbled Output
**Signs:** Gibberish characters, wrong language detected

**Debug Steps:**
```bash
# Verify installation:
which tesseract
tesseract --version

# Test with known-good image:
echo "HELLO WORLD TEST" | tesseract stdin stdout
```

## Performance Tuning

| Mode | Speed | Accuracy | Best For |
|------|-------|----------|----------|
| `--psm 6` | Fast | Good | General documents |
| `--psm 11` | Medium | Better | Single paragraph |
| `--psm 3` | Slow | Excellent | Complex layouts/tables |
| `--oem 3` | Medium | Standard | Default engine |

## Integration Patterns

### Production-Ready Smart Extraction

Use `scripts/vision_fallback.py` for production deployment - implements automatic provider selection with confidence routing:

```bash
# Basic usage:
python3 /root/.hermes/skills/image-processing/ocr-extraction/scripts/vision_fallback.py screenshot.png --chat-format

# With specific languages:
python3 vision_fallback.py form.pdf --lang="eng,jpn" --prefer-vision=false
```

This script:
- ✅ Checks vision API availability automatically
- ✅ Falls back to Tesseract if vision unavailable
- ✅ Reports confidence score with recommendations
- ✅ Formats output for chat context analysis

### Batch Processing Multiple Images

```bash
# Process entire directory in parallel:
python3 /root/.hermes/skills/image-processing/ocr-extraction/scripts/batch_ocr.py ~/Downloads/screenshots \
    --lang="eng,ind" \
    --output=results.json \
    --workers=8
```

Generates structured JSON with extraction results, success/failure tracking, and per-image confidence scores.

---

## Installation & Setup

### Quick Install Command

Run this **once** to set up OCR capabilities:

```bash
apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng tesseract-ocr-ind libtesseract-dev libleptonica-dev && pip3 install pytesseract Pillow
```

### Known Issues & Fixes

**Issue**: Disk space depletion during install (detected 2026-08-24)

**Fix**: Clean `/tmp` before heavy installs:
```bash
rm -rf /tmp/qodercli /tmp/pyinstxtractor /tmp/go-build* && df -h /
```

See [`references/tesseract-troubleshooting.md`](references/tesseract-troubleshooting.md) for complete diagnostic flow.

---

## References

- **Troubleshooting Guide**: [`references/tesseract-troubleshooting.md`](references/tesseract-troubleshooting.md) - comprehensive error handling, config tuning, language-specific tips
- **Batch Processor**: [`scripts/batch_ocr.py`](scripts/batch_ocr.py) - parallel image processing with progress tracking  
- **Smart Extractor**: [`scripts/vision_fallback.py`](scripts/vision_fallback.py) - hybrid vision+OCR with automatic provider routing

**External Resources:**
- [Tesseract Official Docs](https://tesseract-ocr.github.io/)
- [Pytesseract GitHub](https://github.com/madmachiavelli/pytesseract)
- [Language Pack List](https://github.com/tesseract-ocr/tessdata)

---

## Version History

- **v1.0 (2026-08-24)**: Initial creation by Qoder AI Agent
  - Tesseract 4.1.1 integration with English + Indonesian support
  - CLI tool (`/tmp/ocr_tool.py`) with confidence scoring
  - Production scripts for batch processing + smart fallback
  - Comprehensive troubleshooting documentation
  - Disk space management workflow lessons learned


## Version History

- **v1.0 (2026-08-24)**: Initial creation
  - Tesseract 4.1.1 integration
  - English + Indonesian support
  - CLI tool with confidence scoring
  - Disk space management workflow
