# Codebase Architecture Analysis

## Project Overview

This is a sophisticated Streamlit-based football player scouting platform for analyzing players from various leagues using Wyscout data. The application provides comprehensive player analysis through multiple interactive page.

**Key Statistics:**
- Main Application: `app.py` (5,623 lines)
- Total Python Modules: 29 files
- Technology Stack: Streamlit, Pandas, NumPy, Matplotlib, Plotly, Scikit-learn
- Supported Position Groups: 8+ position types (CB, Fullback, DM, CM, AM, Winger, Forward, Striker)
- Composite Attributes: 60+ weighted composite attributes
- Statistical Metrics: 100+ individual statistics

## Directory Structure

```
persib-scouting-wyscout/
├── app.py (5,623 lines)           # Main Streamlit application with 5+ pages
├── requirements.txt               # Python dependencies
├── CLAUDE.md                      # Project documentation
│
├── config/                        # Configuration modules (14 files)
│   ├── stat_categories.py         # 100+ stat definitions with indicators
│   ├── composite_attributes.py    # 60+ composite attribute formulas
│   ├── grade_attributes.py        # Grade calculation definitions
│   ├── position_groups.py         # Position grouping and filtering
│   ├── position_rankings.py       # Position-specific attribute priorities
│   ├── league_fit_config.py       # League fit analysis configuration
│   ├── team_analysis_config.py    # Team analysis configuration
│   ├── defender_presets.py        # CB/Fullback tactical profiles
│   ├── fullback_presets.py        # Fullback tactical profiles
│   ├── midfielder_presets.py      # DM/CM tactical profiles
│   ├── attacking_midfielder_presets.py  # AM tactical profiles
│   ├── forward_presets.py         # Winger/Forward/Striker tactical profiles
│   ├── similarity_presets.py      # Similarity matching presets
│   ├── role_definitions.py        # Role definitions
│   └── registry.py               # Component registry
│
├── utils/                         # Utility modules (14 files)
│   ├── data_loader.py            # Core data pipeline and CSV operations
│   ├── column_mapping.py          # CSV compatibility and derived metrics
│   ├── player_comparison.py       # Page 1 visualizations
│   ├── player_finder.py           # Page 2 search logic
│   ├── player_similarity.py       # Page 3 similarity scoring
│   ├── similarity_helpers.py      # Similarity helper functions
│   ├── outlier_detection.py       # Page 5 statistical analysis
│   ├── league_fit.py             # League fit scoring logic
│   ├── regression_analysis.py     # Regression analysis utilities
│   ├── team_data_loader.py       # Team-specific data loading
│   ├── team_aggregator.py        # Team data aggregation
│   ├── team_styles.py            # Team styling utilities
│   └── team_visualizations.py    # Team visualization functions
│
├── team_analysis_app.py           # Separate team analysis application
│
└── data/
    └── 2025/                     # Wyscout CSV exports
        ├── [Multiple League CSVs]
```

## Architecture Overview

### Application Pattern: Multi-Page Streamlit App

The main application (`app.py`) follows a Streamlit multi-page pattern with sidebar navigation:

```
Sidebar (Global Filters)
├── Position Group Selection
├── League Multi-Select
└── Calculate Percentiles/Composites Toggles
    ↓
Data Loading Pipeline (Cached)
    ↓
Page Rendering (5+ Pages)
├── Page 1: Player Comparison
├── Page 2: Player Finder
├── Page 3: Player Similarity
├── Page 4: Scatter Analysis
├── Page 5: Outliers Analysis
├── Page 6: League Fit Analysis
└── Page 7: Grade/Classification
```

### Data Processing Pipeline

```
load_all_data() [Cached, no parameters]
    ↓
    - Loads all CSV files from data/2025/
    - Applies column aliases (Competition → League)
    - Calculates derived metrics
    - Returns raw DataFrame with no percentiles/composites

get_distinct_values()
    ↓
    - Extracts unique leagues and positions
    - Used for UI dropdown population

prepare_filtered_data() [Cached by: leagues_tuple, position_group, calculation flags]
    ↓
    filter_players() [Position + League filtering]
    ↓
    calculate_percentiles() [0-100 scale on filtered subset]
    ↓
    calculate_composite_attributes_batch() [60+ COMP_ attributes]
    calculate_grade_attributes_batch() [Grade attributes]
    ↓
    Returns: Filtered DataFrame with percentiles and composites

render_page() [Page-specific filters: age, minutes, contract]
    ↓
    Apply page-level filters (non-cached)
    ↓
    Display visualizations
```

