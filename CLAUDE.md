# wind_forecast

## 1. Overview
- Research paper (target Q1–Q3 journal): short-term (1h/3h/6h) 100 m wind-speed forecasting at 8 Vietnamese sites; Mamba (focus) vs Transformer, LSTM, PatchTST, DLinear, RF; persistence is the skill reference.
- Four questions: accuracy per site, CPU inference cost, cross-site transfer (LOSO, 8×8 matrix, few-shot), explainability (SHAP).
- Current phase: transfer experiments + writing (Section 2 drafted). Success = significant, honest claims vs persistence and baselines (DM/Wilcoxon + Holm).

## 2. Stack & environment
- Python: `py` (Python 3.12 user install, `C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe`). OVERRIDE of the kit rule "use `D:\Project\.venv`": User decided 2026-11-21 to keep `py` 3.12 for this project (all results so far were produced with it). Do not switch.
- Key libs: torch (CPU locally; Colab torch 2.14.1+cu130), scikit-learn, pandas, numpy, scipy, shap, python-docx, pypdf, global-land-mask.
- Mamba uses the official `mamba-ssm` `selective_scan_cuda` kernel built for T4 (sm_75): `MyDrive/WIND_FORECAST_DATA/kernels/selective_scan_cuda_sm75_torch2.14.1.so`; falls back to a PyTorch scan on CPU.
- Env vars (names only): `NREL_API_KEY`, `NREL_EMAIL` (User environment; never write values anywhere).
- GPU: Google Colab free T4 via MCP `colab`. Local CPU: i5-13500H, 16 GB RAM (RF depth 24 on ≥4 sites risks MemoryError; run RF jobs one at a time).

## 3. Commands
- download data: `py scripts/01_download_seawtk.py` (needs NREL_* env vars) → verify gate: `py scripts/02_verify_raw.py` → build: `py scripts/03_build_dataset.py` → pack for Colab: `py scripts/05_pack_for_colab.py`
- per-site benchmark (E1): `py scripts/07_run_benchmark.py --sites A,B,C,D --models RF,Mamba --seeds 5 [--features wind]`
- global / LOSO: `py scripts/09_global_loso.py --sites A,B,C,D,E,F,G,H --models Mamba --seeds 3 --features wind --out results/loso8_wind.csv`
- cross-site 8×8: `py scripts/16_cross_eval.py --sites A,...,H [--features wind]`; few-shot: `py scripts/18_fewshot.py --modes finetune,scratch,rf`
- aggregate + DM tests: `py scripts/08_aggregate.py`; regimes: `py scripts/14_regime.py`; conformal: `py scripts/11_conformal.py`; SHAP: `py scripts/10_shap.py`
- test (QA runs this): self-checks built into scripts — `py scripts/06_models.py` (kernel vs reference scan), `py scripts/08_aggregate.py --selftest` / `py scripts/11_conformal.py --selftest` (check argparse first); smoke run: `py scripts/07_run_benchmark.py --sites A --models Mamba --seeds 1 --epochs 1 --max-batches 2 --out <scratch>/runs.csv`. No `tests/` folder yet.
- lint: ruff not used in this repo (skip and say so).

## 4. Structure
- `scripts/` — numbered pipeline `01`–`21` (data, models, experiments, stats, checks). Entry points only; no `src/` yet.
- `data_v2/` — processed 8-site dataset (`.npz` committed, `.csv` git-ignored) + `PROVENANCE.md`. Read-only.
- `data_2016/` — 2016 back-test set. `data_raw*/` — raw NREL downloads (git-ignored, read-only). `data/` — OLD ERA5 set, rejected (do not use).
- `results/` — CSV results, `tuned.json`; `preds*/`, `models*/` (large, mostly git-ignored).
- `notebooks/colab_resume.py` — current Colab runner (setup + keep-alive cells); `notebooks/benchmark_colab.ipynb` — older runner. `docs/` — plan, journal, meetings, paper drafts. `References/`, `tailieu_rieng/` (copyrighted PDFs, git-ignored).

## 5. Data
- Source: NREL Southeast Asia Wind Toolkit v3 (WRF 9 km/60 min → sup3r GAN 3 km/15 min). MODELLED data, never "measurements".
- 8 sites (A–H, 2 per regime: Inland, Coastal, Complex terrain, Offshore), 100 m hub, 2017–2021, 15 min, local time UTC+7, 175,200 samples/site, 0 gaps; 31 features (W subset = 19 wind-only).
- Split: chronological 70/15/15 per site, purged (no window crosses a boundary); MinMax fitted on train only. Test = Apr–Dec 2021; 2016 = out-of-period back-test.
- Details: `data_v2/PROVENANCE.md`, `docs/paper/section2_data_methods.md`.

