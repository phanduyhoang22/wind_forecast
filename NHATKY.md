# NHATKY

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
