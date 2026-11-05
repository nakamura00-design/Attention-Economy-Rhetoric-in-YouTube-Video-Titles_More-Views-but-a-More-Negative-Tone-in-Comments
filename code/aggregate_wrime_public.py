"""Aggregate the released comment-level WRIME scores to video-level outcomes."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data/comment_wrime_scores_sanitized.csv.gz'
VIDEOS = ROOT / 'data/main_analysis_input_n10013_sanitized.csv'
OUTPUT = ROOT / 'results/video_wrime_outcomes_n10013.csv'
EMOTIONS = ['joy', 'sadness', 'anticipation', 'surprise', 'anger', 'fear', 'disgust', 'trust']

scores = [f'wrime_writer_{emotion}_0to3' for emotion in EMOTIONS]
comments = pd.read_csv(INPUT, compression='gzip')
comments = comments.loc[comments.status.eq('ok')].copy()
for col in scores:
    comments[col] = pd.to_numeric(comments[col], errors='raise')
    if not comments[col].between(0, 3).all():
        raise ValueError(f'Invalid score range: {col}')

grouped = comments.groupby(['doc_id', 'videoId'], as_index=False)
out = grouped[scores].mean()
counts = grouped.size().rename(columns={'size': 'wrime_scored_comments_n'})
out = out.merge(counts, on=['doc_id', 'videoId'], validate='one_to_one')
videos = pd.read_csv(VIDEOS)
out = out.merge(videos, on=['doc_id', 'videoId'], how='left', validate='one_to_one')
if out['いずれか正例'].isna().any():
    raise ValueError('Some WRIME videos are missing from the released video data')
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(OUTPUT, index=False)
print(f'videos={len(out)} comments={int(out.wrime_scored_comments_n.sum())} output={OUTPUT}')
