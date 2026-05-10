"""Shared pytest fixtures for sample-sizer tests."""

import pytest

from sample_sizer.models import (
    EffectSize,
    Homogeneity,
    ResearchMethod,
    SampleSizeInput,
    UsabilityGoal,
)


@pytest.fixture
def default_interview_input():
    return SampleSizeInput(method=ResearchMethod.INTERVIEWS)


@pytest.fixture
def default_survey_input():
    return SampleSizeInput(method=ResearchMethod.SURVEY)


@pytest.fixture
def default_ab_input():
    return SampleSizeInput(method=ResearchMethod.AB_TEST)


@pytest.fixture
def default_experiment_input():
    return SampleSizeInput(method=ResearchMethod.EXPERIMENT)


@pytest.fixture
def default_correlation_input():
    return SampleSizeInput(method=ResearchMethod.CORRELATION)


@pytest.fixture
def homogeneous_interview_input():
    return SampleSizeInput(
        method=ResearchMethod.INTERVIEWS,
        homogeneity=Homogeneity.HOMOGENEOUS,
    )


@pytest.fixture
def heterogeneous_interview_input():
    return SampleSizeInput(
        method=ResearchMethod.INTERVIEWS,
        homogeneity=Homogeneity.HETEROGENEOUS,
    )


@pytest.fixture
def all_methods():
    return list(ResearchMethod)
