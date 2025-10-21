Feature: Team Tactical Style Profile
Why this exists

Add an expand-on-click tactical profile to each team in the existing All Teams page. It shows quick KPIs (points/game, goals/game) plus a radar chart of the team’s style vector so analysts can scan tendencies and rank-based strengths without leaving the list.

UX Summary

Entry point: All Teams page (existing).

Interaction: Clicking a team row expands an inline panel below that row.

Panel content:

KPI strip: Points per game, Goals per game.

Controls:

Mode: Absolute vs League Rank

Labels: Values vs Ranks (1=best…N=worst)

Radar chart: Team style vector, axes colored by percentile (0–100).

Actions:

“View tactical profile” → /teams/profile?team_id=... (stub ok)

“Compare” → /teams/compare?team_id=... (stub ok)

Data & Modes (metric list intentionally omitted)

Inputs: Team Season Stats (your selected per-game style fields) and Matches (for points/game if needed).

Absolute mode: Per-axis league min–max normalization, oriented so outward = better.

League Rank mode: Convert each metric to a rank 1…N (1 = best), then map to radius 1.0…0.0 (1 → outer edge).

Use your existing “higher/lower is better” map so every axis is oriented with better farther from center.

Implementation (instructions only)
1) Data access

Import only the client object and call:

client.team_season_stats(competition_id, season_id)

client.matches(competition_id, season_id) (if computing points/game)

Keep all calculations in this feature module/page (not in the client).

2) One-time precompute per season (in-memory)

On first load (or when (competition_id, season_id) changes):

Fetch Team Season Stats; store raw response in your existing in-memory store.

Optional: Fetch Matches to compute points/game (or map from season stats if already provided).

Build a style matrix: one row per team, columns = your chosen style metrics.

For each metric, compute and store:

abs_radius ∈ [0,1] via min–max on oriented values.

rank (dense ties) and rank_radius ∈ [0,1] from 1…N → 1…0.

percentile (0–100) from oriented values (used for axis color in both modes).

Also store points_pg and goals_pg per team.

Save the entire precomputed bundle in memory keyed by (competition_id, season_id).

3) UI wiring on All Teams

Keep the existing table; on row click:

Render the KPI strip (Points/game, Goals/game).

Render controls: Mode (Absolute/Rank) and Labels (Values/Ranks).

Draw the radar polygon using:

abs_radius in Absolute mode

rank_radius in Rank mode

Axis coloring: color each axis/spoke (and/or its label) using the metric percentile for that team (0–100). Add a small color legend.

Footer buttons: link-only navigation to the stub pages.

4) Normalization, ranking, orientation

Orientation: Apply your higher/lower-is-better map so outward always means better.

Absolute: Per-axis min–max on oriented values; clamp to [0,1].

Rank: Dense 1…N ranks; convert to radius linearly (1 → 1.0, N → 0.0).

Percentiles: Compute from oriented values; these do not change when toggling modes.

5) In-memory storage (no extra cache yet)

Follow your existing pattern: store raw pulls + precompute in memory.

Rebuild only when (competition_id, season_id) changes.

Row toggles and control switches must not trigger refetch or heavy recompute.

6) Edge handling

Missing values: Either hide the axis across all teams or impute with league min and mark as “n/a”.

Constant columns: Treat as “flat”; radius ~0.5 and neutral axis color; label accordingly.

Ties: Dense ranks (equal values share ranks) with deterministic ordering.

Acceptance Criteria (Condensed)

Data & Fetching

Uses only the client object for API calls; all calculations remain in this module.

For each (competition_id, season_id), raw data and a precomputed bundle (abs_radius, rank, rank_radius, percentile, points_pg, goals_pg) are stored in memory and reused.

UI / UX

Expanding a row shows KPI strip, mode & label controls, a radar chart with percentile-colored axes, and two action buttons with correct team_id links.

Switching Absolute ↔ Rank updates polygon radii; labels follow the Values/Ranks toggle.

Radar Behavior

Outward always means better across all metrics.

Axis color reflects the team’s percentile (0–100) for that metric and does not change when switching modes.

Missing/constant metrics render with neutral visuals and clear indicators; no errors or layout glitches.

Performance & Stability

No redundant API calls after initial in-memory precompute.

Row expand and toggle interactions feel instant on a typical laptop.

Manual spot checks confirm known best metrics plot at the outer edge in both modes.