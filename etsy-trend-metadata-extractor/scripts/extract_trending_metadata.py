import os
import sys
import argparse
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any

# Add path to etsy-niche-analyzer to allow importing local_db
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
niche_analyzer_dir = os.path.join(project_root, "etsy-niche-analyzer")
sys.path.append(niche_analyzer_dir)

try:
    import local_db
except ImportError:
    print(f"Error: Could not import local_db from {niche_analyzer_dir}. Ensure you are running this from the correct workspace.", file=sys.stderr)
    sys.exit(1)

def format_matrix(data: List[Dict[str, Any]]) -> str:
    if not data:
        return "No data found matching the criteria."
    
    # We want a markdown table/matrix
    headers = ["Listing ID", "Title (Truncated)", "Shop", "Price ($)", "Sold 24h", "Sold 7d", "URL"]
    
    matrix = "| " + " | ".join(headers) + " |\n"
    matrix += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    for row in data:
        title = str(row.get('title', ''))
        if len(title) > 40:
            title = title[:37] + "..."
        # Escape pipes in markdown table
        title = title.replace('|', '-')
        
        url = row.get('url', '')
        # Clean url if it has tracking params
        if '?' in url:
            url = url.split('?')[0]
            
        r = [
            str(row.get('listing_id', '')),
            title,
            str(row.get('shop_name', '')),
            f"{row.get('price_usd', 0):.2f}",
            str(row.get('sold_24h', 0)),
            str(row.get('sold_7d', 0)),
            f"[Link]({url})"
        ]
        matrix += "| " + " | ".join(r) + " |\n"
        
    return matrix

def main():
    parser = argparse.ArgumentParser(description="Extract detailed metadata of trending Etsy listings for LLM consumption.")
    parser.add_argument('--top-n', type=int, default=10, help='Number of top listings to return (default: 10)')
    parser.add_argument('--sold-24h-threshold', type=int, default=1, help='Minimum sold in 24h (default: 1)')
    parser.add_argument('--sold-7d-threshold', type=int, default=5, help='Minimum sold in 7d (default: 5)')
    parser.add_argument('--days-new', type=int, default=7, help='If > 0, only returns listings originally created in the last N days (default: 7 to match dashboard).')
    parser.add_argument('--min-views', type=int, default=100, help='Minimum recent views (default: 100)')
    parser.add_argument('--keyword', type=str, default=None, help='Filter by specific keyword (optional)')
    parser.add_argument('--format', type=str, choices=['json', 'matrix'], default='json', help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        if args.days_new > 0:
            query = """
                SELECT l.*, 
                       COALESCE(s.sold_24h, 0) as sold_24h, 
                       COALESCE(s.sold_7d, 0) as sold_7d, 
                       COALESCE(s.sold_30d, 0) as sold_30d,
                       (SELECT views FROM etsy_daily_snapshots WHERE listing_id = l.listing_id ORDER BY snapshot_date DESC LIMIT 1) as recent_views
                FROM etsy_listings l
                LEFT JOIN etsy_sold_summary s ON l.listing_id = s.listing_id
                WHERE l.original_creation_ts >= ? 
                  AND (COALESCE(s.sold_24h, 0) >= ? OR COALESCE(s.sold_7d, 0) >= ?)
            """
            import time
            threshold_ts = int(time.time()) - (args.days_new * 86400)
            params = [threshold_ts, 0, 0] # 0 to fetch all, will filter in python
            
            if args.keyword:
                query += " AND l.keyword LIKE ?"
                params.append(f'%"{args.keyword}"%')
                
            query += " ORDER BY COALESCE(s.sold_24h, 0) DESC, l.original_creation_ts DESC"
            
        else:
            query = """
                SELECT l.*, 
                       COALESCE(s.sold_24h, 0) as sold_24h, 
                       COALESCE(s.sold_7d, 0) as sold_7d, 
                       COALESCE(s.sold_30d, 0) as sold_30d,
                       (SELECT views FROM etsy_daily_snapshots WHERE listing_id = l.listing_id ORDER BY snapshot_date DESC LIMIT 1) as recent_views
                FROM etsy_listings l
                LEFT JOIN etsy_sold_summary s ON l.listing_id = s.listing_id
                WHERE (COALESCE(s.sold_24h, 0) >= ? OR COALESCE(s.sold_7d, 0) >= ?)
            """
            params = [0, 0] 
            
            if args.keyword:
                query += " AND l.keyword LIKE ?"
                params.append(f'%"{args.keyword}"%')
                
            query += " ORDER BY COALESCE(s.sold_24h, 0) DESC, l.original_creation_ts DESC"
            
        conn = sqlite3.connect('/home/ding/etsy-market-analyzer/data/etsy_local.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, params)
        results = cur.fetchall()
        conn.close()
            
        # Clean results
        cleaned_results = []
        for row in results:
            r = dict(row)
            
            # Filter minimum views
            if r.get('recent_views', 0) is None or r.get('recent_views', 0) < args.min_views:
                continue
                
            # Anomaly filtering
            if r.get('sold_24h', 0) >= 900:  
                r['sold_24h'] = 0
            if r.get('sold_7d', 0) >= 6300: 
                r['sold_7d'] = 0
                
            if args.sold_24h_threshold > 0 and r.get('sold_24h', 0) < args.sold_24h_threshold:
                continue
            if args.sold_7d_threshold > 0 and r.get('sold_7d', 0) < args.sold_7d_threshold:
                continue
            
            # Tags is often stored as JSON string in sqlite
            if isinstance(r.get('tags'), str) and (r['tags'].startswith('[') or r['tags'].startswith('{')):
                try:
                    r['tags'] = json.loads(r['tags'])
                except:
                    pass
                    
            cleaned_results.append(r)
            
            if len(cleaned_results) >= args.top_n:
                break
            
        if args.format == 'json':
            print(json.dumps(cleaned_results, indent=2, ensure_ascii=False))
        elif args.format == 'matrix':
            print(format_matrix(cleaned_results))
            
    except Exception as e:
        print(f"Error querying database: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
