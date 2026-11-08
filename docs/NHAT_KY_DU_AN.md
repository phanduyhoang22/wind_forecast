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
| 08/11/2026 | Dùng kernel CUDA chính thức `mamba-ssm` (selective_scan) cho Mamba trên GPU | Đề tài lấy Mamba làm trọng tâm; kernel gốc của Gu & Dao vừa nhanh vừa đứng vững trước reviewer. Không có wheel sẵn cho torch 2.14/CUDA 13 → tự build chỉ cho T4 (sm_75) |
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

## 5. Cuộc họp agents

*Sau mỗi kết quả hoặc mỗi giai đoạn, các agent (phương pháp/thống kê, chuyên gia năng lượng gió, kỹ sư ML/tính toán) cùng xem kết quả và chốt bước tiếp. Biên bản ghi ở đây.*

(Chưa có — cuộc họp đầu tiên sau khi pilot xong.)

---

## 6. Việc còn mở

- [ ] Build xong `mamba-ssm` selective_scan cho T4, kiểm tra khớp bản PyTorch, tích hợp vào `06_models.py`
- [ ] Pilot xong → họp agents → chốt chạy đủ 5 seed
- [ ] Sửa ô đồng bộ Drive để chép cả `results/preds/` và `results/models/`
- [ ] Chạy đủ 5 seed (E1), rồi `08` (bảng + DM)
- [ ] LOSO (E3), SHAP (E4–E5), conformal (E6)
- [ ] Viết lại bản thảo: nguồn dữ liệu, horizon, Table 1–8
- [ ] Kiểm tra toàn văn: #7 STS-MambaGPT và #14 có dùng SHAP/shear không; #22 có phải Việt Nam không
- [ ] Cân nhắc xoá `References/*.pdf` khỏi repo public (bản quyền)
- [ ] PatchTST chưa có RevIN — thêm nếu kết quả kém bất thường
