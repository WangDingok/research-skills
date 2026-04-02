---
name: tavily-web-search
description: >
  Tìm kiếm web và đọc nội dung trang web. Dùng khi cần tìm thông tin từ internet, tin tức, 
  xu hướng mới nổi, thảo luận cộng đồng, bài viết blog. Hỗ trợ tìm kiếm đơn lẻ (tavily_search), 
  tìm kiếm batch song song nhiều query (tavily_search_async) và đọc nội dung đầy đủ trang web.
---

# Skill: Tavily Web Search

Hướng dẫn sử dụng `tool.py` để thực hiện nghiên cứu chuyên nghiệp bằng Tavily API, tuân thủ các nguyên tắc của `TAVILY_SEARCH_AGENT_INSTRUCTIONS`.


## 1. Cách chạy Code Tool (tool.py)

File [tool.py](tool.py) hỗ trợ giao diện dòng lệnh (CLI) để thực hiện tìm kiếm:

### Chạy tìm kiếm đơn giản
```bash
python tool.py --query "floral t-shirt trend 2025"
```

### Chạy tìm kiếm và lấy nội dung chi tiết trang web
Sử dụng flag `--fetch_content` để công cụ tải và chuyển đổi nội dung HTML sang Markdown.
```bash
python tool.py --query "Wicked movie merchandise trends" --fetch_content
```

---

## 2. Hướng dẫn Nghiên cứu (Agent Guidelines)

Khi sử dụng công cụ này, bạn phải tuân thủ các quy tắc sau:

### Nguyên tắc Ngôn ngữ & Thị trường
- **LUÔN dùng tiếng Anh** cho mọi truy vấn (`--query`) khi nghiên cứu thị trường quốc tế (US).
- Đúng: `python tool.py --query "cottagecore fashion trends 2025"`
- Sai: `python tool.py --query "xu hướng thời trang cottagecore"`

### Quy trình Nghiên cứu 5 Bước
1. **Phân tích yêu cầu**: Xác định rõ thông tin cụ thể cần tìm.
2. **Tìm kiếm rộng**: Bắt đầu bằng các từ khóa tổng quát.
3. **Đánh giá & Think**: Sau mỗi lần chạy tool, hãy dừng lại đánh giá xem thông tin đã đủ chưa.
4. **Tìm kiếm hẹp**: Thực hiện các truy vấn chi tiết hơn để lấp đầy khoảng trống.
5. **Dừng đúng lúc**: Dừng lại khi đã có đủ thông tin (không cần hoàn hảo tuyệt đối).

### Giới hạn & Điểm dừng
- **Ngân sách**: Tối đa 3 lần tìm kiếm cho truy vấn đơn giản, 5 lần cho phức tạp.
- **Dừng ngay khi**:
    - Có đủ câu trả lời toàn diện.
    - Có ít nhất 3 nguồn/ví dụ chất lượng.
    - 2 lần tìm kiếm cuối cùng cho kết quả trùng lặp.

## Thể hiện suy nghĩ của bạn
Sau mỗi lần gọi công cụ tìm kiếm, hãy để phân tích kết quả:
- Tôi đã tìm thấy thông tin quan trọng nào?
- Còn thiếu thông tin gì?
- Tôi có đủ thông tin để trả lời câu hỏi một cách toàn diện không?
- Tôi nên tìm kiếm thêm hay cung cấp câu trả lời của mình?

## Định dạng Phản hồi 
Khi cung cấp kết quả của bạn:

1.  **Cấu trúc phản hồi của bạn**: Sắp xếp các phát hiện với các tiêu đề rõ ràng và giải thích chi tiết.
2.  **Trích dẫn nguồn trong văn bản**: Sử dụng định dạng [1], [2], [3] khi tham chiếu thông tin từ các tìm kiếm của bạn.
3.  **Bao gồm phần Nguồn**: Kết thúc bằng `### Nguồn` liệt kê mỗi nguồn được đánh số với tiêu đề và URL.

Ví dụ:
```
## Các phát hiện chính

Kỹ thuật ngữ cảnh (Context engineering) là một kỹ thuật quan trọng cho các agent AI. Các nghiên cứu cho thấy việc quản lý ngữ cảnh đúng cách có thể cải thiện hiệu suất lên 40%.

### Nguồn
 Hướng dẫn Kỹ thuật Ngữ cảnh: https://example.com/context-guide
 Nghiên cứu Hiệu suất AI: https://example.com/study
```
"""