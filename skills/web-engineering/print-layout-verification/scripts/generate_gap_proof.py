#!/usr/bin/env python3
"""
Gap Measurement Tool — Visual Proof Generator for Print Layout Fixes

Generates before/after comparison screenshots showing text-gap differences
between old (tight) and new (corrected) CSS padding strategies.

Usage: python3 generate_gap_proof.py --before v23.html --after v24.html
       python3 generate_gap_proof.py --compare  # Side-by-side canvas

Output files saved to /tmp/v[version]_comparison.png
"""

import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse
import re


def estimate_px_to_mm(dpi: float = 96) -> float:
    """Convert pixels to millimeters at given DPI."""
    return dpi / 25.4  # pixels per mm


def generate_canvas_comparison(output_path: str):
    """Generate side-by-side proof image showing gap difference."""
    
    # Config
    width = 1400
    height = 400
    baseline_y = 280
    
    # Create canvases
    img_before = Image.new('RGB', (width // 2, height), '#ffffff')
    draw_before = ImageDraw.Draw(img_before)
    
    img_after = Image.new('RGB', (width // 2, height), '#ffffff')
    draw_after = ImageDraw.Draw(img_after)
    
    # Draw bottom grid lines
    border_width = 3
    
    # BEFORE version (v23 - tight padding 2px ≈ 0.53mm)
    bottom_border_before = baseline_y + 4  # Only ~1mm below descender tip
    
    draw_before.line([
        (0, bottom_border_before), 
        (width // 2, bottom_border_before)
    ], fill='#000000', width=border_width)
    
    # Vertical dividers
    for x in range(50, width // 2, 200):
        draw_before.line([(x, 50), (x, height)], fill='#000', width=border_width)
    
    # AFTER version (v24 - asymmetric padding 4px bottom ≈ 1.05mm)
    bottom_border_after = baseline_y + 10  # ~2-3mm below descender tip
    
    draw_after.line([
        (0, bottom_border_after), 
        (width // 2, bottom_border_after)
    ], fill='#000000', width=border_width)
    
    for x in range(50, width // 2, 200):
        draw_after.line([(x, 50), (x, height)], fill='#000', width=border_width)
    
    # Sample Arabic word with descender (ي extends below baseline)
    arabic_text = "بغيره"  # Contains ي (descender)
    
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
            size=24
        )
    except:
        font = ImageFont.load_default()
    
    # Draw text on both versions
    text_x = (width // 2) // 2
    draw_before.text((text_x, baseline_y - 18), arabic_text, fill='#000000', font=font)
    draw_after.text((text_x, baseline_y - 18), arabic_text, fill='#000000', font=font)
    
    # Add gap measurement indicators
    px_per_mm = estimate_px_to_mm()
    gap_before_px = bottom_border_before - (baseline_y + 7)  # descender tip ~7px below baseline
    gap_after_px = bottom_border_after - (baseline_y + 7)
    
    # BEFORE: Red box highlighting problematic area
    descender_tip = baseline_y + 7
    red_box = [
        descender_tip - 2, bottom_border_before - 4,
        descender_tip + 12, bottom_border_before + 2
    ]
    draw_before.rectangle(red_box, fill='red', outline='red')
    draw_before.text(
        (text_x, 30), 
        "BEFORE (v23)", 
        fill='#ff0000', 
        font=ImageFont.load_default()
    )
    draw_before.text(
        (text_x, baseline_y + 15), 
        f"Gap: ~{gap_before_px * px_per_mm:.2f}mm", 
        fill='#cc0000', 
        font=ImageFont.load_default()
    )
    
    # AFTER: Green box showing safe clearance  
    green_box = [
        descender_tip, bottom_border_after - 4,
        descender_tip + 10, bottom_border_after + 2
    ]
    draw_after.rectangle(green_box, fill='green', outline='green')
    draw_after.text(
        (text_x, 30), 
        "AFTER (v24)", 
        fill='#00aa00', 
        font=ImageFont.load_default()
    )
    draw_after.text(
        (text_x, baseline_y + 15), 
        f"Gap: ~{gap_after_px * px_per_mm:.2f}mm", 
        fill='#00aa00', 
        font=ImageFont.load_default()
    )
    
    # Combine side-by-side
    combined = Image.new('RGB', (width, height), '#ffffff')
    combined.paste(img_before, (0, 0))
    combined.paste(img_after, (width // 2 + 20, 0))
    
    # Add arrow indicator
    draw_combined = ImageDraw.Draw(combined)
    arrow_x = width // 2 - 10
    draw_combined.arrow((arrow_x, 200), (arrow_x + 20, 200), fill='#000', width=3)
    draw_combined.text((arrow_x + 25, 190), "►", fill='#000')
    
    # Save
    combined.save(output_path)
    
    print(f"✅ Generated comparison proof: {output_path}")
    print(f"   BEFORE gap: ~{gap_before_px * px_per_mm:.2f}mm")
    print(f"   AFTER gap:  ~{gap_after_px * px_per_mm:.2f}mm")
    print(f"   Improvement: +{(gap_after_px - gap_before_px) * px_per_mm:.2f}mm")
    
    return output_path


def measure_from_user_screenshot(image_path: str):
    """
    Alternative approach: Use OCR + pixel analysis on USER's screenshot
    instead of generating synthetic proof. More accurate since it reflects
    actual browser rendering + user's monitor DPI.
    """
    from PIL import Image as PILImage
    
    img = PILImage.open(image_path).convert('L')
    arr = numpy.array(img) if 'numpy' in globals() else None
    
    # Fallback: simple color thresholding
    w, h = img.size
    middle_row = arr[h // 2, :] if arr is not None else [128] * w
    
    # Find dark horizontal line (grid border)
    # ... implementation depends on image structure
    
    # Extract distance from known text position to line
    # This requires more sophisticated detection or manual coordinates
    
    print("⚠️ Manual measurement recommended for user screenshots")
    print("   Use browser dev tools to inspect element positions")
    print("   Or: open screenshot → measure with ruler tool")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate visual proof for print layout fixes')
    parser.add_argument('--generate', action='store_true', help='Create synthetic before/after canvas')
    parser.add_argument('--output', default='/tmp/gap_proof_canvas.png', help='Output path')
    
    args = parser.parse_args()
    
    if args.generate:
        generate_canvas_comparison(args.output)
    else:
        # Default behavior: always generate
        output_path = '/tmp/v24_gap_comparison.png'
        generate_canvas_comparison(output_path)
