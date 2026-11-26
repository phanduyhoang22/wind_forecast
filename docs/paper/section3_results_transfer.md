# 3. Results — transfer, few-shot adaptation and explainability (draft v1, 26/11/2026)

> Draft of the Results parts whose experiments are finished and whose claims are fixed by meetings M13–M16 and the T04 QA. T08 adds the per-site benchmark (E1), regimes and conformal intervals; places that need them are marked **[TODO T06]**. Subsection numbers are provisional. Each number carries an HTML comment with its source (run_id in `tasks/RESULTS.md` and/or a committed CSV). All data are modelled (NREL SEA-WTK v3), not measurements. Skill SS = 1 − RMSE_model / RMSE_ref (%), reference = persistence unless stated; RMSE in m/s on the test partition (Apr–Dec 2021).

**Statistical conventions.** The unit of analysis is the target site (n = 8). The primary test is the exact two-sided Wilcoxon signed-rank test on per-site skill computed from the median-seed RMSE; the same test on the RMSE difference (RMSE_ref − RMSE_model, m/s) is the secondary version. p-values are Holm-adjusted over the three horizons of each comparison. With n = 8 the smallest raw p is 0.0078 and the smallest Holm p is 0.023 <!-- results/transfer_stats.csv (p_raw 0.0078125, p_holm 0.0234375) -->. We report wins out of 8 sites and the rank-biserial correlation r_rb.

## 3.1 Per-site benchmark (E1)

**[TODO T06]** E1 tables. Below, the only E1 numbers used are the own-site skill of Mamba with W and with 31 features (R22), as the no-transfer reference.

## 3.2 Zero-shot transfer: leave-one-site-out (LOSO, 8 folds)

In each fold, Mamba with the wind-only set W is trained on the other seven sites (early stopping on their validation partitions) and applied without retraining to the held-out site, which is scaled with min–max statistics of its own training partition ("zero-shot with target climatology scaling"). Three seeds per fold. RF-W (max_depth 16) is the comparator; the pooled ("global") model trained on all eight sites is an upper reference that has seen the target's training data.

**Table 3.2a.** Per-site skill (%) vs persistence, median seed.

| Site | Regime | LOSO Mamba-W 1 h | 3 h | 6 h | LOSO RF-W 1 h | 3 h | 6 h | Global Mamba-W 1 h | 3 h | 6 h |
|---|---|---|---|---|---|---|---|---|---|---|
| A | Inland | 11.3 | 10.2 | 15.3 | 9.5 | 10.6 | 15.8 | 15.1 | 19.0 | 25.7 |
| B | Coastal | 2.6 | 0.6 | 3.9 | 3.5 | 4.5 | 7.0 | 12.2 | 15.3 | 19.5 |
| C | Complex | 16.6 | 18.9 | 25.6 | 8.3 | 7.8 | 11.3 | 19.0 | 24.3 | 33.3 |
| D | Offshore | 0.5 | −1.1 | −7.0 | 0.9 | −7.1 | −13.0 | 6.7 | 2.7 | 3.5 |
| E | Inland | 13.7 | 13.0 | 19.1 | 9.1 | 9.5 | 14.4 | 18.6 | 25.7 | 34.7 |
| F | Coastal | 9.4 | 12.8 | 20.1 | 6.3 | 7.7 | 10.8 | 17.6 | 24.0 | 34.0 |
| G | Complex | 11.7 | 15.5 | 20.3 | 8.9 | 9.2 | 11.7 | 16.0 | 22.9 | 28.9 |
| H | Offshore | 5.3 | −0.1 | 1.5 | 3.6 | −2.9 | −3.1 | 7.7 | 9.4 | 12.1 |
| Mean | | 8.9 | 8.7 | 12.4 | 6.3 | 4.9 | 6.9 | 14.1 | 17.9 | 24.0 |

<!-- R21, R21c, R16 / results/transfer_per_site.csv (seed == median); means = results/transfer_stats.csv (metric skill, seed median, column mean) -->

