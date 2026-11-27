# NHATKY

## 2026-11-27 23:40 — leader — T21 chạy phase B, T23 chờ qa
- Làm được: contract T23 khoá trước (`aaa048b`); qa T21 phase A PASS, merge `2ef6c47`; Mamba T21 xong trên Colab 24/24, S0 khớp R21 (R35, Drive `results/t21/`); RF T21 đang chạy local; T23: references.csv xong (R33), LightGBM chọn `--lag-step 4` theo thời gian (R34).
- Quyết định: làm rõ T21 (Δskill val nguồn, trigger RevIN chỉ Mamba, mốc RF = R16); T23 thống kê theo quy ước 22, một config cho mọi horizon, bỏ DM từng seed cho LightGBM.
- Dở dang / bước tiếp: ghép CSV Mamba từ Drive + RF, `--stats`, qa phase B T21; chạy lại qa T23 phase A rồi LightGBM (không song song với RF).
- Mở chat tiếp: /role leader T21

## 2026-11-27 20:00 — leader — handoff: M19 + M20 chốt, tiếp theo T21 ‖ T23
- Làm được: shift check 64 PASS/0 FAIL; kiểm Drive (24 `losoW8_*.pt`, runs.csv khớp, không npz SHAP mới); họp M19 và M20 (reviewer ngoài + đọc 22 bài); ROADMAP thêm stage S3b (`eddaecd`).
- Quyết định: M20 = phương án B "gói độ tin cậy" (T21, T23–T27), T22 xuống P3; viết bài song song, điểm chính là W vs 31 đặc trưng.
- Dở dang / bước tiếp: viết contract đầy đủ T23, nối Colab, chạy T21 ‖ T23; chưa kiểm dữ liệu 2007–2015.
- Mở chat tiếp: /role leader T21

## 2026-11-27 19:30 — leader — họp M20 đầy đủ (reviewer ngoài + tài liệu)
- Làm được: kiểm Drive (24 checkpoint `losoW8_*`, runs.csv 85118 B khớp repo, không npz SHAP mới); họp M20 với qa, worker, reviewer ngoài, agent đọc tài liệu (22 bài, mức abstract/snippet).
- Quyết định: phương án B "gói độ tin cậy" (cả 4 đồng ý có sửa): T21 + T23 baseline (smart persistence, blend, LightGBM) + T24 foundation model zero-shot + T25 năm 2007–2015 làm test khoá trước + T26 kiểm soát/công suất + T27 thăm dò; T22 xuống P3.
- Dở dang / bước tiếp: viết contract đầy đủ, giao T21 ‖ T23 cho 2 worker.
- Mở chat tiếp: /role leader T21

## 2026-11-27 18:40 — leader — họp M19: backlog cải thiện
- Làm được: họp M19 (qa + worker chỉ đọc); qa xác nhận L09 qua code (scaler MinMax của site đích fit trên train của chính nó → "zero-shot" cần ghi rõ).
- Quyết định: phương án B (theo ủy quyền User): T21 đánh giá lại LOSO-8 với scaler không dùng dữ liệu đích; T22 Ridge/RF có lag cho few-shot; hoãn L11/L06; L13 chỉ kiểm tra.
- Dở dang / bước tiếp: xác nhận checkpoint `losoW8_*` trên Drive, giao T21 + T22 cho worker; sau đó Discussion.
- Mở chat tiếp: /role leader T21

## 2026-11-27 18:00 — leader — handoff: T06 + T08 DONE, tiếp theo họp cải thiện
- Làm được: T06 DONE (qa vòng 2 tính lại DM/regime NN khớp, `8e2fc16`); T08 DONE (Results E1, merge `265ba61`, `939d210`); Colab reset → mount lại Drive, T4 rảnh.
- Quyết định: không cần họp về câu chữ RF 3h/6h (qa: khớp M18).
- Dở dang / bước tiếp: bật keep-alive; `/meeting` chọn hạng mục cải thiện trước Discussion; căn §2.5.4, đánh lại số 3.x; xoá Drive `tmp_t06/`.
- Mở chat tiếp: /role leader

