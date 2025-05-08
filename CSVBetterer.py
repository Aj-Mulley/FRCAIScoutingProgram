import pandas as pd
import os
import glob
import numpy as np

def run(directory):
    column_names = ["frame_index", "tracker_id", "x1", "y1", "x2", "y2"]

    csv_files = glob.glob(os.path.join(directory, "*.csv"))

    for file_path in csv_files:
        # Read CSV without headers and ensure data types
        df = pd.read_csv(file_path, names=column_names, dtype={
            "frame_index": int,
            "tracker_id": int,
            "x1": float,
            "x2": float,
            "y1": float,
            "y2": float
        })

        # Compute average coordinates
        df["x"] = (df["x1"] + df["x2"]) / 2
        df["y"] = (df["y1"] + df["y2"]) / 2

        # Drop old coordinate columns
        df = df[["frame_index", "tracker_id", "x", "y"]]

        # Sort dataframe by frame_index
        df = df.sort_values(by="frame_index")

        # Identify master IDs
        master_ids = []
        for tid in df["tracker_id"]:
            if tid not in master_ids:
                master_ids.append(tid)
            if len(master_ids) == 6:
                break

        # Initialize master coordinates storage
        master_coords = {mid: None for mid in master_ids}
        updated_tracker_ids = []

        # Iterate through rows to assign new tracker IDs
        for _, row in df.iterrows():
            current_tid = row["tracker_id"]
            x, y = row["x"], row["y"]

            if current_tid in master_ids:
                master_coords[current_tid] = (x, y)
                updated_tracker_ids.append(current_tid)
            else:
                best_match = None
                min_distance = float('inf')
                for mid, coords in master_coords.items():
                    if coords is None:
                        continue
                    if abs(x - coords[0]) <= 150 and abs(y - coords[1]) <= 150:
                        distance = np.sqrt((x - coords[0])**2 + (y - coords[1])**2)
                        if distance < min_distance:
                            min_distance = distance
                            best_match = mid

                updated_tracker_ids.append(best_match if best_match is not None else current_tid)

        # Ensure tracker IDs are integers
        df["tracker_id"] = [int(num) for num in updated_tracker_ids]

        # Sort by tracker_id and frame_index for final output
        df_sorted = df.sort_values(by=["tracker_id", "frame_index"])

        # Save final processed CSV
        output_path = os.path.join(directory, f"{os.path.splitext(os.path.basename(file_path))[0]}.csv")
        df_sorted.to_csv(output_path, index=False, header=False)

        print(f"CSV '{file_path}' processed successfully with combined logic!")