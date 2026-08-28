"""Sphinx extension: inject <meta name="nd-review-id"> from page metadata.

Works for both .ipynb (notebook-level metadata) and .md/.myst (YAML
front-matter).  The badge JS reads this meta tag to look up the page
in reviews.json.

Setup (in _config.yml):
  sphinx:
    local_extensions:
      nd_review_meta: _ext
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from docutils.nodes import document
from sphinx.application import Sphinx


def _get_review_id_from_nb_metadata(app: Sphinx, pagename: str) -> Optional[str]:
    """Try to read nd_review_id from notebook (.ipynb) metadata."""
    srcdir = Path(app.srcdir)
    nb_path = srcdir / f"{pagename}.ipynb"
    if not nb_path.is_file():
        return None
    try:
        with nb_path.open("r", encoding="utf-8") as f:
            nb = json.load(f)
        return nb.get("metadata", {}).get("nd_review_id") or None
    except Exception:
        return None


def _get_review_id_from_doctree(doctree: Optional[document]) -> Optional[str]:
    """Try to read nd_review_id from MyST/RST front-matter (docinfo).

    MyST-Parser stores front-matter fields in the doctree's top-level
    field_list or in document.settings.env metadata.
    """
    if doctree is None:
        return None

    # MyST-Parser exposes front-matter via the docutils 'meta' mechanism
    # and also as document settings.
    fm = getattr(doctree.settings, "myst_frontmatter", None) or {}
    if isinstance(fm, dict):
        rid = fm.get("nd_review_id")
        if rid:
            return str(rid)

    return None


def _get_review_id_from_env(app: Sphinx, pagename: str) -> Optional[str]:
    """Try to read nd_review_id from Sphinx environment metadata.

    Jupyter Book / MyST stores notebook metadata under
    env.metadata[pagename].
    """
    env = app.env
    if env is None:
        return None

    # myst_nb stores notebook metadata here
    meta = getattr(env, "metadata", {}).get(pagename, {})
    if isinstance(meta, dict):
        rid = meta.get("nd_review_id")
        if rid:
            return str(rid)

    # nb_metadata is another possible location
    nb_meta = getattr(env, "nb_metadata", {}).get(pagename, {})
    if isinstance(nb_meta, dict):
        rid = nb_meta.get("nd_review_id")
        if rid:
            return str(rid)

    return None


def add_review_meta(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: Optional[document],
) -> None:
    """html-page-context event handler — inject the meta tag."""

    review_id = (
        _get_review_id_from_doctree(doctree)
        or _get_review_id_from_env(app, pagename)
        or _get_review_id_from_nb_metadata(app, pagename)
    )

    if not review_id:
        return

    # Append a raw <meta> tag via context["metatags"].
    # Sphinx uses this list to render meta tags in the <head>.
    metatags = context.get("metatags", "")
    meta_html = f'<meta name="nd-review-id" content="{review_id}">\n'
    context["metatags"] = metatags + meta_html


def setup(app: Sphinx) -> dict[str, Any]:
    app.connect("html-page-context", add_review_meta)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
