# HANDOFF — 2026-11-25 ~06:00 (local), leader

## State
- Runtime of Colab unresponsive since ~22:49 UTC 24 Nov (last Drive sync 22:34). PC shut down per the User rule.
- DONE this session: T01, T03, T09, T14, T15. T16: code merged, Colab runs pending. T12: `fewshot8_cc.csv` 864/864, `fewshot8_ft_free.csv` ~180/432 (Drive). T04 SHAP was running; its CSVs on Drive were not checked. T05 PatchTST not started (7/40).
- Decisions: M13 (transfer claim), M14 (few-shot statistics frozen), M15 (T16 inner validation). User (2026-11-25): agents meet and approve/merge on the User's behalf; paid, public or irreversible actions still need the User; no handoff until asked except on runtime loss.
- Test results of T12 were partly seen by the Leader before M14; the status cell no longer prints RMSE. Do not read few-shot scores before `23_fewshot_stats.py` runs.

## Resume
1. `open_colab_browser_connection` (if the MCP tool fails: `/mcp` reconnect), `get_cells`. The notebook may be empty.
2. Cell 1 = clone repo to `/content/_runner`, exec `notebooks/colab_resume.py`, then start T12 (finetune+scratch `--const-calendar` -> `fewshot8_cc.csv` && finetune -> `fewshot8_ft_free.csv`, both `--sites A..H --models Mamba --seeds 3 --scratch-steps 2000 --init-tag losoW8`, then touch `t12.done` in results and on Drive). Drive consent is needed from the User.
3. T16 cell: clone to `/content/_t16`, copy its `18_fewshot.py` to `scripts/18_fewshot_iv.py` in the main clone, background: wait for Drive `t12.done`, then `--inner-val` runs: `--modes finetune` -> `fewshot8_iv_ft_free.csv`, then `--modes scratch --const-calendar` -> `fewshot8_iv_scratch_cc.csv`, then `t16.done`. Same flags as T12.
4. Status cell every ~15 min; if printed time does not change, the cell did not execute: check Drive `run.log` modifiedTime.

## Next
- When `t12.done`: copy the 4 few-shot CSVs from Drive (check they end with a newline), run `py scripts/23_fewshot_stats.py` (never run on real data; a worker call was denied by the auto-mode classifier; ask the User if denied again), then qa, log in RESULTS.md.
- Then T04 (SHAP CSVs, qa), T05, T07 (conformal after T05), T06 (aggregate, per-sample DM), T08 (Results draft; note H also slightly negative at 3h).
- Open: `data_v2/PROVENANCE.md` says 30 features per a worker, data has 31 (read-only, not edited). Worktree `agent-a997d894c831b203d` left locked; can be removed. Low README wording findings QA-T09-01/02.
