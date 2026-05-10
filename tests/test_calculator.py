"""Tests for rule-based sample size calculator."""

import pytest

from sample_sizer.calculator import calculate
from sample_sizer.models import (
    EffectSize,
    Homogeneity,
    MethodType,
    ResearchMethod,
    SampleSizeInput,
    UsabilityGoal,
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def inp(method, **kwargs):
    return SampleSizeInput(method=method, **kwargs)


def result(method, **kwargs):
    return calculate(inp(method, **kwargs))


# --------------------------------------------------------------------------- #
# Interviews
# --------------------------------------------------------------------------- #


class TestInterviews:
    def test_mixed_recommended(self):
        r = result(ResearchMethod.INTERVIEWS)
        assert r.recommended_n == 18

    def test_homogeneous_recommended(self):
        r = result(ResearchMethod.INTERVIEWS, homogeneity=Homogeneity.HOMOGENEOUS)
        assert r.recommended_n == 12

    def test_heterogeneous_recommended(self):
        r = result(ResearchMethod.INTERVIEWS, homogeneity=Homogeneity.HETEROGENEOUS)
        assert r.recommended_n == 25

    def test_recommended_ge_min(self):
        for h in Homogeneity:
            r = result(ResearchMethod.INTERVIEWS, homogeneity=h)
            assert r.recommended_n >= r.min_n

    def test_max_ge_recommended(self):
        for h in Homogeneity:
            r = result(ResearchMethod.INTERVIEWS, homogeneity=h)
            assert r.max_n >= r.recommended_n

    def test_method_type_is_qualitative(self):
        r = result(ResearchMethod.INTERVIEWS)
        assert r.method_type == MethodType.QUALITATIVE

    def test_has_caveats(self):
        r = result(ResearchMethod.INTERVIEWS)
        assert len(r.caveats) > 0

    def test_rationale_not_empty(self):
        r = result(ResearchMethod.INTERVIEWS)
        assert len(r.rationale) > 20


# --------------------------------------------------------------------------- #
# Focus groups
# --------------------------------------------------------------------------- #


class TestFocusGroups:
    def test_mixed_recommended(self):
        r = result(ResearchMethod.FOCUS_GROUPS)
        assert r.recommended_n == 24  # 4 groups × 6

    def test_homogeneous_recommended(self):
        r = result(ResearchMethod.FOCUS_GROUPS, homogeneity=Homogeneity.HOMOGENEOUS)
        assert r.recommended_n == 18  # 3 × 6

    def test_heterogeneous_recommended(self):
        r = result(ResearchMethod.FOCUS_GROUPS, homogeneity=Homogeneity.HETEROGENEOUS)
        assert r.recommended_n == 40  # 5 × 8

    def test_recommended_ge_min(self):
        for h in Homogeneity:
            r = result(ResearchMethod.FOCUS_GROUPS, homogeneity=h)
            assert r.recommended_n >= r.min_n

    def test_max_ge_recommended(self):
        for h in Homogeneity:
            r = result(ResearchMethod.FOCUS_GROUPS, homogeneity=h)
            assert r.max_n >= r.recommended_n

    def test_method_type_is_qualitative(self):
        r = result(ResearchMethod.FOCUS_GROUPS)
        assert r.method_type == MethodType.QUALITATIVE

    def test_n_positive(self):
        r = result(ResearchMethod.FOCUS_GROUPS)
        assert r.recommended_n > 0


# --------------------------------------------------------------------------- #
# Diary study
# --------------------------------------------------------------------------- #


class TestDiaryStudy:
    def test_mixed_recommended(self):
        r = result(ResearchMethod.DIARY_STUDY)
        assert r.recommended_n == 20

    def test_homogeneous_recommended(self):
        r = result(ResearchMethod.DIARY_STUDY, homogeneity=Homogeneity.HOMOGENEOUS)
        assert r.recommended_n == 15

    def test_heterogeneous_recommended(self):
        r = result(ResearchMethod.DIARY_STUDY, homogeneity=Homogeneity.HETEROGENEOUS)
        assert r.recommended_n == 28

    def test_recommended_ge_min(self):
        for h in Homogeneity:
            r = result(ResearchMethod.DIARY_STUDY, homogeneity=h)
            assert r.recommended_n >= r.min_n

    def test_method_type_qualitative(self):
        r = result(ResearchMethod.DIARY_STUDY)
        assert r.method_type == MethodType.QUALITATIVE


# --------------------------------------------------------------------------- #
# Usability test
# --------------------------------------------------------------------------- #


class TestUsabilityTest:
    def test_formative_recommended(self):
        r = result(ResearchMethod.USABILITY_TEST, usability_goal=UsabilityGoal.FORMATIVE)
        assert r.recommended_n == 8

    def test_summative_recommended(self):
        r = result(ResearchMethod.USABILITY_TEST, usability_goal=UsabilityGoal.SUMMATIVE)
        assert r.recommended_n == 18

    def test_benchmark_recommended(self):
        r = result(ResearchMethod.USABILITY_TEST, usability_goal=UsabilityGoal.BENCHMARK)
        assert r.recommended_n == 35

    def test_formative_min(self):
        r = result(ResearchMethod.USABILITY_TEST, usability_goal=UsabilityGoal.FORMATIVE)
        assert r.min_n == 5

    def test_recommended_ge_min_all_goals(self):
        for g in UsabilityGoal:
            r = result(ResearchMethod.USABILITY_TEST, usability_goal=g)
            assert r.recommended_n >= r.min_n

    def test_method_type_qualitative(self):
        r = result(ResearchMethod.USABILITY_TEST)
        assert r.method_type == MethodType.QUALITATIVE


# --------------------------------------------------------------------------- #
# Card sorting
# --------------------------------------------------------------------------- #


class TestCardSorting:
    def test_mixed_recommended(self):
        r = result(ResearchMethod.CARD_SORTING)
        assert r.recommended_n == 30

    def test_homogeneous_recommended(self):
        r = result(ResearchMethod.CARD_SORTING, homogeneity=Homogeneity.HOMOGENEOUS)
        assert r.recommended_n == 20

    def test_heterogeneous_recommended(self):
        r = result(ResearchMethod.CARD_SORTING, homogeneity=Homogeneity.HETEROGENEOUS)
        assert r.recommended_n == 35

    def test_recommended_ge_min(self):
        for h in Homogeneity:
            r = result(ResearchMethod.CARD_SORTING, homogeneity=h)
            assert r.recommended_n >= r.min_n

    def test_method_type_qualitative(self):
        r = result(ResearchMethod.CARD_SORTING)
        assert r.method_type == MethodType.QUALITATIVE


# --------------------------------------------------------------------------- #
# Tree testing
# --------------------------------------------------------------------------- #


class TestTreeTesting:
    def test_minimum_50(self):
        # Even with tiny population, floor is 50
        r = result(ResearchMethod.TREE_TESTING, margin_of_error=0.15)
        assert r.recommended_n >= 50

    def test_default_recommended_ge_50(self):
        r = result(ResearchMethod.TREE_TESTING)
        assert r.recommended_n >= 50

    def test_narrow_margin_higher_n(self):
        r_wide = result(ResearchMethod.TREE_TESTING, margin_of_error=0.10)
        r_narrow = result(ResearchMethod.TREE_TESTING, margin_of_error=0.03)
        assert r_narrow.recommended_n >= r_wide.recommended_n

    def test_method_type_quantitative(self):
        r = result(ResearchMethod.TREE_TESTING)
        assert r.method_type == MethodType.QUANTITATIVE

    def test_recommended_ge_min(self):
        r = result(ResearchMethod.TREE_TESTING)
        assert r.recommended_n >= r.min_n


# --------------------------------------------------------------------------- #
# Survey
# --------------------------------------------------------------------------- #


class TestSurvey:
    def test_default_n_approx_385(self):
        # z=1.96, p=0.5, e=0.05 → n = ceil(1.96² × 0.25 / 0.0025) = 385
        r = result(ResearchMethod.SURVEY)
        assert r.recommended_n == 385

    def test_narrow_margin_higher_n(self):
        r_wide = result(ResearchMethod.SURVEY, margin_of_error=0.10)
        r_narrow = result(ResearchMethod.SURVEY, margin_of_error=0.03)
        assert r_narrow.recommended_n > r_wide.recommended_n

    def test_high_confidence_higher_n(self):
        r_95 = result(ResearchMethod.SURVEY, confidence_level=0.95)
        r_99 = result(ResearchMethod.SURVEY, confidence_level=0.99)
        assert r_99.recommended_n > r_95.recommended_n

    def test_finite_correction_reduces_n(self):
        r_inf = result(ResearchMethod.SURVEY)
        r_fin = result(ResearchMethod.SURVEY, population_size=500)
        assert r_fin.recommended_n < r_inf.recommended_n

    def test_finite_correction_small_population(self):
        r = result(ResearchMethod.SURVEY, population_size=200)
        assert r.recommended_n <= 200

    def test_method_type_quantitative(self):
        r = result(ResearchMethod.SURVEY)
        assert r.method_type == MethodType.QUANTITATIVE

    def test_recommended_ge_min(self):
        r = result(ResearchMethod.SURVEY)
        assert r.recommended_n >= r.min_n

    def test_rationale_contains_cochran(self):
        r = result(ResearchMethod.SURVEY)
        assert "Cochran" in r.rationale

    def test_has_caveats(self):
        r = result(ResearchMethod.SURVEY)
        assert len(r.caveats) >= 2


# --------------------------------------------------------------------------- #
# A/B test
# --------------------------------------------------------------------------- #


class TestABTest:
    def test_small_effect_higher_n(self):
        r_small = result(ResearchMethod.AB_TEST, effect_size=EffectSize.SMALL)
        r_large = result(ResearchMethod.AB_TEST, effect_size=EffectSize.LARGE)
        assert r_small.recommended_n > r_large.recommended_n

    def test_medium_effect_n_positive(self):
        r = result(ResearchMethod.AB_TEST, effect_size=EffectSize.MEDIUM)
        assert r.recommended_n > 0

    def test_large_effect_n_positive(self):
        r = result(ResearchMethod.AB_TEST, effect_size=EffectSize.LARGE)
        assert r.recommended_n > 0

    def test_total_is_even(self):
        # total = 2 × per arm
        r = result(ResearchMethod.AB_TEST)
        assert r.recommended_n % 2 == 0

    def test_higher_power_higher_n(self):
        r_80 = result(ResearchMethod.AB_TEST, power=0.80)
        r_90 = result(ResearchMethod.AB_TEST, power=0.90)
        assert r_90.recommended_n > r_80.recommended_n

    def test_method_type_quantitative(self):
        r = result(ResearchMethod.AB_TEST)
        assert r.method_type == MethodType.QUANTITATIVE

    def test_recommended_ge_min(self):
        r = result(ResearchMethod.AB_TEST)
        assert r.recommended_n >= r.min_n

    def test_actual_power_set(self):
        r = result(ResearchMethod.AB_TEST, power=0.80)
        assert r.actual_power == 0.80


# --------------------------------------------------------------------------- #
# Experiment
# --------------------------------------------------------------------------- #


class TestExperiment:
    def test_small_effect_higher_n(self):
        r_small = result(ResearchMethod.EXPERIMENT, effect_size=EffectSize.SMALL)
        r_large = result(ResearchMethod.EXPERIMENT, effect_size=EffectSize.LARGE)
        assert r_small.recommended_n > r_large.recommended_n

    def test_medium_n_positive(self):
        r = result(ResearchMethod.EXPERIMENT, effect_size=EffectSize.MEDIUM)
        assert r.recommended_n > 0

    def test_total_is_even(self):
        r = result(ResearchMethod.EXPERIMENT)
        assert r.recommended_n % 2 == 0

    def test_higher_power_higher_n(self):
        r_80 = result(ResearchMethod.EXPERIMENT, power=0.80)
        r_90 = result(ResearchMethod.EXPERIMENT, power=0.90)
        assert r_90.recommended_n > r_80.recommended_n

    def test_method_type_quantitative(self):
        r = result(ResearchMethod.EXPERIMENT)
        assert r.method_type == MethodType.QUANTITATIVE

    def test_recommended_ge_min(self):
        r = result(ResearchMethod.EXPERIMENT)
        assert r.recommended_n >= r.min_n

    def test_actual_power_set(self):
        r = result(ResearchMethod.EXPERIMENT, power=0.85)
        assert r.actual_power == 0.85


# --------------------------------------------------------------------------- #
# Correlation
# --------------------------------------------------------------------------- #


class TestCorrelation:
    def test_small_effect_higher_n(self):
        r_small = result(ResearchMethod.CORRELATION, effect_size=EffectSize.SMALL)
        r_large = result(ResearchMethod.CORRELATION, effect_size=EffectSize.LARGE)
        assert r_small.recommended_n > r_large.recommended_n

    def test_minimum_20(self):
        r = result(ResearchMethod.CORRELATION, effect_size=EffectSize.LARGE)
        assert r.recommended_n >= 20
        assert r.min_n >= 20

    def test_medium_n_positive(self):
        r = result(ResearchMethod.CORRELATION)
        assert r.recommended_n > 0

    def test_method_type_quantitative(self):
        r = result(ResearchMethod.CORRELATION)
        assert r.method_type == MethodType.QUANTITATIVE

    def test_recommended_ge_min(self):
        r = result(ResearchMethod.CORRELATION)
        assert r.recommended_n >= r.min_n

    def test_rationale_contains_fisher(self):
        r = result(ResearchMethod.CORRELATION)
        assert "Fisher" in r.rationale


# --------------------------------------------------------------------------- #
# All-methods smoke tests
# --------------------------------------------------------------------------- #


class TestAllMethods:
    @pytest.mark.parametrize("method", list(ResearchMethod))
    def test_calculate_returns_result(self, method):
        r = calculate(SampleSizeInput(method=method))
        assert r is not None

    @pytest.mark.parametrize("method", list(ResearchMethod))
    def test_result_has_positive_n(self, method):
        r = calculate(SampleSizeInput(method=method))
        assert r.recommended_n > 0
        assert r.min_n > 0
        assert r.max_n > 0

    @pytest.mark.parametrize("method", list(ResearchMethod))
    def test_result_has_rationale(self, method):
        r = calculate(SampleSizeInput(method=method))
        assert r.rationale

    @pytest.mark.parametrize("method", list(ResearchMethod))
    def test_result_has_power_notes(self, method):
        r = calculate(SampleSizeInput(method=method))
        assert r.power_notes

    @pytest.mark.parametrize("method", list(ResearchMethod))
    def test_min_le_recommended_le_max(self, method):
        r = calculate(SampleSizeInput(method=method))
        assert r.min_n <= r.recommended_n <= r.max_n
