import subprocess
from abc import ABC, abstractmethod

from backend.config.paths import (
    ARTIFACTS_AI2_CSV_FILE,
    ARTIFACTS_AI_CSV_FILE,
    ARTIFACTS_BASELINE_CSV_FILE,
    COMPSTRAT_RESULTS_DIR,
    LAUNCH_INFO_FILE,
    MODEL2_ONNX_FILE,
    MODEL_ONNX_FILE,
    RESULTS_DIR,
    get_thread_filepath,
)
from backend.launch_service.app_setup import IMAGE_NAME


class DockerRunner(ABC):
    WORKSPACE = "/workspace/PySymGym"
    RUNSTRAT_RESULTS = f"{WORKSPACE}/tools/runstrat/results"
    RUNSTRAT_RESOURCES = f"{WORKSPACE}/tools/runstrat/resources"
    COMPSTRAT_STRAT = f"{WORKSPACE}/tools/compstrat/strat"
    COMPSTRAT_RESULTS = f"{WORKSPACE}/tools/compstrat/results"
    COMPSTRAT_RESOURCES = f"{WORKSPACE}/tools/compstrat/resources"
    MAPS_PATH = f"{WORKSPACE}/maps/DotNet/Maps/Root/bin/Release/net8.0"

    TIMEOUT = "120"

    def run(self, uid) -> None:
        cmd = self._docker_cmd(uid) + self._tool_cmd()
        subprocess.run(cmd, check=True, capture_output=True)

    def _docker_cmd(self, uid) -> list[str]:
        return [
            "docker",
            "run",
            "--rm",
            "--name",
            f"pysymbench-{uid}",
            *self._volumes(uid),
            IMAGE_NAME,
        ]

    @abstractmethod
    def _volumes(self, uid) -> list[str]:
        """Docker volume mappings"""

    @abstractmethod
    def _tool_cmd(self) -> list[str]:
        """Command executed inside container"""


class RunstratBaseline(DockerRunner):
    def _volumes(self, uid) -> list[str]:
        return [
            "-v",
            f"{get_thread_filepath(uid, RESULTS_DIR)}:{self.RUNSTRAT_RESULTS}",
            "-v",
            f"{get_thread_filepath(uid, LAUNCH_INFO_FILE)}:{self.RUNSTRAT_RESOURCES}/launch_info.csv",
        ]

    def _tool_cmd(self) -> list[str]:
        return [
            "runstrat/runstrat.py",
            "-s",
            "ExecutionTreeContributedCoverage",
            "-t",
            self.TIMEOUT,
            "-ps",
            self.WORKSPACE,
            "-sd",
            f"{self.RUNSTRAT_RESULTS}/artifacts_run_baseline",
            "-as",
            self.MAPS_PATH,
            f"{self.RUNSTRAT_RESOURCES}/launch_info.csv",
        ]


class RunstratAI(DockerRunner):
    def _volumes(self, uid) -> list[str]:
        return [
            "-v",
            f"{get_thread_filepath(uid, RESULTS_DIR)}:{self.RUNSTRAT_RESULTS}",
            "-v",
            f"{get_thread_filepath(uid, LAUNCH_INFO_FILE)}:{self.RUNSTRAT_RESOURCES}/launch_info.csv",
            "-v",
            f"{get_thread_filepath(uid, MODEL_ONNX_FILE)}:{self.RUNSTRAT_RESOURCES}/model.onnx",
        ]

    def _tool_cmd(self) -> list[str]:
        return [
            "runstrat/runstrat.py",
            "-s",
            "AI",
            "-mp",
            f"{self.RUNSTRAT_RESOURCES}/model.onnx",
            "-t",
            self.TIMEOUT,
            "-ps",
            self.WORKSPACE,
            "-sd",
            f"{self.RUNSTRAT_RESULTS}/artifacts_run_ai",
            "-as",
            self.MAPS_PATH,
            f"{self.RUNSTRAT_RESOURCES}/launch_info.csv",
        ]


class RunstratAI2(DockerRunner):
    """Runs the AI strategy with the second model (model2.onnx), outputs to artifacts_run_ai2/."""

    def _volumes(self, uid) -> list[str]:
        return [
            "-v",
            f"{get_thread_filepath(uid, RESULTS_DIR)}:{self.RUNSTRAT_RESULTS}",
            "-v",
            f"{get_thread_filepath(uid, LAUNCH_INFO_FILE)}:{self.RUNSTRAT_RESOURCES}/launch_info.csv",
            "-v",
            f"{get_thread_filepath(uid, MODEL2_ONNX_FILE)}:{self.RUNSTRAT_RESOURCES}/model2.onnx",
        ]

    def _tool_cmd(self) -> list[str]:
        return [
            "runstrat/runstrat.py",
            "-s",
            "AI",
            "-mp",
            f"{self.RUNSTRAT_RESOURCES}/model2.onnx",
            "-t",
            self.TIMEOUT,
            "-ps",
            self.WORKSPACE,
            "-sd",
            f"{self.RUNSTRAT_RESULTS}/artifacts_run_ai2",
            "-as",
            self.MAPS_PATH,
            f"{self.RUNSTRAT_RESOURCES}/launch_info.csv",
        ]


class Compstrat(DockerRunner):
    def __init__(self, s1: str, csv_path1: str, s2: str, csv_path2: str) -> None:
        self.s1 = s1
        self.csv_path1 = csv_path1
        self.s2 = s2
        self.csv_path2 = csv_path2

    def _volumes(self, uid) -> list[str]:
        return [
            "-v",
            f"{get_thread_filepath(uid, self.csv_path1)}:{self.COMPSTRAT_STRAT}/strat1",
            "-v",
            f"{get_thread_filepath(uid, self.csv_path2)}:{self.COMPSTRAT_STRAT}/strat2",
            "-v",
            f"{get_thread_filepath(uid, COMPSTRAT_RESULTS_DIR)}:{self.COMPSTRAT_RESULTS}",
        ]

    def _tool_cmd(self) -> list[str]:
        return [
            "compstrat/compstrat.py",
            "-s1",
            self.s1,
            "-r1",
            f"{self.COMPSTRAT_STRAT}/strat1",
            "-s2",
            self.s2,
            "-r2",
            f"{self.COMPSTRAT_STRAT}/strat2",
            "-cp",
            f"{self.COMPSTRAT_RESOURCES}/compare_confs.yaml",
            "--savedir",
            self.COMPSTRAT_RESULTS,
        ]


def run_pipeline(uid) -> None:
    RunstratBaseline().run(uid)
    RunstratAI().run(uid)
    Compstrat("BASELINE", ARTIFACTS_BASELINE_CSV_FILE, "AI", ARTIFACTS_AI_CSV_FILE).run(
        uid
    )


def run_model_vs_model_pipeline(uid) -> None:
    RunstratAI().run(uid)
    RunstratAI2().run(uid)
    Compstrat("MODEL1", ARTIFACTS_AI_CSV_FILE, "MODEL2", ARTIFACTS_AI2_CSV_FILE).run(
        uid
    )


def run_publish_pipeline(uid) -> None:
    RunstratAI().run(uid)
