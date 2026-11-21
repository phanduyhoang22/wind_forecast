# MEETINGS

Meetings M01–M08 (2026-11-09 → 2026-11-15) were held before the kit with three standing agents (methods/statistics reviewer, wind-energy domain expert, ML engineer) and Claude deciding by majority. Full minutes (Vietnamese): `docs/NHAT_KY_DU_AN.md` §5 and later sections; briefs: `docs/meetings/`. From now on, meetings follow `/meeting` (qa, worker, Leader, Director, User decides).

## M12 — 2026-11-21 — T02 QA FAIL: scratch baseline is not fair
- trigger: QA finding that invalidates an earlier interpretation (M07: "scratch fails because of range coverage").
- evidence: R18 (`fewshot_scratch2.csv`, 72/72 runs). QA T02 report 2026-11-21: no line-level bug in the scratch path (steps→epochs, patience, warm-up, best-state restore, val = target's own); but a Ridge on the same 19 W features and the same k weeks gives RMSE 1h A DB 0.830/0.807/0.772 and B DB 0.704/0.616/0.608 (1/2/4 w), versus scratch 2.70 (A DB 1w, only 2 % of test out of range) and 2.76→3.30 (B DB, worse as coverage improves). Each k-week window lies in one month, so `month_sin/cos` are constant in training while the test spans 0–0.93; ReduceLROnPlateau patience stays at 3 epochs (with 1 w, lr halves every ~40 steps). QA-T02-02 (low): the window excludes the 23:45 sample.
- question: how to obtain a fair from-scratch few-shot baseline before T12 (M11 condition 1)?
- options: A) diagnose + fix: drop the calendar `month_*` (and test `hr_*`) for scratch, scale the LR-scheduler patience to steps, pilot 1 run (A DB 1w), then re-run the 72 scratch runs (~1–2 h T4); add Ridge on k weeks as a linear reference (CPU); B) do not fix the NN: report Ridge/RF on k weeks as the from-scratch references and describe the NN scratch failure as overfitting/extrapolation; C) keep current plan (report scratch as is).
- qa: evidence SOLID. Confirmed `07_run_benchmark.py:117` `ReduceLROnPlateau(patience=3)` in epochs is never converted to steps in 18 (only early stop + warm-up are). C is a strawman; B hides an untuned NN. A is post-hoc but strengthens the baseline (conservative): select the fix on validation only, freeze it before test, disclose it. The scheduler fix must also apply to finetune (shared `run_nn`); dropping `month_*` only for scratch is an asymmetry, so drop it for both or report a finetune ablation. Recommends A + Ridge; report the finetune gain vs the best of scratch-NN / Ridge / RF.
- worker: A feasible, ~15–20 lines in 2 files: `sched_patience` argument in `run_nn` (default 3 keeps E1/LOSO identical), 18 passes `ceil(400/nb)`; `month_*` held constant in a copy of `d.X` (dimension stays 19); Ridge mode ~8 lines (CPU, seconds). GPU 1–2 h for 72 runs. A real 19→17 input drop for finetune would need all LOSO-W models retrained, so keep the dimension.
- leader: folds into T11/T12 (already planned re-runs with the 8-fold init), so the extra GPU is only the A–D sensitivity re-run (~2 h). No stage change.
- director recommendation: A + Ridge. (1) The LR-scheduler patience is scaled to steps for BOTH finetune and scratch. (2) The `month_*` handling is selected on validation only in a pilot (scheduler-only vs scheduler + constant `month_*`), for scratch; if constant `month_*` is chosen, report a finetune ablation with the same change (no retraining). Freeze the choice before any test score is read. (3) Add Ridge on k weeks as the linear reference; the main claim = finetune vs the best of {scratch NN, Ridge, RF}. (4) Fix QA-T02-02 (include the 23:45 sample). (5) Disclose as a post-hoc change of the baseline. R18 stays in RESULTS as a failed/invalid baseline row. Dissent: qa prefers symmetric `month_*` handling; settled by (2).
- decision: A + Ridge with conditions (1)–(5), 2026-11-21. Taken by the Director under the User's delegation; the User is informed in chat. | status: DECIDED
- follow-up (Leader, 2026-11-22): the first pilot (`pilot_free.csv` / `pilot_const.csv`, A–D, 1 seed, 72 + 72 rows) logged test metrics only, with no validation column, so it cannot be used for selection. Disclosure: the Leader saw partial test RMSE in the run logs (const looked better at A–C). Fix: T13 adds `val_best`/`best_epoch`, then the pilot is re-run and the selection uses `val_best` only.
- action items: T11 expanded (init-tag + sched patience + month option + ridge mode + 23:45 fix); pilot on validation; T12 runs finetune/scratch/ridge/rf at A–H (8-fold init) + A–D (4-fold init, sensitivity) with the frozen code; T02 closed as superseded.

