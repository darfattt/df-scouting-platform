import subprocess, re, os

repo_dir = r'e:\darfat\work\playground\persib-scouting-wyscout'
result = subprocess.run(['git', 'show', 'HEAD:app.py'], cwd=repo_dir, capture_output=True)

# Try multiple encodings
content = None
for enc in ['utf-8', 'utf-16le', 'utf-16', 'cp1252', 'latin-1']:
    try:
        decoded = result.stdout.decode(enc)
        if 'def main' in decoded or 'def sanitize_key' in decoded:
            content = decoded
            print(f"Decoded with: {enc}")
            break
    except:
        continue

if not content:
    print("Could not decode")
    exit(1)

lines = content.splitlines()

# Find the outliers section - search for "Outliers Analysis" in the original main()
outlier_start = None
for i, line in enumerate(lines):
    if 'Outliers Analysis' in line and 'header' in line:
        outlier_start = i
        print(f"Found outlier header at line {i+1}: {line.strip()}")

# Also find where the outlier page rendering starts and ends in the original code
# Look for the section that handles the outliers rendering
for i, line in enumerate(lines):
    if 'outlier' in line.lower() and ('render' in line.lower() or 'detect' in line.lower() or 'display' in line.lower()):
        print(f"  Line {i+1}: {line.strip()[:100]}")

# Find the render_outliers function if there is one
for i, line in enumerate(lines):
    if re.match(r'^\s+elif.*Outliers', line):
        print(f"  Routing at line {i+1}: {line.strip()[:100]}")
    if 'render_outliers' in line:
        print(f"  render_outliers at line {i+1}: {line.strip()[:100]}")
