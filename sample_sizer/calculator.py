"""Rule-based sample size calculator for 10 research methods."""

import math
from typing import Optional

from .models import (
    EffectSize,
    Homogeneity,
    MethodType,
    ResearchMethod,
    SampleSizeInput,
    SampleSizeResult,
    UsabilityGoal,
)

# --------------------------------------------------------------------------- #
# Lookup tables
# --------------------------------------------------------------------------- #

_Z_CONF = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}
_Z_POWER = {0.70: 0.524, 0.75: 0.674, 0.80: 0.842, 0.85: 1.036, 0.90: 1.282, 0.95: 1.645}

_EFFECT_D = {EffectSize.SMALL: 0.2, EffectSize.MEDIUM: 0.5, EffectSize.LARGE: 0.8}
_EFFECT_H = {EffectSize.SMALL: 0.2, EffectSize.MEDIUM: 0.5, EffectSize.LARGE: 0.8}
_EFFECT_R = {EffectSize.SMALL: 0.1, EffectSize.MEDIUM: 0.3, EffectSize.LARGE: 0.5}

METHOD_TYPE_MAP = {
    ResearchMethod.INTERVIEWS: MethodType.QUALITATIVE,
    ResearchMethod.FOCUS_GROUPS: MethodType.QUALITATIVE,
    ResearchMethod.DIARY_STUDY: MethodType.QUALITATIVE,
    ResearchMethod.USABILITY_TEST: MethodType.QUALITATIVE,
    ResearchMethod.CARD_SORTING: MethodType.QUALITATIVE,
    ResearchMethod.TREE_TESTING: MethodType.QUANTITATIVE,
    ResearchMethod.SURVEY: MethodType.QUANTITATIVE,
    ResearchMethod.AB_TEST: MethodType.QUANTITATIVE,
    ResearchMethod.EXPERIMENT: MethodType.QUANTITATIVE,
    ResearchMethod.CORRELATION: MethodType.QUANTITATIVE,
}

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _z_conf(cl: float) -> float:
    return _Z_CONF.get(round(cl, 2), 1.960)


def _z_power(pwr: float) -> float:
    return _Z_POWER.get(round(pwr, 2), 0.842)


def _finite_correction(n: int, population: Optional[int]) -> int:
    if population is None or population <= 0:
        return n
    n_adj = (n * population) / (n + population - 1)
    return max(1, math.ceil(n_adj))


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def calculate(inp: SampleSizeInput) -> SampleSizeResult:
    """Dispatch to the appropriate method-specific calculator."""
    _dispatch = {
        ResearchMethod.INTERVIEWS: _calc_interviews,
        ResearchMethod.FOCUS_GROUPS: _calc_focus_groups,
        ResearchMethod.DIARY_STUDY: _calc_diary_study,
        ResearchMethod.USABILITY_TEST: _calc_usability,
        ResearchMethod.CARD_SORTING: _calc_card_sorting,
        ResearchMethod.TREE_TESTING: _calc_tree_testing,
        ResearchMethod.SURVEY: _calc_survey,
        ResearchMethod.AB_TEST: _calc_ab_test,
        ResearchMethod.EXPERIMENT: _calc_experiment,
        ResearchMethod.CORRELATION: _calc_correlation,
    }
    fn = _dispatch.get(inp.method)
    if fn is None:
        raise ValueError(f"Unknown method: {inp.method}")
    return fn(inp)


# --------------------------------------------------------------------------- #
# Qualitative methods
# --------------------------------------------------------------------------- #


