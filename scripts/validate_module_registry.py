"""Tarkista repositorion seurantamoduulirekisteri ja sen turvalliset rajaukset."""

from scripts.module_registry import REGISTRY_PATH, load_registry


def main() -> None:
    """Validoi kaikki rekisterimerkinnät ja ilmoita eristetyt virheet."""
    result = load_registry()
    for module in result.modules:
        if module.status == "invalid":
            print(f"VIRHE: {module.module_id}: {module.error}")
        else:
            print(f"OK: {module.module_id}: {module.status}")

    if result.invalid_modules:
        raise SystemExit(f"Rekisterissä on {len(result.invalid_modules)} virheellistä merkintää.")

    print(
        f"OK: {len(result.active_modules)} aktiivista ja validoitua moduulia "
        f"rekisterissä {REGISTRY_PATH.relative_to(REGISTRY_PATH.parents[1])}."
    )


if __name__ == "__main__":
    main()
