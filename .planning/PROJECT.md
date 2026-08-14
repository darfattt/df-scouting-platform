# PROJECT.md - Darfat Scouting Hub

## Project Overview

**Darfat Scouting Hub** is a sophisticated Streamlit-based football player scouting platform for analyzing players from various leagues using Wyscout data. The application provides professional scouting tools with advanced statistical analysis, composite attribute calculations, and role-based player evaluation.

## Version History

| Version | Status | Release Date | Description |
|---------|--------|--------------|-------------|
| v5.1 | Current | 2026-03 | **Milestone 1: Stabilization & Refactoring** - Git cleanup, data validation, performance optimization |
| v5.0 | Archived | 2026-02 | Production-ready core application on `feature/app-v5` |
| v4.0 | Archived | 2025-12 | Previous version with chatbot and scraper modules |
| v3.0 | Archived | 2025-10 | Initial multi-page scouting application |

**Current Branch:** `feature/app-v5` → transitioning to `main` after v5.1 completion
**Current Milestone:** Milestone 1 - Stabilization & Refactoring (v5.1)

---

## Key Features

### 8-Page Application Architecture

1. **Player Comparison** - Side-by-side analysis of 2-3 players with detailed statistics and composite attributes
2. **Player Finder** - Role-based and responsibility-based player search with tactical preset profiles
3. **Player Similarity** - Find similar players using weighted cosine similarity across multiple metrics
4. **Scatter Analysis** - Interactive scatter plots for exploring relationships between two metrics
5. **Outliers Analysis** - Statistical outlier detection to identify exceptional performers using Z-score and IQR methods
6. **K-Means Clustering** - Identify player archetypes within position groups using unsupervised learning
7. **League Fit** - Analyze player physical compatibility with target league (BRI Liga 1) using 11 physical proxy metrics
8. **Regression Analysis** - Statistical modeling to understand relationships between player statistics

### Supported Position Groups
- CB (Center Back)
- Fullback (LB, RB, LWB, RWB)
- DM (Defensive Midfielder)
- CM (Central Midfielder)
- AM (Attacking Midfielder)
- Winger (LW, RW)
- Forward/Striker (CF)

**Total:** 60+ composite attributes calculated from 100+ statistical metrics

---

## Technical Architecture

### Technology Stack

**Core Framework:**
- Streamlit 1.31.0 - Web UI framework
- Pandas 2.2.0 - Data manipulation and analysis
- NumPy 1.26.3 - Numerical computing
- Matplotlib 3.8.2 - Static visualizations
- Plotly 5.18.0 - Interactive charts

**Machine Learning & Statistics:**
- Scikit-learn 1.4.0 - Cosine similarity, K-means clustering
- SciPy 1.11.0 - Statistical calculations
- Statsmodels 0.14.0 - Regression analysis (OLS, Poisson)
- Altair 5.0.0 - Declarative visualizations
- Seaborn 0.13.0 - Statistical plots

**AI/ML Extensions:**
- Ollama 0.6.1 - Local LLM integration (planned chatbot)
- ChromaDB 0.4.0 - Vector database (planned RAG)
- FuzzyWuzzy 0.18.0 - String matching

**Data Integration:**
- Supabase 2.0.0 - Database integration
- Psycopg2-binary 2.9.9 - PostgreSQL adapter
- Requests 2.31.0 - API client
- Pillow 10.0.0 - Image processing (team logos)

### Project Structure

