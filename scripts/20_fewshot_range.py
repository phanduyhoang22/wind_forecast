# Hop #7: ty le gio tap test nam ngoai khoang [min,max] cua k tuan train few-shot.
#   py scripts/20_fewshot_range.py
import importlib.util, os, numpy as np, pandas as pd
s=importlib.util.spec_from_file_location('g','scripts/09_global_loso.py'); g=importlib.util.module_from_spec(s); s.loader.exec_module(g)
dp=g.dp
for t in 'ABCD':
    d=dp.load_site(t); tr=d.idx_train; times=d.time
    for win,end in {"DB":"2020-03-31 23:45","TN":"2020-07-01 00:00"}.items():
        e=int(np.searchsorted(times[tr], pd.Timestamp(end)))
        for k in (1,4):
            sub=tr[max(0,e-k*672):e]; y=d.y_raw[sub,0]; yt=d.y_raw[d.idx_test,0]
            print(t,win,k,'train %.1f-%.1f'%(y.min(),y.max()),'test ngoai khoang %.0f%%'%(100*((yt<y.min())|(yt>y.max())).mean()))
