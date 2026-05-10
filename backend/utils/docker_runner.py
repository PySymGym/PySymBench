import subprocess
from abc import ABC, abstractmethod

from backend.config.paths import (
    ARTIFACTS_AI_CSV_FILE,
    ARTIFACTS_BASELINE_CSV_FILE,
    COMPSTRAT_RESULTS_DIR,
    LAUNCH_INFO_FILE,
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


class Compstrat(DockerRunner):
    def _volumes(self, uid) -> list[str]:
        return [
            "-v",
            f"{get_thread_filepath(uid, ARTIFACTS_AI_CSV_FILE)}:{self.COMPSTRAT_STRAT}/ai_strat",
            "-v",
            f"{get_thread_filepath(uid, ARTIFACTS_BASELINE_CSV_FILE)}:{self.COMPSTRAT_STRAT}/baseline_strat",
            "-v",
            f"{get_thread_filepath(uid, COMPSTRAT_RESULTS_DIR)}:{self.COMPSTRAT_RESULTS}",
        ]

    def _tool_cmd(self) -> list[str]:
        return [
            "compstrat/compstrat.py",
            "-s1",
            "BASELINE",
            "-r1",
            f"{self.COMPSTRAT_STRAT}/baseline_strat",
            "-s2",
            "AI",
            "-r2",
            f"{self.COMPSTRAT_STRAT}/ai_strat",
            "-cp",
            f"{self.COMPSTRAT_RESOURCES}/compare_confs.yaml",
            "--savedir",
            self.COMPSTRAT_RESULTS,
        ]


def run_pipeline(uid) -> None:
    RunstratBaseline().run(uid)
    RunstratAI().run(uid)
    Compstrat().run(uid)


def run_publish_pipeline(uid) -> None:
    RunstratAI().run(uid)
