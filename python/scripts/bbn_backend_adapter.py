"""Backend adapters for a real BBN code.

This module defines a stable contract for connecting the V77L/V77M wrappers to
an external BBN executable. It does not vendor AlterBBN or PArthENoPE; it only
provides a concrete adapter skeleton that can write inputs, run a backend, and
parse outputs once a local installation is available.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BBNPhysicsRequest:
    beta_e_phys: float
    gamma_exch_phys: float
    gamma_drain_phys: float
    config_cosmo: dict[str, float] | None = None


@dataclass(frozen=True)
class BBNPhysicsResult:
    D_over_H: float
    Y_p: float
    Li7_over_H: float
    Be7_over_H: float
    Li_total_over_H: float
    backend: str
    executable_path: str
    input_dir: str
    output_dir: str
    log_path: str | None = None
    raw_output_path: str | None = None


class BBNBackendAdapter(ABC):
    """Common contract for a BBN backend."""

    backend_name: str

    def __init__(self, executable_path: str | Path, work_dir: str | Path | None = None) -> None:
        self.executable_path = Path(executable_path)
        self.work_dir = Path(work_dir) if work_dir is not None else Path.cwd()

    def ensure_executable(self) -> None:
        if not self.executable_path.exists():
            raise FileNotFoundError(f"BBN executable not found: {self.executable_path}")

    def create_io_directories(self) -> tuple[Path, Path]:
        input_dir = self.work_dir / f"{self.backend_name}_input"
        output_dir = self.work_dir / f"{self.backend_name}_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        return input_dir, output_dir

    def write_inputs(self, request: BBNPhysicsRequest, input_dir: Path) -> None:
        payload = {
            "request": asdict(request),
            "backend": self.backend_name,
        }
        (input_dir / "request.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self.write_backend_inputs(request, input_dir)

    @abstractmethod
    def write_backend_inputs(self, request: BBNPhysicsRequest, input_dir: Path) -> None:
        """Write the backend-specific input files."""

    @abstractmethod
    def command(self, input_dir: Path, output_dir: Path) -> list[str]:
        """Return the command used to execute the backend."""

    @abstractmethod
    def parse_outputs(self, output_dir: Path) -> BBNPhysicsResult:
        """Parse backend outputs into a normalized result object."""

    def run(self, request: BBNPhysicsRequest) -> BBNPhysicsResult:
        self.ensure_executable()
        input_dir, output_dir = self.create_io_directories()
        self.write_inputs(request, input_dir)

        command = self.command(input_dir, output_dir)
        completed = subprocess.run(
            command,
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
            raise RuntimeError(
                f"{self.backend_name} run failed with return code {completed.returncode}; see {log_path}"
            )

        result = self.parse_outputs(output_dir)
        return BBNPhysicsResult(
            D_over_H=result.D_over_H,
            Y_p=result.Y_p,
            Li7_over_H=result.Li7_over_H,
            Be7_over_H=result.Be7_over_H,
            Li_total_over_H=result.Li_total_over_H,
            backend=self.backend_name,
            executable_path=str(self.executable_path),
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            log_path=str(log_path),
            raw_output_path=result.raw_output_path,
        )


class AlterBBNBackendAdapter(BBNBackendAdapter):
    backend_name = "alterbbn"

    def write_backend_inputs(self, request: BBNPhysicsRequest, input_dir: Path) -> None:
        param_file = input_dir / "param_file.dat"
        eta_value = 6.137e-10
        if request.config_cosmo and "eta" in request.config_cosmo:
            eta_value = float(request.config_cosmo["eta"])
        param_lines = [
            f"eta={eta_value}",
            f"beta_e_phys={request.beta_e_phys}",
            f"gamma_exch_phys={request.gamma_exch_phys}",
            f"gamma_drain_phys={request.gamma_drain_phys}",
        ]
        if request.config_cosmo:
            for key, value in request.config_cosmo.items():
                if key == "eta":
                    continue
                param_lines.append(f"cosmo_{key}={value}")
        param_file.write_text("\n".join(param_lines) + "\n", encoding="utf-8")

        cosmo_file = input_dir / "cosmo_file.dat"
        cosmo_table = None
        if request.config_cosmo:
            maybe_table = request.config_cosmo.get("cosmo_table")
            if isinstance(maybe_table, list) and maybe_table:
                cosmo_table = maybe_table

        if cosmo_table:
            lines = ["t T dTdt Tnu H nb_etaf"]
            for row in cosmo_table:
                if isinstance(row, dict):
                    lines.append(
                        "{t} {T} {dTdt} {Tnu} {H} {nb_etaf}".format(
                            t=row.get("t", 0.0),
                            T=row.get("T", 0.0),
                            dTdt=row.get("dTdt", 0.0),
                            Tnu=row.get("Tnu", 0.0),
                            H=row.get("H", 0.0),
                            nb_etaf=row.get("nb_etaf", 0.0),
                        )
                    )
            cosmo_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            cosmo_file.write_text(
                "# AlterBBN cosmo_file.dat fallback\n"
                "# expected columns: t T dTdt Tnu H nb_etaf\n"
                "# provide config_cosmo['cosmo_table'] as a list of rows to emit the tabular form\n",
                encoding="utf-8",
            )

    def command(self, input_dir: Path, output_dir: Path) -> list[str]:
        return [str(self.executable_path), str(input_dir), str(output_dir)]

    def parse_outputs(self, output_dir: Path) -> BBNPhysicsResult:
        abundance_file = output_dir / "abundance_file.dat"
        if not abundance_file.exists():
            raise FileNotFoundError(f"missing AlterBBN abundance file: {abundance_file}")

        values = self._read_key_value_file(abundance_file)
        return BBNPhysicsResult(
            D_over_H=float(values.get("D_over_H", values.get("D/H", "nan"))),
            Y_p=float(values.get("Y_p", values.get("Yp", "nan"))),
            Li7_over_H=float(values.get("Li7_over_H", values.get("Li7/H", "nan"))),
            Be7_over_H=float(values.get("Be7_over_H", values.get("Be7/H", "nan"))),
            Li_total_over_H=float(values.get("Li_total_over_H", values.get("Li_total/H", "nan"))),
            backend=self.backend_name,
            executable_path=str(self.executable_path),
            input_dir=str(output_dir.parent / f"{self.backend_name}_input"),
            output_dir=str(output_dir),
            raw_output_path=str(abundance_file),
        )

    @staticmethod
    def _read_key_value_file(path: Path) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
        return values


class ParthenopeBackendAdapter(BBNBackendAdapter):
    backend_name = "parthenope"

    def write_backend_inputs(self, request: BBNPhysicsRequest, input_dir: Path) -> None:
        input_payload = {
            "beta_e_phys": request.beta_e_phys,
            "gamma_exch_phys": request.gamma_exch_phys,
            "gamma_drain_phys": request.gamma_drain_phys,
            "config_cosmo": request.config_cosmo or {},
        }
        (input_dir / "parthenope_input.json").write_text(
            json.dumps(input_payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        driver_file = input_dir / "parthenope_driver.ini"
        driver_lines = [
            f"beta_e_phys={request.beta_e_phys}",
            f"gamma_exch_phys={request.gamma_exch_phys}",
            f"gamma_drain_phys={request.gamma_drain_phys}",
        ]
        if request.config_cosmo:
            for key, value in request.config_cosmo.items():
                if isinstance(value, (str, int, float, bool)):
                    driver_lines.append(f"{key}={value}")
        driver_file.write_text("\n".join(driver_lines) + "\n", encoding="utf-8")

    def command(self, input_dir: Path, output_dir: Path) -> list[str]:
        return [str(self.executable_path), str(input_dir), str(output_dir)]

    def parse_outputs(self, output_dir: Path) -> BBNPhysicsResult:
        candidates = [output_dir / "abundance_file.dat", output_dir / "results.json"]
        for candidate in candidates:
            if candidate.exists():
                if candidate.suffix == ".json":
                    payload = json.loads(candidate.read_text(encoding="utf-8"))
                else:
                    payload = self._read_key_value_file(candidate)
                return BBNPhysicsResult(
                    D_over_H=float(payload.get("D_over_H", payload.get("D/H", "nan"))),
                    Y_p=float(payload.get("Y_p", payload.get("Yp", "nan"))),
                    Li7_over_H=float(payload.get("Li7_over_H", payload.get("Li7/H", "nan"))),
                    Be7_over_H=float(payload.get("Be7_over_H", payload.get("Be7/H", "nan"))),
                    Li_total_over_H=float(payload.get("Li_total_over_H", payload.get("Li_total/H", "nan"))),
                    backend=self.backend_name,
                    executable_path=str(self.executable_path),
                    input_dir=str(output_dir.parent / f"{self.backend_name}_input"),
                    output_dir=str(output_dir),
                    raw_output_path=str(candidate),
                )
        raise FileNotFoundError(f"missing PArthENoPE output file in {output_dir}")

    @staticmethod
    def _read_key_value_file(path: Path) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
        return values


def create_backend(name: str, executable_path: str | Path, work_dir: str | Path | None = None) -> BBNBackendAdapter:
    normalized = name.strip().lower()
    if normalized in {"alterbbn", "alteralterbbn"}:
        return AlterBBNBackendAdapter(executable_path=executable_path, work_dir=work_dir)
    if normalized in {"parthenope", "parthenope3.0", "parthenope30"}:
        return ParthenopeBackendAdapter(executable_path=executable_path, work_dir=work_dir)
    raise ValueError(f"unknown BBN backend: {name}")


def backend_is_available(executable_path: str | Path) -> bool:
    path = Path(executable_path)
    if path.exists():
        return True
    return shutil.which(str(executable_path)) is not None


def example_cosmo_config() -> dict[str, object]:
    return {
        "eta": 6.137e-10,
        "Tnu_over_T": 0.714,
        "cosmo_table": [
            {"t": 1.0e-2, "T": 3.0, "dTdt": -1.0e2, "Tnu": 3.0, "H": 1.0e2, "nb_etaf": 1.0e-10},
            {"t": 1.0e0, "T": 1.0, "dTdt": -1.0e0, "Tnu": 1.0, "H": 1.0e0, "nb_etaf": 1.0e-12},
            {"t": 1.0e2, "T": 1.0e-1, "dTdt": -1.0e-3, "Tnu": 1.0e-1, "H": 1.0e-2, "nb_etaf": 1.0e-14},
        ],
    }


ALTERBBN_INPUT_CONTRACT = {
    "param_file.dat": [
        "eta=<value>",
        "beta_e_phys=<value>",
        "gamma_exch_phys=<value>",
        "gamma_drain_phys=<value>",
        "cosmo_<key>=<value> for any extra scalar input",
    ],
    "cosmo_file.dat": [
        "tabular columns: t T dTdt Tnu H nb_etaf",
        "one row per cosmological point",
    ],
    "outputs": [
        "abundance_file.dat with key=value rows, or stdout redirected into a file",
    ],
}

PARTHENOPE_INPUT_CONTRACT = {
    "parthenope_input.json": [
        "JSON wrapper payload with beta_e_phys, gamma_exch_phys, gamma_drain_phys, config_cosmo",
    ],
    "parthenope_driver.ini": [
        "key=value bridge file for the backend executable",
        "contains the three physical levers plus scalar cosmology keys",
    ],
    "outputs": [
        "abundance_file.dat or results.json as parsed by the adapter",
    ],
}