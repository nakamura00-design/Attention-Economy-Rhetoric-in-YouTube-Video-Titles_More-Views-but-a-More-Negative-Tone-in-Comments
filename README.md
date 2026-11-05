# Data and code companion repository

This repository contains the public data and analysis code accompanying the
Scientific Reports manuscript on attention-economy rhetoric, audience
engagement, and comment emotions in YouTube political communication.

## Release status

This is the minimum safe release prepared for submission. It contains
sanitized analysis inputs and author-written reproduction code; it does **not**
redistribute comment text, comment identifiers, author identifiers, or a bulk
raw API export.

The release includes the following materials:

- `data/main_analysis_input_n10013_sanitized.csv`: the 10,013-video input
  used for the main video-level analyses. It contains the video/channel
  identifiers and analysis variables required by the models, including view,
  like, and comment counts, day index, format variables, political-party and
  policy labels, and the four rhetoric labels. Titles, channel names,
  categories, durations, normalized metrics, and subscriber counts are not
  included.
- `data/annotation_500_final_sanitized.csv`: the 500-video annotation sample
  with the final majority-vote labels and analysis-relevant metadata. It does
  not include titles, annotator-level records, notes, or individual annotator
  identifiers.
- `data/comment_wrime_scores_sanitized.csv.gz`: comment-level WRIME scores for
  eight emotions, together with the minimum linkage and processing fields
  needed for aggregation. It does not include comment text, comment IDs,
  parent IDs, author IDs, or URLs.

The released materials reproduce the main video-level analyses and the
aggregation of comment-level WRIME scores. They do not reproduce the original
text-to-WRIME inference step, because the underlying comment text and comment
identifiers are not redistributed.

## Data release review and restrictions

Before release, each field was reviewed against the YouTube Data API Services
Terms and Developer Policies, privacy and copyright considerations, and the
requirements for a Scientific Reports data availability statement. The review
was informed by the release strategy used in [An Audit of Misinformation Filter
Bubbles on YouTube](https://github.com/kinit-sk/yaudit-recsys-2021): release
reproducibility-enabling derived data and code where permitted, while avoiding
bulk redistribution of raw YouTube/API-derived user content and documenting
how researchers can reacquire or regenerate restricted inputs.

Accordingly, the following materials are not publicly distributed:

- raw YouTube API responses and cached API exports;
- comment text and comment-level identifiers;
- author or channel-user profile information beyond the identifiers retained
  in the sanitized analysis input;
- raw embedding files, comment-level UMAP coordinates, semantic-comment
  caches, and files that could facilitate reconstruction or linkage of the
  underlying comments;
- API credentials, OAuth tokens, cookies, and machine-specific paths.

The governing documents are explicit about these constraints. The [YouTube
Developer Policies](https://developers.google.com/youtube/terms/developer-policies)
state that, after the permitted storage period, an API client must “either
delete or refresh the stored data,” and must make reasonable efforts to keep
stored API data consistent with the current data available through YouTube.
The [YouTube API Services Terms](https://developers.google.com/youtube/terms/api-services-terms-of-service)
also require API clients to comply with applicable privacy laws and to maintain
controls protecting the privacy, security, and confidentiality of YouTube data.
These provisions are why this repository does not publish a static bulk copy of
raw API responses or comment content; it publishes only reviewed, minimized
research inputs and derived scores.

YouTube-derived data can change over time and may be subject to deletion or
privacy requests. The released data should therefore be treated as a
time-stamped research release, not as a permanent mirror of YouTube.

The embedding-based exploratory analysis is not included in the reproducible
scope of this minimum release. Its embeddings were generated directly from
YouTube comment text and retain information about the semantic content of
individual user-generated comments. Publishing them with video identifiers,
UMAP coordinates, or row-level indices could enable semantic inference or
linkage to other public records. They also remain derived representations of
third-party content, so withholding the text does not remove the associated
privacy, copyright, deletion, and platform-policy considerations.

We therefore do not distribute the comment-level embeddings, UMAP coordinates,
K-means assignments, embedding caches, or comment-to-coordinate indices. This
is a deliberate data-protection and terms-compliance decision. Because the
restricted text and its derived representations are not released, the
embedding-to-UMAP-to-K-means analysis cannot be independently rerun from this
repository.

## Code overview

- `code/h1a_content_fe.py`: estimates the H1a video-view models using channel
  fixed effects, short-video and publication-date controls, followed by staged
  political-party, format, and policy controls.
- `code/h1bc_content_fe.py`: estimates the engagement models for like counts
  and comment counts using profiled Poisson channel fixed effects with view
  exposure and staged controls.
- `code/aggregate_wrime_public.py`: validates the released WRIME scores and
  aggregates them to the video level.
- `code/h2ab_wrime_video_fe_public.py`: creates the H2ab video-level WRIME analysis input
  from the released score table without requiring comment text or identifiers.

All public scripts read from `data/` and write derived outputs to `results/`.
Supplementary clickbait specifications are not included in this minimum
release; the repository focuses on the manuscript's primary M0–M3 analyses.

## Contents

- `data/README.md` — safe data-release workflow.
- `code/README.md` — code-release workflow and provenance.
- `data/main_analysis_input_n10013_sanitized.csv` — sanitized main-analysis input.
- `data/annotation_500_final_sanitized.csv` — sanitized 500-video final-consensus annotations.
- `data/comment_wrime_scores_sanitized.csv.gz` — comment-level WRIME scores without comment text or IDs.

## Reproduction route

The reproducible route is: obtain the permitted identifiers and field definitions from this repository, reacquire current public metadata through the documented YouTube API workflow, apply the published label and analysis code, and report the retrieval date. Results involving mutable metrics should be interpreted as time-stamped observations, not permanent copies of YouTube state.

## License and third-party material

Documentation and original code added to this repository may be released under MIT unless the authors specify another license. YouTube metadata, comments, titles, and other third-party material remain subject to their original rights and the YouTube API Services Terms; this repository does not grant a license to redistribute them.

## Contact and takedown

For a suspected privacy, copyright, or deletion issue, open a private contact request with the corresponding author rather than posting personal data in a public issue. The maintainers will review and remove or update affected derived artifacts as appropriate.

