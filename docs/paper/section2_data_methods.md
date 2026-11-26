# 2. Data and Methods — draft v2 (26/11/2026)

> Draft v1 was written after meetings #6–#7; v2 aligns Sections 2.5.3, 2.5.4 and 2.6 with the transfer, few-shot, statistics and SHAP designs as they were run (meetings M07–M16). Numbers in this section are frozen inputs (data, configuration); results-dependent numbers live in Section 3. Items marked **[TODO]** need a figure or a final check. HTML comments give the source of each design statement (script:line or meeting Mxx).

## 2.1 Data source

All time series are taken from the NREL Southeast Asia Wind Toolkit v3 (SEA-WTK; Draxl et al., NREL/TP-5000-85481). They were retrieved through the Wind Toolkit Data Download API (endpoint `wtk-seasiawind-v3-download`) on 11 September 2026. SEA-WTK is a **modelled** dataset, not a measurement record. The Weather Research and Forecasting (WRF) model produces fields at 9 km / 60 min. The sup3r generative adversarial network (GAN) then downscales them to 3 km / 15 min, a 3× increase in spatial resolution and a 4× increase in temporal resolution. Three of every four 15-min samples are therefore GAN-generated. Section 2.6 tests whether this affects forecast skill.

We use the five years 2017-01-01 to 2021-12-31, sampled every 15 min in local time (UTC+7) at 100 m hub height. After the first 24 h are removed for the 24-h lag features, each site has 175,200 samples. The series contain no gaps and no missing values. The year 2016 is downloaded separately and used only as an out-of-period test set (Section 2.5.4).

Before modelling, every site passes a verification gate (`02_verify_raw.py`) with two checks:

1. **Interpolation check.** For each of the four 15-min phases (:00, :15, :30, :45), we compute the residual between the observed value and linear interpolation from its neighbours. A phase residual of exactly zero would reveal linearly interpolated data. All phases at all sites have residuals between 0.05 and 0.09 m/s.
2. **Label-leak check.** Two-point linear extrapolation must not reproduce the target at any phase.

An earlier dataset based on ERA5 was rejected by check 1, because three of its four phases had zero residual.

## 2.2 Study sites

The sites cover four wind regimes, with two sites per regime (Table 1). The first site of each regime (A–D) was chosen to represent a regime that is typical of Vietnamese wind-energy zones. The second sites (E–H) were added so that cross-site transfer could be evaluated both within and across regimes. They were selected with a gate fixed **before** any model results for them existed:

- at least 70 km from the existing site of the same regime;
- Pearson correlation of the 100 m wind-speed series with that site below 0.8;
- for coastal sites, mean wind speed of at least 6 m/s;
- for offshore sites, no island inside or adjacent to the grid cell.

**Candidates rejected by the gate**

| Candidate | Location | Reason |
|---|---|---|
| Tuy Phong | 11.22° N, 108.72° E | correlation 0.81 with B |
| Binh Thuan–Vung Tau shelf | 9.80° N, 108.60° E | correlation 0.95 with D |
| Bac Lieu, Soc Trang | – | mean 5.1–5.6 m/s |

**Deviation from the pre-registered gate.** We lowered the coastal mean threshold from 6.0 to 5.5 m/s after inspecting candidates. In SEA-WTK, only the Ninh Thuan–Binh Thuan belt exceeds 6 m/s, and its only candidate duplicated site B. Two checks confirm that the retained site F (Binh Dinh coast) is genuinely coastal:

- its mean diurnal cycle peaks at 14:00 local time, the afternoon sea-breeze phase, identical to site B. The inland sites peak at 18–19 h and the offshore sites at 18–23 h (Table 2);
- its grid cell lies about 3 km inland of the shoreline, based on a 1-km land–sea mask (`21_coast_distance.py`). Site B lies about 10 km inland.

**Table 1.** Study sites (SEA-WTK v3, 100 m, 2017–2021).

