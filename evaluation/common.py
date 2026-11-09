"""Shared helpers for the evaluation CLIs: paths, CSV/JSONL writers, resume, hashing, budget."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import re
import subprocess
import sys
import threading
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from core.config import REPO_ROOT, RESULTS_DIR
from core.models import resolve_model_aliases


EXTRACTION_DIR = RESULTS_DIR / "extraction"
PIPELINE_DIR = RESULTS_DIR / "pipeline"
ABLATION_DIR = RESULTS_DIR / "ablation"
# Ablation on a fixed bank of real invalid generations (see evaluation/run_ablation_stress.py).
ABLATION_STRESS_DIR = RESULTS_DIR / "ablation_stress"
BEST_REQUIREMENTS_PATH = EXTRACTION_DIR / "best_requirements.json"


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def add_models_arg(parser: argparse.ArgumentParser, default: list[str] | None = None) -> None:
    parser.add_argument(
        "--models", nargs="+", default=default or ["all"],
        help="Model aliases from core/models.py, or 'all' (= every candidate).",
    )


def parse_models(parser: argparse.ArgumentParser, aliases: list[str]) -> list[str]:
    try:
        return resolve_model_aliases(aliases)
    except ValueError as exc:
        parser.error(str(exc))


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------
def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, columns: Iterable[str], rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns))
        writer.writeheader()
        writer.writerows(rows)


def read_csv_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def read_csv_keys(path: Path, key_columns: Iterable[str]) -> set[tuple[str, ...]]:
    key_columns = list(key_columns)
    return {tuple(str(row[c]) for c in key_columns) for row in read_csv_rows(path)}


class CsvAppender:
    """Append-only CSV writer (header on first write, flush per row, thread-safe)."""

    def __init__(self, path: Path, columns: Iterable[str], lock: threading.RLock | None = None) -> None:
        self.path = path
        self.columns = list(columns)
        self.lock = lock or threading.RLock()
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > 0:
            with path.open(newline="", encoding="utf-8") as fh:
                header = next(csv.reader(fh), [])
            if header != self.columns:
                raise RuntimeError(
                    f"{path} has a different header than expected; move it away before resuming.\n"
                    f"found={header}\nexpected={self.columns}"
                )

    def append_many(self, rows: Iterable[dict]) -> None:
        rows = list(rows)
        with self.lock:
            write_header = not self.path.exists() or self.path.stat().st_size == 0
            with self.path.open("a", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=self.columns)
                if write_header:
                    writer.writeheader()
                writer.writerows(rows)
                fh.flush()

    def append(self, row: dict) -> None:
        self.append_many([row])


class JsonlAppender:
    def __init__(self, path: Path, lock: threading.RLock | None = None) -> None:
        self.path = path
        self.lock = lock or threading.RLock()
        path.parent.mkdir(parents=True, exist_ok=True)

    def append_many(self, records: Iterable[dict]) -> None:
        lines = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
        with self.lock, self.path.open("a", encoding="utf-8") as fh:
            fh.write(lines)
            fh.flush()


# ---------------------------------------------------------------------------
# Requirements
# ---------------------------------------------------------------------------
def normalize_requirements(requirements: Any) -> dict[str, list[str]]:
    """Keep only {category: [non-empty str, ...]} entries; drop empty categories."""
    normalized: dict[str, list[str]] = {}
    if not isinstance(requirements, dict):
        return normalized
    for category, reqs in requirements.items():
        if not isinstance(reqs, list):
            continue
        cleaned = [str(r).strip() for r in reqs if isinstance(r, (str, int, float)) and str(r).strip()]
        if cleaned:
            normalized[str(category).strip()] = cleaned
    return normalized


def count_requirements(requirements: dict[str, list[str]]) -> int:
    return sum(len(v) for v in requirements.values())


def requirements_sha256(requirements: dict[str, list[str]]) -> str:
    canonical = json.dumps(requirements, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_best_requirements(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(
            f"error: requirements file not found: {path}\n"
            "The input requirements of the study are not distributed (see Data availability in README.md). Try the "
            "invented example with --requirements examples/greenhouse_requirements.json, or build your own input "
            "with evaluation.run_extraction. Nothing was run."
        )
    payload = read_json(path)
    requirements = payload["requirements"]
    digest = requirements_sha256(requirements)
    if payload.get("sha256") and payload["sha256"] != digest:
        raise SystemExit(f"{path}: sha256 mismatch (file was modified by hand?)")
    payload["sha256"] = digest
    return payload


def slugify(text: str, max_len: int = 80) -> str:
    slug = re.sub(r"[^\w\-]+", "_", text.strip(), flags=re.ASCII).strip("_") or "category"
    if len(slug) > max_len:
        slug = f"{slug[:max_len]}_{hashlib.sha1(text.encode('utf-8')).hexdigest()[:8]}"
    return slug


# ---------------------------------------------------------------------------
# Budget
# ---------------------------------------------------------------------------
class Budget:
    """Thread-safe running total of USD spent in this invocation."""

    def __init__(self, limit_usd: float | None) -> None:
        self.limit_usd = limit_usd
        self.spent_usd = 0.0
        self._lock = threading.Lock()

    def add(self, cost_usd: float) -> None:
        with self._lock:
            self.spent_usd += cost_usd

    @property
    def exceeded(self) -> bool:
        return self.limit_usd is not None and self.spent_usd >= self.limit_usd


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------
# Frozen files (generation prompt, repair prompt, router, knowledge bases): SHA-256 stored in this file.
FROZEN_MANIFEST = REPO_ROOT / "tests" / "golden" / "frozen_files.json"


def frozen_file_mismatches() -> list[str]:
    """Frozen files whose content differs from the stored hashes (line endings normalised, for Windows checkouts)."""
    files = read_json(FROZEN_MANIFEST)["files"]
    mismatches = []
    for rel, expected in files.items():
        path = REPO_ROOT / rel
        data = path.read_bytes().replace(b"\r\n", b"\n") if path.exists() else b""
        if hashlib.sha256(data).hexdigest() != expected:
            mismatches.append(rel)
    return mismatches


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


@lru_cache(maxsize=1)
def git_state() -> dict:
    """Code version of this process, computed once.

    git_dirty: uncommitted changes to tracked or untracked files outside results/ (the outputs being
    written) and paper/ (ignored). frozen_prompt_kb_match: the frozen files match the stored hashes.
    """
    status = _git("status", "--porcelain", "--", ".", ":(exclude)results", ":(exclude)paper")
    return {
        "git_commit": _git("rev-parse", "HEAD"),
        "git_dirty": None if status is None else bool(status),
        "frozen_prompt_kb_match": not frozen_file_mismatches(),
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def provenance(model_id: str, requirements_sha256: str, timestamp_utc: str | None = None) -> dict:
    """Fields every new generation, repair and judgment carries."""
    return {**git_state(), "timestamp_utc": timestamp_utc or utc_now(), "model_id": model_id,
            "requirements_sha256": requirements_sha256}


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_run_manifest(out_dir: Path, **fields: Any) -> None:
    """Appends one record per invocation (command line, code version, inputs) to <out_dir>/run_manifest.jsonl."""
    record = {"timestamp_utc": utc_now(), "argv": sys.argv, **git_state(), **fields}
    JsonlAppender(out_dir / "run_manifest.jsonl").append_many([record])
