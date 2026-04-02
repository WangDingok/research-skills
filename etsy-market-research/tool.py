"""
Async Etsy Market Research Skill (Standalone)

Yêu cầu:
    - analyzer.py (chứa class EtsyTrendAnalyzer)
    - ETSY_API_KEY=...
"""

import os
import json
import asyncio
from typing import List
from dotenv import load_dotenv

from analyzer import EtsyTrendAnalyzer

load_dotenv()


# =========================
# Helper
# =========================

def _get_analyzer():
    api_key = os.getenv("ETSY_API_KEY")
    if not api_key:
        raise ValueError("Missing ETSY_API_KEY")

    return EtsyTrendAnalyzer(api_key=api_key)


# =========================
# Public Async APIs
# =========================

async def search_etsy_trends_by_keyword(
    keywords: List[str],
    days_back: int = 30,
    limit_per_request: int = 100,
    max_items: int = 1000,
) -> str:
    """
    Phân tích xu hướng Etsy theo danh sách từ khóa.
    Trả về:
        - engagement_score
        - median_price
        - median_favorites
        - top_tags
        - chart_paths
        - comparison_charts
    """

    try:
        analyzer = _get_analyzer()

        results = await asyncio.wait_for(
            asyncio.to_thread(analyzer.run_analysis, keywords, days_back, limit_per_request, max_items),
            timeout=120,
        )

        keyword_analysis = results.get("keyword_analysis", {})
        chart_paths = results.get("chart_paths", [])
        comparison_charts = results.get("comparison_charts", {})

        output = []

        for kw, analysis_data in keyword_analysis.items():
            if "error" in analysis_data:
                continue

            output.append({
                "keyword": kw,
                "total_listings": analysis_data.get("total_listings"),
                "engagement_score": analysis_data.get("engagement_score"),
                "fav_view_rate_pct": analysis_data.get("fav_view_rate_pct"),
                "median_price": analysis_data.get("price_stats", {}).get("50%"),
                "median_favorites": analysis_data.get("favorites_stats", {}).get("50%"),
                "top_tags": [
                    t[0] for t in analysis_data.get("top_tags", [])[:5]
                ],
            })

        return json.dumps({
            "analysis": output,
            "chart_paths": chart_paths,
            "comparison_charts": comparison_charts,
            "status": "success",
        }, ensure_ascii=False)

    except asyncio.TimeoutError:
        return json.dumps({
            "error": f"Timeout: Etsy analysis vượt quá thời gian cho phép",
            "status": "failed"
        })

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "failed"
        })


async def get_etsy_top_listings(
    keyword: str,
    top_n: int = 5,
) -> str:
    """
    Lấy top N sản phẩm nổi bật nhất theo từ khóa.
    """

    try:
        analyzer = _get_analyzer()

        def _fetch():
            listings = analyzer._fetch_listings(keywords=keyword)
            return analyzer._get_top_listings(
                listings,
                keyword,
                top_n=top_n,
            ), len(listings)

        top_listings, total_fetched = await asyncio.wait_for(
            asyncio.to_thread(_fetch),
            timeout=30,
        )

        return json.dumps({
            "keyword": keyword,
            "top_listings": top_listings,
            "total_fetched": total_fetched,
            "status": "success",
        }, ensure_ascii=False)

    except asyncio.TimeoutError:
        return json.dumps({
            "error": f"Timeout: Lấy top listings vượt quá thời gian cho phép",
            "status": "failed"
        })

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "failed"
        })

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Etsy Trend Analyzer")
    parser.add_argument("--keywords", nargs="+", help="Danh sách từ khóa để phân tích", required=True)
    parser.add_argument("--days_back", type=int, default=30, help="Số ngày quay lại để phân tích (default: 30)")
    parser.add_argument("--limit_per_request", type=int, default=100, help="Số sản phẩm tối đa mỗi lần fetch (default: 100)")
    parser.add_argument("--max_items", type=int, default=500, help="Số sản phẩm tối đa để phân tích (default: 500)")
    parser.add_argument("--mode", type=str, default="analysis", help="Chế độ chạy (default: analysis, options: analysis, top_listings)")  

    args = parser.parse_args()

    if args.mode == "analysis":
        result = asyncio.run(search_etsy_trends_by_keyword(
            keywords=args.keywords,
            days_back=args.days_back,
            limit_per_request=args.limit_per_request,
            max_items=args.max_items,
        ))
    elif args.mode == "top_listings":
        if len(args.keywords) != 1:
            print("Error: Chế độ top_listings chỉ hỗ trợ một từ khóa duy nhất.")
            exit(1)
        result = asyncio.run(get_etsy_top_listings(
            keyword=args.keywords[0],
            top_n=5,
        ))
    else:        
        print(f"Error: Chế độ không hợp lệ '{args.mode}'. Vui lòng chọn 'analysis' hoặc 'top_listings'.")
        exit(1) 
    
    print(result)
