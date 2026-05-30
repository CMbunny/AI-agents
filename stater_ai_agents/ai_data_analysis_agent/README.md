# 📊 Data Analysis Agent

An AI-powered data analysis tool built with Python, Streamlit, and OpenAI GPT-4o.

Upload any CSV or use the built-in sales dataset — the agent automatically generates charts and insights, then lets you dig deeper through a natural language chat interface.

---

## What It Does

1. **Auto Analysis** — on load, the agent runs a full analysis: summary stats + 3 interactive charts
2. **Chat** — ask follow-up questions in plain English; the agent decides which tools to call to answer you
3. **Upload your own data** — works with any CSV that has numeric columns

---

## Demo Dataset

Includes a default `default_dataset.csv` with 100 rows of fictional sales data:

| Column | Description |
|--------|-------------|
| Date | Transaction date |
| Product | Product name (Laptop, Phone, Tablet, Monitor, Keyboard) |
| Region | Sales region (North, South, East, West) |
| Sales | Revenue in ₹ |
| Profit | Profit in ₹ |

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| Streamlit | UI framework |
| OpenAI GPT-4o | Agent brain — decides which tools to call |
| Plotly | Interactive charts |
| Pandas | Data manipulation |
| python-dotenv | API key management |

---

## Project Structure

```
data_analysis_agent/
├── app.py                  # Streamlit UI
├── agent.py                # OpenAI agent loop + tool calling logic
├── tools.py                # Predefined analysis tools + tool registry
├── default_dataset.csv     # Sample sales dataset
├── requirements.txt        # Python dependencies
├── .env                    # Your API key (not committed to GitHub)
└── README.md
```

---

## Setup & Running

### 1. Clone the repo

```bash
git clone https://github.com/CMbunny/AI-agents.git
cd AI-agents/data_analysis_agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your OpenAI API key

Create a `.env` file in the `data_analysis_agent/` folder:

```
OPENAI_API_KEY=your_openai_api_key_here
```

> Get your API key at: https://platform.openai.com/api-keys

### 4. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## How the Agent Works

This agent uses **OpenAI tool calling** — a pattern where you give the model a list of functions it can call, and it decides which ones to invoke based on your question.

```
User question
     ↓
GPT-4o reads the question + tool menu
     ↓
GPT-4o says: "call plot_sales_by_product"
     ↓
Python runs the function, returns the result
     ↓
GPT-4o reads the result, writes a response
     ↓
Response + chart shown in UI
```

The agent loop runs until GPT-4o stops calling tools and gives a final text response.

### Available Tools

| Tool | What it does |
|------|-------------|
| `get_summary_stats` | Total sales, profit, best product, best region, margin |
| `plot_sales_by_product` | Bar chart — sales per product |
| `plot_sales_over_time` | Line chart — monthly sales trend |
| `plot_profit_by_region` | Bar chart — profit per region |

---

## Example Questions to Ask

- "Which product is most profitable?"
- "Show me the sales trend"
- "Which region is underperforming?"
- "Compare profit margins across products"

---

## Part of AI Agents Portfolio

This agent is part of a growing collection of AI agents built for learning and portfolio purposes.

| Agent | Description | Folder |
|-------|-------------|--------|
| Music Generator | Generates music recommendations using AI | `starter_ai_agents/` |
| Customer Support Voice Agent | Voice-based support agent with TTS | `voice_ai_agents/` |
| Data Analysis Agent | Auto-analyzes CSV data with charts + chat | `data_analysis_agent/` |

> Repo: [github.com/CMbunny/AI-agents](https://github.com/CMbunny/AI-agents)