```
persib-scouting-wyscout/
├── app.py (5,623 lines)           # Main 8-page Streamlit application
├── team_analysis_app.py           # Separate team analysis module
│
├── config/                        # Configuration modules (declarative)
│   ├── stat_categories.py         # 6 stat categories, 100+ metrics
│   ├── composite_attributes.py    # 60+ composite attribute formulas
│   ├── grade_attributes.py        # Grade attribute definitions
│   ├── position_groups.py         # Position mapping and filtering
│   ├── position_rankings.py       # Position-specific attribute priorities
│   ├── role_definitions.py        # Role definition registry
│   ├── league_fit_config.py       # Target league + physical proxy metrics
│   ├── team_analysis_config.py    # Team analysis configuration
│   │
│   ├── defender_presets.py        # CB, Fullback role profiles
│   ├── fullback_presets.py       # Fullback role profiles
│   ├── midfielder_presets.py     # DM, CM role profiles
│   ├── attacking_midfielder_presets.py  # AM role profiles
│   ├── forward_presets.py         # Winger, Forward, Striker role profiles
│   ├── similarity_presets.py      # Similarity matching presets
│   └── registry.py               # Central configuration registry
│
├── utils/                         # Utility modules (business logic)
│   ├── data_loader.py             # Core data pipeline (18KB)
│   ├── column_mapping.py          # CSV compatibility layer
│   ├── player_comparison.py       # Page 1 visualizations (64KB)
│   ├── player_finder.py            # Page 2 search logic (33KB)
│   ├── player_similarity.py       # Page 3 similarity scoring (33KB)
│   ├── similarity_helpers.py      # Similarity helper functions
│   ├── outlier_detection.py       # Page 5 statistics (13KB)
│   ├── regression_analysis.py     # Page 8 regression models (15KB)
│   ├── league_fit.py               # Page 7 league compatibility (20KB)
│   │
│   ├── team_data_loader.py        # Team data loading
│   ├── team_aggregator.py         # Team-level aggregation
│   ├── team_styles.py             # Team playing style analysis
│   └── team_visualizations.py     # Team visualization functions
│
└── data/
    └── 2025/                      # Wyscout CSV exports
        ├── BRI Liga 1 25-26.csv
        ├── Thai League 1 25-26.csv
        ├── Malaysian Super League 25-26.csv
        ├── Singapore Premier League 25-26.csv
        ├── Cambodian Premier League 25-26.csv
        └── V.League 1 25-26.csv
```

### Data Processing Pipeline

```
load_all_data() [cached once, no parameters]
    ↓ (loads raw CSV files from data/2025/)
get_distinct_values() [extract unique leagues/positions]
    ↓
prepare_filtered_data() [cached by: position_group + leagues_tuple]
    ├── Filter by position group and selected leagues
    ├── Calculate percentiles on filtered subset (0-100 scale)
    └── Calculate composite attributes (batch processing)
        ↓
render_page() [with page-specific filters: age, minutes, contract]
```

**Key Insight:** Percentiles are recalculated whenever global filters (position group or leagues) change, ensuring fair comparison within the filtered dataset.

### Configuration System

The application uses a modular configuration system to separate data definitions from business logic:

#### Stat Categories (config/stat_categories.py)
- **Defensive:** Tackles, interceptions, duels, defensive actions
- **Offensive:** Goals, shots, xG, box entries, dribbles
- **Progressive:** Progressive passes/runs/carries, deep progressions
- **Chance Creation:** Assists, xA, key passes, crosses, smart passes
- **General:** Passes, pass accuracy, ball touches, aerial duels
- **Set Pieces:** Corners, free kicks, throw-ins

#### Composite Attributes (config/composite_attributes.py)
60+ weighted composite attributes organized by position type:

**Defenders:** Security, Progressive Passing, Ball Carrying, Aerial Ability, 1v1 Defending, Anticipation

**DM/CM:** Destroying, Dictating Tempo, Box-to-Box, Progressive Passing, Ball Retention, Pressing, Linkup Play

**AM/Wingers:** Finishing, 1v1 Ability, Movement Off Ball, Chance Creation, Linkup Play, Progressive Passing

**Fullbacks:** Overlapping, Underlapping, Ball Carrying, Crossing, Defensive Positioning, 1v1 Defending

**Forwards/Strikers:** Clinical Finishing, Poaching, Hold-up Play, Pressing, Movement, 1v1 Ability

Each composite attribute includes:
- `display_name`: Human-readable name
- `description`: What the attribute measures
- `archetypes`: Example players who exemplify this attribute
- `components`: List of (stat_name, weight) tuples (negative weights = inverse relationship)
- `icon`: Emoji for visual display

