"""
EtsyTrendAnalyzer — Standalone Version

Không phụ thuộc research_agent hoặc _lib.config.
Chỉ cần truyền api_key khi khởi tạo.
"""

import os
import time
import json
import statistics
from collections import Counter
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

import requests


@dataclass
class _EtsyRuntimeConfig:
    max_limit_per_request: int = 100
    request_timeout_sec: int = 15
    max_retry_429: int = 3
    rate_limit_sleep_sec: float = 0.5


@dataclass
class _RuntimeConfig:
    etsy: _EtsyRuntimeConfig = field(default_factory=_EtsyRuntimeConfig)


class EtsyTrendAnalyzer:
    """
    Lấy dữ liệu, phân tích và trực quan hóa xu hướng từ Etsy,
    tập trung vào danh mục áo thun.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openapi.etsy.com/v3/application/listings/active",
        data_dir: str = "/home/ding/debug_mc/Research-Agents/public/charts",
        charts_dir: str = "/home/ding/debug_mc/Research-Agents/",
        taxonomy_ids: Optional[List[int]] = None,
    ):
        if not api_key:
            raise ValueError("ETSY_API_KEY chưa được cung cấp.")

        self.api_key = api_key
        self.base_url = base_url
        self.data_dir = data_dir
        self.charts_dir = charts_dir
        self.taxonomy_ids = taxonomy_ids or [559]  # 559 = T-Shirts mặc định
        self.config = _RuntimeConfig()

        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.charts_dir, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": self.api_key,
        })

    def _get_cache_filename(self, keywords: Optional[str], days_back: int) -> str:
        keyword_str = "general"
        if keywords:
            keyword_str = keywords.replace(" ", "_").replace('"', '').lower()
        return os.path.join(self.data_dir, f"listings_tshirts_{keyword_str}_{days_back}days.json")

    def _fetch_listings(
        self,
        keywords: Optional[str] = None,
        days_back: Optional[int] = None,
        limit_per_request: Optional[int] = None,
        max_items: Optional[int] = None,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """Lấy danh sách sản phẩm cho tất cả taxonomy áo thun, gộp và loại bỏ trùng lặp."""
        if days_back is None:
            days_back = 30  
        if limit_per_request is None:
            limit_per_request = 100  
        if max_items is None:
            max_items = 500  

        cache_filename = self._get_cache_filename(keywords, days_back)

        if not force_refresh and os.path.exists(cache_filename):
            try:
                with open(cache_filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"Đã tải dữ liệu cache: {len(data.get('listings', []))} sản phẩm từ {cache_filename}")
                return data.get('listings', [])
            except Exception as e:
                print(f"Lỗi khi tải cache: {e}")

        all_listings_map = {}
        start_date = datetime.now() - timedelta(days=days_back)
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(datetime.now().timestamp())

        headers = {"x-api-key": self.api_key, "Accept": "application/json"}
        search_desc = "T-shirts"
        if keywords:
            search_desc += f" với từ khóa: '{keywords}'"

        print(f"\nĐang tìm nạp {search_desc} (trong {days_back} ngày qua)...")

        actual_limit = min(limit_per_request, self.config.etsy.max_limit_per_request)
        for tax_id in self.taxonomy_ids:
            offset = 0
            retry_429 = 0
            print(f"   - Đang quét taxonomy ID: {tax_id}")
            while True:
                if max_items and len(all_listings_map) >= max_items:
                    break

                params = {
                    "taxonomy_id": tax_id,
                    "limit": actual_limit,
                    "offset": offset,
                    "created_min": start_timestamp,
                    "created_max": end_timestamp,
                }
                if keywords:
                    params["keywords"] = keywords

                try:
                    response = requests.get(
                        self.base_url,
                        headers=headers,
                        params=params,
                        timeout=self.config.etsy.request_timeout_sec,
                    )
                    if response.status_code == 429:
                        retry_429 += 1
                        if retry_429 > self.config.etsy.max_retry_429:
                            print(f"Đã vượt quá {self.config.etsy.max_retry_429} lần retry 429. Dừng quét.")
                            break
                        retry_after = int(response.headers.get('retry-after', 5))
                        print(f"Rate limit (lần {retry_429}/{self.config.etsy.max_retry_429}). Chờ {retry_after}s...")
                        time.sleep(retry_after)
                        continue
                    retry_429 = 0

                    response.raise_for_status()
                    data = response.json()
                    results = data.get("results", [])

                    if not results:
                        break

                    for listing in results:
                        all_listings_map[listing['listing_id']] = listing

                    print(f"     Page {offset // actual_limit + 1}: +{len(results)} sản phẩm (Tổng: {len(all_listings_map)})")
                    offset += actual_limit
                    time.sleep(self.config.etsy.rate_limit_sleep_sec)

                except requests.exceptions.RequestException as e:
                    print(f"Lỗi: {e}")
                    break

        all_listings = list(all_listings_map.values())
        print(f"Hoàn tất: {len(all_listings)} sản phẩm duy nhất.")

        if all_listings:
            cache_data = {
                "cached_date": datetime.now().isoformat(),
                "keywords": keywords,
                "days_back": days_back,
                "listings": all_listings,
            }
            with open(cache_filename, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"Đã lưu cache: {cache_filename}")

        return all_listings

    def _get_top_listings(self, listings: List[Dict], keyword: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """Lấy top N listings theo favorites, có fetch thêm ảnh và tên shop."""
        if not listings:
            return []

        sorted_listings = sorted(listings, key=lambda x: x.get('num_favorers', 0) or 0, reverse=True)
        top_candidates = sorted_listings[:top_n]
        headers = {"x-api-key": self.api_key, "Accept": "application/json"}
        result = []

        for item in top_candidates:
            listing_id = item.get('listing_id')
            price_raw = item.get('price', {})
            price_val = price_raw.get('amount', 0) / 100 if isinstance(price_raw, dict) else 0

            image_url = ""
            shop_name = ""

            if listing_id:
                try:
                    resp = requests.get(
                        f"https://openapi.etsy.com/v3/application/listings/{listing_id}",
                        headers=headers,
                        params={"includes": "Images,Shop"},
                        timeout=self.config.etsy.request_timeout_sec,
                    )
                    if resp.status_code == 200:
                        detail = resp.json()
                        images = detail.get("images", [])
                        if images:
                            image_url = images[0].get("url_570xN", images[0].get("url_170x135", ""))
                        shop = detail.get("shop", {})
                        shop_name = shop.get("shop_name", "")
                    time.sleep(self.config.etsy.rate_limit_sleep_sec)
                except Exception as e:
                    print(f"Lỗi khi lấy chi tiết listing {listing_id}: {e}")

            listing_url = item.get('url', f"https://www.etsy.com/listing/{listing_id}")
            result.append({
                'title': (item.get('title') or '')[:80],
                'price': round(price_val, 2),
                'favorites': int(item.get('num_favorers', 0) or 0),
                'views': int(item.get('views', 0) or 0),
                'image_url': image_url,
                'shop_name': shop_name,
                'url': listing_url,
                'listing_id': listing_id,
            })

        return result

    def _generate_general_dashboard(self, listings: List[Dict], analysis: Dict[str, Any], days_back: int) -> List[str]:
        """Tạo dashboard 2x3 tổng quan thị trường áo thun chung."""
        try:
            from .chart import generate_general_dashboard
        except ImportError:
            from chart import generate_general_dashboard
        return generate_general_dashboard(listings, analysis, days_back, self.charts_dir)

    def _generate_keyword_dashboard(self, listings: List[Dict], keyword: str, analysis: Dict[str, Any]) -> Optional[str]:
        """Tạo dashboard 2x2 cho một keyword cụ thể."""
        try:
            from .chart import generate_keyword_dashboard
        except ImportError:
            from chart import generate_keyword_dashboard
        return generate_keyword_dashboard(listings, keyword, analysis, self.charts_dir)

    def _generate_comparison_charts(self, keyword_results: Dict[str, Any]) -> Dict[str, str]:
        """Tạo biểu đồ so sánh tất cả keywords cùng lúc."""
        try:
            from .chart import generate_comparison_charts
        except ImportError:
            from chart import generate_comparison_charts
        return generate_comparison_charts(keyword_results, self.charts_dir)

    def _analyze_data(self, listings: List[Dict], keyword: str) -> Dict[str, Any]:
        """Phân tích chi tiết danh sách sản phẩm."""
        if not listings:
            return {"total": 0, "error": "Không có dữ liệu để phân tích."}

        import pandas as pd

        df = pd.DataFrame(listings)
        df['price'] = df['price'].apply(lambda p: p.get('amount', 0) / 100 if isinstance(p, dict) else 0)
        df['favorites'] = pd.to_numeric(df.get('num_favorers', pd.Series(dtype='int')), errors='coerce').fillna(0).astype(int)
        df['views'] = pd.to_numeric(df.get('views', pd.Series(dtype='int')), errors='coerce').fillna(0).astype(int)

        price_stats = df['price'].describe().to_dict()
        favorites_stats = df['favorites'].describe().to_dict()
        views_stats = df['views'].describe().to_dict()

        median_views = views_stats.get('50%', 0)
        median_favorites = favorites_stats.get('50%', 0)
        p75_views = views_stats.get('75%', 0)
        p75_favorites = favorites_stats.get('75%', 0)

        # Use p75 as a more robust engagement anchor than median for sparse Etsy tails.
        engagement_score = (p75_views * 0.4) + (p75_favorites * 0.6)

        total_views = int(df['views'].sum())
        total_favorites = int(df['favorites'].sum())
        fav_view_rate = (total_favorites / total_views * 100) if total_views > 0 else 0
        fav_view_rate_median = (median_favorites / median_views * 100) if median_views > 0 else 0

        all_tags = [tag for tags_list in df['tags'].dropna() for tag in tags_list]
        top_tags = Counter(all_tags).most_common(20)

        return {
            "keyword": keyword,
            "total_listings": len(df),
            "price_stats": {k: round(v, 2) for k, v in price_stats.items()},
            "favorites_stats": {k: round(v, 2) for k, v in favorites_stats.items()},
            "views_stats": {k: round(v, 2) for k, v in views_stats.items()},
            "engagement_score": round(engagement_score, 2),
            "fav_view_rate_pct": round(fav_view_rate, 2),
            "fav_view_rate_median_pct": round(fav_view_rate_median, 2),
            "total_favorites": total_favorites,
            "total_views": total_views,
            "top_tags": top_tags[:5],
        }

    def run_analysis(self, keywords: List[str], days_back: int = 30, limit_per_request: int = 100, max_items: int = 500, force_refresh: bool = False) -> Dict[str, Any]:
        """Chạy phân tích cho danh sách keywords hoặc thị trường chung."""
        if not keywords:
            print("Chạy phân tích thị trường chung...")
            listings = self._fetch_listings(keywords=None, days_back=days_back, limit_per_request=limit_per_request, max_items=max_items, force_refresh=force_refresh)
            analysis_result = self._analyze_data(listings, "Thị trường chung")
            result = {"general_analysis": analysis_result}
            chart_paths = self._generate_general_dashboard(listings, analysis_result, days_back)
            if chart_paths:
                result["chart_paths"] = chart_paths
            return result
        else:
            print(f"Chạy phân tích cho keywords: {keywords}")
            keyword_results = {}
            keyword_listings = {}
            for kw in keywords:
                listings = self._fetch_listings(keywords=kw, days_back=days_back)
                keyword_results[kw] = self._analyze_data(listings, kw)
                keyword_listings[kw] = listings

            final_result = {"keyword_analysis": keyword_results}
            chart_paths = []

            for kw in keywords:
                analysis = keyword_results.get(kw, {})
                if "error" not in analysis:
                    dp = self._generate_keyword_dashboard(keyword_listings[kw], kw, analysis)
                    if dp:
                        chart_paths.append(dp)

            comparison_charts = self._generate_comparison_charts(keyword_results)
            if comparison_charts:
                final_result["comparison_charts"] = comparison_charts
                chart_paths.extend(comparison_charts.values())

            if chart_paths:
                final_result["chart_paths"] = chart_paths

            return final_result
