import streamlit as st
import asyncio
from manager import TourManager
from agents import set_default_openai_key
from tours import save_tour, get_all_tours, delete_tour, get_tour_by_id
from cost import estimate_cost
from pdf_export import generate_pdf
from agent import MOCK_MODE


def tts(text, voice_style="Friendly & Casual"):
    from pathlib import Path
    from openai import OpenAI
    from datetime import datetime

    voice_instructions = {
        "Friendly & Casual": """You are a friendly and engaging tour guide. Speak naturally and conversationally, as if you're walking alongside the visitor. 
        Use a warm, inviting tone throughout. Avoid robotic or formal language. Make the tour feel like a casual conversation with a knowledgeable friend.
        Use natural transitions between topics and maintain an enthusiastic but relaxed pace.""",

        "Professional & Detailed": """You are a professional and knowledgeable tour guide. Speak clearly and precisely, with authority and depth.
        Use a composed, informative tone throughout. Emphasize important details and historical facts.
        Maintain a measured, deliberate pace that gives the listener time to absorb the information.""",

        "Enthusiastic & Energetic": """You are an energetic and passionate tour guide. Speak with excitement and enthusiasm, as if this is the most amazing place you've ever visited.
        Use a lively, expressive tone throughout. Build excitement around key landmarks and stories.
        Maintain a dynamic, upbeat pace that keeps the listener engaged and eager to learn more."""
    }

    client = OpenAI()
    speech_file_path = Path(__file__).parent / f"speech_tour_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="nova",
        input=text,
        instructions=voice_instructions.get(voice_style, voice_instructions["Friendly & Casual"])
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path


def run_async(func, *args, **kwargs):
    try:
        return asyncio.run(func(*args, **kwargs))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))


