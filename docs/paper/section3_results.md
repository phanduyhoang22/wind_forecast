# 3. Results — per-site benchmark (E1), regimes, prediction intervals and CPU cost (draft v1, 27/11/2026)

> Draft of the E1 Results parts that waited for T05 (PatchTST 40/40), T06 (aggregate statistics) and T07 (conformal intervals). The claims follow meeting M18 (E1 claim) and M02 (per-seed DM primary). Transfer, few-shot and SHAP results are in `section3_results_transfer.md`; the subsection numbers of the two files overlap and are provisional. Each number carries an HTML comment with its source (run_id in `tasks/RESULTS.md` and/or a committed CSV under `results/`). All data are modelled (NREL SEA-WTK v3), not measurements. The Discussion is not part of this draft.

**Conventions.** RMSE and MAE in m/s on the test partition (Apr–Dec 2021, 26,161 windows per site) <!-- Section 2.4 (windows per site) -->. Skill SS = 1 − RMSE_model / RMSE_persistence, in %; persistence RMSE from `results/baselines.csv`. All E1 models use the 31 features. Per site, a model's RMSE is the mean over its five seeds and SS is computed from that mean; "8-site mean SS" is the mean of the eight per-site values <!-- scripts/08_aggregate.py:58-79 (summarize); results/summary_by_site.csv (skill), results/summary_overall.csv (skill_avg) -->. "pp" = percentage points of SS.

## 3.1 Accuracy per site and horizon

**Table 3.1a.** Mean over the eight sites. RMSE: mean ± standard deviation over the five seeds of the 8-site mean RMSE; MAE: mean over seeds; SS: 8-site mean. Persistence: mean over sites.

| Model | RMSE 1 h | 3 h | 6 h | MAE 1 h | 3 h | 6 h | SS 1 h | 3 h | 6 h |
|---|---|---|---|---|---|---|---|---|---|
| Mamba | 0.618 ± 0.003 | 1.099 ± 0.004 | 1.361 ± 0.004 | 0.435 | 0.813 | 1.027 | 15.8 | 21.8 | 27.9 |
| Transformer | 0.621 ± 0.003 | 1.097 ± 0.003 | 1.356 ± 0.003 | 0.435 | 0.811 | 1.019 | 15.3 | 22.0 | 28.2 |
| RF | 0.620 ± <0.001 | 1.123 ± <0.001 | 1.415 ± <0.001 | 0.430 | 0.833 | 1.073 | 15.5 | 20.1 | 25.2 |
| LSTM | 0.638 ± 0.003 | 1.130 ± 0.005 | 1.391 ± 0.006 | 0.452 | 0.837 | 1.050 | 13.1 | 19.7 | 26.4 |
| PatchTST | 0.700 ± 0.042 | 1.202 ± 0.023 | 1.491 ± 0.021 | 0.491 | 0.888 | 1.124 | 4.4 | 14.7 | 21.2 |
| DLinear | 0.682 ± 0.001 | 1.219 ± 0.001 | 1.523 ± 0.001 | 0.486 | 0.908 | 1.162 | 7.4 | 13.7 | 19.7 |
| Persistence | 0.738 | 1.423 | 1.925 | 0.519 | 1.058 | 1.475 | 0 | 0 | 0 |

<!-- R31 / results/summary_overall.csv (RMSE_mean, RMSE_std, MAE_mean, skill_avg); persistence = results/baselines.csv (model persistence, mean over sites A-H) -->

**Table 3.1b.** SS (%) per site and horizon (seed-mean RMSE). Bold: lowest RMSE in the row. Persistence RMSE in m/s.

