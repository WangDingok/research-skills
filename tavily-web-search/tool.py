"""
Async Tavily Web Search (Standalone)

Yêu cầu:
    pip install tavily-python httpx markdownify python-dotenv
    TAVILY_API_KEY=...
"""

import os
import json
import asyncio
from typing import List, Literal

import httpx
from markdownify import markdownify
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


# =========================
# Helper: Fetch Web Content
# =========================

async def fetch_webpage_content_async(
    url: str,
    timeout: float = 15.0
) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return markdownify(response.text)
    except Exception as e:
        return f"Error fetching content from {url}: {str(e)}"


# =========================
# Single Query Search
# =========================

async def tavily_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    fetch_content: bool = False,
    timeout: int = 30,
) -> str:
    """
    Tìm kiếm web bằng Tavily API.

    Returns:
        JSON string gồm:
            - query
            - results (list)
    """

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return json.dumps({"error": "Missing TAVILY_API_KEY"})

    client = TavilyClient(api_key=api_key)

    def sync_search():
        return client.search(
            query=query,
            max_results=max_results,
            topic=topic,
        )

    try:
        search_results = await asyncio.wait_for(
            asyncio.to_thread(sync_search),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        return json.dumps({
            "error": f"Timeout: Tavily search timed out for '{query}'"
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

    results = search_results.get("results", [])

    if fetch_content and results:
        tasks = [
            fetch_webpage_content_async(res["url"])
            for res in results
        ]
        contents = await asyncio.gather(*tasks)
    else:
        contents = [
            res.get("content", "No snippet available.")
            for res in results
        ]

    formatted_results = []

    for i, res in enumerate(results):
        formatted_results.append({
            "title": res.get("title"),
            "url": res.get("url"),
            "content": contents[i]
        })

    return json.dumps({
        "query": query,
        "results": formatted_results
    }, ensure_ascii=False)


# =========================
# Batch Search
# =========================

async def tavily_search_batch(
    queries: List[str],
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    fetch_content: bool = False,
    timeout: int = 30,
) -> str:
    """
    Tìm kiếm song song nhiều queries.

    Returns:
        JSON string: list kết quả theo từng query
    """

    async def _search_one(q: str):
        result = await tavily_search(
            query=q,
            max_results=max_results,
            topic=topic,
            fetch_content=fetch_content,
            timeout=timeout,
        )
        return json.loads(result)

    tasks = [_search_one(q) for q in queries]
    all_results = await asyncio.gather(*tasks)

    return json.dumps(all_results, ensure_ascii=False)

if __name__ == "__main__":
    import asyncio
    import argparse

    parser = argparse.ArgumentParser(description="Tavily Web Search Test")
    parser.add_argument("--query", type=str, default="latest trends in AI", help="Query to search")
    parser.add_argument("--fetch_content", action="store_true", help="Whether to fetch webpage content")
    args = parser.parse_args()  
    
    result = asyncio.run(tavily_search_batch([args.query], fetch_content=args.fetch_content))
    print(result)