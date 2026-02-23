import os
import subprocess
from abc import ABC, abstractmethod


class DockerRunner(ABC):
    IMAGE = "pysymgym-test"

    def run(self) -> None:
        cmd = self._docker_cmd() + self._tool_cmd()
        subprocess.run(cmd, check=True)

    def _docker_cmd(self) -> list[str]:
        return [
            "docker",
            "run",
            "--rm",
            *self._volumes(),
            self.IMAGE,
        ]

    @abstractmethod
    def _volumes(self) -> list[str]:
        """Docker volume mappings"""

    @abstractmethod
    def _tool_cmd(self) -> list[str]:
        """Command executed inside container"""

    @staticmethod
    def _get_path(path: str) -> str:
        return os.path.abspath("backend/" + path)


class RunstratBaseline(DockerRunner):
    def _volumes(self) -> list[str]:
        return [
            "-v",
            f"{self._get_path('results')}:/workspace/PySymGym/tools/runstrat/results",
            "-v",
            f"{self._get_path('uploads/launch_info.csv')}"
            ":/workspace/PySymGym/tools/runstrat/launch_info.csv",
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
            "runstrat/launch_info.csv",
        ]


class RunstratAI(DockerRunner):
    def _volumes(self) -> list[str]:
        return [
            "-v",
            f"{self._get_path('results')}:/workspace/PySymGym/tools/runstrat/results",
            "-v",
            f"{self._get_path('uploads/launch_info.csv')}"
            ":/workspace/PySymGym/tools/runstrat/launch_info.csv",
            "-v",
            f"{self._get_path('uploads/model.onnx')}"
            ":/workspace/PySymGym/tools/runstrat/resources/model.onnx",
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
            "runstrat/launch_info.csv",
        ]


class Compstrat(DockerRunner):
    def _volumes(self) -> list[str]:
        return [
            "-v",
            f"{self._get_path('results/artifacts_run_ai/AI.csv')}"
            ":/workspace/PySymGym/tools/compstrat/strat/ai_strat",
            "-v",
            f"{self._get_path('results/artifacts_run_baseline/ExecutionTreeContributedCoverage.csv')}"
            ":/workspace/PySymGym/tools/compstrat/strat/baseline_strat",
            "-v",
            f"{self._get_path('results/compstrat_results')}"
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


def run_pipeline() -> None:
    RunstratBaseline().run()
    RunstratAI().run()
    Compstrat().run()