| h | Site | Regime | Pers. RMSE | Mamba | Transformer | RF | LSTM | PatchTST | DLinear |
|---|---|---|---|---|---|---|---|---|---|
| 1 h | A | Inland | 0.845 | **18.2** | 17.3 | 17.0 | 14.9 | 11.2 | 5.4 |
|  | B | Coastal | 0.640 | 12.9 | 12.4 | **13.3** | 10.7 | 3.1 | 5.8 |
|  | C | Complex | 0.608 | 18.3 | **20.0** | 18.1 | 16.2 | 8.2 | 10.8 |
|  | D | Offshore | 0.538 | 7.7 | 5.1 | **8.1** | 5.2 | −7.3 | 5.6 |
|  | E | Inland | 0.818 | **22.1** | 21.5 | 20.5 | 19.5 | 7.6 | 13.4 |
|  | F | Coastal | 0.884 | 18.5 | 19.1 | **19.7** | 16.4 | 10.6 | 9.4 |
|  | G | Complex | 0.815 | **20.0** | 18.6 | 18.4 | 15.8 | 10.1 | 6.6 |
|  | H | Offshore | 0.755 | 8.3 | 8.1 | **8.7** | 5.8 | −8.1 | 2.4 |
| 3 h | A | Inland | 1.634 | 23.9 | **24.4** | 21.8 | 21.0 | 18.0 | 15.6 |
|  | B | Coastal | 1.191 | 18.4 | **18.9** | 18.4 | 16.9 | 12.9 | 10.5 |
|  | C | Complex | 1.199 | 26.7 | **27.8** | 25.4 | 25.1 | 19.5 | 18.6 |
|  | D | Offshore | 1.004 | **7.9** | 6.6 | 4.8 | 5.3 | 1.2 | 3.3 |
|  | E | Inland | 1.582 | 30.6 | **30.9** | 29.2 | 28.1 | 21.8 | 20.4 |
|  | F | Coastal | 1.759 | 27.3 | **27.8** | 26.7 | 26.1 | 19.8 | 18.0 |
|  | G | Complex | 1.605 | **28.0** | 27.7 | 25.8 | 25.2 | 20.9 | 17.9 |
|  | H | Offshore | 1.410 | **11.8** | 11.6 | 9.0 | 9.5 | 3.5 | 5.2 |
| 6 h | A | Inland | 2.197 | 31.4 | **31.8** | 27.9 | 29.1 | 25.8 | 24.1 |
|  | B | Coastal | 1.538 | 22.7 | **23.3** | 21.7 | 21.1 | 16.5 | 13.2 |
|  | C | Complex | 1.675 | **36.2** | 35.9 | 34.2 | 35.0 | 28.2 | 27.7 |
|  | D | Offshore | 1.314 | 8.3 | **8.7** | 5.5 | 6.7 | 3.8 | 4.1 |
|  | E | Inland | 2.114 | 38.4 | **38.9** | 36.4 | 37.1 | 31.8 | 29.4 |
|  | F | Coastal | 2.432 | **36.6** | 36.5 | 33.8 | 35.4 | 29.3 | 26.8 |
|  | G | Complex | 2.236 | 34.1 | **34.2** | 30.5 | 32.7 | 26.7 | 23.9 |
|  | H | Offshore | 1.893 | 15.4 | **15.9** | 11.3 | 13.8 | 7.6 | 8.3 |

<!-- R31 / results/summary_by_site.csv (skill, RMSE_mean for bold); results/baselines.csv (persistence RMSE); regimes: Section 2.2, Table 1 -->

**Skill against persistence.** Mamba, Transformer and RF beat persistence at every site and horizon; so do LSTM and DLinear <!-- results/summary_by_site.csv (skill > 0 in 142 of 144 rows; the 2 others are PatchTST 1h D, H) -->. PatchTST is the only exception: at 1 h it is worse than persistence at the two offshore sites, D (SS −7.3 %) and H (−8.1 %) <!-- R31 / results/summary_by_site.csv (PatchTST 1h D -0.0732, H -0.0809) -->. The three strongest models are close in 8-site mean SS: Mamba 15.8 / 21.8 / 27.9 %, Transformer 15.3 / 22.0 / 28.2 %, RF 15.5 / 20.1 / 25.2 % at 1 / 3 / 6 h <!-- R31 / results/summary_overall.csv (skill_avg) -->. LSTM follows (13.1 / 19.7 / 26.4 %), then PatchTST (4.4 / 14.7 / 21.2 %) and DLinear (7.4 / 13.7 / 19.7 %) <!-- R31 / results/summary_overall.csv -->. SS rises with horizon for every model because persistence RMSE grows faster (0.738 → 1.925 m/s from 1 h to 6 h) than model RMSE <!-- results/baselines.csv; results/summary_overall.csv -->.

**Best model per cell.** Over the 24 site–horizon cells, the lowest seed-mean RMSE belongs to Transformer in 12, Mamba in 8 and RF in 4 <!-- results/summary_by_site.csv (argmin RMSE_mean per site x horizon); M18 evidence -->. At 1 h the cells split between RF (4), Mamba (3) and Transformer (1); at 3 h and 6 h Transformer has 11 of 16 and Mamba 5 <!-- results/summary_by_site.csv (argmin per horizon: 1h RF 4, Mamba 3, Transformer 1; 3h Transformer 5, Mamba 3; 6h Transformer 6, Mamba 2) -->. Mamba has a lower seed-mean RMSE than Transformer at 6, 3 and 2 of 8 sites at 1, 3 and 6 h, and than RF at 4, 7 and 8 of 8 <!-- results/summary_by_site.csv (RMSE_mean, Mamba < rival per site) -->. Mamba is ahead of LSTM, PatchTST and DLinear at all eight sites and horizons <!-- results/summary_by_site.csv (RMSE_mean, 24/24 cells each) -->.

**Sites.** The two offshore sites, D and H, have the lowest skill of all sites for every model and horizon except DLinear at 1 h (where A is below D) <!-- results/summary_by_site.csv (two smallest skill per model x horizon = {D, H} in 17/18) -->; for Mamba, SS there is 7.7–15.4 % <!-- results/summary_by_site.csv -->. For Mamba, the inland site E has the highest skill at every horizon (22.1 / 30.6 / 38.4 %) <!-- results/summary_by_site.csv -->. At D, persistence RMSE is the lowest of all sites at every horizon (0.538 / 1.004 / 1.314 m/s) <!-- results/baselines.csv -->.

