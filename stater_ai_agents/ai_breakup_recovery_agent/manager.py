from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
import logging

from agent import (
    MOCK_MODE,
    EmotionalProfile,
    AgentResponse,
    HELPLINES,
    mock_emotional_profile,
    mock_agent_response,
    initialize_gemini_agents,
    initialize_claude_agent,
    process_uploaded_images,
)

logger = logging.getLogger(__name__)


# ── STEP 1: RED FLAGS AGENT (Claude) ──────────────────────────────────────────

def run_red_flags_agent(
    anthropic_api_key: str,
    user_input: str,
    uploaded_files: list,
    mode: str,  # "gentle" | "brutal"
) -> EmotionalProfile:
    """
    Runs first. Builds emotional profile that drives all other agents.
    Returns EmotionalProfile even in mock mode.
    """
    if MOCK_MODE:
        return mock_emotional_profile(user_input)

    try:
        red_flags_agent = initialize_claude_agent(anthropic_api_key)
        if not red_flags_agent:
            raise ValueError("Failed to initialize Red Flags Agent")

        images = process_uploaded_images(uploaded_files) if uploaded_files else []

        prompt = f"""
Analyze this person's emotional state and situation carefully.

User's message:
\"\"\"{user_input}\"\"\"

User-selected mode: {mode}
(gentle = they want support | brutal = they want raw truth)

Based on your analysis, produce a structured emotional profile.
Detect region from any context clues in their message (place names, language style, currency).
If no region clues exist, default helpline_region to "both".

Be precise. This profile will be used to calibrate how 4 other AI agents respond to this person.
"""

        response = red_flags_agent.run(prompt, images=images)

        # Parse Claude's response into EmotionalProfile
        # Claude is instructed to return structured data — we extract it from markdown
        raw = response.content

        # Build profile from Claude's structured output
        # Claude returns readable text — we parse severity signal words
        severity = _extract_severity(raw)
        needs_helpline = severity == "crisis" or any(
            word in user_input.lower()
            for word in ["hurt myself", "end it", "can't go on", "no reason to live", "disappear"]
        )

        return EmotionalProfile(
            severity=severity,
            emotional_state=_extract_section(raw, "emotional_state"),
            red_flags_detected=_extract_list(raw, "red_flags_detected"),
            needs_helpline=needs_helpline,
            helpline_region=_extract_section(raw, "helpline_region") or "both",
            suggested_tone="crisis-support" if needs_helpline else _extract_section(raw, "suggested_tone") or mode,
            raw_analysis=raw
        )

    except Exception as e:
        logger.error(f"Red Flags Agent error: {str(e)}")
        # Safe fallback — never crash the app on this step
        return EmotionalProfile(
            severity="medium",
            emotional_state="Unable to complete full analysis. Proceeding with care.",
            red_flags_detected=[],
            needs_helpline=False,
            helpline_region="both",
            suggested_tone=mode,
            raw_analysis=f"Analysis error: {str(e)}"
        )


# ── STEP 2: GEMINI AGENTS (concurrent) ────────────────────────────────────────

def run_single_agent(agent, agent_name: str, prompt: str, images: list) -> AgentResponse:
    """Runs one Gemini agent. Called inside ThreadPoolExecutor."""
    try:
        response = agent.run(prompt, images=images)
        return AgentResponse(agent_name=agent_name, content=response.content)
    except Exception as e:
        logger.error(f"{agent_name} error: {str(e)}")
        return AgentResponse(
            agent_name=agent_name,
            content="",
            error=str(e)
        )


