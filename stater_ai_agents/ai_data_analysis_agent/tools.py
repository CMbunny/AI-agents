import pandas as pd
import plotly.express as px
import json


def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Returns key summary statistics from the dataframe.
    Answers: total sales, total profit, best product, best region.
    """
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    best_product = df.groupby("Product")["Sales"].sum().idxmax()
    best_region = df.groupby("Region")["Sales"].sum().idxmax()
    avg_profit_margin = round((df["Profit"].sum() / df["Sales"].sum()) * 100, 2)

    return {
        "total_sales": total_sales,
        "total_profit": round(total_profit, 2),
        "best_product": best_product,
        "best_region": best_region,
        "avg_profit_margin_percent": avg_profit_margin,
        "total_rows": len(df),
    }


def plot_sales_by_product(df: pd.DataFrame):
    """
    Returns a Plotly bar chart: total sales grouped by product.
    """
    grouped = df.groupby("Product")["Sales"].sum().reset_index()
    grouped = grouped.sort_values("Sales", ascending=False)

    fig = px.bar(
        grouped,
        x="Product",
        y="Sales",
        title="Total Sales by Product",
        color="Product",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig.update_layout(showlegend=False)
    return fig


def plot_sales_over_time(df: pd.DataFrame):
    """
    Returns a Plotly line chart: total sales over time (by month).
    """
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    grouped = df.groupby("Month")["Sales"].sum().reset_index()

    fig = px.line(
        grouped,
        x="Month",
        y="Sales",
        title="Sales Over Time (Monthly)",
        markers=True,
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plot_profit_by_region(df: pd.DataFrame):
    """
    Returns a Plotly bar chart: total profit grouped by region.
    """
    grouped = df.groupby("Region")["Profit"].sum().reset_index()
    grouped = grouped.sort_values("Profit", ascending=False)

    fig = px.bar(
        grouped,
        x="Region",
        y="Profit",
        title="Total Profit by Region",
        color="Region",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_layout(showlegend=False)
    return fig


# ── TOOL REGISTRY ──
# This is what we pass to the OpenAI agent so it knows what tools exist.
# Think of this as a "menu" the agent reads before deciding what to call.

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_summary_stats",
            "description": "Get key summary statistics from the dataset: total sales, total profit, best product, best region, and average profit margin.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "plot_sales_by_product",
            "description": "Generate a bar chart showing total sales for each product.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "plot_sales_over_time",
            "description": "Generate a line chart showing how total sales changed month by month.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "plot_profit_by_region",
            "description": "Generate a bar chart showing total profit for each region.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


# ── TOOL DISPATCHER ──
# Given a tool name and the dataframe, call the right function.
# The agent returns a tool name → we look it up here and run it.

def dispatch_tool(tool_name: str, df: pd.DataFrame):
    tools = {
        "get_summary_stats": get_summary_stats,
        "plot_sales_by_product": plot_sales_by_product,
        "plot_sales_over_time": plot_sales_over_time,
        "plot_profit_by_region": plot_profit_by_region,
    }

    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")

    return tools[tool_name](df)