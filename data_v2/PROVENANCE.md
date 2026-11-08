# Nguồn gốc dữ liệu — `data_v2/`

Tài liệu này là căn cứ để viết §2.2–2.3 và mục Data Availability của bản thảo.
Mô tả sai nguồn gốc là lỗi nghiêm trọng hơn kết quả kém, nên phần này cần được
chép gần như nguyên văn vào bài.

## Nguồn

**NREL Southeast Asia Wind Toolkit v3**, truy cập qua Wind Toolkit Data Download API
(`developer.nlr.gov`, endpoint `wtk-seasiawind-v3-download`), tải ngày 2026-09-11.

Chuỗi sản xuất dữ liệu:

```
WRF (Weather Research and Forecasting), 9 km / 60 phút
        │
        ▼  sup3r — GAN siêu phân giải, ×3 không gian, ×4 thời gian
   3 km / 15 phút, 2007–2021
```

**Điều bắt buộc phải nêu trong bài:** đây là dữ liệu *mô hình hoá*, không phải đo
đạc. Độ phân giải vật lý gốc là 9 km / 60 phút; các điểm 15 phút và lưới 3 km do
mạng sinh đối kháng (GAN) sinh ra. Không được mô tả là SCADA, met mast, hay quan
trắc. Bản thảo hiện ghi "localized SCADA measurements" (§2.2) và nguồn
"SCADA / Met Mast" (Table 3) — cả hai đều sai và phải sửa.

Tham chiếu: <https://docs.nrel.gov/docs/fy23osti/85481.pdf>

## Trạm

| Trạm | Chế độ | Toạ độ yêu cầu | Ô lưới thực nhận | Mean (m/s) | Std |
|---|---|---|---|---|---|
| A | Inland | 21.00 N, 105.80 E | 20.9954, 105.7896 | 4.497 | 2.152 |
| B | Coastal | 11.72 N, 109.11 E | 11.7217, 109.1090 | 7.277 | 3.296 |
| C | Complex Terrain | 14.00 N, 108.00 E | 14.0017, 108.0117 | 5.557 | 2.482 |
| D | Offshore | 10.50 N, 109.30 E | 10.4920, 109.3011 | 8.051 | 3.753 |

Toạ độ trạm B khác bản thảo gốc (11.6 N, 108.9 E). Điểm cũ nằm sâu trong đất liền
khoảng 25 km và chỉ cho mean 4.43 m/s, không xứng nhãn "Coastal". Ô lưới ERA5 rộng
~31 km của tập dữ liệu cũ trộn gió biển vào đất liền nên che mất sai sót này; ở lưới
3 km thì lộ ra. Điểm mới nằm trên vành đai điện gió Ninh Thuận thực.

## Phạm vi

- Giai đoạn: 2017-01-01 → 2021-12-31 (5 năm, đã gồm ngày nhuận)
- Bước thời gian: 15 phút, **0 gap**, **0 NaN**
- 175,200 mẫu/trạm sau khi cắt phần đầu thiếu lag 24h → tổng 700,800 mẫu
- Múi giờ: giờ địa phương (`utc=false`), để đặc trưng chu kỳ ngày khớp giờ mặt trời VN
- Độ cao hub: 100 m

## Biến

18 biến tải về: `windspeed_` tại 10/40/80/100/120/160/200 m; `winddirection_` tại
10/80/100/120 m; `temperature_` tại 10/80/100/120 m; `pressure_` tại 0/100/200 m.

30 đặc trưng dẫn xuất — xem [`scripts/03_build_dataset.py`](../scripts/03_build_dataset.py).
Đáng chú ý:

- `air_density` = p₁₀₀ / (R·T₁₀₀), R = 287.05 J·kg⁻¹·K⁻¹
- `shear_alpha` = ln(v₁₂₀/v₈₀) / ln(120/80), kẹp về [−0.5, 1.5]
- `veer_120_80` = chênh hướng gió giữa 120 m và 80 m, bọc về [−180°, 180°]
- `dT_10_100` = T₁₀ − T₁₀₀, proxy độ ổn định khí quyển
- Lag và rolling **chỉ nhìn về quá khứ**; rolling không căn giữa

Nhãn y(t+h) **không** nằm trong file — do code huấn luyện tự sinh bằng sliding window.

## Kiểm định

Chạy [`scripts/02_verify_raw.py`](../scripts/02_verify_raw.py). Cả 4 trạm đều đạt:

1. **Residual nội suy theo phase** — cả 4 phase (`:00 :15 :30 :45`) đều có residual
   xấp xỉ nhau (0.051–0.087). Không phase nào bằng 0, tức không có nội suy tuyến tính.
2. **Rò rỉ nhãn** — quy tắc ngoại suy tuyến tính 2 điểm không cho RMSE = 0 ở bất kỳ
   phase nào.
3. **Baseline persistence** — mức sàn mô hình phải vượt.

Phép thử (1) chính là thứ đã loại bỏ tập dữ liệu cũ trong `data/`, nơi các phase
`:15 :30 :45` cho residual đúng bằng 0.000000: dữ liệu 15 phút được nội suy tuyến
tính từ dữ liệu giờ, khiến 50% nhãn ở horizon 30 phút trở thành hàm tất định của
input. **Không dùng lại `data/` cho bất kỳ kết quả nào trong bài.**

## Baseline persistence (R², 15% cuối) — mức sàn để so sánh

| Trạm | 1h | 3h | 6h |
|---|---|---|---|
| A Inland | 0.848 | 0.429 | −0.032 |
| B Coastal | 0.963 | 0.871 | 0.784 |
| C Complex Terrain | 0.940 | 0.768 | 0.547 |
| D Offshore | 0.981 | 0.933 | 0.885 |

Ở trạm A horizon 6h, persistence có R² âm — kém hơn cả việc đoán giá trị trung bình.
Mọi mô hình phải được báo cáo kèm bảng này; thiếu nó thì không thể biết R² = 0.9 là
giỏi hay chỉ là quán tính của chuỗi.

## Tái lập

```bash
py scripts/01_download_seawtk.py    # cần NREL_API_KEY và NREL_EMAIL
py scripts/02_verify_raw.py         # cổng kiểm định — không đạt thì dừng
py scripts/03_build_dataset.py
```
