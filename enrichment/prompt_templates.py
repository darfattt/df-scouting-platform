"""
Prompt Templates - Structured prompts for Gemini AI analyst
All statistics are pre-computed by Python/ML. The LLM writes narrative ONLY.
"""

from typing import Dict, List, Optional


def build_player_scouting_prompt(
    player_name: str,
    position: str,
    team: str,
    league: str,
    age: Optional[int],
    performance_tier: str,
    composite_score: float,
    composite_percentile: float,
    key_stats: Dict[str, float],
    shap_top_features: Optional[List[Dict]] = None,
    position_group: str = "Unknown",
    best_role: Optional[str] = None,
    top_archetypes: Optional[List[str]] = None,
    target_league: Optional[str] = None,
) -> str:
    """
    Build a structured scouting report prompt for Gemini.
    All numbers are pre-computed; Gemini only writes narrative.

    Args:
        player_name: Full player name
        position: Player position
        team: Current club
        league: Current league
        age: Player age
        performance_tier: Elite / Good / Average / Below Average
        composite_score: 0-100 composite performance score
        composite_percentile: Percentile rank in dataset
        key_stats: Dict of stat_name -> value for all available ML features
        shap_top_features: List of {feature, shap_value, feature_value} dicts (from SHAP)
        position_group: Position group filter applied (e.g. "Midfielder")

    Returns:
        Prompt string ready for Gemini
    """
    age_str = f"{age} years old" if age else "age unknown"

    # Format key stats table
    stats_lines = []
    for stat_name, value in key_stats.items():
        if value is not None and str(value) != "nan":
            stats_lines.append(f"  - {stat_name}: {value:.2f}")
    stats_block = "\n".join(stats_lines) if stats_lines else "  - No per-90 stats available"

    # Format SHAP insights
    shap_block = ""
    if shap_top_features:
        shap_lines = []
        for item in shap_top_features[:5]:
            direction = "positively" if item["shap_value"] > 0 else "negatively"
            shap_lines.append(
                f"  - {item['feature']} (value: {item['feature_value']:.2f}) → {direction} impacts prediction"
            )
        shap_block = "\nKey ML Explainability (SHAP — what drives this tier prediction):\n" + "\n".join(shap_lines)

    # Benchmark-league note (computed outside the f-string because Python 3.10 disallows backslashes in f-string expressions)
    benchmark_block = ""
    if target_league:
        benchmark_block = (
            f"\nBenchmark League: tier and z-score above are computed relative to "
            f"{target_league}. Frame the verdict as fit for this league."
        )

    prompt = f"""You are an expert football scout and analyst at a professional club.
Write a concise, professional SCOUTING REPORT for the player below.

IMPORTANT RULES:
- You MUST base all analysis ONLY on the statistics provided. Do NOT invent statistics.
- Write in professional scouting language (concise, actionable, specific).
- Structure the report with clear sections.
- **IMPORTANT**: Mention the player's current **Club** and **Position** naturally within the "Overall Assessment" narrative.
- Do not add commentary unrelated to the data provided.
- Avoid generic filler sentences. Be specific and direct.

=== PLAYER PROFILE ===
Name: {player_name}
Age: {age_str}
Position: {position}
Club: {team}
League: {league}
Position Group: {position_group}

=== PERFORMANCE ASSESSMENT ===
ML Performance Tier: {performance_tier}
Composite Score: {composite_score:.1f}/100 (Top {100 - composite_percentile:.0f}% of dataset){benchmark_block}

=== STATISTICAL PROFILE (per 90 minutes) ===
{stats_block}
{shap_block}

=== SCOUTING REPORT FORMAT (use these exact sections) ===

**Overall Assessment**
[2-3 sentences on overall profile and performance tier justification]

**Defensive Contribution**
[Analysis of defensive duels, interceptions, tackles, and successful defensive actions. Particularly critical for Defenders, Fullbacks, and DMs.]

**Physical & Aerial Presence**
[Comment on aerial duels, accelerations, offensive duels if data available]

**Technical & Creative Play**
[Analysis of key passes, progressive runs, shot assists, crosses, smart passes]

**Attacking Contribution**
[Specific analysis of offensive stats — goals, assists, xG, dribbles, touches in box, etc.]

**Tactical Role & Best Fit**
[Analysis based on the player's **Best Role**: {best_role if best_role else 'N/A'}. How do they fit this role? Mention the player's **Top 5 Archetypes** (highest statistical scores): {', '.join(top_archetypes) if top_archetypes else 'N/A'}.]

**Scouting Verdict**
[Recommendation: suitable for what type of team/system? Transfer interest level? Age + tier context?]

**Flags / Watch Points**
[Any statistical weaknesses or caveats visible in the data]

Write the report now:"""

    return prompt


