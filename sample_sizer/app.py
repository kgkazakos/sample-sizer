"""Streamlit UI for sample-sizer — interactive sample size calculator."""

import plotly.graph_objects as go
import streamlit as st

from .calculator import calculate
from .models import (
    EffectSize,
    Homogeneity,
    MethodType,
    ResearchMethod,
    SampleSizeInput,
    UsabilityGoal,
)
from .power import generate_power_curve

# --------------------------------------------------------------------------- #
# Page config
# --------------------------------------------------------------------------- #

st.set_page_config(
    page_title="sample-sizer · CPR Orbital",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
# Custom CSS (DM Mono / DM Sans, CPR palette)
# --------------------------------------------------------------------------- #

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    code, pre, .stCode {
        font-family: 'DM Mono', monospace !important;
    }

    /* ---- Header ---- */
    .cpr-header {
        display: flex;
        align-items: baseline;
        gap: 10px;
        margin-bottom: 4px;
    }
    .cpr-title {
        font-family: 'DM Mono', monospace;
        font-size: 22px;
        font-weight: 500;
        color: #111;
    }
    .cpr-badge {
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        background: #f0f0f0;
        color: #666;
        padding: 2px 8px;
        border-radius: 20px;
        border: 0.5px solid #ddd;
    }
    .cpr-sub {
        font-size: 13px;
        color: #888;
        margin-bottom: 24px;
    }

    /* ---- Metric cards ---- */
    .metric-row {
        display: flex;
        gap: 12px;
        margin: 16px 0;
    }
    .metric-card {
        flex: 1;
        background: #fafafa;
        border: 0.5px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-card.primary {
        background: #f0faf5;
        border-color: #1D9E75;
        border-left-width: 3px;
    }
    .metric-label {
        font-size: 11px;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
        font-family: 'DM Mono', monospace;
    }
    .metric-value {
        font-family: 'DM Mono', monospace;
        font-size: 36px;
        font-weight: 500;
        color: #111;
        line-height: 1;
    }
    .metric-card.primary .metric-value { color: #1D9E75; }
    .metric-sub {
        font-size: 11px;
        color: #aaa;
        margin-top: 4px;
    }

    /* ---- Type badge ---- */
    .type-badge {
        display: inline-block;
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        padding: 2px 10px;
        border-radius: 20px;
        margin-bottom: 12px;
    }
    .type-qual  { background: #e6f1fb; color: #185FA5; border: 0.5px solid #b5d4f4; }
    .type-quant { background: #faeeda; color: #854f0b; border: 0.5px solid #fac775; }

    /* ---- Section headings ---- */
    .section-head {
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #aaa;
        margin: 20px 0 8px;
    }

    /* ---- Rationale box ---- */
    .rationale-box {
        background: #fafafa;
        border-left: 3px solid #ddd;
        padding: 12px 16px;
        border-radius: 0 6px 6px 0;
        font-size: 13px;
        color: #444;
        line-height: 1.6;
    }

    /* ---- Caveat list ---- */
    .caveat-item {
        font-size: 12.5px;
        color: #555;
        padding: 5px 0;
        border-bottom: 0.5px solid #f0f0f0;
        line-height: 1.5;
    }
    .caveat-item:last-child { border-bottom: none; }

    /* ---- AI narrative ---- */
    .narrative-box {
        background: #f5f0ff;
        border: 0.5px solid #c9b8ef;
        border-left: 3px solid #7F77DD;
        padding: 14px 18px;
        border-radius: 0 6px 6px 0;
        font-size: 13px;
        color: #3d3060;
        line-height: 1.65;
    }

    /* ---- Sidebar ---- */
    .sidebar-section {
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #bbb;
        padding: 12px 0 4px;
    }

    /* Hide default streamlit hamburger menu */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Labels & maps
# --------------------------------------------------------------------------- #

METHOD_LABELS = {
    ResearchMethod.INTERVIEWS: "Semi-structured interviews",
    ResearchMethod.FOCUS_GROUPS: "Focus groups",
    ResearchMethod.DIARY_STUDY: "Diary study",
    ResearchMethod.USABILITY_TEST: "Usability test",
    ResearchMethod.CARD_SORTING: "Card sorting",
    ResearchMethod.TREE_TESTING: "Tree testing",
    ResearchMethod.SURVEY: "Survey",
    ResearchMethod.AB_TEST: "A/B test",
    ResearchMethod.EXPERIMENT: "Controlled experiment",
    ResearchMethod.CORRELATION: "Correlation study",
}

LABEL_TO_METHOD = {v: k for k, v in METHOD_LABELS.items()}
QUALITATIVE = {m for m, t in {
    ResearchMethod.INTERVIEWS: MethodType.QUALITATIVE,
    ResearchMethod.FOCUS_GROUPS: MethodType.QUALITATIVE,
    ResearchMethod.DIARY_STUDY: MethodType.QUALITATIVE,
    ResearchMethod.USABILITY_TEST: MethodType.QUALITATIVE,
    ResearchMethod.CARD_SORTING: MethodType.QUALITATIVE,
}.items()}

QUAL_GROUP = ["Semi-structured interviews", "Focus groups", "Diary study", "Usability test", "Card sorting"]
QUANT_GROUP = ["Tree testing", "Survey", "A/B test", "Controlled experiment", "Correlation study"]

CPR_COLOUR = "#1D9E75"
POWER_LINE = "#7F77DD"

# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #

st.markdown(
    """
    <div class="cpr-header">
        <span class="cpr-title">sample-sizer</span>
        <span class="cpr-badge">CPR Orbital · Tool 21</span>
    </div>
    <div class="cpr-sub">AI-assisted sample size calculator · 10 research methods · power curves included</div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Sidebar — inputs
# --------------------------------------------------------------------------- #

with st.sidebar:
    st.markdown('<div class="sidebar-section">Method</div>', unsafe_allow_html=True)

    group = st.radio(
        "Method type",
        ["Qualitative", "Quantitative"],
        horizontal=True,
        label_visibility="collapsed",
    )
    methods = QUAL_GROUP if group == "Qualitative" else QUANT_GROUP
    method_label = st.selectbox("Research method", methods)
    method = LABEL_TO_METHOD[method_label]
    is_qual = method in QUALITATIVE

    # ---- Qualitative params
    if is_qual:
        st.markdown('<div class="sidebar-section">Qualitative params</div>', unsafe_allow_html=True)
        hom_label = st.select_slider(
            "Participant homogeneity",
            options=["Homogeneous", "Mixed", "Heterogeneous"],
            value="Mixed",
        )
        homogeneity = Homogeneity(hom_label.lower())

        usability_goal = UsabilityGoal.FORMATIVE
        if method == ResearchMethod.USABILITY_TEST:
            ug_map = {"Formative": UsabilityGoal.FORMATIVE, "Summative": UsabilityGoal.SUMMATIVE, "Benchmark": UsabilityGoal.BENCHMARK}
            ug_label = st.selectbox("Usability goal", list(ug_map.keys()))
            usability_goal = ug_map[ug_label]
    else:
        homogeneity = Homogeneity.MIXED
        usability_goal = UsabilityGoal.FORMATIVE

    # ---- Quantitative params
    if not is_qual:
        st.markdown('<div class="sidebar-section">Statistical params</div>', unsafe_allow_html=True)

        confidence = st.select_slider(
            "Confidence level",
            options=[0.90, 0.95, 0.99],
            value=0.95,
            format_func=lambda x: f"{x:.0%}",
        )
        power_target = st.select_slider(
            "Statistical power",
            options=[0.70, 0.75, 0.80, 0.85, 0.90],
            value=0.80,
            format_func=lambda x: f"{x:.0%}",
        )
        effect_map = {"Small": EffectSize.SMALL, "Medium": EffectSize.MEDIUM, "Large": EffectSize.LARGE}
        effect_label = st.select_slider("Effect size", options=list(effect_map.keys()), value="Medium")
        effect_size = effect_map[effect_label]

        if method in (ResearchMethod.SURVEY, ResearchMethod.TREE_TESTING):
            margin_of_error = st.slider("Margin of error", 0.01, 0.15, 0.05, 0.01, format="%.2f")
            proportion = st.slider("Expected proportion", 0.1, 0.9, 0.5, 0.05)
            population = st.number_input("Population size (0 = infinite)", min_value=0, value=0)
            population_size = int(population) if population > 0 else None
        else:
            margin_of_error = 0.05
            proportion = 0.5
            population_size = None
    else:
        confidence = 0.95
        power_target = 0.80
        effect_size = EffectSize.MEDIUM
        margin_of_error = 0.05
        proportion = 0.5
        population_size = None

    # ---- LLM
    st.markdown('<div class="sidebar-section">LLM enrichment (optional)</div>', unsafe_allow_html=True)
    llm_backend = st.selectbox("Backend", ["None", "openai", "anthropic", "gemini"])
    llm_backend = None if llm_backend == "None" else llm_backend
    study_goal = st.text_area(
        "Study goal (for narrative)",
        placeholder="e.g. Understand why enterprise users abandon onboarding after step 3",
        height=80,
    )

# --------------------------------------------------------------------------- #
# Compute
# --------------------------------------------------------------------------- #

inp = SampleSizeInput(
    method=method,
    homogeneity=homogeneity,
    usability_goal=usability_goal,
    confidence_level=confidence,
    margin_of_error=margin_of_error,
    expected_proportion=proportion,
    power=power_target,
    effect_size=effect_size,
    population_size=population_size,
    study_goal=study_goal,
    llm_backend=llm_backend,
)

result = calculate(inp)

# LLM enrichment
if llm_backend:
    with st.spinner("Generating AI narrative…"):
        try:
            from .llm import enrich_with_llm
            result = enrich_with_llm(inp, result, llm_backend)
        except Exception as exc:
            st.warning(f"LLM enrichment failed: {exc}")

# Power curve
power_curve = generate_power_curve(
    method=method,
    effect_size=effect_size,
    alpha=1 - confidence,
    n_range=(5, max(result.max_n * 2, 200)),
    steps=50,
)

# --------------------------------------------------------------------------- #
# Main panel
# --------------------------------------------------------------------------- #

left_col, right_col = st.columns([3, 2], gap="large")

with left_col:
    # Type badge
    if result.method_type == MethodType.QUALITATIVE:
        st.markdown('<span class="type-badge type-qual">Qualitative · Saturation-based</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="type-badge type-quant">Quantitative · Power-based</span>', unsafe_allow_html=True)

    # Metric cards
    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-label">Minimum N</div>
                <div class="metric-value">{result.min_n}</div>
                <div class="metric-sub">viable floor</div>
            </div>
            <div class="metric-card primary">
                <div class="metric-label">Recommended N</div>
                <div class="metric-value">{result.recommended_n}</div>
                <div class="metric-sub">robust target</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Maximum N</div>
                <div class="metric-value">{result.max_n}</div>
                <div class="metric-sub">diminishing returns</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Rationale
    st.markdown('<div class="section-head">Rationale</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rationale-box">{result.rationale}</div>', unsafe_allow_html=True)

    # Power / saturation
    st.markdown('<div class="section-head">Power & saturation notes</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rationale-box">{result.power_notes}</div>', unsafe_allow_html=True)

    # Caveats
    if result.caveats:
        st.markdown('<div class="section-head">Caveats</div>', unsafe_allow_html=True)
        caveat_html = "".join(f'<div class="caveat-item">· {c}</div>' for c in result.caveats)
        st.markdown(caveat_html, unsafe_allow_html=True)

    # AI narrative
    if result.narrative:
        st.markdown('<div class="section-head">AI narrative</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="narrative-box">{result.narrative}</div>', unsafe_allow_html=True)

with right_col:
    # Power curve chart
    if power_curve:
        ns = [p.n for p in power_curve]
        pws = [p.power for p in power_curve]

        fig = go.Figure()

        # Power curve
        fig.add_trace(
            go.Scatter(
                x=ns,
                y=pws,
                mode="lines",
                line=dict(color=POWER_LINE, width=2.5),
                name="Power",
                hovertemplate="n=%{x}<br>power=%{y:.1%}<extra></extra>",
            )
        )

        # 80% power reference line
        fig.add_hline(
            y=0.80,
            line_dash="dash",
            line_color="#ccc",
            line_width=1,
            annotation_text="80% power",
            annotation_position="top right",
            annotation_font_size=10,
            annotation_font_color="#aaa",
        )

        # Recommended N marker
        fig.add_vline(
            x=result.recommended_n,
            line_dash="dot",
            line_color=CPR_COLOUR,
            line_width=1.5,
            annotation_text=f"n={result.recommended_n}",
            annotation_position="top right",
            annotation_font_size=10,
            annotation_font_color=CPR_COLOUR,
        )

        # Recommended N point
        rec_power = next((p.power for p in power_curve if p.n == result.recommended_n), None)
        if rec_power is None and power_curve:
            closest = min(power_curve, key=lambda p: abs(p.n - result.recommended_n))
            rec_power = closest.power

        if rec_power is not None:
            fig.add_trace(
                go.Scatter(
                    x=[result.recommended_n],
                    y=[rec_power],
                    mode="markers",
                    marker=dict(color=CPR_COLOUR, size=10, symbol="circle"),
                    name=f"n={result.recommended_n}",
                    hovertemplate=f"n={result.recommended_n}<br>power={rec_power:.1%}<extra></extra>",
                )
            )

        metric_label = "Power" if result.method_type == MethodType.QUANTITATIVE and method not in (
            ResearchMethod.SURVEY, ResearchMethod.TREE_TESTING
        ) else "CI Precision (proxy)"

        fig.update_layout(
            height=280,
            margin=dict(l=0, r=10, t=28, b=0),
            plot_bgcolor="#fafafa",
            paper_bgcolor="white",
            font=dict(family="DM Sans, sans-serif", size=11, color="#555"),
            title=dict(
                text=f"Power curve · {effect_label} effect (α={1 - confidence:.2f})" if not is_qual else "Power curve",
                font=dict(size=12, color="#777"),
                x=0,
            ),
            xaxis=dict(
                title="Sample size (N)",
                showgrid=True,
                gridcolor="#ececec",
                zeroline=False,
                tickfont=dict(size=10),
            ),
            yaxis=dict(
                title=metric_label,
                range=[0, 1.05],
                tickformat=".0%",
                showgrid=True,
                gridcolor="#ececec",
                zeroline=False,
                tickfont=dict(size=10),
            ),
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        # Qualitative saturation illustration
        import random
        random.seed(method.value)
        n_points = 30
        cumulative = []
        seen = set()
        count = 0
        for i in range(1, n_points + 1):
            new = max(0, int(random.gauss(3, 1.5)) if i < 5 else int(random.gauss(1.5, 1)))
            new = max(0, min(new, 5))
            count += new
            cumulative.append(count)

        # Normalise
        max_themes = max(cumulative)
        saturation = [c / max_themes for c in cumulative]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=list(range(1, n_points + 1)),
                y=saturation,
                mode="lines+markers",
                line=dict(color=CPR_COLOUR, width=2),
                marker=dict(size=5, color=CPR_COLOUR),
                hovertemplate="Participant %{x}<br>Theme coverage: %{y:.0%}<extra></extra>",
            )
        )
        fig.add_hline(
            y=0.85,
            line_dash="dash",
            line_color="#ccc",
            line_width=1,
            annotation_text="85% coverage",
            annotation_position="top right",
            annotation_font_size=10,
            annotation_font_color="#aaa",
        )
        fig.add_vline(
            x=result.recommended_n,
            line_dash="dot",
            line_color=CPR_COLOUR,
            line_width=1.5,
            annotation_text=f"n={result.recommended_n}",
            annotation_position="top right",
            annotation_font_size=10,
            annotation_font_color=CPR_COLOUR,
        )
        fig.update_layout(
            height=280,
            margin=dict(l=0, r=10, t=28, b=0),
            plot_bgcolor="#fafafa",
            paper_bgcolor="white",
            font=dict(family="DM Sans, sans-serif", size=11, color="#555"),
            title=dict(
                text="Thematic saturation curve (illustrative)",
                font=dict(size=12, color="#777"),
                x=0,
            ),
            xaxis=dict(title="Participants", showgrid=True, gridcolor="#ececec", zeroline=False, tickfont=dict(size=10)),
            yaxis=dict(title="Theme coverage", range=[0, 1.05], tickformat=".0%", showgrid=True, gridcolor="#ececec", zeroline=False, tickfont=dict(size=10)),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Method summary card
    st.markdown('<div class="section-head">Method summary</div>', unsafe_allow_html=True)
    summary = {
        "Method": method_label,
        "Type": result.method_type.value.title(),
        "Recommended N": result.recommended_n,
        "Range": f"{result.min_n} – {result.max_n}",
    }
    if result.confidence_level:
        summary["Confidence"] = f"{result.confidence_level:.0%}"
    if result.actual_power:
        summary["Power"] = f"{result.actual_power:.0%}"

    for k, v in summary.items():
        cols = st.columns([2, 3])
        cols[0].markdown(f"<span style='font-size:11px;color:#aaa;font-family:DM Mono,monospace'>{k}</span>", unsafe_allow_html=True)
        cols[1].markdown(f"<span style='font-size:12px;color:#333'>{v}</span>", unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# Footer
# --------------------------------------------------------------------------- #

st.markdown("---")
st.markdown(
    "<span style='font-size:11px;color:#bbb;font-family:DM Mono,monospace'>"
    "sample-sizer · CPR Orbital Tool 21 · "
    "<a href='https://github.com/kgkazakos/sample-sizer' style='color:#bbb'>github.com/kgkazakos/sample-sizer</a>"
    "</span>",
    unsafe_allow_html=True,
)
