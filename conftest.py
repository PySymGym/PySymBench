import os


def pytest_configure(config):
    os.environ.setdefault("DB_URL", "sqlite://")
