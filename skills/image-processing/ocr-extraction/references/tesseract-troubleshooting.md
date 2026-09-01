# Tesseract OCR Troubleshooting Guide

## Installation Issues

### "No space left on device"
**Diagnosis:** Disk full (common on Docker/VM environments)

**Fix:**
```bash
# Check disk usage:
df -h / /tmp /root

# Clean temp directories:
rm -rf /tmp/qodercli /tmp/pyinstxtractor /tmp/go-build*

# Docker cleanup (if running containers):
docker system prune -a -f

# Verify freed space:
df -h /  # Should show >1GB available
```

**Prevention:** Always check disk before heavy installs. Keep `du -sh /tmp/*` monitoring.

---

### pip install fails with HTTP timeout
**Cause:** PyPI mirrors slow/down, network instability

**Fix:** Use alternative mirror or download wheel offline:
```bash
pip3 install --use-mirror=https://pypi.tuna.tsinghua.edu.cn/simple pytesseract Pillow
```

Or download wheel manually and install locally.

---

## Accuracy Issues

### Low Confidence (<40%)
**Symptoms:** Gibberish text, wrong words detected

**Troubleshooting Steps:**

#### 1. Check Image Quality
```bash
# Inspect image resolution:
identify screenshot.png  # From ImageMagick

# If <72 DPI, increase resolution:
from PIL import Image
img = Image.open('screenshot.png')
high_res = img.resize((width*2, height*2), Image.Resampling.LANCZOS)
```

#### 2. Adjust Tesseract Config
```python
# For scanned documents with noise:
config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,;:()'

# For clean screenshots with clear text:
config = r'--oem 1 --psm 11'

# For tables/forms with complex layout:
config = r'--oem 3 --psm 3'
```

#### 3. Preprocess Image
```python
from PIL import Image, ImageFilter, ImageOps

# Convert to grayscale (better contrast):
gray = ImageOps.grayscale(img).convert('L')

# Apply threshold for binarization:
thresholded = gray.point(lambda x: 255 if x > 128 else 0, '1')

# Sharpen edges:
sharpened = thresholded.filter(ImageFilter.SHARPEN)

# Run OCR on preprocessed image:
result = pytesseract.image_to_string(sharpened, lang='eng+ind', config=config)
```

---

### Garbled Output (Wrong Language)
**Symptoms:** Text detected but in gibberish or mixed languages

**Fix:** Force language detection or specify explicitly:

```bash
# List available languages:
tesseract --list-langs

# Test with single language:
python3 /tmp/ocr_tool.py form.pdf --lang="eng"

# Or detect automatically (Tesseract v4+):
config = r'--psm 6'
result = pytesseract.image_to_data(img, lang='auto', config=config)
```

**Note:** Multi-language mixing requires careful segmentation. Best to split document into sections by language first.

---

## Empty Output

### No Text Detected at All
**Causes:**
- Image is purely graphical (no text content)
- Extremely low contrast
- Corrupted image file
- Image rotated/mirrored

**Debug Flow:**

```python
from PIL import Image
import pytesseract

def diagnose_ocr(image_path):
    # Step 1: Load and inspect
    img = Image.open(image_path)
    print(f"Format: {img.format}, Mode: {img.mode}, Size: {img.size}")
    
    # Step 2: Basic tesseract test
    from io import BytesIO
    bio = BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    
    result = pytesseract.run_tesseract(input=bio.read(), 
                                       lang='eng',
                                       config=r'--psm 6')
    
    return result

# Run diagnosis
output = diagnose_ocr('problem_image.png')
print(output.decode())
```

**Common Fixes:**
1. **Rotate image** if upside-down/sideways:
   ```python
   rotated = img.rotate(180, expand=True)
   ```
   
2. **Check contrast** visually or via histogram
   
3. **Verify file integrity**: `file problem_image.png`

---

## Performance Optimization

### Slow Processing (>30 seconds per image)
**Causes:** High resolution, complex layouts, wrong PSM mode

**Speed Tips:**

```python
# Downsample large images:
max_width = 2000
scale_factor = max_width / img.width
new_size = (max_width, int(img.height * scale_factor))
resized = img.resize(new_size, Image.Resampling.LANCZOS)

# Use faster PSM mode:
fast_config = r'--psm 6 --oem 1'  # Single block, neural net only

# Process in batches if multiple images:
# See scripts/batch_ocr.py for parallel processing example
```

---

## Environment-Specific Notes

### Hermes Agent Environment
**Known Issues:**
- Limited disk space (~30GB total) → always clean `/tmp` after heavy installs
- Python packages may fail due to space → use apt-get for binaries
- Vision API quota depletion common → OCR becomes primary extraction method

**Best Practices:**
1. Check disk: `df -h /` before any install
2. Clean up: `rm -rf /tmp/*` if space < 1GB
3. Prefer lightweight tools over heavy frameworks

---

## Reference Commands

### Quick Test Suite
```bash
#!/bin/bash
# test_ocr_setup.sh

echo "=== TESSERACT CHECK ==="
which tesseract || echo "❌ Not installed"

echo "=== LANGUAGE PACKS ==="
tesseract --list-langs | head -10

echo "=== TEST IMAGE ==="
echo "HELLO WORLD TEST 123" | tesseract stdin stdout

echo "=== PYTHON PACKAGE ==="
python3 -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

Run this script to verify complete setup.

---

Generated: 2026-08-24 by Qoder AI Agent
