import supervision as sv
import roboflow
import numpy as np
import cv2
import pandas as pd
import os
import CSVBetterer

# Initialize Roboflow model
rf = roboflow.Roboflow(api_key="API_Key_Here")  # Replace with your API Key
model = rf.workspace().project("scouting-2024").version("1").model  # Model ID and Train Number
tracker = sv.ByteTrack(lost_track_buffer=120)
smoother = sv.DetectionsSmoother(length=10)

# Define file path for CSV
file_path = "data.csv"
with open(file_path, 'w')as file:
    file.write("")# clears the file
    
# Define annotators
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

def callback(frame: np.ndarray, index: int) -> np.ndarray:
    # Convert the frame to RGB (Roboflow expects RGB)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Use the predict method
    results = model.predict(frame_rgb, confidence=40, overlap=30).json()
    
    # Convert Roboflow results to Detections format using from_inference
    detections = sv.Detections.from_inference(results)
    detections = tracker.update_with_detections(detections)
    detections = smoother.update_with_detections(detections)

    labels = [f"#{tracker_id}" for tracker_id in detections.tracker_id]

    # Ensure new_data is defined before converting to DataFrame
    new_data = {
        "frame_index": [index] * len(detections),
        "tracker_id": detections.tracker_id,
        "x_min": detections.xyxy[:, 0],
        "y_min": detections.xyxy[:, 1],
        "x_max": detections.xyxy[:, 2],
        "y_max": detections.xyxy[:, 3],
    }
    # Convert to DataFrame and append to CSV
    df = pd.DataFrame(new_data)
    df.to_csv(file_path, mode='a', index=False, header=not os.path.exists(file_path))

    # Annotate the frame
    annotated_frame = box_annotator.annotate(scene=frame.copy(), detections=detections)
    annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)

    return annotated_frame

sv.process_video(
    source_path="Video1",  # Video you want to process
    target_path="Video1Annotated",  # Output name of the video after processing
    callback=callback
)
CSVBetterer.run()
#Sent to wherever you are CD'd
