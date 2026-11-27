#!/usr/bin/env python3 -I
# CDHD tercile — CatBoost (first / track A). BOTH 8-model count (N=8) & full-ensemble (N=219, pooled calib). Estimator=CatBoost LOOCV. Hits only.
import numpy as np, pandas as pd, xarray as xr
from pathlib import Path
from catboost import CatBoostRegressor
import matplotlib; matplotlib.use("Agg"); matplotlib.rcParams["font.family"]="Nimbus Sans"; matplotlib.rcParams["font.size"]=12; matplotlib.rcParams["mathtext.fontset"]="stixsans"
import matplotlib.pyplot as plt
D=Path("data"); EM=D/"ERA5/monthly"; V10=Path("/data1/ERA5/single_level/monthly_1.0/10m_v_component_of_wind"); FIG=Path("figure")
COL=["#36b5ff","#d9d9d9","#ff5a4e"]; EV=[int(y) for y in range(1993,2017)]; Y46=np.arange(1979,2025); pos={int(Y):k for k,Y in enumerate(Y46)}; PREDN=["t2mna","v10io"]
CB=dict(iterations=200,depth=2,learning_rate=0.05,l2_leaf_reg=5.0,loss_function="RMSE",random_seed=42,verbose=0,allow_writing_files=False)
def detr(x): x=np.asarray(x,float); n=len(x); t=np.arange(n)-(n-1)/2.; a=x-x.mean(); s=(t*t).sum(); return a-((t*a).sum()/s)*t
def box_ja(kind,a,b,c,e):
    out=[]
    for y in Y46:
        vv=[]
        for mm in (7,8):
            if kind=="t2m": ds=xr.open_dataset(EM/f"ERA5m_{y}{mm:02d}.nc"); da=ds["t2m"]
            else: ds=xr.open_dataset(V10/f"ERA5m_{y}{mm:02d}.nc"); da=ds["v10"].squeeze()
            lat=da["latitude"].values; lon=da["longitude"].values; ml=(lat>=a)&(lat<=b); mo=(lon>=c)&(lon<=e)
            s=(da.values if da.values.ndim==2 else da.values[0])[np.ix_(ml,mo)]; w=np.cos(np.deg2rad(lat[ml]))[:,None]
            vv.append(float(np.nansum(s*w)/np.nansum(w*np.ones_like(s)))); ds.close()
        out.append(np.mean(vv))
    return np.array(out)
d=xr.open_dataset(D/"ERA5_JA_CDHD_index_1979-2024.nc"); yc=d.year.values.astype(int); cdhd=np.array([float(d.korea_nday.values[list(yc).index(y)]) for y in Y46]); d.close()
ym={int(Y):float(cdhd[k]) for k,Y in enumerate(Y46)}
PRED={"t2mna":box_ja("t2m",8.5,20.5,306.5,325.5),"v10io":box_ja("v10",5.5,12.5,87.5,92.5)}
yt=detr(np.array([ym[Y] for Y in Y46])); Xf={p:detr(PRED[p]) for p in PRED}
OM={p:np.array([Xf[p][pos[Y]] for Y in EV]).mean() for p in PREDN}; OSD={p:np.array([Xf[p][pos[Y]] for Y in EV]).std() for p in PREDN}
pm=pd.read_csv(D/"c3s_cdhd_permember_predictors_1993-2016.csv"); models=sorted(pm.model.unique())
MOD={}
for Y in EV:
    tr=Y46!=Y; Xtr=np.column_stack([Xf[p][tr] for p in PREDN]); m=CatBoostRegressor(**CB); m.fit(Xtr,yt[tr]); MOD[Y]=m
def votes(mode):
    out={Y:[] for Y in EV}
    for mo in models:
        sub=pm[pm.model==mo]
        if mode=="8model":
            g=sub.groupby("year")[PREDN].mean(); cal={p:{} for p in PREDN}
            for p in PREDN:
                cm,cs=g[p].mean(),g[p].std()
                for Y in g.index: cal[p][int(Y)]=(g.loc[Y,p]-cm)/cs*OSD[p]+OM[p]
            for Y in g.index:
                if int(Y) in EV: out[int(Y)].append([cal[p][int(Y)] for p in PREDN])
        else:
            cal={p:{} for p in PREDN}
            for p in PREDN:
                cm,cs=sub[p].mean(),sub[p].std()
                for _,r in sub.iterrows(): cal[p][(int(r.year),int(r.member))]=(r[p]-cm)/cs*OSD[p]+OM[p]
            for _,r in sub.iterrows():
                if int(r.year) in EV: out[int(r.year)].append([cal[p][(int(r.year),int(r.member))] for p in PREDN])
    return out