## 2026-11-27 17:55 — leader — T08 DONE (Results E1)
- Làm được: `docs/paper/section3_results.md` (3.1–3.6: độ chính xác, DM theo seed, regime, conformal, độ trễ CPU, sai lệch công khai); qa vòng 1 FAIL (2 câu sai số §3.3), vòng 2 PASS; merge `265ba61`.
- Quyết định: Director APPROVE theo ủy quyền; câu chữ RF 3h/6h giữ nguyên (qa: khớp M18, trung thực), không cần họp.
- Dở dang / bước tiếp: `/meeting` chọn hạng mục cải thiện (`docs/limitations_and_improvements.md` §2) trước khi viết Discussion; căn chỉnh §2.5.4; đánh lại số mục 3.x; xoá Drive `tmp_t06/`, worktree cũ `agent-af25ad602b8f31bd8`.
- Mở chat tiếp: /role leader

## 2026-11-27 17:35 — leader — T06 DONE
- Làm được: Colab reset → mount lại Drive, kiểm runs.csv 600 dòng + giờ shap đúng; tải 200 preds NN (md5 8/8 khớp); qa vòng 2 tự tính lại DM/Holm/regime: 600/600, 120/120, 1176/1176 khớp → PASS; R31c.
- Quyết định: Director APPROVE theo ủy quyền User 2026-11-25; T06 DONE. Phát hiện mới QA-T06-07 (ramp nhạy với giá trị trùng ở q95, skill lệch < 1e-3) → ghi vào hạn chế.
- Dở dang / bước tiếp: T08 (viết mục E1 theo M18). Xoá thư mục tạm Drive `tmp_t06/` khi tiện. Keep-alive đang chạy (chết theo chat).
- Mở chat tiếp: /role leader T08

## 2026-11-27 17:25 — leader — handoff: T06 vòng 2 chờ tính lại DM NN
- Làm được: T07 DONE (`f799e33`, 1440 dòng); F-T05-01 đóng (`917953a`); T06 QA_PASSED (`2f2d0ae`, `58a2648`); M18 chốt A + B(1) (`d7b1d1d`).
- Quyết định: claim E1 "không khác biệt có ý nghĩa" Mamba/Transformer/RF; DM theo seed là chính.
- Dở dang / bước tiếp: tải 200 preds NN từ Drive về scratch, qa tự tính lại DM + regime NN, Director APPROVE T06; rồi T08. Bật lại keep-alive Colab.
- Mở chat tiếp: /role leader T06

## 2026-11-27 17:20 — leader — F-T05-01 đóng, T06 QA_PASSED, M18 chốt
- Làm được: F-T05-01 đóng (`917953a`, qa PASS, SHAP R27 dùng được); T06 chạy Colab, R31 (`2f2d0ae`), qa vòng 2 PASS sau sửa đường dẫn (`58a2648`); họp M18 (`eef7308`).
- Quyết định: M18 = A + B(1) (User giao cho họp quyết): claim "không khác biệt có ý nghĩa" Mamba/Transformer/RF, DM theo seed là chính, chi phí CPU từ `latency.csv`.
- Dở dang / bước tiếp: T06 vòng 2 — tải 200 preds NN từ Drive về scratch, qa tự tính lại DM + regime NN; rồi Director APPROVE T06; sau đó T08.
- Mở chat tiếp: /role leader T06

## 2026-11-27 16:55 — leader — T07 DONE
- Làm được: chạy tiếp RF C, D (job nền chết theo chat cũ); 20/20 dự đoán test trùng bit với bản cũ; `621aad9` thêm 20 val npz; qa vòng 2 PASS; merge `dc6587b`; Colab chạy lại conformal: 1440 dòng (R30, R29c sửa R29).
- Quyết định: Director APPROVE theo ủy quyền User 2026-11-25; T07 DONE.
- Dở dang / bước tiếp: đóng F-T05-01 (diff toàn bộ CSV); T06. T08 không được nói "đạt độ phủ danh nghĩa" (QA-T07-04), phải ghi PINAW chia theo biên độ train.
- Mở chat tiếp: /role leader T06

