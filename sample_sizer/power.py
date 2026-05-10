"""Power analysis utilities for quantitative research methods."""

import math
from typing import List, Tuple

from .models import EffectSize, PowerCurvePoint, ResearchMethod

# --------------------------------------------------------------------------- #
# Effect size tables
# --------------------------------------------------------------------------- #

_EFFECT_D = {EffectSize.SMALL: 0.2, EffectSize.MEDIUM: 0.5, EffectSize.LARGE: 0.8}
_EFFECT_H = {EffectSize.SMALL: 0.2, EffectSize.MEDIUM: 0.5, EffectSize.LARGE: 0.8}
_EFFECT_R = {EffectSize.SMALL: 0.1, EffectSize.MEDIUM: 0.3, EffectSize.LARGE: 0.5}

_ALPHA_MAP = {0.10: 1.645, 0.05: 1.960, 0.01: 2.576}

# --------------------------------------------------------------------------- #
# Standard normal CDF
# --------------------------------------------------------------------------- #


def _phi(x: float) -> float:
    """Standard normal CDF via math.erf (full machine precision)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _z_crit(alpha: float) -> float:
    """Two-sided critical z value for significance level alpha."""
    return _ALPHA_MAP.get(round(alpha, 2), 1.960)


# --------------------------------------------------------------------------- #
# Per-method power functions
# --------------------------------------------------------------------------- #


def power_for_n_ttest(n_per_group: int, d: float, alpha: float = 0.05) -> float:
    """
    Compute power for a two-sample independent t-test.

    Parameters
    ----------
    n_per_group:  sample size per group
    d:            Cohen's d effect size
    alpha:        significance level (two-sided)
    """
    if n_per_group <= 0 or d <= 0:
        return 0.0
    z_a = _z_crit(alpha)
    ncp = d * math.sqrt(n_per_group / 2.0)
    power = 1.0 - _phi(z_a - ncp) + _phi(-z_a - ncp)
    return min(1.0, max(0.0, power))


def power_for_n_abtest(n_per_arm: int, h: float, alpha: float = 0.05) -> float:
    """
    Compute power for a two-proportion z-test (A/B test).

    Parameters
    ----------
    n_per_arm:  sample size per arm
    h:          Cohen's h effect size
    alpha:      significance level (two-sided)
    """
    if n_per_arm <= 0 or h <= 0:
        return 0.0
    z_a = _z_crit(alpha)
    ncp = h * math.sqrt(n_per_arm)
    power = 1.0 - _phi(z_a - ncp) + _phi(-z_a - ncp)
    return min(1.0, max(0.0, power))


def power_for_n_correlation(n: int, r: float, alpha: float = 0.05) -> float:
    """
    Compute power for a Pearson correlation test (Fisher r-to-z).

    Parameters
    ----------
    n:      total sample size
    r:      expected Pearson r
    alpha:  significance level (two-sided)
    """
    if n <= 3 or abs(r) >= 1.0 or r == 0.0:
        return 0.0
    z_a = _z_crit(alpha)
    z_r = 0.5 * math.log((1 + abs(r)) / (1 - abs(r)))
    ncp = z_r * math.sqrt(n - 3)
    power = 1.0 - _phi(z_a - ncp) + _phi(-z_a - ncp)
    return min(1.0, max(0.0, power))


# --------------------------------------------------------------------------- #
# Power curve generation
# --------------------------------------------------------------------------- #

_QUANTITATIVE_METHODS = {
    ResearchMethod.AB_TEST,
    ResearchMethod.EXPERIMENT,
    ResearchMethod.CORRELATION,
    ResearchMethod.SURVEY,
    ResearchMethod.TREE_TESTING,
}


def generate_power_curve(
    method: ResearchMethod,
    effect_size: EffectSize = EffectSize.MEDIUM,
    alpha: float = 0.05,
    n_range: Tuple[int, int] = (10, 300),
    steps: int = 40,
) -> List[PowerCurvePoint]:
    """
    Generate (n, power) data points for a quantitative method.

    For qualitative methods returns an empty list (saturation is used instead).
    For survey / tree_testing, returns a CI-precision proxy (1 − margin_of_error).
    """
    if method not in _QUANTITATIVE_METHODS:
        return []

    d = _EFFECT_D[effect_size]
    h = _EFFECT_H[effect_size]
    r = _EFFECT_R[effect_size]
    z_a = _z_crit(alpha)

    n_start, n_end = n_range
    step = max(1, (n_end - n_start) // steps)
    points: List[PowerCurvePoint] = []

    for n in range(n_start, n_end + 1, step):
        if method == ResearchMethod.EXPERIMENT:
            pwr = power_for_n_ttest(n // 2, d, alpha)
        elif method == ResearchMethod.AB_TEST:
            pwr = power_for_n_abtest(n // 2, h, alpha)
        elif method == ResearchMethod.CORRELATION:
            pwr = power_for_n_correlation(n, r, alpha)
        elif method in (ResearchMethod.SURVEY, ResearchMethod.TREE_TESTING):
            # CI precision proxy: proportion of variance explained by sample
            e = z_a * math.sqrt(0.25 / max(n, 1))
            pwr = min(1.0, 1.0 - e)
        else:
            continue

        points.append(PowerCurvePoint(n=n, power=round(pwr, 4)))

    return points


def recommended_n_for_power(
    method: ResearchMethod,
    target_power: float,
    effect_size: EffectSize = EffectSize.MEDIUM,
    alpha: float = 0.05,
    max_n: int = 5000,
) -> int:
    """Return the minimum n that achieves target_power for a quantitative method."""
    for n in range(2, max_n + 1):
        d = _EFFECT_D[effect_size]
        h = _EFFECT_H[effect_size]
        r = _EFFECT_R[effect_size]

        if method == ResearchMethod.EXPERIMENT:
            pwr = power_for_n_ttest(n // 2, d, alpha)
        elif method == ResearchMethod.AB_TEST:
            pwr = power_for_n_abtest(n // 2, h, alpha)
        elif method == ResearchMethod.CORRELATION:
            pwr = power_for_n_correlation(n, r, alpha)
        else:
            return n  # Not applicable — return minimum

        if pwr >= target_power:
            return n

    return max_n