## M11 — 2026-11-21 — Extend few-shot (E9) to all 8 sites
- trigger: User question ("we have 8 sites, right?"). Few-shot finetune (R11) and scratch (T02, R18) cover A–D only, because the finetune init is the 4-fold LOSO-W model. All other experiments cover A–H.
- evidence: R11, R13, R18; T02 median table (finetune beats persistence at A–C, ≈ at D; scratch 1.4–3.3 m/s; RF k-weeks 0.82–3.48). T02 QA is still running (scratch result looks anomalous).
- question: run few-shot at all 8 sites, using the 8-fold LOSO-W models (`losoW8_*`, available after T01) as the finetune init?
- options: A) after T01, run finetune + scratch + RF at A–H with the `losoW8` init (8 × 2 windows × 3 weeks × 3 seeds = 144 runs per mode; ≈ 3–4 h GPU + RF on CPU), report the 8-site table as the main one and the 4-fold A–D run as a sensitivity check; B) only add E–H with the 8-fold init (72 runs per mode), mixing 4-fold (A–D) and 8-fold (E–H) inits; C) keep current plan (A–D only, stated as a limitation).
- qa: A SOLID (conditional), B INVALID (the init is confounded with the site, so a pooled Wilcoxon is invalid), C WEAK (n = 4 is below the n = 8 rule; reads as cherry-picked). Scratch rows are INVALID until the T02 bug check clears. Verify that each `losoW8_{t}` excludes t. The init name is hard-coded at `18_fewshot.py:90`.
- worker: A is feasible: ~5 lines (`--init-tag`, default `losoW`); 2 modes × 144 runs × 30–100 s ≈ 2.4–8 h T4, plus RF on CPU (one job at a time, several hours). Keep the old CSVs for disclosure. First step: a light task plus a 1-site, 1-seed smoke run. B is not recommended (not comparable).
- leader: depends on T01 (~9–10 h GPU left); adds ~3–8 h GPU after T05; no stage change (S3 done-criteria: the few-shot table gets n = 8).
- director recommendation: A. Conditions: (1) the T02 QA must clear the scratch path; if it is a bug, fix it first and re-run scratch; (2) run only after T01 is merged into the files as `losoW8_*`; (3) light task T11 adds `--init-tag` to `18_fewshot.py`, with new out CSVs `fewshot8*.csv`; (4) the 8-site table is the main one; the A–D 4-fold run becomes a sensitivity check (disclosed). Dissent: none.
- decision: A with conditions (1)–(4), 2026-11-21. Taken by the Director under the User's delegation ("cứ họp rồi quyết định nhé"); the User is informed in chat. | status: DECIDED
- action items: T11 (init-tag light task); T12 few-shot A–H (finetune + scratch on Colab, RF on CPU), after T01 + the T02 QA.

## M10 — 2026-11-21 — PatchTST missing at sites E–H
- trigger: Drive inventory (Leader, 2026-11-21): `runs.csv` has DLinear/LSTM/Mamba/Transformer 5 seeds × 8 sites and PatchTST only A 5, B 2 (7/20), with no runs at E–H; `runs_rf.csv` has 8 × 5. ROADMAP S2 says "6 models × 8 sites × 5 seeds", but T05 covers only A–D (M06: "PatchTST must reach 20/20").
- evidence: Drive `results/runs.csv` (501 rows); R03, R09; M06.
- question: should PatchTST also run at E–H (5 seeds) so that the E1 table is complete for 8 sites?
- options: A) extend T05 to A–H (13 + 20 = 33 runs, ~16 min/run ≈ 9 h T4); B) T05 stays A–D (13 runs ≈ 3.5 h); the paper reports PatchTST on 4 sites only, discloses this, and leaves the 8-site DM/Holm without PatchTST; C) keep current plan (= B without an explicit disclosure decision).
- qa: direction valid; evidence WEAK only because the docs disagree (ROADMAP "14/20", STATUS "6/20", Drive 7/20). The Leader resolved this: Drive `runs.csv` deduplicated on (site, model, seed) gives PatchTST A 5, B 2, C–H 0. B leaves holes in the model×site table, invites a "selective reporting" critique and gives an uneven Holm family; C leaves ROADMAP and T05 in contradiction. Recommends A.
- worker: A only needs `--sites A..H` (skip key (site, model, seed), one row appended per run, so a reset loses at most one run). `08_aggregate` does not crash on a missing site, but its `overall` average would cover different site sets per model, so B needs a common-site restriction. Effort: A ≈ 9–10 h T4 (3–4 resets); B ≈ 3.5 h. Do A incrementally: A–D finish first in site order, so B already holds if the GPU runs out.
- leader: +~5.5 h GPU on top of the ~24 h queue; no stage change; S2 done-criteria become literally true (6 × 8 × 5).
- director recommendation: A, run incrementally (sites in order A..H). Condition: if the GPU budget runs out before E–H finish, fall back to B with a common-site average and disclosure. Dissent: none.
- decision: A, 2026-11-21. Taken by the Director under the User's delegation ("họp agents rồi đưa ra quyết định, nhớ thông báo"); the User is informed in chat. | status: DECIDED
- action items: T05 scope -> A–H (33 runs); fix ROADMAP S2 count; the new chain is applied when Colab is restarted after the T10 merge.