## 2026-11-27 01:25 — leader — handoff: T07 vòng 2 worker đang chạy
- Làm được: T05 DONE (`7b6531b`); F-T05-01 completeness khớp R27; M17 chốt A; worker commit `b0a73d1` (sửa 11_conformal.py) và đang chạy RF A–D (A xong, B dở).
- Quyết định: handoff sớm vì hết token; Colab giữ nguyên.
- Dở dang / bước tiếp: kiểm scratch t07, chạy nốt RF site thiếu, so 20/20 dự đoán test, chép val npz, qa, merge, chạy lại 11 trên Colab.
- Mở chat tiếp: /role leader T07

## 2026-11-27 — leader — M17: T07 chọn phương án A
- Làm được: họp M17 (qa: bằng chứng WEAK chỉ ở RF A–D; worker: A khả thi, ~15–20 phút CPU); biên bản `tasks/MEETINGS.md`, commit `398d00f`.
- Quyết định: User chọn A (chạy lại RF A–D có cổng kiểm tái lập seed 0; sửa lượng tử, PINAW theo biên độ train, báo cặp thiếu).
- Dở dang / bước tiếp: worker T07 vòng 2 đang chạy (worktree); sau đó qa, rồi Leader chạy lại 11 trên Colab (1440 dòng).
- Mở chat tiếp: /role leader T07

## 2026-11-27 — director — duyệt T05
- Làm được: T05 APPROVE (qa PASS `5fc2cc9`, runs.csv 600 dòng, 40/40 PatchTST).
- Quyết định: check (3) SHAP npz tách sang F-T05-01 (còn mở, chặn dùng số SHAP ở T08). Paper phải nêu QA-T05-02 (12/120 dòng chạm trần 50 epoch) và QA-T05-03 (PatchTST thua persistence 1h ở D, H).
- Dở dang / bước tiếp: Leader set T05 DONE; đọc kết quả shapchk F-T05-01; T07 chọn (a)/(b); T06.
- Mở chat tiếp: /role leader T07

## 2026-11-27 01:15 — leader — handoff: T05 qa PASS, T07 qa FAIL, Colab vẫn chạy
- Làm được: T05 40/40 xong, `runs.csv` 600 dòng (`5fc2cc9`), qa PASS (`6633991`). T07 conformal chạy trên Colab, `conformal.csv` 1320 dòng, R29 (`549bfec`); qa FAIL tiêu chí số dòng (RF thiếu val A–D) (`d0e12ad`).
- Phát hiện F-T05-01: SHAP npz A–D bị tính lại ngày 26/11; đang chạy `25_shap_check.py` trên Colab để so.
- Quyết định: User giữ Colab chạy, keep-alive `e23b42ee` ở chat này; User qua chat director duyệt T05.
- Dở dang / bước tiếp: đọc kết quả shapchk; User chọn T07 (a)/(b); T06 sau khi T05 DONE.
- Mở chat tiếp: /role director T05 (rồi /role leader T07)

## 2026-11-27 — leader — T05 tạm dừng Colab
- Làm được: shift check 65 PASS / 0 FAIL / 2 NOT_VERIFIED; Drive run.log dừng ở 17:08Z 26/11 (runtime coi như mất, T05 38/40, thiếu H seed 3–4).
- Quyết định: User "ngừng colab" -> không chạy lại setup cell.
- Dở dang / bước tiếp: chạy lại setup cell khi User cho, chuỗi bỏ qua khóa đã xong, chạy tiếp H seed 3–4.
- Mở chat tiếp: /role leader T05

## 2026-11-27 00:18 — leader — handoff: T05 38/40, status cell treo
- Làm được: keep-alive Colab 14 phút suốt buổi; PatchTST 38/40 lúc 17:01 UTC (A–G xong, H seed 0–2 xong).
- Sự cố: status cell ~17:15 UTC treo >120 s; Drive `run.log` sửa lần cuối 17:08 UTC (lúc 17:18 là 9,5 phút) → có thể mất runtime, chưa chắc.
- Dở dang / bước tiếp: kiểm runtime; mất thì nối lại + setup (chuỗi tự bỏ qua run đã xong); 40/40 → qa T05 → T07 → T06 → T08.
- Mở chat tiếp: /role leader T05

