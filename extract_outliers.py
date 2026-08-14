import subprocess, re, os

repo_dir = r'e:\darfat\work\playground\persib-scouting-wyscout'
result = subprocess.run(['git', 'show', 'HEAD:app.py'], cwd=repo_dir, capture_output=True)
content = result.stdout.decode('utf-8')
lines = content.splitlines(keepends=True)

# Find render_outliers_analysis_page
func_name = 'render_outliers_analysis_page'
start_line = None
for i, line in enumerate(lines):
    if re.match(r'^def\s+' + re.escape(func_name) + r'\s*\(', line):
        start_line = i
        break

if start_line is None:
    print(f"Could not find {func_name}")
    exit(1)

# Find end: next top-level def
end_line = len(lines)
for i, line in enumerate(lines[start_line+1:], start=start_line+1):
    if re.match(r'^def\s+', line) or re.match(r'^class\s+', line):
        end_line = i
        break

func_text = ''.join(lines[start_line:end_line]).rstrip() + '\n'
print(f"Extracted {func_name}: lines {start_line+1}-{end_line} ({end_line-start_line} lines)")

target = os.path.join(repo_dir, 'pages', 'outliers_extracted.py')
with open(target, 'w', encoding='utf-8') as f:
    f.write(func_text)
print(f"Written to {target}")
