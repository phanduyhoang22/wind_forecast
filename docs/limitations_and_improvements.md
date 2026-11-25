# Limitations and improvement backlog

Written 2026-11-25 (Leader) at the User's request. **Nothing here is approved or scheduled.** The running experiments (T04, T05, T16) keep their frozen configuration (M13–M15). Improvements start after T04, T05, T06 and T16 are finished, and each method change needs a `/meeting` first. Numbers come from `tasks/RESULTS.md` (run ids given); costs are judgements, not measurements.

## 1. Limitations

### A. Affecting the main conclusions
| id | limitation | evidence | possible improvement | cost |
|---|---|---|---|---|
| L01 | Mamba is not clearly more accurate: Mamba ≈ Transformer, RF close at 1h | R03, RMSE 1h, mean A–D: 0.560 / 0.564 / 0.562 m/s | Centre the paper on transfer, cost, explainability and statistics; hybrid architecture only as an option | low (writing) / high (new model) |
| L02 | Modelled data (WRF + sup3r GAN), not measurements | `data_v2/PROVENANCE.md`, M08 | Check against met-mast or lidar data if any can be obtained | high |
| L03 | No NWP input | M08 | Add archived operational forecasts (never reanalysis: future leakage) | high |
| L04 | n = 8 target sites, 2 per regime; the smallest reachable Holm p (3 horizons) is 0.023 | M08, R21 | More sites (M08 decided against) | high |
| L05 | Zero-shot transfer is fragile: LOSO 3h/6h not significant vs persistence; Mamba-W vs RF-W not significant; cross-regime skill negative | R21, R21c (Holm p 0.078, 0.117); R23 (−8.2/−10.6/−6.7%) | Source-site selection by similarity, target-free normalization, domain adaptation | medium |
| L06 | Fine-tuning adds little over zero-shot: n.s. at 1h and 3h, 6h depends on seed aggregation; no visible effect of 1/2/4 weeks | R25, R25c, QA-T12-02/04; median `best_epoch` 1; not reproduced in R26 (M16) | Lower LR, layer freezing, adapters | low–medium |

### B. Fairness and reviewer risk
| id | limitation | evidence | possible improvement | cost |
|---|---|---|---|---|
| L07 | Few-shot references are weak (the oracle best is below persistence) | R25c (−9.1/−15.8/−11.1%) | Tuned Ridge, RF with lags, LOSO-pretrained LSTM/DLinear | medium |
| L08 | Fine-tuning and scratch use ~9 months of target validation data (checkpoint, early stopping, LR schedule); Ridge/RF do not | QA-T12-05 | T16 done (R26, M16): no gain over zero-shot; control run separating the confounds | medium (est. 2–4 T4-h) |
| L09 | Target MinMax scaler is fitted on the full target train set, so LOSO "zero-shot", cross-site and few-shot results are not free of target data (each site uses the MinMax of its own train segment) | `scripts/09_global_loso.py:12`, `04_data_pipeline.py:180`, R23, QA-T12 item 4 | Scaler from the k weeks only, or window-wise normalization | low–medium |
| L10 | RF and Ridge see only the last time step (19 features), neural networks see the whole look-back | QA-T12 item 4 | RF/Ridge with lagged inputs | low |
| L11 | The LOSO 8-fold covers Mamba and RF only, so a transfer benefit cannot be attributed to Mamba | R16, R21 | Transformer / PatchTST LOSO-W | medium (GPU) |
| L12 | Post-hoc choices: coastal threshold 6.0→5.5 m/s, scratch step budget, `month_*` handling | M06, M07, M12 | Disclose (cannot be undone) | low |
| L13 | Test 2021 and the 2016 back-test were viewed repeatedly | — | Select on validation only, freeze rules first (as in M14); use unseen years (see P1) | medium |

### C. Scope
| id | limitation | evidence | possible improvement |
|---|---|---|---|
| L14 | One hub height (100 m); test period Apr–Dec 2021 only (no Jan–Mar) | M08, CLAUDE.md §5; R10 partly compensates | Full-year evaluation on other years |
| L15 | Mamba full-sequence CPU latency is high; only step mode is fast | R04: 22.4 ms vs 1.62 ms (Transformer 2.91 ms) | Smaller model, ONNX export; always state the mode |
| L16 | SHAP and conformal results are not QA'd yet; SHAP completeness error in the run log is 6.4–7.3% (sites B, C, D) | T04 log, 2026-11-25 | QA; more background samples or steps |

## 2. Proposed order (after the current queue is done)
1. Normalization that needs no target training data (L09).
2. Lighter fine-tuning (L06), Transformer LOSO-W (L11), stronger references (L07, L10), zero-shot foundation model baseline.
3. Source-site selection by similarity (L05).
4. **P1:** the NREL dataset covers 2007–2021 and this project uses 2016–2021. Check whether 2007–2015 can be downloaded for the 8 sites; they would be an unseen test set (L13). This changes M08 (no extra years), so it needs a meeting.
5. NWP input (L03), real measurements (L02).