def build_quick_summary_prompt(
    player_name: str,
    tier: str,
    top_stats: Dict[str, float],
) -> str:
    """
    Build a short 2-sentence summary prompt for quick insights.

    Args:
        player_name: Player name
        tier: Performance tier
        top_stats: Top 3-5 stats

    Returns:
        Short prompt for quick AI summary
    """
    stats_str = ", ".join([f"{k}: {v:.2f}" for k, v in top_stats.items()])
    return f"""In exactly 2 sentences, summarize {player_name}'s profile.
Tier: {tier}. Key stats: {stats_str}.
Be direct and specific. Do not use filler language."""

def build_team_gap_prompt(
    target_team: str,
    benchmark_teams: List[str],
    gaps_text: str,
    position_group_gaps: Optional[List[Dict]] = None,
    archetype_gaps: Optional[List[Dict]] = None,
    attribute_gaps: Optional[List[Dict]] = None,
) -> str:
    """
    Build a structured prompt evaluating team tactical gaps with full position-group context.

    Args:
        target_team: The team being analysed
        benchmark_teams: Teams used as benchmarks
        gaps_text: Legacy free-text gap summary (used as fallback)
        position_group_gaps: List of dicts with keys:
            position_group, your_count, bench_avg_count, delta
        archetype_gaps: List of dicts (one per position group, sorted by priority desc) with keys:
            position_group, archetypes (List[str] display names), yours, bench_avg, gap,
            your_quality, bench_quality, priority
        attribute_gaps: List of dicts with keys:
            position_group, responsibility (display name), your_avg, bench_avg, gap

    Returns:
        Prompt string ready for the AI model
    """
    benchmarks_str = ", ".join(benchmark_teams)

    # --- Build Position Group Count Block ---
    pos_group_block = ""
    if position_group_gaps:
        lines = ["Position Group | Your Squad | Bench Avg | Δ Gap"]
        lines.append("-" * 55)
        for item in position_group_gaps:
            delta = item.get("delta", 0)
            sign = "▲" if delta > 0 else ("▼" if delta < 0 else "═")
            lines.append(
                f"  {item['position_group']:<12} | "
                f"{item['your_count']:<10} | "
                f"{item['bench_avg_count']:<9.1f} | "
                f"{sign} {abs(delta):.1f}"
            )
        pos_group_block = "\n".join(lines)

    # --- Build Ranked Archetype Gap Block ---
    # archetype_gaps is now grouped: one entry per position group, archetypes = list
    archetype_block = ""
    if archetype_gaps:
        lines = [
            "Rank | Position Group | Missing Archetypes                    | Bench Avg | Priority"
        ]
        lines.append("-" * 90)
        for rank, item in enumerate(archetype_gaps[:10], 1):
            archs = item.get("archetypes", [item.get("archetype", "?")])
            archs_str = ", ".join(archs)
            lines.append(
                f"  #{rank:<4} | {item['position_group']:<14} | {archs_str:<38} | "
                f"{item.get('bench_avg', 0):<9.1f} | {item.get('priority', 0):.1f}"
            )
        archetype_block = "\n".join(lines)

    # --- Build Attribute Gap Block ---
    attr_block = ""
    if attribute_gaps:
        lines = ["Position Group | Responsibility           | Your Avg | Bench Avg | Gap"]
        lines.append("-" * 70)
        for item in attribute_gaps:
            lines.append(
                f"  {item['position_group']:<14} | {item['responsibility']:<25} | "
                f"{item.get('your_avg', 0):<8.1f} | {item.get('bench_avg', 0):<9.1f} | "
                f"{item.get('gap', 0):.1f}"
            )
        attr_block = "\n".join(lines)

    # --- Compose the prompt ---
    sections = [
        "You are an expert Chief Scout and Director of Football.",
        f"Write a concise, actionable SCOUTING RECOMMENDATION REPORT for **{target_team}**.",
        "",
        "IMPORTANT RULES:",
        "- All numbers below are pre-computed from real match data. Do NOT invent statistics.",
        f"- The benchmark teams are: {benchmarks_str}.",
        "- Each recruitment priority is ONE position group. If a group has multiple missing archetypes, list them together under one priority number.",
        "- Use the archetype display names exactly as given (e.g. \"Ball Winning\", \"Prog. Pass\", \"Box Presence\").",
        "- Estimate a realistic Market Value Range (€) for each priority.",
        "- Be direct, specific, and actionable.",
        "",
        "=== SQUAD GAP ANALYSIS ===",
        f"Target Team : {target_team}",
        f"Benchmark   : {benchmarks_str}",
    ]

    if pos_group_block:
        sections += ["", "--- POSITION GROUP HEADCOUNT vs BENCHMARK ---", pos_group_block]

    if archetype_block:
        sections += ["", "--- RANKED ARCHETYPE GAPS (one row per position group, sorted by priority) ---", archetype_block]
    elif gaps_text:
        sections += ["", "--- ATTRIBUTE GAPS PER POSITION GROUP ---", gaps_text]

    if attr_block:
        sections += ["", "--- ATTRIBUTE / RESPONSIBILITY DEFICIENCIES PER POSITION GROUP ---", attr_block]

    sections += [
        "",
        "=== REPORT FORMAT ===",
        "Use EXACTLY these section headers and the structure below. Separate each priority block with a blank line.",
        "",
        "### 🔴 TOP RECRUITMENT PRIORITIES",
        "",
        "For each priority write:",
        "  **#N Priority — [Position Group]: [Archetype 1], [Archetype 2]**",
        "  (blank line)",
        "  - **Why it matters:** [1-2 sentences tactical impact vs benchmarks]",
        "  - **Ideal profile:** [specific role/style]",
        "  - **Estimated market value:** [€X – €Y, with brief justification]",
        "  (blank line before next priority)",
        "",
        "List exactly 3 priorities (or fewer if fewer gaps exist).",
        "",
        "### 📊 ATTRIBUTE DEFICIENCY SUMMARY",
        "",
        "For each position group with an attribute gap, one bullet:",
        "  - [Position Group] – [Responsibility] ([your_avg] vs [bench_avg]): [1-sentence consequence]",
        "",
        "### 🎯 SCOUTING DIRECTIVE",
        "",
        "One bold paragraph (≤ 3 sentences). State: which position to target first, what archetype/profile",
        "to filter for, and a concrete data threshold (e.g. top 25% in Ball Winning score).",
        "",
        "Write the report now:",
    ]

    return "\n".join(sections)


