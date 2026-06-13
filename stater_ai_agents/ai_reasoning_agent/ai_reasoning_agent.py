import streamlit as st
from manager import run_comparison
from agent import MOCK_MODE

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Reasoning Agent",
    page_icon="🧠",
    layout="wide",
)

# ── STYLES ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding-top: 2rem; }

    .agent-card {
        background: #1a1d2e;
        border: 1px solid #2d3154;
        border-radius: 12px;
        padding: 1.4rem;
        margin-bottom: 1rem;
    }
    .agent-card.reasoning-card { border-color: #4f46e5; }
    .agent-card.ollama-card   { border-color: #059669; }

    .agent-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .label-regular   { color: #94a3b8; }
    .label-reasoning { color: #818cf8; }
    .label-ollama    { color: #34d399; }

    .answer-text {
        font-size: 1rem;
        color: #e2e8f0;
        line-height: 1.7;
    }
    .step-item {
        background: #0f1117;
        border-left: 3px solid #4f46e5;
        padding: 0.5rem 0.8rem;
        margin: 0.4rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.88rem;
        color: #cbd5e1;
    }
    .step-item.ollama-step { border-left-color: #059669; }
    .meta-pill {
        display: inline-block;
        background: #2d3154;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        color: #94a3b8;
        margin-right: 6px;
        margin-top: 0.6rem;
    }
    .mock-banner {
        background: linear-gradient(90deg, #78350f, #92400e);
        border: 1px solid #d97706;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        color: #fde68a;
        font-size: 0.88rem;
        margin-bottom: 1.2rem;
    }
    .divider { border-top: 1px solid #2d3154; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 AI Reasoning Agent")
    st.markdown("Compare how different models reason through the same question.")
    st.markdown("---")

    if not MOCK_MODE:
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Your key is never stored.",
        )
    else:
        api_key = "mock"
        st.info("Mock mode is ON — no API key needed.")

    st.markdown("---")
    st.markdown("### ⚙️ Settings")

    include_ollama = st.toggle(
        "Include Local Model (qwq:32b)",
        value=False,
        help="Requires Ollama installed and qwq:32b pulled locally.",
    )

    st.markdown("---")
    st.markdown("### 📖 How it works")
    st.markdown("""
- **Regular Agent** — `gpt-4o-mini`, fast, no explicit reasoning chain
- **Reasoning Agent** — `gpt-4o`, thinks step by step before answering
- **Local Agent** — `qwq:32b` via Ollama, runs 100% on your machine
    """)

    st.markdown("---")
    st.caption("Folder: `starter_ai_agents/ai_reasoning_agent`")
    st.caption("Run: `streamlit run ai_reasoning_agent.py`")

# ── MOCK BANNER ────────────────────────────────────────────────────────────────
if MOCK_MODE:
    st.markdown("""
    <div class="mock-banner">
        ⚠️ <strong>Mock Mode ON</strong> — Responses are hardcoded for UI testing.
        Flip <code>MOCK_MODE = False</code> in <code>agent.py</code> to go live.
    </div>
    """, unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("## 🧠 AI Reasoning Comparison")
st.markdown("Ask any question and see how each model thinks through it.")

# ── QUESTION INPUT ─────────────────────────────────────────────────────────────
question = st.text_area(
    "Your question",
    placeholder="e.g. How many r's are in 'strawberry'? Or: Is it faster to fly or drive from Delhi to Jaipur?",
    height=100,
)

example_questions = [
    "How many r's are in 'strawberry'?",
    "If a train leaves at 9am going 80km/h and another at 10am going 100km/h, when does the second catch up?",
    "Is 1.1 + 2.2 exactly equal to 3.3 in most programming languages? Why?",
    "Which is heavier: a kg of steel or a kg of feathers?",
]

with st.expander("💡 Try an example question"):
    for eq in example_questions:
        if st.button(eq, key=eq):
            question = eq
            st.rerun()

st.markdown("---")

run_button = st.button("▶ Run Comparison", type="primary", use_container_width=True)

# ── RUN ────────────────────────────────────────────────────────────────────────
if run_button:
    if not question.strip():
        st.warning("Please enter a question first.")
        st.stop()

    if not MOCK_MODE and not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        st.stop()

    with st.spinner("Running agents concurrently..."):
        results = run_comparison(
            question=question.strip(),
            api_key=api_key,
            include_ollama=include_ollama,
        )

    st.markdown("### 📊 Results")

    cols = st.columns(3 if include_ollama else 2)

    def render_agent_card(col, label, r, step_color="#4f46e5"):
        with col:
            st.markdown(f"**{label}**")
            st.info(r.answer)
            if r.tokens_used > 0:
                st.caption(f"Model: {r.model} · Tokens: {r.tokens_used}")
            else:
                st.caption(f"Model: {r.model}")
            if r.reasoning_steps:
                with st.expander("🔍 Reasoning Steps"):
                    for i, step in enumerate(r.reasoning_steps, 1):
                        st.markdown(f"`{i}.` {step}")

    render_agent_card(cols[0], "⚡ Regular Agent", results["regular"])
    render_agent_card(cols[1], "🔍 Reasoning Agent", results["reasoning"])

    if include_ollama and "ollama" in results:
        render_agent_card(cols[2], "🖥️ Local Agent (Ollama)", results["ollama"])
    # ── SUMMARY ────────────────────────────────────────────────────────────────
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🔎 Key Takeaway")

    regular_has_reasoning = bool(results["regular"].reasoning_steps)
    reasoning_has_steps = bool(results["reasoning"].reasoning_steps)

    if reasoning_has_steps and not regular_has_reasoning:
        st.success("✅ The Reasoning Agent showed its thinking steps. The Regular Agent gave a direct answer with no visible reasoning.")
    elif reasoning_has_steps:
        st.info("Both agents provided reasoning. Compare the depth of their thinking above.")
    else:
        st.info("Both agents answered directly. Try a harder question to see reasoning steps emerge.")