**Table 3.2b.** Transfer tests (exact two-sided Wilcoxon, n = 8, Holm over horizons). Mean skill %; for "Mamba-W vs RF-W" skill = 1 − RMSE_Mamba / RMSE_RF.

| Comparison | h | Mean SS | Wins/8 | r_rb | Holm p (skill) | Holm p (RMSE diff.) |
|---|---|---|---|---|---|---|
| LOSO Mamba-W vs persistence | 1 h | 8.9 | 8 | 1.00 | **0.023** | **0.023** |
| | 3 h | 8.7 | 6 | 0.78 | 0.078 | 0.078 |
| | 6 h | 12.4 | 7 | 0.83 | 0.078 | 0.078 |
| LOSO RF-W vs persistence | 1 h | 6.3 | 8 | 1.00 | **0.023** | **0.023** |
| | 3 h | 4.9 | 6 | 0.78 | 0.109 | 0.109 |
| | 6 h | 6.9 | 6 | 0.61 | 0.148 | 0.109 |
| LOSO Mamba-W vs RF-W | 1 h | 2.9 | 6 | 0.83 | 0.117 | 0.117 |
| | 3 h | 4.0 | 6 | 0.72 | 0.117 | 0.117 |
| | 6 h | 6.0 | 6 | 0.83 | 0.117 | 0.117 |
| Global Mamba-W vs persistence | 1 / 3 / 6 h | 14.1 / 17.9 / 24.0 | 8 / 8 / 8 | 1.00 | 0.023 each | 0.023 each |
| Global Mamba-W vs global RF-W | 1 / 3 / 6 h | 3.4 / 5.3 / 7.5 | 8 / 8 / 8 | 1.00 | 0.023 each | 0.023 each |

<!-- R21, R21c, R16 / results/transfer_stats.csv (seed median; metric skill and d_rmse) -->

**Zero-shot skill.** LOSO Mamba-W beats persistence at all eight unseen sites at 1 h (mean 8.9 %, median 10.4 %, Holm p = 0.023) <!-- R21 / results/transfer_stats.csv (losoW Mamba persistence median skill 1h: mean 0.0889, median 0.1039, wins 8, p_holm 0.0234) -->; this is the only horizon with a significant improvement. At 3 h and 6 h the mean skill stays positive (8.7 % and 12.4 %; wins 6/8 and 7/8) but is not significant (Holm p = 0.078 both) <!-- R21 / results/transfer_stats.csv -->. The losses sit offshore: D is below persistence at 3 h (−1.1 %) and 6 h (−7.0 %), H marginally at 3 h (−0.1 %); the coastal site B gains only 0.6–3.9 % <!-- R21 / results/transfer_per_site.csv -->. The RMSE-difference test agrees (Table 3.2b). Against the own-site E1-W model (14.19 / 18.23 / 24.09 %) <!-- R22 / results/runs_wind.csv (median seed, mean A–H) -->, zero-shot transfer gives up about 5 / 9 / 12 pp <!-- derived: R22 − R21 (14.19−8.89, 18.23−8.74, 24.09−12.36) -->, while the pooled model reaches the own-site level (14.1 / 17.9 / 24.0 %) <!-- R21c / results/transfer_stats.csv (globalW Mamba persistence median skill) -->; these two comparisons are descriptive, not tested.

**Mamba vs RF.** LOSO Mamba-W has a lower RMSE than LOSO RF-W on average (2.9 / 4.0 / 6.0 %) at 6 of 8 sites per horizon, but not significantly (Holm p = 0.117 each) <!-- R21c / results/transfer_stats.csv (losoW Mamba RF median skill) -->: a consistent direction, not a superiority. RF-W is better at B at all horizons <!-- results/transfer_per_site.csv (losoW median RMSE B: Mamba 0.624/1.183/1.479, RF 0.618/1.138/1.430) -->. In the pooled setting Mamba-W wins 8/8 (Holm p = 0.023) <!-- R21c / results/transfer_stats.csv (globalW Mamba RF) -->, but that setting is not zero-shot. LOSO covers only Mamba and RF, so a transfer advantage cannot be attributed to the Mamba architecture.