#### Role Presets
Pre-defined tactical roles with metric weights for each position type:
- **CB:** Ball-Playing Defender, Stopper, Modern CB, etc.
- **DM/CM:** Deep-Lying Playmaker, Box-to-Box, Destroyer, Regista, etc.
- **AM:** Classic 10, Inside Forward, Wide Playmaker, etc.
- **Fullback:** Attacking FB, Defensive FB, Inverted FB, etc.
- **Forwards:** Complete Forward, Poacher, False 9, etc.

---

## Page Details

### Page 1: Player Comparison
- Select 2-3 players for side-by-side statistical analysis
- Display stats by category (Defensive, Progressive, Offensive, Chance Creation, General, Set Pieces)
- Show composite attributes with radar charts and dot visualizations
- Display role/preset match scores to identify tactical fit
- Color-coded comparison: Red (#f01616), Blue (#3498db), Orange (#e67e22)

### Page 2: Player Finder
- **Role-based search:** Use preset tactical profiles (e.g., Ball-Playing CB, Deep-Lying Playmaker)
- **Responsibility-based search:** Search by specific composite attributes (e.g., Aerial Ability, Progressive Passing)
- **Advanced filters:** Age range, minimum minutes played, contract expiration
- **Adjustable metric weights:** Customize importance of each statistic
- Returns top N players ranked by weighted score

### Page 3: Player Similarity
- Find players similar to a reference player using cosine similarity
- **Weighted similarity:** Adjust importance of individual stats
- **Multiple visualization tabs:**
  - Similar players ranking
  - Metric contribution breakdown
  - Composite attribute comparison
- Filter by minutes, age range, and number of results

### Page 4: Scatter Analysis
- Interactive scatter plots for exploring relationships between two metrics
- **Dual-axis metric selection:** Choose X and Y axis from 100+ stats
- **Color coding options:** By position, team, or age groups
- **Interactive highlighting:** Click points to identify players
- **Quadrant analysis:** Identify players in different performance zones

### Page 5: Outliers Analysis
- Statistical outlier detection to identify exceptional performers
- **Two methods:** Z-Score (standard deviations) and IQR (interquartile range)
- **Single metric focus:** Clear, interpretable results for specific attributes
- **Both raw stats and composite attributes:** 100+ metrics available
- **High performers only:** Focus on positive outliers (talent identification)
- **Three-tab results:**
  - Interactive table with CSV export
  - Publication-ready matplotlib figures with team logos
  - Statistical interpretation guide

### Page 6: K-Means Clustering
- Identify player archetypes within position groups using unsupervised learning
- Configurable number of clusters (2-10)
- Cluster visualization on 2D PCA space
- Cluster profile analysis
- Player-by-cluster breakdown

### Page 7: League Fit
- Analyze player physical compatibility with target league (BRI Liga 1)
- **11 physical proxy metrics:** Accelerations, Duels, Aerial duels, Progressive runs, Defensive actions, Offensive duels, Dribbles
- Position-specific weight tables for target league assessment
- Risk classification: Ready (fit), Monitor (close fit), High risk (low fit)
- Benchmark comparison: target league vs source leagues
- Leaderboard showing best-fit players

### Page 8: Regression Analysis
- Statistical modeling to understand relationships between player statistics
- **Two regression models:**
  - OLS (Ordinary Least Squares) - Linear regression
  - Poisson Regression - For count data (goals, assists)
- Correlation matrix with heatmap visualization
- Variance Inflation Factor (VIF) analysis for multicollinearity
- Model comparison (AIC, BIC, R-squared)
- Coefficient interpretation and significance testing

---

## Key Design Patterns

### Percentile-Based Comparison
All raw statistics are converted to percentile ranks (0-100 scale) within the filtered dataset. This ensures fair comparison across:
- Different leagues (Thai League vs BRI Liga 1)
- Different positions (CB vs DM vs Winger)
- Different age groups

**Why percentiles?** A player with 5.0 progressive passes per 90 might be:
- 90th percentile among CBs
- 50th percentile among CMs
- 30th percentile among AMs

### Multi-Tiered Caching Strategy

```python
# Tier 1: Load all data once (no parameters)
@st.cache_data
def load_all_data():
    return load_all_league_data("data/2025/")

# Tier 2: Filter and process (cached by filter params)
@st.cache_data
def prepare_filtered_data(df, leagues_tuple, position_group):
    # Only recalculates when position group or leagues change
    filtered = filter_players(df, positions, leagues)
    with_percentiles = calculate_percentiles(filtered, stat_cols)
    with_composites = calculate_composite_attributes_batch(...)
    return with_composites
```

**Cache invalidation:** When global filters (position group or leagues) change, `prepare_filtered_data()` recalculates percentiles on the new subset.

### Multi-Layered Filtering

1. **Global filters** (sidebar):
   - Position group dropdown
   - League multi-select
   - Applied in `prepare_filtered_data()` [cached]

2. **Page-specific filters:**
   - Age range slider
   - Minimum minutes played
   - Contract expiration date
   - Applied after caching, within page render

### Composite Attributes Pre-Calculated

Composite attributes are calculated once during `prepare_filtered_data()` and stored with `COMP_` prefix:
- Batch calculation for performance (one pass through DataFrame)
- Stored as percentiles (0-100 scale)
- Available for all pages without recalculation

**Calculation Formula:**
```python
for component_stat, weight in components:
    composite_value += percentile(component_stat) * weight
composite_percentile = percentile(composite_value)  # Re-rank composite
```

---

## Data Structure

### CSV Files
Located in `data/2025/`
- **Encoding:** UTF-8 BOM (`utf-8-sig`)
- **Required Columns:**
  - **Metadata:** Player, Age, Team, Birth country, Position, Competition, League, Minutes played
  - **Statistics:** 100+ stat columns defined in `config/stat_categories.py`

### Column Naming Convention
- **Raw stats:** Exact Wyscout column names (e.g., "Progressive passes per 90")
- **Percentiles:** Same name as raw stat, stored in same DataFrame
- **Composite attributes:** Prefixed with `COMP_` (e.g., "COMP_Progressive Passing")
- **Player info:** Defined in `PLAYER_INFO_COLUMNS` (Age, Team, Position, etc.)

### Data Types
- **Per-90 stats:** Float (e.g., 5.2 passes per 90)
- **Percentages:** Float (e.g., 75.5 for 75.5%)
- **Absolute counts:** Integer (e.g., 12 goals)

---

## Recent Changes (Git Context)

### v5.1 In Progress - Major Refactoring & Data Expansion

**Deleted Files (auxiliary module removal):**
- `chatbot/` - AI chatbot module with RAG architecture (relocated for future v7.1 milestone)
- `scrapperfc/` - Wyscout data scraper (deprecated, using manual CSV exports)
- `scripts/` - Utility scripts for sync and validation (consolidated)
- `app_db.py` - Database integration module (replaced with new data loader)

**Modified Files:**
- `.claude/settings.local.json` - Claude Code settings updated
- `data/2025/BRI Liga 1 25-26.csv` - Updated league data

**New Southeast Asian League Data (2025 Season):**
- Thai League 1 25-26
- Malaysian Super League 25-26
- Singapore Premier League 25-26
- Cambodian Premier League 25-26
- V.League 1 25-26

**Additional League Data Added:**
- Top 5 European leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)
- Major South American leagues (Brasileirao, Argentina LPF)
- Additional Asian & European leagues for expanded coverage

