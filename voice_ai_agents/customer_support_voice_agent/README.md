# 🎙️ Customer Support Voice Agent

An OpenAI SDK powered customer support agent that delivers voice-powered responses to questions about your knowledge base using OpenAI's GPT-4o and TTS capabilities. The system crawls through documentation websites with Firecrawl, processes the content into a searchable knowledge base with Qdrant, and provides both text and voice responses to user queries.

## Features

- **Knowledge Base Creation**
  - Crawls documentation websites using Firecrawl
  - Stores and indexes content using Qdrant vector database
  - Generates embeddings for semantic search using FastEmbed

- **AI Agent Team**
  - **Documentation Processor**: Analyzes documentation content and generates clear, concise responses to user queries
  - **TTS Agent**: Converts text responses into natural-sounding speech with appropriate pacing and emphasis
  - **Voice Customization**: Supports multiple OpenAI TTS voices:
    - alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse

- **Interactive Interface**
  - Clean Streamlit UI with sidebar configuration
  - Real-time documentation search and response generation
  - Built-in audio player with download capability
  - Progress indicators for system initialization and query processing

## How to Run

1. **Clone the Repository**
   ```bash
   git clone https://github.com/CMbunny/AI-agents.git
   cd AI-agents/voice_ai_agents
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
   - Get OpenAI API key from [OpenAI Platform](https://platform.openai.com)
   - Get Qdrant URL and API key from [Qdrant Cloud](https://cloud.qdrant.io)
   - Get Firecrawl API key from [Firecrawl](https://firecrawl.dev)

4. **Run the Application**
   ```bash
   streamlit run customer_support_voice_agent.py
   ```

5. **Use the Interface**
   - Enter your API keys in the sidebar
   - Input the documentation URL you want the agent to learn from
   - Select your preferred voice from the dropdown
   - Click "Initialize System" to process the documentation
   - Ask questions and receive both text and voice responses

## Tech Stack

| Tool | Purpose |
|---|---|
| OpenAI GPT-4o | Generates answers from documentation |
| OpenAI TTS | Converts answers to voice (MP3) |
| Firecrawl | Scrapes and crawls documentation websites |
| Qdrant | Vector database for storing and searching embeddings |
| FastEmbed | Generates text embeddings locally |
| Streamlit | UI |

## Project Structure

```
voice_ai_agents/
├── customer_support_voice_agent.py   # Main application
├── requirements.txt                  # Dependencies
└── README.md
```