**Seed sensitivity (Table 3.2c).** The 1 h result holds for seeds 1 and 2 but not for seed 0, which loses at B (−5.0 %) and D (−0.8 %) and gives Holm p = 0.117 on skill or 0.078 on the RMSE difference <!-- R21c / results/transfer_stats.csv (losoW Mamba persistence seed 0); results/transfer_per_site.csv (seed 0, 1h) -->. At 3 h and 6 h seed 1 alone would reach Holm p < 0.05, the other seeds would not; we report the seed median. Per-site signs change across seeds at B (all horizons), D (1 h) and H (3 h, 6 h) <!-- results/transfer_per_site.csv (losoW Mamba seeds 0,1,2) -->. RF is practically seed-invariant.

**Table 3.2c.** LOSO Mamba-W vs persistence per seed (mean skill %, wins/8, Holm p on skill).

| Seed | 1 h | 3 h | 6 h |
|---|---|---|---|
| 0 | 7.7, 6/8, 0.117 | 8.4, 7/8, 0.117 | 12.1, 7/8, 0.117 |
| 1 | 9.4, 8/8, 0.023 | 9.3, 6/8, 0.039 | 13.0, 7/8, 0.031 |
| 2 | 9.4, 8/8, 0.023 | 7.4, 5/8, 0.219 | 11.4, 5/8, 0.219 |
| median | 8.9, 8/8, 0.023 | 8.7, 6/8, 0.078 | 12.4, 7/8, 0.078 |

<!-- R21, R21c / results/transfer_stats.csv (losoW, Mamba, persistence, skill, seeds 0/1/2/median) -->

LOSO keeps the target's regime partner in the training pool (fold D trains on H), so these are transfers to unseen sites, not unseen regimes; we make no regime-level claim. Sites A and D were also the tuning sites (Section 2.5.1).

## 3.3 Cross-site matrix and the wind-only feature set

Each single-site model is applied without retraining to every target (target training scaler). Per target we average skill over the own site, the one same-regime source and the six cross-regime sources.

**Table 3.3a.** Mamba-W, skill (%) vs the target's persistence, median seed of 3.

| Target | Own 1 h | 3 h | 6 h | Same 1 h | 3 h | 6 h | Cross 1 h | 3 h | 6 h |
|---|---|---|---|---|---|---|---|---|---|
| A | 14.8 | 17.6 | 25.8 | 2.7 | 7.5 | 15.0 | 2.6 | 3.5 | 8.3 |
| B | 12.4 | 15.9 | 19.1 | −4.7 | −3.3 | 0.7 | −19.4 | −19.1 | −19.5 |
| C | 19.1 | 23.5 | 31.5 | 8.7 | 15.4 | 22.3 | −1.3 | −2.1 | 5.2 |
| D | 6.4 | 5.0 | 6.1 | −10.4 | −9.2 | −20.7 | −37.3 | −50.9 | −53.3 |
| E | 18.0 | 24.8 | 34.1 | 3.5 | 16.3 | 27.9 | 7.6 | 6.3 | 13.7 |
| F | 16.2 | 23.8 | 34.1 | 4.4 | 8.3 | 17.4 | −1.0 | 2.1 | 9.6 |
| G | 17.5 | 25.1 | 31.6 | 7.5 | 13.3 | 20.8 | −5.1 | −2.3 | 2.8 |
| H | 7.7 | 8.6 | 11.4 | 2.5 | 4.7 | 6.7 | −12.0 | −22.0 | −20.1 |
| Mean | 14.0 | 18.0 | 24.2 | 1.8 | 6.6 | 11.3 | −8.2 | −10.6 | −6.7 |

<!-- R23 / results/cross_eval_wind.csv (median RMSE over seeds 0-2 per source-target-horizon; persistence from results/baselines.csv) -->

**Table 3.3b.** Mean skill (%) over 8 targets, Mamba, median seed; W − 31 in pp with Holm p (Wilcoxon over targets).