def _calc_interviews(inp: SampleSizeInput) -> SampleSizeResult:
    h = inp.homogeneity
    if h == Homogeneity.HOMOGENEOUS:
        min_n, rec_n, max_n = 8, 12, 15
        rationale = (
            "Homogeneous participant pool reaches thematic saturation quickly. "
            "Nielsen & Landauer (1993) suggest ~85% of issues surface by participant 12 "
            "in demographically similar groups."
        )
    elif h == Homogeneity.HETEROGENEOUS:
        min_n, rec_n, max_n = 20, 25, 35
        rationale = (
            "Heterogeneous populations require more participants to reach saturation across "
            "subgroups. Guest et al. (2006) recommend 20–30 for diverse samples — saturation "
            "is rarely achieved below 20 when behavioural variation is high."
        )
    else:
        min_n, rec_n, max_n = 12, 18, 25
        rationale = (
            "Mixed participant pool — 15–20 is the practical saturation target, with 18 as a "
            "robust default (Guest et al., 2006; Creswell, 2013). Plan interim analysis at n=8 "
            "and n=15 to assess whether new themes are emerging."
        )

    caveats = [
        "Add 10–20% buffer for participant drop-off and no-shows.",
        "Saturation is emergent — run interim thematic checks every 5 participants.",
        "Cross-cultural samples may need separate saturation tracking per subgroup.",
    ]
    return SampleSizeResult(
        method=inp.method,
        method_type=MethodType.QUALITATIVE,
        recommended_n=rec_n,
        min_n=min_n,
        max_n=max_n,
        rationale=rationale,
        power_notes=(
            "Qualitative research uses saturation rather than statistical power. "
            "Plan interim reviews and stop when no new themes emerge across 3 consecutive interviews."
        ),
        caveats=caveats,
    )


def _calc_focus_groups(inp: SampleSizeInput) -> SampleSizeResult:
    h = inp.homogeneity
    if h == Homogeneity.HOMOGENEOUS:
        n_groups, min_g, max_g, per_group = 3, 2, 4, 6
    elif h == Homogeneity.HETEROGENEOUS:
        n_groups, min_g, max_g, per_group = 5, 4, 6, 8
    else:
        n_groups, min_g, max_g, per_group = 4, 3, 5, 6

    rec_n = n_groups * per_group
    min_n = min_g * 5
    max_n = max_g * 8

    rationale = (
        f"Krueger & Casey (2015) recommend 3–5 focus groups per segment, with 6–8 participants "
        f"per group. Recommended: {n_groups} groups × {per_group} participants = {rec_n} total. "
        f"Run groups sequentially — stop when new groups yield no new themes."
    )
    caveats = [
        f"Recruit {per_group + 2} per group to cover no-shows (typical drop: 15–25%).",
        "Avoid mixing hierarchically distinct participants (e.g., managers and direct reports).",
        "Online groups can be smaller (5–6) as engagement fatigue sets in faster.",
    ]
    return SampleSizeResult(
        method=inp.method,
        method_type=MethodType.QUALITATIVE,
        recommended_n=rec_n,
        min_n=min_n,
        max_n=max_n,
        rationale=rationale,
        power_notes=(
            f"Minimum viable: {min_g} groups. "
            f"Saturation typically reached by group {n_groups} in similar-segment studies."
        ),
        caveats=caveats,
    )


def _calc_diary_study(inp: SampleSizeInput) -> SampleSizeResult:
    h = inp.homogeneity
    if h == Homogeneity.HOMOGENEOUS:
        min_n, rec_n, max_n = 10, 15, 20
    elif h == Homogeneity.HETEROGENEOUS:
        min_n, rec_n, max_n = 20, 28, 40
    else:
        min_n, rec_n, max_n = 15, 20, 30

    rationale = (
        "Diary studies require sustained engagement — larger than interview samples to "
        "compensate for attrition. Bolger et al. (2003) report 15–25 participants as typical "
        "for experience sampling methods. Plan for 20–40% dropout over a 2-week study."
    )
    caveats = [
        "Recruit 30–50% above your target to account for diary fatigue and dropout.",
        "Pilot with 3–5 participants to validate probe design and response burden.",
        "Daily prompts >2 minutes correlate with ~40% dropout increase (Eisma et al., 2020).",
    ]
    return SampleSizeResult(
        method=inp.method,
        method_type=MethodType.QUALITATIVE,
        recommended_n=rec_n,
        min_n=min_n,
        max_n=max_n,
        rationale=rationale,
        power_notes=(
            "Plan for 20–40% attrition over a 2-week study. "
            "N is the completion target, not the recruitment target."
        ),
        caveats=caveats,
    )


