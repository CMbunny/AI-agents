import asyncio
from concurrent.futures import ThreadPoolExecutor
from agent import run_regular_agent, run_reasoning_agent, run_ollama_agent, AgentResponse


def _run_all_sync(question: str, api_key: str, include_ollama: bool) -> dict[str, AgentResponse]:
    """Runs all agents concurrently using threads (OpenAI SDK is sync)."""

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_regular = executor.submit(run_regular_agent, question, api_key)
        future_reasoning = executor.submit(run_reasoning_agent, question, api_key)
        future_ollama = executor.submit(run_ollama_agent, question) if include_ollama else None

        results = {
            "regular": future_regular.result(),
            "reasoning": future_reasoning.result(),
        }

        if future_ollama:
            results["ollama"] = future_ollama.result()

    return results


def run_comparison(question: str, api_key: str, include_ollama: bool = False) -> dict[str, AgentResponse]:
    """
    Main entry point for the Streamlit UI.
    Runs selected agents concurrently and returns their responses.
    """
    return _run_all_sync(question, api_key, include_ollama)