| Group | 31 features 1 / 3 / 6 h | W 1 / 3 / 6 h | W − 31 (pp) | Holm p |
|---|---|---|---|---|
| Own site (3 seeds) | 16.2 / 21.9 / 27.9 | 14.0 / 18.0 / 24.2 | see text (R22) | — |
| Same regime | −3.8 / 1.6 / 6.8 | 1.8 / 6.6 / 11.3 | +5.6 / +5.0 / +4.4 | 0.297 / 0.297 / 0.164 |
| Cross regime | −19.4 / −19.6 / −16.1 | −8.2 / −10.6 / −6.7 | +11.2 / +9.1 / +9.4 | 0.031 / 0.031 / 0.023 |

<!-- R23, R24 / results/cross_eval_wind.csv, results/cross_eval_nn.csv (model Mamba), results/baselines.csv; Holm p from R23 -->

**W costs skill at the own site.** With five seeds, E1-W Mamba reaches 14.19 / 18.23 / 24.09 % against 16.05 / 21.81 / 27.95 % with 31 features (−1.87 / −3.58 / −3.86 pp); W is better at 1 / 0 / 0 of 8 sites (Holm p = 0.023 each) <!-- R22 / results/runs_wind.csv, results/runs.csv (Mamba, median seed) -->. The 1 h difference depends on seed aggregation (seed mean: Holm p = 0.055) <!-- R22 -->.

**W helps across regimes.** W raises cross-regime skill by 11.2 / 9.1 / 9.4 pp (Holm p = 0.031 / 0.031 / 0.023) <!-- R23 -->, consistent with the E7 site-identification result (Section 2.5.3). The same-regime gain (5.6 / 5.0 / 4.4 pp) is not significant (Holm p ≥ 0.164) <!-- R23 -->. Even with W, single-source transfer does not beat persistence: same- and cross-regime skill do not differ significantly from zero <!-- R23 -->, and cross-regime skill is positive at only 2 / 3 / 5 of 8 targets, against 6 / 6 / 7 for the same-regime source <!-- results/cross_eval_wind.csv (targets with skill > 0, median seed) -->. Offshore D is the hardest target (cross-regime −37.3 to −53.3 %) <!-- results/cross_eval_wind.csv -->. Same-regime sources beat cross-regime ones by 10.0 / 17.2 / 18.0 pp (Holm p = 0.023 each) <!-- R23 -->. The same-regime group is one site pair per target, and the targets are not independent (each site is also a source).

With 31 features, Transformer and RF show the same ordering own > same > cross (Table 3.3c; seed means, R24, not to be mixed with the median-seed rows), so the pattern is not specific to Mamba. Pooling seven sources (LOSO-W, 8.9 / 8.7 / 12.4 %) is on average better than the single same-regime source (1.8 / 6.6 / 11.3 %) <!-- R21 / results/transfer_stats.csv; R23 / results/cross_eval_wind.csv -->; descriptive, not tested.

**Table 3.3c.** 31 features, seed mean of 3, mean skill (%) over 8 targets (own / same / cross).

| Model | 1 h | 3 h | 6 h |
|---|---|---|---|
| Mamba | 16.0 / −4.6 / −20.9 | 21.8 / 0.4 / −20.0 | 27.8 / 7.7 / −16.3 |
| Transformer | 15.3 / −5.3 / −23.3 | 21.9 / 4.7 / −13.6 | 28.1 / 9.9 / −9.3 |
| RF | 15.5 / −3.0 / −17.9 | 20.1 / 2.9 / −16.6 | 25.2 / 5.8 / −14.3 |

<!-- R09, R24 / results/cross_eval_nn.csv, results/cross_eval_rf.csv, results/baselines.csv (skill per seed, then mean over seeds) -->

## 3.4 Few-shot adaptation