| Site | Regime | Location | Grid cell (lat, lon) | Mean (m/s) | Std (m/s) |
|---|---|---|---|---|---|
| A | Inland | Red River Delta (Ha Noi) | 20.995, 105.790 | 4.50 | 2.15 |
| B | Coastal | Ninh Thuan coast | 11.722, 109.109 | 7.28 | 3.30 |
| C | Complex terrain | Central Highlands (Gia Lai) | 14.002, 108.012 | 5.56 | 2.48 |
| D | Offshore | South-central shelf | 10.492, 109.301 | 8.05 | 3.75 |
| E | Inland | Thanh Hoa lowland | 19.843, 105.543 | 3.80 | 1.90 |
| F | Coastal | Binh Dinh coast | 13.848, 109.274 | 5.73 | 2.87 |
| G | Complex terrain | Huong Hoa (Quang Tri) | 16.640, 106.640 | 7.10 | 2.99 |
| H | Offshore | Gulf of Tonkin | 20.304, 107.189 | 6.43 | 3.15 |

**Table 2.** Mean diurnal cycle of 100 m wind speed (local time; `results/diurnal_cycle.csv`).

| Site | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| Hour of maximum | 19 | 14 | 5 | 18 | 18 | 14 | 20 | 23 |
| Relative amplitude | 0.46 | 0.12 | 0.30 | 0.04 | 0.47 | 0.24 | 0.19 | 0.13 |

**[TODO Fig. 1]** Map of the eight sites, with wind-speed distributions shown as insets.

## 2.3 Input features and target

The download contains 18 raw variables:

- wind speed at 10, 40, 80, 100, 120, 160 and 200 m;
- wind direction at 10, 80, 100 and 120 m;
- temperature at 10, 80, 100 and 120 m;
- pressure at 0, 100 and 200 m.

From these we derive 31 input features (`03_build_dataset.py`; Table 3). Every lag and rolling statistic looks only backward, and rolling windows are not centred. The target is the 100 m wind speed at t + h, for h ∈ {1 h, 3 h, 6 h} (4, 12 and 24 steps). Labels are produced by the sliding window and are never stored as features.

**Table 3.** Input features. "W" marks the 19-feature wind-only subset used for the transfer experiments (Section 2.5.3).

| Group | Features | W |
|---|---|---|
| Hub wind and persistence | `wind_speed`, lags 15 min / 1 h / 3 h / 6 h / 24 h, rolling mean 1 h and 6 h, rolling std 1 h, increments over 15 min and 1 h | ✓ |
| Wind profile (speeds) | wind speed at 10, 80, 120 and 200 m | ✓ |
| Calendar | sin/cos of hour of day, sin/cos of month | ✓ |
| Direction | sin/cos of direction, u and v components | |
| Profile shape | shear exponent α between 80 and 120 m and over 10–200 m; veer between 120 and 80 m | |
| Thermodynamic | temperature, pressure, air density p/(R·T) at 100 m, ΔT between 10 and 100 m (stability proxy), ΔP between 0 and 200 m | |

## 2.4 Forecasting setup

**Samples.** Each sample is a 96-step (24 h) input window **x**_{t−95:t} ∈ ℝ^{96×31}. A single model predicts all three horizons jointly through a multi-output head.

**Data split.** Each site is split chronologically into 70 % training, 15 % validation and 15 % test data:

| Set | Period | Windows per site |
|---|---|---|
| Train | Jan 2017 – Jul 2020 | 122,520 |
| Validation | Jul 2020 – Apr 2021 | 26,162 |
| Test | Apr – Dec 2021 | 26,161 |

The split is **purged**. A window is valid only if its whole input span and its label at t + 24 lie inside one partition. As a result, no training window contains rows that serve as validation or test labels.

**Scaling.** Features and target are min–max scaled using statistics from the training partition of the same site only. Predictions are transformed back to m/s before scoring.

Because the test year 2021 begins in April, it contains no Northeast-monsoon core (January–March). The 2016 back-test (Section 2.5.4) fills this gap.

## 2.5 Models and experiments

### 2.5.1 Models

We compare six forecasters and two reference predictors. All neural models use a hidden width of 64. Each one ends with the same head, a 64 → 32 linear layer, ReLU, and a 32 → 3 linear layer. The head reads the representation at the last time step, except for DLinear and PatchTST, which use their native flatten heads.

