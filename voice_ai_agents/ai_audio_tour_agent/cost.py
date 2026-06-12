# Cost estimates based on OpenAI pricing (mid-2025)
# GPT-4o: $5/1M input, $15/1M output
# GPT-4o-mini: $0.15/1M input, $0.60/1M output
# TTS gpt-4o-mini-tts: $15/1M characters

GPT4O_INPUT = 5.00 / 1_000_000
GPT4O_OUTPUT = 15.00 / 1_000_000
GPT4O_MINI_INPUT = 0.15 / 1_000_000
GPT4O_MINI_OUTPUT = 0.60 / 1_000_000
TTS_PER_CHAR = 15.00 / 1_000_000

WORDS_PER_MINUTE = 150
CHARS_PER_WORD = 5


def estimate_cost(
    num_stops: int,
    num_interests: int,
    duration: int,
) -> dict:
    """
    Returns a cost breakdown and total estimated cost in USD.
    """

    total_words = duration * WORDS_PER_MINUTE
    words_per_section = total_words // max(num_interests, 1)

    # ── Planner Agent (GPT-4o) ─────────────────────────────────────────────
    planner_input_tokens = 300
    planner_output_tokens = 150
    planner_cost = (
        planner_input_tokens * GPT4O_INPUT +
        planner_output_tokens * GPT4O_OUTPUT
    )

    # ── Location Suggestion Agent (GPT-4o-mini + web search) ──────────────
    suggestion_input_tokens = 500
    suggestion_output_tokens = 300
    suggestion_cost = (
        suggestion_input_tokens * GPT4O_MINI_INPUT +
        suggestion_output_tokens * GPT4O_MINI_OUTPUT
    )

    # ── Specialist Agents (GPT-4o-mini + web search) ───────────────────────
    # Each agent per stop: prompt tokens + output tokens
    tokens_per_section = int(words_per_section * 1.5)
    specialist_input_tokens = 400  # prompt overhead per agent
    specialist_output_tokens = tokens_per_section
    specialist_cost_per_agent = (
        specialist_input_tokens * GPT4O_MINI_INPUT +
        specialist_output_tokens * GPT4O_MINI_OUTPUT
    )
    # Total: num_interests agents × num_stops
    total_specialist_cost = specialist_cost_per_agent * num_interests * num_stops

    # ── Orchestrator Agent (GPT-4o-mini) ───────────────────────────────────
    orchestrator_input_tokens = int(total_words * 1.5) + 500
    orchestrator_output_tokens = int(total_words * 1.5)
    orchestrator_cost = (
        orchestrator_input_tokens * GPT4O_MINI_INPUT +
        orchestrator_output_tokens * GPT4O_MINI_OUTPUT
    )

    # ── TTS (gpt-4o-mini-tts) ─────────────────────────────────────────────
    total_chars = total_words * CHARS_PER_WORD
    tts_cost = total_chars * TTS_PER_CHAR

    # ── Total ──────────────────────────────────────────────────────────────
    total = (
        planner_cost +
        suggestion_cost +
        total_specialist_cost +
        orchestrator_cost +
        tts_cost
    )

    return {
        "planner": round(planner_cost, 5),
        "suggestions": round(suggestion_cost, 5),
        "specialist_agents": round(total_specialist_cost, 5),
        "orchestrator": round(orchestrator_cost, 5),
        "tts": round(tts_cost, 5),
        "total": round(total, 4)
    }