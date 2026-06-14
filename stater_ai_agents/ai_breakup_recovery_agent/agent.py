from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.anthropic import Claude
from agno.tools.duckduckgo import DuckDuckGoTools
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

# ── MOCK MODE ──────────────────────────────────────────────────────────────────
# Set to True to run without API keys (for development/testing)
# Set to False to use real Gemini + Anthropic APIs
MOCK_MODE = True
# ──────────────────────────────────────────────────────────────────────────────


# ── PYDANTIC MODELS ────────────────────────────────────────────────────────────

class EmotionalProfile(BaseModel):
    """Output from Red Flags Agent — drives tone of all other agents."""
    severity: str                        # "low" | "medium" | "high" | "crisis"
    emotional_state: str                 # plain English summary of how user feels
    red_flags_detected: list[str]        # toxic patterns found in text/screenshots
    needs_helpline: bool                 # True if situation is serious
    helpline_region: str                 # "india" | "global" | "both"
    suggested_tone: str                  # "gentle" | "brutal" | "crisis-support"
    raw_analysis: str                    # full Claude response text


class AgentResponse(BaseModel):
    """Standard response from each of the 4 Gemini agents."""
    agent_name: str
    content: str
    error: Optional[str] = None


# ── HELPLINE DATA ──────────────────────────────────────────────────────────────

HELPLINES = {
    "india": [
        {"name": "iCall (Mental Health)", "number": "9152987821", "hours": "Mon–Sat, 8am–10pm"},
        {"name": "Vandrevala Foundation", "number": "1860-2662-345", "hours": "24/7"},
        {"name": "AASRA (Suicide Prevention)", "number": "9820466627", "hours": "24/7"},
        {"name": "Snehi", "number": "044-24640050", "hours": "24/7"},
    ],
    "global": [
        {"name": "Crisis Text Line", "number": "Text HOME to 741741", "hours": "24/7"},
        {"name": "International Association for Suicide Prevention", "number": "https://www.iasp.info/resources/Crisis_Centres/", "hours": "24/7"},
        {"name": "Befrienders Worldwide", "number": "https://www.befrienders.org", "hours": "24/7"},
    ]
}


# ── MOCK RESPONSES ─────────────────────────────────────────────────────────────

def mock_emotional_profile(user_input: str) -> EmotionalProfile:
    return EmotionalProfile(
        severity="medium",
        emotional_state=f"User seems hurt and confused based on: '{user_input[:80]}...' " if len(user_input) > 80 else f"User seems hurt based on: '{user_input}'",
        red_flags_detected=["Excessive blame on self", "Signs of emotional dependency"],
        needs_helpline=False,
        helpline_region="both",
        suggested_tone="gentle",
        raw_analysis="[MOCK MODE] This is a simulated emotional profile. Flip MOCK_MODE = False to use real Claude analysis."
    )

def mock_agent_response(agent_name: str, user_input: str) -> AgentResponse:
    responses = {
        "Therapist Agent": f"[MOCK] I hear you. What you're going through with '{user_input[:60]}' is real and valid. You're not alone in this.",
        "Closure Agent": f"[MOCK] Here's an unsent message template based on your situation: 'I needed you to know how I felt...' — use this for emotional release, not to actually send.",
        "Glow Up Agent": f"[MOCK] Your 7-day glow up plan starts today. Day 1: No checking their profile. Day 2: One new thing you've been postponing...",
        "Brutal Honesty Agent": f"[MOCK] Straight talk: based on what you shared, there were patterns here that weren't working. Here's what the data says about why relationships fail this way...",
    }
    return AgentResponse(
        agent_name=agent_name,
        content=responses.get(agent_name, f"[MOCK] Response from {agent_name}"),
    )


# ── AGENT INITIALIZERS ─────────────────────────────────────────────────────────

