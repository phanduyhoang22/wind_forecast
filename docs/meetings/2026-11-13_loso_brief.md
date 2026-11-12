# Brief cuộc họp #3 — sau LOSO (13/11/2026)

## Đã làm từ họp #2
- `08`: DM theo từng seed (k/5, Holm) + t ghép; ensemble báo riêng. `14`: phân tích theo chế độ (mùa/ngày-đêm/ramp). `09`: dùng tuned.json, lưu trọng số, có RF. `15`: latency riêng. Tất cả đã commit; chưa chạy `08` bản mới và `14` trên dự đoán mạng nơ-ron (cần dữ liệu trên Drive).
- Tập test xác nhận: 03/04/2021–31/12/2021 (thiếu lõi gió mùa Đông Bắc tháng 1–3).
- Latency CPU 1 luồng, batch 1 (ms): DLinear 0.43; **Mamba-step (hồi quy, cập nhật 1 quan sát mới) 1.62**; LSTM 2.44; Transformer 2.91; PatchTST 5.68; Mamba full-window 22.4; RF (500 cây depth 24, n_jobs=1) 34.9. Mamba-step khớp forward đầy đủ (lệch 9e-8).
- LOSO + global (3 seed; Mamba, Transformer trên GPU; RF trên CPU) — xong. PatchTST E1 đang chạy.

## Kết quả (RMSE m/s, mean 3 seed)

global = 1 mô hình huấn luyện trên train cả 4 trạm, chấm test từng trạm. loso = huấn luyện 3 trạm, chấm trạm thứ 4 chưa thấy (không site ID, không fine-tune). Local (E1, huấn luyện riêng, 5 seed) để so.

**1h**
| Trạm | Persist. | Local Mamba | Global Mamba | Global Transf. | Global RF | LOSO Mamba | LOSO Transf. | LOSO RF |
|---|---|---|---|---|---|---|---|---|
| A | 0.845 | 0.691 | 0.692 | 0.692 | 0.706 | 0.811 | 0.827 | 0.806 |
| B | 0.640 | 0.557 | 0.555 | 0.547 | 0.560 | **0.631** | 0.847 | 0.674 |
| C | 0.608 | 0.496 | 0.474 | 0.477 | 0.503 | 0.618 | 0.586 | 0.587 |
| D | 0.538 | 0.496 | 0.501 | 0.498 | 0.503 | 0.596 | 0.631 | 0.682 |

**3h**: LOSO Mamba/Transf./RF — A 1.670/1.549/1.521 (pers. 1.634); B 1.138/1.209/1.185 (1.191); C 1.165/1.133/1.162 (1.199); D 1.139/1.157/1.311 (1.004).
**6h**: A 2.175/2.049/1.959 (2.197); B 1.469/1.473/1.553 (1.538); C 1.488/1.440/1.548 (1.675); D 1.483/1.461/1.678 (1.314).

Skill LOSO vs persistence (trung bình 4 trạm): 1h Mamba −1.8%, RF −6.0%, Transformer −11.0%; 3h −2.1/−5.0/−1.5%; 6h +0.9/−2.6/+3.4%.

Độ biến thiên seed LOSO lớn: Mamba A 0.783–0.841, B 0.598–0.649, C 0.582–0.663; Transformer B 0.718–0.935 (cả 3 seed kém persistence), D 0.602–0.677.
Global ≈ local (C global tốt hơn: 0.474 vs 0.496); pooling không hại, đôi khi giúp.

## Câu hỏi cần chốt
1. Diễn giải kết quả LOSO: "zero-shot không vượt persistence" — đây là phát hiện chính hay hạn chế? Viết thế nào cho trung thực và có giá trị?
2. Mamba ổn định hơn ở 1h khi chuyển giao (đặc biệt B, D), Transformer sụp ở B. Có nói được gì về inductive bias, hay chỉ là nhiễu seed (3 seed)?
3. Có nên thêm thí nghiệm rẻ để biến LOSO thành câu chuyện hữu ích: (a) chuẩn hoá theo trạm đích dùng thống kê train của trạm đích (đã làm) vs chuẩn hoá theo cửa sổ; (b) few-shot fine-tune trên 1–4 tuần dữ liệu trạm đích; (c) dự báo "delta" (v(t+h) − v(t)) thay vì mức tuyệt đối để khử chênh lệch mean giữa trạm?
4. Ưu tiên tiếp theo với GPU còn lại: PatchTST E1 (đang chạy, ~6 h), SHAP, few-shot, thêm seed?
5. Khung bài cuối cùng: các đóng góp chính và thứ tự trình bày.