Each target gets k ∈ {1, 2, 4} weeks of local data in two seasonal windows (Northeast monsoon, ending 31 March 2020 23:45; Southwest monsoon, ending 30 June 2020 23:45; `scripts/18_fewshot.py`): six cells per site. The LOSO-W model that never saw the target (Section 3.2) is fine-tuned on these weeks. References are fitted from scratch on the same weeks: Mamba (random initialisation), Ridge and RF on the 19 W features. The statistics were fixed before completion (M14): median-seed RMSE per cell (3 seeds), skill per cell, mean over the six cells per site, test across the 8 sites. The primary comparison is fine-tune vs the *oracle* reference, the lowest test RMSE of {scratch, Ridge, RF} per site, cell and horizon; chosen on test, it is conservative against fine-tuning. Other comparisons are secondary (own Holm family each); by-week numbers are descriptive.

Two protocols are reported. With **target validation** (R25) the neural models use the target's validation partition (about nine months) for checkpoint selection, early stopping and the learning-rate schedule. With **inner validation** (R26) there is no target-validation early stopping: the last 20 % of the k-week window (after a 120-sample gap) is held out for it. Ridge and RF use the full k-week fits in both. Wording: k weeks for fitting, the target validation set (R25) or an inner split (R26) for early stopping, target-climatology scaling.

**Table 3.4a.** Few-shot tests, fine-tune with free calendar: mean skill % / wins of 8 / Holm p. Skill vs a reference = 1 − RMSE_fine-tune / RMSE_ref.

| Comparison | Protocol | 1 h | 3 h | 6 h |
|---|---|---|---|---|
| vs oracle reference (primary) | target val. (R25) | 15.2 / 8 / **0.023** | 21.7 / 8 / **0.023** | 22.9 / 8 / **0.023** |
| | inner val. (R26) | 13.2 / 8 / **0.023** | 20.5 / 8 / **0.023** | 22.0 / 8 / **0.023** |
| vs persistence | target val. (R25) | 9.7 / 8 / 0.023 | 11.2 / 7 / 0.031 | 15.6 / 7 / 0.031 |
| | inner val. (R26) | 6.9 / 6 / 0.117 | 8.2 / 6 / 0.117 | 12.2 / 7 / 0.117 |
| vs zero-shot LOSO-W | target val. (R25) | 0.8 / 5 / 0.313 | 2.6 / 6 / 0.078 | 3.7 / 8 / 0.023 |
| | inner val. (R26) | −2.2 / 1 / 0.070 | −0.7 / 3 / 0.766 | −0.1 / 3 / 0.844 |
| vs zero-shot, RMSE difference | target val. (R25) | p 0.250 | p 0.078 | p 0.023 |
| | inner val. (R26) | p 0.047 | p 0.766 | p 0.766 |
| fine-tune const vs free calendar | target val. (R25) | −1.4 / 1 / 0.031 | −3.1 / 0 / 0.023 | −3.8 / 1 / 0.031 |

<!-- R25, R25c / results/fewshot8_stats.csv; R26 / results/fewshot8_iv_stats.csv (metric skill unless stated; d_rmse rows for the RMSE difference) -->

**Table 3.4b.** Descriptive mean skill (%) vs persistence, 8 sites × 6 cells, median seed.

| Method | target val. (R25) 1 / 3 / 6 h | inner val. (R26) 1 / 3 / 6 h |
|---|---|---|
| Fine-tune (free calendar) | 9.7 / 11.2 / 15.6 | 6.9 / 8.2 / 12.2 |
| Fine-tune (const calendar) | 8.4 / 8.4 / 12.4 | — |
| Zero-shot LOSO-W (no target data) | 8.9 / 8.7 / 12.4 | 8.9 / 8.7 / 12.4 |
| Oracle reference (best of the three below) | −9.1 / −15.8 / −11.1 | −10.5 / −20.3 / −15.3 |
| Scratch Mamba (const calendar) | −86.2 / −40.1 / −25.2 | −129.0 / −73.6 / −53.5 |
| Ridge | −10.5 / −23.2 / −19.7 | −10.5 / −23.2 / −19.7 |
| RF | −149.8 / −75.5 / −51.8 | −149.8 / −75.5 / −51.8 |

