# 🎧 AI Audio Tour Agent

A self-guided audio tour generator that creates personalized, natural-sounding audio tours for any location. Built on a multi-agent architecture using the OpenAI Agents SDK — each agent specializes in a domain (History, Architecture, Culture, Culinary), runs concurrently, and the results are assembled into a single cohesive audio experience.

---

## 🚀 Features

- **Multi-Agent Architecture** — Planner, specialist agents, and an Orchestrator work together to produce a complete tour
- **Concurrent Agent Execution** — All specialist agents run in parallel for faster generation
- **Live Web Search** — Each agent fetches up-to-date information about your location at runtime
- **Smart Time Allocation** — Planner agent distributes time based on your interests, not just equally
- **Expressive TTS** — Audio generated using `gpt-4o-mini-tts` with three selectable voice styles
- **Customizable** — Choose location, interests, duration (5–60 min), and guide personality
- **Download Support** — Save your audio tour as an MP3

---

## 🧠 Agent Architecture

```
User Input (location, interests, duration)
        │
        ▼
  Planner Agent          ← Allocates time per section based on interests
        │
        ▼
┌───────────────────────────────────┐
│  Concurrent Specialist Agents     │
│  ┌────────────┐ ┌──────────────┐  │
│  │ History    │ │ Architecture │  │
│  └────────────┘ └──────────────┘  │
│  ┌────────────┐ ┌──────────────┐  │
│  │  Culture   │ │   Culinary   │  │
│  └────────────┘ └──────────────┘  │
└───────────────────────────────────┘
        │
        ▼
  Orchestrator Agent     ← Adds intro, transitions, conclusion
        │
        ▼
     TTS Model           ← Converts to natural speech (MP3)
```

---

## 📁 Project Structure

```
ai_audio_tour_agent/
├── ai_audio_tour_agent.py   # Streamlit UI
├── agent.py                 # All agent definitions and Pydantic models
├── manager.py               # Orchestration logic and async execution
├── printer.py               # Terminal progress display (Rich)
└── requirements.txt         # Dependencies
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/CMbunny/AI-agents.git
cd AI-agents/voice_ai_agents/ai_audio_tour_agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get your OpenAI API Key

Sign up at [platform.openai.com](https://platform.openai.com/) and generate an API key.

### 4. Run the app

```bash
streamlit run ai_audio_tour_agent.py
```

### 5. Enter your API key in the sidebar

The app will prompt you for your OpenAI API key in the sidebar. It is never stored on disk.

---

## 🎮 How to Use

1. Enter a location (e.g. `Jaipur`, `Eiffel Tower`, `Brooklyn`)
2. Select your interests — History, Architecture, Culinary, Culture
3. Set your tour duration using the slider (5–60 minutes)
4. Pick a voice style for your guide
5. Click **Generate Tour**
6. Read the tour text or listen to the audio player
7. Download the MP3 if you want to take it with you

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Web UI |
| OpenAI Agents SDK | Multi-agent orchestration |
| GPT-4o / GPT-4o-mini | Content generation |
| GPT-4o-mini-tts | Text to speech |
| WebSearchTool | Live location data |
| Pydantic | Structured agent outputs |
| Rich | Terminal progress display |

---

## 📦 Requirements

```
openai==1.68.2
openai-agents==0.0.6
pydantic==2.10.6
pydantic_core==2.27.2
python-dotenv==1.0.1
rich==13.9.4
streamlit==1.43.2
```

---

## ⚠️ Notes

- Each tour generation makes multiple API calls (Planner + up to 4 specialist agents + Orchestrator + TTS). Costs will vary based on duration and number of interests selected.
- Audio files are saved locally with timestamps to avoid overwrites. Clean them up periodically if running many tours.
- The `printer.py` terminal display is active during generation — you'll see live progress in your terminal while the Streamlit UI shows a spinner.