def _calc_usability(inp: SampleSizeInput) -> SampleSizeResult:
    goal = inp.usability_goal
    if goal == UsabilityGoal.FORMATIVE:
        min_n, rec_n, max_n = 5, 8, 12
        rationale = (
            "Nielsen's (1993) landmark study: 5 users find ~85% of usability problems in "
            "formative testing (assuming p=0.31 per-problem detection). CPR recommends 8 "
            "to account for moderator-participant interaction effects and edge-case tasks."
        )
        power_notes = (
            "The 5-user heuristic assumes a 31% per-problem detection rate. "
            "For complex or multi-path flows, use 8–12."
        )
    elif goal == UsabilityGoal.SUMMATIVE:
        min_n, rec_n, max_n = 12, 18, 25
        rationale = (
            "Summative testing requires enough participants to detect performance differences. "
            "18 participants provides ~80% power to detect medium-sized usability differences "
            "(d=0.5) at α=0.05 for task time or success rate comparisons."
        )
        power_notes = (
            "Power: ~80% at n=18 for medium effect (d=0.5). "
            "For benchmark comparisons across design iterations, use 25+."
        )
    else:  # benchmark
        min_n, rec_n, max_n = 25, 35, 50
        rationale = (
            "Benchmark studies require stable mean estimates. 35 participants produces "
            "confidence intervals narrow enough (±8–12 SUS points) for reliable cross-iteration "
            "comparisons. Sauro & Lewis (2012) recommend 25–35 for SUS benchmarking."
        )
        power_notes = "CI on SUS score: ±12 points at n=25, ±8 at n=35. Industry standard for longitudinal benchmarks."

    caveats = [
        "Each distinct task flow may need its own subsample if paths diverge significantly.",
        "Remote unmoderated may need 2× participants to match moderated data quality.",
        "Accessibility testing requires separate recruitment from mainstream usability cohorts.",
    ]
    return SampleSizeResult(
        method=inp.method,
        method_type=MethodType.QUALITATIVE,
        recommended_n=rec_n,
        min_n=min_n,
        max_n=max_n,
        rationale=rationale,
        power_notes=power_notes,
        caveats=caveats,
    )


def _calc_card_sorting(inp: SampleSizeInput) -> SampleSizeResult:
    h = inp.homogeneity
    if h == Homogeneity.HOMOGENEOUS:
        min_n, rec_n, max_n = 15, 20, 30
    elif h == Homogeneity.HETEROGENEOUS:
        min_n, rec_n, max_n = 25, 35, 50
    else:
        min_n, rec_n, max_n = 20, 30, 40

    rationale = (
        "Tullis & Wood (2004) recommend 20–30 participants for open card sorts. "
        "Dendrogram cluster stability typically reaches asymptote by n=30. "
        "Closed card sorts can use slightly fewer (15–20) due to reduced grouping ambiguity."
    )
    caveats = [
        "Open sorts are noisier — fewer participants = less stable cluster solutions.",
        "If using automated tools (e.g., OptimalSort), 30+ significantly improves dendrogram reliability.",
        "Pilot with 3–5 participants to validate that card labels are unambiguous.",
    ]
    return SampleSizeResult(
        method=inp.method,
        method_type=MethodType.QUALITATIVE,
        recommended_n=rec_n,
        min_n=min_n,
        max_n=max_n,
        rationale=rationale,
        power_notes="Cluster stability: measurable at n=20, reliable at n=30+.",
        caveats=caveats,
    )


# --------------------------------------------------------------------------- #
# Quantitative methods
# --------------------------------------------------------------------------- #


