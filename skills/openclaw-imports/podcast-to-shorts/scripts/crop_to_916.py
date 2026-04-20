import cv2
import mediapipe as mp
import numpy as np
import argparse
import os

def process_video(input_path, output_path):
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {input_path}")
        return

    # Get video properties
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Target 9:16 aspect ratio (Portrait)
    # We keep height, and calculate width as height * 9/16
    target_height = orig_height
    target_width = int(target_height * 9 / 16)

    # Output codec (H.264 if possible, or mp4v)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))

    print(f"Processing: {orig_width}x{orig_height} -> {target_width}x{target_height} @ {fps}fps")

    frame_count = 0
    last_x_center = orig_width // 2 # Default center

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detect face for centering
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)

        if results.detections:
            # Take the first detected face (usually the most prominent)
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            x_center = int((bbox.xmin + bbox.width / 2) * orig_width)
            
            # Simple smoothing (moving average or lerp could be added here)
            # For now, let's use a very basic smoothing to avoid jitter
            current_x_center = int(0.1 * x_center + 0.9 * last_x_center)
        else:
            current_x_center = last_x_center

        # Calculate crop area
        left = current_x_center - target_width // 2
        right = current_x_center + target_width // 2

        # Boundary checks
        if left < 0:
            left = 0
            right = target_width
        if right > orig_width:
            right = orig_width
            left = orig_width - target_width

        # Crop and write
        cropped_frame = frame[0:target_height, left:right]
        out.write(cropped_frame)

        last_x_center = current_x_center
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"Progress: {frame_count}/{total_frames} frames", end='\r')

    cap.release()
    out.release()
    print(f"\nFinished! Saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crop 16:9 podcast to 9:16 shorts using face detection.")
    parser.add_argument("input", help="Input video file path")
    parser.add_argument("-o", "--output", help="Output video file path (default: input_shorts.mp4)")
    
    args = parser.parse_args()
    
    if not args.output:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}_shorts.mp4"
        
    process_video(args.input, args.output)
