"""Profiled Poisson channel FE, view exposure, staged content/date controls."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import optimize, special, stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/h1bc_content_fe'
OUT.mkdir(exist_ok=True)
SOURCE = ROOT/'data/main_analysis_input_n10013_sanitized.csv'
d = pd.read_csv(SOURCE)
assert len(d)==10013 and d.videoId.nunique()==10013
d['any_clickbait']=d['いずれか正例'].astype(float)
blocks={}
for col in ['political_party','format','policy']:
    blocks[col]=[]
    for label in sorted({v for s in d[col] for v in s.split('｜') if v!='なし'}):
        term=col+':'+label
        d[term]=d[col].map(lambda s:float(label in s.split('｜')))
        blocks[col].append(term)
dates=[]
for date in sorted(d['published at'].unique())[1:]:
    term='date:'+date; dates.append(term)
    d[term]=d['published at'].eq(date).astype(float)
rows=[]; audits=[]
for outcome in ['like count','comment count']:
    valid=d[outcome].notna() & d['view count'].gt(0)
    a=d.loc[valid].copy()
    assert a[outcome].ge(0).all()
    switch=a.groupby('channel Id').any_clickbait.nunique()
    a=a[a['channel Id'].isin(switch[switch.eq(2)].index)].copy()
    base_n=len(a)
    totals=a.groupby('channel Id')[outcome].sum()
    a=a[a['channel Id'].isin(totals[totals.gt(0)].index)].copy().reset_index(drop=True)
    a[['videoId','channel Id']].to_csv(OUT/(outcome.split()[0]+'_sample.csv'),index=False)
    codes,groups=pd.factorize(a['channel Id']); n=len(a); g=len(groups)
    y=a[outcome].to_numpy(float); offset=np.log(a['view count'].to_numpy(float))
    sy=np.bincount(codes,weights=y)
    terms=['any_clickbait','is_short',*dates]
    for stage in range(4):
        if stage: terms+=blocks[['political_party','format','policy'][stage-1]]
        w=a[terms]-a.groupby('channel Id')[terms].transform('mean')
        keep=[]; dropped=[]
        for term in terms:
            if np.linalg.matrix_rank(w[[*keep,term]].to_numpy())>len(keep): keep.append(term)
            else: dropped.append(term)
        x=w[keep].to_numpy(float); k=len(keep)
        def evaluate(b):
            eta=offset+x@b
            mx=np.full(g,-np.inf); np.maximum.at(mx,codes,eta)
            ex=np.exp(eta-mx[codes]); den=np.bincount(codes,weights=ex)
            logden=mx+np.log(den)
            mu=sy[codes]*ex/den[codes]
            loss=(sy@logden-y@eta)/y.sum()
            grad=x.T@(mu-y)/y.sum()
            sx=np.zeros((g,k)); np.add.at(sx,codes,mu[:,None]*x)
            h=x.T@(mu[:,None]*x)-sx.T@(sx/sy[:,None])
            return loss,grad,h,mu,sx
        fit=optimize.minimize(lambda b:evaluate(b)[:2],np.zeros(k),jac=True,
                              hess=lambda b:evaluate(b)[2]/y.sum(),method='trust-exact',
                              options={'gtol':1e-10,'maxiter':300})
        loss,grad,h,mu,sx=evaluate(fit.x)
        assert np.max(np.abs(grad))<1e-8, (outcome,stage,fit.message)
        assert np.linalg.matrix_rank(h)==k, 'Potential separation or singular information'
        xres=x-sx[codes]/sy[codes,None]
        scores=np.zeros((g,k)); np.add.at(scores,codes,xres*(y-mu)[:,None])
        bread=np.linalg.inv(h)
        cov=g/(g-1)*(n-1)/(n-g-k)*bread@(scores.T@scores)@bread
        se=np.sqrt(np.diag(cov)); critical=stats.t.ppf(.975,g-1)
        for j,term in enumerate(keep):
            b=fit.x[j]; lo=b-critical*se[j]; hi=b+critical*se[j]
            rows.append(dict(outcome=outcome,model=f'M{stage}',term=term,beta=b,se=se[j],
                             p=2*stats.t.sf(abs(b/se[j]),g-1),rr=np.exp(b),low=np.exp(lo),high=np.exp(hi),n=n,channels=g))
        audits.append(dict(outcome=outcome,model=f'M{stage}',n=n,channels=g,
                           missing=int(d[outcome].isna().sum()),zero_views=int(d['view count'].eq(0).sum()),
                           zero_channel_rows_removed=base_n-n,dropped=dropped,iterations=int(fit.nit),
                           max_scaled_score=float(np.max(np.abs(grad))),max_abs_beta=float(abs(fit.x).max()),
                           hessian_condition=float(np.linalg.cond(h))))
r=pd.DataFrame(rows)
r.to_csv(OUT/'all_coefficients.csv',index=False)
key=r[r.term.eq('any_clickbait')]
key.to_csv(OUT/'key_results.csv',index=False)
(OUT/'audit.json').write_text(json.dumps(audits,indent=2,ensure_ascii=False))
print(key.to_string(index=False))
print(json.dumps(audits,ensure_ascii=False))
