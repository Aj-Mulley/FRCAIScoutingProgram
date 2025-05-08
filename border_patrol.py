import pandas as pd

def run(csv_path):
    # Read CSV with no headers
    df = pd.read_csv(csv_path, header=None)

    # The second column (index 1) contains the team numbers
    unique_teams = []
    team_map = {}

    for team in df[1]:
        if team not in unique_teams:
            if len(unique_teams) < 6:
                unique_teams.append(team)
            else:
                if team not in team_map:
                    print(f"Found new Team_num: {team}")
                    print(f"Existing valid team numbers: {unique_teams}")
                    while True:
                        replacement = input(f"Enter a replacement Team_num for {team}: ")
                        try:
                            replacement = int(replacement)
                            if replacement in unique_teams:
                                team_map[team] = replacement
                                break
                            else:
                                print("Please enter a valid number from the existing list.")
                        except ValueError:
                            print("Please enter a valid integer.")

    # Apply the replacements
    df[1] = df[1].apply(lambda t: team_map[t] if t in team_map else t)

    # Save CSV with no header and no index
    df.to_csv(csv_path, index=False, header=False)
    print(f"Updated CSV saved to {csv_path}")
