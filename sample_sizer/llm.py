"""Optional LLM enrichment via DSPy — requires API keys and dspy-ai package."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SampleSizeInput, SampleSizeResult


# --------------------------------------------------------------------------- #
# DSPy module (loaded lazily so rule-based core never imports dspy)
# --------------------------------------------------------------------------- #


def _build_module():  # pragma: no cover
    import dspy

    class _NarrativeSignature(dspy.Signature):
        """
        Generate a plain-language narrative explaining a sample size recommendation
        to a practitioner product researcher.
        """

        method: str = dspy.InputField(desc="Research method name (e.g. semi-structured interviews, A/B test)")
        recommended_n: int = dspy.InputField(desc="Recommended sample size")
        min_n: int = dspy.InputField(desc="Minimum viable sample size")
        max_n: int = dspy.InputField(desc="Maximum practical sample size")
        rationale: str = dspy.InputField(desc="Statistical or methodological rationale")
        study_goal: str = dspy.InputField(desc="The researcher's stated study goal or context")
        narrative: str = dspy.OutputField(
            desc=(
                "2–3 sentence plain-language narrative. Explain why this sample size makes sense "
                "for the stated goal, include one practical implication, and flag the most "
                "important caveat. Write for a product researcher, not a statistician."
            )
        )

    class SampleSizeNarrator(dspy.Module):
        def __init__(self):
            self.generate = dspy.ChainOfThought(_NarrativeSignature)

        def forward(self, inp: "SampleSizeInput", result: "SampleSizeResult") -> str:
            pred = self.generate(
                method=inp.method.value.replace("_", " "),
                recommended_n=result.recommended_n,
                min_n=result.min_n,
                max_n=result.max_n,
                rationale=result.rationale,
                study_goal=inp.study_goal or "general product research",
            )
            return pred.narrative

    return SampleSizeNarrator


# --------------------------------------------------------------------------- #
# Backend configuration
# --------------------------------------------------------------------------- #

_BACKEND_MODELS = {
    "openai": "openai/gpt-4o-mini",
    "anthropic": "anthropic/claude-haiku-4-5-20251001",
    "gemini": "gemini/gemini-2.0-flash",
}


def configure_lm(backend: str) -> None:  # pragma: no cover
    import dspy

    model_str = _BACKEND_MODELS.get(backend, backend)
    lm = dspy.LM(model=model_str)
    dspy.configure(lm=lm)


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #


def enrich_with_llm(
    inp: "SampleSizeInput",
    result: "SampleSizeResult",
    backend: str,
) -> "SampleSizeResult":  # pragma: no cover
    """Attach an LLM-generated narrative to *result* (mutates and returns it)."""
    configure_lm(backend)
    narrator_cls = _build_module()
    narrator = narrator_cls()
    result.narrative = narrator(inp, result)
    return result