def initialize_gemini_agents(gemini_api_key: str) -> tuple:
    """Initialize the 4 Gemini-powered agents."""
    try:
        model = Gemini(id="gemini-2.0-flash-exp", api_key=gemini_api_key)

        therapist_agent = Agent(
            model=model,
            name="Therapist Agent",
            instructions=[
                "You are an empathetic therapist specializing in heartbreak recovery.",
                "Your tone adapts based on the emotional profile provided in the prompt.",
                "1. Validate feelings without toxic positivity",
                "2. Use gentle humor only if the profile indicates low/medium severity",
                "3. In crisis situations, be calm, grounding, and directive",
                "4. Never minimize pain — acknowledge it first, then offer hope",
                "5. Analyze both text and image inputs for emotional context",
            ],
            markdown=True
        )

        closure_agent = Agent(
            model=model,
            name="Closure Agent",
            instructions=[
                "You are a closure specialist helping people process unspoken feelings.",
                "1. Create templates for messages that should NEVER be sent — for catharsis only",
                "2. Offer journaling prompts for emotional release",
                "3. Suggest closure rituals (letter burning, voice memos, etc.)",
                "4. Adapt tone based on severity — softer for high severity cases",
                "5. Always remind user these are for internal healing, not to be sent",
            ],
            markdown=True
        )

        glow_up_agent = Agent(
            model=model,
            name="Glow Up Agent",
            instructions=[
                "You are a post-breakup glow up coach — practical, energizing, real.",
                "1. Design a 7-day recovery challenge with specific daily tasks",
                "2. Include social media detox strategy with clear rules",
                "3. Suggest a healing playlist (genres/moods, not specific songs)",
                "4. Focus on self-investment: skills, body, social life, creativity",
                "5. Keep it motivating but realistic — no toxic positivity",
            ],
            markdown=True
        )

        brutal_honesty_agent = Agent(
            model=model,
            name="Brutal Honesty Agent",
            tools=[DuckDuckGoTools()],
            instructions=[
                "You are a no-BS relationship analyst.",
                "1. Give raw, objective feedback about what went wrong",
                "2. Use research and data to back up your points",
                "3. Call out both sides — the ex AND the user's own patterns",
                "4. Provide clear, actionable steps to avoid repeating this",
                "5. End with reasons why this ending is actually an opportunity",
                "Never sugarcoat. Never blame only one side.",
            ],
            markdown=True
        )

        return therapist_agent, closure_agent, glow_up_agent, brutal_honesty_agent

    except Exception as e:
        logger.error(f"Error initializing Gemini agents: {str(e)}")
        return None, None, None, None


def initialize_claude_agent(anthropic_api_key: str) -> Optional[Agent]:
    """Initialize the Red Flags Agent powered by Claude."""
    try:
        claude_model = Claude(id="claude-sonnet-4-6", api_key=anthropic_api_key)

        red_flags_agent = Agent(
            model=claude_model,
            name="Red Flags Agent",
            instructions=[
                "You are a sensitive emotional intelligence analyst.",
                "Your job is to read between the lines — not just what the user says, but HOW they say it.",
                "",
                "ANALYZE:",
                "1. The user's own words — word choice, self-blame patterns, desperation signals",
                "2. Chat screenshots if provided — look for manipulation, gaslighting, love bombing, stonewalling",
                "3. The TYPE of questions being asked — are they asking 'how do I move on' or 'how do I get them back'?",
                "",
                "OUTPUT a structured assessment with:",
                "- severity: low / medium / high / crisis",
                "- emotional_state: plain English summary of how the user actually feels",
                "- red_flags_detected: list of specific toxic patterns found",
                "- needs_helpline: true if user shows signs of crisis, self-harm ideation, or severe distress",
                "- helpline_region: detect from context clues (language, currency mentions, place names) — india / global / both",
                "- suggested_tone: gentle / brutal / crisis-support",
                "- raw_analysis: your full human-readable analysis",
                "",
                "Be compassionate but precise. This profile drives how ALL other agents respond.",
                "If severity is 'crisis', always set needs_helpline to true.",
            ],
            markdown=True
        )

        return red_flags_agent

    except Exception as e:
        logger.error(f"Error initializing Claude agent: {str(e)}")
        return None


# ── IMAGE PROCESSING ───────────────────────────────────────────────────────────

def process_uploaded_images(uploaded_files: list) -> list:
    """Convert Streamlit uploaded files to Agno Image objects."""
    from agno.media import Image as AgnoImage

    processed = []
    for file in uploaded_files:
        try:
            temp_path = os.path.join(tempfile.gettempdir(), f"temp_{file.name}")
            with open(temp_path, "wb") as f:
                f.write(file.getvalue())
            processed.append(AgnoImage(filepath=Path(temp_path)))
        except Exception as e:
            logger.error(f"Error processing image {file.name}: {str(e)}")
            continue
    return processed