### Key Design Principles

#### 1. Multi-Tiered Caching Strategy

**Tier 1: Data Loading** (`load_all_data()`)
- Cached with no parameters
- Only loads once per session
- Returns raw data without calculations

**Tier 2: Data Processing** (`prepare_filtered_data()`)
- Cached by filter parameters (leagues_tuple, position_group, calculation flags)
- Recalculates percentiles on filtered subset when filters change
- Ensures fair comparison within the selected dataset

**Tier 3: Page Rendering**
- Page-specific filters (age, minutes, contract) applied after caching
- Simple row filters - no expensive recalculations

**Why tuple for leagues?** Lists are mutable and can't be hashed for caching. Convert to tuple for cache key.

#### 2. Percentile-Based Comparison System

All raw statistics are converted to percentile ranks (0-100 scale) within the filtered dataset.

**Benefits:**
- Fair comparison across different leagues (Serie B vs Premier League)
- Fair comparison across different positions (CB vs DM vs Winger)
- Normalized scale for weighted scoring
- Intuitive interpretation (90th percentile = top 10%)

**Example:**
```
5.0 progressive passes per 90:
- Among CBs: 90th percentile
- Among CMs: 50th percentile
- Among AMs: 30th percentile
```

#### 3. Composite Attributes System

60+ composite attributes are defined in `config/composite_attributes.py` with:
- `display_name`: Human-readable name
- `description`: What the attribute measures
- `archetypes`: Example players who exemplify this attribute
- `components`: List of (stat_name, weight) tuples (negative weights = inverse relationship)
- `icon`: Emoji for visual display

**Example Structure:**
```python
"Security": {
    "display_name": "Security",
    "description": "Retain possession under pressure through passing...",
    "archetypes": ["William Saliba", "Manuel Akanji"],
    "components": [
        {"stat": "Accurate short / medium passes, %", "weight": 0.28, "use_percentile": True},
        {"stat": "Accurate passes, %", "weight": 0.20, "use_percentile": True},
        # ... more components
    ],
    "icon": "🛡️"
}
```

**Calculation Formula:**
```python
composite_value = Σ(percentile(component_stat) * weight)
composite_percentile = percentile(composite_value)  # Re-rank composite
```

#### 4. Role/Preset Profiles

Pre-defined tactical profiles with metric weights for each position type:
- **Purpose**: Codify scout knowledge about what makes a good "Deep-Lying Playmaker" vs "Box-to-Box Midfielder"
- **Storage**: Separate files per position group (`config/midfielder_presets.py`)
- **Usage**: Player Finder page, Role Matching analysis

**Example:**
```python
"Deep-Lying Playmaker": {
    "Progressive passes per 90": 1.2,
    "Passes to final third per 90": 1.0,
    "Forward passes per 90": 0.9,
    # ... 10-20 metrics for comprehensive profile
}
```

## Page Architecture Details

### Page 1: Player Comparison

**Components:**
- Multi-player selection (2-3 players)
- Category-based stat tables (Defensive, Offensive, Progressive, etc.)
- Composite attribute visualizations (radar charts, dot charts)
- Role/preset match scoring
- Color-coded comparison (Green, Blue, Orange)

**Key Functions:**
- `display_player_comparison()` - Side-by-side stat tables with percentile bars
- `display_composite_attributes()` - Radar charts and bar graphs
- `display_attribute_rankings_1d_dot()` - Dot charts on 0-100 scale
- `display_role_preset_match()` - Tactical fit analysis

### Page 2: Player Finder

**Search Types:**
1. **Role-based search**: Use preset tactical profiles (e.g., Ball-Playing CB, Deep-Lying Playmaker)
2. **Responsibility-based search**: Search by specific composite attributes

**Components:**
- Preset selection dropdown
- Advanced filters (age, minutes, contract)
- Adjustable metric weights
- Top N results table with scores

**Key Classes:**
- `DefenderScorer` - Scoring for CB, Fullback positions
- `MidfielderScorer` - Scoring for DM, CM positions
- `ForwardScorer` - Scoring for AM, Winger, Forward, Striker positions

**Scoring Logic:**
```python
weighted_score = Σ(percentile(metric) * weight)
rank by weighted_score, return top N
```

### Page 3: Player Similarity

