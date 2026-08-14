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
df = load_player_data(csv_path)
csv_columns = list(df.columns)

# Load config metrics
config_metrics = set()
for cat in STAT_CATEGORIES.values():
    for stat in cat.get('stats', []):
        config_metrics.add(stat['column'])
        
for col in PLAYER_INFO_COLUMNS.values():
    config_metrics.add(col)

# Compare
missing_in_config = [col for col in csv_columns if col not in config_metrics]

# Known non-metric columns to exclude
exclude = {
    'Full name', 'Wyscout id', 'Team within selected timeframe', 'Team logo', 
    'Contract expires', 'Passport country', 'On loan', 'Foot'
}

final_missing = sorted([col for col in missing_in_config if col not in exclude])

results = []
results.append("Verification Results:")
results.append("---------------------")
results.append(f"Goals in config: {'Goals' in config_metrics}")
results.append(f"Aerial duels per 90.1 in CSV: {'Aerial duels per 90.1' in csv_columns}")
results.append("\nRemaining missing metrics:")
for col in final_missing:
    results.append(f"- {col}")

with open('verification_results.txt', 'w') as f:
    f.write('\n'.join(results))
