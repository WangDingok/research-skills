import os
import sys
import time
import asyncio
import httpx
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
from typing import Optional
from collections import Counter
from supabase import Client, create_client

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args, **_kwargs):
        return False

# Add path to etsy-market-research to allow importing its db module
etsy_market_research_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "etsy-market-research")
sys.path.append(etsy_market_research_dir)

_client: Optional[Client] = None

def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
        if not url or not key:
            raise EnvironmentError("SUPABASE_URL và SUPABASE_KEY chưa được set trong .env")
        _client = create_client(url, key)
    return _client

# Load environment variables for Etsy API Key
load_dotenv(os.path.join(etsy_market_research_dir, '.env'))
ETSY_API_KEY = os.environ.get("ETSY_API_KEY", "")

def fetch_trending_data():
    """Fetch the latest trending data from Supabase."""
    client = get_client()
    
    print("Fetching all trending data across all dates...")
    
    # Use the newly created view that joins all 3 tables directly in Postgres
    # Remove eq("crawl_date") to get all historical trending data
    response = (
        client.table("view_trending_full_dashboard")
        .select("*")
        .order("crawl_date", desc=True)
        .order("rank_position", desc=False)
        .execute()
    )
    
    if not response.data:
        print("No trending data found in database.")
        return None, None
        
    return response.data, "All_Time"

async def fetch_batch_info(batch_ids, client, headers, sem, info_map, progress):
    max_retries = 3
    retries = 0
    url = "https://openapi.etsy.com/v3/application/listings/batch"
    params = [("listing_ids[]", str(lid)) for lid in batch_ids]
    params.append(("includes", "Images,Shop"))
    
    while retries <= max_retries:
        async with sem:
            try:
                resp = await client.get(url, headers=headers, params=params, timeout=15)
                
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    for data in results:
                        l_id = data.get("listing_id")
                        if not l_id: continue
                        
                        images = data.get("images", [])
                        img = ""
                        if images:
                            img = images[0].get("url_570xN") or images[0].get("url_fullxfull") or images[0].get("url_170x135", "")
                        
                        shop_name = data.get("shop", {}).get("shop_name", "")
                        
                        info_map[l_id] = {
                            "image_url": img,
                            "shop_name": shop_name
                        }
                    break
                        
                elif resp.status_code == 429:
                    wait = int(resp.headers.get("retry-after", 2))
                    await asyncio.sleep(wait)
                    retries += 1
                    continue
                else:
                    break
                    
            except Exception as e:
                retries += 1
                if retries > max_retries:
                    break
                await asyncio.sleep(2 * retries)
                continue
                
    progress[0] += len(batch_ids)
    if progress[0] % 100 == 0:
        print(f"  Progress: {progress[0]} items fetched...")

async def _fetch_info_async(listing_ids):
    if not ETSY_API_KEY:
        print("ETSY_API_KEY not found. Cannot fetch missing info.")
        return {}
        
    print(f"Fetching images & shop names for {len(listing_ids)} listings from Etsy API using async batch...")
    
    headers = {"x-api-key": ETSY_API_KEY}
    info_map = {}
    progress = [0]
    
    sem = asyncio.Semaphore(10)
    
    batch_size = 100
    batches = [listing_ids[i:i + batch_size] for i in range(0, len(listing_ids), batch_size)]
    
    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_batch_info(batch, client, headers, sem, info_map, progress)
            for batch in batches
        ]
        await asyncio.gather(*tasks)
            
    print(f"  ✓ Finished fetching. Retrieved data for {len(info_map)} items.")
    return info_map

def fetch_info_from_etsy(listing_ids):
    """Wrapper to run async fetching."""
    return asyncio.run(_fetch_info_async(listing_ids))