**Features:**
- Find players similar to reference player
- Multiple similarity methods: Cosine, Euclidean, Pearson
- Weighted similarity calculation
- Metric contribution breakdown
- Composite attribute comparison

**Key Class:**
- `SimilarityScorer` - Main similarity calculation class

**Methods:**
- `calculate_similarity()` - Find most similar players
- Supports league weighting and position filtering

### Page 4: Scatter Analysis

**Features:**
- Interactive scatter plots for metric exploration
- Dual-axis metric selection (100+ stats)
- Color coding options (by position, team, age)
- Interactive point highlighting
- Quadrant analysis
- Export-ready visualizations

**Libraries:**
- Matplotlib for static charts
- Plotly for interactive charts

### Page 5: Outliers Analysis

**Features:**
- Statistical outlier detection for exceptional player identification
- Two methods: Z-Score and IQR
- Single metric focus (clear, interpretable results)
- Both raw stats and composite attributes
- High performers only (positive outliers for talent ID)
- Three-tab results: table, matplotlib figures, interpretation guide

**Key Functions:**
- `detect_outliers_zscore()` - Z-score based detection (threshold = 3.0 = 99.7%)
- `detect_outliers_iqr()` - IQR-based detection (multiplier = 1.5)
- `create_outliers_table_figure()` - Publication-ready matplotlib figures
- `display_outliers_analysis()` - Streamlit interactive table

### Page 6: League Fit Analysis

**Purpose:** Compare source-league players against BRI Liga 1 benchmarks using 11 event-based physical proxy metrics.

**Features:**
- Position-specific weight tables
- Risk classification (Ready/Monitor/Not Ready)
- Benchmark comparison charts
- Fit leaderboard figures
- Player deep-dive analysis

**Key Functions:**
- `compute_target_benchmarks()` - Calculate target league averages
- `compute_source_benchmarks()` - Calculate source league averages
- `compute_fit_scores()` - Calculate similarity scores
- `create_benchmark_comparison_chart()` - Visual comparison
- `create_fit_leaderboard_figure()` - Ranking visualization

### Page 7: Grade/Classification

**Features:**
- Grade calculation based on composite attributes
- Classification by performance tiers
- Team-specific grade analysis

## Configuration System

### Stat Categories (`config/stat_categories.py`)

Defines 6 statistical categories with 100+ metrics:
- **Defensive**: Tackles, interceptions, duels, defensive actions
- **Offensive**: Goals, shots, xG, box entries, dribbles
- **Progressive**: Progressive passes/runs/carries, deep progressions
- **Chance Creation**: Assists, xA, key passes, crosses, smart passes
- **General**: Passes, pass accuracy, ball touches, aerial duels
- **Set Pieces**: Corners, free kicks, throw-ins

**Indicator System:**
- `HIGHER_IS_GOOD` (default): Higher values are better (goals, assists, passes)
- `LOWER_IS_GOOD`: Lower values are better (fouls, cards, conceded goals)

### Position Groups (`config/position_groups.py`)

Maps logical position groups to specific position tags from Wyscout data:
- **CB** → ["CB", "RCB", "LCB", "RCB3", "LCB3"]
- **Fullback** → ["LB", "RB", "LWB", "RWB", "LB5", "RB5"]
- **DM** → ["DMF", "LDMF", "RDMF"]
- **CM** → ["LCMF", "RCMF", "CMF", "LCMF3", "RCMF3"]
- **AM** → ["AMF", "LAMF", "RAMF"]
- **Winger** → ["LW", "RW", "LWF", "RWF"]
- **Forward** → ["CF"]
- **Striker** → ["CF"]

Also includes combined groups:
- "Defender" → CB + Fullback
- "Midfielder" → DM + CM
- "Midfielder_N_AM" → DM + CM + AM
- "Forward" → CF + Winger + AM

## Utility Modules

### Data Loader (`utils/data_loader.py`)

Core data pipeline handling all CSV operations and transformations:

**Key Functions:**
- `load_player_data()` - Load single CSV with UTF-8 BOM encoding
- `load_all_league_data()` - Load and combine all CSV files
- `filter_players()` - Filter by position group and selected leagues
- `calculate_percentiles()` - Convert raw stats to percentile ranks (0-100)
- `calculate_composite_attributes_batch()` - Batch compute all composite attributes
- `calculate_grade_attributes_batch()` - Batch compute grade attributes
- `get_player_info()` - Retrieve player metadata
- `get_player_stats()` - Get raw stats + percentiles for specific player
- `get_player_composite_attrs()` - Get pre-calculated composite attributes

