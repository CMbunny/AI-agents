# 💔 Breakup Recovery Squad

An AI-powered breakup recovery app with **5 specialized agents** — built with Streamlit, Agno, Google Gemini, and Anthropic Claude.

The Red Flags Agent (Claude) runs first, builds an emotional profile of the user, and calibrates how all other agents respond. The remaining 4 agents then run concurrently via `ThreadPoolExecutor`.

---

## 🤖 The Squad

| Agent | Model | Role |
|---|---|---|
| 🔴 Red Flags Agent | Claude (Anthropic) | Runs first — analyzes emotional state, detects toxic patterns, triggers helplines if needed |
| 🤗 Therapist Agent | Gemini 2.0 Flash | Empathetic support, validation, grounding techniques |
| ✍️ Closure Agent | Gemini 2.0 Flash | Unsent message templates, journaling prompts, closure rituals |
| ✨ Glow Up Agent | Gemini 2.0 Flash | 7-day recovery challenge, social media detox, self-investment plan |
| 💪 Brutal Honesty Agent | Gemini 2.0 Flash + DuckDuckGo | Raw feedback, pattern analysis, research-backed insights |

---

## 🚀 Features

- **Emotional Profiling** — Claude reads not just what you say, but *how* you say it to build a severity profile (low / medium / high / crisis)
- **Calibrated Responses** — all 4 Gemini agents receive the emotional profile before generating a single word
- **Crisis Detection** — auto-detects serious situations and surfaces real human helpline numbers (India + Global)
- **Mode Toggle** — 💙 Gentle (empathy first) or 🔥 Brutal (no filter, raw truth)
- **Chat Screenshot Analysis** — upload screenshots for Red Flags Agent to analyze toxic patterns
- **Concurrent Execution** — 4 Gemini agents run simultaneously via `ThreadPoolExecutor`
- **Mock Mode** — develop and test without API keys (one line flip)

---

## 🛠️ Tech Stack

- **UI:** Streamlit
- **Agent Framework:** Agno
- **Models:** Gemini 2.0 Flash (Google) + Claude Sonnet (Anthropic)
- **Search:** DuckDuckGo (Brutal Honesty Agent)
- **Concurrency:** ThreadPoolExecutor
- **Validation:** Pydantic v2

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/CMbunny/AI-agents
cd starter_ai_agents/ai_breakup_recovery_agent

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run ai_breakup_recovery_agent.py
```

---

## 🔑 API Keys

Two keys required — enter both in the sidebar:

| Key | Where to get it | Used by |
|---|---|---|
| Gemini API Key | [Google AI Studio](https://makersuite.google.com/app/apikey) | Agents 2–5 |
| Anthropic API Key | [Anthropic Console](https://console.anthropic.com/) | Red Flags Agent |

---

## 🧪 Mock Mode

No API keys? No problem. Open `agent.py` and check line 1:

```python
MOCK_MODE = True   # ← flip to False to go live
```

Mock mode returns simulated responses that echo your actual input — so you can test the full UI flow without spending API credits.

---

## 🏗️ Project Structure

```
ai_breakup_recovery_agent/
├── ai_breakup_recovery_agent.py   ← Streamlit UI (main entry point)
├── agent.py                       ← All 5 agent definitions + Pydantic models
├── manager.py                     ← Pipeline orchestration
├── requirements.txt
└── README.md
```

---

## 🔄 How It Works

```
User Input + Screenshots
        ↓
Red Flags Agent (Claude)
  → Builds EmotionalProfile
  → Detects severity: low / medium / high / crisis
  → Sets suggested_tone for other agents
  → Triggers helplines if needed
        ↓
ThreadPoolExecutor
  → Therapist Agent  ─┐
  → Closure Agent    ─┤ all run concurrently
  → Glow Up Agent    ─┤ each receives EmotionalProfile
  → Brutal Honesty   ─┘
        ↓
Streamlit UI renders results
(helplines shown first if crisis detected)
```

---

## ⚠️ Disclaimer

This app is not a substitute for professional mental health support. If you're in crisis, please reach out to a real human. Helplines are surfaced automatically when the app detects serious distress.