- **Mamba.** Two selective state-space (S6) blocks: `d_state` = 16, expansion factor 2, causal depthwise convolution of width 4, pre-LayerNorm, residual connections (Gu & Dao, 2024). The selective scan runs on the official `mamba-ssm` CUDA kernel, compiled for the T4 (sm_75). We verified it against a reference PyTorch scan. For CPU deployment we also implement Mamba-step, a recurrent single-step inference mode that carries the SSM and convolution state forward, so each new 15-min sample costs O(1).
- **Transformer.** Encoder only: 2 layers, 4 heads, feed-forward width 128, sinusoidal positional encoding.
- **LSTM.** Two stacked layers of 64 units.
- **PatchTST.** Patch length 16, stride 8, 2 encoder layers, 4 heads (Nie et al., 2023). Reversible instance normalisation (RevIN) is treated as a tuned option.
- **DLinear.** Moving-average decomposition with kernel 25 and linear trend and seasonal maps (Zeng et al., 2023).
- **Random forest (RF).** 500 trees, `max_features` = √p, `min_samples_split` = 5, `min_samples_leaf` = 2. The input is the feature vector at time t; lags are already present as engineered features.
- **Persistence.** v̂(t + h) = v(t). This is the skill reference for every result.
- **Climatology.** Mean wind speed of the training partition.

**Training.** All neural models are trained under the same protocol:

- MSE loss, AdamW optimiser;
- weight decay 0.01, applied only to weight matrices, never to biases, normalisation parameters or the SSM Δ-bias;
- linear learning-rate warm-up over one epoch, then ReduceLROnPlateau (factor 0.5, patience 3);
- gradient clipping at norm 1.0, mixed precision, batch size 128;
- at most 50 epochs, with early stopping on validation MSE (patience 10); the weights with the best validation score are restored.

**Hyper-parameter tuning.** We use a fixed grid that is identical in size across model families. It is evaluated on sites A and D, and configurations are selected on the validation set only (`12_tune.py`):

| Model | Grid | Selected |
|---|---|---|
| LSTM, Transformer, Mamba | lr ∈ {3·10⁻⁴, 10⁻³} × dropout ∈ {0.1, 0.2} | Mamba: lr 3·10⁻⁴, dropout 0.1; Transformer: 3·10⁻⁴, 0.2; LSTM: 10⁻³, 0.2 |
| PatchTST | lr ∈ {3·10⁻⁴, 10⁻³} × RevIN ∈ {off, on}, dropout 0.1 | lr 3·10⁻⁴, RevIN off |
| DLinear | lr ∈ {3·10⁻⁴, 10⁻³} | lr 10⁻³ |
| RF | max_depth ∈ {12, 16, 24} | 24 |

The selected configuration is then used unchanged at all eight sites. Every neural configuration is trained with five random seeds.

**Hardware.** Neural models were trained on an NVIDIA T4 (Google Colab). RF, latency measurements and all statistics ran on a laptop CPU (Intel Core i5-13500H, 16 GB RAM).

### 2.5.2 E1 — per-site benchmark

At each of the eight sites, every model is trained and tested on that site's own data (5 seeds for each model and site). In addition to the individual seeds, we report the **seed ensemble**, the mean of the five seeds' predictions, as a separate method.

### 2.5.3 Cross-site transfer

The aim is to estimate how well a model forecasts at a site with no local training history.

