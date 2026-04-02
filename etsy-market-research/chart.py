"""Chart generation utilities for Etsy market research."""

import os
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def _build_dataframe(listings: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(listings)
    df["price"] = df["price"].apply(lambda p: p.get("amount", 0) / 100 if isinstance(p, dict) else 0)
    df["favorites"] = pd.to_numeric(df.get("num_favorers", pd.Series(dtype="int")), errors="coerce").fillna(0).astype(int)
    df["views"] = pd.to_numeric(df.get("views", pd.Series(dtype="int")), errors="coerce").fillna(0).astype(int)
    return df


def generate_general_dashboard(
    listings: List[Dict[str, Any]],
    analysis: Dict[str, Any],
    days_back: int,
    charts_dir: str,
) -> List[str]:
    """Tạo dashboard 2x3 tổng quan thị trường áo thun chung."""
    if not listings or len(listings) < 10:
        return []

    import numpy as np

    df = _build_dataframe(listings)

    sns.set_theme(style="whitegrid")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chart_paths: List[str] = []

    fig, axes = plt.subplots(2, 3, figsize=(22, 14))
    fig.patch.set_facecolor("#f5faff")
    for _ax in axes.flat:
        _ax.set_facecolor("#f5faff")
    fig.suptitle(
        f"Etsy T-Shirt Market Discovery - Tổng quan {days_back} ngày\n"
        f"{len(df)} sản phẩm  *  Mức tương tác: {analysis.get('engagement_score', 0)}  *  "
        f"Yêu thích/Xem: {analysis.get('fav_view_rate_pct', 0)}%",
        fontsize=16,
        fontweight="bold",
        y=1.01,
    )

    ax = axes[0, 0]
    all_tags = [tag for tags_list in df["tags"].dropna() for tag in tags_list]
    top_tags = Counter(all_tags).most_common(20)
    if top_tags:
        tag_names = [t[0] for t in top_tags][::-1]
        tag_counts = [t[1] for t in top_tags][::-1]
        colors = sns.color_palette("viridis", len(tag_names))
        bars = ax.barh(tag_names, tag_counts, color=colors, edgecolor="white")
        ax.bar_label(bars, fmt="%d", padding=3, fontsize=8)
    ax.set_title("Top 20 Tags — Niche đang tập trung", fontsize=12, fontweight="bold")
    ax.set_xlabel("Số lần xuất hiện")

    ax = axes[0, 1]
    price_data = df["price"][df["price"] > 0]
    if len(price_data) > 0:
        p95 = price_data.quantile(0.95)
        price_clipped = price_data[price_data <= p95]
        ax.hist(price_clipped, bins=30, color="#4C72B0", edgecolor="white", alpha=0.85)
        ax.axvline(price_data.median(), color="#C44E52", linestyle="--", linewidth=2, label=f"Median: ${price_data.median():.1f}")
        ax.axvline(price_data.mean(), color="#DD8452", linestyle=":", linewidth=2, label=f"Mean: ${price_data.mean():.1f}")
        ax.legend(fontsize=9)
    ax.set_title("Phân phối giá ($)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Giá ($)")
    ax.set_ylabel("Số sản phẩm")

    ax = axes[0, 2]
    if "shop_id" in df.columns:
        shop_counts = df["shop_id"].value_counts()
        total_shops = len(shop_counts)
        top5_pct = shop_counts.head(5).sum() / len(df) * 100
        top10_pct = shop_counts.head(10).sum() / len(df) * 100
        rest_pct = 100 - top10_pct
        pie_sizes = [top5_pct, max(top10_pct - top5_pct, 0), max(rest_pct, 0)]
        pie_labels = [f"Top 5 ({top5_pct:.0f}%)", f"Top 6-10 ({top10_pct - top5_pct:.0f}%)", f"Còn lại ({rest_pct:.0f}%)"]
        ax.pie(
            pie_sizes,
            labels=pie_labels,
            colors=["#C44E52", "#DD8452", "#55A868"],
            autopct="",
            startangle=90,
            textprops={"fontsize": 9},
        )
        ax.set_title(f"Phân bố seller ({total_shops} shops)", fontsize=12, fontweight="bold")

    ax = axes[1, 0]
    fav_data = df["favorites"]
    fav_bins = [0, 1, 5, 20, 50, 100, float("inf")]
    fav_labels = ["0 Fav", "1-5", "5-20", "20-50", "50-100", "100+"]
    fav_cats = pd.cut(fav_data, bins=fav_bins, labels=fav_labels, right=False)
    fav_dist = fav_cats.value_counts().reindex(fav_labels).fillna(0)
    total = len(fav_data)
    pct = (fav_dist / total * 100).round(1)
    bar_colors = ["#8172B2", "#4C72B0", "#55A868", "#DD8452", "#C44E52", "#D65F5F"]
    bars = ax.bar(range(len(fav_dist)), fav_dist.values, color=bar_colors, edgecolor="white")
    for i, (v, p) in enumerate(zip(fav_dist.values, pct.values)):
        ax.text(i, v + total * 0.01, f"{int(v)}\\n({p}%)", ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax.set_xticks(range(len(fav_labels)))
    ax.set_xticklabels(fav_labels, fontsize=9)
    ax.set_title("Mức độ cạnh tranh theo Yêu thích", fontsize=12, fontweight="bold")

    ax = axes[1, 1]
    price_valid = df[df["price"] > 0].copy()
    if len(price_valid) > 10:
        bins = [0, 10, 20, 30, 50, 100, float("inf")]
        seg_labels = ["<$10", "$10-20", "$20-30", "$30-50", "$50-100", "$100+"]
        price_valid["price_segment"] = pd.cut(price_valid["price"], bins=bins, labels=seg_labels)
        seg_stats = price_valid.groupby("price_segment", observed=True).agg(
            count=("price", "size"), avg_fav=("favorites", "mean")
        ).reset_index()
        x = np.arange(len(seg_stats))
        w = 0.35
        bars1 = ax.bar(x - w / 2, seg_stats["count"], w, label="Số SP", color="#4C72B0", alpha=0.85)
        ax.bar_label(bars1, fmt="%d", fontsize=8, padding=2)
        ax2 = ax.twinx()
        bars2 = ax2.bar(x + w / 2, seg_stats["avg_fav"], w, label="Avg Yêu thích", color="#DD8452", alpha=0.85)
        ax2.bar_label(bars2, fmt="%.1f", fontsize=8, padding=2)
        ax.set_xticks(x)
        ax.set_xticklabels(seg_stats["price_segment"], rotation=30)
        ax.set_ylabel("Số sản phẩm", color="#4C72B0")
        ax2.set_ylabel("Avg Yêu thích", color="#DD8452")
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper right")
    ax.set_title("Phân khúc giá: Số SP vs Hiệu suất", fontsize=12, fontweight="bold")

    ax = axes[1, 2]
    if len(df) > 20:
        fav_threshold = df["favorites"].quantile(0.8)
        top_df = df[df["favorites"] >= max(fav_threshold, 1)]
        rest_df = df[df["favorites"] < max(fav_threshold, 1)]
        top_tags_set = Counter([tag for tags_list in top_df["tags"].dropna() for tag in tags_list])
        rest_tags_set = Counter([tag for tags_list in rest_df["tags"].dropna() for tag in tags_list])
        tag_success = {
            tag: (cnt / (cnt + rest_tags_set.get(tag, 0))) * 100
            for tag, cnt in top_tags_set.items()
            if (cnt + rest_tags_set.get(tag, 0)) >= 5
        }
        if tag_success:
            sorted_tags = sorted(tag_success.items(), key=lambda x: x[1], reverse=True)[:15]
            t_names = [t[0] for t in sorted_tags][::-1]
            t_rates = [t[1] for t in sorted_tags][::-1]
            colors_tag = ["#55A868" if r >= 50 else "#DD8452" if r >= 30 else "#8172B2" for r in t_rates]
            bars = ax.barh(t_names, t_rates, color=colors_tag, edgecolor="white")
            ax.bar_label(bars, fmt="%.0f%%", padding=3, fontsize=8)
            ax.axvline(50, color="gray", linestyle="--", alpha=0.5, linewidth=1)
    ax.set_title("Tags thành công cao (SP top 20% Yêu thích)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Tỷ lệ thành công (%)")

    plt.tight_layout()
    fp = os.path.join(charts_dir, f"general_market_overview_{timestamp}.png")
    try:
        fig.savefig(fp, bbox_inches="tight", dpi=130)
        chart_paths.append(fp)
    finally:
        plt.close(fig)
    return chart_paths


def generate_keyword_dashboard(
    listings: List[Dict[str, Any]],
    keyword: str,
    analysis: Dict[str, Any],
    charts_dir: str,
) -> Optional[str]:
    """Tạo dashboard 2x2 cho một keyword cụ thể."""
    if not listings or len(listings) < 5:
        return None

    import numpy as np

    df = _build_dataframe(listings)

    sns.set_theme(style="whitegrid")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_kw = keyword.replace(" ", "_").replace("/", "_")[:30]

    fav_view_rate = analysis.get("fav_view_rate_pct", 0)
    bg_color = "#f0fdf4" if fav_view_rate >= 3 else "#fffbf0" if fav_view_rate >= 1 else "#fff5f5"
    health_label = "[NÓNG]" if fav_view_rate >= 3 else "[TRUNG BÌNH]" if fav_view_rate >= 1 else "[LẠNH]"

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.patch.set_facecolor(bg_color)
    for _ax in axes.flat:
        _ax.set_facecolor(bg_color)
    fig.suptitle(
        f"Etsy Market Dashboard — \"{keyword}\" {health_label}\n"
        f"{analysis.get('total_listings', 0)} SP  *  Engagement: {analysis.get('engagement_score', 0)}  *  "
        f"Fav/View: {analysis.get('fav_view_rate_pct', 0)}%",
        fontsize=15,
        fontweight="bold",
        y=1.01,
    )

    ax = axes[0, 0]
    price_valid = df[df["price"] > 0].copy()
    if len(price_valid) > 5:
        bins = [0, 10, 20, 30, 50, 100, float("inf")]
        seg_labels = ["<$10", "$10-20", "$20-30", "$30-50", "$50-100", "$100+"]
        price_valid["seg"] = pd.cut(price_valid["price"], bins=bins, labels=seg_labels)
        seg_stats = price_valid.groupby("seg", observed=True).agg(count=("price", "size"), avg_fav=("favorites", "mean")).reset_index()
        x = np.arange(len(seg_stats))
        w = 0.38
        bars1 = ax.bar(x - w / 2, seg_stats["count"], w, label="Số SP", color="#4C72B0", alpha=0.85, edgecolor="white")
        ax.bar_label(bars1, fmt="%d", fontsize=8, padding=2)
        ax2_r = ax.twinx()
        bars2 = ax2_r.bar(x + w / 2, seg_stats["avg_fav"], w, label="Avg Yêu thích", color="#DD8452", alpha=0.85, edgecolor="white")
        ax2_r.bar_label(bars2, fmt="%.1f", fontsize=8, padding=2)
        ax.set_xticks(x)
        ax.set_xticklabels(seg_stats["seg"], rotation=30, fontsize=9)
        lines1, labs1 = ax.get_legend_handles_labels()
        lines2, labs2 = ax2_r.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labs1 + labs2, fontsize=8, loc="upper right")
    ax.set_title("Phân khúc giá: Số SP vs Avg Yêu thích", fontsize=11, fontweight="bold")

    ax = axes[0, 1]
    fav_data = df["favorites"]
    fav_bins = [0, 1, 5, 20, 50, 100, float("inf")]
    fav_cat_labels = ["0", "1-5", "5-20", "20-50", "50-100", "100+"]
    fav_cats = pd.cut(fav_data, bins=fav_bins, labels=fav_cat_labels, right=False)
    fav_dist = fav_cats.value_counts().reindex(fav_cat_labels).fillna(0)
    total = len(fav_data)
    pct = (fav_dist / total * 100).round(1)
    bar_colors = ["#9e9e9e", "#5c85d6", "#43a863", "#f0a030", "#e05050", "#b71c1c"]
    bars = ax.bar(range(len(fav_dist)), fav_dist.values, color=bar_colors, edgecolor="white")
    for i, (v, p) in enumerate(zip(fav_dist.values, pct.values)):
        ax.text(i, v + total * 0.012, f"{int(v)}\\n({p}%)", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_xticks(range(len(fav_cat_labels)))
    ax.set_xticklabels(fav_cat_labels, fontsize=9)
    ax.set_title("Mức độ cạnh tranh theo Yêu thích", fontsize=11, fontweight="bold")

    ax = axes[1, 0]
    if "shop_id" in df.columns and df["shop_id"].notna().sum() > 0:
        shop_counts = df.groupby("shop_id").size().sort_values(ascending=False)
        total_shops = len(shop_counts)
        top10 = shop_counts.head(10)
        top10_share = top10.sum() / len(df) * 100
        shop_labels_bar = [f"#{i + 1}" for i in range(len(top10))][::-1]
        cmap_colors = plt.cm.RdYlGn_r(np.linspace(0.1, 0.7, len(top10)))[::-1]
        bars = ax.barh(shop_labels_bar, top10.values[::-1], color=cmap_colors, edgecolor="white")
        ax.bar_label(bars, fmt="%d", padding=3, fontsize=8)
        ax.set_title(f"Top 10 shops chiếm {top10_share:.0f}% ({total_shops} shops tổng)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Số listings")

    ax = axes[1, 1]
    if len(df) > 10:
        fav_thresh = df["favorites"].quantile(0.8)
        top_df_tags = df[df["favorites"] >= max(fav_thresh, 1)]
        rest_df_tags = df[df["favorites"] < max(fav_thresh, 1)]
        top_tag_ct = Counter([t for tags in top_df_tags["tags"].dropna() for t in tags])
        rest_tag_ct = Counter([t for tags in rest_df_tags["tags"].dropna() for t in tags])
        min_presence = max(3, int(len(df) * 0.03))
        tag_success = {
            tag: (cnt / (cnt + rest_tag_ct.get(tag, 0))) * 100
            for tag, cnt in top_tag_ct.items()
            if (cnt + rest_tag_ct.get(tag, 0)) >= min_presence
        }
        if tag_success:
            sorted_tags = sorted(tag_success.items(), key=lambda x: x[1], reverse=True)[:15]
            t_names = [t[0] for t in sorted_tags][::-1]
            t_rates = [t[1] for t in sorted_tags][::-1]
            colors_tag = ["#55A868" if r >= 50 else "#DD8452" if r >= 30 else "#8172B2" for r in t_rates]
            bars = ax.barh(t_names, t_rates, color=colors_tag, edgecolor="white")
            ax.bar_label(bars, fmt="%.0f%%", padding=3, fontsize=8)
            ax.axvline(50, color="gray", linestyle="--", alpha=0.5, linewidth=1)
    ax.set_title("Tags xuất hiện ở SP top 20% Yêu thích", fontsize=11, fontweight="bold")
    ax.set_xlabel("Tỷ lệ thành công (%)")

    plt.tight_layout()
    fp = os.path.join(charts_dir, f"etsy_dashboard_{safe_kw}_{timestamp}.png")
    try:
        fig.savefig(fp, bbox_inches="tight", dpi=130)
    finally:
        plt.close(fig)
    return fp


def generate_comparison_charts(keyword_results: Dict[str, Any], charts_dir: str) -> Dict[str, str]:
    """Tạo biểu đồ so sánh tất cả keywords cùng lúc."""
    valid = {k: v for k, v in keyword_results.items() if "error" not in v}
    if len(valid) < 2:
        return {}

    import numpy as np

    sns.set_theme(style="whitegrid")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    charts: Dict[str, str] = {}

    rows = []
    for kw, a in valid.items():
        med_views = a.get("views_stats", {}).get("50%", 0)
        med_fav = a.get("favorites_stats", {}).get("50%", 0)
        med_price = a.get("price_stats", {}).get("50%", 0)
        total = a.get("total_listings", 0)
        fav_rate = (med_fav / med_views * 100) if med_views > 0 else 0
        rows.append({
            "Keyword": kw,
            "fav_view_pct": round(fav_rate, 2),
            "engagement": a.get("engagement_score", 0),
            "med_fav": round(med_fav, 1),
            "med_price": round(med_price, 1),
            "med_views": round(med_views, 0),
            "n_products": total,
        })
    df = pd.DataFrame(rows)
    n = len(df)

    def rank_palette(series: pd.Series, high_is_good: bool = True) -> list:
        ranks = series.rank(ascending=not high_is_good, method="min")
        colors = []
        for rv in ranks:
            t = (rv - 1) / max(n - 1, 1)
            if t < 0.5:
                t2 = t * 2
                rc = int(44 + (255 - 44) * t2)
                gc = int(160 + (127 - 160) * t2)
                bc = int(44 * (1 - t2))
            else:
                t2 = (t - 0.5) * 2
                rc = int(255 + (214 - 255) * t2)
                gc = int(127 + (39 - 127) * t2)
                bc = int(14 + (24 - 14) * t2)
            colors.append(f"#{rc:02x}{gc:02x}{bc:02x}")
        return colors

    df_sorted = df.sort_values("fav_view_pct", ascending=True).reset_index(drop=True)
    metrics_cfg = [
        ("fav_view_pct", "Tỷ lệ Yêu thích/Xem (%)", True, "%.2f%%"),
        ("engagement", "Điểm Tương tác", True, "%.1f"),
        ("med_fav", "Yêu thích trung vị", True, "%.1f"),
        ("med_price", "Giá trung vị ($)", None, "$%.1f"),
        ("med_views", "Lượt xem trung vị", True, "%.0f"),
        ("n_products", "Số sản phẩm (cạnh tranh)", False, "%d"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(22, 12))
    fig.patch.set_facecolor("#f5f9ff")
    fig.suptitle(
        "So sánh Cơ hội giữa các Keyword\n[XANH = tốt nhất  |  ĐỎ = kém nhất  |  XÁM = trung tính (giá)]",
        fontsize=16,
        fontweight="bold",
        y=1.03,
    )

    for (col, title, high_is_good, fmt), ax in zip(metrics_cfg, axes.flat):
        vals = df_sorted[col].values
        kws = df_sorted["Keyword"].values
        colors = rank_palette(df_sorted[col], high_is_good=high_is_good) if high_is_good is not None else ["#4C72B0"] * n
        bars = ax.barh(kws, vals, color=colors, edgecolor="white", linewidth=0.8, height=0.55)
        ax.bar_label(bars, labels=[fmt % v for v in vals], padding=6, fontsize=10, fontweight="bold")
        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        max_val = max(vals) if max(vals) > 0 else 1
        ax.set_xlim(0, max_val * 1.35)
        ax.tick_params(axis="y", labelsize=10)
        ax.xaxis.set_visible(False)
        for spine in ("top", "right", "bottom"):
            ax.spines[spine].set_visible(False)
        ax.set_facecolor("#f5f9ff")

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    fp = os.path.join(charts_dir, f"comparison_dashboard_{timestamp}.png")
    try:
        fig.savefig(fp, bbox_inches="tight", dpi=130)
        charts["comparison_dashboard"] = fp
    finally:
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 9))
    fig.patch.set_facecolor("#fefefe")
    x_vals = df["engagement"].values.astype(float)
    y_vals = df["fav_view_pct"].values.astype(float)
    x_med = float(np.median(x_vals))
    y_med = float(np.median(y_vals))
    x_rng = max(x_vals.max() - x_vals.min(), 1.0)
    y_rng = max(y_vals.max() - y_vals.min(), 0.1)
    ax.set_xlim(max(0.0, x_vals.min() - x_rng * 0.35), x_vals.max() + x_rng * 0.35)
    ax.set_ylim(max(0.0, y_vals.min() - y_rng * 0.35), y_vals.max() + y_rng * 0.35)
    ax.axhspan(y_med, y_vals.max() + y_rng * 0.35, alpha=0.07, color="#2ca02c", zorder=0)
    ax.axhspan(max(0.0, y_vals.min() - y_rng * 0.35), y_med, alpha=0.05, color="#d62728", zorder=0)
    ax.axvline(x_med, ls="--", color="#888888", alpha=0.6, linewidth=1.5, zorder=1)
    ax.axhline(y_med, ls="--", color="#888888", alpha=0.6, linewidth=1.5, zorder=1)
    sizes = df["n_products"].clip(lower=1)
    size_max = float(sizes.max())
    size_scaled = (sizes / size_max * 700).clip(lower=80)
    pt_colors = []
    for _, row in df.iterrows():
        if row["engagement"] >= x_med and row["fav_view_pct"] >= y_med:
            pt_colors.append("#2ca02c")
        elif row["engagement"] < x_med and row["fav_view_pct"] < y_med:
            pt_colors.append("#d62728")
        else:
            pt_colors.append("#ff7f0e")
    ax.scatter(x_vals, y_vals, s=size_scaled, c=pt_colors, alpha=0.85, edgecolors="white", linewidths=2, zorder=5)
    for _, row in df.iterrows():
        ax.annotate(
            row["Keyword"],
            (row["engagement"], row["fav_view_pct"]),
            fontsize=12,
            fontweight="bold",
            ha="center",
            va="bottom",
            xytext=(0, 13),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.75, edgecolor="none"),
            zorder=6,
        )
    best_idx = (df["engagement"].rank() + df["fav_view_pct"].rank()).idxmax()
    best_row = df.loc[best_idx]
    ax.annotate(
        ">> CHỌN NICHE NÀY <<",
        (best_row["engagement"], best_row["fav_view_pct"]),
        fontsize=11,
        fontweight="bold",
        color="#1a7a1a",
        ha="center",
        va="top",
        xytext=(0, -30),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->", color="#1a7a1a", lw=2.5),
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#e8f5e9", edgecolor="#2ca02c", linewidth=1.5),
        zorder=7,
    )
    ax.set_xlabel("Điểm Tương tác — Traffic tiềm năng", fontsize=13, labelpad=10)
    ax.set_ylabel("Tỷ lệ Yêu thích/Xem % — Khả năng chuyển đổi", fontsize=13, labelpad=10)
    ax.set_title(
        "Ma trận Cơ hội — Keyword nào đáng đầu tư?\n[Góc trên-phải = sweet spot  |  Bong bóng NHỎ = ít cạnh tranh]",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.tight_layout()
    fp2 = os.path.join(charts_dir, f"opportunity_matrix_{timestamp}.png")
    try:
        fig.savefig(fp2, bbox_inches="tight", dpi=130)
        charts["opportunity_matrix"] = fp2
    finally:
        plt.close(fig)

    return charts