Possible now, without touching experiments: read the papers below in full; check (not download) the availability of 2007–2015.

## 3. Papers
Read level: **PDF-part** = abstract and conclusion read from the local PDF; **search** = search-engine summary only, full text not opened. Read the full text and check the bibliographic data before citing any of them.

### Mamba vs other models (L01, L15)
| paper | point | read level |
|---|---|---|
| Wang et al., VMamba-WSP, Energy Reports 2026 (`tailieu_rieng/1-s2.0-S2352484726006463-main.pdf`) | 10 m wind, ERA5; RMSE 1.277 vs 1.133 for TRNet-lite; "no overall superiority is claimed" | PDF-part |
| Dong et al., Wind-Mambaformer, Energies 2025, 18, 1155 (`References/energies-18-01155-v2.pdf`), https://www.mdpi.com/1996-1073/18/5/1155 | Hybrid, wind power; authors claim MAE −30%, MSE −60% vs standard Transformer | PDF-part |
| S-Mamba, "Is Mamba Effective for Time Series Forecasting?", https://arxiv.org/abs/2403.11144 | Lower memory and training time, competitive accuracy | search |
| UniMamba, https://arxiv.org/pdf/2604.16325 | ETTm1 MSE: S-Mamba 0.341, iTransformer 0.342, PatchTST 0.324 | search |
| MambaTS, https://arxiv.org/pdf/2405.16440 | Mamba blocks inside PatchTST/iTransformer: less memory, no accuracy advantage found | search |
| Grid-signal benchmark, https://arxiv.org/abs/2602.21415 | No single best model; state-space suited to wind and price, PatchTST to solar | search |
| Long-term forecasting re-evaluation, TMLR 01/2026, https://www.alphaxiv.org/abs/2502.14045.md | 8 models, none dominates on all datasets | search |

### Transfer and few-shot (L05, L06)
| paper | point | read level |
|---|---|---|
| Despotovic et al., IJGE 2026, 23(3), 669–684 (`tailieu_rieng/Manuscript.pdf`) | Wind-speed transfer over 70 stations, close to direct learning (TL score −8% to +4%) | PDF-part |
| Sun & Tian 2025, Applied Energy, https://ideas.repec.org/a/eee/appene/v377y2025ipds0306261924021007.html | Pre-train then fine-tune, new turbines (paywalled in an earlier attempt) | search |
| Weisser, Hashimoto-Cullen & Guedj 2026, https://arxiv.org/html/2601.19674v1 | Meteorological clusters, 8 offshore farms, under 5 months of target data; wind power | search |
| Meta-learning for probabilistic wind power, https://arxiv.org/pdf/2308.07980 | Adaptation by meta-learning | search |
| LoRA for building energy with foundation models, https://arxiv.org/pdf/2506.00630 | Cheaper fine-tuning without accuracy loss; not wind | search |
| LoRA for electrical load, https://arxiv.org/pdf/2610.28200 | Pretrained vs full fine-tuning vs LoRA, OOD evaluation; not wind | search |

### Normalization under distribution shift (L09)
| paper | point | read level |
|---|---|---|
| RevIN, ICLR 2022, https://iclr.cc/virtual/2022/poster/6034 | Reversible instance normalization | search |
| Critique 2026, https://arxiv.org/html/2603.11869v1 | Several RevIN components redundant or harmful | search |
| "Noise or Signal?", https://arxiv.org/pdf/2510.04667 | Contradictions in reversible normalization | search |

### Foundation models as baselines (L07)
| paper | point | read level |
|---|---|---|
| WindFM, https://arxiv.org/html/2509.06311v1 | 8.1M parameters, zero-shot wind power | search |
| Tyan-WP, https://arxiv.org/pdf/2606.08630 | Site metadata embedding (conflicts with our "no site ID" rule); wind power | search |
| Za'ter & Hodge, https://arxiv.org/abs/2604.22077 | Chronos, TimesFM, Moirai and others on solar, wind, load | search |

### NWP and data validity (L02, L03)
| paper | point | read level |
|---|---|---|
| Baggio et al., https://arxiv.org/abs/2503.18797v2 | ARPEGE/AROME + stations, surface wind 1–6 h; abstract reports beating persistence at all horizons | search |
| PeakWeather, https://arxiv.org/pdf/2506.13652 | Station data; deep learning beats ICON NWP up to about 12 h | search |
| NREL Southeast Asia report 2023, https://www.nrel.gov/docs/fy23osti/85481.pdf | 2007–2021, 3 km / 15 min; tower comparison found for Bangladesh only (21 days, Feb 2016); no Vietnam validation found in our search | search |