**Seed spread.** PatchTST varies most between seeds (standard deviation of the 8-site mean RMSE 0.042 m/s at 1 h, ≤ 0.006 m/s for the others; at H its 1 h RMSE spans 0.748–0.953 m/s), RF least (< 0.001 m/s) <!-- results/summary_overall.csv (RMSE_std); R28 / results/runs.csv (PatchTST, 1h, H, seeds 0-4) -->.

## 3.2 Statistical comparison

The primary layer is the per-seed Diebold–Mariano (DM) test of seed i of Mamba against seed i of each rival, Holm-adjusted over all 600 tests (8 sites × 3 horizons × 5 rivals × 5 seeds) (Section 2.6; M02) <!-- R31 / results/dm_per_seed.csv (600 rows); scripts/08_aggregate.py:113-152 (dm_per_seed) -->. A win (loss) is Holm p < 0.05 with Mamba's loss lower (higher). The seed-ensemble DM test (family of 120) is secondary <!-- R31 / results/dm_tests.csv (120 rows) -->; the paired t-test on the five per-seed RMSEs is unadjusted <!-- results/dm_per_seed_summary.csv (p_ttest); scripts/08_aggregate.py:142-151 -->. Effect sizes are differences in 8-site mean SS, Mamba minus rival, per seed (seed i vs seed i), with mean and t-based 95 % CI over the five seeds <!-- computed from results/runs.csv + results/runs_rf.csv + results/baselines.csv; seed mean of the per-seed 8-site SS equals summary_overall skill_avg (diff 8e-17) -->. Seeds are independent across architectures, so this pairing is by seed index only; Welch two-sample CIs include or exclude zero in the same 15 comparisons (e.g. Transformer 6 h [−0.56, +0.01], RF 3 h [+1.42, +1.94]) <!-- throw-away pandas session, same inputs: Welch t-interval on the five per-seed 8-site SS of each model (Transformer 1h [-0.14, 1.12], 3h [-0.42, 0.15], 6h [-0.56, 0.01]; RF 1h [-0.31, 0.86], 3h [1.42, 1.94], 6h [2.45, 2.95]; LSTM [2.03, 3.35], [1.72, 2.60], [1.10, 1.95]; PatchTST [3.85, 18.79], [5.08, 9.20], [5.37, 7.97]; DLinear [7.77, 8.92], [7.87, 8.39], [7.96, 8.45]) -->.

**Table 3.2.** Mamba against each rival. Per-seed DM: number of significant wins / losses out of 40 (8 sites × 5 seeds). Ensemble DM: sites where the Mamba ensemble is significantly better / worse, out of 8. Paired t: sites with unadjusted p < 0.05, Mamba better / worse, out of 8. ΔSS: Mamba minus rival, pp.

| Rival | h | Per-seed DM wins / losses (of 40) | Ensemble DM better / worse (of 8) | Paired t better / worse (of 8) | ΔSS (pp), mean [95 % CI] | Seeds with ΔSS > 0 |
|---|---|---|---|---|---|---|
| Transformer | 1 h | 6 / 4 | 6 / 0 | 1 / 0 | +0.49 [−0.07, +1.05] | 4/5 |
|  | 3 h | 0 / 0 | 0 / 0 | 1 / 1 | −0.13 [−0.31, +0.05] | 1/5 |
|  | 6 h | 0 / 0 | 0 / 0 | 0 / 1 | −0.27 [−0.58, +0.03] | 0/5 |
| RF | 1 h | 4 / 4 | 8 / 0 | 3 / 0 | +0.27 [−0.31, +0.86] | 3/5 |
|  | 3 h | 4 / 0 | 7 / 0 | 6 / 0 | +1.68 [+1.41, +1.95] | 5/5 |
|  | 6 h | 9 / 0 | 8 / 0 | 8 / 0 | +2.70 [+2.45, +2.95] | 5/5 |
| LSTM | 1 h | 18 / 0 | 8 / 0 | 5 / 0 | +2.69 [+1.75, +3.63] | 5/5 |
|  | 3 h | 14 / 0 | 5 / 0 | 6 / 0 | +2.16 [+1.56, +2.75] | 5/5 |
|  | 6 h | 1 / 0 | 1 / 0 | 6 / 0 | +1.53 [+0.99, +2.06] | 5/5 |
| PatchTST | 1 h | 28 / 0 | 7 / 0 | 7 / 0 | +11.32 [+3.51, +19.13] | 5/5 |
|  | 3 h | 36 / 0 | 8 / 0 | 8 / 0 | +7.14 [+5.03, +9.25] | 5/5 |
|  | 6 h | 30 / 0 | 8 / 0 | 8 / 0 | +6.67 [+5.44, +7.89] | 5/5 |
| DLinear | 1 h | 36 / 0 | 8 / 0 | 7 / 0 | +8.34 [+7.69, +8.99] | 5/5 |
|  | 3 h | 40 / 0 | 8 / 0 | 8 / 0 | +8.13 [+7.90, +8.35] | 5/5 |
|  | 6 h | 37 / 0 | 8 / 0 | 8 / 0 | +8.21 [+7.91, +8.51] | 5/5 |

