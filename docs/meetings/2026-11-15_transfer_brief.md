# Brief cuộc họp #6 — kết quả chuyển giao + xác nhận quyết định (15/11/2026)

## Kết quả mới từ họp #5

**1. Thêm 4 trạm (E Thanh Hoá, F Bình Định, G Hướng Hoá, H vịnh Bắc Bộ)**, E1 đủ 5 mô hình × 5 seed. Hash 4 trạm cũ không đổi.

**2. Ma trận chấm chéo 8×8** (mô hình học tại 1 trạm, đủ 31 đặc trưng, chấm trạm khác; skill vs persistence):
| | Mamba 1h | Transformer 1h | RF 1h | Mamba 6h | RF 6h |
|---|---|---|---|---|---|
| tại trạm | +16.0% | +15.3% | +15.5% | +27.8% | +25.2% |
| cùng chế độ | −4.6% | −5.3% | −3.0% | +7.7% | +5.8% |
| khác chế độ | −20.9% | −23.3% | −17.9% | −16.3% | −14.3% |

**3. Tập test lùi thời gian 2016** (8 trạm, không huấn luyện lại; RMSE 1h): cả năm Mamba 0.620, Transformer 0.619, RF 0.621, LSTM 0.638, DLinear 0.679, persistence 0.736. Gió mùa ĐB (tháng 1–3): 0.483 / 0.474 / 0.480 / 0.496 / 0.540 / 0.593. Mọi mô hình vượt persistence mọi mùa.

**4. E7 — LOSO theo bộ đặc trưng** (A–D, 3 seed; skill trung bình 4 trạm; "W" = chỉ tốc độ gió, 19 đặc trưng):
| | 1h | 3h | 6h | RMSE 1h A / B / C / D |
|---|---|---|---|---|
| Mamba-31 | −1.8% | −2.1% | +0.9% | 0.811 / 0.631 / 0.618 / 0.596 |
| **Mamba-W** | **+2.2%** | −0.4% | **+2.2%** | 0.849 / 0.633 / **0.543** / **0.550** |
| RF-31 | −6.0% | −5.0% | −2.6% | 0.806 / 0.674 / 0.587 / 0.682 |
| RF-W | +1.4% | +0.2% | +1.3% | 0.798 / 0.633 / 0.581 / 0.567 |
Persistence 1h: 0.845 / 0.640 / 0.608 / 0.538. Dải seed Mamba-W 1h: A 0.800–0.939 (1 seed lệch), B 0.619–0.652, C 0.516–0.578, D 0.539–0.564.
Delta target (E8, RF): −4.4% (chỉ giúp ít). "Đại lượng tương đối" (27 đặc trưng, RF): −3.4%.

**5. Đánh đổi**: với trạm đã có trong huấn luyện (global), bỏ biến khí tượng làm RMSE tăng 3–5% (Mamba global 1h W vs 31: A 0.725 vs 0.692; D 0.521 vs 0.501).

**Đang chạy**: E9 few-shot (Mamba, khởi tạo từ LOSO-W, 1/2/4 tuần, 2 cửa sổ mùa, so học từ đầu). Sau đó PatchTST còn 14/20 lượt.

## Ba quyết định Claude đã tự đưa ra — cần xác nhận hoặc yêu cầu làm lại
- **Q1.** Bỏ thí nghiệm RF "chỉ tốc độ gió + delta" (hết RAM: cây 73 triệu nút; delta đơn lẻ chỉ giúp −6.0% → −4.4%).
- **Q2.** Dời PatchTST xuống cuối hàng đợi (19 phút/lượt, baseline yếu nhất; ưu tiên LOSO-W và few-shot).
- **Q3.** Nới ngưỡng mean trạm ven biển 6.0 → 5.5 m/s khi chọn trạm F (Bình Định 5.73 m/s); ứng viên ≥ 6 m/s duy nhất (Tuy Phong) trượt vì tương quan 0.81 với B.

## Câu hỏi cần chốt
1. Xác nhận / bác Q1–Q3.
2. Câu chuyện chuyển giao cho bài: "cùng chế độ ≫ khác chế độ" + "biến khí tượng tuyệt đối là mã trạm ngầm; bỏ chúng thì zero-shot vượt persistence" — trình bày thế nào, cần kiểm định gì (3 seed)?
3. Đánh đổi (mục 5): khuyến nghị cấu hình nào cho vận hành (trạm có dữ liệu vs trạm mới)? Có nên chạy E1 bản W cho đủ so sánh?
4. Thứ tự việc còn lại với GPU: SHAP (E10), conformal (E11, CPU), tổng hợp 08/14 cho 8 trạm, PatchTST, thêm seed cho fold A (Mamba-W lệch 0.939)? Khi nào chuyển sang viết bản thảo?