def run_gemini_agents(
    gemini_api_key: str,
    user_input: str,
    uploaded_files: list,
    profile: EmotionalProfile,
    mode: str,
) -> dict[str, AgentResponse]:
    """
    Runs all 4 Gemini agents concurrently using ThreadPoolExecutor.
    Each agent receives the emotional profile as context.
    Returns dict of agent_name → AgentResponse.
    """
    if MOCK_MODE:
        results = {}
        agent_names = ["Therapist Agent", "Closure Agent", "Glow Up Agent", "Brutal Honesty Agent"]
        for name in agent_names:
            results[name] = mock_agent_response(name, user_input)
        return results

    therapist, closure, glow_up, brutal = initialize_gemini_agents(gemini_api_key)
    if not all([therapist, closure, glow_up, brutal]):
        raise ValueError("Failed to initialize one or more Gemini agents")

    images = process_uploaded_images(uploaded_files) if uploaded_files else []

    # Profile context injected into every agent prompt
    profile_context = f"""
EMOTIONAL PROFILE (from Red Flags Analysis):
- Severity: {profile.severity}
- Emotional State: {profile.emotional_state}
- Red Flags Detected: {", ".join(profile.red_flags_detected) if profile.red_flags_detected else "None"}
- Suggested Tone: {profile.suggested_tone}
- User Mode: {mode}

Calibrate your response accordingly. If severity is 'crisis', prioritize grounding and safety.
"""

    # Agent-specific prompts
    prompts = {
        "Therapist Agent": (therapist, f"""
{profile_context}

User's message: \"\"\"{user_input}\"\"\"

Provide empathetic support with:
1. Validation of their specific feelings (not generic comfort)
2. Gentle reframe of the situation
3. One grounding technique they can do right now
4. Words of genuine encouragement
"""),

        "Closure Agent": (closure, f"""
{profile_context}

User's message: \"\"\"{user_input}\"\"\"

Help them find closure with:
1. A template for an unsent message (label it clearly as NOT to be sent)
2. Two journaling prompts specific to their situation
3. One closure ritual they can do this week
4. A reframe: what this chapter taught them
"""),

        "Glow Up Agent": (glow_up, f"""
{profile_context}

User's message: \"\"\"{user_input}\"\"\"

Design their recovery with:
1. A 7-day glow up challenge (one specific task per day)
2. Social media detox rules (clear and realistic)
3. A healing playlist mood guide (genres/vibes, not song names)
4. One investment in themselves to start this week
"""),

        "Brutal Honesty Agent": (brutal, f"""
{profile_context}

User's message: \"\"\"{user_input}\"\"\"

Give them the truth:
1. What actually went wrong (both sides, no blame-shifting)
2. Patterns in their own behavior worth examining
3. What research says about this type of relationship dynamic
4. Three concrete things to do differently next time
5. Why this ending is actually the right outcome
"""),
    }

    results = {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(
                run_single_agent,
                agent,
                name,
                prompt,
                images
            ): name
            for name, (agent, prompt) in prompts.items()
        }

        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as e:
                results[name] = AgentResponse(
                    agent_name=name,
                    content="",
                    error=str(e)
                )

    return results


# ── STEP 3: HELPLINE RESOLVER ──────────────────────────────────────────────────

def get_helplines(profile: EmotionalProfile) -> list[dict]:
    """Returns relevant helpline numbers based on detected region."""
    if not profile.needs_helpline:
        return []

    region = profile.helpline_region.lower()

    if region == "india":
        return HELPLINES["india"]
    elif region == "global":
        return HELPLINES["global"]
    else:  # "both" or unknown
        return HELPLINES["india"] + HELPLINES["global"]


# ── MAIN ORCHESTRATOR ──────────────────────────────────────────────────────────

def run_recovery_pipeline(
    gemini_api_key: str,
    anthropic_api_key: str,
    user_input: str,
    uploaded_files: list,
    mode: str,
) -> tuple[EmotionalProfile, dict[str, AgentResponse], list[dict]]:
    """
    Full pipeline:
    1. Red Flags Agent (Claude) → EmotionalProfile
    2. 4 Gemini agents concurrently → responses calibrated to profile
    3. Helpline resolver → returns numbers if needed

    Returns: (profile, agent_responses, helplines)
    """

    # Step 1 — Red Flags (must finish before others start)
    profile = run_red_flags_agent(
        anthropic_api_key=anthropic_api_key,
        user_input=user_input,
        uploaded_files=uploaded_files,
        mode=mode,
    )

    # Step 2 — Gemini agents (concurrent)
    agent_responses = run_gemini_agents(
        gemini_api_key=gemini_api_key,
        user_input=user_input,
        uploaded_files=uploaded_files,
        profile=profile,
        mode=mode,
    )

    # Step 3 — Helplines if needed
    helplines = get_helplines(profile)

    return profile, agent_responses, helplines


# ── HELPERS: Parse Claude's text output ───────────────────────────────────────

def _extract_severity(text: str) -> str:
    text_lower = text.lower()
    for level in ["crisis", "high", "medium", "low"]:
        if level in text_lower:
            return level
    return "medium"  # safe default


def _extract_section(text: str, key: str) -> str:
    """Extracts value after a key label in Claude's response."""
    lines = text.split("\n")
    for line in lines:
        if key.lower().replace("_", " ") in line.lower() or key.lower() in line.lower():
            parts = line.split(":", 1)
            if len(parts) > 1:
                return parts[1].strip().strip("*").strip()
    return ""


def _extract_list(text: str, key: str) -> list[str]:
    """Extracts bullet list items after a key label in Claude's response."""
    lines = text.split("\n")
    collecting = False
    items = []

    for line in lines:
        if key.lower().replace("_", " ") in line.lower() or key.lower() in line.lower():
            collecting = True
            continue
        if collecting:
            stripped = line.strip()
            if stripped.startswith(("-", "•", "*", "1", "2", "3", "4", "5")):
                items.append(stripped.lstrip("-•*0123456789. "))
            elif stripped == "" and items:
                break  # end of list

    return items