<!-- R25, R25c / results/fewshot8_per_site.csv; R26 / results/fewshot8_iv_per_site.csv (weeks == all, seed == median, mean over sites) -->

**Against the from-scratch references.** In both protocols the LOSO-pretrained, fine-tuned model beats the oracle k-week reference at all eight sites and horizons (15.2 / 21.7 / 22.9 % with target validation, 13.2 / 20.5 / 22.0 % with inner validation; Holm p = 0.023 each) <!-- R25 / results/fewshot8_stats.csv; R26 / results/fewshot8_iv_stats.csv (role primary, metric skill) -->. This is the few-shot claim, and it comes with a weak reference: the oracle reference is itself below persistence (−9.1 / −15.8 / −11.1 % in R25) <!-- R25c / results/fewshot8_per_site.csv (best_test) -->. It shows the value of pre-training over fitting k weeks from scratch, not a gain over a strong baseline. The references improve with more weeks while fine-tuning barely moves: at 1 h with target validation the oracle goes from −23.0 % (1 week) to +2.0 % (4 weeks), fine-tuning stays at 9.4–10.1 % <!-- R25 / results/fewshot8_per_site.csv (weeks 1/2/4, seed median, 1h) --> (descriptive).

**Against zero-shot.** There is no consistent gain over the zero-shot model that fine-tuning starts from. With target validation the gain is small (0.8 / 2.6 / 3.7 %) and significant only at 6 h (Holm p = 0.023), for the seed median only; seed 1 alone is not significant at any horizon <!-- R25, R25c / results/fewshot8_stats.csv -->. With inner validation the sign changes: −2.2 / −0.7 / −0.1 %, wins 1 / 3 / 3, and at 1 h the RMSE is 0.015 m/s higher (RMSE-difference Holm p = 0.047; skill p = 0.070) <!-- R26 / results/fewshot8_iv_stats.csv (zero_shot rows; d_rmse 1h mean −0.0153) -->. Under the frozen M15 rule this sign change limits the claim: we claim no consistent gain over zero-shot, and we do not generalise the one significant difference (the 1 h loss under inner validation, RMSE-difference version). In R25 the median selected epoch is 1 (144 runs) <!-- results/fewshot8_ft_free.csv (best_epoch, median over 144 runs) -->.

**Against persistence.** Fine-tuning beats persistence significantly only with target validation (9.7 / 11.2 / 15.6 %, Holm p = 0.023 / 0.031 / 0.031) <!-- R25 / results/fewshot8_stats.csv -->. With inner validation skill stays positive (6.9 / 8.2 / 12.2 %) but wins drop to 6 / 6 / 7 and Holm p = 0.117 each <!-- R26 / results/fewshot8_iv_stats.csv -->. In R25, offshore D loses to persistence at 3 h (−1.1 %) and 6 h (−4.9 %) <!-- R25c / results/fewshot8_per_site.csv (finetune_free, D) -->, and seed 2 also at 1 h <!-- R25c -->. R26 changes several things at once, so the R25–R26 difference cannot be attributed to the validation signal alone (Section 3.6, item 8).

**Calendar handling.** Holding the month features constant in fine-tuning lowers skill vs the free variant by 1.4 / 3.1 / 3.8 % (Holm p = 0.031 / 0.023 / 0.031) <!-- R25 / results/fewshot8_stats.csv (finetune_cc vs finetune_free) -->; the free variant is the main one, as fixed beforehand (M12, M14). For Ridge and RF the two calendar variants are identical by construction (month features are constant inside a k-week window) <!-- R25c / results/fewshot8_stats.csv (ridge_free = ridge_cc, rf_free = rf_cc) -->, which is not robustness evidence.

## 3.5 Explainability (SHAP)

Expected-gradients SHAP was computed for the per-site Mamba with 31 features (E1) and the LOSO Mamba-W model, seed 0 only, 1,000 test windows and 200 training-window backgrounds per site. All statements refer to one seed; we make no stability claim.

