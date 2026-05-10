"""Core data models for sample-sizer."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ResearchMethod(str, Enum):
    INTERVIEWS = "interviews"
    FOCUS_GROUPS = "focus_groups"
    DIARY_STUDY = "diary_study"
    USABILITY_TEST = "usability_test"
    CARD_SORTING = "card_sorting"
    TREE_TESTING = "tree_testing"
    SURVEY = "survey"
    AB_TEST = "ab_test"
    EXPERIMENT = "experiment"
    CORRELATION = "correlation"


class MethodType(str, Enum):
    QUALITATIVE = "qualitative"
    QUANTITATIVE = "quantitative"


class Homogeneity(str, Enum):
    HOMOGENEOUS = "homogeneous"
    MIXED = "mixed"
    HETEROGENEOUS = "heterogeneous"


class EffectSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class UsabilityGoal(str, Enum):
    FORMATIVE = "formative"
    SUMMATIVE = "summative"
    BENCHMARK = "benchmark"


@dataclass
class SampleSizeInput:
    method: ResearchMethod

    # Qualitative params
    homogeneity: Homogeneity = Homogeneity.MIXED
    usability_goal: UsabilityGoal = UsabilityGoal.FORMATIVE

    # Quantitative params
    confidence_level: float = 0.95
    margin_of_error: float = 0.05
    expected_proportion: float = 0.5
    power: float = 0.80
    effect_size: EffectSize = EffectSize.MEDIUM
    population_size: Optional[int] = None

    # Context
    study_goal: str = ""
    llm_backend: Optional[str] = None


@dataclass
class PowerCurvePoint:
    n: int
    power: float


@dataclass
class SampleSizeResult:
    method: ResearchMethod
    method_type: MethodType
    recommended_n: int
    min_n: int
    max_n: int
    rationale: str
    power_notes: str

    caveats: list = field(default_factory=list)
    power_curve: list = field(default_factory=list)  # List[PowerCurvePoint]
    narrative: Optional[str] = None

    # Quantitative extras
    confidence_level: Optional[float] = None
    actual_power: Optional[float] = None