<!-- R31, R31c / results/dm_per_seed.csv (sum of win, loss by vs x horizon); results/dm_tests.csv (sum of mamba_better, mamba_worse); results/dm_per_seed_summary.csv (p_ttest < 0.05 and sign of d_rmse); ΔSS: throw-away pandas session on results/runs.csv, results/runs_rf.csv, results/baselines.csv (per seed: mean over sites of 1 - RMSE/RMSE_pers; Mamba - rival; t(0.975, 4)) -->

**Mamba, Transformer and RF.** In the primary layer, most comparisons among the three strongest models show no significant difference: 110 of the 120 per-seed tests against Transformer and 99 of the 120 against RF <!-- results/dm_per_seed.csv (vs Transformer: 10 significant; vs RF: 21 significant) -->. Absence of a significant difference is not evidence of equivalence; no equivalence test (TOST) with a pre-stated margin was run, and we make no equivalence claim (M18).

- *Against Transformer:* the 1 h result is mixed: 6 wins and 4 losses of 40 <!-- R31 / results/dm_per_seed.csv (Transformer, 1h: win 6, loss 4) -->, ΔSS +0.49 pp with a CI that includes zero. At 3 h and 6 h no per-seed test is significant in either direction, and Transformer is ahead on average: ΔSS −0.13 and −0.27 pp, with Transformer the better model in 4 of 5 and 5 of 5 seeds <!-- results/dm_per_seed.csv (Transformer 3h, 6h: 0/0); ΔSS from runs.csv (seeds with ΔSS > 0: 1/5, 0/5) -->. Together with the best-in-cell counts (Section 3.1), Transformer is at least as accurate as Mamba at 3 h and 6 h. We describe the two as comparable (Mamba ≈ Transformer, M02).
- *Against RF:* at 1 h the result is again mixed, 4 wins and 4 losses of 40 <!-- R31 / results/dm_per_seed.csv (RF, 1h: win 4, loss 4) -->, ΔSS +0.27 pp with a CI that includes zero. At 3 h and 6 h the direction favours Mamba consistently: lower seed-mean RMSE at 7 and 8 of 8 sites, ΔSS +1.68 and +2.70 pp, positive in all five seeds, with CIs that exclude zero <!-- results/summary_by_site.csv; ΔSS from runs.csv + runs_rf.csv -->. These CIs reflect training randomness only (seed-to-seed variation; RF hardly varies between seeds), not the sampling variability of the test period. Window-level significance is limited: 4 and 9 of 40 per-seed DM tests at 3 h and 6 h, and none against Mamba <!-- results/dm_per_seed.csv (RF 3h: 4/0, 6h: 9/0) -->.

All eight per-seed losses of Mamba are at 1 h: against Transformer at B and C (three seeds at C), against RF at B, C, D and F <!-- results/dm_per_seed.csv (loss == True: 8 of 600, all 1h; Transformer B s0, C s0/s2/s4; RF B s0, C s4, D s3, F s2) -->.

**Mamba against LSTM, PatchTST and DLinear.** Mamba is never significantly worse than these three in any per-seed test <!-- results/dm_per_seed.csv (losses 0 for LSTM, PatchTST, DLinear) -->. Against LSTM, it is significantly better in 18 of 40 per-seed tests at 1 h and 14 of 40 at 3 h, but only 1 of 40 at 6 h, although ΔSS stays positive at all horizons (+2.69 / +2.16 / +1.53 pp, all five seeds) <!-- R31 / results/dm_per_seed.csv (LSTM: 18-14-1 / 0); ΔSS from runs.csv -->. Against PatchTST (28 / 36 / 30 of 40) and DLinear (36 / 40 / 37 of 40) most per-seed tests are significant at every horizon <!-- R31 / results/dm_per_seed.csv -->. The PatchTST ΔSS at 1 h has a wide CI (+3.5 to +19.1 pp) because of PatchTST's seed spread (Section 3.1).

**Ensemble DM (secondary).** Testing the five-seed ensembles gives a more favourable picture for Mamba against RF: significantly better in 23 of 24 site–horizon cells (8 / 7 / 8 at 1 / 3 / 6 h), against 17 wins of 120 in the per-seed layer <!-- R31 / results/dm_tests.csv (RF: mamba_better 8/7/8); results/dm_per_seed.csv (RF wins 4+4+9) -->. The two layers test different objects. Averaging five neural-network seeds removes much of their seed-specific error, whereas RF is already an average of 500 trees and its five seeds differ little (Section 3.1), so the ensemble comparison favours the neural networks over RF by construction (QA-T06-03). Against Transformer, where both sides are averaged, the ensemble Mamba is better at 6 of 8 sites at 1 h, which is more favourable than the mixed per-seed result, and at no site at 3 h and 6 h <!-- results/dm_tests.csv (Transformer: 6/0/0) -->. The ensemble Mamba is never significantly worse than any rival <!-- results/dm_tests.csv (mamba_worse: 0 of 120) -->. We never cite the ensemble layer without the per-seed layer.

## 3.3 Regimes

