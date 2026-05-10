"""Tests for data models."""

import pytest

from sample_sizer.models import (
    EffectSize,
    Homogeneity,
    MethodType,
    PowerCurvePoint,
    ResearchMethod,
    SampleSizeInput,
    SampleSizeResult,
    UsabilityGoal,
)


class TestResearchMethodEnum:
    def test_interviews_value(self):
        assert ResearchMethod.INTERVIEWS == "interviews"

    def test_ab_test_value(self):
        assert ResearchMethod.AB_TEST == "ab_test"

    def test_survey_value(self):
        assert ResearchMethod.SURVEY == "survey"

    def test_experiment_value(self):
        assert ResearchMethod.EXPERIMENT == "experiment"

    def test_correlation_value(self):
        assert ResearchMethod.CORRELATION == "correlation"

    def test_all_methods_count(self):
        assert len(ResearchMethod) == 10

    def test_is_str_enum(self):
        assert isinstance(ResearchMethod.INTERVIEWS, str)


class TestMethodTypeEnum:
    def test_qualitative_value(self):
        assert MethodType.QUALITATIVE == "qualitative"

    def test_quantitative_value(self):
        assert MethodType.QUANTITATIVE == "quantitative"

    def test_is_str_enum(self):
        assert isinstance(MethodType.QUALITATIVE, str)


class TestHomogeneityEnum:
    def test_values(self):
        assert Homogeneity.HOMOGENEOUS == "homogeneous"
        assert Homogeneity.MIXED == "mixed"
        assert Homogeneity.HETEROGENEOUS == "heterogeneous"

    def test_count(self):
        assert len(Homogeneity) == 3


class TestEffectSizeEnum:
    def test_values(self):
        assert EffectSize.SMALL == "small"
        assert EffectSize.MEDIUM == "medium"
        assert EffectSize.LARGE == "large"


class TestUsabilityGoalEnum:
    def test_values(self):
        assert UsabilityGoal.FORMATIVE == "formative"
        assert UsabilityGoal.SUMMATIVE == "summative"
        assert UsabilityGoal.BENCHMARK == "benchmark"


class TestSampleSizeInput:
    def test_defaults(self):
        inp = SampleSizeInput(method=ResearchMethod.INTERVIEWS)
        assert inp.homogeneity == Homogeneity.MIXED
        assert inp.confidence_level == 0.95
        assert inp.margin_of_error == 0.05
        assert inp.power == 0.80
        assert inp.effect_size == EffectSize.MEDIUM
        assert inp.population_size is None
        assert inp.llm_backend is None

    def test_custom(self):
        inp = SampleSizeInput(
            method=ResearchMethod.SURVEY,
            confidence_level=0.99,
            margin_of_error=0.03,
            population_size=5000,
        )
        assert inp.confidence_level == 0.99
        assert inp.population_size == 5000

    def test_study_goal_default(self):
        inp = SampleSizeInput(method=ResearchMethod.AB_TEST)
        assert inp.study_goal == ""


class TestSampleSizeResult:
    def test_defaults(self):
        result = SampleSizeResult(
            method=ResearchMethod.INTERVIEWS,
            method_type=MethodType.QUALITATIVE,
            recommended_n=18,
            min_n=12,
            max_n=25,
            rationale="test",
            power_notes="test",
        )
        assert result.caveats == []
        assert result.power_curve == []
        assert result.narrative is None
        assert result.confidence_level is None
        assert result.actual_power is None

    def test_caveats_not_shared(self):
        r1 = SampleSizeResult(
            method=ResearchMethod.INTERVIEWS,
            method_type=MethodType.QUALITATIVE,
            recommended_n=18,
            min_n=12,
            max_n=25,
            rationale="test",
            power_notes="test",
        )
        r2 = SampleSizeResult(
            method=ResearchMethod.SURVEY,
            method_type=MethodType.QUANTITATIVE,
            recommended_n=100,
            min_n=80,
            max_n=120,
            rationale="test",
            power_notes="test",
        )
        r1.caveats.append("caveat")
        assert len(r2.caveats) == 0


class TestPowerCurvePoint:
    def test_fields(self):
        pt = PowerCurvePoint(n=50, power=0.80)
        assert pt.n == 50
        assert pt.power == 0.80
