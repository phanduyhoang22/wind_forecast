# 2. Data and Methods — draft v1 (15/11/2026)

> Draft written after meetings #6–#7. Numbers in this section are frozen inputs (data, configuration); results-dependent numbers live in Section 3. Items marked **[TODO]** need a figure or a final check.

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

- **Cross-site matrix (8 × 8).** A model trained at source site s is applied without retraining to target site s′, using the target's own scaler. Pairs are labelled same-regime or cross-regime.
- **Pooled (global) and leave-one-site-out (LOSO).** The global model is trained on the pooled training partitions of sites A–D and tested on each site. In LOSO, the model is trained on three sites and tested on the fourth, which it has never seen (zero-shot).
- **Feature-set ablation (E7).** We compare the full 31-feature set with two subsets: the 19-feature wind-only set W (Table 3), and a 27-feature set that adds direction and profile-shape features to W.

  We test the hypothesis that the absolute thermodynamic features act as a latent site identifier and thereby hamper transfer. To do this, an RF classifier (8 classes, 2,500 training and 2,500 test samples per site, raw unscaled values) is trained to recognise the site from a single time step. Using the five thermodynamic features it reaches 92.7 % accuracy; using the 19 W features it reaches 49.8 % (chance level 12.5 %).

  We also test a delta target, y(t + h) − v(t), in combination with the full feature set and with W.
- **Few-shot adaptation (E9).** For a new site t with k ∈ {1, 2, 4} weeks of local data, we compare two strategies:

  | Strategy | Starting point | Training |
  |---|---|---|
  | Fine-tune | LOSO-W model that has never seen t | learning rate 10⁻⁴ on the k weeks |
  | From scratch | random initialisation | fixed budget of 2,000 optimiser steps, early-stopping patience 400 steps, 100 warm-up steps |

  An RF trained on the same k weeks serves as a further reference. The k-week windows end on 31 March 2020 (Northeast monsoon) or 1 July 2020 (Southwest monsoon). Validation and test sets are those of site t. Scalers use the climatological statistics of site t's training partition; we state this assumption explicitly.

  The step budget for training from scratch was set after a pilot run. In that run the original epoch-based schedule (≈ 300 steps for one week) stopped while the model was still on its initial plateau.

### 2.5.4 Robustness analyses

- **2016 back-test.** The trained E1 models are applied without retraining to 2016 (35,040 samples per site), using the 2017–2020 scalers, and scored season by season. Because 2016 precedes the training period, this is a backward-in-time evaluation.
- **GAN-phase check.** Test RMSE is computed separately at WRF-native time steps (on the hour) and at GAN-generated steps (:15, :30, :45).
- **Regime analysis.** Skill is computed by monsoon season and by day (06:00–18:00) versus night. It is also computed for ramp events, defined as the largest 5 % of |v(t + h) − v(t)| for each site and horizon.
- **Uncertainty.** We use split conformal prediction, with absolute validation residuals as the calibration set, at nominal coverage 90 % (α = 0.1). We report the coverage probability (PICP) and the normalised interval width (PINAW), overall and by wind-speed tercile.
- **Explainability.** Expected-gradients SHAP (GradientExplainer) is computed for 1,000 test windows against 200 training-window backgrounds. We aggregate attributions by feature group and by lag, for the per-site Mamba and the Mamba-W LOSO model. As a sanity check we report the completeness error, |Σ SHAP − (f(x) − E f)| relative to |f(x) − E f|.
- **Cost.** We report:
  - trainable parameters and training time;
  - CPU inference latency for batch sizes 1 and 256, with 1 and 4 threads, measured after warm-up;
  - for Mamba, both the parallel scan and Mamba-step.

## 2.6 Evaluation and statistics

**Metrics.** RMSE, MAE and R² in m/s. Skill relative to persistence is SS = 1 − RMSE_model / RMSE_persistence, and every table carries the persistence baseline.

**Pairwise tests.**

- **Test statistic.** Diebold–Mariano tests on squared-error loss differentials with the Harvey–Leybourne–Newbold small-sample correction. The HAC variance uses a Bartlett kernel with lag max(h − 1, 96), so that the 24-h overlap of input windows is covered.
- **Multiple comparisons.** p-values are adjusted with the Holm procedure within each family (site × horizon).
- **Seed-level evidence.** We report the number of seeds (out of five) on which one model beats another, and a paired t-test across seeds.

**Transfer tests.** The unit of analysis is the **target site**, not the individual window.

- Same-regime and cross-regime skill are compared with a Wilcoxon signed-rank test across target sites.
- Zero-shot skill is compared with persistence using DM tests, Holm-adjusted.
- We report the median across seeds together with the seed range.

**Pre-registration and deviations.** The following were fixed before the corresponding results were seen:

- the tuning grid;
- the site-selection gate;
- the choice of test statistics.

The two post-hoc deviations are reported above: the coastal mean threshold (Section 2.2) and the step budget for training from scratch (Section 2.5.3).

## Data and code availability
SEA-WTK v3 is publicly available from NREL. Download, verification, feature construction, all experiments and statistics are reproducible from the project repository (`scripts/01`–`20`). **[TODO: DOI/Zenodo snapshot at submission]**
