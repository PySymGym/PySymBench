import subprocess


def run_runstrat():
    cmd = [
        "docker", "run", "--rm",
        "pysymgym-test",

        "-s", "ExecutionTreeContributedCoverage",
        "-t", "120",
        "-ps", "/workspace/PySymGym",
        "-sd", "artifacts_run",
        "-as",
        "/workspace/PySymGym/tools/runstrat/resources/ForTests/bin/Release/net7.0",
        "/workspace/PySymGym/tools/runstrat/resources/for_tests.csv"
    ]

    subprocess.run(cmd, check=True)


run_runstrat()