**Implementation Details:**
- UTF-8 BOM encoding (`utf-8-sig`) for CSV files
- Automatic removal of unnamed columns
- Percentile calculation uses `rank(pct=True)` for 0-1 scale, then * 100
- Batch processing for composite attributes (one pass through DataFrame)

### Column Mapping (`utils/column_mapping.py`)

CSV compatibility layer handling schema changes:

**Features:**
- `COLUMN_ALIASES`: Maps old column names to new standardized names
- `calculate_derived_metrics()`: Computes metrics missing from CSV
- Backward compatibility with older data exports

**Example:**
```python
COLUMN_ALIASES = {
    "League": "Competition",
    "Matches played": "Matches",
    # ... many more aliases
}
```

## Technology Stack

### Core Framework
- **Streamlit 1.31.0**: Web UI framework with multi-page support
- **Pandas 2.2.0**: Data manipulation and analysis
- **NumPy 1.26.3**: Numerical computing and array operations

### Visualization
- **Matplotlib 3.8.2**: Static charts and figures
- **Plotly 5.18.0**: Interactive charts
- **Seaborn 0.13.0**: Statistical data visualization
- **Altair 5.0.0**: Declarative visualization (optional)
- **Pillow 10.0.0**: Image processing for team logos

### Machine Learning & Statistics
- **Scikit-learn 1.4.0**: Cosine similarity, clustering algorithms
- **SciPy 1.11.0+**: Statistical functions, Pearson correlation
- **Statsmodels 0.14.0**: Regression analysis, statistical modeling

### External Services
- **Ollama 0.6.1+**: Local LLM integration for AI chatbot
- **ChromaDB 0.4.0+**: Vector database for embeddings
- **Supabase 2.0.0+**: Database integration
- **Requests 2.31.0+**: HTTP client for API calls

### Text Processing
- **Fuzzywuzzy 0.18.0+**: Fuzzy string matching for player names
- **Python-Levenshtein 0.23.0+**: String distance calculations

### Database
- **psycopg2-binary 2.9.9+**: PostgreSQL database adapter
- **python-dotenv 1.0.0+**: Environment variable management

## Data Flow Diagrams

### Main Data Flow

```
CSV Files (data/2025/*.csv)
    ↓
load_all_data() [Cached]
    ↓
    - Apply column aliases
    - Calculate derived metrics
    - Return raw DataFrame
    ↓
prepare_filtered_data() [Cached by filters]
    ↓
    filter_players() [Position + League]
    ↓
    calculate_percentiles() [0-100 scale]
    ↓
    calculate_composite_attributes_batch() [COMP_ prefix]
    ↓
    DataFrame with percentiles and composites
    ↓
Page Rendering (apply page filters)
    ↓
    Visualizations (Matplotlib/Plotly)
```

### Player Finder Flow

```
User selects preset (e.g., "Ball-Playing CB")
    ↓
Load preset metric weights from config
    ↓
Apply filters (age, minutes, contract)
    ↓
Calculate weighted score for each player:
    Σ(percentile(metric) * weight)
    ↓
Sort by weighted score (descending)
    ↓
Return top N results
```

### Similarity Calculation Flow

```
User selects reference player
    ↓
Extract reference player's percentile vector
    ↓
Apply metric weights to create weighted vectors
    ↓
Calculate similarity (cosine/euclidean/pearson)
    ↓
Compute metric-level contribution
    ↓
Rank by similarity score (0-1 scale)
    ↓
Return top N most similar players
```

### Outlier Detection Flow

```
User selects metric and method (Z-score/IQR)
    ↓
Calculate statistics on filtered dataset:
    - Z-score: mean, std
    - IQR: Q1, Q3, IQR
    ↓
Identify outliers based on threshold:
    - Z-score: ±3σ (99.7%)
    - IQR: Q3 + 1.5×IQR
    ↓
Focus on high performers (positive outliers)
    ↓
Sort by outlier score (descending)
    ↓
Return top N exceptional players
```

## Code Organization Patterns

### Separation of Concerns

