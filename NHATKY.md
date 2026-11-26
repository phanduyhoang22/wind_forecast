# NHATKY

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
