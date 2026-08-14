# K-Means Clustering Feature - User Guide

## Overview
The K-Means Clustering page enables you to identify player archetypes using unsupervised machine learning. Group similar players based on their statistical profiles to discover tactical patterns and player types.

## How to Use

### Step 1: Apply Global Filters (Sidebar)
- **Position Group**: Select the position you want to analyze (e.g., "CM", "CB", "Winger")
- **Leagues**: Choose which leagues to include in the analysis

### Step 2: Configure Page Filters
- **Age Range**: Adjust slider to filter players by age (e.g., 22-35 for prime players)
- **Minimum Minutes**: Set minimum playing time threshold (e.g., 900 minutes)

### Step 3: Select Features for Clustering
**IMPORTANT**: You must select at least 5 features for meaningful clustering.

#### Feature Selection Tips:
- **Mix categories**: Combine defensive, offensive, and technical attributes
- **Use suggested presets**: Click "Suggested Feature Sets" expander for examples:
  - **Defensive-focused**: For CB/DM analysis
  - **Possession-focused**: For CM/Playmaker analysis
  - **Attacking-focused**: For Winger/Forward analysis
  - **All-around**: Mixed positions

#### Example Feature Sets:

**For Central Midfielders:**
- Progressive passes per 90
- Tackles per 90
- Passes per 90
- COMP_Dictating Tempo
- COMP_Destroying
- COMP_Progressive Passing
- COMP_Ball Retention
- Defensive duels per 90

**For Center Backs:**
- Tackles per 90
- Interceptions per 90
- Defensive duels per 90
- COMP_1v1 Defending
- COMP_Aerial Ability
- COMP_Anticipation
- COMP_Progressive Passing
- Accurate passes, %

**For Wingers:**
- Goals per 90
- Shots per 90
- Dribbles per 90
- COMP_Finishing
- COMP_1v1 Ability
- COMP_Movement Off Ball
- COMP_Chance Creation
- xG per 90

### Step 4: Choose Normalization Method
- **StandardScaler** (Recommended): Mean=0, Std=1 - Handles outliers better
- **MinMaxScaler**: Scales to 0-1 range - Easier interpretation

### Step 5: Run Clustering Analysis
Click the **"Run Clustering Analysis"** button to:
1. Prepare data (remove NaN values)
2. Scale features using selected method
3. Calculate elbow plot (WCSS for k=2 to 10)
4. Perform PCA for 2D visualization

### Step 6: Analyze Elbow Plot
The elbow plot shows "Within-Cluster Sum of Squares (WCSS)" vs "Number of Clusters (k)".

**How to interpret:**
- Look for the "elbow" - the point where the curve bends
- Before the elbow: Adding clusters significantly improves fit
- After the elbow: Diminishing returns from additional clusters
- Common k values: 3-6 clusters for most analyses

**Example:**
- If curve bends sharply at k=4, that's your optimal cluster count
- If no clear elbow, try k=5 as a starting point

### Step 7: Select Number of Clusters
Use the slider to adjust k based on the elbow plot. The system will:
- Fit K-Means with your selected k
- Assign each player to a cluster
- Project data to 2D using PCA

### Step 8: Explore Results in 3 Tabs

#### Tab 1: 2D Scatter Plot
**Interactive visualization** showing player clusters in PCA space.

**Features:**
- **Colored circles**: Players (color = cluster assignment)
- **Large crosses**: Cluster centroids (center points)
- **Tooltips**: Hover over points to see player details

**Highlighting Options:**
- **Highlight Team**: Select a club to make their players larger (useful for "where do Barcelona players cluster?")
- **Highlight Player**: Select a player to add red stroke (useful for "which cluster is Messi in?")
- **Interactive zoom/pan**: Click and drag to zoom, scroll to pan

**Use Cases:**
- Identify which cluster your target players belong to
- See if players from the same team cluster together (tactical similarity)
- Find outliers (players far from any centroid)

#### Tab 2: Cluster Statistics
**Quantitative summary** of each cluster.

**Cluster Summary Table:**
- Player Count: Number of players in each cluster
- Average Age: Mean age per cluster
- Average Minutes: Playing time per cluster
- Top 5 Features: Mean values for selected metrics

**Export:** Download CSV for further analysis in Excel/Python

**Player Lists by Cluster:**
- Expandable sections showing all players in each cluster
- Sorted alphabetically for easy lookup
- Includes team, age, position, and top 3 features

**Use Cases:**
- Compare cluster sizes (balanced vs imbalanced clusters)
- Identify "young talent" clusters (low avg age, high performance)
- Export for presentation/reports

#### Tab 3: Interpretation Guide
**Automated characterization** of each cluster based on feature deviations.

**For each cluster:**
- **Higher than average**: Features where cluster exceeds overall mean (strengths)
- **Lower than average**: Features where cluster falls below mean (weaknesses)
- **Example players**: 5 sample players from the cluster

