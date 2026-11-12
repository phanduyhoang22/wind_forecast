# Nhật ký dự án — Dự báo tốc độ gió đa địa điểm bằng Mamba

File này ghi lại những gì đã làm, quyết định đã chốt, kết quả và việc còn mở.
Mục mới thêm ở **đầu** mỗi phần. Kế hoạch tổng thể: [`Ke_hoach_du_an_v2.docx`](Ke_hoach_du_an_v2.docx).

---

## 1. Tóm tắt dự án

- **Bài toán:** dự báo tốc độ gió ở độ cao 100 m, horizon **1h / 3h / 6h**, cửa sổ nhìn lại 24 giờ (96 bước × 15 phút).
- **Mô hình:** Mamba (S6, mô hình chính) so với RF, LSTM, Transformer, PatchTST, DLinear; mốc sàn là persistence và climatology.
- **Dữ liệu:** NREL SEA Wind Toolkit v3 (WRF 9 km/60 phút → GAN sup3r 3 km/15 phút), 4 trạm, 2017–2021, 175.200 mẫu/trạm, 31 đặc trưng. Là dữ liệu **mô hình hoá**, không phải đo đạc — xem [`data_v2/PROVENANCE.md`](../data_v2/PROVENANCE.md).

| Trạm | Chế độ | Toạ độ | Mean (m/s) |
|---|---|---|---|
| A | Đất liền | 21.00 N, 105.79 E | 4.50 |
| B | Ven biển | 11.72 N, 109.11 E | 7.28 |
| C | Đồi núi | 14.00 N, 108.01 E | 5.56 |
| D | Ngoài khơi | 10.49 N, 109.30 E | 8.05 |

- **Đóng góp dự kiến:** benchmark công bằng đa chế độ gió; SHAP với đặc trưng vật lý nhiều độ cao (shear, veer, ổn định); LOSO; skill score + kiểm định Diebold–Mariano; khoảng dự báo conformal.

---

## 2. Quyết định đã chốt

| Ngày | Quyết định | Lý do |
|---|---|---|
| 08/11/2026 | Dùng kernel CUDA chính thức `mamba-ssm` (selective_scan) cho Mamba trên GPU — **đã chạy** | Đề tài lấy Mamba làm trọng tâm; kernel gốc của Gu & Dao vừa nhanh vừa đứng vững trước reviewer. Không có wheel cho torch 2.14/CUDA 13 → tự build `csrc/selective_scan` chỉ cho T4 (sm_75), C++20, 24 phút. Khớp bản tham chiếu: forward 2,7e-7, gradient 7e-7. Tốc độ: **18 ms/batch** (PyTorch+compile 168, PyTorch thuần 630, LSTM 14). File `.so` lưu ở `Drive/WIND_FORECAST_DATA/kernels/` |
| 08/11/2026 | `torch.compile` cho selective scan khi chạy GPU (bản PyTorch) | Nhanh ~3,5× (295 → 85 s/epoch), lệch so với bản gốc 6e-8 |
| 08/11/2026 | RF chạy trên máy (CPU), các mô hình mạng nơ-ron chạy trên Colab (GPU T4) | RF không cần GPU; ~40 s/lượt trên i5-13500H |
| 08/11/2026 | Thêm baseline PatchTST và DLinear | Bài S-Mamba (Neurocomputing 2025) và ECTO (arXiv 2026) dùng chúng; DLinear có thể thua persistence → cần có trong bảng |
| 08/11/2026 | Push code + `data_v2/*.npz` lên GitHub public; Colab clone repo rồi chép lên Drive | Không có Google Drive Desktop; công cụ Drive không tải nổi 44 MB nhị phân. Người dùng đồng ý; commit không ghi Claude |
| 08/11/2026 | Không đẩy CSV 52 MB/trạm, bản thảo `.md`, `.mcp.json` | CSV trùng nội dung `.npz`; bản thảo chưa công bố |
| 08/11/2026 | Horizon 1h / 3h / 6h (thay 30/60/120 phút của bản thảo cũ) | Theo hợp đồng dữ liệu v2; bản thảo phải viết lại |
| 08/11/2026 | LOSO và global pooled **không** dùng site ID | Khoảng cách LOSO − global là chi phí chuyển giao thuần |
| trước 08/11 | Bỏ hoàn toàn dữ liệu `data/` cũ | Nội suy tuyến tính từ dữ liệu giờ → 50% nhãn 30 phút là hàm tất định của input |