## 6. Key documents
- `docs/NHAT_KY_DU_AN.md` — full Vietnamese project log, all meeting minutes #1–#8 and results (read first for history).
- `docs/Ke_hoach_du_an_v2.docx` — approved plan v2.0. `docs/Tong_quan_du_an.docx` — project overview (Vietnamese).
- `docs/paper/section2_data_methods.md` — paper Section 2 draft. `paper_wind_prediction_ver2.md` — OLD draft (outdated data claims; do not reuse numbers).
- `docs/meetings/*_brief.md` — meeting briefs.

## 7. Development pipeline
data → per-site benchmark (E1) → transfer (LOSO / cross-site / few-shot) → explainability & uncertainty → statistics & aggregation → paper writing → submission.
Current stage: **transfer** (Mamba 8-fold LOSO running) with writing started. Details: `tasks/ROADMAP.md`. Submission needs User approval.

## 8. Project rules & overrides
- Every result reported with persistence skill; DM test (HAC lag max(h−1, 96), HLN, Holm); per-seed evidence; transfer stats unit = target site (Wilcoxon, n = 8).
- Same tuning grid for all models, selected on validation only (`results/tuned.json`); 5 seeds per config (LOSO 8-fold: 3 seeds, meeting #8).
- Post-hoc deviations must be disclosed in the paper (coastal threshold 6.0→5.5 m/s; scratch step budget).
- Project decisions go through an agent meeting first (now `/meeting`, minutes in `tasks/MEETINGS.md`).
- OVERRIDE of the kit rule "ask before `pip install`": User allows installing any package a task needs without asking (2026-11-15, re-confirmed 2026-11-21). Install with `py -m pip install <pkg>`, then name what was installed in the reply and in NHATKY.md. Installed so far beyond the base stack: `global-land-mask` (local), `shap` (Colab, each session).
- ROADMAP target dates stay TBD by User decision (2026-11-21); work proceeds stage by stage.
- Colab runner: `notebooks/colab_resume.py` (setup cell + keep-alive cell). The MCP notebook opens empty after each reset — paste the setup cell, run it, then add the status cell.
- Commits: no Claude attribution (User request).
- Reasoning effort (User, 2026-11-21): every chat chooses the effort itself, per task, including the `effort` of worker/qa subagents, without asking: low for keep-alives and bookkeeping, higher for meetings, QA, statistics and writing.
- Start of every Leader shift (User, 2026-11-25), before taking work: (1) read `tasks/HANDOFF.md`; (2) run `py scripts/24_shift_check.py --full` and read every WARN / FAIL / NOT_VERIFIED line (exit 0 does not mean all verified; it compares stats CSVs with RESULTS.md, not raw runs); (3) run the Colab status cell; (4) look around the next task: the code it touches and its callers, stated assumptions, open QA findings, what the previous shift did NOT verify (`docs/limitations_and_improvements.md` too). Report the result in the first reply.

## 9. Boundaries
- Never write the NREL API key or emails into files, logs or commits.
- Do not modify `data_v2/`, `data_2016/`, `data_raw*/`; do not reuse `data/` (rejected).
- Colab: free T4 only; compute units / Pro need User OK. Keep-alive the runtime every ~15 min while jobs run.
- When GPU is gone or Colab cannot be reconnected (or the queue finishes): commit + push, then `shutdown /s /t 600` (User rule).

### Connectors
- `colab` MCP (project `.mcp.json`, git-ignored): browser connection to a Colab T4 notebook; jobs run as a background bash chain, resumable (skip finished keys).
- Google Drive: `MyDrive/WIND_FORECAST_DATA/` — `results/` (synced every 5 min from Colab), `kernels/`, packed data. Repo clone on Colab: `/content/wind_forecast`.

## 10. State & journal
- Tasks, approved decisions, evidence: `tasks/STATUS.md` (single source of truth).
- Stages, milestones, dates: `tasks/ROADMAP.md`.
- Experiment runs and metrics: `tasks/RESULTS.md`.
- All-hands meeting minutes and decisions: `tasks/MEETINGS.md`.
- What got done, per chat: `NHATKY.md`.
