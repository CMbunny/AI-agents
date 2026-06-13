# 🧠 AI Reasoning Agent

Compare how different AI models reason through the same question — side by side, in a Streamlit UI.

## What it does

Ask any question and see three models work through it:

| Agent | Model | Reasoning |
|---|---|---|
| Regular Agent | gpt-4o-mini | Direct answer, no visible reasoning chain |
| Reasoning Agent | gpt-4o | Step-by-step thinking shown before final answer |
| Local Agent (optional) | qwq:32b via Ollama | Runs 100% on your machine, free |

## Setup

```bash
git clone https://github.com/CMbunny/AI-agents.git
cd starter_ai_agents/ai_reasoning_agent
pip install -r requirements.txt
```

## Run

```bash
streamlit run ai_reasoning_agent.py
```

Stop with `Ctrl + C`.

## Mock Mode

`MOCK_MODE = True` is set by default in `agent.py` — the app runs and echoes your question back with labeled mock responses so you can test the full UI without spending any API credits.

To go live:
1. Open `agent.py`
2. Set `MOCK_MODE = False`
3. Enter your OpenAI API key in the sidebar when the app loads

## UI Features

- **Side-by-side comparison** — Regular Agent and Reasoning Agent in two columns
- **Reasoning steps expander** — click to see the Reasoning Agent's thinking chain
- **Example questions** — expandable list of pre-written test questions
- **Ollama toggle** — enable/disable local model from the sidebar without restarting
- **Mock mode banner** — clearly visible when running without an API key
- **Key Takeaway** — summary below results explaining what differed between agents

## Local Model (Optional)

To enable the `qwq:32b` local agent:
1. Install [Ollama](https://ollama.com)
2. Run: `ollama pull qwq:32b`
3. Toggle "Include Local Model" in the sidebar

If Ollama isn't installed or the model isn't running, the local agent column shows a clear error — the rest of the app keeps working normally.

## Files

| File | Purpose |
|---|---|
| `agent.py` | Agent functions, Pydantic output model, mock responses, `MOCK_MODE` flag |
| `manager.py` | Concurrent execution of all agents via `ThreadPoolExecutor` |
| `ai_reasoning_agent.py` | Streamlit UI — sidebar, question input, results cards, key takeaway |
| `requirements.txt` | Dependencies |

## Dependencies

```
openai
streamlit
python-dotenv
ollama
```