---

## 3. Nhật ký công việc

### 08/11/2026

**Thiết lập**
- Cài MCP Colab vào dự án (chép `.mcp.json` từ dự án solar).
- Đọc toàn bộ code, tài liệu, bản thảo; phát hiện bản thảo ghi sai nguồn dữ liệu (SCADA/ERA5), sai số đặc trưng (22 → 31), Table 2 "12 sub-regime" không có dữ liệu.

**Tổng quan tài liệu**
- Tìm 23 bài 2024–2026 (nhiều nhóm Trung Quốc), đối chiếu thư mục qua Crossref: 19/23 xác minh được.
- Khoảng trống chính: chưa bài nào kết hợp Mamba + đa chế độ gió + SHAP (bài Graph-Mamba-Transformer, Appl. Sci. 2026, tự nêu cần kiểm chứng đa địa điểm).
- Sửa sai: DA-SSSM là 2026 (không phải 2025); bài transfer learning 70 trạm dùng ELM/AR, không phải học sâu; MoE-Mamba không phải nhóm Trung Quốc. Một bài 太阳能学报 không xác minh được → không trích dẫn.
- Kết quả: [`Ke_hoach_du_an_v2.docx`](Ke_hoach_du_an_v2.docx) (bản 1.1).

**Code** (tất cả trong `scripts/`, đã push)
- `06_models.py`: thêm DLinear, PatchTST. Số tham số: LSTM 60K, Transformer 71K, Mamba 70K, PatchTST 71K, DLinear 614.
- `07_run_benchmark.py`: lưu dự đoán test (`results/preds/`), trọng số và dự đoán val (`results/models/`); compile Mamba trên GPU.
- `08_aggregate.py`: bảng mean ± std, skill score, chi phí, Diebold–Mariano (HLN). Self-test đạt.
- `09_global_loso.py`: global pooled + LOSO. Kiểm tra: đảo chuẩn hoá đúng (sai số 2e-6), không cửa sổ nào vắt qua hai trạm.
- `10_shap.py`: GradientExplainer, xếp hạng đặc trưng, tỷ trọng theo nhóm vật lý, hồ sơ theo độ trễ.
- `11_conformal.py`: split conformal, PICP/PINAW theo tercile tốc độ gió. Self-test PICP 0,891 (mục tiêu 0,90).
- Notebook Colab: sửa lỗi chuỗi `print('` xuống dòng (SyntaxError).

**Sự cố**
- Lần chạy RF đầu chết: PowerShell `*>` làm hết bộ nhớ → chạy qua Bash.
- RF hết RAM ở lượt 16/20 → chạy tiếp, script tự bỏ qua lượt đã xong.
- Mamba bản PyTorch thuần chậm (295 s/epoch, gấp ~30× LSTM) → compile, rồi build kernel `mamba-ssm`.
- Build `mamba-ssm` lỗi 2 lần: thiếu `ninja`; header torch 2.14 cần C++20 (mamba-ssm dùng C++17). Lần 3 thành công.
- Pilot khởi động lại 2 lần (thêm compile, rồi thêm kernel); các lượt đã xong được giữ nguyên nhờ cơ chế bỏ qua.

**Cách dùng kernel ở phiên Colab mới:** chép `Drive/WIND_FORECAST_DATA/kernels/selective_scan_cuda_sm75_torch2.14.1.so` thành `/content/ss_build/selective_scan_cuda.so`, chạy script với `PYTHONPATH=/content/ss_build`. Nếu Colab đổi phiên bản torch thì phải build lại (ô build trong notebook).

---

## 4. Kết quả

### RF — 4 trạm × 5 seed (CPU) — xong 08/11/2026

RMSE (m/s), trung bình 5 seed; độ lệch giữa seed < 0,001.