- **Cross-site matrix (8 × 8).** A model trained at source site s is applied without retraining to target site s′, using the target's own scaler. Pairs are labelled same-regime or cross-regime. The matrix is computed for Mamba with W and, with the 31 features, for Mamba, Transformer and RF, each with three seeds. <!-- scripts/16_cross_eval.py:13, :102 (same_regime); STATUS T03 scope (Mamba W, 3 seeds); RESULTS R09, R24 (31 features, 3 seeds) -->
- **Leave-one-site-out (LOSO) and pooled (global) model.** LOSO has eight folds. In each fold the model is trained on the pooled training partitions of the other seven sites, with early stopping on their pooled validation partitions, and is tested on the held-out site, which it has never seen (zero-shot). The global model is trained on the pooled training partitions of all eight sites and tested on each of them; it has seen the target's training data and serves as an upper reference. <!-- scripts/09_global_loso.py:83-86 (train/val of training sites, test of test sites), :112-115 (folds: global = all sites, loso = all but one); README.md:97 (--sites A..H); M08 --> Neither model receives a site identifier. <!-- scripts/09_global_loso.py:9-10; STATUS Approved decisions 2026-11-08 --> Every site, the held-out one included, is min–max scaled with the statistics of its own training partition; we call this "zero-shot with target climatology scaling": no target labels are used in training, but target data are used for the scaler. <!-- scripts/09_global_loso.py:12-15, :89-90; M13 (5) --> Mamba with W is trained with the E1 configuration (Section 2.5.1) and three seeds per fold. <!-- scripts/09_global_loso.py:121-123, :129-130 (tuned.json); README.md:97 (--seeds 3); M08 --> RF with W, also with three seeds, is the comparator; it uses max_depth 16 instead of the tuned 24. <!-- README.md:98 (--tuned results/tuned_rf_d16.json); results/tuned_rf_d16.json; M07, M08 --> Each target's regime partner stays in the training pool, so LOSO measures transfer to unseen sites, not to unseen regimes. <!-- scripts/09_global_loso.py:115; M13 qa --> The original plan, a four-fold LOSO and a global model on sites A–D, was replaced by this design because four target sites cannot reach p < 0.125 (M08; Section 3.6, item 1).
- **Feature sets (E7).** The transfer feature set was chosen in a preliminary four-fold LOSO ablation on sites A–D with RF. It compared the full 31-feature set with two subsets: the 19-feature wind-only set W (Table 3), and a 27-feature set that adds direction (sin/cos, u, v), shear, veer and ΔT between 10 and 100 m to W. <!-- scripts/04_data_pipeline.py:146-149 (FEATURE_SETS wind, relative); RESULTS R07; M05 (W is the transfer configuration) --> These four-fold runs are superseded by the eight-fold design (Section 3.6, item 1). **[TODO: decide whether the four-fold E7/E8 ablation (R07, R12) is reported, e.g. in a supplement.]** In the reported experiments W is compared with the 31-feature set at the own site (E1 with 31 features vs E1 with W, five seeds each) and in the cross-site matrix. <!-- STATUS T03 scope; RESULTS R22, R23, R24 -->

  We test the hypothesis that the absolute thermodynamic features act as a latent site identifier and thereby hamper transfer. To do this, an RF classifier (8 classes, 2,500 training and 2,500 test samples per site, raw unscaled values) is trained to recognise the site from a single time step. Using the five thermodynamic features it reaches 92.7 % accuracy; using the 19 W features it reaches 49.8 % (chance level 12.5 %).

  In the same preliminary ablation we also tested a delta target, y(t + h) − v(t), with the full feature set and with W. <!-- scripts/09_global_loso.py:93-97 (--delta); RESULTS R07, R12 -->
