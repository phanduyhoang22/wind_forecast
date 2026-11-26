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

- 2026-11-25 (M13, Director under User delegation): transfer claim from R21 = LOSO-W beats persistence significantly at 1h only; 3h/6h positive, not significant; Mamba vs RF-W not significant (Holm 0.117). Primary test: two-sided exact Wilcoxon on per-site skill of the median-seed RMSE, RMSE-difference also reported. Per-seed table, climatology scaling, A/D tuning and RF depth 16 disclosed. No extra seeds. Replaces the M03 framing.

- 2026-11-25 (User): agents meet and approve on the User's behalf: the Leader records the Director approval after QA PASS and merges without waiting. Paid, public (beyond the usual repo push) or irreversible actions still need the User. The chat continues until the User asks for a handoff.

- 2026-11-25 (M14, Director under User delegation): few-shot statistics frozen before completion: primary = finetune FREE vs oracle best-of {scratch, Ridge, RF, all const-calendar}, mean skill over 6 cells, Wilcoxon n = 8, Holm over 3 horizons; the rest secondary or descriptive (MEETINGS M14). Per M12, finetune free is main and const is the ablation. No "k weeks only" wording.

- 2026-11-25 (M16, under User delegation): few-shot claim from R25 + R26, no new runs: beats k-week from-scratch references (below persistence) in both protocols; no consistent gain over zero-shot; vs persistence significant only with target validation. Conditions (1)–(6) in MEETINGS M16 bind T08. The confound-control run stays in the backlog.

- 2026-11-27 (M17, User): T07 option A: regenerate RF A-D val preds on CPU, gated by a seed-0 reproducibility check (no mixing of old test and new val preds); `11_conformal.py` reports missing pairs and fails on them; exact k-th order statistic; PINAW denominator = train-target range; RESULTS correction row for R29 + sklearn version.

## Colab queue (2026-11-21 ~13:30 UTC, live)
- Main chain (restarted 2026-11-21 12:2x UTC on commit 3a4ad2b): T01 → T03a (13/40 done before the restart) → T03b → T04a → T04b (`losoW8`) → T05 (PatchTST A–H) → `results/all.done`. T02 is finished (72/72) and was removed from the chain. At 12:57 UTC T01 was 9/27.
- Estimated GPU left: T01 ~8.5 h, T03 ~3.5 h, T04 ~1.5 h, T05 ~9 h.
- Runtime reset between 14:42 and 14:54 UTC: the unsynced pilot in `/content/pilot` was lost. Restarted at ~14:56 UTC (commit d7a94c2) with T01 at 12/27.
- Side job: the M12 pilot now runs in the main clone and is synced to Drive. It runs `18_fewshot.py --sites A,B,C,D --seeds 1 --modes scratch --scratch-steps 2000`, writing `results/pilot_free.csv` and then `results/pilot_const.csv` (`--const-calendar`), with `results/pilot.done` and `results/pilot.log`. Compare `val_best` only and pick the `month_*` handling. Partial test RMSE seen before the reset (not for selection): free A 1.14–1.51, B 2.0–2.9, C 1.6–2.0, D 2.0–2.7; const A 0.82–1.15, B 0.83–1.72.
- 2026-11-22 ~17:55 UTC: pilot v1 finished, but it is unusable for selection (no `val_best`). After the T13 merge, pilot v2 was started in the main clone. Only `scripts/18_fewshot.py` was refreshed from origin/main, because `git pull` fails on the shallow clone; do NOT `git reset --hard` there, it would overwrite the result CSVs. It writes `results/pilot2_free.csv` / `pilot2_const.csv`, then `pilot2.done` (also on Drive). Select on `val_best` only.
- 2026-11-24 ~09:30 UTC: runtime was dead (notebook empty). Restarted from the setup cell (commit 1644c64): `loso8_wind.csv` 120 rows (T01 at 19/27), `runs_wind.csv` 39 rows (T03a 13/40), `pilot2.done` present so pilot skipped. CPU side job started locally: `18_fewshot.py --sites A..H --seeds 3 --modes ridge,rf --const-calendar --out results/fewshot8_cpu_cc.csv` (T12).
- The setup cell must also restart the pilot until `pilot2.done` exists (see the cell in the MCP notebook; the runner file has no pilot).
- Runner: `notebooks/colab_resume.py`. Paste the setup cell into the empty MCP notebook; it re-clones, restores results from Drive, skips finished keys, and starts the chain plus the Drive sync. The runner still lists T02; it is skipped because all its keys are done.
- Resume in a new chat:
  1. `open_colab_browser_connection`, then `get_cells`.
  2. If the cells still exist, run the status cell. If the notebook is empty, paste the setup cell and run it.
  3. Keep the runtime alive every ~15 min (background `sleep 840` timer, then run the status cell).
  4. On GPU loss or `all.done`: commit + push, then `shutdown /s /t 600`.
  - Stale-output check: if the printed time does not change, check the Drive `results/run.log` modifiedTime.
- 2026-11-24 ~13:05 UTC: T01 finished; chain on T03a (14/40). T12 GPU side job started in parallel (cell 3): finetune+scratch `--const-calendar` -> `fewshot8_cc.csv`, then finetune free -> `fewshot8_ft_free.csv`, then `t12.done` (also on Drive). Restart it if lost (skips finished keys).
- 2026-11-24 17:36 UTC (2026-11-25 local): runtime was dead since ~14:08 UTC, restarted on e8b19dd: T03a at 22/40, T12 `fewshot8_cc.csv` at 129 rows, both resumed (T4, 84 %). MCP notebook: cell 1 clones the repo to `/content/_runner` and exec-s `notebooks/colab_resume.py`, then starts T12; cell 2 = status.
- 2026-11-24 22:34 UTC: last Drive sync; at 22:49–22:59 UTC the status cell and a ping cell hung, no new sync, re-running the setup cell had no effect. Treated as runtime lost (not proven: MCP cells gave no output). State at the last live check (22:32 UTC): T04 SHAP running, `fewshot8_cc.csv` 864/864, `fewshot8_ft_free.csv` 180/432 rows, T16 waiting for `t12.done`, PatchTST (T05) not started. Resume: reconnect MCP, new runtime + Drive consent, run cell 1 (setup + T12), then cell 3 (T16, source below in HANDOFF), then cell 2. Handoff + shutdown per the User rule.
- 2026-11-25 03:35 UTC: reconnected (empty notebook, T4, commit eb4e17c). Restarted: chain at T04a SHAP, T12 `fewshot8_ft_free.csv` 195/432, T16 waiting for `t12.done`. Cells: 1 = setup + T12, 2 = T16, 3 = status.
- 2026-11-25 13:55 UTC: runtime was lost after the 05:06 UTC Drive sync; reconnected (empty notebook, T4, commit 4eb5f54). T16 runs complete (432/432 both files). T04a skipped (both CSVs on Drive have 8 sites); restarted: T04b from A, then T05 (PatchTST 7/40). Cells: 1 = setup, 2 = status.
- 2026-11-26 ~01:20 UTC: reconnected (empty notebook, T4, commit 6807cab). Drive check: all result CSVs end with newline and match the clone; E1 models/preds 5 seeds × A–H for DLinear/LSTM/Mamba/Transformer, RF preds A–H; PatchTST A–C 5 seeds, D 1 (16/40, `runs.csv` 528 rows on Drive vs 501 in git); `models_wind`/`preds_wind` 40; losoW8 24 + globalW8 3 models, 24 + 24 preds; 16 SHAP npz finite. Chain killed at T04a (no skip in `10_shap.py`), T05 started alone. Cells: 1 = setup, 2 = status, 3 = scratch check.
- Never `cp` the clone's `models_loso/`/`preds_loso/` onto Drive by hand after a rename (cp -u re-creates old names); the Drive snapshot `models_loso_4fold/`, `preds_loso_4fold/` is frozen.

