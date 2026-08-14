import subprocess
import os
import re

repo_dir = r'e:\darfat\work\playground\persib-scouting-wyscout'

def get_old_content():
    result = subprocess.run(['git', 'show', 'HEAD:app.py'], cwd=repo_dir, capture_output=True)
    # Try different encodings
    for enc in ['utf-16le', 'utf-8', 'cp1252']:
        try:
            return result.stdout.decode(enc)
        except:
            continue
    return None

content = get_old_content()
if not content:
    print("Could not decode content.")
    exit(1)

lines = content.splitlines()
all_funcs = [line[4:].split('(')[0] for line in lines if line.startswith('def ')]

print(f"Total functions found: {len(all_funcs)}")
print("Sample functions:", all_funcs[:20])

# Match similarity functions with fuzzy search
similarity_funcs = [f for f in all_funcs if 'similarity' in f.lower()]
print("Similarity functions found:", similarity_funcs)
