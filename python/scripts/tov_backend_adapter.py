"""Backend adapter for a real compact-object/TOV solver.

This module mirrors the BBN backend contract: it writes a normalized request,
invokes an external executable, and parses a normalized output payload. The
workspace does not vendor any TOV solver, so this adapter stays generic and can
be pointed at a local installation when available.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class TOVPhysicsRequest:
    epsilon_best: float
    delta_em: float
    g_eff_ns_target: float
    f_temps_ns_target: float
    config_compact: dict[str, float] | None = None


@dataclass(frozen=True)
class TOVPhysicsResult:
    M_max: float
    R_1_4: float
    z_ns: float
    E_jet_boost: float
    backend: str
    executable_path: str
    input_dir: str
    output_dir: str
    log_path: str | None = None
    raw_output_path: str | None = None


class TOVBackendAdapter(ABC):
    backend_name: str

    def __init__(self, executable_path: str | Path, work_dir: str | Path | None = None) -> None:
        self.executable_path = Path(executable_path)
        self.work_dir = Path(work_dir) if work_dir is not None else Path.cwd()

    def ensure_executable(self) -> None:
        if not self.executable_path.exists() and shutil.which(str(self.executable_path)) is None:
            raise FileNotFoundError(f"TOV executable not found: {self.executable_path}")

    def create_io_directories(self) -> tuple[Path, Path]:
        input_dir = self.work_dir / f"{self.backend_name}_input"
        output_dir = self.work_dir / f"{self.backend_name}_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        return input_dir, output_dir

    def write_inputs(self, request: TOVPhysicsRequest, input_dir: Path) -> None:
        payload = {
            "request": asdict(request),
            "backend": self.backend_name,
        }
        (input_dir / "request.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self.write_backend_inputs(request, input_dir)

    @abstractmethod
    def write_backend_inputs(self, request: TOVPhysicsRequest, input_dir: Path) -> None:
        pass

    @abstractmethod
    def command(self, input_dir: Path, output_dir: Path) -> list[str]:
        pass

    @abstractmethod
    def parse_outputs(self, output_dir: Path) -> TOVPhysicsResult:
        pass

    def run(self, request: TOVPhysicsRequest) -> TOVPhysicsResult:
        self.ensure_executable()
        input_dir, output_dir = self.create_io_directories()
        self.write_inputs(request, input_dir)

        completed = subprocess.run(
            self.command(input_dir, output_dir),
            cwd=str(self.work_dir),
            capture_output=True,
            text=True,
            check=False,
        )

        log_path = output_dir / f"{self.backend_name}.log"
        log_path.write_text(
            "\n".join(
                [
                    f"backend: {self.backend_name}",
                    f"executable: {self.executable_path}",
                    f"returncode: {completed.returncode}",
                    "--- stdout ---",
                    completed.stdout,
                    "--- stderr ---",
                    completed.stderr,
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        if completed.returncode != 0:
            raise RuntimeError(f"{self.backend_name} run failed with return code {completed.returncode}; see {log_path}")

        result = self.parse_outputs(output_dir)
        return TOVPhysicsResult(
            M_max=result.M_max,
            R_1_4=result.R_1_4,
            z_ns=result.z_ns,
            E_jet_boost=result.E_jet_boost,
            backend=self.backend_name,
            executable_path=str(self.executable_path),
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            log_path=str(log_path),
            raw_output_path=result.raw_output_path,
        )


class GenericTOVBackendAdapter(TOVBackendAdapter):
    backend_name = "tov"

    def write_backend_inputs(self, request: TOVPhysicsRequest, input_dir: Path) -> None:
        driver_file = input_dir / "tov_driver.json"
        driver_file.write_text(
            json.dumps(
                {
                    "epsilon_best": request.epsilon_best,
                    "delta_em": request.delta_em,
                    "g_eff_ns_target": request.g_eff_ns_target,
                    "f_temps_ns_target": request.f_temps_ns_target,
                    "config_compact": request.config_compact or {},
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    def command(self, input_dir: Path, output_dir: Path) -> list[str]:
        return [str(self.executable_path), str(input_dir), str(output_dir)]

    def parse_outputs(self, output_dir: Path) -> TOVPhysicsResult:
        candidates = [output_dir / "tov_results.json", output_dir / "results.json", output_dir / "tov_results.dat"]
        for candidate in candidates:
            if not candidate.exists():
                continue
            if candidate.suffix == ".json":
                payload = json.loads(candidate.read_text(encoding="utf-8"))
            else:
                payload = self._read_key_value_file(candidate)
            return TOVPhysicsResult(
                M_max=float(payload.get("M_max", payload.get("Mmax", "nan"))),
                R_1_4=float(payload.get("R_1_4", payload.get("R14", "nan"))),
                z_ns=float(payload.get("z_ns", payload.get("zNS", "nan"))),
                E_jet_boost=float(payload.get("E_jet_boost", payload.get("Ejet_boost", "nan"))),
                backend=self.backend_name,
                executable_path=str(self.executable_path),
                input_dir=str(output_dir.parent / f"{self.backend_name}_input"),
                output_dir=str(output_dir),
                raw_output_path=str(candidate),
            )
        raise FileNotFoundError(f"missing TOV output file in {output_dir}")

    @staticmethod
    def _read_key_value_file(path: Path) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
        return values


def create_tov_backend(executable_path: str | Path, work_dir: str | Path | None = None) -> TOVBackendAdapter:
    return GenericTOVBackendAdapter(executable_path=executable_path, work_dir=work_dir)


def tov_backend_is_available(executable_path: str | Path) -> bool:
    path = Path(executable_path)
    if path.exists():
        return True
    return shutil.which(str(executable_path)) is not None