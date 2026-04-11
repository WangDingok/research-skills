---
name: etsy-trending-dashboard
description: >
  Tạo báo cáo tổng quan về các sản phẩm đang trending trên Etsy dưới dạng HTML Dashboard cho người dùng xem trực tiếp và xuất dữ liệu ra file CSV để Agent phân tích chuyên sâu bằng Pandas.
---

# Skill: Etsy Trending Dashboard

## 1. Mục đích

Skill này cung cấp script `trending_dashboard.py` (cần chạy trong môi trường conda `etsy_env`) để trích xuất dữ liệu trending từ database (Supabase) và tạo ra hai định dạng báo cáo đồng thời tại thư mục `logs/`:

1. **HTML Dashboard** (`Trending_Report_All_Time.html`): 
   - Dashboard có các biểu đồ Plotly tương tác và bảng danh sách sản phẩm đầy đủ thông tin (hình ảnh, giá, lượt xem, số lượng bán trong 24h, ngày crawl...).
   - **Dành cho Người Dùng**: Dễ dàng xem trực quan trên trình duyệt.

2. **CSV Data** (`Trending_Report_All_Time.csv`):
   - Chứa toàn bộ dữ liệu raw của các sản phẩm đang trending.
   - **Dành cho Agent**: Để đọc vào Pandas (`pd.read_csv()`) khi cần truy vấn, filter hoặc phân tích chuyên sâu theo yêu cầu của người dùng.

---

## 2. Cách chạy Code

Di chuyển vào thư mục skill và chạy script thông qua conda:

```bash
cd research-skills/etsy-trending-dashboard
python trending_dashboard.py
```

Sau khi chạy xong, thư mục `logs/` sẽ chứa:
- `Trending_Report_All_Time.html`
- `Trending_Report_All_Time.csv`

---
