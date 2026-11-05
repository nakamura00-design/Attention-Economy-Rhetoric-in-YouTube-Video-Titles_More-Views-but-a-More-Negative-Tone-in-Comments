# Data release workflow

No raw or bulk YouTube-derived dataset is included in the initial release.

Before adding a data file:

1. Record its source, retrieval date, and exact fields.
2. Separate API-derived fields from author-created labels and aggregates.
3. Remove raw comment text, author identifiers, private data, credentials, and unnecessary third-party content.
4. Check current YouTube policy, deletion/refresh obligations, copyright, and applicable research-ethics requirements.
5. Run a secret scan and a small-cell/re-identification review.
6. Add the file, checksum, license/rights note, and update procedure to `RELEASE_MANIFEST.csv`.

Researchers needing the source observations should use the documented API reacquisition route where permitted. The repository does not promise that a later API response will be identical to the original observation.