def build_league_fit_prompt(
    player_name: str,
    position: str,
    team: str,
    source_league: str,
    target_league: str,
    fit_score: float,
    risk_label: str,
    position_group: str,
    metric_details: List[Dict],
    above_avg_count: int,
    below_avg_count: int,
) -> str:
    """
    Build a league fit adaptation report prompt.
    All numbers are pre-computed; the LLM writes narrative only.

    Args:
        player_name: Full player name
        position: Player's position string
        team: Current club
        source_league: League the player currently plays in
        target_league: League we are evaluating fit against
        fit_score: 0-100 league fit score
        risk_label: 'Ready' | 'Monitor' | 'Risk'
        position_group: Position group used for weighting
        metric_details: List of dicts with keys:
            metric_display, player_val, league_mean, league_std, z_score, weight
        above_avg_count: Number of metrics where player is above league mean
        below_avg_count: Number of metrics where player is below league mean

    Returns:
        Prompt string ready for the AI model
    """
    # Format metric table
    metric_lines = []
    for m in metric_details:
        z = m.get("z_score", 0.0)
        direction = "▲ above" if z >= 0 else "▼ below"
        gap = abs(z)
        metric_lines.append(
            f"  - {m['metric_display']}: player={m['player_val']:.2f} | "
            f"{target_league} avg={m['league_mean']:.2f} | "
            f"z={z:+.2f} ({direction} avg by {gap:.2f} std, weight={m['weight']:.1f})"
        )
    metric_block = "\n".join(metric_lines) if metric_lines else "  - No metrics available"

    # Identify biggest strengths and gaps
    sorted_metrics = sorted(metric_details, key=lambda x: x.get("z_score", 0), reverse=True)
    top_strengths = [m["metric_display"] for m in sorted_metrics[:3] if m.get("z_score", 0) >= 0]
    top_risks = [m["metric_display"] for m in sorted_metrics[-3:] if m.get("z_score", 0) < 0]

    strengths_str = ", ".join(top_strengths) if top_strengths else "None clearly above average"
    risks_str = ", ".join(reversed(top_risks)) if top_risks else "No significant weaknesses detected"

    prompt = f"""You are an expert football scout and Director of Football writing a LEAGUE ADAPTATION REPORT.

IMPORTANT RULES:
- Base ALL analysis ONLY on the statistics provided below. Do NOT invent numbers.
- Write in professional scouting language: concise, direct, actionable.
- Structure the report with the exact sections below.
- The fit score is 0-100; higher = better physical/tactical match to the target league.
- Risk labels: "Ready" (≥60), "Monitor" (45-59), "Risk" (<45).
- Do not use generic filler sentences.

=== PLAYER PROFILE ===
Name: {player_name}
Position: {position} ({position_group})
Current Club: {team}
Source League: {source_league}
Target League: {target_league}

=== LEAGUE FIT ASSESSMENT ===
Fit Score: {fit_score:.1f}/100
Adaptation Risk: {risk_label}
Metrics above {target_league} avg: {above_avg_count}
Metrics below {target_league} avg: {below_avg_count}

Top Physical Strengths (vs {target_league}): {strengths_str}
Main Adaptation Risks: {risks_str}

=== METRIC BREAKDOWN (per 90 min vs {target_league} baseline) ===
[metric | player value | league avg | z-score | weight]
{metric_block}

=== REPORT FORMAT (use exact section headers) ===

**Adaptation Summary**
[2-3 sentences. State the fit score, risk label, and overall suitability for {target_league}. Mention source vs target league context.]

**Physical Strengths vs {target_league}**
[Which metrics is the player clearly above the {target_league} average? What tactical advantage does this provide?]

**Adaptation Risks & Gaps**
[Which metrics are significantly below the {target_league} average (z < -0.5)? What is the practical consequence on the pitch?]

**Position-Specific Assessment**
[For a {position_group}, which of the weighted metrics matter most? Does this player's profile align with what {target_league} {position_group}s typically require?]

**Transfer Recommendation**
[Is this player recommended for transfer to {target_league}? State: Ready (sign now) / Monitor (6-month loan) / Risk (needs specific system). Be decisive.]

**Scout's Watch Points**
[1-3 bullet flags — specific metrics or patterns that scouts should track in video analysis before final decision]

Write the report now:"""

    return prompt