| Trạm | 1h | 3h | 6h | Persistence 1h / 3h / 6h |
|---|---|---|---|---|
| A | 0.706 | 1.284 | 1.592 | 0.845 / 1.634 / 2.197 |
| B | 0.560 | 0.975 | 1.205 | 0.640 / 1.191 / 1.538 |
| C | 0.504 | 0.899 | 1.107 | 0.608 / 1.199 / 1.675 |
| D | 0.498 | 0.956 | 1.240 | 0.538 / 1.004 / 1.314 |

Skill so với persistence: A 16–28%, B 13–22%, C 17–34%, **D chỉ 5–7%** (ngoài khơi, persistence rất mạnh).

### Pilot mạng nơ-ron — 1 seed (GPU) — đang chạy

| Trạm | Mô hình | 1h | 3h | 6h |
|---|---|---|---|---|
| A | LSTM | 0.720 | 1.261 | 1.515 |
| A | Transformer | 0.713 | 1.241 | 1.511 |

(Pilot chạy bằng code cũ: không có file dự đoán → không dùng cho DM/SHAP/conformal.)

---

### Tuning (`12_tune.py`) — xong 09/11/2026

Trạm A + D, 1 seed, chọn theo val MSE (thang chuẩn hoá) trung bình 2 trạm. Cấu hình chốt → `results/tuned.json`:

| Mô hình | Cấu hình chốt | val A | val D | Epoch tốt nhất |
|---|---|---|---|---|
| Transformer | lr 3e-4, dropout 0.2 | **0.003837** | **0.001905** | 18 / 20 |
| Mamba | lr 3e-4, dropout 0.1 | 0.003869 | 0.001916 | 10 / 7 |
| LSTM | lr 1e-3, dropout 0.2 | 0.004188 | 0.002009 | 9 / 7 |
| RF | max_depth 24 | 0.004297 | 0.002046 | — |
| PatchTST | lr 3e-4, dropout 0.1, không RevIN | 0.004507 | 0.002079 | 29 / 24 |
| DLinear | lr 1e-3 | 0.005207 | 0.002088 | 16 / 17 |

- Sau khi sửa weight decay + warmup, Mamba hết dừng sớm (epoch 2–3 → 7–10); lr 3e-4 tốt hơn 1e-3 ở Mamba, Transformer.
- Transformer và Mamba gần như ngang nhau trên val (lệch < 1%).
- RevIN làm PatchTST **kém hơn** ở cả 2 trạm (A 0.00495 vs 0.00451) — dữ liệu đã MinMax theo train, chuẩn hoá theo cửa sổ làm mất mức tuyệt đối của gió.
- **Lệch khỏi lưới định trước:** PatchTST chỉ tune lr × RevIN, giữ dropout 0,1 (19 phút/lượt; ở 3 mô hình kia dropout đổi val < 1%). Phải ghi trong phần phương pháp.

### E1 — đang chạy
- RF 4 trạm × 5 seed (CPU, max_depth 24) — **xong**, `results/runs_rf.csv`. Bản chưa tune đổi tên `runs_rf_untuned.csv`.
- Lượt 1 (GPU): Mamba, Transformer, LSTM, DLinear × 4 trạm × 5 seed → `results/runs.csv`.
- Lượt 2 (GPU): PatchTST (~5,5 h) chạy sau cùng.
- Giữ runtime Colab: chạy ô tiến độ mỗi 15 phút (runtime từng bị ngắt khi để yên).

## 5. Cuộc họp agents

*Sau mỗi kết quả hoặc mỗi giai đoạn, các agent (phương pháp/thống kê, chuyên gia năng lượng gió, kỹ sư ML/tính toán) cùng xem kết quả và chốt bước tiếp. Biên bản ghi ở đây.*

### Họp #1 — 09/11/2026, sau pilot

**Đầu vào:** [`meetings/2026-11-09_pilot_brief.md`](meetings/2026-11-09_pilot_brief.md). Thành viên: phương pháp & thống kê, khí tượng & năng lượng gió, kỹ sư ML.

