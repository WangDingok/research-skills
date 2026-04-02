"""
Async Google Trends Skill (giữ batch + summary)

Yêu cầu:
    pip install google-search-results matplotlib python-dotenv
"""

import os
import json
import math
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
from serpapi import Client
from dotenv import load_dotenv

load_dotenv()


def _create_chart(timeline_data, keyword_str: str) -> str:
    charts_dir = Path("charts")
    charts_dir.mkdir(exist_ok=True)

    dates = []
    values_per_query = []

    # Số query trong batch
    num_queries = len(timeline_data[0]["values"])

    for i in range(num_queries):
        values_per_query.append([])

    for item in timeline_data:
        dates.append(item["date"])
        for i in range(num_queries):
            values_per_query[i].append(
                item["values"][i]["extracted_value"]
            )

    plt.figure(figsize=(12, 6))

    queries = keyword_str.split(", ")
    for i, query in enumerate(queries):
        plt.plot(dates, values_per_query[i], label=query)

    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Interest Score")
    plt.title(f"Google Trends: {keyword_str}")
    plt.legend()
    plt.tight_layout()

    filename = f"{keyword_str.replace(' ', '_').replace(',', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = charts_dir / filename

    plt.savefig(filepath)
    plt.close()

    return str(filepath)


async def search_google_trends_by_keyword(
    keyword: List[str] | str,
    geo: str = "US",
    timeframe: str = "today 1-m",
) -> str:
    """
    Async search Google Trends theo batch 5 keywords.
    Có summary + vẽ biểu đồ.
    Trả về JSON string.
    """

    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return json.dumps({"error": "Missing SERPAPI_API_KEY"})

    client = Client(api_key=api_key)

    kw_list = [keyword] if isinstance(keyword, str) else keyword
    all_batch_results = []

    async def sync_search(q: str):
        return await asyncio.to_thread(
            client.search,
            {
                "engine": "google_trends",
                "q": q,
                "geo": geo,
                "date": timeframe,
                "data_type": "TIMESERIES",
            },
        )

    for i in range(0, len(kw_list), 5):
        batch = kw_list[i:i + 5]
        keyword_str = ", ".join(batch)

        try:
            results = await sync_search(keyword_str)
            data = results.as_dict()

            timeline = data.get("interest_over_time", {}).get("timeline_data", [])
            if not timeline:
                all_batch_results.append({
                    "batch_keywords": keyword_str,
                    "error": "No timeline data"
                })
                continue

            summaries = []

            num_queries = len(timeline[0]["values"])

            for q_index in range(num_queries):
                values = [
                    item["values"][q_index]["extracted_value"]
                    for item in timeline
                ]

                n = len(values)
                avg = sum(values) / n if n > 0 else 0

                variance = sum((x - avg) ** 2 for x in values) / n if n > 0 else 0
                std_dev = math.sqrt(variance)

                stability = "stable" if avg > 0 and (std_dev / avg) <= 0.5 else "volatile"

                quarter = max(1, n // 4)
                early_avg = sum(values[:quarter]) / quarter
                recent_avg = sum(values[-quarter:]) / quarter

                if early_avg > 0:
                    change_pct = ((recent_avg - early_avg) / early_avg) * 100
                else:
                    change_pct = 100.0 if recent_avg > 0 else 0.0

                if change_pct > 20:
                    direction = "rising"
                elif change_pct < -20:
                    direction = "declining"
                else:
                    direction = "flat"

                summaries.append({
                    "query": batch[q_index],
                    "avg_interest": round(avg, 2),
                    "recent_avg": round(recent_avg, 2),
                    "stability": stability,
                    "direction": direction,
                    "change_pct": round(change_pct, 1),
                    "peak_value": max(values),
                    "min_value": min(values),
                })

            chart_path = await asyncio.to_thread(
                _create_chart, timeline, keyword_str
            )

            all_batch_results.append({
                "batch_keywords": keyword_str,
                "summary": summaries,
                "trend_chart_path": chart_path,
            })

        except Exception as e:
            all_batch_results.append({
                "batch_keywords": keyword_str,
                "error": str(e),
            })

    return json.dumps(all_batch_results, ensure_ascii=False)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Search Google Trends by keyword")
    parser.add_argument("--keyword", type=str, required=True, help="Keyword or comma-separated keywords (max 5 per batch)")
    parser.add_argument("--geo", type=str, default="US", help="Geographical location (default: US)")
    parser.add_argument("--timeframe", type=str, default="today 1-m", help="Timeframe for trends (default: today 1-m)")

    args = parser.parse_args()

    result = asyncio.run(search_google_trends_by_keyword(
        keyword=args.keyword,
        geo=args.geo,
        timeframe=args.timeframe,
    ))

    print(result)