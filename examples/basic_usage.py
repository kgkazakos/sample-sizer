"""Basic usage examples for sample-sizer."""

from sample_sizer import calculate
from sample_sizer.models import (
    EffectSize,
    Homogeneity,
    ResearchMethod,
    SampleSizeInput,
    UsabilityGoal,
)

# --------------------------------------------------------------------------- #
# Qualitative — interviews
# --------------------------------------------------------------------------- #

print("=" * 60)
print("Example 1: Semi-structured interviews")
print("=" * 60)

r = calculate(
    SampleSizeInput(
        method=ResearchMethod.INTERVIEWS,
        homogeneity=Homogeneity.MIXED,
        study_goal="Understand why enterprise users abandon checkout at step 3",
    )
)

print(f"Recommended N : {r.recommended_n}")
print(f"Range         : {r.min_n} – {r.max_n}")
print(f"Method type   : {r.method_type.value}")
print(f"Rationale     : {r.rationale[:120]}...")
print()

# --------------------------------------------------------------------------- #
# Qualitative — usability test
# --------------------------------------------------------------------------- #

print("=" * 60)
print("Example 2: Usability test (summative)")
print("=" * 60)

r = calculate(
    SampleSizeInput(
        method=ResearchMethod.USABILITY_TEST,
        usability_goal=UsabilityGoal.SUMMATIVE,
    )
)
print(f"Recommended N : {r.recommended_n}")
print(f"Range         : {r.min_n} – {r.max_n}")
print(f"Power notes   : {r.power_notes[:100]}...")
print()

# --------------------------------------------------------------------------- #
# Quantitative — survey (with finite correction)
# --------------------------------------------------------------------------- #

print("=" * 60)
print("Example 3: Survey with finite population correction")
print("=" * 60)

r = calculate(
    SampleSizeInput(
        method=ResearchMethod.SURVEY,
        confidence_level=0.95,
        margin_of_error=0.05,
        expected_proportion=0.5,
        population_size=2000,
    )
)
print(f"Recommended N : {r.recommended_n}  (vs {385} for infinite population)")
print(f"Range         : {r.min_n} – {r.max_n}")
print()

# --------------------------------------------------------------------------- #
# Quantitative — A/B test
# --------------------------------------------------------------------------- #

print("=" * 60)
print("Example 4: A/B test (medium effect, 80% power)")
print("=" * 60)

r = calculate(
    SampleSizeInput(
        method=ResearchMethod.AB_TEST,
        effect_size=EffectSize.MEDIUM,
        power=0.80,
        confidence_level=0.95,
    )
)
print(f"Recommended N (total) : {r.recommended_n}")
print(f"Per arm               : {r.recommended_n // 2}")
print(f"Power notes           : {r.power_notes[:120]}...")
print()

# --------------------------------------------------------------------------- #
# Power curve (programmatic)
# --------------------------------------------------------------------------- #

print("=" * 60)
print("Example 5: Power curve for correlation study")
print("=" * 60)

from sample_sizer.power import generate_power_curve

pts = generate_power_curve(
    method=ResearchMethod.CORRELATION,
    effect_size=EffectSize.MEDIUM,
    n_range=(20, 200),
    steps=20,
)

for pt in pts[:5]:
    print(f"  n={pt.n:>4}  power={pt.power:.1%}")
print("  ...")
