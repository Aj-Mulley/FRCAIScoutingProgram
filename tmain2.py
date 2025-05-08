import os
import cv2
import numpy as np
import supervision as sv
from inference_sdk import InferenceConfiguration, InferenceHTTPClient
import pandas as pd
import CSVBetterer
import LRS4
import border_patrol

# Define directories
INPUT_VIDEO_DIR = "input_videos"#May requre an absolute file path.
OUTPUT_CSV_DIR = "output_csvs"
OUTPUT_VIDEO_DIR = "output_videos"

# Ensure output directories exist
os.makedirs(OUTPUT_CSV_DIR, exist_ok=True)
os.makedirs(OUTPUT_VIDEO_DIR, exist_ok=True)

# Inference configuration
MODEL_ID = "scouting_2025/2"
config = InferenceConfiguration(confidence_threshold=0.70, iou_threshold=0.5)
client = InferenceHTTPClient(api_url="http://localhost:9001", api_key="TUPEgxt5z5tg8Odp1kri")
client.configure(config)
client.select_model(MODEL_ID)

Video_Widths = []

def get_video_width(video_path):
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return None
    
    # Get video width and height
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    cap.release()
    return width

def process_video(video_path: str, stride: int = 3):
    # Annotators and trackers
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    tracker = sv.ByteTrack(lost_track_buffer=1200)
    smoother = sv.DetectionsSmoother(length=5)

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    csv_path = os.path.join(OUTPUT_CSV_DIR, f"{video_name}.csv")
    output_video_path = os.path.join(OUTPUT_VIDEO_DIR, f"{video_name}_annotated.mp4")

    # Clear existing CSV content
    with open(csv_path, 'w') as file:
        file.write("")

    Video_Widths.append(get_video_width(video_path))

    def callback(frame: np.ndarray, index: int) -> np.ndarray:
        # Only process frames at the defined stride interval.
        if index % stride != 0:
            return frame

        results = client.infer(frame)
        detections = sv.Detections.from_inference(results)
        detections = tracker.update_with_detections(detections)
        detections = smoother.update_with_detections(detections)
        labels = [f"#{tracker_id}" for tracker_id in detections.tracker_id]

        new_data = {
            "frame_index": [index] * len(detections),
            "tracker_id": detections.tracker_id,
            "x_min": detections.xyxy[:, 0],
            "y_min": detections.xyxy[:, 1],
            "x_max": detections.xyxy[:, 2],
            "y_max": detections.xyxy[:, 3],
        }
        df = pd.DataFrame(new_data)
        df.to_csv(csv_path, mode='a', index=False, header=not os.path.exists(csv_path))

        # Annotate the frame (you can also pass stride to the annotator if needed)
        annotated_frame = box_annotator.annotate(scene=frame.copy(), detections=detections)
        annotated_frame = label_annotator.annotate(
            scene=annotated_frame, detections=detections, labels=labels
        )
        return annotated_frame

    sv.process_video(source_path=video_path, target_path=output_video_path, callback=callback)

# Process each video in the input directory
for filename in os.listdir(INPUT_VIDEO_DIR):
    if filename.lower().endswith(('.mp4', '.avi', '.mov')):
        video_path = os.path.join(INPUT_VIDEO_DIR, filename)
        process_video(video_path)

CSVBetterer.run(OUTPUT_CSV_DIR)
border_patrol.run(OUTPUT_CSV_DIR)
LRS4.run(Video_Widths)