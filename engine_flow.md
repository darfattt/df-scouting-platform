# Smart Scout Engine — Architecture & Flow

This document explains how the Smart Scout engine is built and how data flows through it, end to end. It describes the moving parts in plain terms — no code required.

---

## 1. The Big Picture

The engine takes raw player data and turns it into a ranked shortlist of standout players, each with an AI scouting report and a league-relative benchmark. It does this through four cooperating stages:

```
   Wyscout player data (filtered in the app)
                │
                ▼
   ┌─────────────────────────────┐
   │  1. DATA PIPELINE            │   Clean & prepare the data
   │     Bronze → Silver → Gold   │
   └─────────────────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │  2. ML MODEL                 │   Learn & rank performance tiers
   │     (XGBoost classifier)     │
   └─────────────────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │  3. BENCHMARKING             │   Re-judge against a chosen league
   │     (league re-baselining)   │
   └─────────────────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │  4. AI ANALYST               │   Explain the standouts in words
   │     (scouting reports)       │
   └─────────────────────────────┘
                │
                ▼
   Ranked shortlist + reports + charts
```

Each stage hands its output to the next. The stages are also independent enough that the engine can save its work at every step and re-use it later, instead of recomputing everything each time.

---

## 2. The Architecture, Stage by Stage

### Stage 1 — Data Pipeline (Bronze → Silver → Gold)

The engine borrows a well-known data-engineering pattern called a **medallion architecture**. Data passes through three layers, getting cleaner and more useful at each step. Each layer is saved to disk so it can be inspected or reused.

- **Bronze — the raw snapshot.**
  An exact, untouched copy of the player data as it was filtered in the app. It is timestamped and never modified, so there's always a faithful record of what went in. No calculations happen here.

- **Silver — the cleaned and enriched data.**
  This layer tidies everything up: it makes sure every statistic is a proper number, fills in missing values with sensible defaults, and derives "per 90 minutes" stats where they're missing so players with different playing time can be compared fairly. It also adds a "compared to teammates" measure for each stat, giving a sense of how a player rates relative to their own team.

- **Gold — the decision-ready data.**
  This is where raw numbers become judgments. For each player, the engine builds a single **composite score** by ranking them against everyone else on the statistics that matter *for their position* (a centre-back is judged on defensive and aerial metrics, a striker on shooting and box presence, and so on). From that score it assigns a **performance tier**:
  - **Elite** — top 10%
  - **Good** — next 20% (top 10–30%)
  - **Average** — middle (30–70%)
  - **Below Average** — bottom 30%

  It also records where each player ranks within their position and within their league.

### Stage 2 — ML Model (learning the patterns)

The Gold layer already labels players by tier using straightforward ranking rules. The machine-learning model's job is to **learn the relationship** between a player's underlying stats and those tiers, so it can score players consistently and reveal *which stats drive* a verdict.

- The model is an **XGBoost classifier** — a robust, industry-standard algorithm for this kind of "sort into categories" task.
- It trains on the Gold data, learning to predict a player's tier (Elite / Good / Average / Below Average) from their chosen performance stats.
- Its reliability is checked with **cross-validation** (the data is split into folds, training on some and testing on the rest) so the accuracy figure reflects real generalization rather than memorization.
- A trained model is **saved with a nickname** so different feature setups can coexist. The Smart Scout always retrains a fresh model (nicknamed "dynamic") whenever the user changes which stats to analyze, keeping the model in sync with the question being asked.
- For transparency, the engine can produce an **explainability breakdown** that shows which statistics pushed a particular player toward their predicted tier.

### Stage 3 — Benchmarking (league re-baselining)

A player who looks "Elite" globally may only be "Good" against a top league — and vice versa. After the model predicts tiers, the engine can **re-judge every player against one chosen target league** (for example, BRI Liga 1):

- It keeps the original global verdict *and* the new league-relative verdict side by side.
- It re-measures how far above or below that league's average each player sits.
- If the chosen league has too few players to judge fairly, it safely falls back to the global standard and says so.

### Stage 4 — AI Analyst (turning numbers into narrative)

For any shortlisted player, the engine assembles the player's key stats, best tactical role, and standout qualities into a structured prompt and asks a large language model to write a scouting report.

- It uses **Groq as the primary AI provider**, with **Gemini as an automatic fallback** if Groq is unavailable or fails.
- The report is written in the voice of a professional scout and reflects the league-relative context.
- This stage is optional — if no AI provider is configured, the rest of the engine still works fully.

---

## 3. The End-to-End Flow

Here's what happens, in order, when a user runs the Smart Scout:

1. **Set the starting point.**
   The user picks a minimum minutes-played threshold (to exclude tiny sample sizes) and a target league to benchmark against.

2. **Choose the focus.**
   The user selects what kind of quality to scout for — individual stats, broader playing qualities, or skill grades. This sets the analytical lens and the table's sort order.

3. **Auto-prepare the inputs.**
   Based on that choice, the engine automatically gathers the related statistics it needs to train the model, so the user doesn't have to configure it by hand.

4. **Run the pipeline.**
   The filtered data flows through Bronze → Silver → Gold. A progress indicator tracks each layer. If too few players remain after filtering, the engine asks the user to loosen the threshold.

5. **Train and predict.**
   A fresh model is trained on the Gold data using the selected stats, then it predicts a performance tier and score for every player.

6. **Benchmark against the league.**
   The engine re-judges everyone against the target league, keeping both the global and league-relative verdicts.

7. **Present the shortlist.**
   Results appear as a colour-coded table. Each player gets a **Best Role** and their **Top Archetypes** (strongest qualities). The user can fine-tune on the spot — by age, tier, position, contract expiry, and number of results — without re-running the heavy steps, because the pipeline output is cached.

8. **Explain and visualize.**
   The user can request an AI scouting report for any player, and explore two charts: a **League Fit** plot (age vs. performance relative to the league average) and **distribution** charts breaking the shortlist down by age, role, league, position, market value, and nationality.

---

## 4. Why It's Built This Way

- **Layered pipeline (Bronze/Silver/Gold):** keeps raw data pristine, isolates cleaning from judgment, and makes every step auditable and reusable.
- **Saved intermediate results:** the heavy work (cleaning, scoring, training) is done once and cached, so fine-tuning the shortlist is instant.
- **Position-aware scoring:** players are judged against peers in their own role, not against everyone, so comparisons stay fair.
- **League re-baselining:** "good" is always relative to a standard you choose, which matters when scouting across leagues of different quality.
- **Provider fallback for AI:** if the primary report generator is down, a backup keeps the feature working.

### In short

You give the engine a filter and a focus. It cleans the data, learns who the best performers are, measures them against the league you care about, and hands you a ranked shortlist with written scouting reports and clear visuals — automatically, and in a way that's transparent at every stage.
