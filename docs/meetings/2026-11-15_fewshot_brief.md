# Brief cuộc họp #7 — few-shot baseline + RF depth (15/11/2026)

## Kết quả mới
**1. E9 few-shot (Mamba, trạm A–D, cửa sổ DB/TN, 1/2/4 tuần, 3 seed)** — đang chạy, gần xong trạm D.
- Fine-tune từ LOSO-W (lr 1e-4): RMSE 1h ~0.55–0.66, ngang hoặc tốt hơn LOSO-W zero-shot (A 0.849, B 0.633, C 0.543, D 0.550) và persistence (0.845/0.640/0.608/0.538).
- Học từ đầu (scratch, lr tuned, 30 epoch, patience 5, batch 64): RMSE 1h **2.5–3.0** ở mọi trạm/tuần — gần dự đoán hằng số (σ gió ~3 m/s). 1 tuần = 672 mẫu → ~10 batch/epoch → tối đa ~300 bước, warmup 1 epoch.
- Lo ngại: scratch là baseline "rơm" — reviewer sẽ nói lợi ích fine-tune bị thổi phồng do scratch chưa hội tụ.

**2. RF chỉ tốc độ gió + delta (max_depth=16)**, LOSO RMSE 1h A/B/C/D: 0.804/0.636/0.588/0.569 vs RF-W (depth 24) 0.798/0.633/0.581/0.567 → delta không giúp thêm. Nhưng hai bộ khác depth (16 vs 24).

## Câu hỏi cần chốt
1. Baseline scratch cho few-shot: giữ nguyên / chạy lại với ngân sách bước cố định lớn hơn (vd ≥ 2000 bước, patience 20) / thêm baseline mạnh rẻ (RF học trên đúng k tuần, persistence) / kết hợp? Chi phí GPU: scratch ~30 s/lượt hiện tại; 72 lượt scratch.
2. Có cần chạy RF-W ở depth 16 (CPU ~20 phút) để khử nhiễu so sánh delta không?
3. Vị trí của việc sửa (1) trong hàng đợi GPU đã chốt ở họp #6 (LOSO-W seed 3–4 → E1-W 8 trạm + chéo W → SHAP → PatchTST).
