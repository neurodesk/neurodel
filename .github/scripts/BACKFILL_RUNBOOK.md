# Backfill runbook — fix author metadata on already-published Zenodo DOIs

**One-off remediation.** Corrects records credited to "Neurodesk Project" before
the author-extraction fix (PR #147). Edits each record's metadata in place —
**same concept DOI, same version DOI, no new version.**

Run it via the **"Backfill Zenodo Authors (one-off)"** GitHub Action, which uses
the existing repo secret `ZENODO_TOKEN` (the token never leaves the repo).

> ⚠️ A `workflow_dispatch` workflow is only runnable when its file is on the
> **default branch (`main`)**. So this tooling (`backfill-zenodo-authors.yml` +
> `backfill-zenodo-authors.py`) ships to `main` **temporarily**, is run, then is
> removed by a cleanup PR. The typo fix and the `notebook_metadata.py` fix stay.

## Prerequisites
- PR #147 (the extractor fix) merged to `main`.
- The "Monika Doeirg" → "Monika Doerig" typo fix in
  `container_paths_neurodesk.ipynb` merged to `main` (so the backfill reads the
  correct name). Folded into the same tooling PR.
- Repo secret `ZENODO_TOKEN` present (it already is — used by `publish-dois`).

## Run it (Actions → "Backfill Zenodo Authors (one-off)" → Run workflow)
Do the three dispatches in order, checking the logs/artifact between each:

1. **Dry run** — inputs: `apply = false`. Prints the ~12 planned `old → new`
   creator changes and writes nothing. Confirm the list looks right.
2. **Canary** — inputs: `apply = true`, `limit = 1`. Fixes ONE record. Open its
   DOI on zenodo.org and confirm the creator is corrected and the **DOI is
   unchanged**.
3. **Full run** — inputs: `apply = true`, `limit = 0`. Fixes the rest.
   Optionally set `push_mapping = true` to sync the `authors` field back to the
   `ci-data` ledger (not required — Zenodo is the source of truth).

## After the run
- Delete `.github/workflows/backfill-zenodo-authors.yml` and
  `.github/scripts/backfill-zenodo-authors.py` (+ this runbook) via a cleanup PR.

## Local alternative (keeps `main` untouched)
If you'd rather not put the workflow on `main`, run the script locally with a
Zenodo personal token that has `deposit:write` + `deposit:actions`:
```bash
git show origin/ci-data:doi-mapping.json > doi-mapping.json
python .github/scripts/backfill-zenodo-authors.py \
  --doi-mapping doi-mapping.json --zenodo-token "$ZENODO_TOKEN"            # dry run
# then --apply --limit 1 (canary), then --apply (full)
```
The Zenodo **sandbox can't be used** either way — we edit existing *production*
records by `record_id`, which don't exist on sandbox; the canary is the safeguard.

## Not handled here (needs a human decision)
Published Zenodo DOIs are **permanent — they cannot be self-deleted.** Skipped by
the backfill; relabel their metadata or leave them:
- `template.ipynb` — a DOI that shouldn't exist (scaffolding).
- `swi` / `unwrapping` / `qsm` — each has an old `.md` DOI plus the current
  `.ipynb` DOI (content migrated `.md → .ipynb`).