**Sanity checks.** The completeness error |Σφ − (f(x) − E f)| / |f(x) − E f| is 0.059–0.118, i.e. 6–12 % <!-- R27 / results/shap_completeness.csv (horizons 1h/3h/6h, both tags) -->. It never decreases with horizon (16/16 model–site pairs) and is largest at A, 6 h, E1 (0.118) <!-- results/shap_completeness.csv -->. Pooled over horizons it is 0.064–0.094 (E1) and 0.066–0.085 (LOSO-W) (Table 3.5a) <!-- R27 / results/shap_completeness.csv (horizon all) -->. So 6–12 % of the prediction deviation is left unexplained, and small share differences should not be read. Model outputs recomputed from the stored checkpoints match the stored test predictions within a maximum of 0.009–0.018 m/s per site and a mean of at most 0.0032 m/s (16/16) <!-- R27 / results/shap_provenance.csv -->; mixed-precision inference is the likely cause, unproven, as the check had no negative control (QA-T04-08).

**Table 3.5a.** Completeness error, pooled over horizons (range over 1 / 3 / 6 h).

| Site | E1 Mamba-31 | LOSO Mamba-W |
|---|---|---|
| A | 0.094 (0.070–0.118) | 0.085 (0.070–0.101) |
| B | 0.072 (0.069–0.074) | 0.079 (0.071–0.087) |
| C | 0.073 (0.070–0.075) | 0.076 (0.069–0.084) |
| D | 0.064 (0.063–0.065) | 0.069 (0.063–0.075) |
| E | 0.087 (0.070–0.101) | 0.079 (0.067–0.094) |
| F | 0.082 (0.072–0.090) | 0.073 (0.068–0.080) |
| G | 0.072 (0.062–0.081) | 0.066 (0.059–0.073) |
| H | 0.066 (0.061–0.071) | 0.072 (0.062–0.084) |

<!-- R27 / results/shap_completeness.csv -->

**Two importance measures.** Mean |φ| over windows and time steps counts positive and negative attributions of a feature at different lags as importance. We also report a net measure, mean over windows of |Σ_t φ| over the 96 input steps. Per feature, the ratio 96 × mean |φ| / net has median 2.9 (E1) and 3.1 (LOSO-W) and maximum 37.2 (E1, D, `month_sin`, 1 h) <!-- R27 / results/shap_importance_Mamba_0.csv, results/shap_importance_losoW8_Mamba_0.csv, results/shap_net_importance.csv (ratio 96*mean_abs_shap/mean_abs_net, all site-horizon-feature rows) -->: much of the per-step attribution cancels over time.

**Table 3.5b.** Share (%) of mean |φ| by feature group, mean over 8 sites. E1 "wind profile" includes shear and veer (Table 3).

| Model | Group | 1 / 3 / 6 h |
|---|---|---|
| E1 Mamba-31 | Hub wind and persistence | 25.4 / 22.6 / 23.3 |
| | Wind profile | 23.8 / 23.0 / 20.3 |
| | Calendar | 20.3 / 21.2 / 21.0 |
| | Direction | 17.0 / 19.2 / 18.7 |
| | Thermodynamic | 13.5 / 14.0 / 16.7 |
| LOSO Mamba-W | Wind profile | 47.0 / 43.8 / 39.8 |
| | Hub wind and persistence | 33.9 / 35.5 / 37.2 |
| | Calendar | 19.0 / 20.7 / 22.9 |

<!-- R27 / results/shap_importance_Mamba_0.csv, results/shap_importance_losoW8_Mamba_0.csv (sum of share by group per site-horizon, mean over sites) -->