- **Few-shot adaptation (E9).** For each target site t and k ∈ {1, 2, 4} weeks, the fitting data are the last k × 672 samples (15 min) of t's training partition up to and including one of two window ends: 31 March 2020 23:45 (DB, Northeast monsoon) and 30 June 2020 23:45 (TN, Southwest monsoon). <!-- scripts/18_fewshot.py:34 (WINDOWS), :35 (STEPS_PER_WEEK = 7·96), :86-88 (end sample included); M12 (4), QA-T02-02 --> This gives six cells (2 windows × 3 values of k) per site, at all eight sites, with three seeds. <!-- README.md:105-106 (--sites A..H --seeds 3); M11 --> All methods use the wind-only set W and the min–max scaler fitted on t's full training partition (target climatology scaling). Validation and test sets are those of site t, except under inner validation (below). <!-- scripts/18_fewshot.py:10-12, :69, :77 (features wind) --> Each k-week window lies inside one calendar month, so the month features are constant during fitting. <!-- scripts/03_build_dataset.py:98-99 (month number); M12 -->

  | Method | Role | Starting point | Fitting on the k weeks |
  |---|---|---|---|
  | Fine-tune, free calendar | main | LOSO-W Mamba of the same seed, which has never seen t | learning rate 10⁻⁴, at most 30 epochs, early-stopping patience 5 epochs, one warm-up epoch |
  | Fine-tune, constant calendar | ablation | as above | as above, with the month features held constant |
  | Mamba from scratch, constant calendar | reference | random initialisation | E1 learning rate (3·10⁻⁴); fixed budget of 2,000 optimiser steps, early-stopping patience 400 steps, 100 warm-up steps, each rounded up to whole epochs |
  | Ridge, constant calendar | reference | — | scikit-learn `Ridge` with default regularisation (α = 1) on the 19 W features at time t |
  | RF, constant calendar | reference | — | E1 RF configuration (Section 2.5.1, max_depth 24) on the same inputs as Ridge |

  <!-- fine-tune: scripts/18_fewshot.py:51-52 (30 epochs, patience 5), :96-101 (init models_loso/<init-tag>_<t>_<model>_<seed>.pt), :114-115 (lr 1e-4); README.md:105 (--init-tag losoW8); scripts/07_run_benchmark.py:75 (warmup_epochs=1). scratch: 18_fewshot.py:56-58, :116-119; results/tuned.json (Mamba lr 3e-4); M07. Ridge: 18_fewshot.py:123-128. RF: 18_fewshot.py:67, :121-122; results/tuned.json (RF max_depth 24). Roles: M12 (2), M14 (2), STATUS Approved decisions 2026-11-25 (M14) -->

  Both neural modes use batch size 64 and the E1 optimiser, weight decay and dropout. The patience of the learning-rate scheduler is scaled to 400 optimiser steps in both modes. <!-- scripts/18_fewshot.py:110-113, :130-132; scripts/07_run_benchmark.py:117; M12 (1) --> The first candidate checkpoint is the one after epoch 1, so fine-tuning cannot return the zero-shot initialisation. <!-- scripts/07_run_benchmark.py:125, :170-172; M16 (5) --> "Constant calendar" means that `month_sin` and `month_cos` are held at their value at the end of the k-week window in the fitting, validation and test inputs; the input dimension is unchanged. <!-- scripts/18_fewshot.py:60, :107-109; M12 --> For Ridge and RF the free-calendar variant is run as a sensitivity check; it is identical to the constant-calendar variant by construction, because the month features are constant inside the window. <!-- README.md:106; STATUS T12 planned runs; RESULTS R19, R20, R25c -->

  Two further references need no fitting: the zero-shot LOSO-W model (no target labels) and persistence. The **oracle reference** is, for each site, cell and horizon, the reference with the lowest median-seed test RMSE among scratch, Ridge and RF (all with constant calendar). Because it is chosen on the test set, it is conservative against fine-tuning. <!-- scripts/23_fewshot_stats.py:13, :49 (REFS), :103-106; M14 (2) --> A validation-selected reference (lowest median-seed validation MSE per site and cell, the same for all horizons) is a secondary comparison under target validation. <!-- scripts/23_fewshot_stats.py:14, :107-109; M14 (3) -->

  Two validation protocols are run:

  - **Target validation** (main): the neural modes use the full validation partition of t (about nine months, Section 2.4) for early stopping, checkpoint selection and the learning-rate schedule; Ridge and RF are fitted without validation data (their validation MSE is used only for the validation-selected reference). <!-- scripts/18_fewshot.py:10, :79, :127 (Ridge val MSE), :133 (target val restored); scripts/07_run_benchmark.py:46, :63-64 (RF fit on idx_train, val MSE recorded); M14 qa (~39 weeks) -->
  - **Inner validation** (sensitivity, no target-validation early stopping): for the neural modes the last 20 % of the k-week window (⌊0.2 n⌋ samples) is held out for validation, the 120 samples before it are dropped (96-step input window + 24-step horizon, so that fitting and validation windows do not overlap), and the model is fitted on the remaining samples without refit. It is run for fine-tune (free calendar) and scratch (constant calendar); Ridge and RF keep their full k-week fits. <!-- scripts/18_fewshot.py:61, :103-105, :112 (steps per epoch from the fit subset); scripts/23_fewshot_stats.py:16-17, :47-48 (IV_FILES); M15 -->

  Target data therefore enter all protocols through the scaler, the calendar choice (pilot below) and, at sites A and D, the tuning (Section 3.6, item 8).

  **Post-hoc changes to the baseline.** The step budget for training from scratch was set after a pilot run (M07). In that run the original epoch-based schedule (≈ 300 steps for one week) stopped while the model was still on its initial plateau. After a later QA finding (M12), the from-scratch baseline was revised before the eight-site runs: the scheduler patience was scaled to steps for both fine-tuning and scratch; the calendar handling for scratch was chosen on validation MSE only, in a pilot (sites A–D, one seed), and frozen before any test score was used; Ridge was added; and the window was extended to include its last sample (23:45). The first scratch baseline (R18) is reported as invalid. The step budgets of fine-tuning (epochs) and scratch (steps) differ. <!-- M07; M12 (1)-(5) and pilot v2 follow-up; M14 (7); RESULTS R18 -->

