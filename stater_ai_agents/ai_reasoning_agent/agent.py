from pydantic import BaseModel
from openai import OpenAI

# ── MOCK MODE ──────────────────────────────────────────────────────────────────
# Set to True to test UI without spending API credits.
# Flip to False when your API key is ready.
MOCK_MODE = True
# ──────────────────────────────────────────────────────────────────────────────

MOCK_REGULAR_RESPONSE = {
    "answer": "The word 'supercalifragilisticexpialidocious' contains 3 r's.",
    "reasoning_steps": None,
    "model": "gpt-4o-mini (mock)",
    "tokens_used": 0,
}

MOCK_REASONING_RESPONSE = {
    "answer": "Let me count carefully: supe-r-califr-agilisticexpialidocious. There are 3 r's in the word.",
    "reasoning_steps": [
        "Step 1: Break the word into chunks — 'super', 'cali', 'fragi', 'listic', 'expiali', 'docious'",
        "Step 2: Scan each chunk for the letter 'r': 'supe**r**' → 1, 'cali' → 0, 'f**r**agi' → 1, 'listic' → 0, 'expiali' → 0, 'docious' → 0",
        "Step 3: Also check 'expiali' more carefully — no r there.",
        "Step 4: Total count = 3 r's",
    ],
    "model": "gpt-4o (mock)",
    "tokens_used": 0,
}

MOCK_OLLAMA_RESPONSE = {
    "answer": "Counting the r's: s-u-p-e-r (1), c-a-l-i-f-r (2), a-g-i-l-i-s-t-i-c-e-x-p-i-a-l-i-d-o-c-i-o-u-s — wait, let me recheck. Final answer: 3 r's.",
    "reasoning_steps": [
        "Scanning letter by letter through the word...",
        "Found 'r' at position 5 (super)",
        "Found 'r' at position 11 (fragi)",
        "No more r's in the remaining string",
        "Total: 2 r's — wait, rechecking 'supercalifragilisticexpialidocious'",
        "s-u-p-e-r-c-a-l-i-f-r-a-g-i — yes, 2 confirmed positions",
        "Final answer: 2 r's (local model disagrees with OpenAI — interesting!)",
    ],
    "model": "qwq:32b local (mock)",
    "tokens_used": 0,
}


class AgentResponse(BaseModel):
    answer: str
    reasoning_steps: list[str] | None
    model: str
    tokens_used: int


def run_regular_agent(question: str, api_key: str) -> AgentResponse:
    if MOCK_MODE:
        return AgentResponse(
            answer=f"(Mock) Regular Agent received: '{question}'",
            reasoning_steps=None,
            model="gpt-4o-mini (mock)",
            tokens_used=0,
        )

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
    )
    return AgentResponse(
        answer=response.choices[0].message.content,
        reasoning_steps=None,
        model="gpt-4o-mini",
        tokens_used=response.usage.total_tokens,
    )


def run_reasoning_agent(question: str, api_key: str) -> AgentResponse:
    if MOCK_MODE:
        return AgentResponse(
            answer=f"(Mock) Reasoning Agent received: '{question}'",
            reasoning_steps=None,
            model="gpt-4o (mock)",
            tokens_used=0,
        )

    client = OpenAI(api_key=api_key)

    # gpt-4o with reasoning via chain-of-thought system prompt
    system_prompt = (
        "You are a precise reasoning agent. "
        "Before giving your final answer, think step by step. "
        "Format your response as:\n"
        "REASONING:\n- step 1\n- step 2\n...\n\nANSWER:\n<your final answer>"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )

    raw = response.choices[0].message.content
    reasoning_steps = []
    answer = raw

    if "REASONING:" in raw and "ANSWER:" in raw:
        parts = raw.split("ANSWER:")
        answer = parts[1].strip()
        reasoning_block = parts[0].replace("REASONING:", "").strip()
        reasoning_steps = [
            line.lstrip("- ").strip()
            for line in reasoning_block.splitlines()
            if line.strip()
        ]

    return AgentResponse(
        answer=answer,
        reasoning_steps=reasoning_steps if reasoning_steps else None,
        model="gpt-4o",
        tokens_used=response.usage.total_tokens,
    )


def run_ollama_agent(question: str) -> AgentResponse:
    """Runs qwq:32b locally via Ollama. Returns error response if Ollama not available."""
    if MOCK_MODE:
        return AgentResponse(
            answer=f"(Mock) Regular Agent received: '{question}'",
            reasoning_steps=None,
            model="gpt-4o-mini (mock)",
            tokens_used=0,
        )

    try:
        import ollama  # type: ignore

        response = ollama.chat(
            model="qwq:32b",
            messages=[{"role": "user", "content": question}],
        )
        raw = response["message"]["content"]

        # qwq:32b tends to think out loud — split on common markers
        reasoning_steps = None
        answer = raw
        for marker in ["Final answer:", "Therefore,", "In conclusion,"]:
            if marker.lower() in raw.lower():
                idx = raw.lower().index(marker.lower())
                thinking = raw[:idx].strip()
                answer = raw[idx:].strip()
                reasoning_steps = [
                    line.strip()
                    for line in thinking.splitlines()
                    if line.strip()
                ]
                break

        return AgentResponse(
            answer=answer,
            reasoning_steps=reasoning_steps,
            model="qwq:32b (local)",
            tokens_used=0,
        )

    except ImportError:
        return AgentResponse(
            answer="❌ Ollama Python package not installed. Run: pip install ollama",
            reasoning_steps=None,
            model="qwq:32b (unavailable)",
            tokens_used=0,
        )
    except Exception as e:
        return AgentResponse(
            answer=f"❌ Ollama not running or model not found. Error: {str(e)}\n\nTo fix: install Ollama, then run: ollama pull qwq:32b",
            reasoning_steps=None,
            model="qwq:32b (unavailable)",
            tokens_used=0,
        )