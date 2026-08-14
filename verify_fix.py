import pandas as pd
import sys
import os
import re

# Add current directory to path so we can import utils
sys.path.append(os.getcwd())

from utils.data_loader import load_player_data
from config.stat_categories import STAT_CATEGORIES, PLAYER_INFO_COLUMNS

# Define the paths
csv_path = r'e:\darfat\work\playground\persib-scouting-wyscout\data\2025\indonesia\BRI Liga 1 25-26.csv'

# Load CSV using our NEW load_player_data (which should deduplicate)
try:
    df = load_player_data(csv_path)
    csv_columns = set(df.columns)
except Exception as e:
    print(f"Error reading CSV: {e}")
    sys.exit(1)

# Load config metrics
config_metrics = set()
for cat in STAT_CATEGORIES.values():
    for stat in cat.get('stats', []):
        config_metrics.add(stat['column'])
        
for col in PLAYER_INFO_COLUMNS.values():
    config_metrics.add(col)

# Compare
missing_in_config = csv_columns - config_metrics

# Known non-metric columns to exclude
exclude = {
    'Full name', 'Wyscout id', 'Team within selected timeframe', 'Team logo', 
    'Contract expires', 'Passport country', 'On loan', 'Foot'
}

final_missing = sorted([col for col in missing_in_config if col not in exclude])

print("Missing metrics in config/stat_categories.py (after fix):")
for col in final_missing:
    print(f"{col}")

# Specifically check if Goals is missing (it shouldn't be)
if "Goals" in final_missing:
    print("FAILED: Goals is still missing!")
else:
    print("SUCCESS: Goals is no longer missing.")

# Specifically check if Aerial duels per 90.1 is present (it shouldn't be)
if "Aerial duels per 90.1" in csv_columns:
    print("FAILED: Aerial duels per 90.1 is still present in deduplicated columns!")
else:
    print("SUCCESS: Aerial duels per 90.1 has been deduplicated.")
