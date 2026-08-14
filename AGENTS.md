# AGENTS.md

This file provides guidance to agentic coding agents working in this repository.

## Build and Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit application
streamlit run app.py

# Run example scripts
streamlit run examples/player_screener.py
streamlit run examples/profile_finder.py
streamlit run examples/scatter_analysis.py
```

**Note**: This project does not have a formal test suite. Run the application manually and verify functionality after changes.

## Code Style Guidelines

### Import Organization
- Standard library imports first (os, glob, re)
- Third-party imports second (pandas, numpy, streamlit, matplotlib, sklearn)
- Local imports third (from config.*, from utils.*)
- Group imports logically with blank lines between sections

### Naming Conventions
- **Functions**: `snake_case` - `load_player_data`, `calculate_percentiles`, `filter_players`
- **Classes**: `PascalCase` - `SimilarityScorer`, `DefenderScorer`
- **Constants**: `UPPER_SNAKE_CASE` - `STAT_CATEGORIES`, `COMPOSITE_ATTRIBUTES`, `PLAYER_COLORS`
- **Variables**: `snake_case` - `df_filtered`, `player_name`, `stat_columns`
- **Private methods**: `_prefix` - `_normalize_values` (rarely used)

### Type Hints
- Use type hints for function signatures (optional but encouraged)
- Import from `typing` module: `Dict`, `List`, `Tuple`, `Optional`
- Example: `def load_player_data(csv_path: str) -> pd.DataFrame:`

### Formatting
- 4 spaces for indentation (no tabs)
- Line length: 88-120 characters (follow existing patterns)
- Blank line between functions
- Docstrings for all public functions using Google-style format

### Error Handling
- Raise `ValueError` for invalid inputs or missing data
- Use try-except blocks for CSV loading with informative error messages
- Handle NaN values gracefully in data processing (default to 50 for percentiles, 0 for raw values)
- Example: `raise ValueError(f"Player '{name}' not found")`

### Docstring Format
```python
def function_name(arg1: type, arg2: type) -> return_type:
    """
    Brief description of what the function does

    Args:
        arg1: Description of first argument
        arg2: Description of second argument

    Returns:
        Description of return value

    Raises:
        ValueError: When and why this error occurs
    """
```

### DataFrame Handling
- Always work on copies to avoid mutation: `df_copy = df.copy()`
- Use `.iloc[0]` to get single rows from filtering operations
- Check column existence before accessing: `if col in df.columns`
- Handle NaN values: `pd.isna(value)`, `np.nan_to_num(values, 0)`

### Streamlit Best Practices
- Use `@st.cache_data` for expensive data loading operations
- Use unique `key` parameters for all interactive widgets
- Avoid `st.experimental_rerun()` - prefer `st.rerun()`
- Use `st.columns()` for layout, `st.tabs()` for organizing related content
- Set consistent background color: `#f5f3e8` (cream)

### Configuration Structure
- `config/stat_categories.py`: Define all statistical categories
- `config/composite_attributes.py`: Define weighted attribute formulas
- `config/position_rankings.py`: Map positions to key attributes
- `config/position_groups.py`: Define position filtering groups
- All configs use dictionary-based structures with descriptive keys

### Data Processing Patterns
- Calculate percentiles globally (across all leagues) for fair comparison
- Normalize values to 0-100 scale when combining metrics
- Handle negative metrics (lower is better) by inverting normalization
- Use `pct=True` in `df.rank()` for percentile calculations

### Visualization
- Matplotlib for static charts with consistent styling
- Plotly for interactive charts with hover information
- Fixed color scheme: Green (#2ecc71), Blue (#3498db), Orange (#e67e22)
- Background color: #f5f3e8
- Always close matplotlib figures: `plt.close(fig)`

### Adding New Features
1. **New statistics**: Add to `config/stat_categories.py`
2. **New composite attributes**: Add to `config/composite_attributes.py`
3. **New position groups**: Add to `config/position_groups.py`
4. **New position rankings**: Add to `config/position_rankings.py`
5. Follow existing patterns in utility modules

### File Naming
- Utility functions: `utils/function_name.py`
- Configuration: `config/category_name.py`
- Examples: `examples/description.py`
- Keep filenames descriptive and in snake_case

### Session State Management
- Use `st.session_state` for persisting data across interactions
- Initialize session state with `if 'key' not in st.session_state:`
- Clear session state when needed: `del st.session_state['key']`

### Performance Considerations
- Cache data loading with `@st.cache_data`
- Use vectorized pandas operations instead of loops
- Batch calculate composite attributes rather than per-player
- Limit results to top N (typically 30) for display

### CSV Data Conventions
- Encoding: `utf-8-sig` to handle BOM
- First unnamed column automatically removed
- Required columns: Player, Age, Team, Position, Birth country
- Statistics stored as numeric values (not percentages with %)
