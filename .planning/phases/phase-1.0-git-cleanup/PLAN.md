# PLAN.md - Phase 1.0: Git State Cleanup & Data Organization

**Milestone:** v5.1 - Stabilization & Refactoring
**Phase:** 1.0
**Status:** Ready for Execution
**Created:** 2026-02-28

---

## Phase Overview

This phase focuses on cleaning up the git repository state and organizing the data files. The current state shows many deleted files (auxiliary modules removed in v5.0 refactoring) and unorganized data files scattered across multiple directories.

### Current State Analysis

**Git Status Issues:**
- 50+ deleted files (chatbot/, scrapperfc/, scripts/) - needs proper staging
- 2 modified files (settings.local.json, BRI Liga 1 CSV)
- 40+ untracked files in data/ directory
- Many duplicate league files across different data folders

**Data Directory Issues:**
```
data/
├── 2024/                    # Old data
├── 2025/                    # Primary data folder (6 leagues)
├── 2025_searching/          # Temporary/search data?
├── 2025_Strikers_top/       # Temporary search results?
├── 2026_Shortlists/         # Shortlist exports
├── all/                     # Duplicate data?
├── DEPLOY/                  # Deployment data?
├── expired/                 # Expired data
├── lower/                   # Lower tier leagues?
├── Strikers/                # Striker searches?
├── top/                     # Top leagues?
└── top5/                    # Top 5 leagues (duplicate)
```

**Unorganized CSV Files (data/ root):**
- Multiple duplicates (e.g., BRI Liga 1 in both data/ and data/2025/)
- Top 5 European leagues scattered across folders
- South American leagues in multiple locations
- Expired leagues (e.g., MLS 2024)

---

## Phase Goals

1. **Clean git state** - Properly commit all deletions and modifications
2. **Organize data files** - Consolidate all CSVs into structured directories
3. **Archive temporary/obsolete data** - Move search results and expired data to archive
4. **Update data loader** - Ensure it loads from correct directory structure
5. **Document data structure** - Create README for data organization

---

## Success Criteria

- [ ] Clean git status (no deleted file references, all changes staged)
- [ ] All league CSVs organized in `data/2025/` for active data
- [ ] Archived data moved to `data/archive/` with structure
- [ ] All 6 Southeast Asian leagues load successfully
- [ ] Additional leagues (Top 5, South America) organized and accessible
- [ ] Application runs without data loading errors

---

## Implementation Tasks

### Task 1: Stage and Commit All Deletions

**Priority:** High
**Estimated Effort:** 15 minutes
**Dependencies:** None

**Steps:**
1. Stage all deleted files:
   ```bash
   git add -u
   ```
2. Stage modified files:
   ```bash
   git add .claude/settings.local.json
   git add .planning/PROJECT.md
   ```
3. Create commit with descriptive message:
   ```bash
   git commit -m "$(cat <<'EOF'
   Remove auxiliary modules and update project documentation

   - Remove chatbot/ (relocated for future v7.1 milestone)
   - Remove scrapperfc/ (deprecated, using manual CSV exports)
   - Remove scripts/ (consolidated into utils/)
   - Remove app_db.py (replaced with new data loader)
   - Update PROJECT.md with v5.1 milestone information
   - Update Claude Code settings

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
   EOF
   )"
   ```
4. Verify clean status: `git status`

**Acceptance Criteria:**
- Git status shows no deleted file references
- Commit message follows project conventions
- All file deletions documented in commit

---

### Task 2: Analyze and Categorize All Data Files

**Priority:** High
**Estimated Effort:** 30 minutes
**Dependencies:** None

**Steps:**
1. Scan all data directories for CSV files:
   ```python
   import pandas as pd
   import os
   from pathlib import Path

   def scan_data_files(data_root="data"):
       """Scan and categorize all CSV files"""
       categories = {
           "active_2025": [],
           "archive_2024": [],
           "top5": [],
           "south_america": [],
           "asia": [],
           "temporary": [],
           "duplicates": [],
           "unknown": []
       }

       for csv_path in Path(data_root).rglob("*.csv"):
           # Analyze file name and location
           # Add to appropriate category
           pass

       return categories
   ```

2. Identify duplicates by checking file size and name similarity

3. Generate summary report of data organization

**Acceptance Criteria:**
- All CSV files categorized
- Duplicates identified with file paths
- Summary report generated in `.planning/data_inventory.md`

---

### Task 3: Organize Data Directory Structure

**Priority:** High
**Estimated Effort:** 45 minutes
**Dependencies:** Task 2

