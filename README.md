# wind_forecast

Code and data for a comparative study of short-term (1 h, 3 h, 6 h) 100 m wind-speed forecasting at 8 Vietnamese sites. Mamba, Transformer, LSTM, PatchTST, DLinear and Random Forest (RF) are compared; persistence is the skill reference.

The study covers accuracy per site, CPU inference cost, cross-site transfer (leave-one-site-out, 8×8 matrix, few-shot) and explainability (SHAP). Work in progress: the experiment log is `tasks/RESULTS.md`.

## Data

- Source: NREL Southeast Asia Wind Toolkit v3. WRF at 9 km / 60 min, downscaled by the sup3r GAN to 3 km / 15 min. **This is modelled data, not measurements.**
- 8 sites, 100 m hub height, 2017–2021, 15 min, local time (UTC+7), 175,200 samples per site, no gaps:

| Regime | Sites |
|---|---|
| Inland | A, E |
| Coastal | B, F |
| Complex terrain | C, G |
| Offshore | D, H |

- 31 input features (`--features all`), or a 19-feature wind-only subset (`--features wind`). Input window: 96 steps (24 h).
- Split per site: chronological 70/15/15; no window crosses a boundary; MinMax scaling is fitted on train only. The test set is Apr–Dec 2021.
- `data_v2/`: processed dataset (`.npz`). Provenance: `data_v2/PROVENANCE.md`.
- `data_2016/`: out-of-period 2016 back-test set.
- `data/` (and the notebooks in `model/`) belong to an earlier, rejected version. Do not use them.

## Install

Python 3.12, launched with `py` on Windows. Run all commands from the repository root.

```
py -m pip install torch numpy pandas scipy scikit-learn
py -m pip install shap              # 10_shap.py only
py -m pip install global-land-mask  # 21_coast_distance.py only
```

Mamba needs no extra package: without the compiled `mamba-ssm` CUDA kernel, it falls back to a PyTorch scan. The device (`cuda` or `cpu`) is selected automatically.

Self-checks and a CPU smoke run (the last command can take over 10 minutes on CPU, because it evaluates the full validation and test sets):

```
py scripts/06_models.py
py scripts/08_aggregate.py --selftest
py scripts/11_conformal.py --selftest
py scripts/07_run_benchmark.py --sites A --models Mamba --seeds 1 --epochs 1 --max-batches 2 --out scratch/runs.csv
```

## Reproduce

Scripts with options accept `-h`. Scripts `07`, `09`, `16` and `18` resume: runs already in the `--out` CSV are skipped. To recompute committed results, use a new `--out` file in a new folder: checkpoints and predictions of `07` and `09` go next to it, but `08`, `11`, `13`, `14`, `16`, `17` and `18` always read `results/`.

### 1. Data (optional)

The processed datasets are committed, so this step is only needed to rebuild them (it overwrites `data_v2/` and `data_2016/`). Set the environment variables `NREL_API_KEY` and `NREL_EMAIL` first.

```
py scripts/01_download_seawtk.py --sites A,B,C,D,E,F,G,H --years 2017-2021
py scripts/02_verify_raw.py          # gate: stop if it fails
py scripts/03_build_dataset.py
py scripts/05_pack_for_colab.py      # .csv -> .npz

py scripts/01_download_seawtk.py --sites A,B,C,D,E,F,G,H --years 2016 --raw-dir data_raw_2016
py scripts/03_build_dataset.py --raw-dir data_raw_2016 --out-dir data_2016
py scripts/05_pack_for_colab.py data_2016
```

`04_data_pipeline.py` is the shared data contract (windows, split, scaling). Run it to print the splits and write the baselines:

```
py scripts/04_data_pipeline.py
```

### 2. Tuning

Same budget for all models, sites A and D, selected on validation only. Writes `results/tuned.json` (already committed). Re-running appends to `results/tune.csv`.

```
py scripts/12_tune.py --models RF
py scripts/12_tune.py --models LSTM,Transformer,Mamba,PatchTST,DLinear
```

### 3. Per-site benchmark

Neural models should run on a GPU. RF runs on CPU; run RF jobs one at a time (high memory use).

```
py scripts/07_run_benchmark.py --sites A,B,C,D,E,F,G,H --models RF --seeds 5 --out results/runs_rf.csv
py scripts/07_run_benchmark.py --sites A,B,C,D,E,F,G,H --models LSTM,Transformer,Mamba,PatchTST,DLinear --seeds 5
py scripts/07_run_benchmark.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 5 --features wind --out results/runs_wind.csv
py scripts/15_latency.py
```

