---
name: twitter-trends
description: >
  Lấy các chủ đề đang trending trên Twitter/X. Dùng khi cần khám phá các từ khóa, hashtag, 
  chủ đề đang được thảo luận sôi nổi trên mạng xã hội. Không cần API key. Hỗ trợ hai chế độ: 
  featured (nổi bật theo biên tập) và statistics (xếp hạng theo lượt đề cập/volume).
---

# Skill: Twitter Trends

Hướng dẫn sử dụng `tool.py` để xác định các chủ đề và niche đang thịnh hành trên Twitter/X.

## 1. Cách chạy Code Tool (tool.py)

File [tool.py](tool.py) hỗ trợ giao diện dòng lệnh (CLI) để lấy xu hướng Twitter/X:

### Lấy xu hướng nổi bật (Featured)
Sử dụng `--type featured`. Mặc định quốc gia là `united-states` và thời gian là `month`.
```bash
python tool.py --type featured --country united-states --mode month
```

### Lấy thống kê chi tiết (Statistics - Rank & Volume)
Sử dụng `--type statistics`. Mặc định thời gian là `30d`.
```bash
python tool.py --type statistics --country united-states --mode 7d
```

### Các đối số (Arguments):
- `--type`: `featured` (nổi bật) hoặc `statistics` (thống kê lượt đề cập). **Bắt buộc**.
- `--country`: Tên quốc gia dạng slug (mặc định: `united-states`).
- `--mode`: 
    - Cho `featured`: `day`, `week`, `month`.
    - Cho `statistics`: `24h`, `7d`, `30d`.
- `--timeout`: Thời gian chờ tối đa (mặc định: `20`).

---
## Best Practices


- **Chạy cả hai công cụ song song**: `featured` để bắt trend bất ngờ, `statistics` để xác nhận trend lớn.
- **Kết hợp với Google Trends** (skill `google-trends`): Twitter cho biết "đang hot trên mạng xã hội", Google Trends cho biết "đang được tìm kiếm nhiều" — kết hợp cả hai cho tín hiệu mạnh hơn.
- **Không cần API key**: Tool hoạt động bằng web scraping — dùng được ngay, nhưng tốc độ phụ thuộc vào mạng.
- **Cache tích hợp sẵn**: kết quả được cache 1 giờ.
- **Lọc kết quả**: Tập trung vào các từ khóa có thể áp dụng vào thiết kế áo thun — bỏ qua tin tức chính trị, thể thao trực tiếp.
