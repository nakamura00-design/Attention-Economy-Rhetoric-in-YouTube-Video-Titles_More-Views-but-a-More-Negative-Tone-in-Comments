# Data and code companion repository

This repository is the staged public-release package for the Scientific Reports manuscript on attention-economy rhetoric, audience engagement, and comment emotions in YouTube political communication.

## Release status

This is the minimum safe release prepared for submission. It intentionally contains documentation, a data dictionary, a release manifest, and reproducibility placeholders; it does **not** redistribute a bulk copy of YouTube API responses or comment text.

The source workspace contains video-level metadata, a 500-video annotation sample, analysis code, and comment-derived analyses. Those files are not copied here until each field has been checked against the current YouTube API Services Terms and Developer Policies, privacy requirements, copyright, and any applicable data-subject deletion request.

## Contents

- `DATA_AVAILABILITY.md` — proposed manuscript statement and staged-release policy.
- `PUBLICATION_POLICY.md` — field-by-field publication decision.
- `DATA_DICTIONARY.md` — intended public schema and redaction rules.
- `RELEASE_MANIFEST.csv` — current release inventory; empty entries mean that no file is being redistributed yet.
- `data/README.md` — safe data-release workflow.
- `code/README.md` — code-release workflow and provenance.

## Reproduction route

The reproducible route is: obtain the permitted identifiers and field definitions from this repository, reacquire current public metadata through the documented YouTube API workflow, apply the published label and analysis code, and report the retrieval date. Results involving mutable metrics should be interpreted as time-stamped observations, not permanent copies of YouTube state.

## License and third-party material

Documentation and original code added to this repository may be released under MIT unless the authors specify another license. YouTube metadata, comments, titles, and other third-party material remain subject to their original rights and the YouTube API Services Terms; this repository does not grant a license to redistribute them.

## Contact and takedown

For a suspected privacy, copyright, or deletion issue, open a private contact request with the corresponding author rather than posting personal data in a public issue. The maintainers will review and remove or update affected derived artifacts as appropriate.

