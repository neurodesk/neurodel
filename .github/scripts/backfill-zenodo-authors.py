#!/usr/bin/env python3
"""One-off remediation: correct creators on already-published Zenodo records.

Background
----------
Records published before the author-extraction fix credit "Neurodesk Project"
instead of the notebook's real author (their doi-mapping.json entry has
``authors: []``). Because the publisher short-circuits on an unchanged
source-cell checksum, simply fixing the extractor does NOT touch these records —
they only get a new version when the notebook content changes. This script
corrects them in place.

What it does
------------
For each mapping entry it re-extracts the author(s) from the current content file
and, if that differs from what the record carries, edits the *published* Zenodo
record's metadata IN PLACE (Zenodo "edit" action → PUT metadata → publish). This
keeps the same concept DOI and the same version DOI — no new version is minted.
Metadata is rebuilt with the same ``build_zenodo_metadata`` the normal publisher
uses, so a corrected record is identical to one freshly published with the fix.

Safety
------
- Dry-run by default: prints the planned old→new creators and changes nothing.
  Pass ``--apply`` to actually edit records.
- Skips entries where no real author can be extracted (nothing to improve) and
  entries whose creators already match.
- ``examples/template.ipynb`` is skipped and flagged: it is scaffolding whose
  author cell is a placeholder; its existing DOI should be deleted/deprecated by
  hand rather than re-authored.

Usage
-----
    # Dry run (default) against production Zenodo:
    python .github/scripts/backfill-zenodo-authors.py \
        --doi-mapping doi-mapping.json --zenodo-token "$ZENODO_TOKEN"

    # Actually apply, and write back the updated mapping:
    python .github/scripts/backfill-zenodo-authors.py \
        --doi-mapping doi-mapping.json --output-mapping doi-mapping.json \
        --zenodo-token "$ZENODO_TOKEN" --apply

Rollout (this edits EXISTING published records by ``record_id``, so the Zenodo
sandbox cannot mirror them — mitigate risk with a canary instead of sandbox):
    1. Dry run (default) — inspect the planned old->new creators.
    2. Canary — ``--apply --limit 1`` against prod, then eyeball that DOI.
    3. Full run — ``--apply`` for the rest.
See BACKFILL_RUNBOOK.md for the full post-merge procedure.
"""

import argparse
import importlib.util
import json
import os
import sys

from notebook_metadata import extract_authors_from_content

# Reuse the real publisher's metadata builder + retrying HTTP client. Its filename
# is hyphenated (not a valid module name), so load it by path.
_PUBLISH_PATH = os.path.join(os.path.dirname(__file__), "publish-zenodo.py")
_spec = importlib.util.spec_from_file_location("publish_zenodo", _PUBLISH_PATH)
_pz = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pz)
build_zenodo_metadata = _pz.build_zenodo_metadata
api_request = _pz.api_request
detect_content_type = _pz.detect_content_type

SKIP_KEYS = {"books/examples/template.ipynb"}


def _creator_names(creators):
    return [c.get("name", "") for c in creators or []]


def edit_record_metadata(api_url, record_id, metadata, token):
    """Unlock a published record, replace its metadata, and re-publish (same DOI)."""
    # 1. Move the published record into an editable draft state.
    api_request(
        f"{api_url}/api/deposit/depositions/{record_id}/actions/edit",
        method="POST", token=token,
    )
    # 2. Replace metadata.
    api_request(
        f"{api_url}/api/deposit/depositions/{record_id}",
        method="PUT", data=json.dumps(metadata).encode(), token=token,
    )
    # 3. Re-publish. Same version — no new DOI is minted.
    api_request(
        f"{api_url}/api/deposit/depositions/{record_id}/actions/publish",
        method="POST", token=token,
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doi-mapping", required=True)
    ap.add_argument("--output-mapping", help="If given, write the updated mapping here.")
    ap.add_argument("--zenodo-token", required=True)
    ap.add_argument("--api-url", default="https://zenodo.org")
    ap.add_argument("--repo-root", default=".",
                    help="Repo root that the mapping keys (books/...) are relative to.")
    ap.add_argument("--site-base-url", default="https://neurodesk.org/edu")
    ap.add_argument("--apply", action="store_true",
                    help="Actually edit records. Without this it is a dry run.")
    ap.add_argument("--limit", type=int, default=0,
                    help="Process at most N records that need fixing (0 = no limit). "
                         "Use --limit 1 for a canary run.")
    args = ap.parse_args()

    with open(args.doi_mapping, encoding="utf-8") as fh:
        mapping = json.load(fh)

    planned = corrected = skipped = failed = 0

    for key, entry in mapping.items():
        if args.limit and planned >= args.limit:
            print(f"Reached --limit={args.limit}; stopping (remaining records untouched).")
            break
        record_id = entry.get("record_id")
        content_path = os.path.join(args.repo_root, key)

        if key in SKIP_KEYS:
            print(f"SKIP  {key}: template scaffolding — delete/deprecate its DOI by hand "
                  f"({entry.get('doi_url','')})")
            skipped += 1
            continue
        if not record_id:
            print(f"SKIP  {key}: no record_id in mapping")
            skipped += 1
            continue
        if not os.path.isfile(content_path):
            print(f"SKIP  {key}: content file not found at {content_path} "
                  "(renamed/removed since publish?)")
            skipped += 1
            continue

        authors = extract_authors_from_content(content_path)
        if not authors:
            print(f"SKIP  {key}: still no author extractable — nothing to correct")
            skipped += 1
            continue

        new_creators = [{"name": name} for name in authors]
        old_creators = entry.get("creators")  # may be absent in older mappings
        old_names = _creator_names(old_creators) if old_creators else entry.get("authors") or []

        if list(old_names) == authors:
            skipped += 1
            continue  # already correct

        planned += 1
        print(f"FIX   {key}")
        print(f"        record_id={record_id}  doi={entry.get('doi_url','')}")
        print(f"        creators: {old_names or ['Neurodesk Project (fallback)']} -> {authors}")

        if not args.apply:
            continue

        content_type = entry.get("content_type") or detect_content_type(content_path)
        content_name = os.path.basename(content_path).rsplit(".", 1)[0]
        page_url = entry.get("website_url") or _pz.build_content_page_url(key, args.site_base_url)
        metadata = build_zenodo_metadata(
            content_name=content_name, content_type=content_type,
            content_key=key, page_url=page_url, creators=new_creators,
        )
        try:
            edit_record_metadata(args.api_url, record_id, metadata, args.zenodo_token)
            entry["authors"] = authors
            corrected += 1
            print("        corrected.")
        except Exception as exc:  # noqa: BLE001 — one bad record shouldn't abort the batch
            failed += 1
            print(f"        ::error:: failed to edit {record_id}: {exc}", file=sys.stderr)

    if args.apply and args.output_mapping:
        with open(args.output_mapping, "w", encoding="utf-8") as fh:
            json.dump(mapping, fh, indent=2)
            fh.write("\n")

    print("\n========== BACKFILL SUMMARY ==========")
    mode = "APPLIED" if args.apply else "DRY RUN (no changes made)"
    print(f"Mode:      {mode}")
    print(f"To fix:    {planned}")
    if args.apply:
        print(f"Corrected: {corrected}")
        print(f"Failed:    {failed}")
    print(f"Skipped:   {skipped}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
