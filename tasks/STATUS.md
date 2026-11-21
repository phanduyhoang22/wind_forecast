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
- 2026-11-21 (M12, Director under User delegation): few-shot scratch baseline fixed post hoc (disclosed): LR-scheduler patience scaled to steps for finetune and scratch; `month_*` handling picked on validation in a pilot and frozen before test; Ridge on k weeks added; main claim = finetune vs best of scratch NN / Ridge / RF; R18 kept as an invalid-baseline row.

## Colab queue (2026-11-21 ~13:30 UTC, live)
- Main chain (restarted 2026-11-21 12:2x UTC on commit 3a4ad2b): T01 → T03a (13/40 done before the restart) → T03b → T04a → T04b (`losoW8`) → T05 (PatchTST A–H) → `results/all.done`. T02 is finished (72/72) and was removed from the chain. At 12:57 UTC T01 was 9/27.
- Estimated GPU left: T01 ~8.5 h, T03 ~3.5 h, T04 ~1.5 h, T05 ~9 h.
- Runtime reset between 14:42 and 14:54 UTC: the unsynced pilot in `/content/pilot` was lost. Restarted at ~14:56 UTC (commit d7a94c2) with T01 at 12/27.
- Side job: the M12 pilot now runs in the main clone and is synced to Drive. It runs `18_fewshot.py --sites A,B,C,D --seeds 1 --modes scratch --scratch-steps 2000`, writing `results/pilot_free.csv` and then `results/pilot_const.csv` (`--const-calendar`), with `results/pilot.done` and `results/pilot.log`. Compare `val_best` only and pick the `month_*` handling. Partial test RMSE seen before the reset (not for selection): free A 1.14–1.51, B 2.0–2.9, C 1.6–2.0, D 2.0–2.7; const A 0.82–1.15, B 0.83–1.72.
- The setup cell must also restart the pilot until `pilot.done` exists (see the cell in the MCP notebook; the runner file has no pilot).
- Runner: `notebooks/colab_resume.py`. Paste the setup cell into the empty MCP notebook; it re-clones, restores results from Drive, skips finished keys, and starts the chain plus the Drive sync. The runner still lists T02; it is skipped because all its keys are done.
- Resume in a new chat:
  1. `open_colab_browser_connection`, then `get_cells`.
  2. If the cells still exist, run the status cell. If the notebook is empty, paste the setup cell and run it.
  3. Keep the runtime alive every ~15 min (background `sleep 840` timer, then run the status cell).
  4. On GPU loss or `all.done`: commit + push, then `shutdown /s /t 600`.
  - Stale-output check: if the printed time does not change, check the Drive `results/run.log` modifiedTime.
- Never `cp` the clone's `models_loso/`/`preds_loso/` onto Drive by hand after a rename (cp -u re-creates old names); the Drive snapshot `models_loso_4fold/`, `preds_loso_4fold/` is frozen.

## T01 — Mamba-W LOSO 8-fold
- owner: Leader (Colab) | priority: P0 | status: IN_PROGRESS | attempt_count: 1
- goal: zero-shot transfer of Mamba (wind-only) to each of 8 unseen sites; enables Wilcoxon n = 8.
- scope: `scripts/09_global_loso.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 3 --features wind --out results/loso8_wind.csv`
- inputs: `data_v2/*.npz`, `results/tuned.json` | expected_outputs: `results/loso8_wind.csv`, `results/models_loso/losoW_*`
- acceptance_criteria: 27 runs (3 global + 24 LOSO) in CSV; median-seed skill table + two-sided Wilcoxon (Holm) vs persistence, same format as RF (R12).
- dependencies: Colab T4 | allowed_paths: `results/`
- test_evidence: 7/27 runs on Drive. Fold A median RMSE 1h 0.749 (persistence 0.845, RF-8 0.765); fold B seed 0 0.672 (persistence 0.640) — watch.
- risks: Colab resets (3 so far); ~28 min/run, ~10 h left.
- last_update: 2026-11-21 (Leader): resumed on Colab with T10 code (3a4ad2b); 42 earlier 8-fold files renamed on Drive to `globalW8_*`/`losoW8_*`; Drive snapshot `*_4fold/` taken first.

