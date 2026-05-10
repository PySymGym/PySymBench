from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    total_tests: Mapped[int] = mapped_column(Integer, nullable=False)
    total_errors: Mapped[int] = mapped_column(Integer, nullable=False)
    mean_coverage: Mapped[float] = mapped_column(Float, nullable=False)
    median_coverage: Mapped[float] = mapped_column(Float, nullable=False)
    total_time_sec: Mapped[float] = mapped_column(Float, nullable=False)
    model_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    results_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
