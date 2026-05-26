"""Shared helpers for the regime pytest launchers."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REGIME_MARKERS = {
    "atomique": "atomique",
    "metal": "metal",
    "lanthanide": "lanthanide",
    "dense": "dense",
    "flow": "flow",
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def pytest_executable(root: Path | None = None) -> Path:
    base = root or workspace_root()
    return base / ".venv" / "Scripts" / "pytest.exe"


def build_pytest_command(marker: str | None = None) -> list[str]:
    root = workspace_root()
    command = [str(pytest_executable(root)), "-q"]
    if marker is not None:
        command.extend(["-m", marker])
    command.append(str(root / "python" / "tests"))
    return command


def run_pytest(marker: str | None = None) -> None:
    command = build_pytest_command(marker)
    print(f"Running: {' '.join(command)}")
    subprocess.run(command, check=True)


def run_marker(marker: str) -> None:
    if marker not in REGIME_MARKERS:
        raise ValueError(f"Unsupported regime marker: {marker}")
    run_pytest(REGIME_MARKERS[marker])