## 2026-11-26 19:30 — leader — handoff: T05 23/40, T08c DONE
- Làm được: Colab reset → setup lại 12:10 UTC, PatchTST 23/40 lúc 12:28 UTC (E đang chạy). T08c qa PASS vòng 2, merge `ea1104d`, docs `7c8fee7`, đã push. Shift check đầu ca 65 PASS, 0 FAIL.
- Quyết định: chat này vẫn mở để giữ Colab (cron 14 phút, theo yêu cầu User).
- Dở dang / bước tiếp: T05 tới 40/40 → qa T05 (3 kiểm tra Drive) → T07 → T06 → T08.
- Mở chat tiếp: /role leader T05

## 2026-11-26 19:40 — leader — T08c DONE, Colab chạy lại T05
- Làm được: Colab reset → setup lại 12:10 UTC (`e7c17b2`), PatchTST 23/40 lúc 12:15 UTC; keep-alive cron 14 phút trong chat này. T08c (Section 2: QA-T08b-08/-09, TODO R22/R23, sàn p 0.023, khai báo lag DM + Holm sau pilot) qa PASS vòng 2, merge `ea1104d`.
- Dở dang / bước tiếp: T05 tới 40/40 → qa T05 (3 kiểm tra Drive) → T07 → T06 → T08.
- Mở chat tiếp: /role leader T05

## 2026-11-26 18:20 — leader — handoff: T05 20/40, T08b/T19/T20 DONE
- Làm được: Colab reset 09:47 UTC → chạy lại setup, Drive đủ dữ liệu; T05 PatchTST 20/40 (D xong) lúc 10:18 UTC. T08b `730cfc9`, T19 `25fb482` (+R23e: 17.9 thay 18.0), T20 `8594f40`, đều qa PASS. T02 đóng (superseded).
- Quyết định: chat này vẫn mở để giữ Colab (cron 14 phút, theo yêu cầu User).
- Dở dang / bước tiếp: T05 tới 40/40 (~7 giờ) → qa T05 → T07 → T06 → T08 (mang QA-T08b-08/-09, TODO 2.6).
- Mở chat tiếp: /role leader T05

## 2026-11-26 18:10 — leader — T20 DONE
- Làm được: `24_shift_check.py` kiểm thêm 16 số R22/R23/R23e + selftest 26, qa PASS, merge `8594f40`.
- Dở dang / bước tiếp: T05 trên Colab (19/40 lúc 10:05 UTC); qa T05 → T07 → T06 → T08.
- Mở chat tiếp: /role leader T05

## 2026-11-26 17:50 — leader — T19 DONE
- Làm được: `scripts/26_feature_set_stats.py` tính lại R22/R23, qa PASS, merge `25fb482`; R23e sửa same−cross 6h 18.0 → 17.9. T02 đóng (bị thay bởi T11/T12).
- Dở dang / bước tiếp: T05 PatchTST 19/40 trên Colab (keep-alive); qa T05 → T07 → T06 → T08 (mang theo QA-T08b-08/-09, TODO 2.6).
- Mở chat tiếp: /role leader T05

## 2026-11-26 17:20 — leader — T08b DONE, T05 chạy lại
- Làm được: Colab reset 09:47 UTC, chạy lại setup (T4); Drive đủ dữ liệu (67 CSV khớp, PatchTST 19/40, SHAP npz không đổi). T08b vòng 2 qa PASS, merge `730cfc9`; dọn 4 worktree.
- Dở dang / bước tiếp: keep-alive 14 phút tới hết T05; qa T05, rồi T07, T06, T08 (sửa thêm QA-T08b-08/-09).
- Mở chat tiếp: /role leader T05

## 2026-11-26 09:15 — leader — handoff: T05 chạy trên Colab, T08b chờ vòng 2
- Làm được: T04 DONE (`d406f57`, R27/R27c/R27d), T08a DONE (`a56b751`); T08b worker `70b6a36` qa FAIL vòng 1 (3 MED câu chữ, không sai số) `08c1538`. T05 PatchTST 18/40 lúc 02:10 UTC.
- Quyết định: bỏ `10_shap.py` khỏi chuỗi Colab (không có bước bỏ qua).
- Dở dang / bước tiếp: giữ Colab 14 phút/lần tới hết T05; rồi qa T05, T08b vòng 2, T07, T06, T08.
- Mở chat tiếp: /role leader T05

