from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.anthropic import Claude
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools

# ── Toggle this to True to skip all API calls and return fake data ──
MOCK_MODE = True

MOCK_RESULT = {
    "news": (
        "**[MOCK] Recent Articles Found:**\n\n"
        "1. 'AI agents are eating enterprise software' — TechCrunch\n"
        "2. 'Series B funding surge in autonomous workflows' — VentureBeat\n"
        "3. 'Why 2025 is the year of agentic AI' — a16z Blog\n"
        "4. 'Startups replacing SaaS with AI-native tools' — Forbes\n"
    ),
    "summaries": (
        "**[MOCK] Article Summaries:**\n\n"
        "**Article 1:** Enterprise AI agent adoption is accelerating, with companies replacing "
        "multi-step manual workflows. Key players include Salesforce, ServiceNow, and dozens of startups.\n\n"
        "**Article 2:** Series B rounds for agentic AI startups averaged $45M in Q1 2025, up 3x YoY. "
        "Investors are targeting vertical-specific agents over general-purpose ones.\n\n"
        "**Article 3:** The a16z thesis: agentic AI unlocks a new software category where the product "
        "is an outcome, not a feature set.\n\n"
        "**Article 4:** Early SaaS replacements are happening in HR, finance, and legal — "
        "sectors with repetitive, rules-based workflows.\n"
    ),
    "analysis": (
        "### Key Trends\n"
        "- Vertical AI agents are outperforming horizontal ones in enterprise adoption\n"
        "- Funding is concentrating in outcome-based pricing models (pay-per-task vs seat licenses)\n"
        "- Legal, HR, and finance are the fastest-moving sectors for AI-native replacement\n\n"
        "### Market Gaps\n"
        "- Mid-market companies (\\$10M-\\$100M ARR) are underserved — most tools target enterprise or SMB\n"
        "- Compliance-aware agents for regulated industries (healthcare, finance) are scarce\n\n"
        "### Startup Opportunities\n"
        "- Build a vertical agent for a single high-value workflow (e.g. contract review, invoice reconciliation)\n"
        "- Target outcome-based pricing from day one — easier to sell and stickier than seat licenses\n\n"
        "### Risk Factors\n"
        "- Foundation model commoditization may erode moats built on model quality alone\n"
        "- Enterprises moving slowly on procurement — long sales cycles despite interest\n"
    ),
    "competitors": (
        "---\n\n"
        "**1. Salesforce (Einstein AI)**\n"
        "- **What they do:** CRM platform with embedded AI agents for sales, service, and marketing automation\n"
        "- **Funding stage:** Public (NYSE: CRM) — $34B annual revenue\n"
        "- **Competitive moat:** Massive enterprise customer base, deep CRM data, 30-year brand trust\n"
        "- **Vulnerability signals:** Slow to ship truly autonomous agents; legacy architecture limits agility\n\n"
        "---\n\n"
        "**2. ServiceNow**\n"
        "- **What they do:** IT workflow automation platform expanding into cross-enterprise AI agents\n"
        "- **Funding stage:** Public (NYSE: NOW) — $10B annual revenue\n"
        "- **Competitive moat:** Dominant in ITSM; deeply embedded in Fortune 500 IT departments\n"
        "- **Vulnerability signals:** High switching cost cuts both ways — hard to displace but hard to expand beyond IT\n\n"
        "---\n\n"
        "**3. Glean**\n"
        "- **What they do:** Enterprise AI search and work assistant connecting all company knowledge\n"
        "- **Funding stage:** Series E — $260M raised, $4.6B valuation\n"
        "- **Competitive moat:** Deep enterprise integrations (100+ connectors); strong security posture\n"
        "- **Vulnerability signals:** Microsoft Copilot is a direct threat given Office 365 install base\n\n"
        "---\n\n"
        "**4. Rippling**\n"
        "- **What they do:** HR, IT, and finance automation platform with AI-native workflows\n"
        "- **Funding stage:** Series F — $1.2B raised, $13.5B valuation\n"
        "- **Competitive moat:** Unified employee data model across HR+IT+Finance — rare combination\n"
        "- **Vulnerability signals:** Burning cash aggressively; faces legal battles with Deel\n\n"
        "---\n\n"
        "**5. Dust**\n"
        "- **What they do:** Platform for building internal AI agents connected to company data\n"
        "- **Funding stage:** Series A — $16M raised\n"
        "- **Competitive moat:** Developer-first, highly customizable; strong in Europe\n"
        "- **Vulnerability signals:** Early stage, limited brand recognition; competing against better-funded players\n"
    ), 
    "timestamp": "2025-01-01 00:00",
}


