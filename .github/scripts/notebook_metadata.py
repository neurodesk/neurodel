#!/usr/bin/env python3
"""Helpers to extract author metadata from notebooks and markdown files."""

from __future__ import annotations

import json
import re
from typing import List


# Require a ':' after the label. Without it, a sentence line such as the template's
# "Author of this template : ..." instruction is mistaken for an author field. The
# markdown and front-matter paths below already require the colon; this aligns the
# notebook path with them.
_AUTHOR_LINE_RE = re.compile(r"^authors?\s*:\s*(.*)$", re.IGNORECASE)
_STOP_LINE_RE = re.compile(
    r"^(date|title|license|doi|institution|affiliation|contact|email|version)\b",
    re.IGNORECASE,
)
_FRONT_MATTER_RE = re.compile(r"(?s)\A---\n(.*?)\n---\n")


def _strip_markdown(text: str) -> str:
    """Collapse simple markdown formatting to plain text."""
    cleaned = text.strip()
    cleaned = re.sub(r"\[(.*?)\]\([^)]*\)", r"\1", cleaned)
    cleaned = re.sub(r"</?[^>]+>", " ", cleaned)
    cleaned = cleaned.replace("&nbsp;", " ")
    cleaned = cleaned.replace("**", "").replace("__", "").replace("`", "")
    cleaned = cleaned.replace("*", "").replace("_", "")
    cleaned = re.sub(r"^\s*[-+>#]+\s*", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _looks_like_person(token: str) -> bool:
    words = [word for word in token.split() if word]
    if len(words) < 2:
        return False
    if not any(ch.isalpha() for ch in token):
        return False
    if token.upper() == token and len(token) <= 6:
        return False
    return True


def _split_authors(raw_value: str) -> List[str]:
    """Split a raw author string into a list of names."""
    value = _strip_markdown(raw_value)
    value = re.sub(r"\s+and\s+", " & ", value, flags=re.IGNORECASE)

    if "&" in value:
        candidates = [part.strip() for part in value.split("&")]
    elif ";" in value:
        candidates = [part.strip() for part in value.split(";")]
    elif "," in value and "(" not in value and ")" not in value:
        parts = [part.strip() for part in value.split(",") if part.strip()]
        if len(parts) >= 2 and all(_looks_like_person(part) for part in parts):
            candidates = parts
        else:
            candidates = [value]
    else:
        candidates = [value]

    deduped: List[str] = []
    for candidate in candidates:
        normalized = _strip_markdown(candidate)
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def extract_authors_from_first_cell_source(first_cell_source: str) -> List[str]:
    """Extract author names from the first notebook cell text."""
    lines = first_cell_source.splitlines()
    for index, line in enumerate(lines):
        cleaned_line = _strip_markdown(line)
        match = _AUTHOR_LINE_RE.match(cleaned_line)
        if not match:
            continue

        inline_value = match.group(1).strip()
        if inline_value:
            return _split_authors(inline_value)

        continuation: List[str] = []
        for next_line in lines[index + 1 :]:
            raw_next = next_line.strip()
            cleaned_next = _strip_markdown(next_line)

            if not cleaned_next:
                if continuation:
                    break
                continue
            if _STOP_LINE_RE.match(cleaned_next):
                break
            if raw_next.startswith("#"):
                break
            if _AUTHOR_LINE_RE.match(cleaned_next):
                break

            continuation.append(cleaned_next)

        if continuation:
            return _split_authors(" ".join(continuation))
        return []

    return []


def extract_authors_from_notebook(notebook_obj: dict) -> List[str]:
    """Extract author names from the notebook's leading markdown header.

    The project template puts the title in the first cell and the "**Author**:"
    line in a *later* markdown cell, so scanning only cells[0] misses the author
    and the publisher falls back to a generic creator. Scan the contiguous
    markdown header block instead and return the first hit.

    The scan stops at the first code cell — author metadata always lives in the
    header, so stopping there avoids picking up stray "Author:" mentions in later
    citation/reference prose. Non-code, non-markdown cells (e.g. leading raw
    cells) are skipped rather than treated as the boundary.
    """
    for cell in notebook_obj.get("cells", []):
        cell_type = cell.get("cell_type")
        if cell_type == "code":
            break
        if cell_type != "markdown":
            continue
        source = cell.get("source", [])
        cell_source = "".join(source) if isinstance(source, list) else str(source)
        authors = extract_authors_from_first_cell_source(cell_source)
        if authors:
            return authors
    return []


def extract_authors_from_first_cell(notebook_path: str) -> List[str]:
    """Load a notebook and return author names from its leading markdown header."""
    with open(notebook_path, "r", encoding="utf-8") as fh:
        notebook_obj = json.load(fh)
    return extract_authors_from_notebook(notebook_obj)


def _extract_front_matter(markdown_text: str) -> str:
    """Return YAML front matter content without delimiters."""
    match = _FRONT_MATTER_RE.match(markdown_text)
    return match.group(1) if match else ""


def _extract_authors_from_front_matter(front_matter: str) -> List[str]:
    """Extract author/authors from markdown front matter."""
    if not front_matter:
        return []

    lines = front_matter.splitlines()
    for idx, line in enumerate(lines):
        match = re.match(r"^\s*authors?\s*:\s*(.*)$", line, flags=re.IGNORECASE)
        if not match:
            continue

        inline_value = match.group(1).strip()
        if inline_value and inline_value not in ("|", ">"):
            if inline_value.startswith("[") and inline_value.endswith("]"):
                inline_value = inline_value[1:-1]
            return _split_authors(inline_value)

        collected: List[str] = []
        for next_line in lines[idx + 1 :]:
            if re.match(r"^\s*[A-Za-z0-9_-]+\s*:", next_line):
                break
            list_match = re.match(r"^\s*-\s*(.+)\s*$", next_line)
            if list_match:
                collected.append(list_match.group(1).strip())
                continue
            if next_line.strip():
                collected.append(next_line.strip())
                continue
            if collected:
                break

        if collected:
            return _split_authors(" & ".join(collected))
        return []

    return []


def _extract_authors_from_markdown_body(markdown_text: str) -> List[str]:
    """Extract author names from common markdown body patterns."""
    for line in markdown_text.splitlines()[:120]:
        cleaned = _strip_markdown(line)
        if not cleaned:
            continue

        author_match = re.match(r"^authors?\s*:\s*(.+)$", cleaned, flags=re.IGNORECASE)
        if author_match:
            return _split_authors(author_match.group(1).strip())

        created_match = re.search(
            r"\bthis tutorial was created by\s+(.+?)(?:[.!]|$)",
            cleaned,
            flags=re.IGNORECASE,
        )
        if created_match:
            return _split_authors(created_match.group(1).strip())

    return []


def extract_authors_from_markdown(markdown_path: str) -> List[str]:
    """Load a markdown file and return author names from front matter/body."""
    with open(markdown_path, "r", encoding="utf-8") as fh:
        markdown_text = fh.read()

    front_matter = _extract_front_matter(markdown_text)
    authors = _extract_authors_from_front_matter(front_matter)
    if authors:
        return authors

    return _extract_authors_from_markdown_body(markdown_text)


def extract_authors_from_content(content_path: str) -> List[str]:
    """Dispatch author extraction based on file extension."""
    lowered = content_path.lower()
    if lowered.endswith(".ipynb"):
        return extract_authors_from_first_cell(content_path)
    if lowered.endswith(".md"):
        return extract_authors_from_markdown(content_path)
    return []
