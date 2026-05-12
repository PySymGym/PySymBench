import logging
from dataclasses import dataclass

from backend.db.database import SessionLocal
from backend.db.models import Experiment
from backend.file_utils.runstrat_metrics import RunstratMetrics

logger = logging.getLogger(__name__)


@dataclass
class ExperimentRecord:
    id: int
    experiment_name: str
    model_name: str
    email: str
    total_tests: int
    total_errors: int
    mean_coverage: float
    median_coverage: float
    total_time_sec: float
    methods_launched: int | None
    methods_with_results: int | None
    language: str | None
    is_baseline: bool
    model_object_key: str | None
    results_object_key: str | None
    created_at: str


def save_experiment(
    experiment_name: str,
    model_name: str,
    email: str,
    metrics: RunstratMetrics,
    methods_launched: int | None = None,
    language: str | None = None,
    is_baseline: bool = False,
    model_object_key: str | None = None,
    results_object_key: str | None = None,
) -> int:
    with SessionLocal() as session:
        record = Experiment(
            experiment_name=experiment_name,
            model_name=model_name,
            email=email,
            total_tests=metrics.total_tests,
            total_errors=metrics.total_errors,
            mean_coverage=metrics.mean_coverage,
            median_coverage=metrics.median_coverage,
            total_time_sec=metrics.total_time_sec,
            methods_launched=methods_launched,
            methods_with_results=metrics.methods_with_results,
            language=language,
            is_baseline=is_baseline,
            model_object_key=model_object_key,
            results_object_key=results_object_key,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        logger.info("Saved experiment %d: %s", record.id, experiment_name)
        return record.id


def _to_record(r: Experiment) -> ExperimentRecord:
    return ExperimentRecord(
        id=r.id,
        experiment_name=r.experiment_name,
        model_name=r.model_name,
        email=r.email,
        total_tests=r.total_tests,
        total_errors=r.total_errors,
        mean_coverage=r.mean_coverage,
        median_coverage=r.median_coverage,
        total_time_sec=r.total_time_sec,
        methods_launched=r.methods_launched,
        methods_with_results=r.methods_with_results,
        language=r.language,
        is_baseline=r.is_baseline,
        model_object_key=r.model_object_key,
        results_object_key=r.results_object_key,
        created_at=r.created_at.isoformat(),
    )


_DEFAULT_ORDER = [
    Experiment.mean_coverage.desc(),
    Experiment.total_tests.desc(),
    Experiment.total_errors.desc(),
    Experiment.created_at.desc(),
    Experiment.total_time_sec.asc(),
]


def get_all_experiments() -> list[ExperimentRecord]:
    with SessionLocal() as session:
        rows = session.query(Experiment).order_by(*_DEFAULT_ORDER).all()
        return [_to_record(r) for r in rows]


def get_experiments_by_language(language: str) -> list[ExperimentRecord]:
    with SessionLocal() as session:
        rows = (
            session.query(Experiment)
            .filter(Experiment.language == language)
            .order_by(*_DEFAULT_ORDER)
            .all()
        )
        return [_to_record(r) for r in rows]


def get_aggregated_all_experiments() -> list[ExperimentRecord]:
    """Return pre-computed aggregated records saved with language='all'."""
    return get_experiments_by_language("all")