def _calc_tree_testing(inp: SampleSizeInput) -> SampleSizeResult:
    z = _z_conf(inp.confidence_level)
    e = inp.margin_of_error
    p = inp.expected_proportion

    n_raw = math.ceil((z**2 * p * (1 - p)) / (e**2))
    n_adj = _finite_correction(n_raw, inp.population_size)
    n_final = max(50, n_adj)

    min_n = max(50, math.ceil(n_final * 0.7))
    max_n = math.ceil(n_final * 1.3)

    pop_note = f", finite-corrected to {n_adj} for population={inp.population_size:,}" if inp.population_size else ""
    rationale = (
        f"Tree testing measures task success rate (binary proportion). "
        f"Using z={z:.3f} (CI={inp.confidence_level:.0%}), p={p:.2f}, margin of error ±{e:.0%}: "
        f"n = {n_raw} raw{pop_note}. Industry minimum is 50 participants."
    )
    caveats = [
        "Always recruit at least 50 participants regardless of formula output.",
        "Test each distinct navigation path separately if tasks vary in complexity.",
        "Remote unmoderated works well for tree tests — it scales cheaply.",
    ]
    return SampleSizeResult(
        method=inp.method,
        method_type=MethodType.QUANTITATIVE,
        recommended_n=n_final,
        min_n=min_n,
        max_n=max(60, max_n),
        rationale=rationale,
        power_notes=(
            f"Raw n={n_raw}"
            + (f", corrected={n_adj}" if inp.population_size else "")
            + ". Industry floor: 50."
        ),
        caveats=caveats,
        confidence_level=inp.confidence_level,
    )


def _calc_survey(inp: SampleSizeInput) -> SampleSizeResult:
    z = _z_conf(inp.confidence_level)
    e = inp.margin_of_error
    p = inp.expected_proportion

    n_raw = math.ceil((z**2 * p * (1 - p)) / (e**2))
    n_adj = _finite_correction(n_raw, inp.population_size)

    min_n = max(30, math.ceil(n_adj * 0.8))
    max_n = math.ceil(n_adj * 1.2)

    pop_str = f" (finite-corrected from {n_raw} for population={inp.population_size:,})" if inp.population_size else ""
    rationale = (
        f"Cochran's (1977) formula: n = z²·p·(1−p) / e². "
        f"With z={z:.3f}, p={p:.2f}, e={e:.2f}: n = {n_adj}{pop_str}."
    )
    power_notes = (
        "This is the minimum n for stated confidence and margin of error — not a power calculation. "
        "For subgroup analysis, apply the formula separately per subgroup."
    )
    send_n = math.ceil(n_adj * 1.3)
    caveats = [
        f"Add 20–40% for non-response (target invitations: {send_n:,}).",
        "For subgroup comparisons, ensure n≥30 per subgroup.",
        "Consider whether non-responders differ systematically from responders (non-response bias).",
    ]
    return SampleSizeResult(
        method=inp.method,
        method_type=MethodType.QUANTITATIVE,
        recommended_n=n_adj,
        min_n=min_n,
        max_n=max_n,
        rationale=rationale,
        power_notes=power_notes,
        caveats=caveats,
        confidence_level=inp.confidence_level,
    )


def _calc_ab_test(inp: SampleSizeInput) -> SampleSizeResult:
    h = _EFFECT_H[inp.effect_size]
    z_a = _z_conf(inp.confidence_level)
    z_b = _z_power(inp.power)

    # Cohen's h: n per arm = (z_alpha/2 + z_beta)² / h²
    n_per_arm = math.ceil(((z_a + z_b) ** 2) / (h**2))
    n_total = n_per_arm * 2

    min_n = math.ceil(n_total * 0.7)
    max_n = math.ceil(n_total * 1.5)

    rationale = (
        f"Two-proportion z-test (Cohen's h={h}). "
        f"Effect size: {inp.effect_size.value} (h={h}). "
        f"Power={inp.power:.0%}, α={1 - inp.confidence_level:.2f} (two-sided). "
        f"n per arm = {n_per_arm:,}, total = {n_total:,}."
    )
    power_notes = (
        f"Power: {inp.power:.0%} to detect h={h} ({inp.effect_size.value} effect). "
        f"Run time depends on traffic volume: {n_per_arm:,} exposures needed per arm."
    )
    caveats = [
        "Run both arms simultaneously — sequential exposure introduces time confounds.",
        "Pre-register your stopping rule. Peeking at results inflates Type I error.",
        "Ensure MDE is business-meaningful before accepting the effect size assumption.",
        f"If traffic is limited, consider whether {n_per_arm:,} users/arm is achievable in budget.",
    ]
    return SampleSizeResult(
        method=inp.method,
        method_type=MethodType.QUANTITATIVE,
        recommended_n=n_total,
        min_n=min_n,
        max_n=max_n,
        rationale=rationale,
        power_notes=power_notes,
        caveats=caveats,
        confidence_level=inp.confidence_level,
        actual_power=inp.power,
    )


