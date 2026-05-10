"""sample-sizer: AI-assisted sample size calculator for product research."""

from .calculator import calculate
from .models import (
    EffectSize,
    Homogeneity,
    MethodType,
    ResearchMethod,
    SampleSizeInput,
    SampleSizeResult,
    UsabilityGoal,
)

__version__ = "0.1.0"
__all__ = [
    "calculate",
    "EffectSize",
    "Homogeneity",
    "MethodType",
    "ResearchMethod",
    "SampleSizeInput",
    "SampleSizeResult",
    "UsabilityGoal",
]