### 4. Transfer

Steps `16`, `17` (neural models) and `18` (fine-tuning) need the weights from `07` or `09`. `--tuned results/tuned_rf_d16.json` limits RF to depth 16.

```
# global and leave-one-site-out
py scripts/09_global_loso.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 3 --features wind --out results/loso8_wind.csv
py scripts/09_global_loso.py --sites A,B,C,D,E,F,G,H --models RF --seeds 3 --features wind --tuned results/tuned_rf_d16.json --out results/loso8_rf_wind.csv

# 8x8 cross-site matrix
py scripts/16_cross_eval.py --sites A,B,C,D,E,F,G,H --models Mamba,Transformer,RF --seeds 3
py scripts/16_cross_eval.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 3 --features wind --out results/cross_eval_wind.csv

# few-shot (1, 2, 4 weeks)
py scripts/18_fewshot.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 3 --modes finetune,scratch --init-tag losoW8 --scratch-steps 2000 --const-calendar --out results/fewshot8_cc.csv
py scripts/18_fewshot.py --sites A,B,C,D,E,F,G,H --seeds 3 --modes ridge,rf --const-calendar --out results/fewshot8_cpu_cc.csv

# 2016 back-test, no retraining of neural models
py scripts/17_backtest_2016.py --sites A,B,C,D,E,F,G,H --models Mamba,Transformer,LSTM,DLinear,RF --seeds 5
```

### 5. Explainability, uncertainty, statistics

These read the predictions and weights in `results/`.

```
py scripts/10_shap.py --sites A,B,C,D,E,F,G,H --model Mamba --seed 0
py scripts/10_shap.py --sites A,B,C,D,E,F,G,H --model Mamba --seed 0 --models-dir results/models_loso --pattern "losoW8_{site}_{model}_{seed}.pt" --features wind --tag losoW8
py scripts/11_conformal.py --models Mamba
py scripts/08_aggregate.py           # summaries, Diebold-Mariano tests with Holm correction
py scripts/13_phase_check.py         # GAN steps vs WRF steps
py scripts/14_regime.py              # season, day/night, ramps
py scripts/19_site_checks.py         # diurnal cycle, site-ID classifier
py scripts/20_fewshot_range.py       # wind range coverage of few-shot windows (prints only)
py scripts/21_coast_distance.py
```

## Colab GPU runner

`notebooks/colab_resume.py` is the current runner (free T4). Paste it into one Colab cell, check the repository URL and Drive folder at the top, and run it. It mounts Drive, clones the repository, restores finished results, loads the prebuilt kernel (`WIND_FORECAST_DATA/kernels/` on Drive, required by the cell), then starts the job queue and a 5-minute sync to Drive in the background. Progress is in `results/run.log`. The commented block at its end is a status / keep-alive cell. After a runtime reset, run the cell again; finished runs are skipped. `notebooks/benchmark_colab.ipynb` is an older runner.

## Outputs

All outputs go to `results/`. Not every file is committed: model weights (`.pt`) are git-ignored, and some GPU results and predictions are stored on Drive.

| Script | Output |
|---|---|
| `04` | `baselines.csv` |
| `07` | `runs.csv` (or `--out`), `preds/`, `models/` (`preds_wind/`, `models_wind/` with `--features wind`) |
| `08` | `summary_by_site.csv`, `summary_overall.csv`, `summary_cost.csv`, `dm_tests.csv`, `dm_per_seed.csv`, `dm_per_seed_summary.csv` |
| `09` | `loso.csv` (or `--out`), `preds_loso/`, `models_loso/` |
| `10` | `shap_importance_*.csv`, `shap_temporal_*.csv`, `shap_*.npz` |
| `11` | `conformal.csv` |
| `12` | `tune.csv`, `tuned.json` |
| `13`, `14`, `15` | `phase_check.csv`, `regime.csv`, `latency.csv` |
| `16`, `17`, `18` | `cross_eval.csv`, `backtest_2016.csv`, `fewshot.csv` (or `--out`) |
| `19` | `diurnal_cycle.csv`, `site_id_classifier.csv` |
| `21` | `coast_distance.csv` |

RMSE and MAE are in m/s; skill = 1 − RMSE / RMSE of persistence.