**Interpretation:** v5.0 completed with production-ready core features. v5.1 focuses on cleanup, data validation, and stabilization before expanding functionality.

---

## Project Goals

### Primary Goals
1. **Professional Player Evaluation:** Provide scouts with comprehensive statistical analysis tools
2. **League-Specific Scouting:** Enable targeted scouting for BRI Liga 1 with league fit analysis
3. **Role-Based Identification:** Find players matching specific tactical profiles using preset configurations
4. **Data-Driven Decisions:** Support player acquisition decisions with statistical evidence and composite attributes

### Success Criteria
- **Usability:** Intuitive interface for non-technical scouts and analysts
- **Accuracy:** Reliable percentile calculations and composite attribute scoring
- **Performance:** Fast data loading and responsive UI with efficient caching
- **Extensibility:** Easy to add new leagues, positions, stats, and composite attributes
- **Visual Quality:** Publication-ready visualizations for presentations and reports

### Technical Success Metrics
- Data loading time < 10 seconds for 10,000+ players
- Page navigation < 2 seconds (cached)
- 99.9% uptime for production deployment
- Support for 20+ leagues with 10,000+ players total
- Zero data loss during CSV import/export

---

## Current Branch Status

**Branch:** `feature/app-v5`
**Main Branch:** `main`
**Status:** Active development, production-ready core features

