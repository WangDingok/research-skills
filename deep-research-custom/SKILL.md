---
name: deep-research-custom
description: Sử dụng kỹ năng này thay vì WebSearch thông thường cho BẤT KỲ câu hỏi nào yêu cầu nghiên cứu web chuyên sâu và khám phá trending hiện tại. Kích hoạt khi có các câu hỏi như "X là gì", "giải thích về X", "so sánh X và Y", "nghiên cứu về X", hoặc trước các tác vụ tạo nội dung. Cung cấp phương pháp nghiên cứu đa chiều có hệ thống thay vì các tìm kiếm đơn lẻ hời hợt. Sử dụng kết hợp với các kỹ năng (Skills trong cùng thư mục hiện tại) với các folder là tavily-web-search, twitter-trends, google-ai-search để thực hiện tìm kiếm và truy xuất nội dung.
---

# Kỹ năng Nghiên cứu Chuyên sâu (Deep Research)

## Tổng quan

Kỹ năng này cung cấp một phương pháp luận có hệ thống để thực hiện nghiên cứu web kỹ lưỡng. **Hãy tải kỹ năng này TRƯỚC KHI bắt đầu bất kỳ tác vụ tạo nội dung nào** để đảm bảo bạn thu thập đủ thông tin từ nhiều góc độ, chiều sâu và nguồn khác nhau.

Kỹ năng này được thiết kế để hoạt động cùng với kỹ năng [tavily-web-search], [twitter-trends] và [google-ai-search]. Khi dùng Skill này hãy sử dụng toàn bộ các kỹ năng trên để có kết quả nghiên cứu tốt nhất.

## Khi nào cần sử dụng kỹ năng này

**Luôn tải kỹ năng này khi:**

### Các câu hỏi nghiên cứu
- Hỏi về xu hướng trending, tin tức mới nhất, hoặc các chủ đề đang nổi. 
- Người dùng muốn hiểu sâu về một khái niệm, công nghệ hoặc chủ đề.
- Câu hỏi yêu cầu thông tin hiện tại, toàn diện từ nhiều nguồn.
- Một lần tìm kiếm web đơn lẻ là không đủ để trả lời chính xác và đầy đủ.

### Tạo nội dung (Giai đoạn tiền nghiên cứu)
- Viết bài báo, báo cáo hoặc tài liệu hướng dẫn.
- Bất kỳ nội dung nào yêu cầu thông tin thực tế, ví dụ thực tế hoặc dữ liệu cập nhật.

## Nguyên tắc cốt lõi

**Đừng bao giờ tạo nội dung chỉ dựa trên kiến thức chung có sẵn.** Chất lượng đầu ra của bạn phụ thuộc trực tiếp vào chất lượng và số lượng nghiên cứu được thực hiện trước đó. Một truy vấn tìm kiếm đơn lẻ KHÔNG BAO GIỜ là đủ.

## Phương pháp luận nghiên cứu

### Giai đoạn 1: Khám phá rộng (Broad Exploration)

Bắt đầu với các tìm kiếm rộng để hiểu bức tranh toàn cảnh:

1. **Khảo sát ban đầu**: Tìm kiếm chủ đề chính để hiểu ngữ cảnh tổng thể.
2. **Xác định các khía cạnh**: Từ kết quả ban đầu, xác định các chủ đề phụ, chủ đề liên quan, hoặc các góc độ cần khám phá sâu hơn.
3. **Lập bản đồ thông tin**: Ghi chú các quan điểm khác nhau, các bên liên quan hoặc các luồng ý kiến hiện có.

### Giai đoạn 2: Đào sâu (Deep Dive)

Đối với mỗi khía cạnh quan trọng đã xác định, thực hiện nghiên cứu mục tiêu:

1. **Truy vấn cụ thể**: Tìm kiếm với các từ khóa chính xác cho từng chủ đề phụ.
2. **Sử dụng nhiều cách diễn đạt**: Thử các tổ hợp từ khóa và cách diễn đạt khác nhau (đặc biệt là tiếng Anh nếu nghiên cứu thị trường quốc tế).
3. **Truy xuất nội dung đầy đủ**: Sử dụng chức năng `fetch_content` trong kỹ năng `tavily-web-search` để đọc các nguồn quan trọng một cách đầy đủ, không chỉ dựa vào các đoạn trích dẫn (snippets).
4. **Theo dõi các tham chiếu**: Khi một nguồn đề cập đến các tài liệu quan trọng khác, hãy tìm kiếm cả những tài liệu đó.

