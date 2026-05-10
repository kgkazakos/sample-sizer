# sample-sizer

> AI-assisted sample size calculator for product research — 10 methods, power curves, LLM narratives.

**CPR Orbital Tool 21 · S4: Research ops**

Deciding on sample size is one of the most contested moments in research planning. The stat formulas feel detached from qualitative reality. The "just use 5 users" heuristic gets overextended into contexts it was never designed for. And stakeholders always want a confident number before you've had a chance to think it through.

`sample-sizer` covers 10 research methods — qualitative, quantitative, and everything in between — and gives you a justified recommendation with the reasoning behind it. Power curves for quantitative methods. Saturation guidance for qualitative ones. Optional LLM backend for plain-language narratives that non-researchers can actually act on.

---

## Features

- **10 research methods** — interviews, focus groups, diary studies, usability testing (formative / summative / benchmark), card sorting, tree testing, surveys, A/B tests, controlled experiments, and correlation studies
- **Method-aware rationale** — each recommendation cites the methodological literature behind it (Nielsen, Guest, Cochran, Cohen, Tullis, etc.)
- **Power curves** — interactive Streamlit visualisation of the power vs N trade-off for quantitative methods
- **Saturation curves** — illustrative thematic saturation trajectory for qualitative methods
- **Finite population correction** — Cochran's formula with correction for bounded populations
- **LLM narrative enrichment** — optional DSPy module (OpenAI / Anthropic / Gemini) generates plain-language stakeholder-ready explanations
- **CLI + JSON** — pipe results into CI pipelines, research ops tooling, or other CPR tools
- **Zero API calls by default** — fully functional rule-based core; LLMs are opt-in

---

## Install

```bash
pip install sample-sizer            # rule-based core + CLI
pip install "sample-sizer[app]"     # + Streamlit UI
pip install "sample-sizer[llm]"     # + LLM enrichment (DSPy)
pip install "sample-sizer[all]"     # everything
```

---

## Usage

### CLI

```bash
# Basic calculation
sample-sizer calculate interviews

# With parameters
sample-sizer calculate interviews --homogeneity heterogeneous

# Usability test — benchmark goal
sample-sizer calculate usability_test --usability-goal benchmark

# Survey with finite population correction
sample-sizer calculate survey --margin-of-error 0.03 --population 2000

# A/B test — 90% power, small effect
sample-sizer calculate ab_test --power 0.90 --effect-size small

# JSON output (CI-friendly)
sample-sizer calculate experiment --json-output

# With LLM narrative
sample-sizer calculate interviews \
  --goal "Understand why enterprise users abandon onboarding at step 3" \
  --llm-backend anthropic
```

### Batch mode

```bash
# Run a JSON array of method configs
sample-sizer batch methods.json --output results.json
```

`methods.json`:
```json
[
  {"method": "interviews", "homogeneity": "mixed"},
  {"method": "survey", "margin_of_error": 0.05, "population_size": 5000},
  {"method": "ab_test", "effect_size": "medium", "power": 0.80}
]
```

### Streamlit UI

```bash
streamlit run -m sample_sizer.app
# or
python -m streamlit run sample_sizer/app.py
```

### Python API

```python
from sample_sizer import calculate
from sample_sizer.models import ResearchMethod, SampleSizeInput, Homogeneity

result = calculate(SampleSizeInput(
    method=ResearchMethod.INTERVIEWS,
    homogeneity=Homogeneity.MIXED,
))

print(result.recommended_n)  # 18
print(result.rationale)
print(result.caveats)
```

---

## Methods covered

| Method | Type | Key parameter |
|--------|------|---------------|
| `interviews` | Qualitative | `--homogeneity` |
| `focus_groups` | Qualitative | `--homogeneity` |
| `diary_study` | Qualitative | `--homogeneity` |
| `usability_test` | Qualitative | `--usability-goal` |
| `card_sorting` | Qualitative | `--homogeneity` |
| `tree_testing` | Quantitative | `--margin-of-error`, `--confidence` |
| `survey` | Quantitative | `--margin-of-error`, `--proportion`, `--population` |
| `ab_test` | Quantitative | `--effect-size`, `--power` |
| `experiment` | Quantitative | `--effect-size`, `--power` |
| `correlation` | Quantitative | `--effect-size`, `--power` |

---

## LLM backends

Set the appropriate API key environment variable before use:

| Backend | Flag | Env var |
|---------|------|---------|
| OpenAI | `--llm-backend openai` | `OPENAI_API_KEY` |
| Anthropic | `--llm-backend anthropic` | `ANTHROPIC_API_KEY` |
| Google Gemini | `--llm-backend gemini` | `GEMINI_API_KEY` |

LLM enrichment is implemented via [DSPy](https://dspy.ai/) with `ChainOfThought`. It is **not tested in CI** — treat it as a community extension point.

---

## Development

```bash
git clone https://github.com/kgkazakos/sample-sizer
cd sample-sizer
pip install -e ".[dev]"
pytest tests/ -v
ruff check sample_sizer/
```

---

## Part of the CPR Ecosystem

`sample-sizer` is **Tool 21** in the [CPR Orbital](https://github.com/kgkazakos) 40-tool series — a portfolio of open-source Python tools for AI-native product research, shipping almost daily from March to December 2026.

**Related tools:**
- [`guide-scorer`](https://github.com/kgkazakos/guide-scorer) — score discussion guides before you run the study that needs this sample
- [`research-rubric`](https://github.com/kgkazakos/research-rubric) — evaluate research quality after the study is done
- [`power-analyst`](https://github.com/kgkazakos/power-analyst) — deeper statistical power analysis for experimental designs
- [`study-planner`](https://github.com/kgkazakos/study-planner) *(upcoming)* — full study scoping with sample size as one input

**Computational Product Research (CPR)** is an independent discipline built around AI-native tooling for systematic product research. Learn more at [github.com/kgkazakos](https://github.com/kgkazakos).

---

## License

MIT © Kostas Kazakos
