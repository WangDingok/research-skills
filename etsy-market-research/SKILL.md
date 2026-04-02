---
name: etsy-market-research
description: >
  Phân tích thị trường áo thun trên Etsy: khám phá tổng quan thị trường, phân tích từng niche cụ thể,
  và lấy danh sách sản phẩm bán chạy nhất. Dùng khi cần đánh giá cơ hội thương mại, mức độ cạnh
  tranh, phân bố giá, và top sản phẩm thực tế cho một keyword/niche. 
---

# Skill: Etsy Market Research

## 1. Cách chạy Code Tool (tool.py)

File [tool.py](tool.py) hỗ trợ giao diện dòng lệnh (CLI) với các chế độ phân tích khác nhau:

### Chế độ 1: Phân tích thị trường tổng quan (Market Discovery)
Khi không có keyword cụ thể, hãy dùng danh sách trống (trong code là `keywords=[]`). 
python tool.py --keywords "" --days_back 30 
```

### Chế độ 2: Phân tích theo Niche cụ thể (Verify Keywords)
Truyền danh sách các từ khóa niche để so sánh chỉ số tiềm năng.
```bash
python tool.py --keywords "floral t-shirt" "botanical tee" --days_back 30 --max_items 1000
```

### Các đối số (Arguments):
- `--keywords`: Từ khóa **Bắt buộc**.
- `--days_back`: Số ngày quay lại để phân tích (mặc định: `30`).
- `--limit_per_request`: Số sản phẩm tối đa mỗi lần fetch (mặc định: `100`).
- `--max_items`: Tổng số sản phẩm tối đa để phân tích (mặc định: `1000`). Nên đặt cao để có dữ liệu đủ lớn (1000-5000 là tốt), nhưng có thể điều chỉnh nếu cần phân tích nhanh hơn.
- '--mode': 'anayze' (phân tích thị trường) hoặc 'top_listings' (lấy top sản phẩm). Mặc định: 'analyze'.
---

## 2. Hướng dẫn Nghiên cứu (Agent Guidelines)

Khi sử dụng công cụ này, bạn phải tuân thủ quy trình 3 giai đoạn sau:

### Giai đoạn 1 — Phân tích tổng quan:
1. Gọi tool để lấy dashboard discovery.
2. Trình bày: top niches, mức giá phổ biến, mức cạnh tranh, tags thành công.

### Giai đoạn 2 — Verify keywords (Xác minh Niche):
1. Gọi tool với danh sách keywords cụ thể từ Giai đoạn 1.
2. **LUÔN dùng tiếng Anh** cho tham số `--keywords`.
3. Đánh giá dựa trên:
    *   **Tiềm năng**: `engagement_score`, `fav_view_rate_pct`.
    *   **Mức giá**: `median_price`.
    *   **Cạnh tranh**: `total_listings` (thấp = cơ hội cao).

### Giai đoạn 3 — Lấy TOP sản phẩm:
Sử dụng hàm `get_etsy_top_listings` trong code để lấy hình ảnh và link sản phẩm, sau đó trình bày dưới dạng bảng Markdown:
| # | Hình ảnh | Tên sản phẩm | Shop | Giá | ❤️ Favs | 👁 Views | Link |
|---|---------|-------------|------|-----|---------|----------|------|

---

## Best Practices

- **Luôn bắt đầu với `keywords=[]`** để có bức tranh tổng quan trước khi đi sâu vào niche cụ thể.
- **Kết hợp với Google Trends** (skill `google-trends`): Etsy cho biết "thị trường đang như thế nào", Google Trends cho biết "người ta có đang tìm kiếm không".
- **`tag_analysis.success_rate_pct`**: Tags có success_rate cao nhưng frequency thấp = cơ hội tốt (ít người dùng nhưng hiệu quả).
- **`rising_related_queries` từ Google Trends** + `top_tags` từ Etsy market dashboard = combo tìm niche mạnh nhất.
- **Rate limiting**: Tool tự xử lý rate limit (0.5s/request, retry khi gặp 429) — không cần lo.
