"""
Async Google AI Search Skill (SGE)

Yêu cầu:
    pip install google-search-results python-dotenv
    SERPAPI_API_KEY=...
"""

import os
import json
import asyncio
from typing import Optional

from serpapi import Client
from dotenv import load_dotenv

load_dotenv()


async def google_ai_search(
    query: str,
    geo: str = "US",
    timeout: int = 30,
) -> str:
    """
    Tìm kiếm bằng Google AI Mode (SGE) qua SerpAPI.

    Args:
        query: Từ khóa hoặc câu hỏi tìm kiếm.
        geo: Khu vực địa lý (mặc định "US").
        timeout: Thời gian chờ tối đa (giây).

    Returns:
        JSON string chứa:
            - reconstructed_markdown
            - references
    """

    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return json.dumps({"error": "Missing SERPAPI_API_KEY"})

    client = Client(api_key=api_key)

    def sync_search():
        return client.search({
            "engine": "google_ai_mode",
            "q": query,
            "geo": geo,
        })

    try:
        results = await asyncio.wait_for(
            asyncio.to_thread(sync_search),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        return json.dumps({
            "error": f"Timeout: Google AI Search không phản hồi trong {timeout}s"
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

    data = results.as_dict()

    output = {
        "query": query,
        "reconstructed_markdown": data.get("reconstructed_markdown"),
        "references": data.get("references"),
    }

    return json.dumps(output, ensure_ascii=False)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Google AI Search Skill")
    parser.add_argument("--query", type=str, required=True, help="Từ khóa hoặc câu hỏi tìm kiếm")
    parser.add_argument("--geo", type=str, default="US", help="Khu vực địa lý (mặc định: US)")
    parser.add_argument("--timeout", type=int, default=30, help="Thời gian chờ tối đa (giây)")

    args = parser.parse_args()

    result = asyncio.run(google_ai_search(args.query, args.geo, args.timeout))
    print(result)