def process_data(raw_data):
    """Convert raw Supabase JSON response into a flat Pandas DataFrame."""
    processed = []
    
    # Identify which listings need images OR shop name
    needs_info = [row.get("listing_id") for row in raw_data if not row.get("image_url") or not row.get("shop_name")]
    
    # If there are missing details, fetch them
    info_cache = {}
    if needs_info:
        print(f"Found {len(needs_info)} items missing images or shop_name. Fetching all...")
        info_cache = fetch_info_from_etsy(needs_info)
    
    from datetime import datetime, timezone
    
    # NEW: Prepare list to update DB
    db_updates = []

    for row in raw_data:
        # Parse tags
        tags = row.get("tags", [])
        if isinstance(tags, str):
            tags = tags.strip("{}" ).split(",")

        l_id = row.get("listing_id")
        image_url = row.get("image_url")
        shop_name = row.get("shop_name", "")

        # Merge fetched info if applicable
        if l_id in info_cache:
            fetched_img = info_cache[l_id].get("image_url")
            fetched_shop = info_cache[l_id].get("shop_name")
            
            needs_db_update = False
            if not image_url and fetched_img:
                image_url = fetched_img
                needs_db_update = True
            if not shop_name and fetched_shop:
                shop_name = fetched_shop
                needs_db_update = True
                
            # If we retrieved new data, save it so we can update the DB later
            if needs_db_update:
                db_updates.append({
                    "listing_id": l_id,
                    "image_url": image_url,
                    "shop_name": shop_name
                })

        sold_24h = row.get("sold_24h", 0)
        if sold_24h and sold_24h > 1000:
            sold_24h = 0

        # ori_release_time: Get from 'original_creation_time' if available, or 'original_creation_date', or None
        ori_release_time = row.get("original_creation_time") or row.get("original_creation_date")
        ori_release_time_str = "-"
        since_ori_str = "-"
        days_live = 9999
        if ori_release_time:
            try:
                # Support both timestamp (int/float) and ISO string
                if isinstance(ori_release_time, (int, float)):
                    dt_ori = datetime.fromtimestamp(ori_release_time, tz=timezone.utc)
                else:
                    # If it's an ISO string, only take the date part (YYYY-MM-DD)
                    dt_ori = None
                    if 'T' in str(ori_release_time):
                        dt_ori = datetime.fromisoformat(str(ori_release_time).split('T')[0]).replace(tzinfo=timezone.utc)
                    else:
                        dt_ori = datetime.fromisoformat(str(ori_release_time)[:10]).replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                # Ensure dt_ori has hours, minutes, and seconds for accurate hour calculation
                if isinstance(ori_release_time, (int, float)):
                    delta = now - dt_ori
                else:
                    # If only date is available, consider it as 00:00:00 UTC
                    dt_ori_full = datetime.combine(dt_ori.date(), datetime.min.time(), tzinfo=timezone.utc)
                    delta = now - dt_ori_full
                hours = max(0, int(delta.total_seconds() // 3600))
                days = delta.days
                days_live = max(0, days)
                ori_release_time_str = dt_ori.strftime("%Y-%m-%d")
                if hours < 24:
                    since_ori_str = f"{hours} giờ"
                else:
                    since_ori_str = f"{days} ngày"
            except Exception:
                try:
                    # If parsing fails, just try to take the date part if it's a string
                    ori_release_time_str = str(ori_release_time)[:10]
                    since_ori_str = "-"
                except Exception:
                    ori_release_time_str = str(ori_release_time)
                    since_ori_str = "-"

        flat_row = {
            "crawl_date": row.get("crawl_date"),
            "rank": row.get("rank_position"),
            "listing_id": l_id,
            "title": row.get("title", ""),
            "price": float(row.get("current_price") or 0),
            "views": row.get("recent_views", 0),
            "favorites": row.get("recent_favorers", 0),
            "tags": tags,
            "url": row.get("url", ""),
            "image_url": image_url,
            "shop_name": shop_name,
            "sold_24h": sold_24h,
            "days_since": row.get("days_since_original_creation", 0),
            "days_live": days_live,
            "ori_release_time": ori_release_time_str,
            "since_ori": since_ori_str
        }
        processed.append(flat_row)
    
    df = pd.DataFrame(processed)
    
    # If there are multiple days, deduplicate by listing_id, keeping the most recent record (already sorted by crawl_date desc)
    df = df.drop_duplicates(subset=['listing_id'], keep='first')
    
    # NEW: Update missing info back to database
    if db_updates:
        print(f"Saving {len(db_updates)} newly fetched images & shop names to Database...")
        client = get_client()
        
        # Supabase Python client upsert limits: usually 1000 rows max. 
        # But we'll chunk by 500 to be safe.
        chunk_size = 500
        for i in range(0, len(db_updates), chunk_size):
            chunk = db_updates[i:i + chunk_size]
            try:
                # We must use UPDATE instead of UPSERT to avoid violating NOT NULL constraints
                # since we are only sending partial data (missing title, price, etc.)
                for item in chunk:
                    client.table("etsy_listings").update({
                        "image_url": item["image_url"],
                        "shop_name": item["shop_name"]
                    }).eq("listing_id", item["listing_id"]).execute()
            except Exception as e:
                print(f"Error saving to DB: {e}")
        print("✓ Database update complete.")
    
    return df

def generate_dashboard(df, report_date):
    """Generate the HTML dashboard with Plotly."""
    if df.empty:
        print("DataFrame is empty. Cannot generate dashboard.")
        return
        
    print(f"Generating dashboard for {len(df)} trending items...")
    
    # ------------------------------------------------------------------
    # Chart 1: Top Tags Horizontal Bar Chart (Niche & Keyword X-Ray)
    # ------------------------------------------------------------------
    # Extract and count tags
    all_tags = []
    for tags in df['tags']:
        if isinstance(tags, list):
            # Clean up tags and filter out generic ones if needed
            all_tags.extend([t.strip().lower() for t in tags if len(t.strip()) > 2])
            
    tag_counts = Counter(all_tags).most_common(25)  # Top 25 tags for better readability in a bar chart
    
    tag_df = pd.DataFrame(tag_counts, columns=['Tag', 'Count'])
    
    # Sort ascending for horizontal bar chart (so biggest is at top)
    tag_df = tag_df.sort_values(by='Count', ascending=True)
    
    fig_treemap = px.bar(
        tag_df, 
        y='Tag', 
        x='Count',
        orientation='h',
        color='Count',
        color_continuous_scale='Blues',
        title="1. Niche & Keyword X-Ray (Most frequent tags in trending products)",
        labels={'Count': 'Frequency', 'Tag': 'Keyword / Tag'}
    )
    
    # ------------------------------------------------------------------
    # Chart 2: Pricing Sweet Spot (Histogram)
    # ------------------------------------------------------------------
    # Group by $5 price bins
    bins = range(0, int(df['price'].max()) + 10, 5)
    labels = [f"${i}-{i+4.99}" for i in range(0, int(df['price'].max()) + 5, 5)]
    df['price_bin'] = pd.cut(df['price'], bins=bins, labels=labels, right=False)
    
    # Calculate stats per bin
    price_stats = df.groupby('price_bin', observed=False).agg(
        Listing_Count=('listing_id', 'count'),
        Avg_Views=('views', 'mean'),
        Avg_Sold=('sold_24h', 'mean')
    ).reset_index()
    
    # Drop empty bins
    price_stats = price_stats[price_stats['Listing_Count'] > 0]
    
    fig_price = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bars for listing count
    fig_price.add_trace(
        go.Bar(x=price_stats['price_bin'], y=price_stats['Listing_Count'], name="Number of Listings", marker_color='rgba(55, 128, 191, 0.7)'),
        secondary_y=False,
    )
    
    # Add line for average views
    fig_price.add_trace(
        go.Scatter(x=price_stats['price_bin'], y=price_stats['Avg_Views'], name="Avg Views", mode="lines+markers", marker_color='red'),
        secondary_y=True,
    )
    
    fig_price.update_layout(title_text="2. Pricing Sweet Spot (Where the market is)")
    fig_price.update_xaxes(title_text="Price Range")
    fig_price.update_yaxes(title_text="Number of Listings", secondary_y=False)
    fig_price.update_yaxes(title_text="Average Views", secondary_y=True)
    
    # ------------------------------------------------------------------
    # Generate Interactive HTML Table for All Items
    # ------------------------------------------------------------------
    # Convert all records to dicts for javascript to handle
    records = df.to_dict(orient='records')
    import json
    records_json = json.dumps(records)
    
    table_html = f"""
    <h2 style='font-family: Arial, sans-serif; color: #333; margin-top: 50px;'>🏆 All Trending Winners</h2>
    <div style='margin-bottom: 10px;'>
        <label for='sortSelect'><b>Sort By:</b></label>
        <select id='sortSelect' onchange='renderTable()' style='padding: 8px; border-radius: 4px; border: 1px solid #ccc; font-size: 14px;'>
            <option value='sold_24h'>Sold (24h) - High to Low</option>
            <option value='views'>Views - High to Low</option>
            <option value='favorites'>Favorites - High to Low</option>
            <option value='rank'>Rank - Top to Bottom</option>
        </select>
    </div>
    
    <style>
        @keyframes blinker {{
            50% {{ opacity: 0.5; }}
        }}
    </style>
    <table style='width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
        <thead>
            <tr style='background-color: #f2f2f2; border-bottom: 2px solid #ddd; text-align: left;'>
                <th style='padding: 12px; width: 60px;'>Rank</th>
                <th style='padding: 12px; width: 100px;'>Image</th>
                <th style='padding: 12px;'>Title & Tags</th>
                <th style='padding: 12px;'>Price</th>
                <th style='padding: 12px; text-align: center;'>Views</th>
                <th style='padding: 12px; text-align: center;'>Favorites</th>
                <th style='padding: 12px; text-align: center;'>Sold (24h)</th>
                <th style='padding: 12px; text-align: center;'>Ori Release</th>
                <th style='padding: 12px; text-align: center;'>Since Ori</th>
                <th style='padding: 12px; text-align: center;'>Crawl Date</th>
            </tr>
        </thead>
        <tbody id='tableBody'>
        </tbody>
    </table>
    
    <script>
        const tableData = {records_json};
        
        function renderTable() {{
            const sortBy = document.getElementById('sortSelect').value;
            const tbody = document.getElementById('tableBody');
            
            // Sort the data based on selection
            const sortedData = [...tableData].sort((a, b) => {{
                if (sortBy === 'rank') {{
                    return a[sortBy] - b[sortBy]; // Ascending for rank
                }}
                return b[sortBy] - a[sortBy]; // Descending for others
            }});
            
            let html = '';
            sortedData.forEach((row, i) => {{
                let bgColor = i % 2 === 0 ? '#ffffff' : '#f9f9f9';
                let highlightBadge = '';
                let titleStyle = 'color: #E56A54; text-decoration: none; font-weight: bold;';
                
                // Highlight condition: listed < 4 days and has sales
                if (row.days_live < 4 && row.sold_24h > 0) {{
                    bgColor = '#fffae6'; // Highlight background
                    titleStyle = 'color: #d32f2f; text-decoration: none; font-weight: bold; font-size: 1.1em;';
                    highlightBadge = `<div style='margin-bottom: 5px;'><span style='background-color: #f44336; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; animation: blinker 1.5s linear infinite;'>🔥 HOT NEW RELEASE</span></div>`;
                }}

                const imgSrc = row.image_url ? `<img src='${{row.image_url}}' width='80' style='border-radius: 4px;'/>` : 'No Image';
                
                let tagsDisplay = '';
                if (row.tags && row.tags.length > 0) {{
                    const previewTags = row.tags.slice(0, 5).join(', ');
                    tagsDisplay = `<br><span style='font-size: 0.8em; color: #666;'>Tags: ${{previewTags}}...</span>`;
                }}
                
                html += `
                    <tr style='background-color: ${{bgColor}}; border-bottom: 1px solid #ddd;'>
                        <td style='padding: 12px; font-weight: bold; text-align: center;'>#${{row.rank}}</td>
                        <td style='padding: 12px;'>${{imgSrc}}</td>
                        <td style='padding: 12px;'>
                            ${{highlightBadge}}
                            <a href='${{row.url}}' target='_blank' style='${{titleStyle}}'>${{row.title}}</a>
                            <div style='font-size: 0.85em; color: #888; margin-top: 4px;'>Shop: ${{row.shop_name}}</div>
                            ${{tagsDisplay}}
                        </td>
                        <td style='padding: 12px; font-weight: bold; color: #2E7D32;'>$${{row.price.toFixed(2)}}</td>
                        <td style='padding: 12px; text-align: center;'>👀 <b>${{row.views}}</b></td>
                        <td style='padding: 12px; text-align: center;'>❤️ <b>${{row.favorites}}</b></td>
                        <td style='padding: 12px; text-align: center; color: #d32f2f;'>🛒 <b>${{row.sold_24h}}</b></td>
                        <td style='padding: 12px; text-align: center; white-space:nowrap;'>${{row.ori_release_time || '-'}}</td>
                        <td style='padding: 12px; text-align: center; white-space:nowrap;'>${{row.since_ori || '-'}}</td>
                        <td style='padding: 12px; text-align: center; white-space:nowrap;'>${{row.crawl_date || '-'}}</td>
                    </tr>
                `;
            }});
            
            tbody.innerHTML = html;
        }}
        
        // Render table on initial load
        window.addEventListener('DOMContentLoaded', renderTable);
    </script>
    """
    
    # ------------------------------------------------------------------
    # Export Data
    # ------------------------------------------------------------------
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Export CSV for Agent/Pandas Analysis
    csv_filename = os.path.join(out_dir, f"Trending_Report_{report_date.replace('-', '_')}.csv")
    df.to_csv(csv_filename, index=False)
    print(f"CSV data exported to: {csv_filename}")
    
    # 2. Export HTML for Human Viewing
    html_filename = os.path.join(out_dir, f"Trending_Report_{report_date.replace('-', '_')}.html")
    
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(f"""
        <html>
        <head>
            <title>Etsy Trend Report - {report_date}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f7fa; }}
                .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
                .header {{ border-bottom: 2px solid #E56A54; padding-bottom: 10px; margin-bottom: 30px; }}
                h1 {{ color: #333; margin: 0; }}
                .subtitle {{ color: #666; font-size: 1.1em; margin-top: 5px; }}
                .chart-container {{ margin-bottom: 40px; border: 1px solid #eee; border-radius: 8px; padding: 10px; }}
                .footer {{ text-align: center; margin-top: 50px; color: #888; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Etsy Trending Products Dashboard</h1>
                    <div class="subtitle">Data from {report_date} | Total items analyzed: {len(df)}</div>
                </div>
                
                <div class="chart-container">
                    {fig_treemap.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>
                
                <div class="chart-container">
                    {fig_price.to_html(full_html=False, include_plotlyjs=False)}
                </div>
                
                {table_html}
                
                <div class="footer">
                    Generated by Etsy Market Research Pipeline
                </div>
            </div>
        </body>
        </html>
        """)
        
    print(f"HTML Dashboard generated successfully!")
    print(f"Saved to: {html_filename}")
    print("Open this file in your web browser to view the report.")

if __name__ == "__main__":
    raw_data, report_date = fetch_trending_data()
    if raw_data:
        df = process_data(raw_data)
        generate_dashboard(df, report_date)
