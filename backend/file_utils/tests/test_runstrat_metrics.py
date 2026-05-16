import csv

import pytest

from backend.file_utils.runstrat_metrics import (
    RunstratMetrics,
    combine_metrics,
    compute_metrics,
    merge_csvs,
)

FIELDNAMES = ["tests", "errors", "coverage", "total_time_sec"]


def write_metrics_csv(path, rows: list[dict]) -> str:
    filepath = path / "metrics.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    return str(filepath)


def test_compute_metrics_single_row(tmp_path):
    filepath = write_metrics_csv(
        tmp_path,
        [{"tests": 10, "errors": 2, "coverage": 0.75, "total_time_sec": 30.0}],
    )

    result = compute_metrics(filepath)

    assert result == RunstratMetrics(
        total_tests=10,
        total_errors=2,
        mean_coverage=0.75,
        median_coverage=0.75,
        total_time_sec=30.0,
        methods_with_results=1,
    )


def test_compute_metrics_totals_are_summed(tmp_path):
    filepath = write_metrics_csv(
        tmp_path,
        [
            {"tests": 5, "errors": 1, "coverage": 0.5, "total_time_sec": 10.0},
            {"tests": 3, "errors": 0, "coverage": 0.9, "total_time_sec": 20.0},
            {"tests": 7, "errors": 3, "coverage": 0.7, "total_time_sec": 5.0},
        ],
    )

    result = compute_metrics(filepath)

    assert result.total_tests == 15
    assert result.total_errors == 4
    assert result.total_time_sec == pytest.approx(35.0)


def test_compute_metrics_mean_coverage(tmp_path):
    filepath = write_metrics_csv(
        tmp_path,
        [
            {"tests": 1, "errors": 0, "coverage": 0.2, "total_time_sec": 1.0},
            {"tests": 1, "errors": 0, "coverage": 0.4, "total_time_sec": 1.0},
            {"tests": 1, "errors": 0, "coverage": 0.9, "total_time_sec": 1.0},
        ],
    )

    result = compute_metrics(filepath)

    assert result.mean_coverage == pytest.approx(0.5)


def test_compute_metrics_median_differs_from_mean(tmp_path):
    filepath = write_metrics_csv(
        tmp_path,
        [
            {"tests": 1, "errors": 0, "coverage": 0.1, "total_time_sec": 1.0},
            {"tests": 1, "errors": 0, "coverage": 0.2, "total_time_sec": 1.0},
            {"tests": 1, "errors": 0, "coverage": 0.9, "total_time_sec": 1.0},
        ],
    )

    result = compute_metrics(filepath)

    assert result.median_coverage == pytest.approx(0.2)
    assert result.mean_coverage == pytest.approx(0.4)


@pytest.mark.parametrize(
    "rows, expected_total_tests, expected_total_errors, expected_total_time",
    [
        (
            [{"tests": 1, "errors": 0, "coverage": 1.0, "total_time_sec": 5.0}],
            1,
            0,
            5.0,
        ),
        (
            [
                {"tests": 10, "errors": 5, "coverage": 0.5, "total_time_sec": 100.0},
                {"tests": 20, "errors": 3, "coverage": 0.8, "total_time_sec": 50.0},
            ],
            30,
            8,
            150.0,
        ),
        (
            [
                {"tests": 0, "errors": 0, "coverage": 0.0, "total_time_sec": 0.0},
                {"tests": 0, "errors": 0, "coverage": 0.0, "total_time_sec": 0.0},
            ],
            0,
            0,
            0.0,
        ),
    ],
)
def test_compute_metrics_parametrized(
    tmp_path, rows, expected_total_tests, expected_total_errors, expected_total_time
):
    filepath = write_metrics_csv(tmp_path, rows)

    result = compute_metrics(filepath)

    assert result.total_tests == expected_total_tests
    assert result.total_errors == expected_total_errors
    assert result.total_time_sec == pytest.approx(expected_total_time)


