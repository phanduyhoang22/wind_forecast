# ROADMAP — wind_forecast

Target dates: none fixed (User decision 2026-11-21: keep working stage by stage). Submission needs User approval.

## S1 — Data — DONE (2026-11-14)
- goal: verified 15-min, 100 m series for 8 sites (2 per regime) + 2016 back-test year.
- milestones: SEA-WTK download (A–D 2026-09-11; E–H + 2016 2026-11-14); gate `02_verify_raw.py` passed 8/8; features `03`; provenance `data_v2/PROVENANCE.md`; site F coast check (~3 km).
- done-criteria: met.

## S2 — Per-site benchmark (E1) — MOSTLY DONE
- goal: 6 models × 8 sites × 5 seeds with one tuning grid; latency on CPU.
- milestones: tuning (2026-11-09); E1 A–D NNs + RF (2026-11-10); E1 E–H (2026-11-14); latency `15`; GAN-phase check `13`.
- open: PatchTST 7/40 runs at A–H (T05, M10); E1-W Mamba 8 sites (T03).
- done-criteria: all E1 runs present; DM/Holm tables for 8 sites (T06).

## S3 — Transfer — CURRENT
- goal: show when a model trained elsewhere works at a new site.
- milestones done: global/LOSO 4-fold (31 features, W, delta, relative); 8×8 cross-site (31 features); 2016 back-test; few-shot finetune + RF; RF-W LOSO 8-fold (1h: 8/8 sites beat persistence, Holm p = 0.023).
- open: Mamba-W LOSO 8-fold (T01, 7/27); few-shot scratch 2000 steps (T02); cross-site 8×8 W (T03).
- done-criteria: LOSO-8 for Mamba and RF with Wilcoxon (n = 8); few-shot table with fair scratch baseline.

## S4 — Explainability & uncertainty
- goal: SHAP (Mamba-31 per site, Mamba-W LOSO) and conformal intervals.
- tasks: T04, T07. done-criteria: SHAP group/lag tables with completeness error; PICP/PINAW by tercile.

## S5 — Statistics & aggregation
- goal: frozen tables for the paper. tasks: T06. done-criteria: every claim has DM/Wilcoxon + Holm and seed range.

## S6 — Paper writing
- goal: full manuscript. Section 2 drafted (`docs/paper/section2_data_methods.md`); Results/Discussion after S5 (T08); README update (T09).
- done-criteria: complete draft reviewed by User.

## S7 — Submission
- goal: journal choice, formatting, Zenodo/DOI snapshot. Needs User approval.