The test predictions of Section 3.1 are split, without retraining, by monsoon season, by the time of issue (day 06:00–17:59 local time, otherwise night) and by ramp events (the 5 % largest |v(t + h) − v(t)| per site and horizon) <!-- scripts/14_regime.py:4-8, :23-24 (SEASON), :48 (day/night), :54 (ramp); Section 2.5.4 -->. RMSE is the mean over the five seeds; SS is against persistence in the same subset <!-- scripts/14_regime.py:63-64 -->. The test year has no January–March, so the core of the Northeast monsoon is missing (Section 2.4). These results are descriptive; no test was run.

**Table 3.3.** 8-site mean SS (%) by regime. Windows: number of test windows summed over the eight sites. Pers. RMSE: mean over sites (m/s). Bold: highest mean SS in the row.

| Regime | h | Windows (8 sites) | Pers. RMSE | Mamba | Transformer | RF | LSTM | PatchTST | DLinear |
|---|---|---|---|---|---|---|---|---|---|
| SW monsoon (May–Sep) | 1 h | 117,504 | 0.817 | **16.1** | 15.1 | 15.6 | 13.1 | 6.6 | 7.8 |
|  | 3 h | 117,504 | 1.547 | 22.1 | **22.1** | 20.5 | 20.0 | 15.9 | 14.8 |
|  | 6 h | 117,504 | 2.055 | 28.6 | **29.1** | 26.2 | 27.6 | 23.3 | 22.1 |
| Transition (Apr, Oct) | 1 h | 45,128 | 0.667 | 16.2 | 16.2 | **16.4** | 14.2 | −1.6 | 6.7 |
|  | 3 h | 45,128 | 1.328 | 22.6 | **22.8** | 20.9 | 20.4 | 13.7 | 14.4 |
|  | 6 h | 45,128 | 1.858 | **28.4** | 28.2 | 25.5 | 26.2 | 20.7 | 20.2 |
| Early NE monsoon (Nov–Dec) | 1 h | 46,656 | 0.551 | 13.9 | **15.0** | 14.7 | 11.3 | 3.0 | 6.1 |
|  | 3 h | 46,656 | 1.122 | 18.5 | **19.0** | 16.4 | 16.5 | 10.3 | 7.2 |
|  | 6 h | 46,656 | 1.573 | 22.5 | **22.8** | 19.0 | 20.5 | 12.7 | 8.2 |
| Day (06:00–17:59) | 1 h | 104,832 | 0.751 | **18.1** | 17.6 | 17.9 | 15.1 | 6.3 | 9.6 |
|  | 3 h | 104,832 | 1.470 | 24.8 | **25.0** | 23.5 | 22.2 | 16.9 | 16.2 |
|  | 6 h | 104,832 | 2.013 | 30.7 | **31.4** | 28.3 | 29.2 | 24.3 | 23.0 |
| Night | 1 h | 104,456 | 0.723 | **13.2** | 12.7 | 12.8 | 10.9 | 2.4 | 5.1 |
|  | 3 h | 104,456 | 1.373 | 18.4 | **18.5** | 16.4 | 16.7 | 12.2 | 10.8 |
|  | 6 h | 104,456 | 1.830 | **24.5** | 24.3 | 21.4 | 22.9 | 17.6 | 15.8 |
| Ramp (top 5 %) | 1 h | 10,521 | 2.235 | **25.3** | 22.1 | 19.6 | 22.5 | 18.1 | 17.2 |
|  | 3 h | 10,493 | 3.934 | **33.8** | 33.5 | 29.0 | 31.2 | 26.9 | 20.7 |
|  | 6 h | 10,511 | 5.015 | 41.9 | **42.1** | 36.5 | 39.8 | 34.5 | 29.1 |
| Non-ramp | 1 h | 198,767 | 0.555 | 8.5 | 9.9 | **12.3** | 5.8 | −5.9 | 0.1 |
|  | 3 h | 198,795 | 1.146 | 15.3 | **15.7** | 15.1 | 13.4 | 8.0 | 9.8 |
|  | 6 h | 198,777 | 1.602 | 21.7 | **21.9** | 20.0 | 20.4 | 15.3 | 15.4 |

<!-- R31, R31c / results/regime.csv (regime mua: TN, chuyen mua, dau DB; ngay_dem: ngay, dem; ramp: ramp, thuong); skill mean over sites A-H; n = sum over sites of the persistence row; Pers. RMSE = mean over sites of the persistence row -->

**Seasons and time of day.** In every season and at day and night, Mamba and Transformer are within 1.1 pp of each other in the 8-site mean SS <!-- results/regime.csv (max |Mamba - Transformer| over the 15 season and day/night rows: 1.08 pp) -->. RF is close to them at 1 h but up to 3.8 pp behind at 3 h and 6 h, where LSTM is ahead of RF in 7 of the 15 season and day/night rows <!-- results/regime.csv (max gap best of Mamba/Transformer minus RF: 3.76 pp, early NE monsoon 6h; LSTM > RF: SW 6h, transition 6h, early NE 3h/6h, night 3h/6h, day 6h) -->. Skill is lower at night than in the day for every model and horizon (Mamba 13.2 vs 18.1 % at 1 h) <!-- results/regime.csv (night < day in 18/18 model x horizon) -->. It is lowest in the early Northeast monsoon for every model and horizon except PatchTST at 1 h (lowest in the transition months) (Mamba 13.9 / 18.5 / 22.5 %); in that season persistence is also most accurate (0.551 / 1.122 / 1.573 m/s) <!-- results/regime.csv (argmin season per model x horizon) -->. DLinear loses most there (6.1 / 7.2 / 8.2 %) <!-- results/regime.csv -->.