## M09 — 2026-11-21 — LOSO-W 8-fold overwrites 4-fold model/pred files
- trigger: Leader code read before resuming T01 found a file-name collision (QA-type finding that can invalidate stored artifacts of earlier results).
- evidence: `scripts/09_global_loso.py` names files `{st}_{fold}_{model}_{seed}` (st = `global`/`loso` + `D`/`W`/`R`), with no site-count tag; same `results/models_loso/`, `results/preds_loso/` for 4-fold and 8-fold. Local RF: `preds_loso/globalW_*_RF_*` and `losoW_*_RF_*` all dated 2026-11-15 23:01+ = 8-fold run (R16) → 4-fold RF-W preds (R07, R12) gone; CSV metrics intact. Mamba: T01 (R17, 7/27 done: global seeds 0–2 + fold A seeds 0–2 + 1) writes `losoW_{A..H}_Mamba_{0..2}` over the 4-fold LOSO-W files (R15, 5 seeds) on Drive. Users of those files: `18_fewshot.py` finetune init (`models_loso/losoW_{t}_{model}_{seed}.pt`, R11 already done with 4-fold models), T04b SHAP (`--pattern losoW_{site}_...`, sites A–D).
- question: how to handle the collision before resuming T01?
- options:
  A) Backup + rename: before resuming, copy Drive `models_loso/`, `preds_loso/` to a frozen `*_4fold/` snapshot; change `09` so 8-site runs write files with a `8` tag (e.g. `losoW8_A_Mamba_0.pt`) while the CSV `strategy` key stays `losoW` (no re-run of the 7 done runs); move the already-written 8-fold files (by mtime ≥ 2026-11-16) to the new names; T04b SHAP pattern set explicitly (4-fold or 8-fold).
  B) Backup only: snapshot Drive `models_loso/`, `preds_loso/` now (whatever 4-fold files still survive), no code change; after T01, `losoW_*` = 8-fold; document that 4-fold window-level preds are partly lost.
  C) Keep current plan: resume T01 as is; 4-fold results kept as CSV metrics only (secondary, superseded by 8-fold); note in paper that 4-fold DM tests are not reported.
- Drive check (Leader, 2026-11-21): 4-fold Mamba-W files already overwritten on 2026-11-16 17:33–18:48 UTC: `losoW_A_Mamba_{0,1,2}`, `losoW_B_Mamba_0` (.pt + .npz) and the `globalW` Mamba seeds 0–2. Drive keeps only one revision (`list_file_revisions` on `losoW_A_Mamba_0.pt`), so they cannot be recovered. Intact 4-fold: A_3–4, B_1–4, C_0–4, D_0–4.
- qa: evidence SOLID. No script reads `preds_loso` (08/11/13/14 read `results/preds` only), so no reported number depends on the lost files. Extra collision: RF `loso_rf_wind.csv` (d24) and `_d16` wrote the same pred names. The CSV skip key `(strategy, fold, model, seed)` is the same for 4- and 8-fold, so it stays safe only while the two CSVs are separate. `18_fewshot.py:90` and T04b load `losoW_*` with no check, so after T01 they would silently get mixed 8-fold/4-fold inits. Ranks A > B > C; C breaks R11 and 4-fold SHAP reproducibility.
- worker: A is feasible: ~1–2 h, 0 GPU, ~3 lines in `09` (tag `8` when 8 sites; CSV key unchanged) plus an explicit T04b pattern in `colab_resume.py`. Identify the 8-fold files from the `loso8_wind.csv` keys, not from mtime. The `cp -u` sync can recreate old names, so rename only while no Colab job runs, and keep the `*_4fold` snapshot outside `SUBS`. B takes 10 min but does not stop the next overwrite. Reject C.
- leader: no stage or schedule change, and 0 GPU for A. Treat the code change as a light task (worker + qa), which adds ~1 h before T01 resumes. The lost 4-fold seeds (A 0–2, B 0) only affect R11 reproducibility from weights, not any metric. Re-training them is optional (~4 runs × 28 min ≈ 2 h GPU).
- director recommendation: A. It is the only option that stops further loss and makes 8-fold vs 4-fold explicit for 18/10, at zero GPU cost. Conditions: (1) copy the Drive `models_loso/` and `preds_loso/` to `*_4fold/` first; (2) rename the 8-fold files (Mamba seeds from the `loso8_wind.csv` keys, all local RF-W files) while no job runs; (3) T04b SHAP uses the 8-fold models for A–H (the main transfer result); (4) disclose the lost 4-fold artifacts in STATUS/RESULTS; no re-training of lost seeds unless a reviewer asks. Dissent: none (qa and worker both rank A first).
- decision (User): A, 2026-11-21 | status: DECIDED
- action items: T10 (09 file tag + T04b pattern, light task). Leader, before T01 resumes: Drive snapshot `*_4fold/`, rename T01 8-fold files (from `loso8_wind.csv` keys), rename local RF-W 8-fold preds. T04 scope -> 8-fold A–H. User asked to restart Colab first, so the queue runs T02/T03 while T10 is done; T01 goes back in after the T10 merge.

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