**How to interpret:**
- **Cluster 0**: High "Progressive Passing" (+45%), Low "Tackles" (-30%) → Deep-Lying Playmakers
- **Cluster 1**: High "Tackles" (+60%), High "Defensive Duels" (+50%) → Destroyers
- **Cluster 2**: Balanced stats → All-around midfielders

**Use Cases:**
- Create scouting reports ("Cluster 3 = Box-to-Box profiles")
- Understand tactical archetypes in your dataset
- Identify player development paths (move from Cluster A to Cluster B)

## Example Workflow

### Scenario: Find Central Midfielder Archetypes in Top 5 Leagues

1. **Global Filters** (Sidebar):
   - Position Group: CM
   - Leagues: Premier League, La Liga, Serie A, Bundesliga, Ligue 1

2. **Page Filters**:
   - Age: 22-30
   - Min Minutes: 1200

3. **Feature Selection** (8 features):
   - Progressive passes per 90
   - Tackles per 90
   - Passes per 90
   - COMP_Dictating Tempo
   - COMP_Destroying
   - COMP_Progressive Passing
   - COMP_Ball Retention
   - Defensive duels per 90

4. **Normalization**: StandardScaler

5. **Run Analysis**: Click button → 247 players ready

6. **Elbow Plot**: Shows clear elbow at k=4

7. **Select Clusters**: Set slider to 4

8. **Results**:
   - **Cluster 0**: Deep-Lying Playmakers (Rodri, Busquets) - High passing, low tackles
   - **Cluster 1**: Destroyers (Casemiro, Kante) - High tackles, medium passing
   - **Cluster 2**: Box-to-Box (Goretzka, Barella) - Balanced stats
   - **Cluster 3**: Progressive Carriers (De Jong, Verratti) - High progressive actions

9. **Highlight Team**: Select "Manchester City" → See that their CMs cluster in 0 and 2 (possession-focused)

10. **Export**: Download cluster summary CSV for scouting report

## Tips and Best Practices

### Feature Selection
✅ **DO:**
- Select 5-20 features (sweet spot: 8-12)
- Mix offensive and defensive metrics
- Include both volume (per 90) and efficiency (%) stats
- Use composite attributes for holistic profiles

❌ **DON'T:**
- Use fewer than 5 features (too simplistic)
- Use more than 20 features (overfitting risk)
- Select only similar metrics (e.g., all passing stats)

### Interpreting PCA
- **PC1 + PC2 = 60-80% variance**: Good 2D projection
- **PC1 + PC2 < 50% variance**: Data is high-dimensional, 2D may not capture all patterns
- **PC1 + PC2 > 90% variance**: Data is inherently 2D, excellent projection

### Cluster Count Selection
- **Too few clusters (k=2-3)**: Overly broad archetypes
- **Optimal clusters (k=4-6)**: Specific but generalizable
- **Too many clusters (k=8-10)**: Over-segmentation, less useful

### Common Issues

**Issue**: "Not enough data after removing NaN values"
**Solution**: Select different features with less missing data, or reduce minimum minutes filter

**Issue**: No clear elbow in plot
**Solution**: Try k=5 as default, or use silhouette analysis manually

**Issue**: All players in one cluster
**Solution**: Features may not be discriminative - add more diverse metrics

**Issue**: PCA variance too low (<50%)
**Solution**: Data is high-dimensional - consider adding more features or using 3D visualization

## Advanced Use Cases

### 1. Identify Transfer Targets
- Cluster your squad's players
- Find which cluster has gaps
- Search other leagues for players in that cluster

### 2. Tactical Analysis
- Cluster a specific team's players by position
- Identify if they have consistent playing style (all in 1-2 clusters)
- Compare to rival teams

### 3. Youth Development
- Cluster senior team by position
- Cluster academy players using same features
- Identify which youth players fit senior archetypes

### 4. Opposition Scouting
- Cluster opponent's midfielders
- Identify their tactical setup (e.g., 3 destroyers vs 3 playmakers)
- Plan matchday strategy

## Technical Details

### Algorithms Used
- **K-Means**: Partitioning algorithm that minimizes within-cluster variance
- **PCA**: Dimensionality reduction for visualization
- **StandardScaler**: Z-score normalization (mean=0, std=1)
- **MinMaxScaler**: Min-max normalization (range=0-1)

### Limitations
- K-Means assumes spherical clusters (may not capture complex shapes)
- Sensitive to outliers (use StandardScaler to mitigate)
- Requires manual k selection (elbow method helps)
- 2D PCA may lose information for high-dimensional data

### Future Enhancements (Planned)
- 3D clustering visualization (Plotly 3D scatter)
- Custom cluster naming (save "Cluster 0" as "Deep-Lying Playmakers")
- Silhouette score for automatic k selection
- Cluster stability analysis
- Heatmap comparison of cluster centroids

## Support

For issues or feature requests, refer to the main application documentation or contact the development team.