**Nhận định chung (cả 3 đồng thuận)**
- "Mamba thắng" không đứng được: chênh với LSTM/Transformer 0,003–0,009 m/s, DM thường không ý nghĩa, Mamba thua ở D.
- Best epoch 2–3 của Mamba là dấu hiệu cấu hình huấn luyện chưa đúng, không phải "hội tụ nhanh".
- Trạm D là **kết quả** (giới hạn khả năng dự báo theo chế độ), không phải thất bại.
- Latency CPU không phải luận điểm mạnh: dự báo phát lại mỗi 15 phút, mọi mô hình đều thừa sức chạy thời gian thực.

**Lỗi phát hiện trong code**
- Weight decay áp lên `dt_proj.bias` của Mamba (bản gốc miễn) và lên mọi bias/LayerNorm → kéo dt ra khỏi dải khởi tạo. *(Kỹ sư ML)*
- Không có warmup; không lưu đường cong train/val. *(Kỹ sư ML)*
- DM dùng lag HAC h−1, quá ngắn cho chuỗi 15 phút → |stat| phóng đại; không hiệu chỉnh đa phép so. *(Thống kê)*
- `latency_ms` của RF là thông lượng/mẫu với `n_jobs=-1`, không so được với batch 1 của mạng nơ-ron. *(Kỹ sư ML)*
- PatchTST không RevIN → đối thủ "rơm". *(cả 3)*

**Chốt**
1. Sửa code (không tốn GPU): decay chỉ trên ma trận trọng số; warmup 1 epoch; lưu đường cong; RevIN tuỳ chọn cho PatchTST; DM với HAC lag max(h−1, 96) + Holm. — **xong**, commit `ef77872`.
2. Tuning cố định trước, cùng ngân sách: lr {3e-4, 1e-3} × dropout {0,1, 0,2}; PatchTST thêm RevIN {có, không}; DLinear chỉ lr; RF max_depth {12, 16, 24}. Trạm A + D, 1 seed, chọn theo val, áp chung 4 trạm. — **đang chạy** (`12_tune.py`).
3. Kiểm tra RMSE theo phút (GAN vs WRF gốc). — **xong**, xem kết quả dưới.
4. E1: 6 mô hình × 4 trạm × 5 seed với cấu hình chốt (~9 h GPU, 2 phiên).
5. Sau E1: phân tích theo chế độ (gió mùa ĐB/TN, ngày/đêm, ramp, mùa bão 9–11), không train lại.
6. E3 LOSO: Mamba, LSTM (+ RF nếu viết thêm, + persistence). E4 SHAP: Mamba + RF (TreeSHAP đối chiếu); `air_density` làm đối chứng âm.
7. Đo latency bằng script riêng: CPU/GPU × batch 1/1024, số luồng cố định; thêm chế độ hồi quy từng bước của Mamba.
8. Khung bài: "benchmark nghiêm ngặt + khả năng dự báo phụ thuộc chế độ gió–địa hình; SSM ngang mô hình tốt nhất"; đóng góp chính là khung đánh giá (purge, DM+Holm, LOSO, conformal, SHAP vật lý).

**Kết quả kiểm tra theo phút** (`13_phase_check.py`, RF + persistence): tỷ số RMSE điểm GAN (:15/:30/:45) / điểm WRF gốc (:00) = **0,97–1,01** ở mọi trạm × horizon. Sai số không dồn vào điểm GAN sinh; đánh giá chỉ trên điểm :00 cho cùng kết luận → lo ngại "dự báo kết cấu GAN" bị loại trừ.

### Họp #2 — 10/11/2026, sau E1 lượt 1 ([brief](meetings/2026-11-10_e1_brief.md))

**Kết quả E1** (5 seed, trung bình 4 trạm, RMSE 1h/3h/6h): Mamba 0.560/1.005/1.243; Transformer 0.564/1.001/1.238; RF 0.562/1.025/1.283; LSTM 0.577/1.032/1.271; DLinear 0.613/1.098/1.369. Ensemble 5 seed: Mamba 0.537/0.981/1.213 (tốt nhất mọi horizon), RF không đổi.
Tập test xác nhận 03/04–31/12/2021 (thiếu lõi gió mùa ĐB tháng 1–3).