### 2.5.4 Robustness analyses

- **2016 back-test.** The trained E1 models are applied without retraining to 2016 (35,040 samples per site), using the 2017–2020 scalers, and scored season by season. Because 2016 precedes the training period, this is a backward-in-time evaluation.
- **GAN-phase check.** Test RMSE is computed separately at WRF-native time steps (on the hour) and at GAN-generated steps (:15, :30, :45).
- **Regime analysis.** Skill is computed by monsoon season and by day (06:00–18:00) versus night. It is also computed for ramp events, defined as the largest 5 % of |v(t + h) − v(t)| for each site and horizon.
- **Uncertainty.** We use split conformal prediction, with absolute validation residuals as the calibration set, at nominal coverage 90 % (α = 0.1). We report the coverage probability (PICP) and the normalised interval width (PINAW), overall and by wind-speed tercile.
- **Explainability.** Expected-gradients SHAP (`shap.GradientExplainer`) is computed for two models, seed 0 only, at all eight sites: the per-site E1 Mamba with 31 features, and the eight-fold LOSO Mamba-W model whose held-out site is the explained site. <!-- README.md:117-118; scripts/25_shap_check.py:27-30 (TAGS Mamba_0, losoW8_Mamba_0); M09 (3) --> At each site, 1,000 test windows are explained against a background of 200 windows from that site's training partition, both drawn at random with seed 0; each explained window uses 200 integration samples. <!-- scripts/10_shap.py:64-66 (defaults n-explain 1000, n-background 200, nsamples 200), :104-106, :111-116 --> Attributions φ refer to the min–max-scaled model output and have one value per window, input step (96), feature and horizon. We report two importance measures per feature: mean |φ| over windows and input steps, and a net measure, the mean over windows of |Σ_t φ| over the 96 input steps. <!-- scripts/10_shap.py:117, :130; scripts/25_shap_check.py:92 --> Attributions are aggregated by the feature groups of Table 3, with shear and veer counted in the wind-profile group, and by lag. <!-- scripts/10_shap.py:29-41 (GROUPS), :131 (temporal) -->

  Two checks use forward passes only, with the stored attributions and checkpoints (`25_shap_check.py`):

  - *completeness error*, mean |Σ φ − (f(x) − E f)| / mean |f(x) − E f| over the explained windows, where E f is the mean output over the background, per horizon and pooled over horizons; <!-- scripts/25_shap_check.py:46-48; scripts/10_shap.py:120-125 (same pooled definition) -->
  - *provenance*: the background and test indices are rebuilt and must match the stored ones; the checkpoint outputs for the explained windows, transformed back to m/s, are compared with the stored test predictions of the same model (maximum and mean absolute difference). As a negative control (run separately from the script), the stored test predictions of seeds 0 and 1 are compared in the same way. <!-- scripts/25_shap_check.py:73-77, :100-110; RESULTS R27, R27c (negative control, CPU recompute at A and H) -->

  The planned RF TreeSHAP comparison and the `air_density` negative control were not run (Section 3.6, item 9).
- **Cost.** We report:
  - trainable parameters and training time;
  - CPU inference latency for batch sizes 1 and 256, with 1 and 4 threads, measured after warm-up;
  - for Mamba, both the parallel scan and Mamba-step.

## 2.6 Evaluation and statistics

**Metrics.** RMSE, MAE and R² in m/s. Skill relative to persistence is SS = 1 − RMSE_model / RMSE_persistence, and every table carries the persistence baseline.

**Pairwise tests (per-site benchmark, E1).** Diebold–Mariano tests are used only for the window-level comparisons of the per-site benchmark. <!-- M01, M02; scripts/08_aggregate.py:38-55 (dm_test) -->

- **Test statistic.** Diebold–Mariano tests on squared-error loss differentials with the Harvey–Leybourne–Newbold small-sample correction. The HAC variance uses a Bartlett kernel with lag max(h − 1, 96), so that the 24-h overlap of input windows is covered.
- **Multiple comparisons.** p-values are adjusted with the Holm procedure within each family (site × horizon).
- **Seed-level evidence.** We report the number of seeds (out of five) on which one model beats another, and a paired t-test across seeds.

