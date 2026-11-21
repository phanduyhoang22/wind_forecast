# STATUS — wind_forecast

## Goal
Publishable paper (Q1–Q3): Mamba vs Transformer / LSTM / PatchTST / DLinear / RF for 1h/3h/6h wind-speed forecasting at 8 Vietnamese sites (NREL SEA-WTK v3), with cross-site transfer, SHAP and honest statistics against persistence.

State flow: `TODO -> IN_PROGRESS -> READY_FOR_QA -> QA_PASSED -> APPROVAL_PENDING -> DONE` (light: `QA_PASSED -> DONE`). Spec: `.claude/references/multi-agent-spec.md`.

Kit set up on 2026-11-21. Work before that date followed a 3-agent meeting process logged in `docs/NHAT_KY_DU_AN.md`; it is summarised here and in `tasks/MEETINGS.md` (M01–M08), not re-done.

## Approved decisions
- 2026-11-08: data = NREL SEA-WTK v3 (old `data/` rejected: 15-min values linearly interpolated from hourly); official `mamba-ssm` CUDA kernel built for T4; RF on CPU, NNs on Colab; add PatchTST + DLinear; horizons 1h/3h/6h; no site ID in global/LOSO; push code + `data_v2/*.npz` to public GitHub.
- 2026-11-09 (M01): fix weight decay (matrices only), 1-epoch warm-up; DM with HAC lag max(h−1, 96) + Holm; fixed tuning grid on sites A+D, selected on val; 5 seeds; GAN-phase check passed (0.97–1.01).
- 2026-11-10 (M02): per-seed DM (k/5) + paired t is the main table; seed ensemble reported separately; write "Mamba ≈ Transformer", never "outperforms".
- 2026-11-13 (M03): LOSO failure is a finding; try delta target, few-shot (1/2/4 weeks, ≥2 seasonal windows, scratch baseline), feature ablation for the "latent site ID" hypothesis.
- 2026-11-13 (M04): reference papers PowerMamba (IEEE TPWRS 2026), VMamba-WSP (Energy Reports 2026), Despotovic et al. (IJGE 2026); plan v2.0.
- 2026-11-14 (M05): keep 4 sites, add E–H (one per regime) under a pre-set gate; 8×8 cross-site matrix; 2016 back-test. E7 result: wind-only set W (19) is the transfer configuration.
- 2026-11-15 (M06): rerun RF W+delta at max_depth 16; PatchTST stays last but must reach 20/20; site F accepted if afternoon sea-breeze peak and ≤ 5 km from shore (both now confirmed: peak 14 h, ~3 km); disclose threshold relaxation 6.0→5.5 m/s; start writing Data & Methods.
- 2026-11-15 (M07): few-shot scratch baseline re-run with fixed budget 2000 steps / patience 400 / warm-up 100; add RF-on-k-weeks baseline; report honestly if scratch stays poor.
- 2026-11-15 (M08): no extra data (years/sites/heights/masts); LOSO must be 8-fold (n = 4 cannot reach p < 0.125); Mamba-W 3 seeds, RF-W depth 16; modelled-data, single height, no NWP, 2 sites/regime = stated limitations.
- 2026-11-15 (User): install needed packages without asking; commits without Claude attribution; keep Colab alive every 15 min; shutdown PC when GPU/Colab is lost or queue done.
- 2026-11-21 (User): keep everything as done so far — Python stays `py` 3.12 (not `D:\Project\.venv`); ROADMAP target dates stay TBD; auto-install of packages allowed (override of `.claude/rules/code.md`). Pre-kit history is accepted as-is (no re-run through worker/qa).
- 2026-11-21 (M09, User): option A. LOSO runs on a non-default site set write files tagged with the site count (`losoW8_*`, `globalW8_*`); the CSV `strategy` key is unchanged. Before T01 resumes, snapshot Drive `models_loso/` and `preds_loso/` to `*_4fold/` and rename T01's 8-fold files. T04b SHAP uses the 8-fold models A–H. Lost 4-fold artifacts (Mamba-W A seeds 0–2, B seed 0, globalW seeds 0–2; all 4-fold RF-W preds) are disclosed, not re-trained.
- 2026-11-21 (M10, Director under User delegation): PatchTST E1 extended to all 8 sites (40 runs), run in site order; fallback = A–D with a common-site average + disclosure.
- 2026-11-21 (M11, Director under User delegation): few-shot E9 extended to A–H with the 8-fold `losoW8` init (finetune, scratch, RF); the 8-site table is the main one, the 4-fold A–D run a disclosed sensitivity check; conditional on the T02 QA clearing the scratch path and on T01 finishing.

