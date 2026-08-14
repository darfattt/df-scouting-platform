import subprocess
import os

repo_dir = r'e:\darfat\work\playground\persib-scouting-wyscout'

def get_old_content():
    result = subprocess.run(['git', 'show', 'HEAD:app.py'], cwd=repo_dir, capture_output=True)
    try:
        # Try different encodings
        return result.stdout.decode('utf-16le', errors='ignore')
    except:
        return result.stdout.decode('utf-8', errors='ignore')

content = get_old_content()
if not content:
    print("Could not get content.")
    exit(1)

lines = content.splitlines(keepends=True)

functions_to_extract = [
    'display_similarity_results_table',
    'display_similarity_scatter_plot',
    'display_similarity_scatter_plot_composite',
    'display_similarity_player_detail'
]

extracted_functions = {}

for func_name in functions_to_extract:
    start_line = -1
    for i, line in enumerate(lines):
        if line.startswith(f'def {func_name}'):
            start_line = i
            break
    
    if start_line != -1:
        # Find end of function (based on indentation)
        end_line = start_line + 1
        while end_line < len(lines):
            line = lines[end_line]
            if line.strip() != '' and not line.startswith(' ') and not line.startswith('\t'):
                break
            end_line += 1
        extracted_functions[func_name] = ''.join(lines[start_line:end_line])

target_file = os.path.join(repo_dir, 'pages', 'similarity_views.py')
with open(target_file, 'w', encoding='utf-8') as f:
    f.write('import streamlit as st\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport plotly.express as px\nimport plotly.graph_objects as go\nimport altair as alt\n\n')
    for func_content in extracted_functions.values():
        f.write(func_content)
        f.write('\n\n')

print(f"Extracted {len(extracted_functions)} functions to {target_file}.")