## 2026-11-26 09:40 — leader — T08a DONE, đóng NOT_VERIFIED của T04
- Làm được: R27c (tính lại SHAP trên CPU khớp, đối chứng âm provenance), R27d (sửa làm tròn). T08a nháp Results chuyển giao/few-shot/SHAP qa PASS, merge `a56b751`; sửa nhỏ -01/-03 trong `docs/paper/section3_results_transfer.md`.
- Dở dang / bước tiếp: T05 PatchTST chạy trên Colab (16/40 lúc 01:20 UTC), keep-alive 15 phút; xong thì chép `runs.csv` + summary từ Drive, làm T07, T06, rồi T08 (sửa Section 2 theo TODO, thêm E1).
- Mở chat tiếp: /role leader T05

## 2026-11-26 08:35 — leader — T04 DONE, Colab chạy lại T05
- Làm được: nối lại Colab (T4, 01:20 UTC); kiểm tra Drive: CSV đủ, khớp bản clone, model/preds đủ; PatchTST 16/40 (A–C xong, D 1 seed). T04 vòng 2 qa PASS (R27), merge `d406f57`.
- Sự cố: `10_shap.py` không bỏ qua site đã xong nên chuỗi chạy lại SHAP; đã dừng trước khi ghi đè npz, chạy riêng T05. Xóa 2 dòng SHAP khỏi `notebooks/colab_resume.py` (sửa nhỏ).
- Dở dang / bước tiếp: giữ Colab (status cell 15 phút); T05 xong thì T07, T06, T08. Lưu ý QA-T04-08/09 khi viết.
- Mở chat tiếp: /role leader T05

## 2026-11-25 21:08 — leader — T16, T18 DONE; họp M16
- Làm được: Colab mất sau 05:06 UTC, nối lại 13:55 UTC; T16 đủ 432/432 × 2; `23_fewshot_stats.py --inner-val` (T18) qa PASS, merge `be6b306`; R26.
- Kết quả: thắng đối chứng tốt nhất 8/8 (p 0.023) nhưng không còn lợi so với zero-shot (−2.2/−0.7/−0.1%); so persistence p 0.117.
- Quyết định (M16, theo ủy quyền): phương án A, viết từ R25 + R26, không chạy thêm; worker thích B-lite.
- Dở dang / bước tiếp: T04b SHAP losoW8 rồi T05 PatchTST (7/40) trên Colab; T04 qa khi có CSV.
- Mở chat tiếp: /role leader T04

## 2026-11-25 11:49 — leader — T17 DONE (harness đầu ca)
- Làm được: `scripts/24_shift_check.py` (qa FAIL vòng 1 vì PASS giả, PASS vòng 2 trên `54e5150`), merge `2597ac7`; quy trình đầu ca ghi ở `CLAUDE.md` mục 8.
- Dở dang / bước tiếp: T16 scratch và T04 SHAP chạy trên Colab; còn 4 lỗi LOW của script, chưa sửa.
- Mở chat tiếp: /role leader T16

## 2026-11-25 11:35 — leader — Đồng bộ kit, harness đầu ca (T17)
- Làm được: chép từ kit `commands/{handoff,role,task}.md`, `rules/{sessions,docs}.md`, `references/handoff-template.md`, `hooks/session_start.py`, `settings.json` (thêm SessionStart); selftest hook OK. `docs/limitations_and_improvements.md` ghi điểm yếu và bài báo.
- Bỏ qua: `setup-project.md`, `README.md`, `templates` (chỉ có ở kit).
- Dở dang / bước tiếp: worker viết `scripts/24_shift_check.py` (T17), rồi qa; giữ Colab.
- Mở chat tiếp: /role leader T16

## 2026-11-25 11:09 — leader — T12 DONE (qa PASS), Colab chạy lại
- Làm được: nối lại Colab 03:35 UTC (T4); T12 xong, chạy `23_fewshot_stats.py` lần đầu trên dữ liệu thật (R25, R25c, `c25db4c`); qa tính lại khớp.
- Kết quả: finetune thắng baseline tốt nhất 8/8 site (p 0.023), nhưng baseline đó còn kém persistence; so với zero-shot lợi ích nhỏ (chỉ 6h có ý nghĩa, phụ thuộc cách gộp seed).
- Dở dang / bước tiếp: T16 và T04 SHAP đang chạy, sau đó T05 PatchTST; giữ Colab. T16 xong thì thống kê + qa, rồi họp chốt câu kết luận few-shot.
- Mở chat tiếp: /role leader T16

