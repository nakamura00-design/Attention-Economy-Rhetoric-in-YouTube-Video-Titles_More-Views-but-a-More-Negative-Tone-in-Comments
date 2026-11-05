"""H1a: same-sample channel FE, staged content controls, CR1 inference."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/main_analysis_input_n10013_sanitized.csv'
OUT = ROOT / 'results/h1a_content_fe'
OUT.mkdir(exist_ok=True)
d = pd.read_csv(SOURCE)
assert len(d) == 10013 and d.videoId.nunique() == 10013
required = ['view count','いずれか正例','is_short','published at','channel Id','political_party','format','policy']
assert not d[required].isna().any().any()
assert d['view count'].ge(0).all() and d['いずれか正例'].isin([0,1]).all()
switch = d.groupby('channel Id')['いずれか正例'].nunique()
selected = d['channel Id'].isin(switch[switch.eq(2)].index)
d[['videoId','doc_id','channel Id']].assign(in_h1a=selected).to_csv(OUT/'sample_manifest.csv',index=False)
d = d.loc[selected].copy().reset_index(drop=True)
assert len(d) == 6257 and d['channel Id'].nunique() == 559
d['any_clickbait'] = d['いずれか正例'].astype(float)
d['y'] = np.log1p(d['view count'])
dates = sorted(d['published at'].astype(str).unique())
date_terms = []
for date in dates[1:]:
    term = 'date:' + date
    d[term] = d['published at'].astype(str).eq(date).astype(float)
    date_terms.append(term)
blocks = {}; coverage = []
for col in ['political_party','format','policy']:
    labels = sorted({v for s in d[col] for v in s.split('｜') if v != 'なし'})
    blocks[col] = []
    for label in labels:
        term = col + ':' + label
        d[term] = d[col].map(lambda s: int(label in s.split('｜')))
        blocks[col].append(term)
        coverage.append({'term':term,'videos':int(d[term].sum()),'channels_with_label':d.loc[d[term].eq(1),'channel Id'].nunique(),
                         'within_varying_channels':int(d.groupby('channel Id')[term].nunique().gt(1).sum())})
pd.DataFrame(coverage).to_csv(OUT/'content_support.csv',index=False,encoding='utf-8-sig')
terms = ['any_clickbait','is_short',*date_terms]
all_results = []; diagnostics = []; matrices = {}
for stage in range(4):
    if stage: terms += blocks[['political_party','format','policy'][stage-1]]
    w = d[['y',*terms]] - d.groupby('channel Id')[['y',*terms]].transform('mean')
    keep = []; dropped = []
    for term in terms:
        arr = w[[*keep,term]].to_numpy()
        if np.linalg.matrix_rank(arr) > len(keep): keep.append(term)
        else: dropped.append(term)
    x = w[keep].to_numpy(); y = w.y.to_numpy()
    b = np.linalg.lstsq(x,y,rcond=None)[0]; resid = y-x@b
    codes, groups = pd.factorize(d['channel Id']); g = len(groups); n = len(d); k = len(keep)
    bread = np.linalg.inv(x.T@x)
    scores = np.zeros((g,k)); np.add.at(scores,codes,x*resid[:,None])
    # Full dummy-variable equivalent parameter count: G channel intercepts plus K slopes.
    cov = g/(g-1)*(n-1)/(n-g-k)*bread@(scores.T@scores)@bread
    se = np.sqrt(np.diag(cov)); crit = stats.t.ppf(.975,g-1)
    # Recover the channel intercepts to evaluate prediction of the original
    # (not within-demeaned) log outcome.  This is the LSDV-equivalent overall R2.
    xb = d[keep].to_numpy() @ b
    channel_intercept = pd.Series(d['y'].to_numpy() - xb).groupby(d['channel Id']).transform('mean').to_numpy()
    fitted = channel_intercept + xb
    overall_resid = d['y'].to_numpy() - fitted
    overall_r2 = 1 - overall_resid @ overall_resid / np.sum((d['y'].to_numpy() - d['y'].mean()) ** 2)
    overall_adj_r2 = 1 - (1-overall_r2)*(n-1)/(n-g-k)
    for j,term in enumerate(keep):
        lo,hi = b[j]-crit*se[j], b[j]+crit*se[j]
        all_results.append({'model':f'M{stage}','term':term,'beta':b[j],'cluster_se':se[j],
          'ci_low':lo,'ci_high':hi,'p':2*stats.t.sf(abs(b[j]/se[j]),g-1),
          'exp_beta_minus1_percent':100*np.expm1(b[j]),'percent_low':100*np.expm1(lo),'percent_high':100*np.expm1(hi),
          'n':n,'channels':g,'within_r2':1-resid@resid/(y@y),
          'overall_r2':overall_r2,'overall_adj_r2':overall_adj_r2})
    vif = {term: float((x[:,j]@x[:,j])*bread[j,j]) for j,term in enumerate(keep)}
    diagnostics.append({'model':f'M{stage}','slopes':k,'full_parameter_count':g+k,'dropped':dropped,
                        'within_vif_clickbait':vif['any_clickbait'],'max_within_vif':max(vif.values()),
                        'condition_number':float(np.linalg.cond(x)),
                        'within_r2':1-resid@resid/(y@y),'overall_r2':overall_r2,
                        'overall_adj_r2':overall_adj_r2})
    # Independent residualization verifies the focal coefficient (Frisch-Waugh-Lovell).
    z=x[:,1:]; cb=x[:,0]; cbres=cb-z@np.linalg.lstsq(z,cb,rcond=None)[0]
    assert np.isclose(cbres@y/(cbres@cbres),b[0],atol=1e-10)
result=pd.DataFrame(all_results)
result.to_csv(OUT/'all_coefficients.csv',index=False,encoding='utf-8-sig')
key=result[result.term.eq('any_clickbait')]
key.to_csv(OUT/'h1a_results.csv',index=False,encoding='utf-8-sig')
audit={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
       'source_n':10013,'included_n':len(d),'excluded_non_switcher_n':10013-len(d),
       'clickbait_counts':d.any_clickbait.value_counts().to_dict(),'diagnostics':diagnostics,
       'date_fixed_effects':{'reference_date':dates[0],'included_dates':dates[1:],'n_dates':len(dates)},
       'SE_note':'CR1 uses G+K parameters. Previous helper used G-1+K; coefficient unchanged, negligible SE correction.',
       'interpretation':'exp(beta)-1 compares conditional geometric means of views+1, not arithmetic mean views or causal effects.'}
(OUT/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['H1a: タイトル修辞と視聴回数','',f'全モデル: {len(d):,}動画、{g}チャンネル。目的変数 log(1+視聴回数)。',
f'説明変数: いずれか正例。基本統制: チャンネル固定効果、ショート、投稿日固定効果（{len(dates)}日、基準日{dates[0]}）。',
'M1: 政党を追加。M2: フォーマットを追加。M3: 政策を追加。複数ラベルは各0/1、なしは全0。',
'推定: within OLS、チャンネル単位CR1標準誤差、t分布自由度558、両側95%信頼区間。',
'主モデルはM3。M0–M2は調整による変化の確認であり、4本の独立した仮説検定ではない。','',key.to_string(index=False),'',
'指数変換値は views+1 の条件付き幾何平均の比。平均視聴回数の因果的な増加率ではない。',
'正例・負例の両方があるチャンネルに対象を限定。内容は辞書由来の代理変数であり、未検出は内容の不存在を意味しない。',
'内容ラベルは修辞判定と同じタイトルを一部利用し、完全な内容統制ではない。',
'強度別・修辞別分析、H1d、H2、PSMは今回の推定には含めない。',
'独立した残差化による係数検算を実施。詳細はaudit.json。']
(OUT/'h1a_report.txt').write_text('\n'.join(lines),encoding='utf-8')
print(key.to_string(index=False));print(json.dumps(diagnostics,ensure_ascii=False))