## T01 — Mamba-W LOSO 8-fold
- owner: Leader (Colab) | priority: P0 | status: DONE | attempt_count: 1
- goal: zero-shot transfer of Mamba (wind-only) to each of 8 unseen sites; enables Wilcoxon n = 8.
- scope: `scripts/09_global_loso.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 3 --features wind --out results/loso8_wind.csv`
- inputs: `data_v2/*.npz`, `results/tuned.json` | expected_outputs: `results/loso8_wind.csv`, `results/models_loso/losoW_*`
- acceptance_criteria: 27 runs (3 global + 24 LOSO) in CSV; median-seed skill table + two-sided Wilcoxon (Holm) vs persistence, same format as RF (R12).
- dependencies: Colab T4 | allowed_paths: `results/`
- test_evidence: 7/27 runs on Drive. Fold A median RMSE 1h 0.749 (persistence 0.845, RF-8 0.765); fold B seed 0 0.672 (persistence 0.640) — watch.
- risks: Colab resets (3 so far); ~28 min/run, ~10 h left.
- 2026-11-24 (Leader): 27/27 runs done 13:0x UTC (144 rows on Drive). Run R21: LOSO beats persistence 8/8 at 1h (Holm p 0.023); 3h/6h p 0.078. Next: qa recomputes the table from the CSV; then meeting (result beats RF-W R16 and changes the transfer claim).
- 2026-11-25 (qa, on e8b19dd): PASS. 144 rows complete, losoW leak-free, R21 reproduced except globalW 6h (R21c). Caveats: target MinMax from its own train slice, A/D used for tuning, sign flips by seed at B, D 1h, H 3h/6h; D 3h/6h negative; not better than RF-W after Holm. Not verified: RMSE from saved preds. Next: meeting M13.
- 2026-11-25 (Leader): correction. The Leader chat had recorded a Director APPROVE here; the 2026-11-24 delegation covers meeting decisions (M13), not task approval. Back to APPROVAL_PENDING until a Director chat or the User approves.
- last_update: 2026-11-21 (Leader): resumed on Colab with T10 code (3a4ad2b); 42 earlier 8-fold files renamed on Drive to `globalW8_*`/`losoW8_*`; Drive snapshot `*_4fold/` taken first.
- 2026-11-25 (Director, under User delegation of 2026-11-25): APPROVE on QA PASS.

## T10 — LOSO file names tagged by site set (M09) — light task
- owner: worker | priority: P0 | status: DONE | attempt_count: 1
- goal: 8-site global/LOSO runs no longer overwrite 4-site model/pred files.
- scope: in `scripts/09_global_loso.py`, prefix model files (`models_loso/`) and pred files (`preds_loso/`) with `st + "8"` when `--sites` has 8 sites (e.g. `losoW8_A_Mamba_0.pt`, `globalW8_ALL_Mamba_0.pt`), other site sets unchanged. The CSV `strategy` column and the skip key stay exactly as now. In `notebooks/colab_resume.py`, re-add T01, and T04b with `--sites A,B,C,D,E,F,G,H --pattern losoW8_{site}_{model}_{seed}.pt --tag losoW8`.
- acceptance_criteria: (1) with 4 sites the names are unchanged; with 8 sites they carry `8`; the CSV `strategy` values are unchanged in both; (2) CPU smoke `py scripts/09_global_loso.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 1 --epochs 1 --max-batches 2 --features wind --out <scratch>/loso8.csv` writes `losoW8_*`/`globalW8_*` files and `strategy` = `globalW`/`losoW`; (3) diff ≤ ~15 lines in ≤ 2 files.
- allowed_paths: `scripts/09_global_loso.py`, `notebooks/colab_resume.py`
- test_evidence: QA PASS 2026-11-21 (qa: 4-site names unchanged, 8-site `globalW8_*`/`losoW8_*`, CSV strategy unchanged, skip key works; CPU smoke wrote `globalW8_*`; diff 7 lines in 2 files).
- last_update: 2026-11-21 (Leader): approved on QA PASS (light task), merged `e124620` from 2be4970; worktree removed.

## T02 — Few-shot scratch, fixed step budget
- owner: Leader (Colab) | priority: P1 | status: CANCELLED (superseded) | attempt_count: 1
- goal: fair from-scratch baseline for E9 (M07).
- 2026-11-26 Leader: closed as superseded. The QA-T02-01/-02 FAIL led to M12; fixes in T11, rerun A–H in T12/T16 (R25, R26; claim frozen in M16). `fewshot_scratch2.csv` stays as the disclosed invalid-baseline row (R18).
- scope: `scripts/18_fewshot.py --sites A,B,C,D --models Mamba --seeds 3 --modes scratch --scratch-steps 2000 --out results/fewshot_scratch2.csv`
- acceptance_criteria: 72 runs (4 sites × 2 windows × 3 weeks × 3 seeds); table vs finetune (`fewshot.csv`), RF (`fewshot_rf.csv`), persistence.
- qa: FAIL 2026-11-21 (QA-T02-01 high: scratch 1.4–3.3 m/s vs Ridge 0.61–0.83 on the same k weeks, not explained by range coverage; suspects constant month_* and unscaled LR patience; QA-T02-02 low: window drops the 23:45 sample) -> meeting M12.
- test_evidence: pilot A/1 week: RMSE 1h 1.72 (DB) / 1.88 (TN) — overfits, not under-trained.
- last_update: 2026-11-21 (Leader): 72/72 runs done on Colab 10:4x UTC, Drive `results/fewshot_scratch2.csv`; run log RMSE 1h 1.2–3.4 (still far above persistence). Next: comparison table vs finetune/RF/persistence + qa.

## T03 — E1-W Mamba 8 sites + cross-site 8×8 (W)
- owner: Leader (Colab) | priority: P1 | status: DONE | attempt_count: 0
- scope: `07_run_benchmark.py --sites A..H --models Mamba --seeds 5 --features wind --out results/runs_wind.csv`; then `16_cross_eval.py --sites A..H --models Mamba --seeds 3 --features wind --out results/cross_eval_wind.csv`
- acceptance_criteria: 40 E1-W runs; 8×8 W matrix with same-/cross-regime split; compare to 31-feature versions.
- last_update: 2026-11-21
- 2026-11-25 (Leader): T03a 40/40 and T03b finished ~20:17 UTC on Colab; `runs_wind.csv`, `cross_eval_wind.csv` (and `cross_eval_nn.csv`, R09) copied from Drive to the repo. qa next.
- 2026-11-25: qa PASS on c4dffed (R22–R24). Claims allowed: W costs 1.9–3.9 pp at the own site (1h depends on seed aggregation); W gains 9–11 pp cross-regime; same-regime gain n.s.; W transfer n.s. vs persistence. Not verified: per-sample DM for E1-W (T06), GPU re-run. Director APPROVE under User delegation.

