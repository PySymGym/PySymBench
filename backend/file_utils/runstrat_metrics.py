import csv
import statistics
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunstratAggregates:
    tests: float
    errors: float
    coverage: float
    total_time_sec: float


def _read_runstrat_csv(filepath: str | Path) -> list[dict]:
    with open(filepath, newline="") as f:
        return list(csv.DictReader(f))


def compute_averages(filepath: str | Path) -> RunstratAggregates:
    rows = _read_runstrat_csv(filepath)
    return RunstratAggregates(
        tests=statistics.mean([float(r["tests"]) for r in rows]),
        errors=statistics.mean([float(r["errors"]) for r in rows]),
        coverage=statistics.mean([float(r["coverage"]) for r in rows]),
        total_time_sec=statistics.mean([float(r["total_time_sec"]) for r in rows]),
    )


def compute_medians(filepath: str | Path) -> RunstratAggregates:
    rows = _read_runstrat_csv(filepath)
    return RunstratAggregates(
        tests=statistics.median([float(r["tests"]) for r in rows]),
        errors=statistics.median([float(r["errors"]) for r in rows]),
        coverage=statistics.median([float(r["coverage"]) for r in rows]),
        total_time_sec=statistics.median([float(r["total_time_sec"]) for r in rows]),
    )


def compute_total_time(filepath: str | Path) -> float:
    rows = _read_runstrat_csv(filepath)
    return sum(float(r["total_time_sec"]) for r in rows)


def compute_total_tests(filepath: str | Path) -> int:
    rows = _read_runstrat_csv(filepath)
    return sum(int(r["tests"]) for r in rows)


def compute_total_errors(filepath: str | Path) -> int:
    rows = _read_runstrat_csv(filepath)
    return sum(int(r["errors"]) for r in rows)
