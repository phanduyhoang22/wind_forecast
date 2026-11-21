# MEETINGS

Meetings M01–M08 (2026-11-09 → 2026-11-15) were held before the kit with three standing agents (methods/statistics reviewer, wind-energy domain expert, ML engineer) and Claude deciding by majority. Full minutes (Vietnamese): `docs/NHAT_KY_DU_AN.md` §5 and later sections; briefs: `docs/meetings/`. From now on, meetings follow `/meeting` (qa, worker, Leader, Director, User decides).

## M08 — 2026-11-15 — Data gaps review
- trigger: User asked whether missing data needs to be added.
- evidence: brief `docs/meetings/2026-11-15_data_gaps_brief.md`; R15, R16.
- question: which gaps must be fixed before submission; extra data; LOSO 8-fold.
- options: A) add years/sites/heights/measured masts B) 8-fold LOSO only C) keep current plan
- views: reviewer — LOSO-8 MUST (n = 4 → min p 0.125), F coast check MUST; domain — public masts (ESMAP 2008–09, Phan Rang / Phan Thiet / Pleiku) not concurrent, limitation only; ML — LOSO-8 ~11–16 h T4 at 3 seeds, RF depth 16 sequential.
- decision (Claude, majority): B; no extra data; Mamba-W 3 seeds right after LOSO-W A–D; limitations stated. | status: DECIDED
- action items: T01; RF-8 done (R16); F coast done (~3 km).

## M07 — 2026-11-15 — Few-shot baseline + RF depth
- trigger: scratch RMSE ~2.7 (R11) looked like a straw-man baseline.
- decision: fixed step budget 2000 / patience 400 / warm-up 100 after a pilot; add RF on k weeks; rerun RF-W at depth 16 to de-confound delta (3/3). Queue: after LOSO-W A–D (2/3). | status: DECIDED
- action items: T02; R12, R13 done.

## M06 — 2026-11-15 — Transfer results + confirm three unilateral calls
- decision: rerun RF W+delta at depth 16 (2/3); PatchTST last but 20/20 (3/3); accept site F with conditions (sea-breeze peak + ≤ 5 km, both met) and disclose threshold relaxation (3/3). Stats unit = target site; start Data & Methods. | status: DECIDED

## M05 — 2026-11-13/14 — Data expansion
- decision: keep A–D, add E–H under a pre-set gate; 8×8 cross-site matrix; 2016 back-test. | status: DECIDED

## M04 — 2026-11-13 — Closest recent papers
- decision: PowerMamba (IEEE TPWRS 2026), VMamba-WSP (Energy Reports 2026), Despotovic et al. (IJGE 2026); plan v2.0 (`docs/Ke_hoach_du_an_v2.docx`). | status: DECIDED

## M03 — 2026-11-13 — LOSO results
- decision: zero-shot failure is a finding; delta target, few-shot, feature ablation next. | status: DECIDED

## M02 — 2026-11-10 — E1 first pass
- decision: per-seed DM + paired t main table; ensemble separate; "Mamba ≈ Transformer". | status: DECIDED

## M01 — 2026-11-09 — After pilot
- decision: fix weight decay + warm-up; DM lag max(h−1, 96) + Holm; fixed tuning grid on A+D. | status: DECIDED
