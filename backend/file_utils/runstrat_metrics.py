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


def compute_metrics(filepath: str | Path) -> RunstratMetrics:
    with open(filepath, newline="") as f:
        rows = list(csv.DictReader(f))

    coverages = [float(r["coverage"]) for r in rows]

    return RunstratMetrics(
        total_tests=sum(int(r["tests"]) for r in rows),
        total_errors=sum(int(r["errors"]) for r in rows),
        mean_coverage=statistics.mean(coverages),
        median_coverage=statistics.median(coverages),
        total_time_sec=sum(float(r["total_time_sec"]) for r in rows),
    )