**Ramps.** Ramp windows are selected by a large |v(t + h) − v(t)|, which is the absolute error of persistence itself. Skill against persistence is therefore inflated inside the ramp subset and deflated outside it, for every model; these numbers compare models with each other more than with persistence. Inside the ramp subset Mamba has the highest mean SS at 1 h (25.3 % vs Transformer 22.1 %, LSTM 22.5 %, RF 19.6 %); outside it RF is highest at 1 h (12.3 % vs Transformer 9.9 %, Mamba 8.5 %) <!-- results/regime.csv (ramp: ramp / thuong, 1h) -->. At 3 h and 6 h Mamba and Transformer differ by less than 0.5 pp in both subsets <!-- results/regime.csv (|Mamba - Transformer| ramp 0.25 / 0.29, non-ramp 0.32 / 0.24 pp) -->. The ramp subset holds 1,309–1,328 windows per site and horizon instead of exactly 5 %, because values tied at the 95th-percentile threshold are all included; taking v(t) from the raw series instead of the back-transformed inputs changes these counts by up to 13 and SS by less than 0.1 pp (QA-T06-07) <!-- results/regime.csv (persistence, ramp, n per site x horizon: min 1309, max 1328); R31c (QA-T06-07: n up to 13, skill < 1e-3) -->.

**Regime cells below persistence.** Of the 1,008 model–site–horizon–regime cells (6 models × 8 sites × 3 horizons × 7 regime values), 39 have negative SS: 27 for PatchTST, 10 for DLinear and 2 for LSTM; none for Mamba, Transformer or RF <!-- R31 / results/regime.csv (skill < 0, model != persistence: PatchTST 27, DLinear 10, LSTM 2) (QA-T06-04) -->. The PatchTST cells are mostly at D (10) and H (8), and 18 of the 27 are at 1 h (5 at 3 h, 4 at 6 h) <!-- results/regime.csv (PatchTST negative cells by site: D 10, H 8, B 3, F 3, E 2, C 1; by horizon: 1h 18, 3h 5, 6h 4) -->. DLinear is below persistence in six early-Northeast-monsoon cells (F at all three horizons, D at 3 h and 6 h, B at 6 h) and in four non-ramp cells at 1 h (A, B, F, G); LSTM at F (early Northeast monsoon) and H (non-ramp), both at 1 h <!-- results/regime.csv (DLinear and LSTM rows with skill < 0: DLinear dau DB F 1h/3h/6h, D 3h/6h, B 6h; thuong 1h A, B, F, G) -->.

## 3.4 Prediction intervals (E11)

Split conformal intervals ŷ ± q are calibrated per model, site, seed and horizon on the n = 26,162 absolute validation residuals, with q their exact k-th order statistic, k = ⌈(n + 1)(1 − α)⌉, and applied unchanged to the test partition <!-- R30 / scripts/11_conformal.py:44-49 (conformal_q), :66-68; Section 2.4 (validation windows) -->. PICP is the share of test values inside the interval; PINAW is 2q divided by the range of the training-partition target of the same site and horizon, so the denominator does not depend on the test set <!-- scripts/11_conformal.py:68, :139 (y_tr range per horizon); M17 (4) -->. PICP is also split by tercile of the observed test wind speed <!-- scripts/11_conformal.py:69-73 -->. All 1,440 combinations (6 models × 8 sites × 5 seeds × 2 levels × 3 horizons) are present <!-- R30 / results/conformal.csv (1440 rows, 240 per model) -->.

**Table 3.4.** Mean over 8 sites and 5 seeds (and over horizons where not split).

| Model | Nominal | PICP | PICP 1 h / 3 h / 6 h | PICP low / mid / high tercile | PINAW |
|---|---|---|---|---|---|
| Mamba | 0.90 | 0.874 | 0.866 / 0.874 / 0.884 | 0.869 / 0.898 / 0.856 | 0.166 |
| Transformer | 0.90 | 0.874 | 0.864 / 0.874 / 0.883 | 0.870 / 0.895 / 0.856 | 0.165 |
| RF | 0.90 | 0.872 | 0.863 / 0.871 / 0.882 | 0.866 / 0.905 / 0.846 | 0.170 |
| LSTM | 0.90 | 0.874 | 0.866 / 0.873 / 0.883 | 0.868 / 0.899 / 0.855 | 0.170 |
| PatchTST | 0.90 | 0.875 | 0.866 / 0.874 / 0.884 | 0.864 / 0.907 / 0.853 | 0.183 |
| DLinear | 0.90 | 0.876 | 0.864 / 0.876 / 0.888 | 0.864 / 0.911 / 0.854 | 0.187 |
| Mamba | 0.95 | 0.935 | 0.929 / 0.934 / 0.941 | 0.933 / 0.951 / 0.921 | 0.213 |
| Transformer | 0.95 | 0.934 | 0.927 / 0.935 / 0.941 | 0.933 / 0.949 / 0.921 | 0.212 |
| RF | 0.95 | 0.933 | 0.928 / 0.933 / 0.939 | 0.931 / 0.955 / 0.914 | 0.217 |
| LSTM | 0.95 | 0.934 | 0.928 / 0.935 / 0.940 | 0.931 / 0.952 / 0.920 | 0.218 |
| PatchTST | 0.95 | 0.935 | 0.929 / 0.934 / 0.943 | 0.931 / 0.956 / 0.919 | 0.234 |
| DLinear | 0.95 | 0.936 | 0.928 / 0.936 / 0.945 | 0.931 / 0.957 / 0.921 | 0.238 |

