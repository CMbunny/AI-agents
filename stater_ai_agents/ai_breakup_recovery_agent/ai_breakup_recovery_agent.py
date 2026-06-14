import streamlit as st
from manager import run_recovery_pipeline
from agent import MOCK_MODE

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="💔 Breakup Recovery Squad",
    page_icon="💔",
    layout="wide"
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Base */
    .main { background-color: #0f0f13; }
    
    /* Cards */
    .agent-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #2a2a4a;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    .agent-card-crisis {
        background: linear-gradient(135deg, #2d0a0a 0%, #1a0a0a 100%);
        border: 1px solid #8b0000;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }

    /* Profile badge */
    .severity-low { color: #4ade80; font-weight: 700; }
    .severity-medium { color: #facc15; font-weight: 700; }
    .severity-high { color: #f97316; font-weight: 700; }
    .severity-crisis { color: #ef4444; font-weight: 700; }

    /* Helpline card */
    .helpline-card {
        background: linear-gradient(135deg, #1a0a2e 0%, #0a0a1e 100%);
        border: 2px solid #7c3aed;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
    }

    /* Mode toggle label */
    .mode-label {
        font-size: 13px;
        color: #888;
        margin-bottom: 4px;
    }
    
    /* Section divider */
    .section-divider {
        border: none;
        border-top: 1px solid #2a2a4a;
        margin: 32px 0;
    }

    /* Mock banner */
    .mock-banner {
        background: linear-gradient(90deg, #1a1a00, #2a2a00);
        border: 1px solid #555500;
        border-radius: 8px;
        padding: 10px 16px;
        color: #cccc00;
        font-size: 13px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ── MOCK BANNER ────────────────────────────────────────────────────────────────

if MOCK_MODE:
    st.markdown("""
    <div class="mock-banner">
        🧪 <strong>Mock Mode ON</strong> — No API calls are being made. 
        Flip <code>MOCK_MODE = False</code> in <code>agent.py</code> to go live.
    </div>
    """, unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("🔑 API Keys")

    if "gemini_key" not in st.session_state:
        st.session_state.gemini_key = ""
    if "anthropic_key" not in st.session_state:
        st.session_state.anthropic_key = ""

    gemini_key = st.text_input(
        "Gemini API Key",
        value=st.session_state.gemini_key,
        type="password",
        help="Used by Therapist, Closure, Glow Up, and Brutal Honesty agents",
        key="gemini_key_widget"
    )
    if gemini_key != st.session_state.gemini_key:
        st.session_state.gemini_key = gemini_key

    anthropic_key = st.text_input(
        "Anthropic API Key",
        value=st.session_state.anthropic_key,
        type="password",
        help="Used by the Red Flags Agent (Claude) for emotional profiling",
        key="anthropic_key_widget"
    )
    if anthropic_key != st.session_state.anthropic_key:
        st.session_state.anthropic_key = anthropic_key

    if not MOCK_MODE:
        if gemini_key and anthropic_key:
            st.success("Both keys provided ✅")
        elif gemini_key:
            st.warning("Anthropic key missing — Red Flags Agent won't run")
        elif anthropic_key:
            st.warning("Gemini key missing — 4 agents won't run")
        else:
            st.info("Enter both keys to activate all 5 agents")
            st.markdown("""
            - [Get Gemini Key](https://makersuite.google.com/app/apikey)
            - [Get Anthropic Key](https://console.anthropic.com/)
            """)

    st.divider()

    st.markdown("**Agents**")
    st.markdown("🔴 Red Flags — *Claude*")
    st.markdown("🤗 Therapist — *Gemini*")
    st.markdown("✍️ Closure — *Gemini*")
    st.markdown("✨ Glow Up — *Gemini*")
    st.markdown("💪 Brutal Honesty — *Gemini*")

    st.divider()
    st.caption("Red Flags Agent runs first and calibrates all others.")


# ── HEADER ─────────────────────────────────────────────────────────────────────

st.title("💔 Breakup Recovery Squad")
st.markdown("**Five AI agents. One goal: get you through this.**")
st.markdown("Share what happened — the squad handles the rest.")

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── MODE TOGGLE ────────────────────────────────────────────────────────────────

st.markdown("<p class='mode-label'>Choose your recovery mode</p>", unsafe_allow_html=True)
mode = st.radio(
    label="Recovery Mode",
    options=["💙 Gentle Mode", "🔥 Brutal Mode"],
    horizontal=True,
    label_visibility="collapsed",
    help="Gentle = empathy first. Brutal = raw truth, no filter."
)
selected_mode = "gentle" if "Gentle" in mode else "brutal"

st.caption(
    "💙 Gentle — empathy, validation, soft guidance." if selected_mode == "gentle"
    else "🔥 Brutal — no sugar-coating. What actually went wrong and why."
)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── INPUT SECTION ──────────────────────────────────────────────────────────────

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("What happened?")
    user_input = st.text_area(
        "Tell us your story",
        height=180,
        placeholder="Tell us what happened, how you're feeling, what's going through your mind. The more you share, the better the squad can help.",
        label_visibility="collapsed"
    )

with col2:
    st.subheader("Upload Chat Screenshots")
    st.caption("Optional — Red Flags Agent will analyze them for patterns.")
    uploaded_files = st.file_uploader(
        "Screenshots",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="screenshots",
        label_visibility="collapsed"
    )
    if uploaded_files:
        for file in uploaded_files:
            st.image(file, caption=file.name, use_container_width=True)

# ── EXAMPLE PROMPTS ────────────────────────────────────────────────────────────

st.markdown("**Not sure where to start? Try one of these:**")
examples = [
    "We were together for 2 years and they just stopped texting me. No explanation.",
    "I keep checking their Instagram every hour and I can't stop.",
    "They said they love me but they're already with someone else.",
    "I think I was the problem in this relationship.",
]

example_cols = st.columns(4)
for i, example in enumerate(examples):
    with example_cols[i]:
        if st.button(example[:45] + "...", key=f"example_{i}", use_container_width=True):
            st.session_state["prefill"] = example

if "prefill" in st.session_state:
    user_input = st.session_state["prefill"]
    del st.session_state["prefill"]
    st.rerun()

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── RUN BUTTON ─────────────────────────────────────────────────────────────────

run_clicked = st.button("Get Your Recovery Plan 💝", type="primary", use_container_width=True)

if run_clicked:
    if not user_input.strip():
        st.warning("Share something first — even a few words is enough to start.")
    elif not MOCK_MODE and not st.session_state.gemini_key:
        st.warning("Enter your Gemini API key in the sidebar.")
    elif not MOCK_MODE and not st.session_state.anthropic_key:
        st.warning("Enter your Anthropic API key in the sidebar.")
    else:
        try:
            # ── STEP 1: Red Flags Agent ────────────────────────────────────────
            with st.spinner("🔴 Red Flags Agent analyzing your situation..."):
                profile, agent_responses, helplines = run_recovery_pipeline(
                    gemini_api_key=st.session_state.gemini_key,
                    anthropic_api_key=st.session_state.anthropic_key,
                    user_input=user_input,
                    uploaded_files=uploaded_files or [],
                    mode=selected_mode,
                )

            # ── CRISIS: Helplines first, always ───────────────────────────────
            if helplines:
                st.markdown("---")
                st.markdown("### 🆘 You don't have to go through this alone")
                st.markdown("Real humans are available right now. Please reach out:")

                for line in helplines:
                    st.markdown(f"""
                    <div class="helpline-card">
                        <strong>{line['name']}</strong><br>
                        📞 {line['number']}<br>
                        <span style='color:#888; font-size:13px'>{line['hours']}</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

            # ── EMOTIONAL PROFILE ──────────────────────────────────────────────
            st.markdown("## 🔴 Emotional Profile")
            st.caption("Analyzed by Claude — this drives how all other agents respond to you.")

            severity_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "crisis": "🔴"}.get(profile.severity, "🟡")
            st.markdown(f"**Severity:** {severity_emoji} `{profile.severity.upper()}`")
            st.markdown(f"**How you're feeling:** {profile.emotional_state}")
            st.markdown(f"**Tone calibrated to:** `{profile.suggested_tone}`")

            if profile.red_flags_detected:
                with st.expander("🚩 Red Flags Detected"):
                    for flag in profile.red_flags_detected:
                        st.markdown(f"- {flag}")

            if profile.raw_analysis and not MOCK_MODE:
                with st.expander("📋 Full Claude Analysis"):
                    st.markdown(profile.raw_analysis)

            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

            # ── AGENT RESPONSES ────────────────────────────────────────────────

            st.markdown("## Your Recovery Plan")
            st.caption("All 4 agents ran concurrently, calibrated to your emotional profile.")

            agent_display = [
                ("Therapist Agent",      "🤗", "Emotional Support"),
                ("Closure Agent",        "✍️", "Finding Closure"),
                ("Glow Up Agent",        "✨", "Your Glow Up Plan"),
                ("Brutal Honesty Agent", "💪", "Brutal Honesty"),
            ]

            for agent_key, emoji, label in agent_display:
                response = agent_responses.get(agent_key)
                if not response:
                    continue

                with st.expander(f"{emoji} {label}", expanded=True):
                    if response.error:
                        st.error(f"Agent failed: {response.error}")
                    else:
                        st.markdown(response.content)

            # ── KEY TAKEAWAY ───────────────────────────────────────────────────
            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            st.info("💡 **Remember:** Healing isn't linear. Some days will be harder than others. That's not failure — that's the process.")

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
            st.caption("Check your API keys and try again. If the issue persists, check the terminal logs.")

# ── FOOTER ─────────────────────────────────────────────────────────────────────

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #555; font-size: 13px;'>
    Made with ❤️ · Powered by Claude + Gemini · <strong>#BreakupRecoverySquad</strong>
</div>
""", unsafe_allow_html=True)