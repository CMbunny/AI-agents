from concurrent.futures import ThreadPoolExecutor, as_completed
from agent import initialize_agents, MOCK_MODE, MOCK_RESULT
import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")
MAX_HISTORY = 10


def load_history() -> list:
    """Load history from disk. Returns empty list if file doesn't exist."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_to_history(topic: str, angles: list, results: dict) -> None:
    """Append a run to history.json. Keeps only the latest MAX_HISTORY entries."""
    history = load_history()
    entry = {
        "topic": topic,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "angles_used": angles,
        "news": results.get("news", ""),
        "summaries": results.get("summaries", ""),
        "analysis": results.get("analysis", ""),
        "competitors": results.get("competitors", ""),
    }
    history.insert(0, entry)
    history = history[:MAX_HISTORY]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

DEFAULT_ANGLES = [
    "funding and investment news",
    "product launches and competitor activity",
    "market size and regulatory landscape",
]

MAX_COMPETITORS = 5


def _collect_single_angle(news_collector, topic: str, angle: str) -> str:
    """Run news collector for one search angle. Returns raw content string."""
    response = news_collector.run(
        f"Search for recent startup news about '{topic}' specifically focused on: {angle}. "
        f"Return article titles and URLs. Focus on the last 6 months."
    )
    return response.content


def _dedup_merge(results: list[str]) -> str:
    """
    Merge results from multiple angle searches.
    Deduplicates by URL — same URL appearing across angles is included only once.
    Returns a single merged string for the summary writer.
    """
    seen_urls = set()
    merged_lines = []

    for result in results:
        for line in result.splitlines():
            url = None
            if "http" in line:
                parts = line.split()
                for part in parts:
                    if part.startswith("http"):
                        url = part.strip("()[].,")
                        break

            if url:
                if url not in seen_urls:
                    seen_urls.add(url)
                    merged_lines.append(line)
            else:
                merged_lines.append(line)

    return "\n".join(merged_lines)


def _extract_company_names(trend_analyzer, summaries: str, topic: str) -> list[str]:
    """
    Ask Claude to extract the top 5 most-mentioned company names from the summaries.
    Returns a list of company name strings.
    """
    response = trend_analyzer.run(
        f"From the following startup news summaries about '{topic}', "
        f"extract the names of the top {MAX_COMPETITORS} most prominently mentioned companies or startups. "
        f"Return ONLY a plain numbered list of company names, one per line, nothing else. "
        f"Example format:\n1. Salesforce\n2. OpenAI\n\nSummaries:\n{summaries}"
    )
    raw = response.content or ""
    companies = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip leading number + dot (e.g. "1. ", "2. ")
        if line[0].isdigit() and "." in line:
            name = line.split(".", 1)[1].strip()
        else:
            name = line
        if name:
            companies.append(name)
    return companies[:MAX_COMPETITORS]


def _search_single_company(news_collector, company: str, topic: str) -> tuple[str, str]:
    """Search DuckDuckGo for one company. Returns (company_name, search_result)."""
    response = news_collector.run(
        f"Search for recent news about '{company}' in the context of {topic}. "
        f"Find: funding rounds, product updates, valuation, key investors, and any notable risks or challenges. "
        f"Return article titles, URLs, and key facts."
    )
    return company, response.content


def run_competitor_mapping(
    topic: str,
    summaries: str,
    news_collector,
    trend_analyzer,
    competitor_mapper,
) -> str:
    """
    1. Extract top 5 company names from summaries (Claude)
    2. Run parallel DuckDuckGo searches for each company (Gemini/news_collector)
    3. Pass enriched data to competitor_mapper (Claude) for structured profiles
    Returns markdown string with competitor profiles.
    """
    # Step 1: Extract company names
    companies = _extract_company_names(trend_analyzer, summaries, topic)

    if not companies:
        return "_No competitors could be identified from the news summaries._"

    # Step 2: Parallel search per company
    company_data = {}
    with ThreadPoolExecutor(max_workers=len(companies)) as executor:
        futures = {
            executor.submit(_search_single_company, news_collector, company, topic): company
            for company in companies
        }
        for future in as_completed(futures):
            company = futures[future]
            try:
                _, result = future.result()
                company_data[company] = result
            except Exception as e:
                company_data[company] = f"[Search failed: {e}]"

    # Step 3: Build enriched prompt for competitor mapper
    enriched_prompt = f"Topic: {topic}\n\nAnalyze these competitors:\n\n"
    for company, data in company_data.items():
        enriched_prompt += f"## {company}\n{data}\n\n---\n\n"

    response = competitor_mapper.run(enriched_prompt)
    return response.content


def run_analysis_pipeline(
    topic: str,
    angles: list[str],
    gemini_api_key: str,
    anthropic_api_key: str,
) -> dict:
    """
    Full pipeline:
    1. Parallel search across all angles (Gemini)
    2. Dedup + merge results
    3. Summary writer (Gemini) — sequential
    4. Trend analyzer (Claude) — sequential
    5. Competitor mapping (Claude + Gemini) — parallel per company

    Returns dict with keys: news, summaries, analysis, competitors, angles_used
    """
    if MOCK_MODE:
        return {**MOCK_RESULT, "angles_used": angles}

    if len(angles) < 3:
        raise ValueError(f"Minimum 3 search angles required. Got {len(angles)}.")

    news_collector, summary_writer, trend_analyzer, competitor_mapper = initialize_agents(
        gemini_api_key, anthropic_api_key
    )

    # Step 1: Parallel angle searches
    angle_results = {}
    with ThreadPoolExecutor(max_workers=len(angles)) as executor:
        future_to_angle = {
            executor.submit(_collect_single_angle, news_collector, topic, angle): angle
            for angle in angles
        }
        for future in as_completed(future_to_angle):
            angle = future_to_angle[future]
            try:
                angle_results[angle] = future.result()
            except Exception as e:
                angle_results[angle] = f"[Search failed for angle '{angle}': {e}]"

    # Step 2: Dedup + merge
    ordered_results = [angle_results[a] for a in angles]
    merged_news = _dedup_merge(ordered_results)

    # Step 3: Summarize (Gemini)
    summary_response = summary_writer.run(
        f"Read and summarize these articles about '{topic}':\n\n{merged_news}"
    )
    summaries_content = summary_response.content

    # Step 4: Analyze trends (Claude)
    trend_response = trend_analyzer.run(
        f"Analyze the following startup news summaries about '{topic}' "
        f"and identify key trends, market gaps, and opportunities:\n\n{summaries_content}"
    )
    analysis_content = trend_response.content

    # Step 5: Competitor mapping (Claude + Gemini)
    competitors_content = run_competitor_mapping(
        topic=topic,
        summaries=summaries_content,
        news_collector=news_collector,
        trend_analyzer=trend_analyzer,
        competitor_mapper=competitor_mapper,
    )

    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    save_to_history(topic, angles, {
        "news": merged_news,
        "summaries": summaries_content,
        "analysis": analysis_content,
        "competitors": competitors_content,
        "timestamp": ts,
    })

    return {
        "news": merged_news,
        "summaries": summaries_content,
        "analysis": analysis_content,
        "competitors": competitors_content,
        "angles_used": angles,
        "timestamp": ts,
    }