<!-- R30 / results/conformal.csv (mean of PICP, PICP_low, PICP_mid, PICP_high, PINAW by model x nominal [x horizon]) -->

**Coverage is below nominal.** Mean PICP is 0.872–0.876 for a nominal 0.90 and 0.933–0.936 for 0.95 <!-- R30 / results/conformal.csv -->. Only 127 of 720 combinations reach the nominal 0.90 (147 of 720 for 0.95); they are concentrated at site C (all horizons), D (mostly 6 h) and A (6 h) <!-- results/conformal.csv (PICP >= nominal: 0.90 -> C 90, D 32, A 5; 0.95 -> C 90, D 53, A 4) -->. Per combination, PICP ranges from 0.816 to 0.935 (0.90) and 0.893 to 0.973 (0.95) <!-- R30 / results/conformal.csv (min H PatchTST seed 1 1h; max C LSTM seed 0 6h) -->. The shortfall is largest at 1 h and decreases with horizon (Mamba 0.866 / 0.874 / 0.884), and coverage is lowest at G (0.838) and H (0.849) and highest at C (0.917), averaged over models (0.90) <!-- results/conformal.csv (mean PICP by site, nominal 0.90: A .883 B .876 C .917 D .890 E .858 F .882 G .838 H .849) -->. By wind-speed tercile, the high-wind tercile is covered worst (0.846–0.856 at 0.90), the middle tercile best (0.895–0.911); per site the high tercile falls to 0.799 at H and 0.800 at E <!-- results/conformal.csv (PICP_high by model; by site, nominal 0.90) --> (QA-T07-04). Split conformal guarantees coverage only for exchangeable data; a wind series, calibrated on July 2020–April 2021 and tested on April–December 2021, is not exchangeable, and the intervals do not attain their nominal coverage <!-- scripts/11_conformal.py:11-12; Section 2.4 (periods) -->. They are reported as an empirical calibration check, not as valid 90 % or 95 % intervals.

**Width.** Mean PICP is almost the same across models (within 0.004), so PINAW compares widths at equal coverage: Transformer and Mamba give the narrowest intervals (0.165 and 0.166 at 0.90), PatchTST and DLinear the widest (0.183 and 0.187), broadly in line with their RMSE <!-- R30 / results/conformal.csv (mean PINAW 0.90; PICP spread 0.872-0.876) -->.

## 3.5 CPU inference cost

Latency comes from `15_latency.py` only (`results/latency.csv`, run R04, 2026-11-10, laptop CPU) <!-- R04 / results/latency.csv; M18 (cost from latency.csv only) -->. Neural networks were timed with random weights in the tuned architecture (latency does not depend on weight values), after warm-up, as the median and 95th percentile of 50 calls (batch 1) or 10 calls (batch 256); Mamba-step was timed over 200 calls and RF over 30 <!-- scripts/15_latency.py:10-11, :68-80 (timeit), :103-112, :115 (Mamba-step 200), :128 (RF 30) -->. On CPU, Mamba's parallel scan runs through the PyTorch reference implementation <!-- CLAUDE.md §2 (falls back to a PyTorch scan on CPU); Section 2.5.1 -->; Mamba-step, the recurrent mode, matches the full forward pass to < 10⁻⁴ <!-- scripts/15_latency.py:91-99 (assert dev < 1e-4), :113-115 -->. RF was trained at site A with the tuned configuration and timed on one sample with one thread <!-- scripts/15_latency.py:121-128 -->. The model code has not changed since this measurement <!-- M18 qa (06_models.py unchanged since ef77872; tuned.json and latency.csv same commit 4e3bf67) -->.

**Table 3.5.** CPU latency in ms (Intel Core i5-13500H). Batch 1: median (95th percentile) per call. Batch 256: median per sample.