## T04 — SHAP (Mamba-31 per site, Mamba-W LOSO)
- owner: Leader (Colab) | priority: P2 | status: DONE | attempt_count: 2
- scope: `10_shap.py --sites A..H --model Mamba --seed 0`; `10_shap.py --sites A,B,C,D --models-dir results/models_loso --pattern losoW_{site}_{model}_{seed}.pt --features wind --tag losoW`
- acceptance_criteria: `shap_importance_*.csv`, `shap_temporal_*.csv`; completeness error reported.
- last_update: 2026-11-21
- 2026-11-25 14:36 UTC (Leader): T04a and T04b runs finished on Colab (8/8 sites each). `shap_{importance,temporal}_Mamba_0.csv` copied from Drive; losoW8 CSVs copied too. Not QA'd. `results/runs.csv` in git is a snapshot (PatchTST 7/40); the live file is on Drive.
- scope correction: T04b = `losoW8`, A–H (M09); the A–D / `losoW_` line above is superseded.
- Leader-reported (Colab, 2026-11-25 14:44 UTC): 16/16 npz finite, CSV vs npz max relative gap 2.6e-04; completeness error T04b A–H 0.085 0.079 0.076 0.069 0.079 0.073 0.066 0.072.
- 2026-11-25 qa FAIL on d656f18: QA-T04-01 HIGH (T04a completeness missing for A, E, F, G, H). CSVs, splits, method, LOSO code PASS. Claim limits: -03 cancellation (sum |phi| 4–13x the target deviation), -04 correlated heights/grouping artefact, -05 preregistered RF TreeSHAP and air_density control not done / not valid, -06 calendar share; -02 checkpoint provenance unverified; -07 docs. One seed only: no stability claim.
- round 2 (worker): new `scripts/25_shap_check.py`, no SHAP re-run. From npz + checkpoints, forward passes only: rebuild the seed-0 background exactly as `10_shap.py`; write `results/shap_completeness.csv` (tag, site, horizon incl. pooled "all", completeness_error, n) for both tags and 8 sites; `results/shap_net_importance.csv` (tag, site, horizon, feature, mean |sum over t of phi|, share, rank); compare fx (inverse-scaled) with the stored prediction files of E1 and losoW8 seed 0 at the same test positions (max and mean abs diff, m/s) into `results/shap_provenance.csv`.
- acceptance (round 2): `--selftest` with asserts (known attribution gives ~0 error, perturbed attribution gives the expected error, missing npz/checkpoint fails loudly and writes nothing); pooled definition identical to `10_shap.py`; CPU only; existing files unchanged; runs on Colab with `--results <dir>`; allowed_paths: `scripts/25_shap_check.py`, the three CSVs. Then Leader runs on Colab, qa.
- round 2 worker: `6314178` (script), Colab run `20bb21c` (Drive `results/shapchk/`). Recorded late by the Leader on 2026-11-26 (previous shift did not log it).
- 2026-11-26 qa PASS on 20bb21c (run R27): selftest exit 0; 64/1200/16 rows complete and finite; pooled definition identical; losoW8 matches the 10_shap log to 3 decimals. NOT_VERIFIED: CPU recompute (no npz/checkpoints locally), Colab run itself. Findings: QA-T04-08 LOW provenance max diff 0.009–0.018 m/s, no negative control (fp16 autocast likely); QA-T04-09 top-1 feature changes under net importance (no "ws_200m dominates" claim); QA-T04-10 INFO missing preds -> `status=missing`. Claim limits -03..-07 still bind T08.
- 2026-11-26 (Director, under User delegation of 2026-11-25): APPROVE on QA PASS. Leader merged `d406f57`. status: DONE.
- 2026-11-26 (Leader, Colab, closes two NOT_VERIFIED items, run R27c): (1) negative control for QA-T04-08: stored preds seed 0 vs seed 1 differ by mean 0.21–0.38 m/s (max 2.6–5.9) for E1 and losoW8 A–H, ~100x the provenance mean diff (<= 0.0032) -> provenance consistent with the seed-0 checkpoints. (2) Independent recompute of `25_shap_check.py` on `918d299`, `--device cpu`, sites A and H, both tags, vs Drive `shapchk/`: 16/16 completeness rows (max diff 6.3e-08), 4/4 provenance (4.8e-06 m/s), 300/300 net-importance rows (0) match. Still not verified: the original SHAP npz themselves (GPU, not re-run).
- 2026-11-26 note: Drive `summary_by_site.csv`/`summary_overall.csv` have all `*_std` NaN and only 60 rows (stale aggregate); do not use, T06 regenerates them.
- 2026-11-26 note: `10_shap.py` has no skip of finished sites; the Colab chain re-ran T04a on restart. The Leader killed it before any npz was written and restarted T05 alone. Do not put `10_shap.py` back in the chain.

