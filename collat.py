import os
import re
import requests
import pandas as pd

# Firebase database URL
FIREBASE_URL = "https://aiscout-7bec2-default-rtdb.firebaseio.com/matchesList.json"

# Folder paths
INPUT_FOLDER = "lrs_csvs"
OUTPUT_FOLDER = "collat_csvs"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def extract_match_number(filename):
    """Extract the match number from the filename (assumes number before underscore)."""
    match = re.match(r"(\d+)_", filename)
    return int(match.group(1)) if match else None

def process_csv(csv_path, match_data):
    """Process a single CSV file by updating values based on Firebase match data."""
    df = pd.read_csv(csv_path, header=None, names=["Position", "Coral Cycles", "Algae Cycles"])

    position_map = {
        "R1": ("numeric1", "comment1"),
        "R2": ("numeric2", "comment2"),
        "R3": ("numeric3", "comment3"),
        "B1": ("numeric4", "comment4"),
        "B2": ("numeric5", "comment5"),
        "B3": ("numeric6", "comment6"),
    }

    # Update the dataframe with Firebase match data
    for position, (numeric_key, comment_key) in position_map.items():
        mask = df["Position"] == position
        if numeric_key in match_data:
            df.loc[mask, "Position"] = match_data[numeric_key]  # Replace position with numeric value
        if comment_key in match_data:
            df.loc[mask, "Comment"] = match_data[comment_key]  # Append comment in a new column

    return df

def run():
    """Main function to process all CSV files in the folder."""
    # Fetch match data from Firebase
    response = requests.get(FIREBASE_URL)
    if response.status_code != 200:
        print("Failed to fetch data from Firebase")
        return

    matches_list = response.json()
    if not matches_list:
        print("No match data found in Firebase.")
        return

    print(f"Fetched {len(matches_list)} matches from Firebase.")

    # Process each CSV in the input folder
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".csv"):
            csv_path = os.path.join(INPUT_FOLDER, filename)
            match_number = extract_match_number(filename)

            if match_number is None:
                print(f"Skipping {filename}: Unable to determine match number.")
                continue

            # Find the matching entry in Firebase
            match_data = next((data for data in matches_list.values() if data.get("matchNumber") == match_number), None)

            if match_data is None:
                print(f"No Firebase entry found for match {match_number} in {filename}. Skipping...")
                continue

            print(f"Processing {filename} for match {match_number}...")

            # Process the CSV and save the output
            updated_df = process_csv(csv_path, match_data)
            output_filename = f"{os.path.splitext(filename)[0]}_collated.csv"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            updated_df.to_csv(output_path, index=False, header=False)
            print(f"Saved: {output_path}")

run()
all_data = []

# Loop through all files in the folder
for file in os.listdir(OUTPUT_FOLDER):
    if file.endswith('.csv'):  # Check if the file is a CSV
        file_path = os.path.join(OUTPUT_FOLDER, file)
        # Read the CSV file into a DataFrame and append to the list
        df = pd.read_csv(file_path)
        all_data.append(df)

# Concatenate all DataFrames into a single DataFrame
combined_df = pd.concat(all_data, ignore_index=True)

# Save the combined DataFrame to a new CSV file
combined_df.to_csv('combined_output.csv', index=False)

print("CSV files successfully combined into 'combined_output.csv'")