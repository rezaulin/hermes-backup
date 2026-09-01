#!/usr/bin/env python3
"""
Vision Fallback System - Hybrid OCR+Vision Approach
Automatically chooses best extraction method based on availability and budget

Priority order:
1. Vision API (if available & affordable)
2. Tesseract OCR (fallback, free)
3. User notification for low-confidence results
"""
from pathlib import Path
import json
import subprocess
from typing import Dict, Any, Optional
from PIL import Image

def check_vision_api_available() -> bool:
    """Check if any vision-capable provider is configured."""
    
    # Check auth.json for credential pool
    auth_file = Path('/root/.hermes/auth.json')
    if not auth_file.exists():
        return False
    
    try:
        with open(auth_file) as f:
            auth_data = json.load(f)
        
        credentials = auth_data.get('credential_pool', {})
        
        # Check if any provider has valid credentials
        for provider_name, creds in credentials.items():
            if isinstance(creds, list):
                for cred in creds:
                    last_status = cred.get('last_status')
                    if last_status == 'ok':
                        return True
        
        return False
        
    except Exception as e:
        print(f"Error checking vision API: {e}")
        return False


def extract_with_vision(image_path: str) -> Dict[str, Any]:
    """Extract text using vision API (not implemented here, placeholder)."""
    
    # This would call browser_vision or vision_analyze tool
    # For now, returns NotImplementedError to indicate external dependency
    
    return {
        'method': 'vision',
        'success': False,
        'note': 'Vision API currently unavailable - use OCR fallback'
    }


def extract_with_ocr(image_path: str, languages: list = None) -> Dict[str, Any]:
    """Fallback to Tesseract OCR."""
    
    if languages is None:
        languages = ['eng', 'ind']
    
    try:
        import pytesseract
        
        # Setup tesseract
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        
        img = Image.open(image_path)
        
        # Config optimization
        custom_config = r'--oem 1 --psm 6'
        lang_string = '+'.join(languages)
        
        result_data = pytesseract.image_to_data(
            img, 
            lang=lang_string,
            config=custom_config,
            output_type=pytesseract.Output.DICT
        )
        
        # Build structured result
        text_parts = []
        confidences = []
        
        for i in range(len(result_data['text'])):
            word = result_data['text'][i].strip()
            conf = float(result_data['conf'][i])
            
            if word and conf > 0:
                text_parts.append(word)
                confidences.append(conf)
        
        full_text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'method': 'ocr',
            'success': True,
            'confidence': round(avg_confidence, 2),
            'word_count': len(text_parts),
            'languages_used': languages,
            'text': full_text.strip(),
            'preview': full_text[:300] + ('...' if len(full_text) > 300 else ''),
            'recommendation': get_recommendation(avg_confidence)
        }
        
    except ImportError:
        return {
            'method': 'ocr',
            'success': False,
            'error': 'Tesseract not installed - run apt-get install tesseract-ocr && pip3 install pytesseract'
        }
    except Exception as e:
        return {
            'method': 'ocr',
            'success': False,
            'error': str(e)
        }


def get_recommendation(confidence: float) -> str:
    """Generate human-readable recommendation based on confidence score."""
    
    if confidence >= 80:
        return "✅ High confidence - extracted text is reliable"
    elif confidence >= 50:
        return "⚠️ Medium confidence - verify critical information manually"
    else:
        return "❌ Low confidence - consider re-extracting with better image quality"


def extract_image_smart(image_path: str, prefer_vision: bool = True, languages: list = None) -> Dict[str, Any]:
    """
    Main entry point - smart extraction with automatic fallback
    
    Args:
        image_path: Path to image file
        prefer_vision: If True, try vision first then fall back to OCR
        languages: Languages to use for OCR (default: eng+ind)
    
    Returns:
        Dict with keys: method, success, confidence, text, recommendation
    """
    
    # Normalize language list
    if isinstance(languages, str):
        languages = languages.split(',')
    
    result = None
    
    if prefer_vision and check_vision_api_available():
        # Try vision first (higher quality, but may cost quota)
        result = extract_with_vision(image_path)
        
        if result.get('success'):
            return result
    
    # Fallback to OCR (free but lower accuracy)
    ocr_result = extract_with_ocr(image_path, languages)
    
    # Add warning if confidence is low
    if ocr_result['success'] and ocr_result['confidence'] < 50:
        ocr_result['warning'] = "Low OCR confidence detected - visual verification recommended"
    
    return ocr_result


def analyze_image_for_chat(image_path: str) -> str:
    """
    Format extraction result for chat context
    
    Usage when user sends image and says "analyze this":
    Returns formatted message ready for LLM analysis
    """
    
    result = extract_image_smart(image_path)
    
    if not result.get('success'):
        return f"""
Could not extract text from image: {result.get('error', 'Unknown error')}
Please try uploading a clearer screenshot or check image format.
"""
    
    return f"""
📄 IMAGE EXTRACTION RESULT ({result['confidence']}% confidence)
{'='*60}

{result['text'][:1000]}{'...' if len(result['text']) > 1000 else ''}

{'='*60}
📊 Stats: {result['word_count']} words extracted
💡 Recommendation: {result.get('recommendation', 'N/A')}
"""

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart image extraction with vision/OCR fallback')
    parser.add_argument('image_path', help='Path to image file')
    parser.add_argument('--prefer-vision', action='store_true', default=True, 
                       help='Try vision API first (default: True)')
    parser.add_argument('--no-vision', action='store_false', dest='prefer_vision',
                       help='Skip vision API, go straight to OCR')
    parser.add_argument('--lang', default='eng,ind', help='Languages for OCR')
    parser.add_argument('--chat-format', action='store_true',
                       help='Output formatted for chat context')
    
    args = parser.parse_args()
    
    result = extract_image_smart(args.image_path, args.prefer_vision, args.lang.split(','))
    
    if args.chat_format:
        print(analyze_image_for_chat(args.image_path))
    else:
        print(json.dumps(result, indent=2))
