# RESEARCH.md - Darfat Scouting Hub

## Executive Summary

The Darfat Scouting Hub is a mature, production-ready Streamlit application for football player analysis using Wyscout data. The project is currently on the `feature/app-v5` branch with recent refactoring that removed auxiliary modules (chatbot, scraper, scripts) to focus on the core scouting platform.

**Key Findings:**
- 8-page comprehensive scouting application with 5,623 lines of code
- 60+ composite attributes calculated from 100+ statistical metrics
- Support for 8 position groups and multiple Southeast Asian leagues
- Advanced features: K-means clustering, regression analysis, league fit analysis
- Production-ready with modular configuration system

---

## Architecture Analysis

### Core Technology
- **Frontend:** Streamlit 1.31.0 (single-page application pattern)
- **Data Processing:** Pandas 2.2.0, NumPy 1.26.3
- **Visualization:** Matplotlib 3.8.2, Plotly 5.18.0, Altair 5.0.0
- **ML/Statistics:** Scikit-learn 1.4.0, Statsmodels 0.14.0, SciPy 1.11.0

### Application Structure
The application follows a clean separation of concerns:

1. **Configuration Layer** (`config/`): Declarative data definitions
   - Stat categories, composite attributes, role presets
   - Position mappings and rankings
   - League-specific configurations

2. **Business Logic Layer** (`utils/`): Core functionality
   - Data loading and processing pipeline
   - Page-specific logic (comparison, finder, similarity, etc.)
   - Visualization functions

3. **Presentation Layer** (`app.py`): Streamlit UI
   - Page routing and rendering
   - User input handling
   - Global filter management

### Key Design Patterns

#### Percentile-Based Normalization
- All raw stats converted to 0-100 percentile scale
- Percentiles calculated within filtered dataset
- Enables fair comparison across leagues and positions

#### Multi-Tiered Caching
- Tier 1: Raw data load (cached once per session)
- Tier 2: Filtered data with percentiles (cached by filters)
- Optimal performance for interactive use

#### Composite Attribute System
- 60+ weighted attributes calculated from raw stats
- Position-specific formulas (e.g., "Progressive Passing" weights different stats for CB vs AM)
- Stored as percentiles for consistent comparison

---

## Feature Analysis

### Current Features (8 Pages)

| Page | Purpose | Key Capabilities | Complexity |
|------|---------|------------------|------------|
| Player Comparison | Side-by-side player analysis | Multi-player stat tables, radar charts, role matching | High |
| Player Finder | Role-based player search | Preset profiles, weighted scoring, custom presets | High |
| Player Similarity | Find similar players | Cosine similarity, weighted metrics, contribution analysis | High |
| Scatter Analysis | Explore metric relationships | Interactive charts, quadrant analysis, highlighting | Medium |
| Outliers Analysis | Identify exceptional performers | Z-score & IQR methods, statistical interpretation | Medium |
| K-Means Clustering | Identify player archetypes | Configurable clusters, PCA visualization, profiling | Medium |
| League Fit | Physical compatibility assessment | 11 physical proxy metrics, risk classification | High |
| Regression Analysis | Statistical modeling | OLS & Poisson regression, correlation, VIF analysis | High |

### Configuration System

#### Stat Categories (6 categories, 100+ metrics)
- **Defensive (15 metrics):** Tackles, interceptions, duels, fouls, cards
- **Offensive (22 metrics):** Goals, shots, xG, dribbles, touches
- **Progressive (12 metrics):** Passes, progressive passes, accuracy
- **Chance Creation (21 metrics):** Assists, key passes, crosses, smart passes
- **General (10 metrics):** Matches, minutes, xG against, cards
- **Set Pieces (4 metrics):** Free kicks, corners

#### Composite Attributes (60+ attributes)
Organized by position type with:
- Defenders: 7+ attributes (Security, Aerial Ability, 1v1 Defending, etc.)
- DM/CM: 8+ attributes (Destroying, Dictating Tempo, Box-to-Box, etc.)
- AM/Wingers: 6+ attributes (Finishing, 1v1 Ability, Chance Creation, etc.)
- Fullbacks: 6+ attributes (Overlapping, Underlapping, Crossing, etc.)
- Forwards: 6+ attributes (Clinical Finishing, Poaching, Hold-up Play, etc.)

#### Role Presets
- **Defenders:** Ball-Playing CB, Stopper, Modern CB, etc.
- **Midfielders:** Deep-Lying Playmaker, Box-to-Box, Destroyer, Regista
- **Attacking:** Classic 10, Inside Forward, Wide Playmaker
- **Fullbacks:** Attacking FB, Defensive FB, Inverted FB
- **Forwards:** Complete Forward, Poacher, False 9

---

## Data Pipeline

### Data Flow
```
CSV Files (data/2025/)
    ↓
load_all_data() - Load and combine CSVs
    ↓
get_distinct_values() - Extract leagues/positions
    ↓
prepare_filtered_data() - Filter + calculate percentiles + composites
    ↓
render_page() - Page-specific logic and visualization
```

