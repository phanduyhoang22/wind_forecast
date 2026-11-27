# ROADMAP — wind_forecast

Target dates: none fixed (User decision 2026-11-21: keep working stage by stage). Submission needs User approval.
Updated 2026-11-27 (Leader) after M19/M20: S2–S5 done; new stage S3b (credibility package, M20) runs before the full manuscript; writing continues in parallel.

## S1 — Data — DONE (2026-11-14)
- goal: verified 15-min, 100 m series for 8 sites (2 per regime) + 2016 back-test year.
- milestones: SEA-WTK download (A–D 2026-09-11; E–H + 2016 2026-11-14); gate `02_verify_raw.py` passed 8/8; features `03`; provenance `data_v2/PROVENANCE.md`; site F coast check (~3 km).
- done-criteria: met.

## S2 — Per-site benchmark (E1) — DONE (2026-11-27)
- 6 models × 8 sites × 5 seeds (T05 PatchTST 40/40, T03 E1-W); DM/Holm tables (T06, R31); claim M18 (no significant difference Mamba / Transformer / RF).

## S3 — Transfer — DONE (2026-11-27), reopened by S3b
- LOSO-8 Mamba-W + RF-W (T01, R21, M13); cross-site 8×8 W (T03, R22–R24); few-shot A–H (T12, T16, M14–M16).

## S4 — Explainability & uncertainty — DONE
- SHAP (T04, R27), conformal (T07, M17).

## S5 — Statistics & aggregation — DONE
- T06, T14, T15, T18, T19.

## S3b — Credibility package (M19 + M20) — CURRENT
- goal: make the transfer and accuracy claims hold under a target-free, strong-reference, unseen-data test.
- order (M20 consensus):
  1. T21 target-free scaler LOSO-8 (Colab T4) ‖ T23 references: smart persistence, persistence–climatology blend, LightGBM on the DL window (CPU).
  2. T24 zero-shot foundation model (Chronos-Bolt / TTM) vs LOSO-W (T4), descriptive.
  3. T25 2007–2015 unseen test years: availability + NREL cap check -> hash checkpoints, configs, scripts, claims table -> download -> one evaluation.
  4. T26 descriptive controls (size-matched pool, leave-one-regime-out) + power-curve conversion.
  5. T27 exploratory: RevIN (only if T21 trigger fires on source val), LP-FT, adaptive conformal. T22 (P3) last.
- rules: pre-register before each run; val-only selection; Holm families m <= 6; report any direction; disclose test reuse; a claim change -> meeting.
- done-criteria: T21, T23, T24, T25, T26 DONE with QA PASS and RESULTS rows; claims table re-frozen; meeting on the final claims before S6 completes.

## S6 — Paper writing — IN PROGRESS (parallel)
- drafted: Section 2 (`section2_data_methods.md`), Results E1 (`section3_results.md`), Results transfer/few-shot/SHAP (`section3_results_transfer.md`).
- to do: Section 2.5.4 alignment + §3.x numbering (small docs task); framing led by W vs 31 features (site fingerprint), Mamba as one benchmarked model; rename old LOSO result "zero-shot with target-normalised inputs"; few-shot to the supplement; disclose site non-independence (one WRF domain), test reuse, modelled data, 6 h without NWP; Discussion and Introduction after S3b results; read cited papers in full first.
- done-criteria: complete draft reviewed by User.

## S7 — Submission
- goal: journal choice (target after S3b: Renewable Energy if the package holds, else Q2 e.g. Energy Reports / IET RPG), formatting, Zenodo/DOI snapshot. Needs User approval.
