# NHATKY

## 2026-11-25 00:50 — leader — T01 qa PASS (chờ Director duyệt), họp M13, chạy lại Colab
- Làm được:
  - Colab chết từ ~14:08 UTC 24/11; chạy lại 17:36 UTC: T03a 22/40, T12 129 dòng, chạy song song.
  - `loso8_wind.csv` về repo (`e8b19dd`). qa T01 PASS; sửa R21 bằng dòng R21c (globalW 6h là 24.0%).
- Quyết định (M13, Director được User uỷ quyền): phương án A. Chỉ nói thắng persistence có ý nghĩa ở 1h; 3h/6h dương nhưng không ý nghĩa; không nói Mamba hơn RF-W (Holm p 0.117). Không chạy thêm seed.
- Chờ Director duyệt: T01, T14 (`174c54a`) và T09 README (`c992732`), đều qa PASS; T14, T09 chưa merge. Leader từng ghi nhầm Director duyệt T01, đã sửa.
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
