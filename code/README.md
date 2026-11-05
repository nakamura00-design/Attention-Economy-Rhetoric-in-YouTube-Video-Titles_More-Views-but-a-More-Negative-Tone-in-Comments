# Code release workflow

The public code release contains only author-written analysis and preprocessing code needed to reproduce the reported tables and figures from the permitted release inputs.

Before release, remove API keys, OAuth tokens, local paths, cached API responses, raw comment text, and machine-specific credentials. Include a requirements file or environment note, a short run order, and a mapping from each manuscript table/figure to its generating script.

## Main entry points

- `h1a_content_fe.py` — views and staged content controls.
- `h1bc_content_fe.py` — likes/views and comments/views models.
- `aggregate_wrime_public.py` — aggregates the released comment-level WRIME scores to video-level outcomes.
- `h2ab_wrime_video_fe_public.py` — produces the released-score video-level WRIME input for the H2ab analyses.
The primary staged models are `h1a_content_fe.py` and `h1bc_content_fe.py`:
each script estimates M0, M1, M2, and M3 by adding the corresponding control
blocks in sequence.

The code reads only files under this repository's `data/` directory and writes derived results under `results/`.

## Run order

From the repository root:

```text
python3 code/h1a_content_fe.py
python3 code/h1bc_content_fe.py
python3 code/aggregate_wrime_public.py
python3 code/h2ab_wrime_video_fe_public.py
```

The generated `results/` directory is intentionally ignored by Git; it is a
reproducible local output directory rather than part of the minimum release.

The public WRIME input is already model-scored. The repository does not include the original comment text, comment IDs, author IDs, or the raw API export, so it reproduces the reported video-level analyses but not the original text-to-embedding or text-to-WRIME inference step.

Before release, remove API keys, OAuth tokens, local paths, cached API responses, raw comment text, and machine-specific credentials. Include a requirements file or environment note, a short run order, and a mapping from each manuscript table/figure to its generating script.