**What the attributions support.** At 1 h the top-ranked feature is a wind speed (hub or another height) at every site, in both models and under both measures <!-- results/shap_importance_*.csv, results/shap_net_importance.csv (rank 1, 1h) -->. Which height ranks first is not robust: `ws_200m` is first in 16/24 (E1) and 24/24 (LOSO-W) site–horizon cells under mean |φ|, but in 8/24 and 12/24 under the net measure, and the top-1 feature changes in 11 and 12 of 24 cells <!-- R27 / results/shap_importance_*.csv, results/shap_net_importance.csv (rank-1 counts) -->. The wind speeds at different heights are correlated, so their split, and the group totals of Table 3.5b, partly reflect the grouping (QA-T04-04). We claim no dominance of any single height. For E1 at 3 h and 6 h the net measure ranks a direction (`v_wind`), calendar (`hr_cos`) or thermodynamic (`air_density`) feature first in 8 of 16 cells <!-- results/shap_net_importance.csv (Mamba_0, rank 1, 3h/6h) -->.

The calendar share depends on the measure: about one fifth of mean |φ| (Table 3.5b), but a net share at 1 h of 7.9 % (E1) and 10.9 % (LOSO-W), rising to 18.0 % and 18.9 % at 6 h <!-- results/shap_net_importance.csv (hr_sin, hr_cos, month_sin, month_cos; sum of share, mean over sites) -->. In E1 the three largest cancellation ratios are month features (B and D, 1 h) <!-- results/shap_importance_Mamba_0.csv, results/shap_net_importance.csv (top-3 ratios 22.4, 28.1, 37.2) -->. We do not read the calendar share as a physical effect (QA-T04-06). That LOSO-W attributes more to wind speed and profile follows from its feature set; it is not evidence of why W transfers better.

The planned RF TreeSHAP comparison and the `air_density` negative control were not done. `air_density` is not in W and, in E1, ranks in the top three by mean |φ| in 10 of 24 cells <!-- results/shap_importance_Mamba_0.csv (air_density rank <= 3) -->, so it cannot serve as a null feature (QA-T04-05). The SHAP results are descriptive, without a validated physical interpretation.

## 3.6 Disclosed deviations (Sections 3.2–3.5)

1. **LOSO is 8-fold** (M08: n = 4 cannot reach p < 0.125), not the 4-fold A–D design of Section 2.5.3. The 4-fold results (R06–R08, R15) are superseded; some of their files were overwritten, and no reported number depends on them (M09). **[TODO: update Section 2.5.3.]**
2. **Transfer test chosen after R21** (M13): exact Wilcoxon on per-site skill of the median-seed RMSE, plus the RMSE-difference version. The DM tests for zero-shot vs persistence foreseen in Section 2.6 are not reported. No extra seeds were added (optional stopping). **[TODO: align Section 2.6.]**
3. **Target climatology scaling** in all transfer and few-shot settings: "zero-shot" means no target labels in training, not no target data.
4. **Tuning sites A and D** (Section 2.5.1) are also LOSO targets.
5. **RF depth:** RF-W in LOSO uses max_depth 16, not the tuned 24 (M07, R16).
6. **Cross-site design:** one same-regime source per target; targets are not independent.
7. **Few-shot baseline revised post hoc (M12).** The first scratch baseline (R18) was invalid. The scheduler patience was scaled to steps for fine-tune and scratch; constant month features were chosen for scratch on validation MSE in a pilot; Ridge was added. Step budgets differ: fine-tune 30 epochs / patience 5, scratch 2,000 steps / patience 400 / 100 warm-up steps (M14).
8. **Few-shot target-data use and R26 confounds.** In R25 fine-tune and scratch use the ~9-month target validation set for checkpoint, early stopping and LR schedule; Ridge and RF do not. All protocols use target data for the scaler, the constant-calendar choice (M12 pilot) and tuning (A, D). R26 (M15) removes the validation signal but also shrinks the fit data by 24–38 %, drops the most recent data and changes the checkpoint/LR signal; fine-tuning cannot return the zero-shot initialisation (selection starts after epoch 1) (R26, M16). The statistics plan was fixed while runs were incomplete, after the Leader had seen a few R25 rows (M14).
9. **SHAP:** seed 0 only; RF TreeSHAP and the `air_density` control not done; completeness error 6–12 %; provenance check without negative control (R27, QA-T04-05, QA-T04-08).
