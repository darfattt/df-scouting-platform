import pandas as pd
import sys
import os

# Define the paths
csv_path = r'e:\darfat\work\playground\persib-scouting-wyscout\data\2025\indonesia\BRI Liga 1 25-26.csv'
config_path = r'e:\darfat\work\playground\persib-scouting-wyscout\config\stat_categories.py'

# Load CSV columns
try:
    df = pd.read_csv(csv_path, nrows=0, encoding='utf-8-sig')
    csv_columns = set(df.columns)
except Exception as e:
    print(f"Error reading CSV: {e}")
    sys.exit(1)

# Load config metrics
config_metrics = set()
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want STAT_CATEGORIES and PLAYER_INFO_COLUMNS
    namespace = {}
    # Mocking necessary things for exec if needed, but here it's simple dicts
    exec(content, namespace)
    
    stat_categories = namespace.get('STAT_CATEGORIES', {})
    for cat in stat_categories.values():
        for stat in cat.get('stats', []):
            config_metrics.add(stat['column'])
            
    player_info = namespace.get('PLAYER_INFO_COLUMNS', {})
    for col in player_info.values():
        config_metrics.add(col)
except Exception as e:
    print(f"Error reading config: {e}")
    sys.exit(1)

# Compare
missing_in_config = csv_columns - config_metrics

# Known non-metric columns to exclude (player info not in PLAYER_INFO_COLUMNS)
exclude = {
    'Full name', 'Wyscout id', 'Team within selected timeframe', 'Team logo', 
    'Contract expires', 'Passport country', 'On loan', 'Foot', 'Birth country'
}

# The user might have already included some in PLAYER_INFO_COLUMNS
# Birth country is in PLAYER_INFO_COLUMNS as "Birth country"

final_missing = sorted([col for col in missing_in_config if col not in exclude])

print("Missing metrics in config/stat_categories.py:")
for col in final_missing:
    print(f"{col}")
