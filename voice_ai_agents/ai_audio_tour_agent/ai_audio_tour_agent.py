import streamlit as st
import asyncio
from manager import TourManager
from agents import set_default_openai_key
import json

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

with st.sidebar:
    st.title("🔑 Settings")
    api_key = st.text_input("OpenAI API Key:", type="password")
    if api_key:
        st.session_state["OPENAI_API_KEY"] = api_key
        st.success("API key saved!")

st.title("🎧 AI Audio Tour Agent")
st.markdown("""
    <div class='welcome-card'>
        <h3>Welcome to your personalized audio tour guide!</h3>
        <p>I'll help you explore any location with an engaging, natural-sounding tour tailored to your interests.</p>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📍 Where would you like to explore?")
    location = st.text_input("", placeholder="Enter a city, landmark, or location...")
    
    st.markdown("### 🎯 What interests you?")
    interests = st.multiselect(
        "",
        options=["History", "Architecture", "Culinary", "Culture"],
        default=["History", "Architecture"],
        help="Select the topics you'd like to learn about"
    )

with col2:
    st.markdown("### ⏱️ Tour Settings")
    duration = st.slider(
        "Tour Duration (minutes)",
        min_value=5,
        max_value=60,
        value=10,
        step=5,
        help="Choose how long you'd like your tour to be"
    )
    
    st.markdown("### 🎙️ Voice Settings")
    voice_style = st.selectbox(
        "Guide's Voice Style",
        options=["Friendly & Casual", "Professional & Detailed", "Enthusiastic & Energetic"],
        help="Select the personality of your tour guide"
    )

if st.button("🎧 Generate Tour", type="primary"):
    if "OPENAI_API_KEY" not in st.session_state:
        st.error("Please enter your OpenAI API key in the sidebar.")
    elif not location:
        st.error("Please enter a location.")
    elif not interests:
        st.error("Please select at least one interest.")
    else:
        set_default_openai_key(st.session_state["OPENAI_API_KEY"])

        try:
            with st.spinner(f"Creating your personalized tour of {location}..."):
                mgr = TourManager()
                final_tour = run_async(
                    mgr.run, location, interests, duration
                )
        except RuntimeError as e:
            st.error(f"Tour generation failed: {str(e)}")
            st.stop()
        except Exception as e:
            st.error("Something went wrong. Please check your API key and try again.")
            st.stop()

        try:
            with st.spinner("🎙️ Generating audio tour..."):
                progress_bar = st.progress(0)
                tour_audio = tts(final_tour,voice_style)
                progress_bar.progress(100)
        except Exception as e:
            st.error("Tour text was generated but audio failed. Try again.")
            st.stop()

        with st.expander("📝 Tour Content", expanded=True):
            st.markdown(final_tour)

        st.markdown("### 🎧 Listen to Your Tour")
        st.audio(tour_audio, format="audio/mp3")

        with open(tour_audio, "rb") as file:
            st.download_button(
                label="📥 Download Audio Tour",
                data=file,
                file_name=f"{location.lower().replace(' ', '_')}_tour.mp3",
                mime="audio/mp3"
            )