## T10 — LOSO file names tagged by site set (M09) — light task
- owner: worker | priority: P0 | status: DONE | attempt_count: 1
- goal: 8-site global/LOSO runs no longer overwrite 4-site model/pred files.
- scope: in `scripts/09_global_loso.py`, prefix model files (`models_loso/`) and pred files (`preds_loso/`) with `st + "8"` when `--sites` has 8 sites (e.g. `losoW8_A_Mamba_0.pt`, `globalW8_ALL_Mamba_0.pt`), other site sets unchanged. The CSV `strategy` column and the skip key stay exactly as now. In `notebooks/colab_resume.py`, re-add T01, and T04b with `--sites A,B,C,D,E,F,G,H --pattern losoW8_{site}_{model}_{seed}.pt --tag losoW8`.
- acceptance_criteria: (1) with 4 sites the names are unchanged; with 8 sites they carry `8`; the CSV `strategy` values are unchanged in both; (2) CPU smoke `py scripts/09_global_loso.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 1 --epochs 1 --max-batches 2 --features wind --out <scratch>/loso8.csv` writes `losoW8_*`/`globalW8_*` files and `strategy` = `globalW`/`losoW`; (3) diff ≤ ~15 lines in ≤ 2 files.
- allowed_paths: `scripts/09_global_loso.py`, `notebooks/colab_resume.py`
- test_evidence: QA PASS 2026-11-21 (qa: 4-site names unchanged, 8-site `globalW8_*`/`losoW8_*`, CSV strategy unchanged, skip key works; CPU smoke wrote `globalW8_*`; diff 7 lines in 2 files).
- last_update: 2026-11-21 (Leader): approved on QA PASS (light task), merged `e124620` from 2be4970; worktree removed.

## T02 — Few-shot scratch, fixed step budget
- owner: Leader (Colab) | priority: P1 | status: IN_PROGRESS (QA FAIL round 1) | attempt_count: 1
- goal: fair from-scratch baseline for E9 (M07).
- scope: `scripts/18_fewshot.py --sites A,B,C,D --models Mamba --seeds 3 --modes scratch --scratch-steps 2000 --out results/fewshot_scratch2.csv`
- acceptance_criteria: 72 runs (4 sites × 2 windows × 3 weeks × 3 seeds); table vs finetune (`fewshot.csv`), RF (`fewshot_rf.csv`), persistence.
- qa: FAIL 2026-11-21 (QA-T02-01 high: scratch 1.4–3.3 m/s vs Ridge 0.61–0.83 on the same k weeks, not explained by range coverage; suspects constant month_* and unscaled LR patience; QA-T02-02 low: window drops the 23:45 sample) -> meeting M12.
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

## T11 — Few-shot code fixes (M11 + M12) — light task
- owner: worker | priority: P0 | status: DONE | attempt_count: 2
- goal: fair few-shot baselines plus an 8-fold init option.
- scope:
  - (a) `run_nn` gets `sched_patience=3`; the default keeps E1/LOSO identical. `18_fewshot.py` passes the step-scaled value (`ceil(patience_steps / steps_per_epoch)`) for both finetune and scratch.
  - (b) `--init-tag` (default `losoW`) selects the finetune init file.
  - (c) `--const-calendar` holds `month_sin`/`month_cos` at their window value in a copy of `X`; the input dimension is unchanged.
  - (d) `--modes ridge`: sklearn Ridge on `d.flat`, same k weeks.
  - (e) the k-week window includes its end sample (23:45, QA-T02-02).
- acceptance_criteria:
  - defaults reproduce the current behaviour (same file names; scheduler patience 3 in E1/LOSO);
  - the CPU smoke `py scripts/18_fewshot.py --sites A --models Mamba --seeds 1 --weeks 1 --modes ridge,scratch --scratch-steps 50 --out <scratch>/fs.csv` (check `-h` first) runs and writes rows;
  - Ridge RMSE 1h at A DB 1w ≈ 0.83;
  - diff ≤ ~50 lines in 2 files.
- allowed_paths: `scripts/07_run_benchmark.py`, `scripts/18_fewshot.py`
- test_evidence:
  - round 1 QA PASS (c0e2a0d): defaults unchanged; stubbed NN run got `sched_patience` 40 (1w) / 10 (4w); Ridge A DB 1w RMSE 1h 0.8206; const-calendar copies and restores X; diff 19+/6− in 2 files.
  - QA found two more bugs: QA-T11-02 (high, pre-existing: resume crashed on `prev.mode`) and QA-T11-01 (low: TN window ended on Jul 1 00:00). Both fixed in e54f35d.
  - round 2 QA PASS: re-runs print skips; DB and TN windows each hold 672 samples ending at 23:45.
  - Real NN training was only stubbed; it will be checked by the Colab pilot.
- last_update: 2026-11-21 (Leader): approved on QA PASS (light task); merged `80f0081`.

## T12 — Few-shot A–H with the 8-fold init (M11)
- owner: Leader (Colab) + worker (RF, CPU) | priority: P1 | status: TODO | attempt_count: 0
- scope: `18_fewshot.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 3 --modes finetune,scratch --scratch-steps 2000 --init-tag losoW8 --out results/fewshot8.csv`; RF: `--modes rf --out results/fewshot8_rf.csv` (CPU).
- acceptance_criteria: 144 runs per mode; median-seed table vs persistence; Wilcoxon (n = 8, Holm) finetune vs persistence and vs scratch/RF.
- dependencies: T01, T10, T11, T02 QA | last_update: 2026-11-21
