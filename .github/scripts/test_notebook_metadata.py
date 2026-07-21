#!/usr/bin/env python3
"""Tests for author extraction, focused on the cell-scan / label-match behaviour.

Run: python .github/scripts/test_notebook_metadata.py   (or via pytest)

Regression context: the extractor originally read only cells[0]. Notebooks that
follow the project template put the title in cells[0] and the "**Author**:" line
in a later markdown cell, so their author was silently dropped and the Zenodo
publisher fell back to the generic "Neurodesk Project" creator.
"""

from notebook_metadata import (
    extract_authors_from_notebook,
    extract_authors_from_first_cell_source,
)


def _md(*sources):
    return {"cells": [{"cell_type": "markdown", "source": s} for s in sources]}


def test_author_in_first_cell_still_works():
    nb = _md("# Title\n\n**Author**: Jane Doe\n")
    assert extract_authors_from_notebook(nb) == ["Jane Doe"]


def test_author_in_second_cell_template_layout():
    # Title and author in separate cells — the layout that used to be dropped.
    nb = _md("# Scripted First-Level Analyses\n", "**Author**: John Smith\n")
    assert extract_authors_from_notebook(nb) == ["John Smith"]


def test_author_inside_html_orcid_markup():
    # Mirrors the real Demo_fmriprep_FEAT header: label on one line, name wrapped
    # in an ORCID <a>/<i> block on the next.
    cell = (
        '**Author**: <div style="margin-top: 10px;">\n'
        '    <a href="https://orcid.org/0000-0001-5754-9633" target="_blank">\n'
        '        <i class="fab fa-orcid"></i> David V. Smith\n'
        "    </a>\n"
        "</div>\n"
    )
    assert extract_authors_from_notebook(_md("# Title\n", cell)) == ["David V. Smith"]


def test_template_decoy_line_is_not_matched():
    # "Author of this template : X" is an instruction sentence, not an author field.
    src = "**Author of this template** : Someone Example [Remove this line]\n"
    assert extract_authors_from_first_cell_source(src) == []


def test_multiple_authors_split():
    nb = _md("# Title\n", "**Author**: Ada Lovelace and Alan Turing\n")
    assert extract_authors_from_notebook(nb) == ["Ada Lovelace", "Alan Turing"]


def test_scan_stops_at_first_code_cell():
    # An "Author:" that only appears after code (e.g. in prose) must not be picked up.
    nb = {
        "cells": [
            {"cell_type": "markdown", "source": "# Title only\n"},
            {"cell_type": "code", "source": "print('hi')\n"},
            {"cell_type": "markdown", "source": "**Author**: Too Late\n"},
        ]
    }
    assert extract_authors_from_notebook(nb) == []


def test_leading_raw_cell_is_skipped_not_boundary():
    nb = {
        "cells": [
            {"cell_type": "raw", "source": "---\nrise config\n---\n"},
            {"cell_type": "markdown", "source": "# Title\n"},
            {"cell_type": "markdown", "source": "**Author**: Grace Hopper\n"},
        ]
    }
    assert extract_authors_from_notebook(nb) == ["Grace Hopper"]


def test_no_author_returns_empty():
    nb = _md("# Just a title\n", "Some description with no author line.\n")
    assert extract_authors_from_notebook(nb) == []


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {t.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    raise SystemExit(1 if failed else 0)
