#!/usr/bin/env python
"""Execute every notebook in order and write the analysis figures and tables.

Each notebook is run in place, so the committed copies keep their outputs. Any
cell that raises -- including assertions that validate the results carried into
the manuscript -- stops the run and reports which notebook failed.

    python run_all.py              # run all seven notebooks
    python run_all.py 03 04        # run only the notebooks whose names start 03, 04
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTEBOOKS = [
    "00_build_datasets.ipynb",
    "01_light_environment.ipynb",
    "02_leaf_gas_exchange.ipynb",
    "03_growth_rhythmicity_ml.ipynb",
    "04_sexual_dimorphism.ipynb",
    "05_branch_architecture.ipynb",
    "06_growth_physiology.ipynb",
]


def run(name):
    print(f"\n=== {name} ===", flush=True)
    started = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook",
         "--execute", "--inplace", "--ExecutePreprocessor.timeout=3600", name],
        cwd=ROOT / "notebooks", capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout[-4000:])
        print(result.stderr[-4000:], file=sys.stderr)
        return False
    print(f"    ok ({time.time() - started:.0f} s)", flush=True)
    return True


def main():
    wanted = sys.argv[1:]
    selected = [n for n in NOTEBOOKS
                if not wanted or any(n.startswith(w) for w in wanted)]
    if not selected:
        print(f"no notebook matches {wanted}", file=sys.stderr)
        return 1

    # Notebook 00 writes the datasets the others read, so it must lead.
    if wanted and selected[0] != NOTEBOOKS[0] and not (ROOT / "data/processed/unified_growth_dataset.csv").exists():
        print("data/processed is empty -- run 00_build_datasets first", file=sys.stderr)
        return 1

    failed = [n for n in selected if not run(n)]
    if failed:
        print(f"\nFAILED: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"\nAll {len(selected)} notebooks executed. "
          f"Figures in results/figures, tables in results/tables.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