1. **Configuration** (`config/`): All static data, definitions, and presets
2. **Data Pipeline** (`utils/data_loader.py`): All data loading and processing
3. **Business Logic** (`utils/player_*.py`): Domain-specific algorithms
4. **Visualization** (`utils/*_visualizations.py`): Chart and figure creation
5. **Application** (`app.py`): UI rendering and page orchestration

### Consistent Naming Conventions

- **Files**: `snake_case.py`
- **Functions**: `snake_case()`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Composite Attributes**: `COMP_AttributeName`
- **Grade Attributes**: `GRADE_AttributeName`

### Module Organization

Each module has a single, well-defined responsibility:
- `player_comparison.py` - Only comparison visualizations
- `player_finder.py` - Only finder scoring logic
- `player_similarity.py` - Only similarity algorithms
- `outlier_detection.py` - Only outlier detection

## Deployment Architecture

### Development Mode
```bash
streamlit run app.py
```

### Production Considerations
- Streamlit Community Cloud (recommended for this scale)
- Self-hosted with Nginx/Gunicorn (for custom domains)
- Docker containerization possible (not currently implemented)

### Data Storage
- **CSV Files**: Local file system (`data/2025/`)
- **Caching**: Streamlit's built-in `@st.cache_data`
- **Session State**: Streamlit's built-in `st.session_state`

## Security Considerations

### Current State
- No authentication implemented
- No API rate limiting
- No input validation beyond basic type checking
- No SQL injection risks (uses pandas, not direct SQL)

### Recommendations
- Implement user authentication if deploying publicly
- Add input validation for all user inputs
- Rate limit API calls (if adding external APIs)
- Sanitize file paths when loading CSVs

## Performance Characteristics

### Caching Strategy
- Tier 1: Data loading (once per session)
- Tier 2: Filtered data processing (when filters change)
- Tier 3: Page rendering (no caching, simple filters)

### Optimization Techniques
- Batch processing for composite attributes
- Efficient DataFrame operations (vectorized with pandas)
- Lazy loading (charts only rendered when tab selected)
- Efficient boolean indexing for filtering

### Performance Bottlenecks
- Large CSV files: Initial loading can be slow (10-30 seconds)
- Percentile calculation: O(n log n) on filtered dataset
- Similarity calculation: O(n) for n players
- Scatter plots: Can be slow with large datasets (>10k points)

## Scalability Limitations

### Current Limitations
- **File-based data**: CSVs must fit in memory
- **Client-side rendering**: All processing happens server-side
- **No pagination**: All results displayed at once
- **Single-user model**: Not designed for concurrent users

### Scaling Approaches
- Move to database (PostgreSQL with Supabase integration already started)
- Implement pagination for large result sets
- Add background processing for expensive calculations
- Deploy with horizontal scaling (multiple Streamlit instances)

## Integration Points

### External Data Sources
- **Wyscout**: Primary data source via CSV exports
- **Team logos**: Fetched from external URLs via requests
- **Supabase**: Database integration (partial)

### External Services
- **Ollama**: Local LLM for AI chatbot (separate app)
- **ChromaDB**: Vector database for embeddings (chatbot)

## Future Architecture Considerations

### Potential Enhancements
1. **Database Backend**: Replace CSV-based data with PostgreSQL
2. **API Layer**: Add REST API for external integrations
3. **Authentication**: User authentication and authorization
4. **Multi-tenancy**: Support multiple scouting organizations
5. **Real-time Updates**: Live data feeds from Wyscout API
6. **Microservices**: Separate UI from processing logic
7. **Caching Layer**: Redis for distributed caching

### Technical Debt Areas
1. **Large app.py file**: 5,623 lines - consider splitting into modules
2. **Monolithic architecture**: All pages in single file
3. **No tests**: No automated testing framework
4. **No CI/CD**: Manual deployment process
5. **Hardcoded values**: Some league/team names are hardcoded

## Summary

This is a well-architected, modular Streamlit application with:
- Clear separation of concerns (config, data, logic, visualization)
- Sophisticated data pipeline with multi-tiered caching
- Comprehensive player analysis capabilities (7 pages)
- Extensible configuration system (presets, composite attributes)
- Professional visualization quality (matplotlib, plotly)
- Good performance for single-user use cases

**Strengths:**
- Modular and maintainable codebase
- Flexible configuration system
- Comprehensive feature set
- Professional-grade visualizations

**Areas for Improvement:**
- Large monolithic app.py file
- No automated testing
- No CI/CD pipeline
- Limited scalability for concurrent users
- File-based data storage