## 2026-11-25 06:00 — leader — T03 DONE, M14/M15, mất runtime Colab
- Làm được:
  - T03 DONE (R22–R24); T15 DONE (`scripts/23_fewshot_stats.py`, qa PASS); code T16 `--inner-val` merge.
  - Push `1dcf2f2` và các commit trước; T12 `fewshot8_cc.csv` đủ 864/864, `fewshot8_ft_free.csv` 180/432 (chỉ trên Drive).
- Quyết định (Director được User uỷ quyền): M14 chốt thống kê few-shot; M15 dùng val nội bộ cho T16. User cho phép họp agents rồi duyệt, merge thay.
- Dở dang / bước tiếp: Colab không phản hồi từ 22:49 UTC (sync cuối 22:34); chạy lại cell thiết lập, rồi cell T16. Xong T12 thì chạy `23_fewshot_stats.py` (lần đầu trên dữ liệu thật, từng bị bộ lọc chặn) rồi qa.
- Mở chat tiếp: /role leader T12

## 2026-11-25 00:50 — leader — T01 qa PASS (chờ Director duyệt), họp M13, chạy lại Colab
- Làm được:
  - Colab chết từ ~14:08 UTC 24/11; chạy lại 17:36 UTC: T03a 22/40, T12 129 dòng, chạy song song.
  - `loso8_wind.csv` về repo (`e8b19dd`). qa T01 PASS; sửa R21 bằng dòng R21c (globalW 6h là 24.0%).
- Quyết định (M13, Director được User uỷ quyền): phương án A. Chỉ nói thắng persistence có ý nghĩa ở 1h; 3h/6h dương nhưng không ý nghĩa; không nói Mamba hơn RF-W (Holm p 0.117). Không chạy thêm seed.
- T01, T14 (`d71d29d`), T09 (`453e16a`) DONE: User uỷ quyền họp agents rồi duyệt thay (25/11). Leader từng ghi nhầm Director duyệt T01 trước đó, đã sửa.
- T03 DONE (R22–R24). M14 chốt thống kê few-shot trước khi có đủ kết quả (T15 DONE, `scripts/23_fewshot_stats.py`); M15: T16 (val nội bộ) đã merge code, chờ `t12.done` trên Colab (cell 3).
- Dở dang / bước tiếp: giữ Colab; khi `t12.done` thì lập bảng few-shot + qa; sau T03/T05 thì làm T06.
- Mở chat tiếp: /role leader T12

## 2026-11-24 13:10 — leader — T01 xong, chạy T12, giữ Colab
- Làm được:
  - Colab chết từ 22/11; dán lại cell thiết lập (commit `1644c64`), chuỗi chạy tiếp.
  - T01 xong 27/27 (R21): LOSO-W thắng persistence 8/8 ở 1h, Holm p 0.023; 3h/6h p 0.078. Tốt hơn RF-W (R16). Bảng tính nhanh trong cell Colab, chưa qa; CSV mới chỉ có trên Drive.
  - T12 CPU: Ridge + RF A–H có/không `--const-calendar` xong (R19, R20, `da02b41`). T12 GPU (`fewshot8_cc.csv`, `fewshot8_ft_free.csv`) chạy song song trên Colab từ ~13:05 UTC.
  - T03a 15/40 lúc 13:07 UTC. Push `2075484`.
- Quyết định (User): có vấn đề thì tự họp agents, Director quyết thay User (đã lưu memory).
- Dở dang / bước tiếp:
  1. Giữ runtime Colab ngay (hẹn giờ cũ bị Claude Code tắt do máy thiếu RAM lúc 13:07).
  2. Lấy `loso8_wind.csv` từ Drive về repo, spawn qa tính lại bảng R21 → T01 QA.
  3. Họp `/meeting` về R21 (Mamba vượt RF-W, đổi kết luận transfer).
  4. Khi `t12.done`: bảng few-shot A–H + Wilcoxon (T12).
- Mở chat tiếp: /role leader T01

