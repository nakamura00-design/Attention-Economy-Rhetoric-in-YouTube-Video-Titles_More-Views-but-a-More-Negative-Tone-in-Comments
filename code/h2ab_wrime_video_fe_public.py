#!/usr/bin/env python3
"""Reproduce video-level WRIME outcomes from the released score table.

Comment text and comment identifiers are intentionally not required. The input
already contains the eight released WRIME scores for each comment record.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
VIDEOS = ROOT / "data/main_analysis_input_n10013_sanitized.csv"
COMMENTS = ROOT / "data/comment_wrime_scores_sanitized.csv.gz"
OUT = ROOT / "results/wrime_video_fe_public"
SCORES = [
    "wrime_writer_joy_0to3", "wrime_writer_sadness_0to3",
    "wrime_writer_anticipation_0to3", "wrime_writer_surprise_0to3",
    "wrime_writer_anger_0to3", "wrime_writer_fear_0to3",
    "wrime_writer_disgust_0to3", "wrime_writer_trust_0to3",
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    videos = pd.read_csv(VIDEOS)
    comments = pd.read_csv(COMMENTS, compression="gzip")
    comments = comments.loc[comments["status"].eq("ok")].copy()
    if comments.empty:
        raise ValueError("No valid WRIME rows found")
    for column in SCORES:
        if not comments[column].between(0, 3).all():
            raise ValueError(f"Invalid WRIME range in {column}")
    aggregated = comments.groupby(["doc_id", "videoId"], as_index=False)[SCORES].mean()
    counts = comments.groupby(["doc_id", "videoId"]).size().rename("wrime_scored_comments_n").reset_index()
    aggregated = aggregated.merge(counts, on=["doc_id", "videoId"], validate="one_to_one")
    joined = videos.merge(aggregated, on=["doc_id", "videoId"], how="left", validate="one_to_one")
    joined.to_csv(OUT / "video_wrime_outcomes_n10013.csv", index=False)
    audit = pd.DataFrame([{
        "videos": len(videos),
        "videos_with_scores": int(joined["wrime_scored_comments_n"].notna().sum()),
        "valid_comment_score_rows": len(comments),
        "score_columns": len(SCORES),
        "note": "Means are computed from released model scores; original comment text and IDs are not included.",
    }])
    audit.to_csv(OUT / "audit.csv", index=False)
    print(audit.to_string(index=False))


if __name__ == "__main__":
    main()
