import subprocess
import os


def run_compstrat():
    ai_artifacts = os.path.abspath("results/artifacts_run_ai/AI.csv")
    baseline_artifacts = os.path.abspath("results/artifacts_run_baseline/ExecutionTreeContributedCoverage.csv")
    compstrat_results = os.path.abspath("results/compstrat_results")

    cmd = [
        "docker", "run", "--rm",

        "-v", f"{ai_artifacts}:/workspace/PySymGym/tools/compstrat/strat/ai_strat",
        "-v", f"{baseline_artifacts}:/workspace/PySymGym/tools/compstrat/strat/baseline_strat",
        "-v", f"{compstrat_results}:/workspace/PySymGym/tools/compstrat/results",

        "pysymgym-test",
        "compstrat/compstrat.py",

        "-s1", "BASELINE",
        "-r1", "/workspace/PySymGym/tools/compstrat/strat/baseline_strat",
        "-s2", "AI",
        "-r2", "/workspace/PySymGym/tools/compstrat/strat/ai_strat",
        "-cp", "/workspace/PySymGym/tools/compstrat/resources/compare_confs.yaml",
        "--savedir", "/workspace/PySymGym/tools/compstrat/results"
    ]

    subprocess.run(cmd, check=True)