def test_compute_metrics_accepts_path_object(tmp_path):
    filepath = tmp_path / "metrics.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow(
            {"tests": 1, "errors": 0, "coverage": 1.0, "total_time_sec": 1.0}
        )

    result = compute_metrics(filepath)

    assert result.total_tests == 1


def test_compute_metrics_counts_methods_with_results(tmp_path):
    filepath = write_metrics_csv(
        tmp_path,
        [
            {"tests": 1, "errors": 0, "coverage": 0.1, "total_time_sec": 1.0},
            {"tests": 2, "errors": 0, "coverage": 0.2, "total_time_sec": 1.0},
            {"tests": 3, "errors": 0, "coverage": 0.3, "total_time_sec": 1.0},
        ],
    )

    result = compute_metrics(filepath)

    assert result.methods_with_results == 3


def test_combine_metrics_aggregates_across_files(tmp_path):
    csharp_dir = tmp_path / "csharp"
    csharp_dir.mkdir()
    java_dir = tmp_path / "java"
    java_dir.mkdir()

    file1 = write_metrics_csv(
        csharp_dir,
        [
            {"tests": 5, "errors": 1, "coverage": 0.5, "total_time_sec": 10.0},
            {"tests": 3, "errors": 0, "coverage": 0.7, "total_time_sec": 20.0},
        ],
    )
    file2 = write_metrics_csv(
        java_dir,
        [
            {"tests": 4, "errors": 2, "coverage": 0.9, "total_time_sec": 15.0},
        ],
    )

    combined = combine_metrics([file1, file2])

    assert combined.total_tests == 12
    assert combined.total_errors == 3
    assert combined.total_time_sec == pytest.approx(45.0)
    assert combined.methods_with_results == 3
    assert combined.mean_coverage == pytest.approx(0.7)
    assert combined.median_coverage == pytest.approx(0.7)


def test_combine_metrics_single_file_equals_compute_metrics(tmp_path):
    filepath = write_metrics_csv(
        tmp_path,
        [
            {"tests": 5, "errors": 1, "coverage": 0.5, "total_time_sec": 10.0},
            {"tests": 3, "errors": 0, "coverage": 0.9, "total_time_sec": 20.0},
        ],
    )

    assert combine_metrics([filepath]) == compute_metrics(filepath)


def test_merge_csvs_preserves_header_and_rows(tmp_path):
    src1 = tmp_path / "src1"
    src1.mkdir()
    src2 = tmp_path / "src2"
    src2.mkdir()

    file1 = write_metrics_csv(
        src1,
        [{"tests": 1, "errors": 0, "coverage": 0.5, "total_time_sec": 1.0}],
    )
    file2 = write_metrics_csv(
        src2,
        [
            {"tests": 2, "errors": 1, "coverage": 0.6, "total_time_sec": 2.0},
            {"tests": 3, "errors": 0, "coverage": 0.7, "total_time_sec": 3.0},
        ],
    )

    dest = tmp_path / "merged.csv"
    merge_csvs([file1, file2], dest)

    with open(dest, newline="") as f:
        reader = csv.DictReader(f)
        assert list(reader.fieldnames or []) == FIELDNAMES
        rows = list(reader)

    assert len(rows) == 3
    assert rows[0]["tests"] == "1"
    assert rows[1]["tests"] == "2"
    assert rows[2]["tests"] == "3"


def test_merge_csvs_then_compute_matches_combine(tmp_path):
    csharp_dir = tmp_path / "csharp"
    csharp_dir.mkdir()
    java_dir = tmp_path / "java"
    java_dir.mkdir()

    file1 = write_metrics_csv(
        csharp_dir,
        [{"tests": 5, "errors": 1, "coverage": 0.5, "total_time_sec": 10.0}],
    )
    file2 = write_metrics_csv(
        java_dir,
        [{"tests": 4, "errors": 2, "coverage": 0.9, "total_time_sec": 15.0}],
    )
    dest = tmp_path / "merged.csv"

    merge_csvs([file1, file2], dest)

    assert compute_metrics(dest) == combine_metrics([file1, file2])