## Colab queue (as of last Drive sync 2026-11-16 18:58 UTC — nothing ran after)
T01 → T02 → T03 → T04 → T05. Runner: `notebooks/colab_resume.py` (paste the setup cell into the empty MCP notebook; it re-clones, restores results from Drive, skips finished keys, starts the chain + Drive sync). Estimated GPU left: T01 ~10 h, T02 ~3–4 h, T03 ~4–5 h, T04 ~1.5 h, T05 ~4.4 h (≈ 24 h).
How to resume in a new chat: `open_colab_browser_connection` → paste setup cell → run → add status cell → keep-alive every ~15 min (background `sleep 840` timer) → on GPU loss or `all.done`: commit + push, `shutdown /s /t 600`.

## T01 — Mamba-W LOSO 8-fold
- owner: Leader (Colab) | priority: P0 | status: IN_PROGRESS | attempt_count: 1
- goal: zero-shot transfer of Mamba (wind-only) to each of 8 unseen sites; enables Wilcoxon n = 8.
- scope: `scripts/09_global_loso.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 3 --features wind --out results/loso8_wind.csv`
- inputs: `data_v2/*.npz`, `results/tuned.json` | expected_outputs: `results/loso8_wind.csv`, `results/models_loso/losoW_*`
- acceptance_criteria: 27 runs (3 global + 24 LOSO) in CSV; median-seed skill table + two-sided Wilcoxon (Holm) vs persistence, same format as RF (R12).
- dependencies: Colab T4 | allowed_paths: `results/`
- test_evidence: 7/27 runs on Drive. Fold A median RMSE 1h 0.749 (persistence 0.845, RF-8 0.765); fold B seed 0 0.672 (persistence 0.640) — watch.
- risks: Colab resets (3 so far); ~28 min/run, ~10 h left.
- last_update: 2026-11-21

## T10 — LOSO file names tagged by site set (M09) — light task
- owner: worker | priority: P0 | status: DONE | attempt_count: 1
- goal: 8-site global/LOSO runs no longer overwrite 4-site model/pred files.
- scope: in `scripts/09_global_loso.py`, prefix model files (`models_loso/`) and pred files (`preds_loso/`) with `st + "8"` when `--sites` has 8 sites (e.g. `losoW8_A_Mamba_0.pt`, `globalW8_ALL_Mamba_0.pt`), other site sets unchanged. The CSV `strategy` column and the skip key stay exactly as now. In `notebooks/colab_resume.py`, re-add T01, and T04b with `--sites A,B,C,D,E,F,G,H --pattern losoW8_{site}_{model}_{seed}.pt --tag losoW8`.
- acceptance_criteria: (1) with 4 sites the names are unchanged; with 8 sites they carry `8`; the CSV `strategy` values are unchanged in both; (2) CPU smoke `py scripts/09_global_loso.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 1 --epochs 1 --max-batches 2 --features wind --out <scratch>/loso8.csv` writes `losoW8_*`/`globalW8_*` files and `strategy` = `globalW`/`losoW`; (3) diff ≤ ~15 lines in ≤ 2 files.
- allowed_paths: `scripts/09_global_loso.py`, `notebooks/colab_resume.py`
- test_evidence: QA PASS 2026-11-21 (qa: 4-site names unchanged, 8-site `globalW8_*`/`losoW8_*`, CSV strategy unchanged, skip key works; CPU smoke wrote `globalW8_*`; diff 7 lines in 2 files).
- last_update: 2026-11-21 (Leader): approved on QA PASS (light task), merged `e124620` from 2be4970; worktree removed.

## T02 — Few-shot scratch, fixed step budget
- owner: Leader (Colab) | priority: P1 | status: READY_FOR_QA | attempt_count: 1
- goal: fair from-scratch baseline for E9 (M07).
- scope: `scripts/18_fewshot.py --sites A,B,C,D --models Mamba --seeds 3 --modes scratch --scratch-steps 2000 --out results/fewshot_scratch2.csv`
- acceptance_criteria: 72 runs (4 sites × 2 windows × 3 weeks × 3 seeds); table vs finetune (`fewshot.csv`), RF (`fewshot_rf.csv`), persistence.
- test_evidence: pilot A/1 week: RMSE 1h 1.72 (DB) / 1.88 (TN) — overfits, not under-trained.
- last_update: 2026-11-21 (Leader): 72/72 runs done on Colab 10:4x UTC, Drive `results/fewshot_scratch2.csv`; run log RMSE 1h 1.2–3.4 (still far above persistence). Next: comparison table vs finetune/RF/persistence + qa.

