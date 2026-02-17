import subprocess
import os


def run_runstrat():
    host_artifacts = os.path.abspath("results")
    host_launch_info = os.path.abspath("launch_info.csv")

    cmd = [
        "docker", "run", "--rm",

        "-v", f"{host_artifacts}:/workspace/PySymGym/tools/runstrat/results",
        "-v", f"{host_launch_info}:/workspace/PySymGym/tools/runstrat/launch_info.csv",

        "pysymgym-test",

        "-s", "ExecutionTreeContributedCoverage",
        "-t", "120",
        "-ps", "/workspace/PySymGym",
        "-sd", "results/artifacts_run",
        "-as",
        "/workspace/PySymGym/maps/DotNet/Maps/Root/bin/Release/net7.0",
        "/workspace/PySymGym/tools/runstrat/launch_info.csv"

    ]

    subprocess.run(cmd, check=True)


run_runstrat()
