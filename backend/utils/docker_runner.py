import subprocess
from abc import ABC, abstractmethod

from backend.config.paths import (
    get_process_filepath,
    RESULTS_DIR,
    LAUNCH_INFO_FILE,
    MODEL_ONNX_FILE,
    ARTIFACTS_AI_CSV_FILE,
    ARTIFACTS_BASELINE_CSV_FILE,
    COMPSTRAT_RESULTS_DIR,
)
from docker.build_container import IMAGE_NAME


class DockerRunner(ABC):
    def run(self, uid) -> None:
        cmd = self._docker_cmd(uid) + self._tool_cmd()
        subprocess.run(cmd, check=True)

    def _docker_cmd(self, uid) -> list[str]:
        return [
            "docker",
            "run",
            "--rm",
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
            f"{get_process_filepath(uid, RESULTS_DIR)}:/workspace/PySymGym/tools/runstrat/results",
            "-v",
            f"{get_process_filepath(uid, LAUNCH_INFO_FILE)}"
            f":/workspace/PySymGym/tools/runstrat/resources/launch_info.csv",
        ]

    def _tool_cmd(self) -> list[str]:
        return [
            "runstrat/runstrat.py",
            "-s",
            "ExecutionTreeContributedCoverage",
            "-t",
            "120",
            "-ps",
            "/workspace/PySymGym",
            "-sd",
            "runstrat/results/artifacts_run_baseline",
            "-as",
            "/workspace/PySymGym/maps/DotNet/Maps/Root/bin/Release/net8.0",
            "runstrat/resources/launch_info.csv",
        ]


class RunstratAI(DockerRunner):
    def _volumes(self, uid) -> list[str]:
        return [
            "-v",
            f"{get_process_filepath(uid, RESULTS_DIR)}:/workspace/PySymGym/tools/runstrat/results",
            "-v",
            f"{get_process_filepath(uid, LAUNCH_INFO_FILE)}"
            f":/workspace/PySymGym/tools/runstrat/resources/launch_info.csv",
            "-v",
            f"{get_process_filepath(uid, MODEL_ONNX_FILE)}"
            f":/workspace/PySymGym/tools/runstrat/resources/model.onnx",
        ]

    def _tool_cmd(self) -> list[str]:
        return [
            "runstrat/runstrat.py",
            "-s",
            "AI",
            "-mp",
            "/workspace/PySymGym/tools/runstrat/resources/model.onnx",
            "-t",
            "120",
            "-ps",
            "/workspace/PySymGym",
            "-sd",
            "runstrat/results/artifacts_run_ai",
            "-as",
            "/workspace/PySymGym/maps/DotNet/Maps/Root/bin/Release/net8.0",
            "runstrat/resources/launch_info.csv",
        ]


class Compstrat(DockerRunner):
    def _volumes(self, uid) -> list[str]:
        return [
            "-v",
            f"{get_process_filepath(uid, ARTIFACTS_AI_CSV_FILE)}"
            ":/workspace/PySymGym/tools/compstrat/strat/ai_strat",
            "-v",
            f"{get_process_filepath(uid, ARTIFACTS_BASELINE_CSV_FILE)}"
            ":/workspace/PySymGym/tools/compstrat/strat/baseline_strat",
            "-v",
            f"{get_process_filepath(uid, COMPSTRAT_RESULTS_DIR)}"
            ":/workspace/PySymGym/tools/compstrat/results",
        ]

    def _tool_cmd(self) -> list[str]:
        return [
            "compstrat/compstrat.py",
            "-s1",
            "BASELINE",
            "-r1",
            "/workspace/PySymGym/tools/compstrat/strat/baseline_strat",
            "-s2",
            "AI",
            "-r2",
            "/workspace/PySymGym/tools/compstrat/strat/ai_strat",
            "-cp",
            "/workspace/PySymGym/tools/compstrat/resources/compare_confs.yaml",
            "--savedir",
            "/workspace/PySymGym/tools/compstrat/results",
        ]


def run_pipeline(uid) -> None:
    RunstratBaseline().run(uid)
    RunstratAI().run(uid)
    Compstrat().run(uid)
