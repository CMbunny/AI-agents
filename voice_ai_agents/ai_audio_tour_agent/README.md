# 🎧 AI Audio Tour Agent

A self-guided audio tour generator that creates personalized, natural-sounding tours for any location. Built on a multi-agent architecture using the OpenAI Agents SDK — each agent specializes in a domain, runs concurrently, and the results are assembled into a single cohesive audio experience with PDF export.

---

## 🚀 Features

### 🧠 Multi-Agent Architecture
- **Planner Agent** — Allocates time per section based on your interests, not just equally
- **Location Suggestion Agent** — Searches the web and suggests 6 real stops (Popular or Hidden Gems)
- **History Agent** — Delivers historical narratives with an authoritative, professorial voice
- **Architecture Agent** — Highlights design details and structures with a descriptive tone
- **Culture Agent** — Explores local customs and traditions with a warm, respectful voice
- **Culinary Agent** — Describes food culture and recommendations with a passionate voice
- **Orchestrator Agent** — Assembles all content with intro, transitions, and conclusion

### 📍 Multi-Stop Route Planning
- Enter a city and choose between **Popular Spots** or **Hidden Gems**
- The Location Suggestion Agent fetches 6 real stops via live web search
- Select which stops you want using checkboxes — all pre-checked by default
- Each stop gets its own dedicated section in the tour with a natural intro

### ⚡ Concurrent Agent Execution
- All specialist agents run in parallel using `asyncio.gather()`
- Reduces generation time from ~40 seconds to ~10 seconds for a 4-interest tour

### 🌐 Language Selection
- Tour content can be generated in 10 languages: English, Hindi, French, Spanish, German, Italian, Portuguese, Japanese, Chinese, Arabic
- Language instruction is passed directly to each agent prompt

### 🎭 Tour Personas
- Choose a guide personality that changes tone, voice, and content emphasis:

| Persona | Tone | Emphasizes |
|---|---|---|
| Friendly Local | Casual, warm, personal | Culture |
| History Professor | Authoritative, detailed, academic | History |
| Food Critic | Passionate, descriptive, opinionated | Culinary |
| Architecture Enthusiast | Technical, visual, descriptive | Architecture |
| Storyteller | Dramatic, narrative, engaging | History |

- If the persona's emphasized interest isn't selected, it gets added automatically with a UI notice

### 🔊 Expressive TTS
- Audio generated using `gpt-4o-mini-tts` with three selectable voice styles:
  - Friendly & Casual
  - Professional & Detailed
  - Enthusiastic & Energetic

### 💰 Live Cost Estimator
- Shows a real-time cost breakdown before you generate
- Updates automatically as you change duration, stops, and interests
- Breaks down cost by: Planner, Suggestions, Specialist Agents, Orchestrator, TTS

### 📚 Persistent Tour History
- Every generated tour is saved to `tours.json` on disk
- Sidebar shows all past tours, newest first
- Click any saved tour to reload the full content instantly
- Delete tours you no longer need
- Persists across sessions and browser restarts

### 📄 PDF Export
- Download a fully styled PDF of your tour script
- Includes: city title, metadata box, visual route (Stop 1 → Stop 2 → Stop 3), full tour content with stop headers, footer with generation details

---

## 📁 Project Structure

```
ai_audio_tour_agent/
├── ai_audio_tour_agent.py   # Streamlit UI — main app file
├── agent.py                 # All agent definitions and Pydantic models (MOCK_MODE flag here)
├── manager.py               # Orchestration logic, async execution, agent calls
├── tours.py                 # Tour history — save, load, delete (persists to tours.json)
├── cost.py                  # Cost estimation logic
├── pdf_export.py            # PDF generation using ReportLab
├── printer.py               # Terminal progress display using Rich
├── tours.json               # Auto-created on first tour generation
└── requirements.txt         # All dependencies
```

---

## 🧩 Agent Flow

```
User Input (city, preference, stops, interests, persona, language, duration)
        │
        ▼
Location Suggestion Agent    ← Web search → 6 real stops (Popular or Hidden Gems)
        │
        ▼
  Planner Agent              ← Allocates time budget per interest section
        │
        ▼
┌─────────────────────────────────────────────┐
│         Concurrent Specialist Agents         │
│  (one set per stop, all running in parallel) │
│  ┌──────────┐  ┌─────────────┐              │
│  │ History  │  │Architecture │              │
│  └──────────┘  └─────────────┘              │
│  ┌──────────┐  ┌─────────────┐              │
│  │ Culture  │  │  Culinary   │              │
│  └──────────┘  └─────────────┘              │
└─────────────────────────────────────────────┘
        │
        ▼
  Orchestrator Agent         ← Adds intro, stop transitions, conclusion
        │
        ▼
     TTS Model               ← Converts to natural speech (MP3)
        │
        ▼
   PDF Export                ← Styled downloadable tour script
        │
        ▼
   Tour History              ← Saved to tours.json for future sessions
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

Sign up at [platform.openai.com](https://platform.openai.com) and generate an API key.

### 4. Run the app

```bash
streamlit run ai_audio_tour_agent.py
```

### 5. Enter your API key in the sidebar

The app will prompt you for your OpenAI API key in the sidebar. It is never stored on disk.

---

## 🧪 Mock Mode (No API Key Needed)

The app ships with `MOCK_MODE = True` in `agent.py`. In this mode:

- No API calls are made
- Pre-loaded tour content for Jaipur is shown
- The full UI flow works — stop selection, interests, persona, language, cost estimator, PDF export, tour history
- Audio generation is skipped with a clear notice

To go live, change one line in `agent.py`:

```python
MOCK_MODE = False  # was True
```

---

## 🎮 How to Use

1. Enter a city name (e.g. `Jaipur`, `Paris`, `Tokyo`)
2. Choose **Popular Spots** or **Hidden Gems**
3. Click **Find Spots** — 6 stops appear with descriptions
4. Select which stops you want to visit using checkboxes
5. Pick your interests (History, Architecture, Culinary, Culture)
6. Set tour duration (5–60 minutes)
7. Choose a language
8. Choose a tour persona
9. Review the estimated cost
10. Click **Generate Tour**
11. Read the tour text in the expandable section
12. Download the **MP3 audio** or the **PDF tour script**
13. Access any past tour from the **📚 My Tours** sidebar

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Web UI |
| OpenAI Agents SDK | Multi-agent orchestration |
| GPT-4o | Planner agent |
| GPT-4o-mini | All specialist and orchestrator agents |
| GPT-4o-mini-tts | Text to speech |
| WebSearchTool | Live location data per agent |
| Pydantic | Structured agent outputs |
| ReportLab | PDF generation |
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
reportlab==4.1.0
```

---

## ⚠️ Notes

- Each tour makes multiple API calls. Cost depends on number of stops, interests, and duration. Check the live estimator before generating.
- Audio and PDF files are saved locally with timestamps. Clean them up periodically.
- `tours.json` is created automatically on first use. Do not delete it if you want to keep your tour history.
- The `printer.py` terminal display shows live agent progress in your terminal while the Streamlit UI shows a spinner.
- `MOCK_MODE = True` by default — flip to `False` in `agent.py` when your API key is ready.