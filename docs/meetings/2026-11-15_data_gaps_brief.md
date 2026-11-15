# Brief cuộc họp #8 — rà soát dữ liệu: thiếu gì, có cần bổ sung không (15/11/2026)

## Dữ liệu hiện có
- NREL SEA-WTK v3 (WRF 9 km/60 phút → sup3r GAN 3 km/15 phút), 100 m hub, 2017–2021, 175.200 mẫu/trạm, 0 gap. Có sẵn trong WTK: 2007–2021, độ cao 10–200 m.
- 8 trạm, 4 chế độ × 2 (A–D gốc, E–H thêm ở họp #5). Thêm năm 2016 làm test lùi thời gian.
- 31 đặc trưng; bộ W 19 đặc trưng. Chia 70/15/15 theo thời gian (test 04–12/2021).
- API key NREL đã có; tải 1 trạm × 1 năm mất vài phút (giới hạn 1 req/s).

## Các khoảng trống Claude nhận thấy
1. **Không có dữ liệu đo thực.** Toàn bộ là dữ liệu mô hình hoá; reviewer có thể hỏi kết quả có đúng với gió thật không. Chưa rõ có nguồn đo công khai nào ở VN (vd chiến dịch đo gió ESMAP/World Bank, trạm khí tượng) dùng được hay không.
2. **LOSO chỉ có 4 fold (A–D).** Wilcoxon theo trạm đích với n = 4 có p nhỏ nhất = 0.125 → không bao giờ có ý nghĩa thống kê. Ma trận chéo 8×8 có n = 8 (p nhỏ nhất 0.0078). LOSO trên 8 trạm chưa chạy.
3. **Test chính thiếu lõi gió mùa Đông Bắc** (test bắt đầu 04/2021) — đã bù bằng 2016, nhưng 2016 là đánh giá lùi thời gian.
4. **Một độ cao (100 m)**; không kiểm tra 80/120 m.
5. **Few-shot chỉ 2 cửa sổ mùa** (kết thúc 31/03 và 01/07/2020).
6. **Trạm F**: khoảng cách tới bờ ≤ 5 km chưa xác nhận (điều kiện họp #6).
7. **Không có dự báo NWP làm đầu vào** (vận hành thực thường dùng) — hiện là dự báo thuần chuỗi thời gian.
8. Mỗi chế độ chỉ 2 trạm; năm khảo sát 5 năm trong khi WTK có 15 năm.

## Câu hỏi cần chốt
1. Khoảng trống nào **bắt buộc** xử lý trước khi nộp (reviewer Q1–Q3 sẽ bắt), cái nào chỉ cần nêu là hạn chế?
2. Có cần tải thêm dữ liệu không (thêm năm, thêm trạm, thêm độ cao, dữ liệu đo)? Nếu có: cụ thể gì, chi phí (thời gian tải, GPU) bao nhiêu?
3. Có nên chạy LOSO trên 8 trạm (8 fold) để kiểm định có ý nghĩa không? Vị trí trong hàng đợi GPU hiện tại (LOSO-W 5 seed A–D → scratch 2000 bước → E1-W 8 trạm + chéo W → SHAP → PatchTST)?