**Recent Commits:**
- `6206523` - Initialize Milestone 1: Stabilization & Refactoring (v5.1)
- `checkposits` - Checkpoint management
- `checkpoints` - State checkpointing
- `update version` - Version bump
- `scrapper fc` - Scraper integration work
- `league fit` - League fit analysis feature

**Git Status:**
- Planning files committed to .planning/ directory
- Modified: 2 files (settings.local.json, BRI Liga 1 CSV)
- Deleted: ~40 files (auxiliary modules - chatbot, scrapperfc, scripts)
- Untracked: Multiple data folders and league CSVs (need organization)

---

## Development Workflow

### Making Changes
1. **Config changes** (stats, attributes, presets): Edit config files, no code changes needed
2. **Visualization changes:** Modify utils/player_comparison.py
3. **Search logic:** Update utils/player_finder.py or utils/player_similarity.py
4. **Data pipeline:** Modify utils/data_loader.py (affects all pages)

### Testing Changes
1. Clear Streamlit cache: Press 'C' in running app or `st.cache_data.clear()`
2. Verify percentiles recalculate correctly after filter changes
3. Test with multiple position groups and leagues
4. Check edge cases: single player, no results, missing data

### Adding New Data
1. Export CSV from Wyscout with all required columns
2. Place in `data/2025/` folder
3. Ensure UTF-8 encoding (convert if needed)
4. Restart app to load new data (automatic discovery)

---

## Dependencies Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

**Note:** For Ollama/ChromaDB chatbot features (currently removed), additional setup required.

---

## Known Limitations

1. **Single-Tenant Application:** No multi-user authentication or session isolation
2. **Static Data:** Requires manual CSV updates from Wyscout exports
3. **No Real-Time Data:** Data updates depend on manual Wyscout exports
4. **Memory Usage:** Large datasets (>50,000 players) may cause memory pressure
5. **Browser Compatibility:** Tested primarily on Chrome and Firefox

---

## Future Enhancements

### Potential Features (Not Yet Prioritized)
1. **Multi-User Authentication:** Role-based access control for scouts
2. **Real-Time Data Integration:** Direct Wyscout API integration
3. **Player Reports:** PDF export for player profiles and comparisons
4. **Watchlist Management:** Track players of interest over time
5. **Collaboration Features:** Share reports and annotations between scouts
6. **AI-Powered Insights:** Chatbot integration for natural language queries
7. **Performance Predictions:** Machine learning models for future performance
8. **Video Integration:** Link scouting reports to match footage

---

## Contact & Support

**Developer:** DARFAT
**Platform:** Claude Code with GSD workflow
**Codebase Location:** E:\darfat\work\playground\persib-scouting-wyscout
**Current Version:** v5.1 (feature/app-v5 branch)
**Current Milestone:** Milestone 1 - Stabilization & Refactoring (Started: 2026-02-28)

---

*Last Updated: 2026-02-28*
*Document Generated by: GSD Project Initialization*
*Milestone Status: v5.1 In Progress*
