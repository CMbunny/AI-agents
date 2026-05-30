import os
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# ── MOCK MODE ──
# Set to True to test the UI without an OpenAI API key.
# Set to False when you have your API key in .env — nothing else changes.
MOCK_MODE = False

if not MOCK_MODE:
    from openai import OpenAI
    from tools import TOOL_DEFINITIONS, dispatch_tool
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
else:
    from tools import dispatch_tool

SYSTEM_PROMPT = """
You are a data analysis assistant. You have access to tools that analyze a sales dataset.

When the user asks a question or you need to produce an analysis:
- Call the relevant tool(s) to answer the question.
- After getting tool results, explain the findings in plain English.
- Be concise. Lead with the most important insight.
- If the user asks something you cannot answer with the available tools, say so clearly.

Available data columns: Date, Product, Region, Sales, Profit.
"""


def _mock_auto_analysis(df: pd.DataFrame):
    """Returns real charts + fake summary text. No API call."""
    results = [
        {"tool": "get_summary_stats",        "output": dispatch_tool("get_summary_stats", df)},
        {"tool": "plot_sales_by_product",     "output": dispatch_tool("plot_sales_by_product", df)},
        {"tool": "plot_sales_over_time",      "output": dispatch_tool("plot_sales_over_time", df)},
        {"tool": "plot_profit_by_region",     "output": dispatch_tool("plot_profit_by_region", df)},
    ]
    summary = (
        "📊 [MOCK MODE — no API key] "
        "Analysis complete. Laptop leads in total sales, the North region shows the highest profit, "
        "and sales trend upward through mid-year. Switch MOCK_MODE to False to get real AI insights."
    )
    return results, summary


def _mock_chat(user_message: str, df: pd.DataFrame):
    """Returns a fake chat response. No API call."""
    results = []
    response = (
        f"📊 [MOCK MODE] You asked: '{user_message}'. "
        "This is a placeholder response. Set MOCK_MODE = False in agent.py and add your "
        "OpenAI API key to .env to get real answers."
    )
    return results, response


def run_auto_analysis(df: pd.DataFrame):
    """
    Called once when data is first loaded.
    Returns: (list of tool results, summary text)
    """
    if MOCK_MODE:
        return _mock_auto_analysis(df)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "The dataset has just been loaded. "
                "Please run a complete analysis: get the summary stats, "
                "then generate all three charts (sales by product, sales over time, profit by region). "
                "Call all tools now."
            ),
        },
    ]

    results = []
    text_response = ""

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if message.tool_calls:
            messages.append({"role": "assistant", "content": message.content, "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                }
                for tc in message.tool_calls
            ]})

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                result = dispatch_tool(tool_name, df)
                results.append({"tool": tool_name, "output": result})

                if isinstance(result, dict):
                    tool_result_content = json.dumps(result)
                else:
                    tool_result_content = f"Chart '{tool_name}' generated successfully."

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result_content,
                })
        else:
            text_response = message.content
            break

    return results, text_response


def run_chat(df: pd.DataFrame, chat_history: list, user_message: str):
    """
    Called each time the user sends a message in the chat box.
    Returns: (list of tool results, response text)
    """
    if MOCK_MODE:
        return _mock_chat(user_message, df)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    results = []
    text_response = ""

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if message.tool_calls:
            messages.append({"role": "assistant", "content": message.content, "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                }
                for tc in message.tool_calls
            ]})

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                result = dispatch_tool(tool_name, df)
                results.append({"tool": tool_name, "output": result})

                if isinstance(result, dict):
                    tool_result_content = json.dumps(result)
                else:
                    tool_result_content = f"Chart '{tool_name}' generated successfully."

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result_content,
                })
        else:
            text_response = message.content
            break

    return results, text_response