# Tesseract OCR as Vision Fallback

When the vision/image analysis tool fails ("couldn't quite see it"), use Tesseract OCR via terminal as a reliable workaround.

## Prerequisites
```bash
# Check if installed
which tesseract && tesseract --version

# Install if needed (Ubuntu/Debian)
sudo apt-get install tesseract-ocr tesseract-ocr-ind tesseract-ocr-msa
```

## Hermes Image Location
When user sends image and vision fails, the image path is in the error message:
```
/root/.hermes/cache/images/img_[hash].jpg
```

## Usage Pattern
```bash
# OCR with Indonesian + English (mixed content)
tesseract /root/.hermes/cache/images/img_xxx.jpg /tmp/ocr_output -l ind+eng 2>&1
cat /tmp/ocr_output.txt

# English only (code, terminal output)
tesseract /root/.hermes/cache/images/img_xxx.jpg /tmp/ocr_output -l eng 2>&1
cat /tmp/ocr_output.txt
```

## Quality by Image Type

| Image Type | Expected Quality | Notes |
|------------|-----------------|-------|
| UI screenshots | ✅ High | Text is crisp, well-spaced |
| Terminal/console | ✅ High | Monospace font, high contrast |
| Documents/tables | ⚠️ Medium | Tables may lose structure |
| Handwritten text | ❌ Poor | Ask user to type instead |
| Small/low-res | ❌ Poor | Needs preprocessing |

## Language Codes
- `eng` = English (pre-installed)
- `ind` = Indonesian
- `msa` = Malay
- Combine: `-l ind+eng` for mixed content
- More: `apt install tesseract-ocr-[lang]`

## Limitations vs Vision Tool
- ❌ Cannot understand layout/context
- ❌ Cannot identify UI elements visually
- ❌ Cannot read charts/graphs
- ✅ Fast and reliable for text extraction
- ✅ Works without special provider setup

## Common Errors
```
Error in boxClipToRectangle: box outside rectangle
Error in pixScanForForeground: invalid box
```
These are warnings, not fatal errors — Tesseract still extracts text. Safe to ignore.

## Real Session Use Case
User sent screenshots of Claude Desktop settings to troubleshoot gateway issues. Vision tool failed. Tesseract successfully extracted:
- Menu items (General, Account, Privacy, Billing, etc.)
- Config file paths
- MCP server configuration
- Version numbers and URLs

This allowed full troubleshooting without vision capability.
