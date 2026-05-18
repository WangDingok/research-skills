---
name: etsy-trend-metadata-extractor
description: Extracts detailed metadata for top trending Etsy listings based on sales metrics thresholds. Use this skill when you need structured data (JSON or Matrix) of top N trending products on Etsy to feed into LLMs for analysis, idea generation, or detailed reporting. Configurable by top N limits, sales thresholds, and freshness.
---

# Skill: etsy-trend-metadata-extractor

This skill fetches raw, detailed metadata for the most heavily-trending products on Etsy directly from the local SQLite database. While other skills might present high-level dashboards in HTML, this skill is specifically designed to output structured data (JSON or a Markdown matrix) that is optimized for LLMs to read, analyze, and use for generating insights.

## When to use this skill
- When the user asks for the "top 5", "top 10", or "top 15" trending Etsy products with all their details.
- When you need to feed detailed listing data (tags, titles, prices, sales metrics) into an LLM context to brainstorm designs, analyze niches, or write reports.
- When the user wants to filter products by sales velocity (e.g. `sold_24h_threshold`, `sold_7d_threshold`).

## Usage

Use the provided script in the `scripts` directory to query the local database.

```bash
python scripts/extract_trending_metadata.py --top-n <number> [--sold-24h-threshold <n>] [--sold-7d-threshold <n>] [--format json|matrix]
```

### Parameters

- `--top-n`: Number of listings to retrieve (e.g., 5, 10, 15). Default is 10.
- `--sold-24h-threshold`: Minimum sales in the last 24 hours. Default is 1.
- `--sold-7d-threshold`: Minimum sales in the last 7 days. Default is 5.
- `--days-new`: If greater than 0, filters for listings that were created within the last N days (hot NEW listings). Default is 7 (which matches the exact behavior of the old Supabase trending dashboard view).
- `--min-views`: Minimum recent views required. Default is 100 (also matches the old dashboard).
- `--keyword`: Optional keyword to filter specific niches.
- `--format`: Format of the output. Options are `json` (default, good for deep LLM analysis including tags and dates) or `matrix` (markdown table, good for quick human/LLM readability).

### Examples

**Get top 5 overall trending listings with high recent velocity in JSON format:**
```bash
python scripts/extract_trending_metadata.py --top-n 5 --sold-24h-threshold 3 --format json
```

**Get a Markdown matrix of the top 15 hot new listings (created in the last 30 days):**
```bash
python scripts/extract_trending_metadata.py --top-n 15 --days-new 30 --format matrix
```

**Get top 10 listings in a specific niche (e.g., "shirt"):**
```bash
python scripts/extract_trending_metadata.py --top-n 10 --keyword "shirt" --format matrix
```

## How to use the output
1. If the output is JSON, you can pass this exact JSON into your context to answer user questions about pricing strategies, tag usage, or title formatting of top sellers.
2. If the output is a matrix, it's very suitable to directly display to the user in a chat interface or include in a final markdown report.
