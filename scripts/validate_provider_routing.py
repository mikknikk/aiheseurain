"""Validoi repositorion tekninen palvelureitityskonfiguraatio."""
from scripts.provider_router import load_provider_config


def main() -> None:
    """Tarkista reitityksen skeema ja varmista, ettei testiympäristö aktivoidu tuotantoon."""
    config = load_provider_config()
    if any(item["enabled"] for item in config["providers"]):
        raise SystemExit("Tuotantopalvelujen aktivointi vaatii erillisen hyväksytyn käyttöönoton.")
    if config["routes"] or config["default_route"] is not None:
        raise SystemExit("Tuotantoreitit vaativat erillisen käyttöönoton ja adapterien rekisteröinnin.")
    print("OK: palvelureitityksen skeema on kelvollinen; tuotantopalveluja tai reittejä ei ole aktivoitu.")


if __name__ == "__main__":
    main()
