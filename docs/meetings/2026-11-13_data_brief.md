# Brief cuộc họp #5 — có mở rộng dữ liệu không (13/11/2026)

## Bối cảnh mới từ họp #3–#4
- Kế hoạch v2.0 (docs/Ke_hoach_du_an_v2.docx): định vị bài = benchmark nghiêm ngặt (C1) + hiệu quả Mamba từng bước (C2) + chuyển giao giữa chế độ gió (C3) + SHAP vật lý (C4) + khả năng dự báo theo chế độ (C5) + minh bạch dữ liệu (C6).
- Đã đọc toàn văn 3 bài: PowerMamba (IEEE TPWRS 2026 — Mamba chỉ cạnh tranh, không persistence/kiểm định); VMamba-WSP (Energy Reports 2026 — tốc độ gió ERA5 lưới 13×13, Mamba kém ConvGRU 16%, chậm 30×, 3 seed); Despotovic et al. (IJGE 2026 — 70 trạm Tây Ban Nha, chuyển giao zero-shot với ELM/AR chỉ dùng lag tốc độ gió ≈ học tại trạm, TL Score −8…+4%, không so persistence).
- Thí nghiệm đã lên kế hoạch: E7 ablation đặc trưng cho LOSO (chỉ tốc độ gió vs đủ 31 đặc trưng — giả thuyết áp suất/mật độ là "site ID ngầm"), E8 delta target, E9 few-shot, E10 SHAP, E11 conformal. PatchTST E1 đang chạy.

## Dữ liệu hiện tại
4 trạm × 1 trạm/chế độ (A đất liền Hà Nội, B ven biển Ninh Thuận, C đồi núi Gia Lai, D ngoài khơi Bình Thuận), NREL SEA WTK v3, 2017–2021, 15 phút, 100 m, 31 đặc trưng. Chia 70/15/15: train 01/2017–07/2020, val 07/2020–04/2021, test 03/04–31/12/2021 (thiếu lõi gió mùa Đông Bắc tháng 1–3). WTK có sẵn 2007–2021. API NREL miễn phí (~1 request/trạm/năm).

## Vấn đề
- Mỗi chế độ chỉ có 1 trạm → mọi fold LOSO đều là chuyển giao **khác chế độ**; không tách được "khác chế độ" với "khác trạm".
- Tập test thiếu tháng 1–3.

## Các phương án
| | Nội dung | Dùng lại kết quả hiện có | GPU thêm (ước) |
|---|---|---|---|
| A | Giữ 4 trạm. Chỉ chạy E7–E11. Ghi hạn chế về tập test | Tất cả | ~6 h |
| B | Thêm 4 trạm (mỗi chế độ thêm 1), cùng giai đoạn/cách chia. LOSO 8 trạm: so chuyển giao cùng chế độ vs khác chế độ | E1, tuning, latency của A–D | E1 4 trạm ~5 h + LOSO lại ~16 h (8 fold) + E7–E11 ~6 h |
| C | Thêm năm 2016, chia lại (train 2016–2019 / val 2020 / test cả 2021), có hoặc không thêm trạm | Không (làm lại hết) | ~25–40 h |

Ngân sách: Colab T4 miễn phí, phiên ~12 h, đã từng mất runtime và phải đổi tài khoản; mọi job có cơ chế chạy tiếp.

## Câu hỏi cần chốt
1. Phương án A, B hay C (hoặc biến thể, ví dụ B nhưng LOSO chỉ cho Mamba + RF, hay B với chỉ 2 trạm thêm cho chế độ quan trọng nhất)?
2. Nếu B: toạ độ cụ thể (lat, lon) cho 4 trạm mới, mỗi chế độ 1 trạm, khác biệt đủ xa trạm cũ nhưng cùng chế độ; tiêu chí chọn. (Nhắc lại: trạm B cũ từng sai vì nằm sâu trong đất liền 25 km.)
3. Thứ tự với E7–E11: mở rộng dữ liệu trước hay chạy E7/E8 trên 4 trạm trước rồi quyết?
4. Vấn đề tập test thiếu tháng 1–3: xử lý thế nào trong phương án được chọn?
