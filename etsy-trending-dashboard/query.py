"""Query Etsy trending Supabase view with structured filters. Outputs JSON."""

import argparse
import json
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args, **_kwargs):
        return False


_SORT_ALIAS = {
    "sold_24h": "sold_24h",
    "sold": "sold_24h",
    "sales": "sold_24h",
    "views": "recent_views",
    "recent_views": "recent_views",
    "favorites": "recent_favorers",
    "favorers": "recent_favorers",
    "price": "current_price",
    "current_price": "current_price",
    "rank": "rank_position",
    "rank_position": "rank_position",
}


def _run(args):
    # Load sibling .env for ETSY_API_KEY / fallback vars
    sibling_env = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "etsy-market-research",
        ".env",
    )
    if os.path.exists(sibling_env):
        load_dotenv(sibling_env)

    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_KEY"):
        print(json.dumps({"error": "SUPABASE_URL/SUPABASE_KEY missing"}))
        return

    from trending_dashboard import get_client

    client = get_client()

    sort_field = _SORT_ALIAS.get(args.sort_by.lower().strip(), "sold_24h")
    ascending = sort_field == "rank_position"

    q = client.table("view_trending_full_dashboard").select("*")

    if args.days_back and args.days_back > 0:
        cutoff = (date.today() - timedelta(days=args.days_back)).isoformat()
        q = q.gte("crawl_date", cutoff)

    if args.min_price and args.min_price > 0:
        q = q.gte("current_price", args.min_price)
    if args.max_price and args.max_price > 0:
        q = q.lte("current_price", args.max_price)

    if args.shop_name:
        q = q.ilike("shop_name", f"%{args.shop_name}%")

    # Pull a generous window; we dedupe + filter + trim in Python.
    fetch_cap = max(args.top_n * 6, 200)
    resp = (
        q.order(sort_field, desc=not ascending)
        .order("crawl_date", desc=True)
        .limit(fetch_cap)
        .execute()
    )

    rows = resp.data or []

    # Dedupe by listing_id, keep best-ranked (first seen after sort).
    seen = set()
    deduped = []
    for r in rows:
        lid = r.get("listing_id")
        if lid in seen:
            continue
        seen.add(lid)
        deduped.append(r)

    # Tag substring filter (tags column is an array).
    tag_q = args.tag_contains.strip().lower()
    if tag_q:
        def _match(r):
            tags = r.get("tags") or []
            if isinstance(tags, str):
                tags = tags.strip("{}").split(",")
            blob = " ".join(str(t).lower() for t in tags)
            blob += " " + str(r.get("title", "")).lower()
            return tag_q in blob
        deduped = [r for r in deduped if _match(r)]

    deduped = deduped[: args.top_n]

    out_rows = []
    for r in deduped:
        tags = r.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.strip("{}").split(",") if t.strip()]
        sold_24h = r.get("sold_24h") or 0
        if sold_24h and sold_24h > 1000:
            sold_24h = 0
        out_rows.append({
            "rank": r.get("rank_position"),
            "listing_id": r.get("listing_id"),
            "title": r.get("title", ""),
            "price": float(r.get("current_price") or 0),
            "views": r.get("recent_views", 0),
            "favorites": r.get("recent_favorers", 0),
            "sold_24h": sold_24h,
            "url": r.get("url", ""),
            "image_url": r.get("image_url", ""),
            "shop_name": r.get("shop_name", ""),
            "crawl_date": str(r.get("crawl_date", "")),
            "tags": tags[:10],
        })

    print(json.dumps({
        "count": len(out_rows),
        "sort_by": sort_field,
        "days_back": args.days_back,
        "rows": out_rows,
    }))


def main():
    p = argparse.ArgumentParser(description="Query Etsy trending view")
    p.add_argument("--sort-by", default="sold_24h")
    p.add_argument("--top-n", type=int, default=10)
    p.add_argument("--days-back", type=int, default=0)
    p.add_argument("--min-price", type=float, default=0)
    p.add_argument("--max-price", type=float, default=0)
    p.add_argument("--tag-contains", default="")
    p.add_argument("--shop-name", default="")
    _run(p.parse_args())


if __name__ == "__main__":
    main()
