#!/usr/bin/env python3
"""Convert asta.allen.ai report JSON to Markdown.

Usage:
  python3 convert_report_to_md.py input.json [output.md]
"""

import argparse
import json
from collections import OrderedDict
import re
from pathlib import Path


def format_citation(cite: dict) -> str:
    cid = str(cite.get("id") or "").strip() or "(Unknown citation)"
    paper = cite.get("paper") or {}
    title = str(paper.get("title") or "").strip()
    year = paper.get("year")
    venue = str(paper.get("venue") or "").strip()

    parts = [cid]
    if title:
        parts.append(f"— {title}")
    if venue and year:
        parts.append(f"({venue}, {year})")
    elif year:
        parts.append(f"({year})")
    elif venue:
        parts.append(f"({venue})")

    return " ".join(parts).strip()


def author_year(cite: dict) -> str:
    paper = cite.get("paper") or {}
    authors = paper.get("authors") or []
    year = paper.get("year")

    name = "Unknown"
    if authors:
        first = str(authors[0].get("name") or "").strip()
        last = first.split()[-1] if first else "Unknown"
        if len(authors) > 1:
            name = f"{last} et al."
        else:
            name = last

    return f"({name}, {year})" if year else f"({name}, n.d.)"


def build_citation_index(sections: list) -> dict:
    index = {}
    for section in sections:
        for cite in section.get("citations") or []:
            paper = cite.get("paper") or {}
            title = str(paper.get("title") or "").strip().lower()
            if title:
                index[title] = cite
            cid = str(cite.get("id") or "").strip()
            if cid:
                index[cid.lower()] = cite
            corpus_id = str(cite.get("corpusId") or "").strip()
            if corpus_id:
                index[corpus_id] = cite
    return index


def replace_paper_tags(text: str, index: dict) -> str:
    # Match <Paper ...>...</Paper> and prefer the paperTitle attribute if present.
    pattern = re.compile(r"<Paper([^>]*)>(.*?)</Paper>", re.DOTALL)

    def repl(match: re.Match) -> str:
        attrs = match.group(1) or ""
        inner = (match.group(2) or "").strip()

        # Extract paperTitle="..." or paperTitle='...'
        m = re.search(r'paperTitle\s*=\s*([\"\'])(.*?)\1', attrs)
        if m:
            return m.group(2).strip()

        # Fallback: try to map inner text to a citation to produce (Author, Year)
        key = inner
        cite = index.get(key.lower()) or index.get(key)
        if cite:
            return author_year(cite)

        # Last resort: preserve content
        return inner or "(Unknown, n.d.)"

    return pattern.sub(repl, text)


def render_table(table: dict) -> str:
    columns = table.get("columns") or []
    rows = table.get("rows") or []
    cells = table.get("cells") or {}

    headers = ["Paper"] + [str(c.get("name") or "").strip() for c in columns]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in rows:
        row_id = row.get("id")
        row_name = str(row.get("displayValue") or "").strip()
        values = [row_name]
        for col in columns:
            col_id = col.get("id")
            cell = cells.get(f"{row_id}_{col_id}") or {}
            values.append(str(cell.get("displayValue") or "").strip())
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert asta report JSON to Markdown.")
    parser.add_argument("input", help="Path to report JSON file")
    parser.add_argument("output", nargs="?", help="Path to output Markdown file")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    out_path = Path(args.output) if args.output else in_path.with_suffix(".md")

    with in_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    sections = data.get("sections") or []
    if not isinstance(sections, list):
        raise SystemExit("Invalid format: 'sections' is not a list")

    citation_index = build_citation_index(sections)

    lines = []
    # Concatenate sections: title + text
    for section in sections:
        title = str(section.get("title") or "").strip()
        text = str(section.get("text") or "").strip()
        if text:
            text = replace_paper_tags(text, citation_index)
        if title:
            lines.append(f"## {title}")
        if text:
            lines.append(text)
        table = section.get("table")
        if isinstance(table, dict) and table.get("columns") and table.get("rows"):
            lines.append("")
            lines.append(render_table(table))
        lines.append("")

    # Collect citations (dedupe by id, preserve order)
    ordered = OrderedDict()
    for section in sections:
        for cite in section.get("citations") or []:
            cid = str(cite.get("id") or "").strip() or str(cite.get("corpusId") or "").strip()
            if cid and cid not in ordered:
                ordered[cid] = cite

    if ordered:
        lines.append("## Citations")
        for cite in sorted(ordered.values(), key=lambda c: format_citation(c).lower()):
            lines.append(f"- {format_citation(cite)}")
        lines.append("")

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
