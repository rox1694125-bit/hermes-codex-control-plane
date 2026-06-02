#!/usr/bin/env python3
"""Run a local-only knowledge ingestion demo."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "fixtures" / "sample-article.txt"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "demo-output"
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "plus",
    "that",
    "the",
    "these",
    "this",
    "to",
    "with",
    "without",
}


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def title_from_text(text: str) -> str:
    for line in text.splitlines():
        cleaned = line.strip().lstrip("#").strip()
        if cleaned:
            return cleaned
    return "Untitled Source"


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "untitled-source"


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9-]+", text.lower())


def keyword_counts(text: str) -> list[dict[str, int]]:
    counts: dict[str, int] = {}
    for word in words(text):
        if len(word) < 4 or word in STOPWORDS:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{"term": term, "count": count} for term, count in ranked[:8]]


def summary_sentences(text: str) -> list[str]:
    body = re.sub(r"^#.*$", "", text, flags=re.MULTILINE).strip()
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", body) if item.strip()]
    return sentences[:2]


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def run_demo(input_path: Path, output_dir: Path) -> dict:
    text = read_source(input_path)
    source_id = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    title = title_from_text(text)
    slug = slugify(title)
    keywords = keyword_counts(text)
    summary = summary_sentences(text)

    notes_dir = output_dir / "notes"
    raw_dir = output_dir / "raw"
    reports_dir = output_dir / "reports"
    for directory in (notes_dir, raw_dir, reports_dir):
        directory.mkdir(parents=True, exist_ok=True)

    note_path = notes_dir / f"{slug}.md"
    raw_path = raw_dir / f"{source_id}.txt"
    index_path = output_dir / "index.json"
    report_path = reports_dir / "latest-run.json"

    raw_path.write_text(text, encoding="utf-8")

    keyword_lines = "\n".join(f"- {item['term']} ({item['count']})" for item in keywords)
    summary_lines = "\n".join(f"- {sentence}" for sentence in summary)
    note_path.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                f"Source ID: `{source_id}`",
                f"Input: `{input_path.name}`",
                "",
                "## Summary",
                "",
                summary_lines,
                "",
                "## Candidate Concepts",
                "",
                keyword_lines,
                "",
                "## Runtime Boundary",
                "",
                "This demo is local-only. It performs no network calls, external writes, credential edits, or Hermes gateway operations.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    record = {
        "title": title,
        "source_id": source_id,
        "source_file": input_path.name,
        "note": relative(note_path, output_dir),
        "raw": relative(raw_path, output_dir),
        "keywords": keywords,
        "summary": summary,
        "word_count": len(words(text)),
    }
    write_json(index_path, {"records": [record]})
    write_json(
        report_path,
        {
            "ok": True,
            "input": input_path.name,
            "artifacts": {
                "index": relative(index_path, output_dir),
                "note": relative(note_path, output_dir),
                "raw": relative(raw_path, output_dir),
            },
            "record": record,
        },
    )

    return {
        "ok": True,
        "title": title,
        "source_id": source_id,
        "output_dir": str(output_dir),
        "artifacts": {
            "index": str(index_path),
            "note": str(note_path),
            "raw": str(raw_path),
            "report": str(report_path),
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local knowledge ingestion demo.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Local text source to ingest")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Directory for generated demo artifacts")
    parser.add_argument("--json", action="store_true", help="Print machine-readable run summary")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if re.match(r"^[a-z][a-z0-9+.-]*://", args.input, flags=re.IGNORECASE):
        print("URL inputs are intentionally not fetched by this local demo.", file=sys.stderr)
        return 2

    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()

    if not input_path.is_file():
        print(f"Input file does not exist: {input_path}", file=sys.stderr)
        return 2

    result = run_demo(input_path, output_dir)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Knowledge ingestion demo: PASS")
        print(f"Title: {result['title']}")
        print(f"Output: {result['output_dir']}")
        for name, path in result["artifacts"].items():
            print(f"- {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
