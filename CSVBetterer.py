import pandas as pd
def run():
    # Define the file path
    file_path = "data.csv"

    # Define column names manually since the CSV has no headers
    column_names = ["frame_index", "tracker_id", "x1", "x2", "y1", "y2"]

    # Read the CSV without headers and ensure data is treated as numeric
    df = pd.read_csv(file_path, names=column_names, dtype={"frame_index": int, "tracker_id": int, "x1": float, "x2": float, "y1": float, "y2": float})

    # Compute the average coordinates
    df["x_avg"] = (df["x1"] + df["x2"]) / 2
    df["y_avg"] = (df["y1"] + df["y2"]) / 2

    # Keep only the required columns, replacing x1, x2, y1, y2 with x_avg and y_avg
    df = df[["frame_index", "tracker_id", "x_avg", "y_avg"]]

    # Sort the DataFrame by tracker_id before saving
    df_sorted = df.sort_values(by=["tracker_id","frame_index"])
    
    # Write the sorted data back to the original file **without headers**
    df_sorted.to_csv(file_path, index=False, header=False)


    print("CSV updated successfully with averages!")