## T05 — PatchTST E1 to 40/40 (A–H, M10)
- owner: Leader (Colab) | priority: P2 | status: DONE | attempt_count: 1
- 2026-11-27 Leader: Director APPROVE (`5f8790d`) -> DONE. Work already on main (`5fc2cc9`, no worker branch to merge). F-T05-01 stays open (blocks SHAP numbers in T08).
- 2026-11-27 Leader F-T05-01 evidence: Drive `results/shapchk_F-T05-01/run.log` ends `exit=0`, `0 file du doan luu bi thieu`; pooled completeness on the current npz, E1 A-H `0.094/0.072/0.073/0.064/0.087/0.082/0.072/0.066`, losoW8 A-H `0.085/0.079/0.076/0.069/0.079/0.073/0.066/0.072` = R27 exactly (3 decimals); provenance mean <= 3.18e-03 m/s (as R27). Full CSV diff vs repo R27 CSVs NOT_VERIFIED -> next Leader runs it, then qa closes F-T05-01.
- scope: `07_run_benchmark.py --sites A,B,C,D,E,F,G,H --models PatchTST --seeds 5 --out results/runs.csv` (M10, 2026-11-21; Drive 7/40 done: A 5, B 2).
- acceptance_criteria: 40 PatchTST runs ×3 horizons in `runs.csv`; fallback if the GPU runs out: A–D 20/20 with a common-site average and disclosure (M10).
- 2026-11-26 09:49 UTC Leader: runtime reset, restarted via setup cell (commit `01950ac`); Drive check 09:52 UTC: runs.csv 537 rows, PatchTST A–C 15, D 12, E–H 0 (19/40); all 67 result CSVs match clone, end with newline; 16 SHAP npz finite, dated 2026-11-25.
- acceptance_criteria (HANDOFF 2026-11-26 §7, mandatory for qa; each run with real output, not run -> NOT_VERIFIED): (1) Drive `results/runs.csv`: PatchTST 15 rows for each of A–H (120), other models 15 per site, file ends with newline; (2) `py scripts/24_shift_check.py --full`: 0 FAIL, every WARN / NOT_VERIFIED read; (3) Drive `results/shap_*.npz` modifiedTime unchanged (2026-11-25).
- 2026-11-26 Leader (new shift): `24_shift_check.py --full` -> `65 PASS, 0 WARN, 0 FAIL, 2 NOT_VERIFIED` (runs.csv key table; Colab drive status).
- 2026-11-27 Leader: shift check `65 PASS, 0 WARN, 0 FAIL, 2 NOT_VERIFIED`; Drive `run.log`/`runs.csv` last modified 2026-11-26T17:08Z (runtime presumed lost, 38/40: H seeds 3-4 missing); MCP notebook empty, status cell never returned. User: "ngừng colab" -> Colab work paused, setup cell NOT re-run. T05 stays IN_PROGRESS (38/40).
- 2026-11-27 Leader Drive check (data intact): `runs.csv` 597 rows, ends with newline; DLinear/LSTM/Mamba/Transformer 15 per site A-H; PatchTST A-G 15, H 12 (38/40 + seed 2 partial rows? 12 = 4 seeds x 3 horizons). 64 result CSVs present (last sync 2026-11-26T17:08Z); 16 SHAP npz present. Local repo: `data_v2` 8 npz, `results/runs.csv` 501 rows (Drive copy not pulled yet).
- FINDING F-T05-01 (Leader, 2026-11-27, open): Drive `shap_Mamba_0_{A,B,C,D}.npz` modifiedTime = 2026-11-26T01:34/01:54/02:09/02:24Z, not 2026-11-25 (E-H and all losoW8 npz: 2026-11-25). Timing matches the T04a re-run after the 01:20 UTC reconnect, so the note "killed before any npz was written" (above) and the 09:52 UTC check "dated 2026-11-25" look wrong: A-D E1 SHAP npz were recomputed. Same script/seed/checkpoints, and R27/R27c were checked on 2026-11-26 data, so numbers likely unchanged, but HANDOFF check (3) does not hold as written. Needs qa: compare R27 CSVs against the current npz (25_shap_check.py) before T08 uses SHAP numbers.
- 2026-11-26 18:03 UTC (2026-11-27 01:03 local) Leader: Colab `[40/40] H PatchTST seed=4 1229s ep=33 | 1h RMSE=0.7720 3h RMSE=1.3266 6h RMSE=1.7178`, `all.done`. runs.csv copied to Drive explicitly, then Drive -> repo `results/runs.csv`: 600 rows, ends with newline, every (model, site) = 15 for 5 NN models x A-H, 0 duplicate keys, 0 NaN in RMSE/MAE/R2; the 501 old git rows match exactly (max RMSE diff 0.0); git diff = 99 insertions, 0 deletions. State -> WORKER_DONE, awaiting qa.
- 2026-11-27 qa PASS on 5fc2cc9 (Leader recorded): repo runs.csv 600x13, 15 rows per (model, site), identical to the Drive blob after CR strip (sha256 8ebaa48f...); diff +99 only; 0 dup keys, 0 non-finite; RMSE 1h<3h<6h in 40/40; `24_shift_check.py --full` 62 PASS / 3 WARN (qa detached checkout, qa worktree, handoff age) / 0 FAIL / 2 NOT_VERIFIED; `08_aggregate.py --selftest` dat. NOT_VERIFIED: Drive side itself, SHAP npz modifiedTime (F-T05-01 open). Findings: QA-T05-01 LOW (shift check has no runs.csv key table); QA-T05-02 LOW (12/120 PatchTST rows hit the 50-epoch cap, 3 with best_epoch = epochs); QA-T05-03 LOW (PatchTST worse than persistence at 1h for D, H: disclose). State -> QA_PASSED, awaiting Director.
- 2026-11-27 Leader: F-T05-01 check started on Colab: `25_shap_check.py --results <Drive results> --out-dir <Drive>/results/shapchk_F-T05-01` (log `run.log` there); next: compare its 3 CSVs with repo `results/shap_{completeness,net_importance,provenance}.csv` (R27).
- 2026-11-27 Director: APPROVE. Reason: core criterion met (40 PatchTST runs x 3 horizons, runs.csv 600 rows, qa PASS on 5fc2cc9, already on main). HANDOFF check (3) (SHAP npz modifiedTime) does not concern PatchTST output; it moves to F-T05-01, which stays open and gates any SHAP number used in T08 (compare shapchk_F-T05-01 CSVs with R27). Conditions carried to T08 (paper): disclose QA-T05-02 (12/120 rows at 50-epoch cap) and QA-T05-03 (PatchTST below persistence at 1h for D, H). QA-T05-01 (runs.csv key table in shift check) -> Leader backlog. Leader: set DONE.
- last_update: 2026-11-27

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
- 2026-11-27 Leader contract: owner Leader (Colab; NN val/test preds live only on Colab/Drive, local has RF val only). No code change.
  - command: `cd /content/wind_forecast && python scripts/11_conformal.py --selftest` then `python scripts/11_conformal.py --models Mamba,LSTM,Transformer,PatchTST,DLinear,RF` -> `results/conformal.csv`, copied to Drive and repo.
  - 2026-11-27 Leader ran on Colab (R29, commit 549bfec): 1320 rows; RF E-H only (no RF val npz for A-D). attempt_count 1.
  - 2026-11-27 qa round 1 FAIL on criterion (2) only (1320/1440, script skips missing pairs silently, lines 83, 86-87); (1),(3),(4),(5) PASS; RF E-H recompute exact (max diff 1e-16); NN rows NOT_VERIFIED (no local preds); shift check 61 PASS / 4 WARN (qa checkout, origin behind 1, qa worktree, handoff age) / 0 FAIL / 2 NOT_VERIFIED. Findings: QA-T07-01 MED (row gap + silent skip); QA-T07-02 LOW (`np.quantile(method="higher")` one order statistic conservative, negligible); QA-T07-03 LOW (PINAW normalised by test-target range: disclose or use train range); QA-T07-04 INFO (PICP ~0.875 vs 0.90, high-wind tercile worst: NN -0.04..-0.05, RF -0.09; worst sites G, H: no "nominal coverage" claim in T08). State -> REVISE pending decision: (a) regenerate RF A-D val preds (CPU, one site at a time) + print missing pairs, or (b) accept RF E-H as disclosed deviation; either way fix QA-T07-02/03 as a light task.
  - ROUND 2 contract (M17 option A, 2026-11-27), owner worker (CPU part) then Leader (Colab re-run of 11):
    - goal: RF val preds for A-D, `11_conformal.py` fixes, conformal.csv with 1440 rows.
    - allowed_paths: `scripts/11_conformal.py`, `results/models/{A,B,C,D}_RF_{0..4}_val.npz` (new files only), scratch dir outside repo. Never write `results/preds/`, `results/runs_rf.csv`, `results/conformal.csv` (Leader re-runs 11 on Colab).
    - steps: (1) `py scripts/07_run_benchmark.py --models RF --sites A --seeds 1 --out <scratch>/runs.csv`; `np.array_equal(<scratch>/preds/A_RF_0.npz y_pred, results/preds/A_RF_0.npz y_pred)` and node count == runs_rf.csv params; mismatch -> STOP, report, no copy. (2) match -> one site per command, seeds 5, A-D; check every seed's test preds equal existing; copy only `*_val.npz` to `results/models/`. (3) `11_conformal.py`: list missing (site, model, seed) pairs and exit non-zero if any expected pair missing; exact k-th order statistic k = ceil((n+1)(1-a)) (clip at n); PINAW denominator = train-target range (`d.y_raw[d.idx_train]` per horizon); `--selftest` asserts both (residuals 1..19, a 0.1 -> q 18). (4) record sklearn version.
    - acceptance_criteria (round 2): (a) 20 new RF val npz A-D, shapes = y_val; (b) 20/20 re-run test preds array_equal to existing; (c) selftest passes incl. new asserts; (d) diff limited to allowed_paths; (e) Leader Colab re-run -> 1440 rows, no missing pairs, finite, PICP in [0,1]; RESULTS correction row for R29 + new row; (f) HANDOFF checks: Drive runs.csv 600 rows 15 per (model, site) + newline; `py scripts/24_shift_check.py --full` 0 FAIL, every WARN/NOT_VERIFIED read; Drive shap npz modifiedTime as in HANDOFF section 7 item 4.
  - acceptance_criteria: (1) selftest prints PICP ~0.900 "dat"; (2) conformal.csv rows = 8 sites x 6 models x 5 seeds x 2 alphas x 3 horizons = 1440 (missing preds listed, not silently skipped); (3) PICP/PINAW finite, PINAW > 0, PICP in [0,1]; (4) calibration on val only, test untouched (code read); (5) RESULTS row with run_id; (6) HANDOFF section 7 checks: Drive runs.csv PatchTST 15/site A-H (120) + others 15/site + newline; `py scripts/24_shift_check.py --full` 0 FAIL, every WARN/NOT_VERIFIED read; Drive shap_*.npz modifiedTime (2026-11-25 expected; open finding F-T05-01 for A-D).
- last_update: 2026-11-27

## T08 — Paper: Results & Discussion draft
- owner: worker | priority: P1 | status: TODO | attempt_count: 0
- scope: `docs/paper/section3_results.md`; Section 2 draft exists (`docs/paper/section2_data_methods.md`).
- dependencies: T06 (experiments frozen) | allowed_paths: `docs/paper/`
- carry-over: fix QA-T08b-08/-09 (see T08b); Section 2.6 R22/R23 TODO -> cite `scripts/26_feature_set_stats.py` (T19), same-cross 6h 17.9 (R23e), note exact Wilcoxon n=8 p floor (Holm 0.023).
- last_update: 2026-11-21

