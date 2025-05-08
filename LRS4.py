import os
import csv
import pandas as pd
from collections import OrderedDict
import border_patrol

# Define input and output folder paths
input_folder = "output_csvs"
output_folder = "lrs_csvs"

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# -------------------------------
# Tracker Label Assignment
# -------------------------------

import pandas as pd
from collections import OrderedDict

def assign_positions(csv_filename, Video_Widths, VideoNum):
    # Load CSV into DataFrame
    df = pd.read_csv(csv_filename, header=None, names=['frame', 'tracker_id', 'x', 'y'])

    # Convert columns to numeric, coercing errors to NaN
    df = df.apply(pd.to_numeric, errors='coerce')

    # Drop any rows with missing values
    df.dropna(inplace=True)

    # Extract unique tracker positions (first occurrence)
    tracker_positions = df.groupby('tracker_id')[['x', 'y']].first().to_dict(orient='index')

    left_side, right_side = [], []

    # Assign trackers to left or right side based on video width
    for tracker_id, pos in tracker_positions.items():
        x, y = pos['x'], pos['y']
        if x > (Video_Widths[VideoNum] / 2):
            right_side.append((tracker_id, y))
        else:
            left_side.append((tracker_id, y))

    VideoNum += 1  # Move to next video

    # Sort positions by y-value (descending)
    right_side.sort(key=lambda item: item[1], reverse=True)
    left_side.sort(key=lambda item: item[1], reverse=True)

    # Assign labels
    labeled_positions = {tracker_id: f'R{i+1}' for i, (tracker_id, _) in enumerate(right_side)}
    labeled_positions.update({tracker_id: f'B{i+1}' for i, (tracker_id, _) in enumerate(left_side)})

    return labeled_positions


# -------------------------------
# Zone Definition and Helper
# -------------------------------
zones = {
    1: (458, 225, 624, 331),
    2: (862, 435, 945, 586),
    3: (331, 412, 622, 586),
    4: (139, 336, 309, 437),
    5: (973, 346, 1124, 473),
    6: (1165, 624, 1536, 655),
    7: (1291, 389, 1584, 548),
    8: (1705, 548, 1854, 652),
    9: (13, 200, 958, 660),
    10: (958, 202, 1907, 657),
}

#Red CCRA - Blue CCRA - All Red - All Blue
# 1: Red Coral Station
# 2: Red Coral Station
# 3: Red Reef
# 4: Red Processor
# 5: Blue Coral Station
# 6: Blue Coral Station
# 7: Blue Reef
# 8: Blue Processor
# 9: Red General
# 10: Blue General
def is_in_zone(x, y, zone_box):
    x_min, y_min, x_max, y_max = zone_box
    return x_min <= x <= x_max and y_min <= y <= y_max

# -------------------------------
# Process all CSV files in input folder
# -------------------------------
def run(Video_Widths):
    VideoNum = 0
    for filename in os.listdir(input_folder):
        if filename.endswith(".csv"):
            input_filepath = os.path.join(input_folder, filename)
            border_patrol.run(input_filepath)
            output_filename = f"{os.path.splitext(filename)[0]}_LRSed.csv"
            output_filepath = os.path.join(output_folder, output_filename)

            tracker_zones = {}
            df = pd.read_csv(input_filepath, header=None)
            df.dropna(inplace=True)  # Removes rows with missing values
            df = df.astype({0: int, 1: int, 2: float, 3: float})  # Ensures correct types
            data = list(df.itertuples(index=False, name=None))


            data.sort(key=lambda row: row[0])

            for frame_index, tracker_id, x, y in data:
                current_zone = None
                for zone_id, zone_box in zones.items():
                    if is_in_zone(x, y, zone_box):
                        current_zone = zone_id
                        break
                if current_zone is not None:
                    if tracker_id not in tracker_zones:
                        tracker_zones[tracker_id] = []
                    if not tracker_zones[tracker_id] or tracker_zones[tracker_id][-1] != current_zone:
                        tracker_zones[tracker_id].append(current_zone)

            tracker_labels = assign_positions(input_filepath, Video_Widths, VideoNum)
            VideoNum += 1
            
            results = []
            for tracker_id, zone_list in tracker_zones.items():
                starter = True
                new_zone_list = []
                algaeHeld, coralHeld = False, False
                defense_flag = False
                frame_counters = {}

                for i in range(len(zone_list)):
                    zone = zone_list[i]

                    # Team assignment
                    if starter and zone in [1, 2, 3, 4, 9]:  
                        new_zone_list.append('RS')
                        team = 'RS'
                        starter = False
                    elif starter and zone in [5, 6, 7, 8, 10]:  
                        new_zone_list.append('BS')
                        team = 'BS'
                        starter = False

                    # Increment frame counter
                    frame_counters[zone] = frame_counters.get(zone, 0) + 1

                    # Ensure action only occurs if in zone for 5+ frames
                    if frame_counters[zone] >= 5:
                        if zone in [1, 2] and team == 'RS':  
                            new_zone_list.append('CoralPickup')
                            coralHeld = True
                        elif zone in [5, 6] and team == 'BS':  
                            new_zone_list.append('CoralPickup')
                            coralHeld = True

                        if zone == 3 and team == 'RS':  
                            if coralHeld:
                                new_zone_list.append('CoralScore')
                                coralHeld = False
                            elif not algaeHeld:
                                algaeHeld = True
                        elif zone == 7 and team == 'BS':  
                            if coralHeld:
                                new_zone_list.append('CoralScore')
                                coralHeld = False
                            elif not algaeHeld:
                                algaeHeld = True

                        if zone == 4 and team == 'RS' and algaeHeld:  
                            new_zone_list.append('AlgaeScore')
                            algaeHeld = False
                        elif zone == 8 and team == 'BS' and algaeHeld:  
                            new_zone_list.append('AlgaeScore')
                            algaeHeld = False

                    # Defense detection
                    opposing_zones = [5, 6, 7, 8, 10] if team == 'RS' else [1, 2, 3, 4, 9]
                    if zone in opposing_zones and not defense_flag:
                        new_zone_list.append('D')
                        defense_flag = True

                # **🔥 Append final results**
                if tracker_id in tracker_labels:
                    CoralTotal = new_zone_list.count("CoralScore")
                    AlgaeTotal = new_zone_list.count("AlgaeScore")

                    results.append({
                        'id': tracker_labels[tracker_id],
                        'algae': AlgaeTotal,
                        'coral': CoralTotal
                    })


            # **Ensure Sorting Works**
            def sort_key(item):
                label = item['id']
                side = label[0]
                number = int(label[1:])
                return (0 if side == 'R' else 1, number)
            
            # Sort results by ID label
            results.sort(key=sort_key)

            # Write clean CSV
            if results:
                output_df = pd.DataFrame(results)
                output_df.to_csv(output_filepath, columns=["id", "algae", "coral"], index=False, header=False)

                print(f"✅ Processed {filename} -> {output_filename}")
            else:
                print(f"⚠️ No valid data to write for {filename}")