**Target Structure:**
```
data/
├── 2025/                       # Active league data (primary)
│   ├── Southeast Asia/
│   │   ├── BRI Liga 1 25-26.csv
│   │   ├── Thai League 1 25-26.csv
│   │   ├── Malaysian Super League 25-26.csv
│   │   ├── Singapore Premier League 25-26.csv
│   │   ├── Cambodian Premier League 25-26.csv
│   │   └── V.League 1 25-26.csv
│   ├── Top 5 Europe/
│   │   ├── Premier League 25-26.csv
│   │   ├── La Liga 25-26.csv
│   │   ├── Serie A 25-26.csv
│   │   ├── Bundesliga 25-26.csv
│   │   └── Ligue 1 25-26.csv
│   ├── South America/
│   │   ├── Brasileirao 2025.csv
│   │   └── Argentina LPF 2025.csv
│   └── Other/
│       ├── MLS 2025.csv
│       ├── Saudi Pro League 24-25.csv
│       └── ... (other leagues)
├── archive/                    # Historical data
│   ├── 2024/
│   ├── 2023/
│   └── expired/
│       ├── MLS 2024.csv
│       ├── Uzbek Super League 2025.csv (no longer tracked)
│       └── ...
├── exports/                    # Generated exports and reports
│   ├── shortlists/
│   ├── comparisons/
│   └── analyses/
└── search_results/             # Temporary search results
    └── (auto-generated, can be .gitignored)
```

**Steps:**
1. Create new directory structure
2. Move files to appropriate locations:
   - Active 2025 leagues → `data/2025/` with subfolders
   - 2024 data → `data/archive/2024/`
   - Expired/untracked leagues → `data/archive/expired/`
   - Shortlist exports → `data/exports/shortlists/`
   - Search results → `data/search_results/`
3. Remove duplicate files
4. Clean up empty directories

**Acceptance Criteria:**
- All active leagues in `data/2025/`
- Archived data in `data/archive/`
- No duplicate files
- Empty directories removed
- `.gitignore` updated to ignore `data/search_results/`

---

### Task 4: Update Data Loader for New Structure

**Priority:** High
**Estimated Effort:** 30 minutes
**Dependencies:** Task 3

**File:** `utils/data_loader.py`

**Changes Needed:**

1. Update `load_all_league_data()` to handle subdirectories:
```python
def load_all_league_data(folder="data/2025/", subfolders=None):
    """
    Load all CSV files from specified folder and optional subfolders.

    Args:
        folder: Root data folder (default: "data/2025/")
        subfolders: List of subfolder paths to include (default: None = all)
                   Example: ["Southeast Asia", "Top 5 Europe"]

    Returns:
        Combined DataFrame with all leagues
    """
    dfs = []
    data_path = Path(folder)

    if subfolders is None:
        # Load all CSVs from root and subdirectories
        csv_files = list(data_path.rglob("*.csv"))
    else:
        # Load only from specified subfolders
        csv_files = []
        for subfolder in subfolders:
            csv_files.extend((data_path / subfolder).glob("*.csv"))

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            # ... existing loading logic ...
        except Exception as e:
            st.warning(f"Failed to load {csv_file.name}: {e}")

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
```

2. Update distinct values extraction to handle subdirectories

3. Add documentation for new structure

**Acceptance Criteria:**
- Data loader loads from `data/2025/` including subdirectories
- All 6 Southeast Asian leagues load successfully
- Additional leagues (Top 5, South America) accessible
- No errors during data loading
- Function documented with docstring

---

### Task 5: Update .gitignore for Data Directory

**Priority:** Medium
**Estimated Effort:** 10 minutes
**Dependencies:** Task 3

**File:** `.gitignore`

**Additions:**
```gitignore
# Data organization
data/archive/
data/exports/
data/search_results/
data/*.csv  # Ignore root-level CSVs, keep organized ones
```

**Rationale:**
- Archive data: Historical data not needed in version control
- Exports: Generated reports and shortlists
- Search results: Temporary auto-generated files
- Root CSVs: Force organization into proper subdirectories

**Acceptance Criteria:**
- `.gitignore` updated with data exclusions
- Historical/archived data excluded from git
- Exports and search results excluded
- Active league data in `data/2025/` still tracked

---

### Task 6: Test Data Loading After Reorganization

**Priority:** High
**Estimated Effort:** 20 minutes
**Dependencies:** Task 4

**Steps:**
1. Create test script to verify data loading:
```python
# test_data_loading.py
import sys
from utils.data_loader import load_all_league_data, get_distinct_values

def test_data_loading():
    print("Testing data loading...")

    # Load all data
    df = load_all_league_data("data/2025/")
    print(f"Total players: {len(df)}")

    # Get distinct values
    leagues, positions = get_distinct_values(df)
    print(f"Leagues found: {len(leagues)}")
    print(f"Leagues: {leagues}")
    print(f"Positions: {positions}")

    # Verify Southeast Asian leagues
    expected_leagues = [
        "BRI Liga 1 25-26",
        "Thai League 1 25-26",
        "Malaysian Super League 25-26",
        "Singapore Premier League 25-26",
        "Cambodian Premier League 25-26",
        "V.League 1 25-26"
    ]

    missing = [league for league in expected_leagues if league not in leagues]
    if missing:
        print(f"❌ Missing leagues: {missing}")
        return False
    else:
        print(f"✅ All Southeast Asian leagues loaded")
        return True

if __name__ == "__main__":
    success = test_data_loading()
    sys.exit(0 if success else 1)
```

