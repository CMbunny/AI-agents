# AI-agents
A collection of AI agents built with Python — growing list of real-world agent projects.

## Agents

| Agent | Description | Folder |
|---|---|---|
| 🎵 Music Generator Agent | Generates instrumental music from a text prompt using ModelsLab + GPT-4o | [starter_ai_agents/ai_music_generator_agent](starter_ai_agents/ai_music_generator_agent) |
| 🎧 Customer Support Voice Agent | Crawls your docs, answers customer questions in text + voice using GPT-4o + TTS | [voice_ai_agents/customer_support_voice_agent](voice_ai_agents/customer_support_voice_agent) |
| 📊 Data Analysis Agent | Auto-analyzes CSV data with charts + natural language chat using GPT-4o tool calling | [starter_ai_agents/ai_data_analysis_agent](starter_ai_agents/ai_data_analysis_agent) |
| 🗺️ AI Audio Tour Agent | Generates personalized self-guided audio tours for any location using a 7-agent pipeline (Planner, Location Suggestion, Architecture, History, Culture, Culinary, Orchestrator) + TTS. Supports multi-stop selection, personas, languages, PDF export, and tour history | [voice_ai_agents/ai_audio_tour_agent](voice_ai_agents/ai_audio_tour_agent) |
| 🧠 AI Reasoning Agent | Compares regular vs reasoning AI models side by side on any question, with step-by-step thinking chain visible. Optional local model support via Ollama (qwq:32b) | [starter_ai_agents/ai_reasoning_agent](starter_ai_agents/ai_reasoning_agent) |
| 💔 Breakup Recovery Agent | 5-agent recovery squad: emotional profiling (Claude), therapist, closure, glow up plan, and brutal honesty (Gemini). Mode toggle, crisis detection with real helplines, chat screenshot analysis. | starter_ai_agents/ai_breakup_recovery_agent |

## Stack

- Python
- Streamlit (UI)
- OpenAI (GPT-4o, GPT-4o-mini, TTS)
- OpenAI Agents SDK (multi-agent orchestration)
- Plotly (interactive charts)
- Pandas (data manipulation)
- ReportLab (PDF export)
- Ollama (local model support)
- Agno (multi-agent framework)
- Google Gemini 2.0 Flash (Breakup Recovery agents)
- Anthropic Claude Sonnet (Red Flags emotional profiling)
- More tools per agent — see individual READMEs

## More agents coming soon
