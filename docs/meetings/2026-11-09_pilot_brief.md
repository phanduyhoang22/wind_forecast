# Brief cuộc họp #1 — sau pilot (09/11/2026)

## Bối cảnh
Bài báo: dự báo tốc độ gió hub 100 m, horizon 1h/3h/6h (4/12/24 bước × 15 phút), cửa sổ 96 bước (24h), 31 đặc trưng.
Dữ liệu NREL SEA WTK v3 (WRF 9km/60min → GAN sup3r 3km/15min), 4 trạm Việt Nam, 2017–2021, chia 70/15/15 theo thời gian có purge.
Mô hình chính Mamba (S6, kernel CUDA chính thức mamba-ssm, 70K tham số). Đối thủ: RF (500 cây, depth 16, đặc trưng tại bước cuối),
LSTM 60K, Transformer 71K (FFN 128), PatchTST 71K (không RevIN), DLinear 614.
Huấn luyện chung: AdamW lr 1e-3, wd 0.01, batch 128, MSE, ReduceLROnPlateau(3, 0.5), early stop patience 10 trên val, tối đa 50 epoch, mixed precision.
Code: scripts/04 (hợp đồng dữ liệu), 06 (mô hình), 07 (benchmark), 08 (tổng hợp + Diebold–Mariano), 09 (global/LOSO), 10 (SHAP), 11 (conformal).
Kế hoạch: E1 5 seed đầy đủ → E3 LOSO → E4/E5 SHAP → E6 conformal. Ngân sách: Colab T4 miễn phí (~12h/phiên).

## Kết quả pilot (1 seed; RF là 5 seed, std < 0.001)
RMSE (m/s). Persistence ở cột cuối.

| Trạm | H | RF | LSTM | Transf. | Mamba | PatchTST | DLinear | Persist. |
|---|---|---|---|---|---|---|---|---|
| A đất liền | 1h | 0.706 | 0.720 | 0.713 | **0.697** | 0.747 | 0.800 | 0.845 |
| | 3h | 1.284 | 1.261 | **1.241** | 1.251 | 1.313 | 1.381 | 1.634 |
| | 6h | 1.592 | 1.515 | 1.511 | **1.500** | 1.606 | 1.669 | 2.197 |
| B ven biển | 1h | 0.560 | 0.564 | 0.577 | **0.559** | 0.613 | 0.599 | 0.640 |
| | 3h | 0.975 | 0.993 | 0.973 | **0.965** | 1.021 | 1.065 | 1.191 |
| | 6h | 1.205 | 1.236 | **1.182** | 1.185 | 1.270 | 1.336 | 1.538 |
| C đồi núi | 1h | 0.504 | 0.486 | 0.511 | **0.476** | 0.547 | 0.544 | 0.608 |
| | 3h | 0.899 | 0.880 | 0.898 | **0.872** | 0.988 | 0.974 | 1.199 |
| | 6h | 1.107 | **1.085** | 1.094 | 1.091 | 1.228 | 1.213 | 1.675 |
| D ngoài khơi | 1h | **0.498** | 0.511 | 0.528 | 0.527 | 0.522 | 0.512 | 0.538 |
| | 3h | 0.956 | **0.945** | 0.976 | 0.977 | 0.981 | 0.970 | 1.004 |
| | 6h | 1.240 | **1.212** | 1.217 | 1.236 | 1.272 | 1.260 | 1.314 |

Trung bình 4 trạm: Mamba 0.565 / 1.016 / 1.253; LSTM 0.570 / 1.019 / 1.262; Transformer 0.582 / 1.022 / 1.251; RF 0.567 / 1.029 / 1.286.
Skill vs persistence: A–C 12–35%; **D chỉ 2–8% cho mọi mô hình** (RF 7%, Mamba 2–6%).

Diebold–Mariano (Mamba vs X, stat<0 = Mamba tốt hơn; một số ô thiếu vì pilot cũ không lưu dự đoán):
Mamba thắng rõ DLinear, PatchTST ở A–C (|stat| 3.5–17); vs LSTM/Transformer: thường |stat| < 4, nhiều ô không ý nghĩa;
ở D Mamba **thua** LSTM (stat +2.1 đến +4.2) và DLinear ở 1h (+3.0).

Chi phí: best_epoch (epoch tốt nhất trên val) — **Mamba 2–3**, Transformer 4–8, LSTM 6–10, PatchTST 9–18, DLinear 16–37.
Latency CPU batch 1 (median 100 lần, đo bằng bản PyTorch trên CPU, không có kernel): Mamba **10–24 ms**, LSTM ~1.1, Transformer ~1.2, PatchTST 2–15, DLinear 0.3.
Thời gian huấn luyện GPU (sau khi có kernel): Mamba ~180–200 s/lượt, tương đương LSTM/Transformer.

## Câu hỏi cần chốt
1. Chạy E1 (5 seed) ngay với cấu hình hiện tại, hay chỉnh trước? Mamba đạt val tốt nhất ở epoch 2–3 → lr 1e-3 có thể quá cao / overfit sớm; so sánh có công bằng không nếu không mô hình nào được tuning?
2. Nếu tuning: giao thức gì để công bằng và vừa ngân sách (lưới nhỏ trên val, cùng ngân sách cho mọi mô hình)?
3. Latency: đo thế nào để luận điểm "hiệu quả" của bài trung thực (CPU bản PyTorch, GPU có kernel, hay cả hai)?
4. PatchTST thiếu RevIN — thêm hay giữ?
5. Trạm D: mọi mô hình gần như không vượt persistence. Cách trình bày và giải thích?
6. Mô hình nào đưa vào LOSO (E3) và SHAP (E4)?
7. Khung câu chuyện của bài: "Mamba thắng" có còn đứng được không? Nếu chênh lệch nhỏ/không ý nghĩa, nên định vị bài thế nào?
