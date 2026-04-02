# Etsy Taxonomy Reference

Tài liệu tham khảo nhanh về Etsy taxonomy IDs áo thun và các từ khóa niche phổ biến.

---

## Taxonomy IDs áo thun (T-shirt)

Tool `search_etsy_trends_by_keyword` và `get_etsy_top_listings` tự động deduplicate kết quả trên **3 taxonomy IDs sau**:

| Taxonomy ID | Danh mục | Ghi chú |
|---|---|---|
| **449** | Men's Clothing → Tops & Tees → T-Shirts | Áo thun nam |
| **482** | Women's Clothing → Tops & Tees → T-Shirts | Áo thun nữ |
| **559** | Unisex Clothing → Tops & Tees → T-Shirts | Áo thun unisex |

> Mỗi keyword được tìm kiếm trên cả 3 IDs rồi deduplicate theo `listing_id` trước khi phân tích.

---

## Niche phổ biến theo nhóm

### 🐸 Meme & Viral Culture
- `frog meme shirt` — Pepe, Kermit, cottagecore frog
- `cat meme tee` — grumpy cat, business cat
- `dog meme shirt` — doge, shiba inu
- `internet meme tshirt` — broad meme themes

### 🌿 Aesthetic & Lifestyle
- `cottagecore tshirt` — floral, mushroom, nature aesthetic
- `dark academia tee` — books, vintage, moody
- `dark floral tshirt` — gothic botanical
- `mushroom tshirt` — fungi, foraging aesthetic
- `goblincore tee` — rocks, bugs, nature oddities

### 🎨 Art & Design Styles
- `vintage retro tshirt` — 70s/80s/90s throwback
- `botanical print tee` — nature illustration
- `watercolor tshirt` — painted art style
- `minimalist tshirt` — clean, simple design

### 💪 Activism & Statement
- `feminist tshirt` — empowerment, rights
- `lgbtq tshirt` — pride themes
- `mental health awareness tee` — self-care, awareness
- `social justice tshirt` — advocacy

### 🎮 Pop Culture & Fandoms
- `anime tshirt` — general anime aesthetic
- `gaming tshirt` — gamer culture
- `book lover tee` — reading, library aesthetic
- `plant mama tshirt` — plant parent culture

### 🌙 Spiritual & Witchy
- `witchy tshirt` — moon, crystals, tarot
- `astrology tshirt` — zodiac signs
- `celestial tee` — stars, moon, sun
- `manifestation shirt` — law of attraction

### 🐾 Animals & Nature
- `animal lover tshirt` — pets, wildlife
- `dog mom tee` — dog parent culture
- `cat lady shirt` — cat parent culture
- `wildlife tshirt` — birds, foxes, bears

### 💼 Occupation & Identity
- `teacher tshirt` — educator themes
- `nurse tee` — healthcare worker
- `mom shirt` — motherhood themes
- `girl dad tee` — fatherhood

---

## Tips tìm kiếm hiệu quả

1. **Bắt đầu broad, sau đó narrow**: Tìm `cottagecore tshirt` trước, xem `top_tags` dẫn đến `mushroom cottagecore tee` cụ thể hơn.

2. **Kết hợp aesthetic + item**: `"[aesthetic] tshirt"` thường cho kết quả chính xác hơn `"[aesthetic] shirt"` hay `"[aesthetic] tee"`.

3. **Plural vs. singular**: Thử cả hai — Etsy dùng cả `tshirt` lẫn `t-shirt` lẫn `tee`.

4. **Seasonal keywords**: Thêm năm hoặc mùa khi cần (`summer 2026`, `spring tshirt`) để lọc listing mới.

5. **`days_back` param**: Dùng `days_back=7` để chỉ xem listing rất mới (hot), `days_back=90` để xem trend dài hạn hơn.