## 2026-11-21 13:30 — leader — Họp M09–M12, chạy lại Colab, sửa code few-shot
- Làm được:
  - Họp M09 (trùng tên file LOSO 4/8 fold) → T10 sửa `09` (`losoW8_*`, `globalW8_*`), merge `e124620`.
  - Colab chạy lại lúc 12:2x UTC, chain T01 → T03 → T04 → T05; đã đổi tên 42 file 8 fold trên Drive; snapshot `models_loso_4fold/`, `preds_loso_4fold/`.
  - T02 xong 72/72 nhưng qa FAIL (mốc học từ đầu không công bằng) → họp M12 → T11 sửa `07` + `18`, merge `80f0081`; push `91b5e6e`.
- Quyết định (Director, User uỷ quyền):
  - M10: PatchTST chạy đủ A–H.
  - M11: few-shot mở rộng A–H, khởi tạo từ `losoW8`.
  - M12: bộ giảm lr tính theo bước; đặc trưng tháng chọn trên val; thêm Ridge làm mốc.
  - Chi tiết các quyết định ở `tasks/MEETINGS.md`.
- User: được toàn quyền, không cần duyệt lệnh; muốn chạy một mạch thì mở `claude --continue --dangerously-skip-permissions` (`settings.local.json` đã có bypass).
- Dở dang / bước tiếp:
  1. Giữ runtime Colab.
  2. Bản chạy thử M12 (`/content/pilot`): chọn cách xử lý `month_*` theo `val_best`, ghi vào MEETINGS M12.
  3. Khi T01 xong: chạy T12 (few-shot A–H, `--init-tag losoW8`, CSV `fewshot8*.csv`) và chạy Ridge/RF trên CPU.
  4. Hàng đợi chi tiết: STATUS "Colab queue".
- Mở chat tiếp: /role leader T01

## 2026-11-21 — leader — Quy tắc mức suy luận
- Làm được: thêm quy tắc "mỗi chat tự chọn mức suy luận theo việc, cả worker/qa" vào `CLAUDE.md` mục 8 (thay đổi nhỏ, chưa commit).
- Quyết định (User): chat tự chọn mức suy luận; làm tiếp trong chat hiện tại đến khi User bảo chuyển.

## 2026-11-21 — leader — Chốt quyết định kit + chuẩn bị chat mới
- Làm được: ghi quyết định của User vào `CLAUDE.md` (mục 2, 8) và `tasks/STATUS.md` (Approved decisions 2026-11-21); thêm `notebooks/colab_resume.py` (cell thiết lập + cell giữ runtime, vì notebook Colab mở lại luôn trống); ROADMAP bỏ yêu cầu ngày mục tiêu.
- Quyết định (User): giữ nguyên cách làm cũ — Python `py` 3.12 (không dùng `D:\Project\.venv`); không đặt ngày mục tiêu; được tự cài gói (ngoại lệ của `rules/code.md`); lịch sử trước kit giữ nguyên, không chạy lại qua worker/qa.
- Dở dang / bước tiếp: T01 Mamba LOSO 8 fold 7/27 (Colab dừng từ 16/11 18:58 UTC) → mở Colab, dán cell thiết lập, chạy hàng đợi T01→T05 (~24 h GPU), giữ runtime 15 phút/lần; xong hoặc mất GPU thì push + tắt máy.
- Mở chat tiếp: /role leader T01

## 2026-11-21 — leader — Cài bộ khung `.claude` cho dự án
- Làm được: chép kit từ `D:\Project\.claude` (rules, agents, commands, references, policies, hooks, settings); tạo `CLAUDE.md`, `tasks/STATUS.md`, `tasks/ROADMAP.md`, `tasks/RESULTS.md` (R01–R17 điền lại từ nhật ký cũ), `tasks/MEETINGS.md` (M01–M08); `.gitignore` thêm `.claude/worktrees/`, `.claude/hooks/.turns/`.
- Quyết định: giữ `docs/NHAT_KY_DU_AN.md` làm lịch sử chi tiết đến 16/11; từ nay ghi theo kit.
- Dở dang / bước tiếp: Colab dừng từ 16/11 18:58 UTC — T01 (Mamba LOSO 8 fold) 7/27 lượt; hàng đợi T01 → T02 → T03 → T04 → T05. Cần User chốt: dùng `D:\Project\.venv` hay giữ `py` 3.12; ngày mục tiêu cho ROADMAP.
- Mở chat tiếp: /role leader T01