2. Run test and verify output:
```bash
python test_data_loading.py
```

3. Test Streamlit app:
```bash
streamlit run app.py
```

4. Verify all 8 pages load without errors

**Acceptance Criteria:**
- All 6 Southeast Asian leagues load successfully
- Total player count > 0
- All 8 pages render without errors
- No data loading warnings

---

### Task 7: Create Data Directory README

**Priority:** Medium
**Estimated Effort:** 15 minutes
**Dependencies:** Task 3, Task 6

**File:** `data/README.md`

**Content:**
```markdown
# Data Directory Structure

## Directory Layout

```
data/
├── 2025/                    # Active league data (current season)
│   ├── Southeast Asia/       # Southeast Asian leagues
│   ├── Top 5 Europe/        # European top 5 leagues
│   ├── South America/      # South American leagues
│   └── Other/              # Other tracked leagues
├── archive/                 # Historical data (not tracked in git)
├── exports/                 # Generated reports (not tracked in git)
└── search_results/          # Temporary search results (not tracked)
```

## Active Leagues (2025 Season)

### Southeast Asia
- BRI Liga 1 25-26
- Thai League 1 25-26
- Malaysian Super League 25-26
- Singapore Premier League 25-26
- Cambodian Premier League 25-26
- V.League 1 25-26

### Top 5 Europe
- Premier League 25-26
- La Liga 25-26
- Serie A 25-26
- Bundesliga 25-26
- Ligue 1 25-26

### South America
- Brasileirao 2025
- Argentina LPF 2025

## Data Loading

The `utils/data_loader.py` module loads all CSV files from `data/2025/` including subdirectories.

## Adding New Data

To add a new league:
1. Export CSV from Wyscout with required columns
2. Place in appropriate `data/2025/` subfolder
3. Restart the Streamlit app

## Data Format

- Encoding: UTF-8 BOM (`utf-8-sig`)
- Required columns: Player, Age, Team, Position, Competition, Minutes played
- Statistics: All columns defined in `config/stat_categories.py`

## Archive Policy

- Previous season data → `data/archive/YYYY/`
- Expired/untracked leagues → `data/archive/expired/`
- Archive is not tracked in git (see .gitignore)
```

**Acceptance Criteria:**
- README created at `data/README.md`
- Directory structure documented
- Active leagues listed
- Instructions for adding new data included
- Archive policy explained

---

### Task 8: Commit Reorganization Changes

**Priority:** High
**Estimated Effort:** 10 minutes
**Dependencies:** Task 3, Task 4, Task 5, Task 6, Task 7

**Steps:**
1. Stage all new and modified files:
```bash
# Stage data reorganization
git add data/
git add utils/data_loader.py
git add data/README.md

# Update .gitignore
git add .gitignore

# Add data inventory report
git add .planning/data_inventory.md
```

2. Create commit:
```bash
git commit -m "$(cat <<'EOF'
Organize data directory structure and update data loader

- Restructure data/ with clear separation of active/archive/exports
- Consolidate Southeast Asian leagues into data/2025/Southeast Asia/
- Organize Top 5 Europe leagues into dedicated subfolder
- Update data_loader.py to handle subdirectory structure
- Add data/README.md with directory layout and usage instructions
- Update .gitignore to exclude archives and generated files
- Create .planning/data_inventory.md with full data catalog

All 6 Southeast Asian leagues verified loading successfully.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

3. Verify final git status is clean:
```bash
git status
```

**Acceptance Criteria:**
- Clean git status (no uncommitted changes)
- All reorganization changes committed
- Commit message describes changes clearly
- Data inventory documented

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Data loss during file moves | Low | High | Backup entire `data/` before moving; verify file counts |
| Application breaks after reorganization | Medium | Medium | Test thoroughly before committing; keep backup |
| Git merge conflicts on data reorganization | Low | Low | Work on clean branch; coordinate with team |
| Missing league data after move | Low | Medium | Compare file counts before/after; validate with test script |

---

## Dependencies

- **None** - This is the first phase of Milestone 1

---

## Next Phases

After completion of this phase:
- **Phase 1.1:** Data Validation - Test all league CSVs for proper loading and data quality
- **Phase 1.2:** Error Handling Improvements - Add user-friendly error messages
- **Phase 1.3:** Performance Optimization - Profile and optimize data loading pipeline

---

## Verification Plan

### Pre-Execution Checklist
- [ ] Current code backed up (git branch: cleanup-phase-1.0)
- [ ] Data directory backed up (manual copy to data_backup/)
- [ ] Test script prepared

### Post-Execution Checklist
- [ ] All tasks completed
- [ ] Git status clean
- [ ] Data loader tested with all 6 SE Asian leagues
- [ ] Streamlit app loads all 8 pages
- [ ] Data README created
- [ ] .gitignore updated

### Sign-Off Criteria
- [ ] All acceptance criteria met
- [ ] No errors in application logs
- [ ] Data organization documented
- [ ] Team reviewed and approved

---

**Total Estimated Effort:** ~3 hours

**Phase Completion Target:** 2026-02-28