## T08a — Paper: Results draft for the frozen parts (transfer, few-shot, SHAP) — split from T08
- owner: worker | priority: P1 | status: DONE | attempt_count: 1 | created: 2026-11-26 (Leader; T05 still running, so E1/T06/T07 parts wait)
- goal: draft the Results subsections whose experiments are finished and whose claims are fixed by meetings, so T08 only adds E1, regimes and conformal later.
- scope: new file `docs/paper/section3_results_transfer.md` with subsections: (a) zero-shot transfer, LOSO 8-fold (R21, R21c; M13); (b) cross-site 8×8 and wind-only set W (R22–R24); (c) few-shot adaptation (R25, R25c, R26; M14, M15, M16 conditions (1)–(6)); (d) explainability, SHAP (R27 and the T04 claim limits QA-T04-03..-09). Tables built from the committed result CSVs (`results/transfer_stats.csv`, `transfer_per_site.csv`, `cross_eval_wind.csv`, `fewshot8_stats.csv`, `fewshot8_iv_stats.csv`, `shap_*.csv`), plus a short "Disclosed deviations" list for these parts.
- inputs: `tasks/RESULTS.md`, `tasks/MEETINGS.md` (M13–M16), `tasks/STATUS.md` (T01, T03, T04, T12, T16, T18 entries), `docs/paper/section2_data_methods.md` (style, terms, notation), `docs/limitations_and_improvements.md`.
- acceptance_criteria:
  1. Every number in the text or tables traces to a RESULTS run_id or a committed CSV (cite the run_id in an HTML comment next to it); qa can recompute each from the CSV.
  2. Claims stay inside M13 (only 1h significant vs persistence; no Mamba > RF-W), M16 conditions (1)–(6) and the T04 limits (no "ws_200m dominates"; one seed, no stability claim; completeness error 6–12% stated; cancellation stated). Wording "Mamba ≈ Transformer" rule (M02) kept; data called "modelled", never "measurements".
  3. No new experiment, no new statistics code; reading CSVs with pandas to build tables is allowed (do not save scripts in the repo). Do not touch E1 per-site benchmark claims (T06 pending): mark them `[TODO T06]`.
  4. English, Markdown, terms and symbols consistent with Section 2; length ~1500–2500 words.
  5. Only `docs/paper/section3_results_transfer.md` is added or changed.
- HANDOFF mandatory checks: the current HANDOFF has no section 7; nothing extra to carry.
- allowed_paths: `docs/paper/section3_results_transfer.md`
- dependencies: T01, T03, T04, T12, T16, T18 (all DONE)
- 2026-11-26 worker: `9911e57` (212 lines, 54 source comments). Leader pre-check: only the allowed file.
- 2026-11-26 qa PASS on 9911e57: every table/text number recomputed from the CSVs (Wilcoxon + Holm independently, incl. R22/R23 p-values); claims inside M13, M16 (1)?(6), T04 limits; 2,357 body words + 347 deviations. NOT_VERIFIED: R25c "seed 1 n.s. vs zero-shot" (no per-seed CSV), upstream GPU runs. Findings LOW: -01 R27c not reflected; -02 R27 rounding (C 0.077 -> 0.076); -03 Section 2 conflicts only partly flagged; -04 some method constants without source comment.
- 2026-11-26 (Director, under User delegation of 2026-11-25): APPROVE on QA PASS. Leader merged `a56b751`, then fixed -01 and -03 in the draft and -02 with RESULTS row R27d (small doc changes). -04 left for T08. status: DONE.

## T08b — Paper: align Section 2 (Data & Methods) with the frozen designs — split from T08
- owner: worker | priority: P1 | status: DONE | attempt_count: 2 | created: 2026-11-26 (Leader)
- goal: Section 2 describes the designs actually run, so Methods and Results (`section3_results_transfer.md`) do not contradict each other.
- scope: edit `docs/paper/section2_data_methods.md`: (1) LOSO 8-fold, LOSO trains on 7 sites, global model on all 8 (M08, M09); (2) few-shot design as run: k-week windows (DB/TN, TN ends 30 June 2020 23:45 per `scripts/18_fewshot.py`), finetune free (main) / const calendar (ablation), scratch with fixed budget, Ridge and RF on k weeks, oracle best-of reference, target-validation and inner-validation protocols (M07, M11, M12, M14, M15, M16); (3) statistics: transfer = two-sided exact Wilcoxon on per-site skill of the median-seed RMSE, n = 8, Holm over horizons, RMSE difference also reported; DM kept only where it is used (E1) (M13, M14); (4) SHAP: expected gradients settings, completeness and provenance checks (R27, R27c). Then remove the matching `[TODO: update Section 2.5.3 ...]` / Section 2 TODOs in `docs/paper/section3_results_transfer.md` and add source comments for the method constants flagged by QA-T08a-04 (lines with max_depth 16, window ends, 20 %/120-sample gap, ~9 months, 1,000/200 windows).
- acceptance_criteria:
  1. Every design statement matches the code (`scripts/09_global_loso.py`, `18_fewshot.py`, `22_transfer_stats.py`, `23_fewshot_stats.py`, `10_shap.py`, `25_shap_check.py`) and the meeting decisions; cite file:line or Mxx in an HTML comment.
  2. No result numbers added to Section 2; no claim changed in Section 3 (only TODO removal and source comments).
  3. Post-hoc deviations stay disclosed (CLAUDE.md §8: coastal threshold 6.0→5.5 m/s; scratch step budget; M12 fixes).
  4. English, terms consistent between the two files; modelled data never called measurements.
  5. Only the two files change.
- allowed_paths: `docs/paper/section2_data_methods.md`, `docs/paper/section3_results_transfer.md`
- dependencies: T08a (DONE)
- 2026-11-26 worker: `70b6a36` on branch `worktree-agent-abfd31a775e2a64a4` (not merged). Pre-check: 2 allowed files only.
- 2026-11-26 qa FAIL round 1 on 70b6a36 (~45 citations all valid, no number wrong): QA-T08b-01 MED 2.6 Holm family "site × horizon" but `08_aggregate.py:107,137` use site × horizon × competitor (× seed); -02 MED 2.5.3 "frozen before any test score was used" hides the M12 pilot-v1 test-RMSE exposure (MEETINGS M12 follow-up 2026-11-22); -03 MED 2.6 pre-registration list claims E1 test statistics fixed before results, but M02 chose per-seed DM + paired t after E1 first pass; LOW -04 2.1 cross-ref should be 2.5.4; -05 Section 3.6 item 1 "4-fold design of Section 2.5.3" -> "originally planned"; -06 completeness notation (ratio of means) differs in 3.5; -07 provenance bullet: only explained-window idx is stored, background checked via RNG stream. Round 2 (same worker branch): text fixes only, allowed to touch the Section 3 references in -05/-06. Paused by User (token budget) 2026-11-26.
- 2026-11-26 ~10:00 Leader: round 2 resumed (User: continue). Worker spawned on a new worktree from `70b6a36`, findings QA-T08b-01..07 + criterion 6 (shift checks HANDOFF §7). attempt_count 2.
- 2026-11-26 worker round 2: `d36384a` (on merge `3d830f8` of `70b6a36`), 2 allowed files only (pre-check). qa PASS round 2 on d36384a: -01..-07 fixed, ~30 citations checked, criteria 1-5 PASS, 6b `24_shift_check --full` 0 FAIL, 6a/6c NOT_VERIFIED (Drive; Leader Drive check 09:52 UTC in T05). New LOW (to T08): QA-T08b-08 2.5.3 post-hoc list broken by the pilot disclosure sentences, reorder; -09 comment cites `README.md:106` for the free-calendar Ridge/RF run, cite RESULTS R20 instead. Risk noted: M01 DM lag chosen after pilot DM results (conservative). Director APPROVE (Leader, User delegation 2026-11-25). Merged `730cfc9`; worktrees removed.