t33,t67=np.percentile(yt,[100/3,200/3])
def catf(v): return 0 if v<t33 else (2 if v>t67 else 1)
def evaluate(mode):
    vv=votes(mode); frac=np.zeros((len(EV),3)); ocat=[]; nv=[]
    for i,Y in enumerate(EV):
        preds=[float(MOD[Y].predict(np.array([x],dtype=float))[0]) for x in vv[Y]]; cs=[catf(p) for p in preds]; n=len(cs); nv.append(n)
        for c in cs: frac[i,c]+=1.0/n
        ocat.append(catf(yt[pos[Y]]))
    hit=0.0; hm=[]
    for i in range(len(EV)):
        mx=frac[i].max(); win=[c for c in range(3) if abs(frac[i,c]-mx)<1e-9]
        if ocat[i] in win: hit+=1.0/len(win); hm.append("check" if len(win)==1 else "half")
        else: hm.append(None)
    return frac,ocat,hit,hm,int(np.median(nv))
def draw(frac,ocat,hit,hm,title,out):
    fig,ax=plt.subplots(figsize=(6.56,3.2)); P=frac*100; bottom=np.zeros(len(EV))
    for c in range(3):
        ax.bar(EV,P[:,c],bottom=bottom,color=COL[c],width=0.84,edgecolor="white",lw=0.4,zorder=2)
        for i in range(len(EV)):
            if P[i,c]>=7: ax.text(EV[i],bottom[i]+P[i,c]/2,f"{P[i,c]:.0f}",ha="center",va="center",fontsize=8,color=("black" if c==1 else "white"),zorder=4)
        bottom=bottom+P[:,c]
    OBSM={0:("v","#1f78d6"),1:("o","#888888"),2:("^","#d62728")}
    for i in range(len(EV)):
        m,cc=OBSM[ocat[i]]; ax.scatter([EV[i]],[105],marker=m,s=34,c=cc,clip_on=False,zorder=5)
        if hm[i]=="check": ax.text(EV[i],113,"✓",ha="center",va="bottom",fontsize=12,color="#239a3b",fontweight="bold",fontfamily="DejaVu Sans",clip_on=False,zorder=5)
        elif hm[i]=="half": ax.text(EV[i],113,"½",ha="center",va="bottom",fontsize=11,color="#555",fontfamily="DejaVu Sans",clip_on=False,zorder=5)
    ax.set_ylim(0,100); ax.set_xlim(EV[0]-0.7,EV[-1]+0.7); ax.set_yticks([0,33.3,66.7,100]); ax.set_yticklabels(["0","33","67","100"]); ax.set_ylabel("Probability (%)")
    xt=[Y for Y in EV if Y%2==0]; ax.set_xticks(xt); ax.set_xticklabels([f"{Y%100:02d}" for Y in xt])
    ax.text(0.0,1.30,title,transform=ax.transAxes,ha="left",va="bottom",fontsize=13.5)
    ax.text(1.0,1.30,f"Hits {hit:.1f}/{len(EV)}",transform=ax.transAxes,ha="right",va="bottom",fontsize=12.5)
    fig.subplots_adjust(left=0.115,right=0.985,bottom=0.13,top=0.72); fig.savefig(out,dpi=200,transparent=True); plt.close(fig); print("[saved]",out)
for mode,fname in [("8model","fig_tercile_count_CDHD_cb.png"),("member","fig_tercile_member_CDHD_cb.png")]:
    fr,oc,ht,hm,nv=evaluate(mode); print("catboost_first %-7s Hits %.1f/%d votes~%d"%(mode,ht,len(EV),nv))
    draw(fr,oc,ht,hm,f"JA CDHD Tercile Forecast  ($\\mathrm{{CatBoost}}_\\mathrm{{first}}$, N={nv})",FIG/fname)