## T03 — E1-W Mamba 8 sites + cross-site 8×8 (W)
- owner: Leader (Colab) | priority: P1 | status: TODO | attempt_count: 0
- scope: `07_run_benchmark.py --sites A..H --models Mamba --seeds 5 --features wind --out results/runs_wind.csv`; then `16_cross_eval.py --sites A..H --models Mamba --seeds 3 --features wind --out results/cross_eval_wind.csv`
- acceptance_criteria: 40 E1-W runs; 8×8 W matrix with same-/cross-regime split; compare to 31-feature versions.
- last_update: 2026-11-21

## T04 — SHAP (Mamba-31 per site, Mamba-W LOSO)
- owner: Leader (Colab) | priority: P2 | status: TODO | attempt_count: 0
- scope: `10_shap.py --sites A..H --model Mamba --seed 0`; `10_shap.py --sites A,B,C,D --models-dir results/models_loso --pattern losoW_{site}_{model}_{seed}.pt --features wind --tag losoW`
- acceptance_criteria: `shap_importance_*.csv`, `shap_temporal_*.csv`; completeness error reported.
- last_update: 2026-11-21

## T05 — PatchTST E1 to 40/40 (A–H, M10)
- owner: Leader (Colab) | priority: P2 | status: TODO | attempt_count: 0
- scope: `07_run_benchmark.py --sites A,B,C,D,E,F,G,H --models PatchTST --seeds 5 --out results/runs.csv` (M10, 2026-11-21; Drive 7/40 done: A 5, B 2).
- acceptance_criteria: 40 PatchTST runs ×3 horizons in `runs.csv`; fallback if the GPU runs out: A–D 20/20 with a common-site average and disclosure (M10).
- last_update: 2026-11-21

## T06 — Aggregate statistics for 8 sites
- owner: worker | priority: P1 | status: TODO | attempt_count: 0
- goal: final E1 tables + DM/Holm + per-seed evidence for 8 sites; regime tables; Wilcoxon for transfer.
- scope: run `08_aggregate.py`, `14_regime.py` on 8 sites; transfer stats script for LOSO-8 (Mamba vs RF vs persistence, rank-biserial).
- dependencies: T01, T03, T05 | allowed_paths: `scripts/`, `results/`
- last_update: 2026-11-21

## T07 — Conformal intervals (E11)
- owner: worker | priority: P2 | status: TODO | attempt_count: 0
- scope: `py scripts/11_conformal.py` (α 0.1, 0.05), PICP/PINAW overall and by wind tercile.
- dependencies: preds + val preds from E1 | allowed_paths: `results/`
- last_update: 2026-11-21

## T08 — Paper: Results & Discussion draft
- owner: worker | priority: P1 | status: TODO | attempt_count: 0
- scope: `docs/paper/section3_results.md`; Section 2 draft exists (`docs/paper/section2_data_methods.md`).
- dependencies: T06 (experiments frozen) | allowed_paths: `docs/paper/`
- last_update: 2026-11-21

## T09 — Update README
- owner: worker | priority: P3 | status: TODO | attempt_count: 0
- goal: README still describes the old 4-site ERA5 notebooks; rewrite install/run/reproduce for the `scripts/01–21` pipeline.
- allowed_paths: `README.md`
- last_update: 2026-11-21

## T11 — `--init-tag` for few-shot (M11) — light task
- owner: worker | priority: P1 | status: TODO | attempt_count: 0
- goal: `18_fewshot.py` can load the finetune init from `models_loso/{init_tag}_{t}_{model}_{seed}.pt` (default `losoW`, unchanged behaviour).
- acceptance_criteria: default run gives the same file path as now; `--init-tag losoW8` loads `losoW8_*`; diff ≤ ~10 lines.
- allowed_paths: `scripts/18_fewshot.py`
- dependencies: T02 QA verdict | last_update: 2026-11-21

## T12 — Few-shot A–H with the 8-fold init (M11)
- owner: Leader (Colab) + worker (RF, CPU) | priority: P1 | status: TODO | attempt_count: 0
- scope: `18_fewshot.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 3 --modes finetune,scratch --scratch-steps 2000 --init-tag losoW8 --out results/fewshot8.csv`; RF: `--modes rf --out results/fewshot8_rf.csv` (CPU).
- acceptance_criteria: 144 runs per mode; median-seed table vs persistence; Wilcoxon (n = 8, Holm) finetune vs persistence and vs scratch/RF.
- dependencies: T01, T10, T11, T02 QA | last_update: 2026-11-21
