import csv
import statistics
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunstratMetrics:
    total_tests: int
    total_errors: int
    mean_coverage: float
    median_coverage: float
    total_time_sec: float
    methods_with_results: int


def _read_rows(filepath: str | Path) -> list[dict]:
    with open(filepath, newline="") as f:
        return list(csv.DictReader(f))


def compute_metrics(filepath: str | Path) -> RunstratMetrics:
    return _compute_from_rows(_read_rows(filepath))


def combine_metrics(filepaths: list[str | Path]) -> RunstratMetrics:
    all_rows: list[dict] = []
    for fp in filepaths:
        all_rows.extend(_read_rows(fp))
    return _compute_from_rows(all_rows)


def _compute_from_rows(rows: list[dict]) -> RunstratMetrics:
    coverages = [float(r["coverage"]) for r in rows]
    return RunstratMetrics(
        total_tests=sum(int(r["tests"]) for r in rows),
        total_errors=sum(int(r["errors"]) for r in rows),
        mean_coverage=statistics.mean(coverages),
        median_coverage=statistics.median(coverages),
        total_time_sec=sum(float(r["total_time_sec"]) for r in rows),
        methods_with_results=len(rows),
    )
