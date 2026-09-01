#!/usr/bin/env python3
"""
Batch OCR Processing for Multiple Images
Processes images in parallel using ThreadPoolExecutor

Usage: python3 batch_ocr.py <image_dir> [--lang="eng,ind"] [--output=result.json]
"""
import subprocess
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import argparse

def process_single_image(image_path: str, lang: str) -> Dict[str, Any]:
    """Process a single image via OCR."""
    
    try:
        from PIL import Image
        import pytesseract
        
        # Setup tesseract
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        
        img = Image.open(image_path)
        
        # Use optimized config
        custom_config = r'--oem 1 --psm 6'
        result_data = pytesseract.image_to_data(
            img, 
            lang=lang,
            config=custom_config,
            output_type=pytesseract.Output.DICT
        )
        
        # Extract text with confidence filtering
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
            'success': True,
            'path': str(image_path),
            'filename': Path(image_path).name,
            'text': full_text.strip(),
            'confidence': round(avg_confidence, 2),
            'word_count': len(text_parts),
            'preview': full_text[:200] + ('...' if len(full_text) > 200 else '')
        }
        
    except Exception as e:
        return {
            'success': False,
            'path': str(image_path),
            'filename': Path(image_path).name,
            'error': str(e)
        }

def main():
    parser = argparse.ArgumentParser(description='Batch OCR processing')
    parser.add_argument('input_dir', help='Directory containing images')
    parser.add_argument('--lang', default='eng,ind', help='Language codes (comma-separated)')
    parser.add_argument('--output', help='Output JSON file (default: stdout)')
    parser.add_argument('--workers', type=int, default=4, help='Parallel workers')
    
    args = parser.parse_args()
    
    # Find all images
    input_path = Path(args.input_dir)
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}
    images = [f for f in input_path.iterdir() if f.suffix.lower() in image_extensions]
    
    if not images:
        print(f"❌ No images found in {args.input_dir}")
        return
    
    print(f"Found {len(images)} images to process")
    print(f"Languages: {args.lang}")
    print(f"Workers: {args.workers}")
    print()
    
    results = []
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_img = {
            executor.submit(process_single_image, str(img), args.lang): img 
            for img in images
        }
        
        for future in as_completed(future_to_img):
            result = future.result()
            results.append(result)
            
            # Progress indicator
            status = "✅" if result['success'] else "❌"
            preview = result.get('preview', result.get('error', 'N/A'))[:50]
            print(f"{status} {Path(result['path']).name}: {preview}...")
    
    # Summary statistics
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Success: {success_count}/{len(results)}")
    print(f"Failed: {fail_count}/{len(results)}")
    
    if fail_count > 0:
        print("\nFailed files:")
        for r in results:
            if not r['success']:
                print(f"  ❌ {r['filename']}: {r['error']}")
    
    # Output results
    output_json = {
        'total_images': len(results),
        'successful': success_count,
        'failed': fail_count,
        'language_used': args.lang.split(','),
        'results': results
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output_json, f, indent=2)
        print(f"\nResults saved to {args.output}")
    else:
        print(json.dumps(output_json, indent=2))

if __name__ == '__main__':
    main()