| Model | Batch 1, 1 thread | Batch 1, 4 threads | Batch 256, 1 thread | Batch 256, 4 threads |
|---|---|---|---|---|
| DLinear | 0.43 (0.70) | 0.39 (0.47) | 0.154 | 0.045 |
| Mamba-step | 1.62 (2.32) | 1.60 (2.52) | — | — |
| LSTM | 2.44 (3.57) | 2.45 (3.05) | 1.105 | 0.358 |
| Transformer | 2.91 (3.36) | 1.89 (2.75) | 1.963 | 0.506 |
| PatchTST | 5.68 (8.05) | 3.07 (6.54) | 4.831 | 1.464 |
| Mamba (parallel scan) | 22.36 (25.57) | 15.89 (23.78) | 22.198 | 16.502 |
| RF | 34.94 (64.63) | — | — | — |

<!-- R04 / results/latency.csv (ms_median, ms_p95 at batch 1; ms_per_sample at batch 256); — = not measured -->

For one new forecast with one thread, Mamba-step (1.6 ms) is faster than LSTM (2.4 ms), Transformer (2.9 ms) and PatchTST (5.7 ms) and slower only than DLinear (0.4 ms) <!-- R04 / results/latency.csv -->. Mamba-step requires a deployment that keeps the recurrent state from one 15-min step to the next; recomputing the 96-step window with the parallel scan costs 22.4 ms (15.9 ms with four threads), the slowest of the neural networks, and does not become cheaper per sample at batch 256 (22.2 ms) <!-- R04 / results/latency.csv -->. RF is the slowest single-sample predictor (34.9 ms) <!-- R04 / results/latency.csv (RF, batch 1, 1 thread) -->. Every model needs well under a second per forecast, far below the 15-min data interval; the differences matter for embedded or high-volume use, not for feasibility.

## 3.6 Disclosed deviations (Sections 3.1–3.5)

1. **Per-seed DM as the primary layer** and the paired t-test were chosen after the first E1 pass (M02, Section 2.6); the seed-ensemble DM is secondary and favours the neural networks over RF by construction (Section 3.2; QA-T06-03).
2. **Effect sizes added after the results were seen** (M18): ΔSS with 95 % CIs over five seeds, seed i of Mamba paired with seed i of the rival, as in the per-seed DM; the pairing is by seed index only (Welch CIs give the same conclusions). The CIs cover training randomness only, not the test-period sampling variability, and are not adjusted for multiplicity. No equivalence (TOST) test was run.
3. **PatchTST training:** 12 of 120 PatchTST rows (4 runs: A seed 4, E seed 2, G seed 3, H seed 2) ran to epoch 50 (the cap). In 3 of the 4 runs (A seed 4, G seed 3, H seed 2) early stopping (patience 10) had not triggered, so the cap ended training; E seed 2 (best epoch 40) stopped by early stopping at epoch 50. For A seed 4 the best epoch was the last one, so that run may be under-trained <!-- R28 / results/runs.csv (PatchTST epochs == 50: 12 rows; best_epoch 50/40/47/41; best_epoch == epochs: 3 rows); scripts/07_run_benchmark.py:129 (epoch loop to the cap), :170-176 (patience break) --> (QA-T05-02). One DLinear run (G seed 0, best epoch 41) was also ended by the cap <!-- results/runs.csv (DLinear epochs == 50: 3 rows) -->. PatchTST runs were spread over several Colab sessions and resumed run by run (R28); PatchTST was run last and extended to all eight sites by M10. PatchTST is below persistence at 1 h at D and H (Section 3.1; QA-T05-03).
4. **Regimes:** descriptive, no test; ramp subsets include ties at the 95th-percentile threshold, so counts are 1,309–1,328 per site and horizon (Section 3.3; QA-T06-07). The test period has no January–March.
5. **Prediction intervals:** the first conformal run (R29) is superseded (R29c): it lacked RF at A–D and used a slightly conservative quantile and a test-range PINAW denominator. R30 uses the exact k-th order statistic, the training-range denominator, and RF validation predictions at A–D regenerated with scikit-learn 1.9.1, whose test predictions match the stored ones exactly (20 of 20) <!-- R29c, R30; STATUS T07 round 2 (20/20 array_equal); M17 -->. The 95 % level is reported in addition to the 90 % level named in Section 2.5.4 <!-- scripts/11_conformal.py:109 (default alphas 0.1,0.05) -->. Coverage is below nominal (Section 3.4; QA-T07-04).
6. **Cost:** CPU latency only, from the 2026-11-10 measurement with random neural-network weights (R04). The parameter counts and training times planned in Section 2.5.4 are not reported, because `summary_cost.csv` mixes quantities that are not comparable between the neural networks and RF (RF "parameters" are tree nodes; its stored latency is a batch throughput, not a single-sample call) (QA-T06-05) <!-- M18; QA-T06-05 (STATUS T06); results/runs_rf.csv (params = node count, STATUS T07 round 2); scripts/15_latency.py:8 (RF single sample, not per-sample throughput as in 07) -->. Batch 256 and four threads were not measured for RF, nor batch 256 for Mamba-step.
7. **DM statistics are stored in single precision** (float32); no DM statistic is tabled here, and the win/loss flags reproduce exactly in an independent recompute (600 of 600; ensemble 120 of 120) (R31c; QA-T06-06).
8. **Tuning sites:** the shared hyper-parameters were selected on the validation partitions of A and D (Section 2.5.1), which are also E1 test sites.
