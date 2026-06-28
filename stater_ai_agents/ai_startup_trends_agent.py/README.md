# AI Startup Trend Analysis Agent 📈

Identifies emerging trends, market gaps, and startup opportunities in any sector using a 3-agent hybrid pipeline.

## How It Works

Three agents run sequentially, each feeding the next:

| Agent | Model | Task |
|---|---|---|
| News Collector | Gemini 2.0 Flash | DuckDuckGo search for recent articles, funding rounds, and market data |
| Summary Writer | Gemini 2.0 Flash | Reads each article via Newspaper4k and writes concise summaries |
| Trend Analyzer | Claude Sonnet 4.6 | Synthesizes summaries into trends, market gaps, and opportunities |

Gemini handles the mechanical tasks (search + fetch). Claude handles the reasoning-heavy final step where output quality matters most.

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/CMbunny/AI-agents.git
cd AI-agents/starter_ai_agents/ai_startup_trend_analysis_agent
```

### 2. Create and activate a virtual environment
```bash
# macOS/Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run startup_trends_agent.py
```

## API Keys Required

- **Google Gemini API Key** — [Get one here](https://aistudio.google.com/app/apikey)
- **Anthropic API Key** — [Get one here](https://console.anthropic.com/)

Both are entered in the sidebar — never hardcoded.

## Project Structure

```
ai_startup_trend_analysis_agent/
├── agent.py                  # Model init, agent definitions, pipeline logic
├── startup_trends_agent.py   # Streamlit UI
├── requirements.txt
└── README.md
```