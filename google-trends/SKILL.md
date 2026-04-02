---
name: google-trends
description: >
  Phân tích xu hướng tìm kiếm theo thời gian trên Google Trends.
  Dùng khi cần đánh giá độ ổn định (stable/volatile), hướng tăng/giảm,
  mức độ thay đổi %, và đỉnh điểm quan tâm của một hoặc nhiều từ khóa.
  Tự động xuất biểu đồ time series dạng PNG.
  Xử lý batch tối đa 5 từ khóa mỗi lần.
---

# Google Trends

Cách dùng ví dụ: python google-trends/tool.py --keyword "cottagecore tshirt" --geo "US" --timeframe "today 1-m"

Phân tích xu hướng tìm kiếm Google cho **một hoặc nhiều từ khóa**.  
Tool tự động chia thành các batch ≤5 từ khóa (giới hạn Google Trends API) và xử lý tuần tự.

---

## Tham số

- `keyword` (List[str] | str)  
  Một từ khóa hoặc danh sách từ khóa cần phân tích.  
  Ví dụ: `["frog meme shirt", "cottagecore tee"]`

- `geo` (str, mặc định `"US"`)  
  Mã vùng địa lý theo ISO.  
  Ví dụ: `"US"`, `"GB"`, `"VN"`, `""` (toàn cầu)

- `timeframe` (str, mặc định `"today 1-m"`)  
  Khoảng thời gian phân tích.

---

## Giá trị `timeframe` phổ biến

| Giá trị | Ý nghĩa |
|----------|----------|
| `"now 1-H"` | 1 giờ qua |
| `"now 7-d"` | 7 ngày qua |
| `"today 1-m"` | 1 tháng qua *(mặc định)* |
| `"today 3-m"` | 3 tháng qua |
| `"today 12-m"` | 12 tháng qua |
| `"today 5-y"` | 5 năm qua |

---

## Trả về

Chuỗi JSON gồm danh sách kết quả theo từng batch:

```json
[
  {
    "batch_keywords": "frog meme shirt, cottagecore tee",
    "summary": [
      {
        "query": "frog meme shirt",
        "avg_interest": 45.2,
        "recent_avg": 60.3,
        "stability": "stable",
        "direction": "rising",
        "change_pct": 33.4,
        "peak_value": 100,
        "min_value": 12
      }
    ],
    "trend_chart_path": "charts/frog_meme_shirt_20250330_143012.png"
  }
]

Giải thích summary
Trường	Ý nghĩa
avg_interest	Điểm quan tâm trung bình (0–100)
recent_avg	Trung bình 1/4 chuỗi thời gian gần nhất
stability	"stable" nếu (std / mean) ≤ 0.5, ngược lại "volatile"
direction	"rising" / "declining" / "flat" dựa trên thay đổi đầu–cuối
change_pct	% thay đổi giữa giai đoạn đầu và gần nhất
peak_value	Điểm quan tâm cao nhất
min_value	Điểm quan tâm thấp nhất
Quy tắc batching
Tối đa 5 từ khóa / batch (giới hạn API).
Nếu truyền 12 từ khóa → tự chia thành 3 batch (5 + 5 + 2).
Mỗi batch tạo 1 biểu đồ PNG riêng trong thư mục charts/.

Best Practices
Nhóm các từ khóa liên quan trong cùng batch để biểu đồ so sánh có ý nghĩa.
Dùng "today 3-m" hoặc "today 12-m" để đánh giá xu hướng dài hạn.
direction = "rising" + stability = "stable" thường là tín hiệu thị trường tốt.
Nếu change_pct cao nhưng stability = "volatile", có thể là trend ngắn hạn.
Cần biến môi trường SERPAPI_API_KEY để tool hoạt động.