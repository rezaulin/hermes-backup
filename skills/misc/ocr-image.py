#!/usr/bin/env python3
"""
OCR Skill - Extract text from images using Tesseract
Supports: English, Indonesian (Indochinese)
"""
import subprocess
from pathlib import Path
from PIL import Image

def ocr_from_image(image_path: str, languages: list = None) -> dict:
    """
    Extract text from image using Tesseract OCR
    
    Args:
        image_path: Path to image file
        languages: List of language codes ('eng', 'ind', 'chi_sim', etc.)
    
    Returns:
        dict with keys: 'text', 'confidence', 'languages_used'
    """
    if languages is None:
        languages = ['eng', 'ind']  # Default: English + Indonesian
    
    try:
        from PIL import Image
        import pytesseract
        
        # Setup tesseract
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        
        # Load image
        img = Image.open(image_path)
        
        # Configure for best accuracy
        custom_config = r'--oem 1 --psm 6'
        lang_string = '+'.join(languages)
        
        # Run OCR
        ocr_result = pytesseract.image_to_data(
            img, 
            lang=lang_string,
            config=custom_config,
            output_type=pytesseract.Output.DICT
        )
        
        # Extract text
        text_parts = []
        confidences = []
        for i, conf in enumerate(ocr_result['conf']):
            if float(conf) > 0:  # Only include recognized text
                word = ocr_result['text'][i]
                if word.strip():
                    text_parts.append(word)
                    confidences.append(float(conf))
        
        full_text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'success': True,
            'text': full_text.strip(),
            'confidence': round(avg_confidence, 2),
            'languages_used': languages,
            'word_count': len(text_parts),
            'preview': full_text[:200] + '...' if len(full_text) > 200 else full_text
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'text': ''
        }

# Quick test function
def test_ocr(sample_image: str):
    result = ocr_from_image(sample_image, ['eng', 'ind'])
    print(f"Test OCR Results:\n{result}")
    return result

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        test_ocr(sys.argv[1])
    else:
        print("Usage: python3 ocr_skill.py <image_path>")
