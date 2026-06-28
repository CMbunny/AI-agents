import streamlit as st
from agent import MOCK_MODE
from manager import run_analysis_pipeline, load_history, DEFAULT_ANGLES
from pdf_export import generate_pdf

def _render_results(results: dict, topic: str):
    """Render analysis results and PDF download button."""
    st.caption(f"**Angles searched:** {' · '.join(results['angles_used'])}")

    st.subheader("📊 Trend Analysis & Startup Opportunities")
    st.markdown(results["analysis"])
    st.divider()

    st.subheader("🏢 Competitor Map")
    st.markdown(results["competitors"])
    st.divider()

    with st.expander("📰 Article Summaries (Gemini)", expanded=False):
        st.markdown(results["summaries"])

    with st.expander("🔗 Merged News Collection (Gemini)", expanded=False):
        st.markdown(results["news"])

    st.divider()

    # PDF export
    pdf_bytes = generate_pdf(
        topic=topic,
        timestamp=results.get("timestamp", "N/A"),
        angles_used=results["angles_used"],
        analysis=results["analysis"],
        competitors=results["competitors"],
        summaries=results["summaries"],
        news=results["news"],
    )
    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_bytes,
        file_name=f"startup_trends_{topic.replace(' ', '_')[:40]}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Startup Trend Analysis Agent",
    page_icon="📈",
    layout="wide",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔑 API Keys")
    gemini_api_key = st.text_input("Google Gemini API Key", type="password")
    anthropic_api_key = st.text_input("Anthropic API Key", type="password")

    st.divider()
    st.caption("**Models used:**")
    st.caption("• News Collector → Gemini 2.5 Flash")
    st.caption("• Summary Writer → Gemini 2.5 Flash")
    st.caption("• Trend Analyzer → Claude Sonnet 4.6")
    st.caption("• Competitor Mapper → Claude Sonnet 4.6")

    st.divider()
    st.header("📋 History")
    history = load_history()
    if not history:
        st.caption("No past analyses yet.")
    else:
        for i, entry in enumerate(history):
            if st.button(
                f"🕒 {entry['topic']} — {entry['timestamp']}",
                key=f"history_{i}",
                use_container_width=True,
            ):
                st.session_state["loaded_result"] = entry
                st.session_state["loaded_topic"] = entry["topic"]

# ── Main UI ───────────────────────────────────────────────────────────────────
if MOCK_MODE:
    st.warning("⚠️ MOCK_MODE is ON — returning fake data. Set MOCK_MODE = False in agent.py to go live.")

st.title("AI Startup Trend Analysis Agent 📈")
st.caption(
    "Enter a startup sector or technology. Three AI agents will collect news "
    "across multiple angles, summarize sources, and surface actionable trends and opportunities."
)

# ── Topic input ───────────────────────────────────────────────────────────────
topic = st.text_input(
    "Area of interest",
    placeholder="e.g. AI-powered legal tech, climate fintech, B2B SaaS for SMEs...",
)

example_topics = [
    "AI agents for enterprise automation",
    "Climate tech startups",
    "Healthcare AI diagnostics",
    "Developer tools and infrastructure",
]

st.caption("**Example topics:**")
cols = st.columns(len(example_topics))
for col, example in zip(cols, example_topics):
    if col.button(example, use_container_width=True):
        topic = example

st.divider()

# ── Search angle selection ────────────────────────────────────────────────────
st.subheader("🔎 Search Angles")
st.caption(
    "Select at least 2 default angles. Add a custom angle to reach the minimum of 3 searches."
)

col1, col2, col3 = st.columns(3)
angle_funding = col1.checkbox("💰 Funding & investment news", value=True)
angle_products = col2.checkbox("🚀 Product launches & competitors", value=True)
angle_market = col3.checkbox("📊 Market size & regulations", value=True)

custom_angle = st.text_input(
    "➕ Custom search angle (optional)",
    placeholder="e.g. open source alternatives, Asia market expansion...",
)

# Build final angles list
selected_angles = []
if angle_funding:
    selected_angles.append(DEFAULT_ANGLES[0])
if angle_products:
    selected_angles.append(DEFAULT_ANGLES[1])
if angle_market:
    selected_angles.append(DEFAULT_ANGLES[2])
if custom_angle.strip():
    selected_angles.append(custom_angle.strip())

total_searches = len(selected_angles)

# Live feedback on angle count
if total_searches < 3:
    st.warning(f"⚠️ {total_searches} angle(s) selected — minimum 3 required. Check more boxes or add a custom angle.")
else:
    st.success(f"✅ {total_searches} search angle(s) selected — ready to run.")

st.divider()

# ── Load from history if selected ────────────────────────────────────────────
if "loaded_result" in st.session_state:
    entry = st.session_state["loaded_result"]
    st.info(f"📂 Showing saved result for: **{entry['topic']}** — {entry['timestamp']}")
    _render_results(entry, entry["topic"])
    if st.button("✖ Clear loaded result"):
        del st.session_state["loaded_result"]
        del st.session_state["loaded_topic"]
        st.rerun()
    st.divider()

# ── Run button ────────────────────────────────────────────────────────────────
if st.button("🔍 Run Analysis", type="primary", use_container_width=True):
    if not topic.strip():
        st.warning("Enter a topic before running.")
    elif total_searches < 3:
        st.warning("Select at least 3 search angles before running.")
    elif not MOCK_MODE and not gemini_api_key:
        st.warning("Enter your Google Gemini API key in the sidebar.")
    elif not MOCK_MODE and not anthropic_api_key:
        st.warning("Enter your Anthropic API key in the sidebar.")
    else:
        with st.spinner(f"Running {total_searches}-angle search pipeline... this takes ~90–120 seconds."):
            try:
                results = run_analysis_pipeline(
                    topic=topic.strip(),
                    angles=selected_angles,
                    gemini_api_key=gemini_api_key,
                    anthropic_api_key=anthropic_api_key,
                )

                st.success("Analysis complete.")
                _render_results(results, topic.strip())

            except Exception as e:
                st.error(f"Pipeline failed: {e}")
else:
    st.info("Enter your topic, select search angles, then click **Run Analysis**.")