**Transfer tests.** The unit of analysis is the **target site** (n = 8), not the individual window. <!-- M06; M13 (3); STATUS Approved decisions 2026-11-25 (M13) -->

- **LOSO and global model.** For each method and site, the RMSE is the median over the three seeds. Per-site skill is SS = 1 − RMSE_model / RMSE_ref, with persistence as reference, or RF-W when Mamba-W is compared with RF-W. <!-- scripts/22_transfer_stats.py:8-10, :51, :94, :101 -->
- **Test.** The primary test is the exact two-sided Wilcoxon signed-rank test on the eight per-site skills. The same test on the RMSE difference, RMSE_ref − RMSE_model (m/s), is the secondary version. p-values are Holm-adjusted over the three horizons of each comparison, with no adjustment across comparisons. We report wins out of 8, mean and median skill, and the rank-biserial correlation r_rb. The exact test requires that no per-site value is zero or tied in magnitude; otherwise the computation stops. <!-- scripts/22_transfer_stats.py:42-45 (rank_biserial), :48-64 (compare: exact two-sided, Holm per comparison), :56-57; M13 (3) -->
- **Comparisons.** Mamba-W vs persistence, RF-W vs persistence and Mamba-W vs RF-W, for LOSO and for the global model. The tests vs persistence are repeated for each seed as a sensitivity check. <!-- scripts/22_transfer_stats.py:83-101; M13 (4) -->
- **Post-hoc choice.** This test was chosen after the first eight-fold LOSO results had been seen (M13). The original plan compared zero-shot skill with persistence by window-level DM tests; these are not reported (Section 3.6, item 2). <!-- scripts/22_transfer_stats.py:10; M13 (3) -->
- **Own-site W vs 31 features and cross-site matrix.** Differences in skill are tested across the eight sites or targets with the Wilcoxon signed-rank test, Holm-adjusted over horizons. **[TODO: no committed script computes the R22/R23 p-values; confirm the exact two-sided variant and add the computation in T06.]** <!-- RESULTS R22 ("Wilcoxon exact Holm"), R23 -->

**Few-shot tests.** The statistics were fixed before all runs were complete (M14), with the disclosure given in Section 3.6, item 8. <!-- M14 -->

- For each method and cell, the RMSE is the median over the three seeds. Skill vs a reference is computed per cell and averaged over the six cells of each site; the RMSE difference is the difference of the six-cell mean RMSEs. Both are tested with the exact two-sided Wilcoxon signed-rank test, n = 8, Holm over the three horizons of each comparison. <!-- scripts/23_fewshot_stats.py:11-12, :78-88, :103; M14 (1) -->
- The one primary comparison is fine-tune (free calendar) vs the oracle reference. Secondary comparisons, each its own Holm family and not adjusted across comparisons: vs persistence, vs zero-shot LOSO-W, vs each of scratch, Ridge and RF, vs the validation-selected reference, and fine-tune with constant vs free calendar. Fine-tune vs Ridge and RF with free calendar is a sensitivity check. Results by k and by cell are descriptive. <!-- scripts/23_fewshot_stats.py:51-55 (PAIRS); M14 (2)-(4) -->
- Under inner validation the same statistics are computed without the validation-selected reference and without the constant-calendar fine-tune. This sensitivity run is reported whatever its result; a sign change relative to target validation limits the claim. <!-- scripts/23_fewshot_stats.py:16-17, :56 (IV_PAIRS), :107; M15; M16 -->

**Pre-registration and deviations.** The following were fixed before the corresponding results were seen:

- the tuning grid;
- the site-selection gate;
- the test statistics of the per-site benchmark.

The few-shot statistics were fixed while the runs were incomplete, after a few rows had been seen (M14; Section 3.6, item 8).

The post-hoc deviations are disclosed where they occur: the coastal mean threshold (Section 2.2), the step budget for training from scratch and the later revision of the from-scratch baseline (Section 2.5.3; M07, M12), and the choice of the transfer test (above; M13). Further changes to the planned design (eight-fold LOSO, RF depth 16 in LOSO, the SHAP controls not run) are listed in Section 3.6.

## Data and code availability
SEA-WTK v3 is publicly available from NREL. Download, verification, feature construction, all experiments and statistics are reproducible from the project repository (`scripts/01`–`25`). **[TODO: DOI/Zenodo snapshot at submission]**
