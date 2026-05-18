import subprocess
import sys
from pathlib import Path


SCRIPTS = [
    "init_db.py",
    "init_soc_db.py",
    "init_serviceops_db.py",
    "init_projectops_db.py",
]


def run_script(script_name: str) -> None:
    script_path = Path(__file__).parent / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Missing seed script: {script_name}")

    print(f"\n== Running {script_name} ==")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=Path(__file__).parent,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"{script_name} failed with exit code {result.returncode}")

    print(f"== Completed {script_name} ==")


def main() -> None:
    print("ENYRAX DB seed started")

    for script in SCRIPTS:
        run_script(script)

    print("\nENYRAX DB seed completed successfully")


if __name__ == "__main__":
    main()