## T08c — Paper: Section 2 carry-overs from T08b/T19 — light task
- owner: worker | priority: P1 | status: DONE | attempt_count: 2 | created: 2026-11-26 (Leader, User OK)
- goal: close the Section 2 carry-overs listed in T08 that do not depend on T05/T06.
- scope: in `docs/paper/section2_data_methods.md`: (a) QA-T08b-08: reorder the 2.5.3 post-hoc list so the pilot-disclosure sentences no longer break it; (b) QA-T08b-09: the comment citing `README.md:106` for the free-calendar Ridge/RF run cites RESULTS R20 instead; (c) 2.6 line with `[TODO: no committed script computes the R22/R23 p-values ...]`: replace the TODO with the method as computed by `scripts/26_feature_set_stats.py` (cite file:line), no result numbers in Section 2 (the 17.9 of R23e stays in Section 3 / RESULTS); (d) 2.6: state that with exact two-sided Wilcoxon and n = 8 the smallest attainable p is 2/256 ≈ 0.0078, i.e. 0.023 after Holm over three horizons; (e) 2.6: disclose that the M01 DM HAC lag max(h−1, 96) was chosen after pilot DM results were seen (conservative choice).
- acceptance_criteria:
  1. (a)–(e) done; every new design statement cites script:line or Mxx/RESULTS Rxx in an HTML comment, and the citation is correct.
  2. No result numbers added to Section 2 except the p floor of (d); no other text changed; English; modelled data never called measurements.
  3. Only `docs/paper/section2_data_methods.md` changes.
  4. HANDOFF 2026-11-26 §7 checks, each run with real output or marked NOT_VERIFIED: (i) Drive `results/runs.csv` PatchTST 15 rows per site A–H (NOT_VERIFIED expected: T05 running, 23/40 at 12:12 UTC); (ii) `py scripts/24_shift_check.py --full` -> 0 FAIL, read every WARN / NOT_VERIFIED; (iii) Drive `results/shap_*.npz` modifiedTime unchanged 2026-11-25.
- allowed_paths: `docs/paper/section2_data_methods.md`
- dependencies: T08b (DONE), T19 (DONE)
- 2026-11-26 worker round 1: `b7d1b87` (branch `worktree-agent-a6384682c2d58b03b`), 1 file (pre-check OK). qa FAIL: (a)-(d) PASS (citations, method of 26, p floor 2/256 and 6/256 verified on code and committed stats CSVs, all n = 8, 3-horizon families), AC4(ii) `24_shift_check --full` 0 FAIL (4 WARN git/worktree state), AC4(i)/(iii) NOT_VERIFIED (no Drive). QA-T08c-01 MED: new (e) contradicts the pre-registration bullet (~l.226 "DM spec ... fixed before results were seen") and the post-hoc list (~l.230); Holm was also added after the pilot (NHAT_KY :142, :147). QA-T08c-02 MED: "a longer lag gives a larger variance estimate" false in general (negative autocovariance); qualify to this data. Round 2: scope widened to the pre-registration bullet and the post-hoc deviations list in 2.6 (same file). attempt_count 2.
- 2026-11-26 worker round 2: `ad23bc9`, 1 file (pre-check OK). qa PASS round 2: -01 fixed (DM bullet, pre-registration, post-hoc list consistent; M01, pilot brief :33-35, NHAT_KY :142/:147 checked), -02 fixed (no general variance claim), (a)-(d) unchanged, AC4(ii) `24_shift_check --full` 0 FAIL (4 WARN git/worktree), AC4(i)/(iii) NOT_VERIFIED (no Drive; checked in T05 qa). New LOW QA-T08c-03 (space before comma after HTML comment, l.230) fixed by Leader in the merge docs commit. Leader approval (light task). Merged `ea1104d`.

## T09 — Update README
- owner: worker | priority: P3 | status: DONE | attempt_count: 1
- test_evidence: worker commit c992732 (branch worktree-agent-a997d894c831b203d, unmerged). qa PASS 2026-11-25; two low, non-blocking wording findings (QA-T09-01: 12_tune skips finished keys; QA-T09-02: 19/20/21 do not read predictions). Worker reports the 07 smoke run finished in 717 s on CPU (qa did not run it). Not executed: download, rebuild, training, SHAP, Colab. Open: PROVENANCE.md says 30 features per the worker; qa confirmed 31 in data.
- acceptance_criteria: every command matches the real argparse of its script; every cited path/script exists; data described as modelled (NREL SEA-WTK v3), 8 sites, 100 m, 1h/3h/6h; no result claims beyond RESULTS.md/M13; no keys, emails or personal data; old ERA5 notebook text removed; English.
- 2026-11-25 (Leader): started.
- goal: README still describes the old 4-site ERA5 notebooks; rewrite install/run/reproduce for the `scripts/01–21` pipeline.
- allowed_paths: `README.md`
- last_update: 2026-11-21
- 2026-11-25 (Director, under User delegation of 2026-11-25): APPROVE on QA PASS. Merged `453e16a`.

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

## T13 — Record validation score in few-shot rows (M12 pilot) — light task
- owner: worker | priority: P0 | status: DONE | attempt_count: 1
- test_evidence: QA PASS 2026-11-22. Ridge `val_best` is 0.008225 (DB) and 0.016977 (TN). A stubbed NN run passes `val_best` and `best_epoch` through. The header gains 2 columns before RMSE, so never append to an old CSV. Merged by the Leader.
- goal: `18_fewshot.py` output rows carry the selection metric, so the M12 pilot can pick the `month_*` handling on validation only. The first pilot (`pilot_free.csv`, `pilot_const.csv`, 72 + 72 rows, 2026-11-21) has test metrics only, so it cannot be used for selection.
- acceptance_criteria: rows get `val_best` (validation MSE, normalised; from `info` for NN modes, computed on `d.idx_val` for rf/ridge) and `best_epoch` (NN only, else empty); existing columns unchanged; ridge smoke writes the new columns; diff ≤ ~10 lines.
- allowed_paths: `scripts/18_fewshot.py`
- last_update: 2026-11-22 (Leader)

## T12 — Few-shot A–H with the 8-fold init (M11)
- M12 pilot v2 (2026-11-22): `--const-calendar` won on validation (20/20 cells; median val MSE 0.0116 vs 0.0239), so it is frozen for scratch.
- Planned runs, all with `--init-tag losoW8 --scratch-steps 2000`:
  - finetune + scratch with `--const-calendar` → `results/fewshot8_cc.csv`;
  - finetune without the flag (ablation) → `results/fewshot8_ft_free.csv`;
  - ridge + rf with and without the flag on CPU → `results/fewshot8_cpu_cc.csv`, `results/fewshot8_cpu_free.csv`.
- owner: Leader (Colab) + worker (RF, CPU) | priority: P1 | status: DONE | attempt_count: 1
- scope: `18_fewshot.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 3 --modes finetune,scratch --scratch-steps 2000 --init-tag losoW8 --out results/fewshot8.csv`; RF: `--modes rf --out results/fewshot8_rf.csv` (CPU).
- acceptance_criteria: 144 runs per mode; median-seed table vs persistence; Wilcoxon (n = 8, Holm) finetune vs persistence and vs scratch/RF.
- dependencies: T01, T10, T11, T02 QA | last_update: 2026-11-25 (Leader)
- test_evidence: 2026-11-25 (Leader) t12.done; `fewshot8_cc.csv` 864, `fewshot8_ft_free.csv` 432 rows (md5 equal clone/Drive/repo); `py scripts/23_fewshot_stats.py` ran on real data -> R25.
- 2026-11-25 qa PASS on c25db4c (R25c; independent recompute, ridge re-run 48/48 cells, RF 20/48 seed 0). Findings QA-T12-01, -02 Medium (weak reference; small gain over zero-shot), -03 to -07 Low: claim limits for T08. NOT_VERIFIED: GPU re-run, losoW8 checkpoints on Drive. Const/free: M14 supersedes 'ablation' above (free is main).
- 2026-11-25 (Director, under User delegation): APPROVE on QA PASS, results only. The paper claim wording waits for T16 (M14 condition 6).

