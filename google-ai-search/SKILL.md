---
name: google-ai-search
description: >
  Tìm kiếm bằng Google AI Mode (SGE) để lấy tóm tắt AI toàn diện về một chủ đề. Dùng khi cần 
  tóm tắt nhanh có cấu trúc, ý tưởng niche, điểm chính, và gợi ý sản phẩm từ Google AI. 
---

# Skill: Google AI Search

## 1. Cách chạy Code Tool (tool.py)

File [tool.py](tool.py) hỗ trợ giao diện dòng lệnh (CLI) để thực hiện tìm kiếm bằng Google AI Mode (SGE):

### Chạy tìm kiếm đơn giản
```bash
python tool.py --query "floral t-shirt trends 2025"
```

### Chạy tìm kiếm cho khu vực địa lý cụ thể
Mặc định là `US`, bạn có thể thay đổi bằng `--geo`.
```bash
python tool.py --query "cottagecore aesthetic" --geo US
```

### Các đối số (Arguments):
- `--query`: Từ khóa hoặc câu hỏi tìm kiếm. (Đưa phần tiêu chí lọc trend vào query) **Bắt buộc**.
- `--geo`: Khu vực địa lý (ví dụ: `US`, `UK`, `CA`). Mặc định: `US`.
- `--timeout`: Thời gian chờ tối đa giây (mặc định: `30`).

---

## 2. Hướng dẫn Nghiên cứu (Agent Guidelines)

Khi sử dụng công cụ này, bạn phải tuân thủ các quy tắc sau:

### Nguyên tắc Ngôn ngữ & Thị trường
- **Thị trường mục tiêu**: Mặc định là **US**.
- **LUÔN dùng tiếng Anh** cho mọi tham số khi gọi tool (`--query`). KHÔNG dùng tiếng Việt.

### Tiêu chí lọc trend (ÁP DỤNG LUÔN khi khám phá trend):
- **Thời gian**: Chỉ chọn trend có độ dài từ **10 ngày trở lên**.
- **Phân loại trend**: Xác định trend thuộc loại nào:
    1. **EVENT-BASED**: Sự kiện, lễ hội, ra mắt phim.
    2. **SEASONAL**: Theo mùa, ngày lễ.
    3. **CULTURE**: Phong cách sống (cottagecore, dark academia).
    4. **VIRAL TOPIC**: Chủ đề lan truyền mạnh.
    5. **IDENTITY/COMMUNITY**: Fandom, cộng đồng, nghề nghiệp.

Khi gọi tool hãy truyền toàn bộ tiêu chí lọc trend ở trên bằng tiếng anh vào. Câu query phải đầy đủ và chi tiết vì bạn đang giao tiếp với một AI Agent có khả năng hiểu ngôn ngữ tự nhiên.

### Định dạng Phản hồi
Phản hồi cuối cùng phải là danh sách các niche kèm mô tả ngắn gọn kết hợp phân loại theo các tiêu chí lọc trend.

## Đọc kết quả

- **`reconstructed_markdown`**: Phần tóm tắt AI — đọc trực tiếp để lấy ý tưởng và điểm chính. Đây là phần giá trị nhất.
- **`references`**: Danh sách URL nguồn — có thể truyền dùng skills 'tavily-web-search' nếu cần đọc chi tiết.
---

## Best Practices

- **Ưu tiên dùng ở giai đoạn discovery**: phù hợp nhất khi bắt đầu nghiên cứu một chủ đề mới.
- **Kết hợp với Google Trends** (skill `google-trends`): dùng Google AI Search để tìm ý tưởng, sau đó xác nhận từ khóa bằng Google Trends.
- **Phụ thuộc `SERPAPI_API_KEY`**: Cần biến môi trường này. Nếu không có, tool sẽ không khả dụng.