def initialize_agents(gemini_api_key: str, anthropic_api_key: str) -> tuple[Agent, Agent, Agent, Agent]:
    """
    Initialize all four agents with their respective models.
    - News Collector: Gemini 2.5 Flash (mechanical search task)
    - Summary Writer: Gemini 2.5 Flash (mechanical summarization task)
    - Trend Analyzer: Claude Sonnet 4.6 (insight generation, needs best reasoning)
    - Competitor Mapper: Claude Sonnet 4.6 (extraction + competitive reasoning)
    Returns: (news_collector, summary_writer, trend_analyzer, competitor_mapper)
    """
    gemini_model = Gemini(id="gemini-2.5-flash", api_key=gemini_api_key)
    claude_model = Claude(id="claude-sonnet-4-6", api_key=anthropic_api_key)

    news_collector = Agent(
        name="News Collector",
        role="Collects recent startup news, funding rounds, and market analyses on a given topic",
        tools=[DuckDuckGoTools()],
        model=gemini_model,
        instructions=[
            "Search for recent startup news, funding rounds, product launches, and market analyses on the given topic.",
            "Return a list of article titles and their URLs. Focus on the last 6 months.",
            "Aim for at least 8–10 distinct sources.",
        ],
        markdown=True,
    )

    summary_writer = Agent(
        name="Summary Writer",
        role="Reads and summarizes collected startup news articles",
        tools=[Newspaper4kTools(enable_read_article=True, include_summary=True)],
        model=gemini_model,
        instructions=[
            "Read each article URL provided and extract the key facts.",
            "For each article, write a 3–5 sentence summary covering: what happened, who is involved, and why it matters.",
            "Skip articles you cannot access. Do not fabricate content.",
        ],
        markdown=True,
    )

    trend_analyzer = Agent(
        name="Trend Analyzer",
        role="Identifies emerging startup trends, market gaps, and actionable opportunities",
        model=claude_model,
        instructions=[
            "You are an expert startup analyst. Analyze the provided article summaries.",
            "Identify: (1) recurring patterns across multiple sources, (2) emerging technologies or business models, "
            "(3) underserved market gaps, (4) sectors attracting funding.",
            "Structure your output as: Key Trends → Market Gaps → Startup Opportunities → Risk Factors.",
            "Be specific. Name real companies, funding amounts, or technologies when present in the data.",
            "Do not speculate beyond what the summaries support.",
        ],
        markdown=True,
    )

    competitor_mapper = Agent(
        name="Competitor Mapper",
        role="Maps the competitive landscape by identifying and analyzing key players",
        tools=[DuckDuckGoTools()],
        model=claude_model,
        instructions=[
            "You are a competitive intelligence analyst.",
            "You will be given a list of company names and additional search data about each.",
            "For each company, produce a structured profile with exactly these four fields:",
            "  - What they do: one sentence describing their core product/service",
            "  - Funding stage: latest round, amount raised, and valuation if available",
            "  - Competitive moat: what makes them genuinely hard to displace",
            "  - Vulnerability signals: specific weaknesses, threats, or risks based on the data",
            "Only include facts supported by the search results. Do not speculate.",
            "Format each company as a clearly separated section with its name as a bold header.",
        ],
        markdown=True,
    )

    return news_collector, summary_writer, trend_analyzer, competitor_mapper