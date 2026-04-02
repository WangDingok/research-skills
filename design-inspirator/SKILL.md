---
name: design-inspirator
description: 
  Sử dụng sau khi đã xác định được một niche/trend cụ thể. Skill này sẽ tìm kiếm và thu thập các nguồn cảm hứng thiết kế, ý tưởng sản phẩm, bảng màu, và các ví dụ thực tế từ web và các trang thương mại điện tử để hỗ trợ quá trình sáng tạo.
---

**Khai thác và Tìm cảm hứng (Chạy song song)**
1.  **Mục tiêu**: Thu thập thông tin để phục vụ thiết kế sản phẩm theo trend.
2.  **Hành động**: Với mỗi trend, khởi chạy đồng thời Skill sau:
    *   Sử dụng Skill `tavily-web-search` với vai trò mở rộng: yêu cầu nó tìm kiếm các ý tưởng thiết kế, mẫu áo thun phổ biến, bảng màu, và các sản phẩm liên quan.
    *   Sử dụng Skill `google-ai-search` để tìm các ví dụ về sản phẩm trên các nền tảng thương mại điện tử khác nhau.
    *   Sử dụng Skill `etsy-market-research` để phân tích các sản phẩm áo thun đang bán chạy trên Etsy liên quan đến trend đó.
3.  **Tổng hợp**: Sau khi tất cả các Skill hoàn thành, tổng hợp kết quả để tạo một bộ sưu tập ý tưởng thiết kế, bảng màu, và các ví dụ sản phẩm thực tế liên quan đến trend đã chọn. Đây sẽ là nguồn cảm hứng quan trọng cho giai đoạn thiết kế sản phẩm sau này.

---

## Lưu ý

- Khi gọi `tavily-web-search`, hãy yêu cầu nó tập trung vào các trang web thiết kế, blog thời trang, và các nền tảng thương mại điện tử để tìm kiếm ý tưởng thiết kế và bảng màu.
- Khi gọi `google-ai-search`, hãy yêu cầu nó tìm kiếm các ví dụ về sản phẩm áo thun đang bán chạy trên các nền tảng thương mại điện tử như Amazon, eBay, và các cửa hàng trực tuyến khác.
- Khi gọi `etsy-market-research`, hãy yêu cầu nó phân tích các sản phẩm áo thun đang bán chạy trên Etsy liên quan đến trend đã chọn, bao gồm các yếu tố thiết kế phổ biến, bảng màu, và các từ khóa liên quan.