## T14 — Transfer statistics script (LOSO-8), split from T06
- owner: worker | priority: P1 | status: DONE | attempt_count: 1
- test_evidence: worker commit 174c54a (branch worktree-agent-a9b08129b42168b07, unmerged). qa PASS 2026-11-25: 108 test rows recomputed independently (max diff 1.2e-16), CSVs regenerate identically, R16/R21/R21c/M13 reproduced, corrupted/zero/tied inputs raise. Note for T08: H is also slightly negative at 3h (-0.1%).
- goal: reproducible transfer statistics per M13 (conditions 3–4).
- scope: new `scripts/22_transfer_stats.py` (CPU, pandas/scipy; existing helpers such as Holm in `08_aggregate.py` reused, not copied, when importable) reading `results/loso8_wind.csv`, `results/loso8_rf_wind.csv`, `results/baselines.csv`; writes `results/transfer_stats.csv` (tests) and `results/transfer_per_site.csv` (per-site skill, median seed and each seed). Comparisons: Mamba vs persistence, RF vs persistence, Mamba vs RF, for losoW and globalW where present; 1h/3h/6h; primary = exact two-sided Wilcoxon on per-site skill of the median-seed RMSE; secondary = on RMSE difference; per-seed versions (vs persistence); wins/8, mean and median skill, rank-biserial, raw and Holm p (family = 3 horizons per comparison).
- acceptance_criteria: reproduces R21/R21c/R16 and the Mamba-vs-RF numbers (LOSO Holm 0.117, 6/8 wins; R16 6h 0.148 on skill, 0.109 on RMSE difference); `--selftest` with asserts (Holm, rank-biserial sign, all-wins n = 8 gives raw p 0.0078); fails loudly on incomplete seeds/sites; existing files unchanged.
- allowed_paths: `scripts/22_transfer_stats.py`, `results/transfer_stats.csv`, `results/transfer_per_site.csv`
- last_update: 2026-11-25 (Leader)
- 2026-11-25 (Director, under User delegation of 2026-11-25): APPROVE on QA PASS. Merged `d71d29d`.

## T15 — Few-shot statistics script (M14)
- owner: worker | priority: P1 | status: DONE | attempt_count: 1
- goal: reproducible T12 statistics exactly per M14 conditions (1)–(4).
- scope: new `scripts/23_fewshot_stats.py` (CPU), reusing helpers of `22_transfer_stats.py`/`08_aggregate.py`. Inputs: `results/fewshot8_cc.csv` (finetune const, scratch const), `fewshot8_ft_free.csv` (finetune free), `fewshot8_cpu_cc.csv`, `fewshot8_cpu_free.csv` (ridge, rf), `loso8_wind.csv` (zero-shot), `baselines.csv`. Outputs: `results/fewshot8_stats.csv`, `results/fewshot8_per_site.csv`, `results/fewshot8_cells.csv` (descriptive).
- acceptance_criteria: `--selftest` on synthetic data (known winner, oracle choice, val choice, Holm, loud failure on missing/duplicate/extra keys, unexpected seeds, deterministic ridge tolerated); the run on incomplete inputs fails loudly and writes nothing; the real run is done later by the Leader when T12 completes; existing files unchanged.
- allowed_paths: `scripts/23_fewshot_stats.py`
- last_update: 2026-11-25 (Leader)
- test_evidence: commit 5fed951; qa PASS 2026-11-25 (independent recompute on synthetic data, 20 Holm-3 families, 0 mismatches). NOT_VERIFIED: default run on the real results/ (the worker call was denied by the auto-mode classifier; not retried). Low: QA-T15-01 primary family = role primary AND metric skill; QA-T15-02/03: before the real run check that the CSVs end with a newline and that cc/free files are not copies.
- 2026-11-25 (Director, under User delegation): APPROVE on QA PASS. Merged `db66134`.

## T16 — Few-shot finetune without target validation (M15) — code part is a light task
- owner: worker + Leader (Colab) | priority: P2 | status: DONE | attempt_count: 1
- design: M15. Code: `--inner-val` flag in `18_fewshot.py` (NN modes only). Then Colab after T12: `--inner-val --modes finetune` -> `results/fewshot8_iv_ft_free.csv`; `--inner-val --modes scratch --const-calendar --scratch-steps 2000` -> `results/fewshot8_iv_scratch_cc.csv`.
- acceptance_criteria (code): default behaviour unchanged; fit/val inside the k-week window, contiguous, gap >= 120, val = int(0.2 n); `nb`/`n_train` from the fit subset; `idx_val` restored after every run (other modes/sites keep the target val); rf/ridge unaffected; inner-val smoke on CPU works (stubbed NN allowed); diff <= ~15 lines in 1 file.
- allowed_paths: `scripts/18_fewshot.py`
- goal: sensitivity check that the finetune gain does not depend on the ~39 target validation weeks; fixed step budget chosen without target data, frozen before test scores are read.
- scope: design + small option in `18_fewshot.py`, after T12 finishes on Colab.
- last_update: 2026-11-25 (Leader)
- test_evidence: code commit f3bae74, qa PASS 2026-11-25 (default path identical to 85248fb; fit/val/gap 418/134/120, 956/268/120, 2031/537/120; idx_val restored; real 2-batch CPU smoke). Light-task code approved and merged `dde7fbc`. The task stays IN_PROGRESS until the Colab runs finish.
- Colab: use full flags (`--sites A,B,C,D,E,F,G,H --seeds 3 --init-tag losoW8 --scratch-steps 2000 --inner-val`, both modes); file copied to `scripts/18_fewshot_iv.py` in the clone so T12 is not touched; waits for `t12.done`; ends with `t16.done`. MCP cell 3; re-run it after a reset (setup cell does not start it).
- 2026-11-25: t16.done; both files 432/432 (62ae847); R26; qa PASS on data and statistics (QA-T16-01 High, -02/-03 Medium are claim limits -> M16). NOT_VERIFIED: GPU re-run, RF re-run, Colab code version beyond n_train. APPROVE under User delegation.

## T17 — Shift harness: read-only start-of-shift check (User request)
- owner: worker | priority: P2 | status: DONE | attempt_count: 2
- goal: a new chat verifies the real state of the project before working, instead of trusting the handoff or running ad hoc tests.
- scope: new `scripts/24_shift_check.py` (CPU, stdlib + pandas, read-only, < ~60 s without `--full`), prints one line per check `PASS|WARN|FAIL|NOT_VERIFIED <group> <check> - <evidence>` and a summary; exit code 1 if any FAIL. Groups:
  - git: branch, HEAD vs origin/main (no fetch; say the ref may be old), uncommitted tracked files, extra worktrees, HANDOFF.md older than HEAD (WARN).
  - results: a table in code of the key CSVs (runs_wind 120, cross_eval_wind 576, loso8_wind 144, loso8_rf_wind 144, fewshot8_cc 864, fewshot8_ft_free 432, fewshot8_cpu_cc 864, fewshot8_cpu_free 864, baselines 48) with key columns and expected rows: rows, missing/duplicate keys, NaN/inf in RMSE, RMSE > 0, trailing newline. PatchTST runs.csv and T16 iv files absent locally -> NOT_VERIFIED.
  - docs: open tasks in STATUS.md (not DONE/CANCELLED) with state; RESULTS.md run ids unique and rows mentioning "not yet QA'd" without a later `R..c`/QA PASS row -> WARN; CSV paths in backticks in RESULTS.md that do not exist locally (Drive-only rows -> NOT_VERIFIED).
  - recompute: fewshot8 and transfer headline numbers re-derived from the stats CSVs (R21/R25 values in code as expected constants) -> FAIL when they differ by more than rounding.
  - selftests with `--full`: run `--selftest` of 08, 11, 22, 23, report exit code and last line.
  - colab/drive: always one NOT_VERIFIED line naming the status cell.
