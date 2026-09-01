#!/usr/bin/env python3
"""
OCR Tool - Extract text from images using Tesseract OCR
Supports: English, Indonesian (ind), Arabic (ara)

Use when vision API fails or need to extract text from screenshot/image.

Usage:
    python3 ocr_tool.py <image_path> [--lang="eng,ind"] [--json]
    
Example:
    python3 ocr_tool.py /root/.hermes/cache/images/img_8ff8fd698ada.jpg
    python3 ocr_tool.py raport_screenshot.png --lang="eng,ara" --json
"""

import subprocess
import argparse
from pathlib import Path
import pytesseract
from PIL import Image

def ocr_from_image(image_path: str, languages: list = None) -> dict:
    """
    Extract text from image with confidence score
    
    Args:
        image_path: Path to image file
        languages: List of language codes (e.g., ['eng', 'ind', 'ara'])
    
    Returns:
        dict with keys: success, text, confidence, languages_used, word_count
    """
    if languages is None:
        languages = ['eng', 'ind']  # Default: English + Indonesian
    
    try:
        # Setup tesseract
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        
        img = Image.open(image_path)
        
        # Configure for best accuracy on documents/screenshots
        custom_config = r'--oem 3 --psm 6'
        lang_string = '+'.join(languages)
        
        result = pytesseract.image_to_data(
            img, 
            lang=lang_string,
            config=custom_config,
            output_type=pytesseract.Output.DICT
        )
        
        # Build full text with confidence scoring
        text_parts = []
        confidences = []
        
        for i in range(len(result['text'])):
            text = result['text'][i].strip()
            conf = float(result['conf'][i])
            
            # Only include recognized text (confidence > 0)
            if text and conf > 0:
                text_parts.append(text)
                confidences.append(conf)
        
        full_text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'success': True,
            'text': full_text.strip(),
            'confidence': round(avg_confidence, 2),
            'languages': languages,
            'word_count': len(text_parts),
            'preview': full_text[:500] + '...' if len(full_text) > 500 else full_text
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'text': ''
        }

def main():
    parser = argparse.ArgumentParser(description='Extract text from images using Tesseract OCR')
    parser.add_argument('image_path', help='Path to image file')
    parser.add_argument('--lang', default='eng,ind', help='Language codes (comma-separated, e.g., "eng,ind,ara")')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    image_path = Path(args.image_path)
    if not image_path.exists():
        print(f"❌ Error: File not found: {args.image_path}")
        return
    
    try:
        result = ocr_from_image(str(image_path), args.lang.split(','))
        
        if args.json:
            import json
            print(json.dumps(result, indent=2))
        else:
            if result['success']:
                print("\n" + "="*60)
                print("📄 OCR RESULT")
                print("="*60)
                print(f"\n🔤 Text ({result['confidence']}% confidence):")
                print("-"*60)
                print(result['text'])
                print("-"*60)
                print(f"📊 Stats: {result['word_count']} words recognized")
                
                # Warning if confidence is low
                if result['confidence'] < 40:
                    print(f"\n⚠️ Low confidence ({result['confidence']}%) - consider improving image quality")
            else:
                print(f"❌ OCR Failed: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == '__main__':
    main()
