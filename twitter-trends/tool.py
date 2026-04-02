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


def _get_statistics_sync(
    session: requests.Session,
    country: str = "united-states",
    mode: Literal["24h", "7d", "30d"] = "30d",
):
    url = f"{BASE_URL}/{country}/statistics"
    soup = _get_soup(session, url)
    if not soup:
        return []

    mode_map = {
        "24h": "last 24 hours",
        "7d": "last 7 days",
        "30d": "last 30 days",
    }

    target_text = mode_map.get(mode, "last 30 days")

    blocks = soup.find_all("div", class_="tablo_s")
    target_block = None

    for block in blocks:
        header = block.find("div", class_="tablo_s_baslik")
        if header and target_text in header.get_text().lower():
            target_block = block
            break

    if not target_block:
        return []

    results = []
    rows = target_block.select(".tablo_so_siralama")

    for row in rows:
        rank = row.select_one(".tablo_so_sira_no")
        volume = row.select_one(".tablo_so_volume")
        word = row.select_one(".tablo_so_word")

        if not (rank and volume and word):
            continue

        word_text = word.get_text(strip=True)
        if not word_text or word_text == "-":
            continue

        results.append({
            "rank": rank.get_text(strip=True),
            "keyword": word_text,
            "volume": volume.get_text(strip=True),
            "source": row.get("data-src", "")
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
                _get_statistics_sync,
                session,
                country,
                mode,
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