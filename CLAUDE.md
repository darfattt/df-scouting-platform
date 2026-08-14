# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a sophisticated Streamlit-based football player scouting platform for analyzing players from various leagues using Wyscout data. The application has evolved into a five-page system with AI chatbot capabilities:

- **Player Comparison**: Side-by-side analysis of 2-3 players with detailed statistics and composite attributes
- **Player Finder**: Role-based and responsibility-based player search with tactical preset profiles
- **Player Similarity**: Find similar players using weighted cosine similarity across multiple metrics
- **Scatter Analysis**: Interactive scatter plots for exploring relationships between two metrics
- **Outliers Analysis**: Statistical outlier detection to identify exceptional performers using Z-score and IQR methods
- **AI Chatbot** (separate app): RAG-powered conversational interface for player queries

**Supported Position Groups**: CB, Fullback, DM, CM, AM, Winger, Forward, Striker (8 position types, 60+ composite attributes)

## Running the Application

```bash
# Main application (Player Comparison, Finder, Similarity)
pip install -r requirements.txt
streamlit run app.py

# AI Chatbot (requires Ollama - see chatbot/README.md for detailed setup)
# Step 1: Install Ollama from https://ollama.ai
# Step 2: Pull models (one-time setup)
ollama pull phi3:mini
ollama pull nomic-embed-text:latest

# Step 3: Start Ollama server in a separate terminal (REQUIRED)
ollama serve  # Keep this terminal open!

# Step 4: Run the chatbot app in a different terminal
conda activate python_310_env  # or your Python environment
streamlit run chatbot/chatbot_app.py
```

## Architecture

### Five-Page Application (app.py - ~2950 lines)

The main application is organized into five distinct pages accessible via the sidebar:

#### Page 1: Player Comparison
- Select 2-3 players for side-by-side statistical analysis
- Display stats by category (Defensive, Progressive, Offensive, Chance Creation, General, Set Pieces)
- Show composite attributes with radar charts and dot visualizations
- Display role/preset match scores to identify tactical fit
- Color-coded comparison: Green (#2ecc71), Blue (#3498db), Orange (#e67e22)

#### Page 2: Player Finder
- **Role-based search**: Use preset tactical profiles (e.g., Ball-Playing CB, Deep-Lying Playmaker)
- **Responsibility-based search**: Search by specific composite attributes (e.g., Aerial Ability, Progressive Passing)
- **Advanced filters**: Age range, minimum minutes played, contract expiration
- **Adjustable metric weights**: Customize importance of each statistic
- Returns top N players ranked by weighted score

#### Page 3: Player Similarity
- Find players similar to a reference player using cosine similarity
- **Weighted similarity**: Adjust importance of individual stats
- **Multiple visualization tabs**:
  - Similar players ranking
  - Metric contribution breakdown
  - Composite attribute comparison
- Filter by minutes, age range, and number of results

#### Page 4: Scatter Analysis
- Interactive scatter plots for exploring relationships between two metrics
- **Dual-axis metric selection**: Choose X and Y axis from 100+ stats
- **Color coding options**: By position, team, or age groups
- **Interactive highlighting**: Click points to identify players
- **Quadrant analysis**: Identify players in different performance zones
- Export-ready visualizations

#### Page 5: Outliers Analysis
- Statistical outlier detection to identify exceptional performers
- **Two methods**: Z-Score (standard deviations) and IQR (interquartile range)
- **Single metric focus**: Clear, interpretable results for specific attributes
- **Both raw stats and composite attributes**: 100+ metrics available
- **High performers only**: Focus on positive outliers (talent identification)
- **Three-tab results**:
  - Interactive table with CSV export
  - Publication-ready matplotlib figures with team logos
  - Statistical interpretation guide
- Filter by age, minutes played, and top N results

#### Page 6: Outlier Intelligence — Automated Scout (page/outlier_intelligence.py)

A single end-to-end workflow that merges **Data Engineering → ML Prediction → AI Analysis** into one page. Instead of detecting outliers on a raw metric (Page 5), it runs the full Bronze→Silver→Gold pipeline, trains a position-aware ML model on demand, and surfaces elite players with AI scouting reports and league-relative benchmarking.

**Entry point:** `render_outlier_intelligence_page(df_filtered, selected_position_group)`. Shared logic (pipeline, models, enrichment) is lazily imported from `page/ai_intelligence.py` via `import_pipeline()`, `import_models()`, `import_enrichment()`.

**Step-by-step process:**

1. **Define Initial Context** (UI)
   - `Minimum Minutes Played` — the only required filter to start (default 300).
   - `Target League (benchmark)` — the league whose `composite_score` distribution the tier verdict and z-score are re-baselined against. `_pick_default_target_league()` defaults to BRI Liga 1 (`DEFAULT_TARGET_LEAGUE_HINT = "Liga 1"`); choosing the `GLOBAL_LEAGUE_SENTINEL` keeps dataset-wide tiers.

2. **Metric Selection** (analysis context)
   - Pick a metric type: **Raw Stats**, **Composite Attributes** (`COMP_*`), or **Grades** (`GRADE_*`). Raw Stats can be narrowed by category from `STAT_CATEGORIES`.
   - The chosen metric only drives AI focus and table sorting — it does not filter rows.

3. **Auto-sync ML Features**
   - When the selected metric changes, its constituent stats are resolved (Raw → itself; Grade → `GRADE_ATTRIBUTES[key]["components"]`; Composite → `COMPOSITE_ATTRIBUTES[key]["components"]`) and merged with `SUPPLEMENTARY_FEATURES` from `models/feature_engineering.py`. The result pre-populates the `oi_ml_features` multiselect so the model trains on features relevant to the metric.

4. **ML Model Features** (UI)
   - A multiselect (`oi_ml_features`) over `ML_FEATURES + SUPPLEMENTARY_FEATURES + all_stats`. These are the features used to train/predict the performance tier.

5. **Run Pipeline** — `_execute_pipeline(...)`
   - Filter locally by `Minutes played >= min_mins`; abort if fewer than 20 players remain.
   - `run_pipeline(df, progress_callback)` executes the **Bronze → Silver → Gold** data layers (with a Streamlit progress bar); aborts if `result["overall"] != "success"`.
   - `load_gold()` loads the Gold layer, then `train_model(df_gold, feature_names=ml_features, nickname="dynamic")` **always retrains** an XGBoost model so it stays in sync with the user-selected features.
   - `predict_dataframe(df_gold, nickname="dynamic")` returns `df_results` with `predicted_tier_label` and `composite_score`.
   - `_recalibrate_against_target_league(df_results, target_league)` re-baselines against the target league (see below).
   - Results, baseline meta, and a timestamp are stored in `st.session_state` (`oi_results`, `oi_target_baseline`, `oi_timestamp`), then `st.rerun()`.

6. **League re-baselining** — `_recalibrate_against_target_league(...)`
   - Preserves the model's global-trained verdict in `predicted_tier_label_global` before overriding `predicted_tier_label`.
   - If target is Global (or `League` missing, or the league has < 10 players in the result set → falls back with a warning), `composite_zscore` is computed against the global mean/std.
   - Otherwise it computes the target league's mean, std, and P30/P70/P90 quantiles, recomputes `composite_zscore` relative to that league, and reassigns tiers: **Elite** (≥P90), **Good** (≥P70), **Average** (≥P30), **Below Average** (below P30).

7. **Results Display** — `_render_results_section(...)`
   - A benchmark banner reports which league tiers are relative to (or the fallback warning).
   - Secondary post-analysis filters (in an expander): Age range, Top N, Tiers, Position Group, and Contract Expiry — these re-filter the cached results without re-running the pipeline. The table is sorted by the selected context metric (falling back to `composite_score`).
   - For each row it derives two tactical columns: **Best Role** (highest weighted role score from `get_all_roles()`, restricted to roles mapped to the player's position group via `get_roles_for_position`) and **Top Archetypes** (top-3 `COMP_*` attributes, restricted by `get_responsibilities_for_position`).
   - A styled dataframe is shown with tier labels color-coded via `ACCENT_COLORS`.

8. **AI Scout Deep-Dive** (Gemini)
   - Gated by `is_configured()` (requires `GEMINI_API_KEY`). For a chosen player, it assembles a stats dict from the used ML features, recomputes Best Role and Top Archetypes, builds a structured prompt with `build_player_scouting_prompt(...)` (passing the target league for league-relative context), and renders the text from `generate_scouting_report(prompt)`.

9. **Graphical Stats** — `_render_graphical_stats_section(...)`
   - **Scatter tab** — a league-fit plot of **Age (x) vs composite z-score (y)**. Context dots come from the global Gold layer; the z-score reference is anchored to the target league (`TARGET_LEAGUE` from `config/league_fit_config.py`, falling back to the shown cloud when < 10 league peers match the position filter). The monitored player is highlighted in gold, additional players/tiers can be highlighted, and reference lines mark the league average (0) and ±1 std.
   - **Distribution tab** — bar charts of the currently-filtered table: Age, Best Role, League, Position Group, Market Value range, and Passport Country.

**Key session-state keys:** `oi_results`, `oi_target_baseline`, `oi_target_league`, `oi_selected_metric`, `oi_ml_features`, `oi_timestamp`. The trained model is always saved under the `"dynamic"` nickname.

### Data Processing Pipeline

```
load_all_data() [cached once, no parameters]
    ↓
get_distinct_values() [extract unique leagues/positions]
    ↓
prepare_filtered_data() [cached by: position_group + leagues_tuple]
    ├── Filter by position group and selected leagues
    ├── Calculate percentiles on filtered subset (0-100 scale)
    └── Calculate composite attributes (batch processing)
        ↓
render_page() [with page-specific filters: age, minutes, contract]
```

**Key Insight**: Percentiles are recalculated whenever global filters (position group or leagues) change, ensuring fair comparison within the filtered dataset.

### Configuration System

The application uses a modular configuration system to separate data definitions from business logic:

#### config/stat_categories.py
Defines 6 statistical categories with 100+ metrics:
- **Defensive**: Tackles, interceptions, duels, defensive actions
- **Offensive**: Goals, shots, xG, box entries, dribbles
- **Progressive**: Progressive passes/runs/carries, deep progressions
- **Chance Creation**: Assists, xA, key passes, crosses, smart passes
- **General**: Passes, pass accuracy, ball touches, aerial duels
- **Set Pieces**: Corners, free kicks, throw-ins

Also defines:
- `PLAYER_INFO_COLUMNS`: Metadata fields (Player, Age, Team, Position, etc.)
- `PLAYER_COLORS`: Color scheme for multi-player comparisons

#### config/composite_attributes.py (44 KB)
Defines 60+ weighted composite attributes organized by position type. Each attribute includes:
- `display_name`: Human-readable name (e.g., "Progressive Passing")
- `description`: What the attribute measures
- `archetypes`: Example players who exemplify this attribute
- `components`: List of (stat_name, weight) tuples (negative weights = inverse relationship)
- `icon`: Emoji for visual display

**Position-specific attributes:**
- **Defenders**: Security, Progressive Passing, Ball Carrying, Aerial Ability, 1v1 Defending, etc.
- **DM/CM**: Destroying, Dictating Tempo, Box-to-Box, Progressive Passing, Ball Retention, etc.
- **AM/Wingers**: Finishing, 1v1 Ability, Movement Off Ball, Chance Creation, Linkup Play, etc.
- **Fullbacks**: Overlapping, Underlapping, Ball Carrying, Crossing, Defensive Positioning, etc.
- **Forwards/Strikers**: Clinical Finishing, Poaching, Hold-up Play, Pressing, Movement, etc.

Example composite attribute structure:
```python
"COMP_Progressive Passing": {
    "display_name": "Progressive Passing",
    "description": "Ability to play forward passes that advance team position",
    "archetypes": "Toni Kroos, Kevin De Bruyne",
    "components": [
        ("Progressive passes per 90", 0.35),
        ("Forward passes per 90", 0.25),
        ("Smart passes per 90", 0.20),
        ("Accurate passes to final third, %", 0.20)
    ],
    "icon": "➡️"
}
```

#### config/position_groups.py
Maps logical position groups to specific position tags from Wyscout data:
- **CB** → ["CB", "RCB", "LCB", "RCB3", "LCB3"]
- **Fullback** → ["LB", "RB", "LWB", "RWB", "LB5", "RB5"]
- **DM** → ["DMF"]
- **CM** → ["LCMF", "RCMF", "CMF", "LCMF3", "RCMF3"]
- **AM** → ["LAMF", "RAMF", "AMF"]
- **Winger** → ["LW", "RW", "LWF", "RWF"]
- **Forward** → ["CF"]
- **Striker** → ["CF"]

#### config/position_rankings.py
Maps which composite attributes are most relevant for each position type. Used for:
- Display ordering in Player Comparison page
- Emphasis in visualizations
- Default weights in Player Finder

Example:
```python
"CB": [
    "COMP_Security", "COMP_Aerial Ability", "COMP_1v1 Defending",
    "COMP_Progressive Passing", "COMP_Anticipation", ...
]
```

#### config/[position]_presets.py
Role profile configurations for tactical player archetypes:
- **defender_presets.py**: Ball-Playing CB, Stopper, Modern CB, etc.
- **midfielder_presets.py**: Deep-Lying Playmaker, Box-to-Box, Destroyer, Regista, etc.
- **forward_presets.py**: Complete Forward, Poacher, False 9, etc.
- **fullback_presets.py**: Attacking FB, Defensive FB, Inverted FB, etc.
- **attacking_midfielder_presets.py**: Classic 10, Inside Forward, Wide Playmaker, etc.
- **similarity_presets.py**: Presets for similarity matching

Each preset defines metric weights for role-based scoring:
```python
"Deep-Lying Playmaker": {
    "Accurate progressive passes per 90": 1.2,
    "Passes to final third per 90": 1.0,
    "Forward passes per 90": 0.9,
    "Progressive passes per 90": 1.1,
    ...
}
```

### Utility Modules

#### utils/data_loader.py (200+ lines)
Core data pipeline handling all CSV operations and transformations:

**Key Functions:**
```python
load_all_league_data(folder)
    # Loads all CSV files from specified folder (default: data/2025/)
    # Returns: Combined DataFrame with all leagues

get_distinct_values(df)
    # Extracts unique leagues and positions for filter dropdowns
    # Returns: (sorted_leagues, sorted_positions)

filter_players(df, positions, leagues)
    # Filters DataFrame by position group and selected leagues
    # Returns: Filtered DataFrame

calculate_percentiles(df, stat_cols)
    # Converts raw stats to percentile ranks (0-100) within filtered dataset
    # Returns: DataFrame with percentile columns

calculate_composite_attributes_batch(df, composite_definitions)
    # Batch computes all composite attributes using weighted formulas
    # Adds columns with COMP_ prefix
    # Returns: DataFrame with composite attribute columns

get_player_info(df, player_name)
    # Retrieves player metadata (age, team, position, etc.)
    # Returns: Dictionary of player info

get_player_stats(df, player_name, stat_cols)
    # Gets raw stats + percentiles for specific player
    # Returns: Dictionary with stats and percentile values

get_player_composite_attrs(df, player_name)
    # Gets pre-calculated composite attributes
    # Returns: Dictionary of composite attribute percentiles
```

**Important Implementation Details:**
- UTF-8 BOM encoding (`utf-8-sig`) for CSV files
- Automatic removal of unnamed columns
- Percentile calculation uses `rank(pct=True)` for 0-1 scale, then * 100

#### utils/column_mapping.py
CSV compatibility layer handling schema changes:

**COLUMN_ALIASES**: Maps old column names to new standardized names
```python
{
    "League": "Competition",
    "Matches played": "Matches",
    # ... many more aliases
}
```

**calculate_derived_metrics(df)**: Computes metrics missing from CSV
- Calculates derived stats from available columns
- Handles backward compatibility with older data exports

#### utils/player_comparison.py
Visualization functions for Player Comparison page (Page 1):

```python
display_player_comparison(player_data_list, category_stats)
    # Side-by-side stat tables with percentile bars

display_composite_attributes(player_data_list, composite_attrs)
    # Radar charts and bar graphs for composite attributes

display_attribute_rankings_1d_dot(player_data_list, composite_attrs)
    # Dot charts showing attribute rankings on 0-100 scale

display_role_preset_match(df, player_names, position_group)
    # Role matching analysis using preset profiles
    # Shows best tactical fit for each player
```

All visualizations use consistent styling:
- Cream background (#f5f3e8)
- Player-specific colors (Green, Blue, Orange)
- Matplotlib with custom formatting

#### utils/player_finder.py (400+ lines)
Role-based and responsibility-based player search (Page 2):

**Main Classes:**
- `DefenderScorer`: Scoring for CB, Fullback positions
- `MidfielderScorer`: Scoring for DM, CM positions
- `ForwardScorer`: Scoring for AM, Winger, Forward, Striker positions

**Key Method:**
```python
DefenderScorer.calculate_preset_score(
    df,                              # Filtered DataFrame
    preset_name,                     # Role profile name
    top_n=30,                        # Number of results
    min_minutes=0,                   # Minimum minutes filter
    age_range=(18, 40),              # Age range filter
    contract_expires_before=None     # Contract filter (optional)
)
# Returns: DataFrame with players ranked by weighted score
```

**Scoring Logic:**
1. Load preset metric weights
2. Apply filters (minutes, age, contract)
3. Calculate weighted score: sum(percentile * weight) for each metric
4. Rank players by total score
5. Return top N results

#### utils/player_similarity.py (300+ lines)
Similarity scoring using cosine similarity (Page 3):

**Main Class: SimilarityScorer**

**Key Method:**
```python
SimilarityScorer.calculate_similarity(
    df,                              # Filtered DataFrame
    reference_player_name,           # Player to compare against
    weights={metric: weight, ...},   # User-adjustable weights
    min_minutes=500,                 # Minimum minutes filter
    age_range=(22, 35),              # Age range filter
    top_n=30                         # Number of results
)
# Returns: (similarity_scores, percentiles, metric_contributions)
```

**Similarity Calculation:**
1. Extract reference player's percentile vector
2. Apply metric weights to create weighted vectors
3. Calculate cosine similarity between reference and all other players
4. Compute metric-level contribution to similarity
5. Rank players by similarity score (0-1 scale)
6. Return top N most similar players

**Visualization Outputs:**
- Similarity ranking table
- Metric contribution breakdown (which stats drive similarity)
- Composite attribute radar comparison

#### utils/similarity_helpers.py
Helper functions for similarity matching:

```python
get_position_similarity_weights(position_group)
    # Returns default metric weights for position

map_position_to_group(position)
    # Maps specific position to position group

get_presets_for_position(position_group)
    # Returns available presets for position
```

#### utils/outlier_detection.py (389 lines)
Statistical outlier detection for exceptional player identification (Page 5):

**Key Functions:**
```python
detect_outliers_zscore(df, metric, threshold=3.0, higher_is_good=True)
    # Z-score based outlier detection
    # threshold: Standard deviations from mean (default 3.0 = 99.7%)
    # higher_is_good: Metric direction (from STAT_CATEGORIES)
    # Returns: DataFrame with z_score, outlier_type columns

detect_outliers_iqr(df, metric, multiplier=1.5, higher_is_good=True)
    # IQR (Interquartile Range) based detection
    # multiplier: IQR threshold multiplier (default 1.5)
    # More robust to extreme values than Z-score
    # Returns: DataFrame with iqr_distance, outlier_type columns

get_metric_indicator(metric, stat_categories)
    # Determines if metric is HIGHER_IS_GOOD or LOWER_IS_GOOD
    # Composite attributes (COMP_*) always HIGHER_IS_GOOD
    # Returns: True if higher is better, False otherwise

create_outliers_table_figure(outliers_df, metric, method, position_group, df_filtered, top_n=20)
    # Creates matplotlib figure for export
    # Cream background (#f5f3e8), team logos, outlier scores
    # Returns: plt.Figure object

display_outliers_analysis(outliers_df, metric, method, player_info_cols)
    # Streamlit interactive table display
    # Includes CSV download button
    # Dynamic height based on results
```

**Outlier Detection Logic:**
1. Calculate statistical measures (mean/std for Z-score, Q1/Q3/IQR for IQR)
2. Identify outliers based on threshold (±3σ or Q3 + 1.5×IQR)
3. Focus on high performers (positive outliers for talent ID)
4. Handle LOWER_IS_GOOD metrics (invert logic for fouls, cards, etc.)
5. Sort by outlier score and return top N

**Use Cases:**
- Find elite goal scorers (Z-score on "Goals per 90")
- Identify ball-playing CBs (IQR on "Progressive passes per 90")
- Discover high-volume dribblers (Z-score on "Dribbles per 90")
- Scout exceptional defensive disruptors (composite attributes)

### Chatbot Architecture (chatbot/)

The AI chatbot is a separate Streamlit application with RAG (Retrieval-Augmented Generation) architecture for conversational player queries.

#### chatbot/chatbot_app.py
Main Streamlit interface for the AI assistant:
- Chat interface with message history
- Integration with Ollama for local LLM inference
- Session state management for conversation persistence
- Player data context retrieval

#### RAG Pipeline Components

**chatbot/ollama/client.py**
- Local LLM integration using Ollama API
- Manages connection to Ollama server (default: http://localhost:11434)
- Handles model selection and inference parameters
- Error handling for connection failures

**chatbot/vector_store/chroma_wrapper.py**
- ChromaDB wrapper for player embeddings
- Stores and retrieves player data vectors
- Semantic search over player profiles
- Persistent storage of embeddings

**chatbot/retrieval/query_processor.py**
- Processes and normalizes user queries
- Extracts player names, positions, statistics from questions
- Intent classification (comparison, search, analysis)

**chatbot/retrieval/context_builder.py**
- Builds relevant context from player data
- Retrieves similar players and statistics
- Formats context for LLM consumption
- Limits context size for token efficiency

**chatbot/response/generator.py**
- Generates natural language responses using LLM
- Combines retrieved context with conversation history
- Formats responses with statistics and comparisons
- Handles multi-turn conversations

**chatbot/utils/chat_memory.py**
- Manages conversation history
- Stores user messages and assistant responses
- Provides context window for multi-turn dialogue
- Session persistence

**chatbot/knowledge/**
- Domain knowledge modules
- Football terminology and tactical concepts
- Position-specific knowledge bases
- Statistical definitions and formulas

### Data Structure

**CSV Files**: Located in `data/2025/`
- Examples:
  - `Brazil Serie B 2025.csv`
  - `BRI Liga 1 25-26.csv`
  - `La Liga 2025.csv`
  - `Premier League 2025.csv`

**Encoding**: UTF-8 BOM (`utf-8-sig`)

**Required Columns**:
- **Metadata**: Player, Age, Team, Birth country, Position, Competition, League, Minutes played
- **Statistics**: 100+ stat columns defined in `config/stat_categories.py`

**Data Types**:
- **Per-90 stats**: Float (e.g., 5.2 passes per 90)
- **Percentages**: Float (e.g., 75.5 for 75.5%)
- **Absolute counts**: Integer (e.g., 12 goals)

**Column Naming Convention**:
- Raw stats: Use exact Wyscout export column names
- Percentile columns: Added by `calculate_percentiles()` with same name
- Composite attributes: Prefixed with `COMP_` (e.g., `COMP_Progressive Passing`)

### Key Design Patterns

#### Percentile-Based Comparison
All raw statistics are converted to percentile ranks (0-100 scale) within the filtered dataset. This ensures fair comparison across:
- Different leagues (Brazil Serie B vs Premier League)
- Different positions (CB vs DM vs Winger)
- Different age groups

**Why percentiles?** A player with 5.0 progressive passes per 90 might be:
- 90th percentile among CBs
- 50th percentile among CMs
- 30th percentile among AMs

#### Multi-Tiered Caching Strategy

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

**Why tuple for leagues?** Lists are mutable and can't be hashed for caching. Convert to tuple for cache key.

**Cache invalidation**: When global filters (position group or leagues) change, `prepare_filtered_data()` recalculates percentiles on the new subset.

#### Multi-Layered Filtering

1. **Global filters** (sidebar):
   - Position group dropdown
   - League multi-select
   - Applied in `prepare_filtered_data()` [cached]

2. **Page-specific filters**:
   - Age range slider
   - Minimum minutes played
   - Contract expiration date
   - Applied after caching, within page render

**Why separate?** Global filters trigger percentile recalculation (expensive). Page-specific filters are simple row filters (cheap).

#### Composite Attributes Pre-Calculated

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

#### Role/Preset Profiles

Pre-defined tactical roles with metric weights for each position type:
- **Purpose**: Codify scout knowledge about what makes a good "Deep-Lying Playmaker" vs "Box-to-Box Midfielder"
- **Storage**: Separate files per position group (`config/midfielder_presets.py`)
- **Usage**: Player Finder page, Role Matching analysis

**Example Use Case:**
"Find the best Ball-Playing CBs in Brazil Serie B under age 25"
1. Select position: CB
2. Select role: Ball-Playing Defender
3. Filter: Age < 25, League = Brazil Serie B
4. System applies preset weights to calculate scores
5. Returns top 30 players ranked by weighted score

#### Column Mapping and Compatibility

`utils/column_mapping.py` handles CSV schema changes:
- **Aliases**: Map old column names to new (e.g., "League" → "Competition")
- **Derived Metrics**: Calculate missing stats from available data
- **Backward Compatibility**: Support for both old and new Wyscout exports

**Example:**
```python
# Old CSV has "League", new has "Competition"
COLUMN_ALIASES = {"League": "Competition"}
# System uses "Competition" internally, transparently maps from "League"
```

## Adding New Features

### Adding a New Position Group

1. **Update position mapping** in `config/position_groups.py`:
   ```python
   POSITION_GROUPS = {
       # ... existing ...
       "New Position": ["POS1", "POS2", "POS3"]  # Wyscout position tags
   }
   ```

2. **Define key attributes** in `config/position_rankings.py`:
   ```python
   POSITION_KEY_ATTRIBUTES = {
       # ... existing ...
       "New Position": [
           "COMP_Attribute1",
           "COMP_Attribute2",
           # ... ranked by importance
       ]
   }
   ```

3. **Add presets** to appropriate `config/[position]_presets.py` (or create new file):
   ```python
   "Role Name": {
       "Metric 1": 1.2,  # Higher weight = more important
       "Metric 2": 0.8,
       # ... all relevant metrics
   }
   ```

4. **Update scorer classes** in `utils/player_finder.py` if needed:
   - Add to existing scorer class, or
   - Create new scorer class for unique position type

### Adding New Statistics

1. **Add to category** in `config/stat_categories.py`:
   ```python
   STAT_CATEGORIES = {
       "Category Name": [
           # ... existing stats ...
           "New Stat Name",  # Must match CSV column name exactly
       ]
   }
   ```

2. **Ensure CSV contains the column**:
   - Check data export includes the stat
   - Verify column name matches exactly (case-sensitive)

3. **Stats are automatically included**:
   - Percentile calculation (in `calculate_percentiles()`)
   - Available for all comparisons and searches
   - Can be used in composite attributes

### Adding New Composite Attributes

1. **Define in** `config/composite_attributes.py`:
   ```python
   COMPOSITE_ATTRIBUTES["DEFENDER"]["COMP_New Attribute"] = {
       "display_name": "New Attribute",
       "description": "What this attribute measures and why it matters",
       "archetypes": "Player A, Player B, Player C",
       "components": [
           ("Stat 1", 0.4),      # Positive weight
           ("Stat 2", 0.3),
           ("Stat 3", -0.2),     # Negative weight (inverse relationship)
           ("Stat 4", 0.1),
       ],
       "icon": "🎯"  # Choose relevant emoji
   }
   ```

2. **Guidelines for component weights**:
   - Sum doesn't need to equal 1.0 (percentiles are re-ranked)
   - Negative weights for inverse relationships (e.g., -10% Fouls in Tackling)
   - Higher weights for more important components
   - Include 3-6 components (avoid single-stat composites)

3. **Add to position rankings** in `config/position_rankings.py` if relevant:
   ```python
   POSITION_KEY_ATTRIBUTES = {
       "Position": [
           # ... existing ...
           "COMP_New Attribute",  # Add in priority order
       ]
   }
   ```

4. **Automatic integration**:
   - Calculated in `calculate_composite_attributes_batch()`
   - Available in all visualizations
   - Usable in Player Finder and Similarity pages

### Adding New Role Presets

1. **Choose appropriate file** in `config/`:
   - `defender_presets.py` for CB, Fullback
   - `midfielder_presets.py` for DM, CM
   - `attacking_midfielder_presets.py` for AM
   - `forward_presets.py` for Winger, Forward, Striker
   - Or create new file for new position group

2. **Define preset dictionary**:
   ```python
   "Role Name": {
       "Metric 1": 1.5,   # Most important
       "Metric 2": 1.2,
       "Metric 3": 1.0,
       "Metric 4": 0.8,
       "Metric 5": 0.5,   # Less important
       # Include 10-20 metrics for comprehensive profile
   }
   ```

3. **Metric selection guidelines**:
   - Use raw stats (not composite attributes) for granular control
   - Include both volume and efficiency metrics
   - Balance offensive and defensive aspects
   - Consider per-90 vs percentage stats

4. **Preset automatically available**:
   - Player Finder dropdown
   - Role matching analysis
   - No code changes needed

### Troubleshooting Common Issues

#### Chatbot Connection Failures

**For detailed chatbot setup and troubleshooting, see `chatbot/README.md`**

**Error**: `OLLAMA SERVER NOT RUNNING` or `Failed to connect to Ollama`

**Root Cause**: The Ollama server is not running on localhost:11434

**Quick Fix**:
1. Open a **NEW terminal window**
2. Start Ollama server: `ollama serve`
3. **Keep that terminal open** (don't close it!)
4. Restart the chatbot app

**Verification Steps**:
```bash
# Step 1: Verify Ollama is installed
ollama --version

# Step 2: Verify models are downloaded
ollama list
# Should show: phi3:mini and nomic-embed-text:latest

# Step 3: If models missing, pull them
ollama pull phi3:mini
ollama pull nomic-embed-text:latest

# Step 4: Start server (in separate terminal)
ollama serve
# Should show: "Ollama is running on http://localhost:11434"

# Step 5: Test connection (in different terminal)
curl http://localhost:11434/api/tags
# Should return JSON with model list

# Step 6: Run chatbot
conda activate python_310_env
streamlit run chatbot/chatbot_app.py
```

**Common Mistakes**:
- Forgetting to run `ollama serve` before starting chatbot
- Closing the terminal running `ollama serve`
- Not pulling required models first
- Using wrong Python environment (need python_310_env)

#### Percentile Calculation Issues

**Problem**: Percentiles seem incorrect or biased

**Check**:
1. Global filters: Are you comparing within the right position group?
2. League selection: Comparing Serie B players to Premier League?
3. Minutes filter: Low-minute players can skew percentiles

**Fix**: Adjust filters to create appropriate comparison group.

#### Missing Composite Attributes

**Problem**: Composite attribute shows NaN or missing

**Causes**:
1. Missing component stats in CSV
2. Component stat name doesn't match CSV column
3. Column alias not defined in `column_mapping.py`

**Debug**:
```python
# Check available columns
print(df.columns.tolist())

# Check specific player's component stats
player_stats = get_player_stats(df, "Player Name", component_stat_list)
print(player_stats)
```

## Important Implementation Details

### Encoding and Data Handling
- **UTF-8 BOM Encoding**: All CSV files use `utf-8-sig` encoding to handle Byte Order Mark
- **Unnamed Column Handling**: First unnamed column is automatically removed during load
- **Missing Data**: NaN values in stats are handled gracefully (excluded from percentile calculations)

### Visual Design System
- **Color Scheme**:
  - Player 1: Green (#2ecc71)
  - Player 2: Blue (#3498db)
  - Player 3: Orange (#e67e22)
- **Background Color**: Cream (#f5f3e8) for all visualizations
- **Chart Styling**: Consistent matplotlib configuration across all charts

### Performance Optimizations
- **Caching**: Two-tier caching (data load + filtered processing)
- **Batch Processing**: Composite attributes calculated in single pass
- **Lazy Loading**: Charts only rendered when tab is selected
- **DataFrame Indexing**: Efficient filtering using boolean indexing

### Session State Management
Streamlit session state preserves:
- Selected position group
- Selected leagues
- Selected players (Page 1)
- Search parameters (Page 2)
- Reference player (Page 3)
- Page navigation state

### Column Naming Conventions
- **Raw stats**: Exact Wyscout column names (e.g., "Progressive passes per 90")
- **Percentiles**: Same name as raw stat, stored in same DataFrame
- **Composite attributes**: Prefixed with `COMP_` (e.g., "COMP_Progressive Passing")
- **Player info**: Defined in `PLAYER_INFO_COLUMNS` (Age, Team, Position, etc.)

### Error Handling
- **Missing players**: Graceful handling with user-friendly error messages
- **Invalid filters**: Automatic constraint validation
- **Empty results**: Helpful suggestions when no players match criteria
- **CSV loading errors**: Detailed error messages with file path and line number

## Dependencies

Main application dependencies (requirements.txt):

```python
streamlit==1.31.0          # Web UI framework
pandas==2.2.0              # Data manipulation
matplotlib==3.8.2          # Static visualizations
numpy==1.26.3              # Numerical computing
plotly==5.18.0             # Interactive charts (optional, for future features)
scikit-learn==1.4.0        # Cosine similarity calculations
```

Chatbot additional dependencies:

```python
ollama>=0.3.0              # Local LLM integration
chromadb>=0.4.0            # Vector database for embeddings
fuzzywuzzy>=0.18.0         # Fuzzy string matching for player names
python-Levenshtein>=0.23.0 # String distance calculations
```

## File Structure Overview

```
persib-scouting-wyscout/
├── app.py (2090 lines)           # Main 3-page Streamlit app
├── requirements.txt               # Python dependencies
├── CLAUDE.md                      # This file
│
├── config/                        # Configuration modules
│   ├── stat_categories.py         # Stat category definitions
│   ├── composite_attributes.py    # 60+ composite attribute formulas (44 KB)
│   ├── position_groups.py         # Position filtering logic
│   ├── position_rankings.py       # Position-specific attribute priority
│   ├── defender_presets.py        # CB/Fullback role profiles
│   ├── midfielder_presets.py      # DM/CM role profiles
│   ├── attacking_midfielder_presets.py  # AM role profiles
│   ├── forward_presets.py         # Winger/Forward/Striker role profiles
│   ├── fullback_presets.py        # Fullback role profiles
│   └── similarity_presets.py      # Similarity matching presets
│
├── utils/                         # Utility modules
│   ├── data_loader.py (200+ lines)      # Core data pipeline
│   ├── column_mapping.py          # CSV compatibility layer
│   ├── player_comparison.py       # Page 1 visualizations
│   ├── player_finder.py (400+ lines)    # Page 2 search logic
│   ├── player_similarity.py (300+ lines) # Page 3 similarity scoring
│   └── similarity_helpers.py      # Similarity helper functions
│
├── chatbot/                       # AI chatbot application
│   ├── chatbot_app.py             # Chatbot Streamlit interface
│   ├── ollama/
│   │   └── client.py              # Ollama LLM integration
│   ├── vector_store/
│   │   └── chroma_wrapper.py      # ChromaDB wrapper
│   ├── retrieval/
│   │   ├── query_processor.py     # Query processing
│   │   └── context_builder.py     # Context retrieval
│   ├── response/
│   │   └── generator.py           # Response generation
│   ├── utils/
│   │   └── chat_memory.py         # Conversation history
│   └── knowledge/                 # Domain knowledge modules
│
└── data/
    └── 2025/                      # Wyscout CSV exports
        ├── Brazil Serie B 2025.csv
        ├── BRI Liga 1 25-26.csv
        ├── La Liga 2025.csv
        ├── Premier League 2025.csv
        └── ... (multiple league files)
```

## Development Workflow

### Making Changes
1. **Config changes** (stats, attributes, presets): Edit config files, no code changes needed
2. **Visualization changes**: Modify utils/player_comparison.py
3. **Search logic**: Update utils/player_finder.py or utils/player_similarity.py
4. **Data pipeline**: Modify utils/data_loader.py (affects all pages)

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

## Best Practices

### When Working with Percentiles
- Always calculate percentiles AFTER filtering to ensure fair comparison
- Percentiles are relative to the filtered dataset, not absolute skill level
- A 90th percentile CB in Brazil Serie B ≠ 90th percentile CB in Premier League

### When Defining Composite Attributes
- Use 3-6 component stats (avoid single-stat or too complex)
- Include both volume and efficiency metrics
- Consider position-specific context (what matters for this role?)
- Test with known players to validate formula

### When Creating Presets
- Base on real tactical roles and scout knowledge
- Include 10-20 metrics for comprehensive profile
- Weight most important metrics 1.0-1.5, less important 0.3-0.8
- Test against known players to ensure preset captures role essence

### Cache Management
- Global filter changes → Clear cache and recalculate percentiles
- Config changes → No cache clear needed (dynamically loaded)
- Data changes → Restart app to reload CSVs