def _calc_experiment(inp: SampleSizeInput) -> SampleSizeResult:
    d = _EFFECT_D[inp.effect_size]
    z_a = _z_conf(inp.confidence_level)
    z_b = _z_power(inp.power)

    # Independent-samples t-test: n per group = 2 * ((z_alpha + z_beta) / d)²
    n_per_group = math.ceil(2 * ((z_a + z_b) / d) ** 2)
    n_total = n_per_group * 2

    min_n = math.ceil(n_total * 0.7)
    max_n = math.ceil(n_total * 1.5)

    rationale = (
        f"Independent-samples t-test. Cohen's d={d} ({inp.effect_size.value} effect). "
        f"Power={inp.power:.0%}, α={1 - inp.confidence_level:.2f}. "
        f"n per group = {n_per_group}, total = {n_total}."
    )
    power_notes = (
        f"Power: {inp.power:.0%} to detect d={d}. "
        "For repeated-measures designs, required n reduces by ~30–50%."
    )
    caveats = [
        "This is for two-group independent design. Multi-group ANOVA adjusts for multiple comparisons.",
        "Repeated-measures designs require fewer participants for equivalent power.",
        "Validate your assumed effect size against domain benchmarks — d=0.5 is optimistic for many UX outcomes.",
    ]
    return SampleSizeResult(
        method=inp.method,
        method_type=MethodType.QUANTITATIVE,
        recommended_n=n_total,
        min_n=min_n,
        max_n=max_n,
        rationale=rationale,
        power_notes=power_notes,
        caveats=caveats,
        confidence_level=inp.confidence_level,
        actual_power=inp.power,
    )


def _calc_correlation(inp: SampleSizeInput) -> SampleSizeResult:
    r = _EFFECT_R[inp.effect_size]
    z_a = _z_conf(inp.confidence_level)
    z_b = _z_power(inp.power)

    # Fisher r-to-z transform
    z_r = 0.5 * math.log((1 + r) / (1 - r))
    n = math.ceil(((z_a + z_b) / z_r) ** 2 + 3)
    n_final = max(20, n)

    min_n = max(20, math.ceil(n_final * 0.8))
    max_n = math.ceil(n_final * 1.3)

    rationale = (
        f"Pearson correlation, Fisher r-to-z transformation. "
        f"r={r} ({inp.effect_size.value}), z_r={z_r:.3f}. "
        f"Power={inp.power:.0%}, α={1 - inp.confidence_level:.2f}. "
        f"n = {n_final}."
    )
    power_notes = (
        f"Power: {inp.power:.0%} to detect r={r}. "
        "Minimum recommended: 20 participants."
    )
    caveats = [
        "Non-normal distributions may require Spearman's ρ — use similar n, different effect size conventions.",
        "Outliers strongly influence Pearson r — plan for sensitivity analysis.",
        "Cross-sectional correlations cannot establish causality.",
    ]
    return SampleSizeResult(
        method=inp.method,
        method_type=MethodType.QUANTITATIVE,
        recommended_n=n_final,
        min_n=min_n,
        max_n=max(25, max_n),
        rationale=rationale,
        power_notes=power_notes,
        caveats=caveats,
        confidence_level=inp.confidence_level,
        actual_power=inp.power,
    )