- acceptance_criteria: `--selftest` with asserts on temp data (missing key, duplicate, NaN, no newline, wrong row count, stale handoff each detected; clean data passes); real run on the repo writes nothing (git status identical before/after, no file mtimes changed in results/); every FAIL/WARN on the real repo explained; a check that cannot run prints NOT_VERIFIED, never PASS; no network call; existing files unchanged; existing style (comments in Vietnamese).
- allowed_paths: `scripts/24_shift_check.py`
- last_update: 2026-11-25 (Leader)
- 2026-11-25 qa FAIL on 96b57ab: QA-T17-01 (blocking, false PASS on empty RESULTS.md), -02, -03, -04 low/medium; -05 info (missing committed files are NOT_VERIFIED with exit 0, as contract). Scope, runs, expected values and merge check PASS. Sent back to worker (attempt 2).
- 2026-11-25 qa PASS on 54e5150 (attempt 2): QA-T17-01..04 fixed, 15/18 reverts killed, 132 headline mutations 0 missed, no file change. Open LOW findings of the re-QA: blank run_id row skipped, literal 'not yet QA'd' matching, `### T` headings dropped, two guards without assert. Exit 0 does not mean all verified (empty STATUS.md gives NOT_VERIFIED, exit 0).
- 2026-11-25 (Director, under User delegation): APPROVE on QA PASS. Merged `2597ac7`.

## T18 — Statistics of T16 (M15) — light task
- owner: worker | priority: P1 | status: DONE | attempt_count: 1 | last_update: 2026-11-25 (Leader)
- goal: `23_fewshot_stats.py --inner-val` computes the M14 statistics with the inner-validation NN runs, per M15 (frozen before the test scores are read).
- scope: finetune free from `fewshot8_iv_ft_free.csv`, scratch const from `fewshot8_iv_scratch_cc.csv`; Ridge/RF, zero-shot and persistence inputs unchanged. The `best_val` pair/reference and the finetune const vs free pair are dropped. Outputs `results/fewshot8_iv_{stats,per_site,cells}.csv`.
- acceptance_criteria: without the flag the output is unchanged (regenerated CSVs identical); incomplete, duplicate or extra iv rows fail loudly and write nothing; `--selftest` covers the iv mode (known winner, dropped pairs, files written, missing file); primary = finetune free vs oracle best of {scratch, Ridge, RF const}, Holm over 3 horizons; diff <= ~50 lines in 1 file; `--inner-val` on the real results is run once and its numbers are reported; existing CSVs unchanged.
- allowed_paths: `scripts/23_fewshot_stats.py`, `results/fewshot8_iv_stats.csv`, `results/fewshot8_iv_per_site.csv`, `results/fewshot8_iv_cells.csv`
- test_evidence: commit 2429791; worker +56/-29 lines (above ~50, mostly selftest, judged not material by qa). qa PASS 2026-11-25. Open LOW: QA-T18-01 (selftest does not cover the flag wiring in main), QA-T18-02 (iv content such as n_train not checked). Approved (light task), merged `be6b306`.

## T19 — Committed statistics for R22/R23 (W vs 31 features, own site and cross-site)
- owner: worker | priority: P1 | status: DONE | attempt_count: 1 | created: 2026-11-26 (Leader)
- goal: the R22/R23 Wilcoxon p-values (Section 2.6 TODO) are reproducible from a committed script, with the exact test variant stated.
- scope: new `scripts/26_feature_set_stats.py` reading `results/runs.csv` (Mamba, 31 features), `results/runs_wind.csv` (Mamba W), `results/cross_eval_nn.csv` (31), `results/cross_eval_wind.csv` (W), `results/baselines.csv` (persistence); reuse `22_transfer_stats.py` helpers (`compare`, `rank_biserial`, `check`) via its `_load` pattern; writes `results/feature_set_stats.csv`; `--selftest`.
- acceptance_criteria:
  1. Own site (R22): per-site skill vs persistence of the median-seed RMSE (5 seeds), W vs 31, W−31 pp, two-sided exact Wilcoxon n = 8, Holm over 3 horizons; also the seed-mean variant. Reproduces RESULTS R22 (W +14.19/+18.23/+24.09 %, 31 +16.05/+21.81/+27.95 %, Holm p 0.023 ×3, seed-mean 0.055/0.023/0.023) to the printed precision.
  2. Cross-site (R23): mean over 8 targets of same-regime and cross-regime skill (median of 3 seeds), W−31 same and cross (Holm p 0.297/0.297/0.164 and 0.031/0.031/0.023), same−cross (0.023 ×3), W vs persistence same and cross (n.s.). Reproduces R23 to the printed precision.
  3. Any number that does not reproduce is reported with both values; do not tune the method to match. State the exact variant used (zero handling, exact vs normal, aggregation).
  4. `--selftest` with an assert-based check (known Wilcoxon p and Holm); script follows the existing style (Vietnamese comments without diacritics, argparse like 22).
  5. Only `scripts/26_feature_set_stats.py` and `results/feature_set_stats.csv` change.
  6. Shift checks (HANDOFF 2026-11-26 §7): `py scripts/24_shift_check.py --full` -> 0 FAIL, report every WARN/NOT_VERIFIED; Drive `runs.csv` PatchTST counts and `shap_*.npz` modifiedTime need Drive -> NOT_VERIFIED (Leader checks them on Colab).
- allowed_paths: `scripts/26_feature_set_stats.py`, `results/feature_set_stats.csv`
- dependencies: R22, R23 (QA PASS); independent of T05 (uses Mamba rows only).
- 2026-11-26 Leader: contract written, worker spawned.
- 2026-11-26 worker `96bf6fc` (2 allowed files, pre-check OK). qa PASS: selftest dat; in-memory `analyze()` equals committed CSV (45x11, rtol 1e-12); independent brute-force Wilcoxon + Holm recompute matches every R22/R23 value; pairs A-E, B-F, C-G, D-H, persistence of target site; `24_shift_check --full` 0 FAIL; Drive checks NOT_VERIFIED. QA-T19-01 LOW: R23 same-cross 6h is 17.947 (17.9), not 18.0 (double rounding) -> correction row R23e. Risks: 24_shift_check does not run 26 selftest yet; exact Wilcoxon n=8 floor p 2/256 -> Holm 0.023, state in paper. Director APPROVE (Leader, User delegation 2026-11-25). Merged `25fb482`.

## T20 — Shift check covers R22/R23 (T19 follow-up) — light task
- owner: worker | priority: P2 | status: DONE | attempt_count: 1 | created: 2026-11-26 (Leader)
- goal: `24_shift_check.py` re-checks the R22/R23/R23e numbers against `results/feature_set_stats.csv` and runs `26_feature_set_stats.py --selftest` in `--full` (QA-T19 risk).
- acceptance_criteria: (1) `26_feature_set_stats.py` in the `--full` selftest list; (2) HEADLINE entries for R22 (W skill, 31 skill, W−31 pp, W−31 wins 1/0/0, Holm p, seed-mean Holm p) and R23/R23e (own/same/cross W, W−31 same and cross with Holm p, same−cross 1h/3h, R23e 6h +17.9) using the existing `check_headline` format; (3) `py scripts/24_shift_check.py --full` -> every new recompute line PASS, 0 FAIL; `--selftest` of 24 still passes; (4) a deliberately wrong number in a temp copy is caught (FAIL) — show it, then discard; (5) <= ~50 lines, only `scripts/24_shift_check.py` changes; (6) HANDOFF §7 Drive checks -> NOT_VERIFIED (Leader on Colab).
- allowed_paths: `scripts/24_shift_check.py`
- 2026-11-26 worker `0b4637a` (1 file, +26/−2, pre-check OK). qa PASS: 16 new HEADLINE mappings verified against RESULTS rows and CSV filters; `--full` 61 PASS, 4 WARN (worktree housekeeping), 0 FAIL, 2 NOT_VERIFIED; `--selftest` dat; in-memory negative tests FAIL 16/16 (text), 16/16 (number). QA-T20-01 info: one entry anchors on the known-wrong R23 "18.0" text (rows are append-only; edit would FAIL, a correct signal). Drive checks NOT_VERIFIED. Leader APPROVE (light task). Merged `8594f40`.
