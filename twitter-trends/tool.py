"""
Async Twitter/X Trends Scraper (Standalone)

Yêu cầu:
    pip install requests beautifulsoup4 lxml
"""

import json
import asyncio
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import Literal


BASE_URL = "https://www.twitter-trending.com"


# =========================
# Internal Helpers
# =========================

def _get_soup(session: requests.Session, url: str, timeout: int = 15):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    ]

    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        res = session.get(url, headers=headers, timeout=timeout)
        res.raise_for_status()
        return BeautifulSoup(res.text, "lxml")
    except Exception:
        return None


def _get_featured_sync(
    session: requests.Session,
    country: str = "united-states",
    mode: Literal["day", "week", "month"] = "month",
):
    url = f"{BASE_URL}/{country}/en"
    soup = _get_soup(session, url)
    if not soup:
        return []

    mode_map = {
        "day": "gun_one_c",
        "week": "hafta_one_c",
        "month": "ay_one_c",
    }

    container = soup.find("div", id=mode_map.get(mode, "ay_one_c"))
    if not container:
        return []

    results = []
    items = container.select(".one_cikan88")

    for item in items:
        a = item.select_one(".sire_kelime a")
        if not a:
            continue

        keyword = a.get_text(strip=True)
        href = a.get("href", "")

        query = urllib.parse.parse_qs(
            urllib.parse.urlparse(href).query
        )
        raw_val = query.get("s", [""])[0]
        raw = urllib.parse.unquote(raw_val).replace("+", " ")

        results.append({
            "keyword": keyword,
            "raw_query": raw
        })

    return results


def _get_en_trends_sync(
    session: requests.Session,
    country: str = "united-states",
    timeout: int = 15,
):
    """Fetch 50-item trending list from /en via two-step AJAX (cookie + POST).

    Computes a recurrence score: how many of the ~8 hourly snapshot tables
    each keyword appears in.  Keywords that persist across snapshots are
    genuinely trending; flash spikes appear in only 1-2 tables.
    """
    import re

    # Step 1: GET /en page to obtain session cookies
    page_url = f"{BASE_URL}/{country}/en"
    soup = _get_soup(session, page_url, timeout=timeout)
    if not soup:
        return []

    # Extract the JS country variable (e.g. "United States")
    match = re.search(r'sayfaUlkesiJS\s*=\s*"([^"]+)"', str(soup))
    country_name = match.group(1) if match else country.replace("-", " ").title()

    # Step 2: POST AJAX with cookies from step 1
    ajax_url = f"{BASE_URL}/other/trendslist/trend-result.php"
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Referer": page_url,
        "X-Requested-With": "XMLHttpRequest",
    }
    try:
        res = session.post(
            ajax_url,
            data=f"country={urllib.parse.quote(country_name)}",
            headers=headers,
            timeout=timeout,
        )
        res.raise_for_status()
        data = res.json()
    except Exception:
        return []

    # Step 3: Count recurrence across all hourly snapshot tables
    keyword_count = {}       # keyword → number of tables it appears in
    keyword_best_rank = {}   # keyword → best (lowest) rank seen
    table_keys = [k for k in data if k.startswith("table")]

    for table_key in table_keys:
        trends = data[table_key].get("trends", {})
        for idx_key, raw_val in trends.items():
            try:
                parsed = json.loads(raw_val)
            except (json.JSONDecodeError, TypeError):
                continue
            keyword = urllib.parse.unquote(parsed[0]).replace("+", " ")
            rank_num = int(idx_key.lstrip("t"))
            keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
            if keyword not in keyword_best_rank or rank_num < keyword_best_rank[keyword]:
                keyword_best_rank[keyword] = rank_num

    # Step 4: Sort by recurrence desc, then by best rank asc
    sorted_keywords = sorted(
        keyword_count.keys(),
        key=lambda k: (-keyword_count[k], keyword_best_rank[k]),
    )

    total_tables = len(table_keys) or 1
    results = []
    for i, kw in enumerate(sorted_keywords[:50]):
        results.append({
            "rank": str(i + 1),
            "keyword": kw,
            "volume": str(keyword_count[kw] * 1000),
            "recurrence": f"{keyword_count[kw]}~{total_tables}",
        })

    return results


# =========================
# Public Async Functions
# =========================

async def get_twitter_featured_trends(
    country: str = "united-states",
    mode: Literal["day", "week", "month"] = "month",
    timeout: int = 20,
) -> str:
    """
    Lấy các chủ đề nổi bật (featured).
    """

    session = requests.Session()

    try:
        results = await asyncio.wait_for(
            asyncio.to_thread(
                _get_featured_sync,
                session,
                country,
                mode,
            ),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        return json.dumps({
            "error": f"Timeout: Twitter featured trends không phản hồi trong {timeout}s"
        })

    return json.dumps({
        "country": country,
        "mode": mode,
        "results": results
    }, ensure_ascii=False)


async def get_twitter_statistics_trends(
    country: str = "united-states",
    mode: Literal["24h", "7d", "30d"] = "30d",
    timeout: int = 20,
) -> str:
    """
    Lấy thống kê trending (có rank + volume).
    """

    session = requests.Session()

    try:
        results = await asyncio.wait_for(
            asyncio.to_thread(
                _get_en_trends_sync,
                session,
                country,
                timeout,
            ),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        return json.dumps({
            "error": f"Timeout: Twitter statistics trends không phản hồi trong {timeout}s"
        })

    return json.dumps({
        "country": country,
        "mode": mode,
        "results": results
    }, ensure_ascii=False)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Twitter Trends Scraper")
    parser.add_argument("--type", choices=["featured", "statistics"], required=True, help="Loại xu hướng cần lấy")
    parser.add_argument("--country", default="united-states", help="Tên quốc gia (ví dụ: 'united-states', 'turkey')")
    parser.add_argument("--mode", default=None, help="Chế độ thời gian (featured: 'day', 'week', 'month'; statistics: '24h', '7d', '30d')")
    parser.add_argument("--timeout", type=int, default=20, help="Thời gian chờ tối đa (giây)")

    args = parser.parse_args()

    if args.type == "featured":
        mode = args.mode if args.mode else "month"
        result = asyncio.run(get_twitter_featured_trends(args.country, mode, args.timeout))
    else:
        mode = args.mode if args.mode else "30d"
        result = asyncio.run(get_twitter_statistics_trends(args.country, mode, args.timeout))

    print(result)