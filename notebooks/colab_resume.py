# Colab resume runner (paste into ONE notebook cell, Colab T4 runtime).
# Why: the Colab notebook opened through the MCP `colab` browser connection comes back EMPTY after every
# runtime reset, so the setup cell lives here. It mounts Drive, re-clones the repo, copies finished results
# back from Drive (scripts skip finished (site, model, seed) keys), loads the prebuilt mamba-ssm kernel,
# and starts the GPU queue + a 5-min Drive sync loop in the background. Safe to re-run: it does nothing
# if a job is already alive or there is no GPU.
# Queue = tasks/STATUS.md T01 -> T02 -> T03 -> T04 -> T05 (decided in meetings M06-M08).
from google.colab import drive
drive.mount('/content/drive')
import os, glob, shutil, subprocess, time, torch, pandas as pd
print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'KHONG', '| torch', torch.__version__)
DRIVE = '/content/drive/MyDrive/WIND_FORECAST_DATA'; W = '/content/wind_forecast'; K = '/content/ss_build'; R = f'{DRIVE}/results'
alive = subprocess.run('ps aux | grep -E "[0]7_run|[0]9_global|[1]8_few|[1]6_cross|[1]0_shap"', shell=True, capture_output=True, text=True).stdout
print('job dang song:', 'CO' if alive else 'khong')
SUBS = ('preds', 'models', 'preds_loso', 'models_loso', 'preds_wind', 'models_wind')
if not alive and torch.cuda.is_available():
    os.chdir('/content'); shutil.rmtree(W, ignore_errors=True)   # re-run safe: cwd may be inside W
    subprocess.run(['git', 'clone', '-q', '--depth', '1', 'https://github.com/phanduyhoang22/wind_forecast.git', W], check=True)
    for f in glob.glob(f'{R}/*.csv'):   # CPU-side CSVs are authoritative in git, do not overwrite them
        if not os.path.basename(f).startswith(('baselines', 'tune', 'runs_rf', 'loso_rf', 'loso8_rf', 'cross_eval_rf', 'backtest_2016_rf', 'fewshot_rf', 'coast', 'diurnal', 'site_id')):
            shutil.copy(f, f'{W}/results/')
    for sub in SUBS:
        if os.path.isdir(f'{R}/{sub}'): shutil.copytree(f'{R}/{sub}', f'{W}/results/{sub}', dirs_exist_ok=True)
    os.makedirs(K, exist_ok=True)
    shutil.copy(f'{DRIVE}/kernels/selective_scan_cuda_sm75_torch{torch.__version__.split("+")[0]}.so', f'{K}/selective_scan_cuda.so')
    subprocess.run('pip install -q shap', shell=True)
    os.chdir(W)
    print(subprocess.run('git log --oneline -1', shell=True, capture_output=True, text=True).stdout)
    for f in ('loso8_wind.csv', 'fewshot_scratch2.csv', 'runs_wind.csv', 'cross_eval_wind.csv'):
        p = f'results/{f}'; print(f, len(pd.read_csv(p)) if os.path.exists(p) else 0, 'dong')
    PY = f'cd {W} && PYTHONPATH={K} python -u'
    S8 = 'A,B,C,D,E,F,G,H'
    CHAIN = '; '.join([
        f'{PY} scripts/09_global_loso.py --sites {S8} --models Mamba --seeds 3 --features wind --out results/loso8_wind.csv',          # T01
        f'{PY} scripts/18_fewshot.py --sites A,B,C,D --models Mamba --seeds 3 --modes scratch --scratch-steps 2000 --out results/fewshot_scratch2.csv',  # T02
        f'{PY} scripts/07_run_benchmark.py --sites {S8} --models Mamba --seeds 5 --features wind --out results/runs_wind.csv',          # T03a
        f'{PY} scripts/16_cross_eval.py --sites {S8} --models Mamba --seeds 3 --features wind --out results/cross_eval_wind.csv',       # T03b
        f'{PY} scripts/10_shap.py --sites {S8} --model Mamba --seed 0',                                                                # T04a
        f'{PY} scripts/10_shap.py --sites {S8} --model Mamba --seed 0 --models-dir results/models_loso --pattern losoW8_{{site}}_{{model}}_{{seed}}.pt --features wind --tag losoW8',  # T04b
        f'{PY} scripts/07_run_benchmark.py --sites {S8} --models PatchTST --seeds 5 --out results/runs.csv',                         # T05 (M10: A-H)
    ]) + f'; touch {W}/results/all.done'
    SYNC = (f'while true; do D={R}; cp {W}/results/*.csv {W}/results/*.log {W}/results/*.npz $D/ 2>/dev/null; '
            f'for s in {" ".join(SUBS)}; do mkdir -p $D/$s; cp -u {W}/results/$s/* $D/$s/ 2>/dev/null; done; sleep 300; done')
    subprocess.Popen(['bash', '-c', f'({CHAIN}) >> {W}/results/run.log 2>&1'])
    subprocess.Popen(['bash', '-c', SYNC])
    print('da khoi dong: T01 LOSO 8 fold -> T02 scratch 2000 -> T03 E1-W + cheo W -> T04 SHAP x2 -> T05 PatchTST')

# ---- STATUS / KEEP-ALIVE CELL (second cell; run every ~15 min) ----
# import time, os, subprocess
# print(time.strftime('%H:%M:%S'), '| XONG HET' if os.path.exists('/content/wind_forecast/results/all.done') else '| dang chay')
# print(subprocess.run('nvidia-smi --query-gpu=memory.used --format=csv,noheader; grep -E "^\\[[0-9]+/[0-9]+\\]|^[A-H] Mamba|Error|Traceback" /content/wind_forecast/results/run.log | grep -v "bo qua" | tail -4; tail -n 1 /content/wind_forecast/results/run.log', shell=True, capture_output=True, text=True).stdout)
#
# Stale-output check: if the printed time does not change between runs, the cell did not execute.
# Then check Drive modifiedTime of results/run.log (Drive connector); > 15 min old = runtime lost.