### Data Sources
- **Primary:** Wyscout API exports (CSV format)
- **Current Coverage:** 6 Southeast Asian leagues (2025-2026 season)
- **Encoding:** UTF-8 BOM
- **Volume:** ~10,000+ players across all leagues

### Data Quality
- Standardized column names via `column_mapping.py`
- Backward compatibility with older Wyscout exports
- Graceful handling of missing data (NaN values excluded from calculations)

---

## Recent Changes Analysis

### Deleted Files (Major Refactoring)
**Interpretation:** The project is being streamlined to focus on core scouting functionality.

| Module | Purpose | Reason for Removal |
|--------|---------|-------------------|
| `chatbot/` | RAG-powered AI assistant | Not production-ready, too experimental |
| `scrapperfc/` | Wyscout data scraper | Redundant with manual CSV exports |
| `scripts/` | Utility scripts (sync, tests) | Not core to main application |
| `app_db.py` | Database integration | Not currently used |

### Modified Files
- `.claude/settings.local.json` - Claude Code configuration
- `data/2025/BRI Liga 1 25-26.csv` - Updated league data

### New Data (2025 Season)
- Thai League 1 25-26
- Malaysian Super League 25-26
- Singapore Premier League 25-26
- Cambodian Premier League 25-26
- V.League 1 25-26

**Conclusion:** Focus shifted to Southeast Asian markets, particularly for Persib (Indonesian team) scouting.

---

## Technical Debt & Limitations

### Known Issues
1. **No Authentication:** Single-user application, no access control
2. **Static Data:** Manual CSV updates required
3. **Memory Usage:** Large datasets may cause issues
4. **Browser Compatibility:** Limited testing on Safari/Edge

### Potential Improvements
1. **Database Integration:** Replace CSV files with persistent database
2. **API Integration:** Direct Wyscout API connection for real-time data
3. **Multi-User Support:** Authentication and user-specific data
4. **Export Features:** PDF reports, CSV exports with custom selections
5. **Watchlist:** Track players of interest over time

---

## Competitive Analysis

### Similar Tools
- **Wyscout Platform:** Official platform with video integration
- **Instat:** Video + stats platform
- **Transfermarkt:** Player database with market values
- **StatsBomb:** Advanced analytics platform

### Differentiators
- **Open Source:** Customizable and extensible
- **Southeast Asian Focus:** Specialized for regional leagues
- **Composite Attributes:** Unique weighted attribute system
- **League Fit Analysis:** Physical compatibility assessment
- **Free/Low Cost:** No subscription required (only Wyscout data)

---

## User Personas

### Primary Users
1. **Football Scout:** Identify players matching specific tactical profiles
2. **Data Analyst:** Analyze player performance across leagues
3. **Club Manager:** Make data-driven acquisition decisions
4. **Coach:** Evaluate players for specific roles in the team

### User Needs
- Fast, intuitive player search and comparison
- Role-based identification (e.g., "Find a deep-lying playmaker")
- Visual understanding of player strengths/weaknesses
- League compatibility assessment (can player adapt to target league?)
- Export capabilities for presentations and reports

---

## Success Metrics

### Performance Metrics
- Data loading: < 10 seconds for 10,000+ players
- Page navigation: < 2 seconds (with caching)
- Support for 20+ leagues
- 99.9% uptime for production

### Business Metrics
- Scout time saved: 50%+ reduction in manual research
- Player discovery: Identify players that traditional scouting misses
- Decision quality: Data-supported acquisition decisions
- User adoption: Regular use by scouting team

---

## Recommendations

### Immediate Priorities (v5.1)
1. **Stabilize Current Branch:** Complete refactoring, remove deleted file references
2. **Add Data Validation:** Ensure all 2025 league CSVs work correctly
3. **Performance Testing:** Test with 20,000+ players
4. **Documentation:** User guide for non-technical scouts

### Short-Term (v5.2 - v5.3)
1. **Export Features:** CSV export with custom column selection
2. **Player Reports:** PDF generation for player profiles
3. **Watchlist Management:** Track and compare selected players
4. **Data Refresh:** Automated data update pipeline

### Long-Term (v6.0+)
1. **Multi-User Authentication:** User accounts and access control
2. **Database Integration:** PostgreSQL/Supabase for persistent data
3. **Real-Time API:** Direct Wyscout integration
4. **AI Chatbot:** Rebuild with production-ready architecture
5. **Mobile Optimization:** Responsive design for tablets/phones

---

## Conclusion

The Darfat Scouting Hub is a well-architected, feature-rich application with a solid foundation for professional player scouting. The codebase is modular, extensible, and follows best practices for data analysis applications.

**Key Strengths:**
- Comprehensive 8-page analysis suite
- Sophisticated composite attribute system
- Flexible configuration (presets, weights, filters)
- Production-ready with caching optimization

**Key Opportunities:**
- Streamline and complete the refactoring
- Add user-friendly export features
- Implement multi-user support
- Build automated data pipeline

**Recommendation:** Continue on `feature/app-v5` branch with focus on stabilization and incremental improvements before major new features.

---

*Research completed: 2026-02-28*
*Researcher: GSD Research Agent*