### Giai đoạn 3: Tính đa dạng & Xác thực

Đảm bảo bao phủ toàn diện bằng cách tìm kiếm các loại thông tin đa dạng:

| Loại thông tin | Mục đích | Ví dụ tìm kiếm |
|-----------------|---------|------------------|
| **Sự thật & Dữ liệu** | Bằng chứng cụ thể | "thống kê", "dữ liệu", "con số", "quy mô thị trường" |
| **Ví dụ & Trường hợp** | Ứng dụng thực tế | "nghiên cứu điển hình", "ví dụ", "triển khai thực tế" |
| **Ý kiến chuyên gia** | Quan điểm có thẩm quyền | "phân tích chuyên gia", "phỏng vấn", "bình luận" |
| **Xu hướng & Dự báo** | Định hướng tương lai | "xu hướng 2026", "dự báo", "tương lai của" |
| **So sánh** | Ngữ cảnh và thay thế | "so với", "so sánh", "giải pháp thay thế" |
| **Thử thách & Phê bình** | Cái nhìn đa chiều | "thử thách", "hạn chế", "phê bình" |

### Giai đoạn 4: Kiểm tra tổng hợp (Synthesis Check)

Trước khi tiến hành tạo nội dung, hãy xác nhận:

- [ ] Tôi đã tìm kiếm từ ít nhất 3-5 góc độ khác nhau chưa?
- [ ] Tôi đã truy xuất và đọc đầy đủ các nguồn quan trọng nhất chưa?
- [ ] Tôi có dữ liệu cụ thể, ví dụ và quan điểm chuyên gia chưa?
- [ ] Tôi đã khám phá cả khía cạnh tích cực và các thách thức/hạn chế chưa?
- [ ] Thông tin của tôi có cập nhật và từ các nguồn có thẩm quyền không?

**Nếu có bất kỳ câu trả lời nào là KHÔNG, hãy tiếp tục nghiên cứu trước khi tạo nội dung.**

## Mẹo chiến lược tìm kiếm

### Các mẫu truy vấn hiệu quả

- Cụ thể hóa ngữ cảnh: Thay vì "xu hướng AI", hãy dùng "xu hướng áp dụng AI trong doanh nghiệp 2026".
- Dùng từ khóa gợi ý nguồn uy tín: "[chủ đề] McKinsey report", "[chủ đề] white paper", "[chủ đề] academic research".
- Tìm kiếm theo loại nội dung: "[chủ đề] case study", "[chủ đề] thong ke", "[chủ đề] interview".
- Sử dụng mốc thời gian: Luôn sử dụng năm hiện tại từ `<current_date>`.

### Nhận thức về thời gian

**Luôn kiểm tra `<current_date>` trong ngữ cảnh của bạn trước khi tạo BẤT KỲ truy vấn tìm kiếm nào.**

Sử dụng mức độ chính xác phù hợp:
- Nếu hỏi về "hôm nay", "vừa mới ra mắt": Dùng **Tháng + Ngày + Năm**.
- Nếu hỏi về "tuần này": Dùng **Khoảng thời gian trong tuần**.
- Nếu hỏi về "gần đây", "mới nhất": Dùng **Tháng + Năm**.

## Sử dụng kết hợp với Tavily Web Search, Twitter Trends và Google AI Search để có kết quả nghiên cứu tốt nhất:
1. **Tavily Web Search**: Dùng để truy xuất nội dung chi tiết từ các nguồn quan trọng. Luôn sử dụng `fetch_content=True` cho các trang có vẻ chứa nhiều dữ liệu quan trọng.
2. **Twitter Trends**: Dùng để nắm bắt các xu hướng đang nổi trên mạng xã hội, đặc biệt là những chủ đề viral và các tín hiệu thời sự.
3. **Google AI Search**: Dùng để khám phá các chủ đề xu hướng, phân tích chuyên sâu và tìm kiếm các quan điểm chuyên gia tổng hợp từ nhiều nguồn khác nhau.

## Tiêu chuẩn chất lượng

Nghiên cứu của bạn được coi là đủ khi bạn có thể tự tin trả lời:
- Các sự thật và điểm dữ liệu chính là gì?
- Có ít nhất 2-3 ví dụ thực tế cụ thể không?
- Các chuyên gia nói gì về chủ đề này?
- Các xu hướng hiện tại và hướng đi tương lai là gì?
- Các thách thức hoặc hạn chế là gì?
- Điều gì làm cho chủ đề này phù hợp hoặc quan trọng vào lúc này?
