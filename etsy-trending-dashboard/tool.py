"""CLI wrapper for etsy-trending-dashboard — outputs JSON with report paths."""

import argparse
import json
import os
import sys

# Ensure parent package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args, **_kwargs):
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate Etsy trending dashboard")
    parser.parse_args()  # no args for now, kept for consistency with other tools

    # Load env from etsy-market-research sibling (for ETSY_API_KEY)
    etsy_mr_env = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "etsy-market-research",
        ".env",
    )
    if os.path.exists(etsy_mr_env):
        load_dotenv(etsy_mr_env)

    # Validate Supabase credentials
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_KEY"):
        print(
            json.dumps(
                {
                    "error": "SUPABASE_URL and SUPABASE_KEY are required. "
                    "Add them to research-skills/.env"
                }
            )
        )
        return

    from trending_dashboard import fetch_trending_data, generate_dashboard, process_data

    raw_data, report_date = fetch_trending_data()
    if not raw_data:
        print(json.dumps({"error": "No trending data found in Supabase database."}))
        return

    df = process_data(raw_data)
    generate_dashboard(df, report_date)

    # Collect output paths
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    date_slug = report_date.replace("-", "_")
    html_path = os.path.join(logs_dir, f"Trending_Report_{date_slug}.html")
    csv_path = os.path.join(logs_dir, f"Trending_Report_{date_slug}.csv")

    result = {
        "report_date": report_date,
        "total_items": len(df),
        "html_report": html_path if os.path.exists(html_path) else None,
        "csv_data": csv_path if os.path.exists(csv_path) else None,
        "top_tags": [],
        "price_summary": {},
    }

    # Extract quick stats for the agent to present
    try:
        from collections import Counter

        all_tags = []
        for tags in df["tags"]:
            if isinstance(tags, list):
                all_tags.extend([t.strip().lower() for t in tags if len(t.strip()) > 2])
        top_tags = [t for t, _ in Counter(all_tags).most_common(10)]
        result["top_tags"] = top_tags
    except Exception:
        pass

    try:
        result["price_summary"] = {
            "min": round(df["price"].min(), 2),
            "max": round(df["price"].max(), 2),
            "median": round(df["price"].median(), 2),
            "mean": round(df["price"].mean(), 2),
        }
    except Exception:
        pass

    print(json.dumps(result))


if __name__ == "__main__":
    main()