**Chốt:** (1) DM theo từng seed (k/5, Holm) + t ghép là bảng chính; ensemble ×5 là phương pháp riêng, ghi chi phí; (2) Mamba ≈ Transformer, không viết "outperforms"; (3) biến thiên seed là điểm yếu với mô hình đơn — báo min/max; (4) không retune LSTM C (lưới đã khoá; đường cong val bình thường); (5) phân tích theo chế độ, latency riêng, sửa `09`/`10`, LOSO; (6) hạn chế: dữ liệu WRF, test thiếu tháng 1–3, không có NWP. Đã kiểm: E1 chạy đúng cấu hình tuned (log "Cau hinh").

**Latency** (`15_latency.py`, CPU 1 luồng, batch 1, ms): DLinear 0.43; **Mamba-step 1.62** (hồi quy, khớp forward 9e-8); LSTM 2.44; Transformer 2.91; PatchTST 5.68; Mamba full-window 22.4; RF 34.9.

### Họp #3 — 13/11/2026, sau LOSO ([brief](meetings/2026-11-13_loso_brief.md))

**Kết quả:** global (gộp 4 trạm) ≈ local, tốt hơn ở C (0.474 vs 0.496). LOSO zero-shot không vượt persistence: skill trung bình 1h Mamba −1.8%, RF −6.0%, Transformer −11.0%; 6h +0.9 / −2.6 / +3.4%. Transformer sụp ở B (0.847 vs persistence 0.640).
**Phân rã sai số** (`loso_bias.csv`): Transformer B lệch mức −0.59 m/s = 47% MSE, độ lệch chuẩn sai số bằng Mamba (0.602 vs 0.604) → sụp do **lệch mức**, không phải kiến trúc. C: cả hai lệch +0.23–0.28 m/s.

**Chốt:** (1) LOSO là phát hiện: trạm mới cần dữ liệu tại chỗ; ghi rõ đã dùng thống kê không nhãn của trạm đích (thích nghi không giám sát, không phải zero-shot thuần); (2) Mamba ổn định hơn khi chuyển giao chỉ là "quan sát" (3 seed, p tối thiểu 0.1); (3) delta target y(t+h)−v(t) — RF trên CPU trước, Mamba nếu có tác dụng; (4) few-shot 1/2/4 tuần từ train trạm đích + baseline học từ đầu cùng lượng dữ liệu, ≥2 cửa sổ mùa; (5) SHAP Mamba + RF; (6) giả thuyết "áp suất/mật độ = site ID ngầm" cần ablation.
**Khung bài:** dữ liệu & kiểm định → benchmark local (Mamba ≈ Transformer, ensemble Mamba tốt nhất) → hiệu quả (Mamba-step) → khả năng dự báo theo chế độ → SHAP → chuyển giao (zero-shot thất bại, few-shot/delta) → hạn chế.

**Để sau:** DM theo từng seed + Friedman/CD diagram; ACF/phổ trạm D vs A–C; kiểm tra lịch tái khởi tạo WRF; SHAP LSTM cần tắt cuDNN; `09` chưa lưu trọng số/val; DataLoader `num_workers=0`.

---

## 6. Việc còn mở

- [x] Build `mamba-ssm` selective_scan cho T4, kiểm tra khớp, tích hợp vào `06_models.py`
- [ ] Pilot xong → họp agents → chốt chạy đủ 5 seed
- [x] Sửa ô đồng bộ Drive để chép cả `results/preds/` và `results/models/`
- [ ] Đưa bước nạp kernel vào `notebooks/benchmark_colab.ipynb`
- [ ] Chạy đủ 5 seed (E1), rồi `08` (bảng + DM)
- [ ] LOSO (E3), SHAP (E4–E5), conformal (E6)
- [ ] Viết lại bản thảo: nguồn dữ liệu, horizon, Table 1–8
- [ ] Kiểm tra toàn văn: #7 STS-MambaGPT và #14 có dùng SHAP/shear không; #22 có phải Việt Nam không
- [ ] Cân nhắc xoá `References/*.pdf` khỏi repo public (bản quyền)
- [ ] PatchTST chưa có RevIN — thêm nếu kết quả kém bất thường
