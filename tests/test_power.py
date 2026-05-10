"""Tests for power analysis utilities."""

import math

import pytest

from sample_sizer.models import EffectSize, ResearchMethod
from sample_sizer.power import (
    _phi,
    generate_power_curve,
    power_for_n_abtest,
    power_for_n_correlation,
    power_for_n_ttest,
    recommended_n_for_power,
)


class TestPhi:
    def test_at_zero(self):
        assert abs(_phi(0.0) - 0.5) < 1e-6

    def test_large_positive(self):
        assert _phi(10.0) > 0.9999

    def test_large_negative(self):
        assert _phi(-10.0) < 0.0001

    def test_known_value_196(self):
        # P(Z < 1.96) ≈ 0.975
        assert abs(_phi(1.96) - 0.975) < 0.001

    def test_symmetry(self):
        for x in [0.5, 1.0, 1.96, 2.576]:
            assert abs(_phi(x) + _phi(-x) - 1.0) < 1e-9


class TestPowerTtest:
    def test_increases_with_n(self):
        d = 0.5
        p10 = power_for_n_ttest(10, d)
        p50 = power_for_n_ttest(50, d)
        p200 = power_for_n_ttest(200, d)
        assert p10 < p50 < p200

    def test_increases_with_d(self):
        n = 30
        p_small = power_for_n_ttest(n, 0.2)
        p_med = power_for_n_ttest(n, 0.5)
        p_large = power_for_n_ttest(n, 0.8)
        assert p_small < p_med < p_large

    def test_small_n_low_power(self):
        assert power_for_n_ttest(5, 0.2) < 0.3

    def test_large_n_high_power(self):
        assert power_for_n_ttest(500, 0.5) > 0.99

    def test_zero_n_returns_zero(self):
        assert power_for_n_ttest(0, 0.5) == 0.0

    def test_zero_d_returns_zero(self):
        assert power_for_n_ttest(100, 0.0) == 0.0

    def test_output_in_range(self):
        for n in [10, 50, 100, 200]:
            p = power_for_n_ttest(n, 0.5)
            assert 0.0 <= p <= 1.0

    def test_known_approx_n64_d05(self):
        # n=64 per group, d=0.5: power ≈ 0.80
        p = power_for_n_ttest(64, 0.5)
        assert 0.75 < p < 0.90


class TestPowerABTest:
    def test_increases_with_n(self):
        h = 0.3
        p20 = power_for_n_abtest(20, h)
        p100 = power_for_n_abtest(100, h)
        assert p20 < p100

    def test_increases_with_h(self):
        n = 50
        p_small = power_for_n_abtest(n, 0.2)
        p_large = power_for_n_abtest(n, 0.8)
        assert p_small < p_large

    def test_zero_n_returns_zero(self):
        assert power_for_n_abtest(0, 0.5) == 0.0

    def test_zero_h_returns_zero(self):
        assert power_for_n_abtest(100, 0.0) == 0.0

    def test_output_in_range(self):
        for n in [20, 50, 100]:
            p = power_for_n_abtest(n, 0.5)
            assert 0.0 <= p <= 1.0

    def test_large_n_approaches_1(self):
        assert power_for_n_abtest(1000, 0.5) > 0.99


class TestPowerCorrelation:
    def test_increases_with_n(self):
        r = 0.3
        p20 = power_for_n_correlation(20, r)
        p100 = power_for_n_correlation(100, r)
        assert p20 < p100

    def test_increases_with_r(self):
        n = 50
        p_small = power_for_n_correlation(n, 0.1)
        p_large = power_for_n_correlation(n, 0.5)
        assert p_small < p_large

    def test_n_le_3_returns_zero(self):
        assert power_for_n_correlation(3, 0.3) == 0.0

    def test_output_in_range(self):
        for n in [20, 50, 100]:
            p = power_for_n_correlation(n, 0.3)
            assert 0.0 <= p <= 1.0

    def test_large_n_high_power(self):
        assert power_for_n_correlation(500, 0.3) > 0.99


class TestGeneratePowerCurve:
    def test_experiment_returns_points(self):
        pts = generate_power_curve(ResearchMethod.EXPERIMENT)
        assert len(pts) > 0

    def test_ab_test_returns_points(self):
        pts = generate_power_curve(ResearchMethod.AB_TEST)
        assert len(pts) > 0

    def test_correlation_returns_points(self):
        pts = generate_power_curve(ResearchMethod.CORRELATION)
        assert len(pts) > 0

    def test_qualitative_returns_empty(self):
        pts = generate_power_curve(ResearchMethod.INTERVIEWS)
        assert pts == []

    def test_focus_groups_returns_empty(self):
        pts = generate_power_curve(ResearchMethod.FOCUS_GROUPS)
        assert pts == []

    def test_power_values_in_range(self):
        pts = generate_power_curve(ResearchMethod.EXPERIMENT, effect_size=EffectSize.MEDIUM)
        for pt in pts:
            assert 0.0 <= pt.power <= 1.0

    def test_monotone_for_experiment(self):
        pts = generate_power_curve(ResearchMethod.EXPERIMENT, effect_size=EffectSize.MEDIUM)
        powers = [pt.power for pt in pts]
        assert powers == sorted(powers) or all(
            b >= a - 0.01 for a, b in zip(powers, powers[1:])
        )

    def test_n_values_increasing(self):
        pts = generate_power_curve(ResearchMethod.AB_TEST)
        ns = [pt.n for pt in pts]
        assert ns == sorted(ns)

    def test_custom_range(self):
        pts = generate_power_curve(ResearchMethod.CORRELATION, n_range=(20, 100), steps=10)
        assert pts[0].n >= 20
        assert pts[-1].n <= 100

    def test_large_effect_reaches_high_power(self):
        pts = generate_power_curve(ResearchMethod.EXPERIMENT, effect_size=EffectSize.LARGE, n_range=(10, 500))
        max_power = max(pt.power for pt in pts)
        assert max_power > 0.95


class TestRecommendedNForPower:
    def test_experiment_medium(self):
        n = recommended_n_for_power(ResearchMethod.EXPERIMENT, target_power=0.80, effect_size=EffectSize.MEDIUM)
        assert n > 0

    def test_higher_power_needs_more_n(self):
        n80 = recommended_n_for_power(ResearchMethod.EXPERIMENT, target_power=0.80)
        n90 = recommended_n_for_power(ResearchMethod.EXPERIMENT, target_power=0.90)
        assert n90 > n80

    def test_smaller_effect_needs_more_n(self):
        n_small = recommended_n_for_power(ResearchMethod.AB_TEST, target_power=0.80, effect_size=EffectSize.SMALL)
        n_large = recommended_n_for_power(ResearchMethod.AB_TEST, target_power=0.80, effect_size=EffectSize.LARGE)
        assert n_small > n_large