st.set_page_config(
    page_title="AI Audio Tour Agent",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🔑 Settings")
    if MOCK_MODE:
        st.warning("🧪 Mock Mode is ON — no API key needed")
    else:
        api_key = st.text_input("OpenAI API Key:", type="password")
        if api_key:
            st.session_state["OPENAI_API_KEY"] = api_key
            st.success("API key saved!")

    st.markdown("---")
    st.markdown("### 📚 My Tours")

    saved_tours = get_all_tours()

    if not saved_tours:
        st.caption("No saved tours yet. Generate one to get started.")
    else:
        for tour in saved_tours:
            col_a, col_b = st.columns([4, 1])
            with col_a:
                label = f"📍 {tour['city']} — {tour['created_at']}"
                if st.button(label, key=f"load_{tour['id']}", use_container_width=True):
                    st.session_state["loaded_tour"] = tour
                    st.rerun()
            with col_b:
                if st.button("🗑️", key=f"delete_{tour['id']}"):
                    delete_tour(tour['id'])
                    if st.session_state.get("loaded_tour", {}).get("id") == tour['id']:
                        del st.session_state["loaded_tour"]
                    st.rerun()        

# ── Header ─────────────────────────────────────────────────────────────────
st.title("🎧 AI Audio Tour Agent")

if MOCK_MODE:
    st.info("🧪 Running in Mock Mode — suggestions and tour content are pre-loaded for Jaipur. Set MOCK_MODE = False in agent.py to use real GPT-4o agents.")

if "loaded_tour" in st.session_state:
    t = st.session_state["loaded_tour"]
    st.markdown(f"### 📍 Loaded Tour: {t['city']} — {t['created_at']}")
    st.caption(f"Stops: {', '.join(t['stops'])} | Interests: {', '.join(t['interests'])} | Language: {t['language']} | Persona: {t['persona']} | Duration: {t['duration']} min")
    with st.expander("📝 Tour Content", expanded=True):
        st.markdown(t["content"])
    if st.button("✖️ Close Loaded Tour"):
        del st.session_state["loaded_tour"]
        st.rerun()
    st.markdown("---")

st.markdown("""
    <div class='welcome-card'>
        <h3>Welcome to your personalized audio tour guide!</h3>
        <p>Enter a city, pick your spots, choose your interests, and get a full audio tour tailored just for you.</p>
    </div>
""", unsafe_allow_html=True)

# ── Phase 1: City + Preference ─────────────────────────────────────────────
st.markdown("### 📍 Where would you like to explore?")

col1, col2 = st.columns([2, 1])

with col1:
    city = st.text_input("", placeholder="Enter a city (e.g. Jaipur, Paris, Tokyo)...")

with col2:
    preference = st.radio(
        "What kind of spots?",
        options=["Popular", "Hidden Gems"],
        horizontal=True,
        help="Popular = iconic must-see spots. Hidden Gems = lesser-known local favourites."
    )

if st.button("🔍 Find Spots", type="secondary"):
    if not city:
        st.error("Please enter a city name.")
    elif not MOCK_MODE and "OPENAI_API_KEY" not in st.session_state:
        st.error("Please enter your OpenAI API key in the sidebar.")
    else:
        if not MOCK_MODE:
            set_default_openai_key(st.session_state["OPENAI_API_KEY"])

        with st.spinner(f"Finding {preference.lower()} spots in {city}..."):
            try:
                mgr = TourManager()
                suggestions = run_async(mgr.get_suggestions, city, preference)
                st.session_state["suggestions"] = suggestions
                st.session_state["city"] = city
                st.session_state["preference"] = preference
            except Exception as e:
                st.error(f"Could not fetch suggestions: {str(e)}")
                st.stop()

# ── Phase 2: Stop Selection ────────────────────────────────────────────────
if "suggestions" in st.session_state:
    suggestions = st.session_state["suggestions"]

    st.markdown(f"### 📌 Select Your Stops — {st.session_state['preference']} spots in {st.session_state['city']}")
    st.caption("Pick the places you want to visit. Select at least one.")

    selected_stops = []
    cols = st.columns(2)

    for i, stop in enumerate(suggestions.stops):
        with cols[i % 2]:
            checked = st.checkbox(
                f"**{stop.name}**",
                value=True,
                key=f"stop_{i}",
                help=stop.description
            )
            st.caption(stop.description)
            if checked:
                selected_stops.append(stop.name)

    # ── Phase 3: Tour Settings + Generate ─────────────────────────────────
    if selected_stops:
        st.markdown("---")
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown("### 🎯 What interests you?")
            interests = st.multiselect(
                "",
                options=["History", "Architecture", "Culinary", "Culture"],
                default=["History", "Architecture"],
                help="Select the topics you'd like to learn about at each stop"
            )

            # Persona to emphasis mapping
            PERSONA_EMPHASIS = {
                    "Friendly Local": "Culture",
                    "History Professor": "History",
                    "Food Critic": "Culinary",
                    "Architecture Enthusiast": "Architecture",
                    "Storyteller": "History"
            }

            # Auto-add emphasized interest if not already selected
            emphasized = PERSONA_EMPHASIS[persona]
            if emphasized not in interests:
                interests = list(interests) + [emphasized]
                st.info(f"✨ {persona} persona detected — **{emphasized}** has been added to your interests automatically.")

       with col_right:
            st.markdown("### ⏱️ Tour Settings")
            duration = st.slider(
                    "Tour Duration (minutes)",
                    min_value=5,
                    max_value=60,
                    value=15,
                    step=5,
                    help="Total duration across all selected stops"
            )

            st.markdown("### 🌐 Language")
            language = st.selectbox(
            "",
                options=[
                "English", "Hindi", "French", "Spanish", "German",
                "Italian", "Portuguese", "Japanese", "Chinese", "Arabic"
                ],
                 help="Language for the tour content"
             )
             
             st.markdown("### 🎭 Tour Persona")
             persona = st.selectbox(
             "",
                options=[
                    "Friendly Local",
                    "History Professor",
                    "Food Critic",
                    "Architecture Enthusiast",
                    "Storyteller"
                    ],
                    help="Choose the personality and style of your tour guide"
                )


            st.markdown("### 🎙️ Voice Style")
            voice_style = st.selectbox(
                    "",
                    options=["Friendly & Casual", "Professional & Detailed", "Enthusiastic & Energetic"],
                    help="Select the personality of your tour guide"
            )

            # ── Live Cost Estimate ─────────────────────────────────────────────────
            st.markdown("### 💰 Estimated Cost")

            if MOCK_MODE:
                st.caption("Cost estimation is shown for reference. No API calls are made in Mock Mode.")

            num_stops = len(selected_stops) if selected_stops else 1
            num_interests = len(interests) if interests else 1

            breakdown = estimate_cost(
                num_stops=num_stops,
                num_interests=num_interests,
                duration=duration,
            )

            col_cost1, col_cost2 = st.columns(2)

            with col_cost1:
                st.metric("Planner", f"${breakdown['planner']:.5f}")
                st.metric("Suggestions", f"${breakdown['suggestions']:.5f}")
                st.metric("Specialist Agents", f"${breakdown['specialist_agents']:.4f}")

            with col_cost2:
                st.metric("Orchestrator", f"${breakdown['orchestrator']:.4f}")
                st.metric("TTS", f"${breakdown['tts']:.4f}")

            st.info(f"**Total Estimated Cost: ${breakdown['total']:.4f} USD**")
            st.caption("Estimates are approximate. Actual cost may vary slightly based on response length.")

        if st.button("🎧 Generate Tour", type="primary"):
            if not interests:
                st.error("Please select at least one interest.")
            else:
                if not MOCK_MODE:
                    set_default_openai_key(st.session_state["OPENAI_API_KEY"])

                try:
                    with st.spinner(f"Creating your tour of {len(selected_stops)} stop(s) in {st.session_state['city']}..."):
                        mgr = TourManager()
                        final_tour = run_async(
                            mgr.run,
                            st.session_state["city"],
                            selected_stops,
                            interests,
                            duration,
                            language,
                            persona
                        )
                except RuntimeError as e:
                    st.error(f"Tour generation failed: {str(e)}")
                    st.stop()
                except Exception as e:
                    st.error("Something went wrong. Please check your API key and try again.")
                    st.stop()

                # Save tour to disk
                save_tour(
                    city=st.session_state["city"],
                    stops=selected_stops,
                    interests=interests,
                    language=language,
                    persona=persona,
                    duration=duration,
                    content=final_tour
                )
                st.success("✅ Tour saved to your history.")

                # Display tour text
                with st.expander("📝 Tour Content", expanded=True):
                st.markdown(final_tour)

                # Audio section
                if MOCK_MODE:
                    st.warning("🧪 Mock Mode — audio generation skipped. Set MOCK_MODE = False in agent.py and add your API key to generate real audio.")
                else:
                    try:
                        with st.spinner("🎙️ Generating audio tour..."):
                            progress_bar = st.progress(0)
                            tour_audio = tts(final_tour, voice_style)
                            progress_bar.progress(100)

                        st.markdown("### 🎧 Listen to Your Tour")
                        st.audio(tour_audio, format="audio/mp3")

                        with open(tour_audio, "rb") as file:
                            st.download_button(
                                label="📥 Download Audio Tour",
                                data=file,
                                file_name=f"{st.session_state['city'].lower().replace(' ', '_')}_tour.mp3",
                                mime="audio/mp3"
                            )
                    except Exception as e:
                        st.error("Tour text was generated but audio failed. Try again.")
                        st.stop()

 # ------------── PDF Export ─────────────────────────────────────────────────────────
                        st.markdown("### 📄 Export Tour as PDF")
                        try:
                            pdf_path = generate_pdf(
                                city=st.session_state["city"],
                                stops=selected_stops,
                                interests=interests,
                                language=language,
                                persona=persona,
                                duration=duration,
                                estimated_cost=breakdown["total"],
                                content=final_tour,
                            )
                            with open(pdf_path, "rb") as f:
                                st.download_button(
                                    label="📥 Download PDF Tour Script",
                                    data=f,
                                    file_name=f"{st.session_state['city'].lower().replace(' ', '_')}_tour.pdf",
                                    mime="application/pdf"
                                )
                        except Exception as e:
                            st.error(f"PDF generation failed: {str(e)}")