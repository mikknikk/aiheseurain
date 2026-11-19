"""Suorita aihekohtainen Python-runner erillisessä bubblewrap-sandboxissa.

Runnerille näkyvät vain:
- lukuoikeudellinen JSON-syöte (/input/bundle.json),
- lukuoikeudellinen runner-ohjelma (/runner/runner.py),
- kirjoitusoikeudellinen tuloshakemisto (/output),
- Pythonin ja käyttöjärjestelmän välttämättömät runtime-tiedostot.

Päärepon tiedostoja, kotihakemistoa, verkkoa tai ympäristömuuttujia ei liitetä
sandboxiin. Jos Linux/bubblewrap-ympäristöä ei ole saatavilla, suoritus epäonnistuu
suljetusti: tavalliseen subprocess-ajoon ei pudota.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import resource
import tempfile
from typing import Any, Mapping

from scripts.module_input_bundle import bundle_to_json

MAX_RESULT_BYTES = 5 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 300
PYTHON_EXECUTABLE = "/usr/bin/python3"


class IsolatedRunnerError(RuntimeError):
    """Sandboxatun runner-ajon tai tuloksen validoinnin virhe."""


def _runtime_mounts() -> list[str]:
    """Määritä vain Python-ajon vaatimat järjestelmäkirjastot luettaviksi."""
    mounts: list[str] = []
    for path in ("/usr", "/lib", "/lib64"):
        if os.path.exists(path):
            mounts.extend(["--ro-bind", path, path])
    return mounts


def _limit_child_resources(timeout_seconds: int):
    """Rajoita runnerin CPU-aikaa, tiedostokokoa, tiedostokuvauksia ja core-dumppeja."""
    def apply_limits() -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (timeout_seconds, timeout_seconds + 1))
        resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_RESULT_BYTES, MAX_RESULT_BYTES))
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    return apply_limits


def _sandbox_command(
    bubblewrap: str, workspace: Path, *, timeout_seconds: int
) -> list[str]:
    """Rakenna verkoton mount-namespacen komento ilman repositorioliitoksia."""
    input_dir = workspace / "input"
    runner_dir = workspace / "runner"
    output_dir = workspace / "output"
    output_file = output_dir / "result.json"
    command = [
        bubblewrap,
        "--unshare-all",
        "--die-with-parent",
        "--new-session",
        "--clearenv",
        "--proc", "/proc",
        "--dev", "/dev",
        "--tmpfs", "/tmp",
        "--dir", "/input",
        "--dir", "/runner",
        "--dir", "/output",
        "--ro-bind", str(input_dir), "/input",
        "--ro-bind", str(runner_dir), "/runner",
        "--ro-bind", str(output_dir), "/output",
        "--bind", str(output_file), "/output/result.json",
        "--chdir", "/tmp",
        "--setenv", "PATH", "/usr/bin",
        "--setenv", "HOME", "/tmp",
        "--setenv", "PYTHONNOUSERSITE", "1",
        "--setenv", "PYTHONDONTWRITEBYTECODE", "1",
    ]
    command.extend(_runtime_mounts())
    command.extend([PYTHON_EXECUTABLE, "-I", "-S", "/runner/runner.py",
                    "/input/bundle.json", "/output/result.json"])
    return command


def run_isolated_module(
    bundle: Mapping[str, Any],
    runner_source: str,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    bubblewrap_path: str | None = None,
) -> dict[str, Any]:
    """Suorita runner vain rajatussa sandboxissa ja palauta sen JSON-tulos.

    Runnerin lähdekoodi on sisältöä, ei tiedostopolku. Näin suorittajalle ei
    välitetä repositorion tiedostoviitteitä. Tulostiedosto luetaan vasta kun
    prosessi on päättynyt onnistuneesti; virheellinen tai liian suuri tulos
    hylätään eikä mitään moduulin tilaa päivitetä tässä funktiossa.
    """
    if not isinstance(runner_source, str) or not runner_source.strip():
        raise IsolatedRunnerError("Runner-ohjelman lähdekoodi puuttuu.")
    if not isinstance(timeout_seconds, int) or timeout_seconds < 1 or timeout_seconds > 3600:
        raise IsolatedRunnerError("Aikarajan pitää olla kokonaisluku väliltä 1–3600 sekuntia.")
    bubblewrap = bubblewrap_path or shutil.which("bwrap")
    if os.name != "posix" or not Path("/proc").exists() or not bubblewrap:
        raise IsolatedRunnerError(
            "Turvallista Linux/bubblewrap-sandboxia ei ole saatavilla; ajo estettiin."
        )
    if not Path(PYTHON_EXECUTABLE).is_file():
        raise IsolatedRunnerError(
            f"Sandboxin Python-ajonaika puuttuu: {PYTHON_EXECUTABLE}"
        )

    with tempfile.TemporaryDirectory(prefix="aiheseurain-run-") as temporary:
        workspace = Path(temporary)
        input_dir, runner_dir, output_dir = (
            workspace / "input", workspace / "runner", workspace / "output"
        )
        for directory in (input_dir, runner_dir, output_dir):
            directory.mkdir(mode=0o700)
        input_file = input_dir / "bundle.json"
        runner_file = runner_dir / "runner.py"
        result_file = output_dir / "result.json"
        input_file.write_text(bundle_to_json(bundle), encoding="utf-8")
        runner_file.write_text(runner_source, encoding="utf-8")
        result_file.write_bytes(b"")
        input_file.chmod(0o400)
        runner_file.chmod(0o400)
        result_file.chmod(0o600)

        command = _sandbox_command(bubblewrap, workspace, timeout_seconds=timeout_seconds)
        try:
            completed = subprocess.run(
                command,
                cwd=workspace,
                env={"PATH": "/usr/bin"},
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=_limit_child_resources(timeout_seconds),
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise IsolatedRunnerError("Aiheajo ylitti sallitun suoritusajan.") from exc
        except OSError as exc:
            raise IsolatedRunnerError("Sandbox-prosessia ei voitu käynnistää.") from exc

        if completed.returncode != 0:
            raise IsolatedRunnerError(
                f"Sandboxattu aiheajo epäonnistui (exit {completed.returncode})."
            )

        result_file = output_dir / "result.json"
        try:
            # Avaa vain tavallinen tiedosto; älä seuraa runnerin mahdollisesti luomia symlinkkejä.
            descriptor = os.open(result_file, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(descriptor, "rb") as result_stream:
                if not os.path.isfile(result_file) or os.fstat(result_stream.fileno()).st_size > MAX_RESULT_BYTES:
                    raise IsolatedRunnerError("Runnerin tulostiedosto on virheellinen tai ylittää 5 MiB:n kokorajan.")
                raw_result = result_stream.read(MAX_RESULT_BYTES + 1)
            if len(raw_result) > MAX_RESULT_BYTES:
                raise IsolatedRunnerError("Runnerin tulos ylittää sallitun 5 MiB:n kokorajan.")
            result = json.loads(raw_result.decode("utf-8"))
        except IsolatedRunnerError:
            raise
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IsolatedRunnerError("Runnerin tulos ei ole kelvollista UTF-8 JSON -dataa.") from exc
        if not isinstance(result, dict):
            raise IsolatedRunnerError("Runnerin tuloksen ylimmän tason pitää olla JSON-olio.")
        return result
