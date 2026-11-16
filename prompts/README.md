# Automaation käynnistyskehotteet

Tämä hakemisto sisältää `mikknikk/uutiset`-repositorioon liittyvien kolmen automaation asetuksiin kopioitavat käynnistyskehotteet. Kunkin `.txt`-tiedoston sisältö on tarkoitettu kopioitavaksi sellaisenaan automaation prompt-kenttään.

## Tiedostot ja vastuut

| Automaatio | Kanoninen käynnistyskehote | Varsinainen käsikirja |
|---|---|---|
| Päivittäinen uutisseurannan aihekierros | [`paauutisseuranta.txt`](paauutisseuranta.txt) | [`docs/paaautomaation-ohje.md`](../docs/paaautomaation-ohje.md) |
| Intialaisten elokuvien näytösvahti | [`naytosvahti.txt`](naytosvahti.txt) | [`docs/intialaisten-elokuvien-naytosseuranta.md`](../docs/intialaisten-elokuvien-naytosseuranta.md) |
| Viikoittainen järjestelmän laatutarkistus | [`laatutarkistus.txt`](laatutarkistus.txt) | [`docs/laatutarkistuksen-ohje.md`](../docs/laatutarkistuksen-ohje.md) |

## Ylläpitoperiaate

- `prompts/*.txt` sisältää vain automaation asetuksiin kopioitavan tekstin. Älä lisää tiedostoihin selittäviä otsikoita tai Markdown-muotoilua.
- Tehtävien varsinainen sisältö, rajaukset, tarkistuslistat ja onnistumisehdot määritellään yllä olevissa käsikirjoissa. Käynnistyskehote ohjaa lukemaan oikean käsikirjan ja tekemään sen esitarkistukset.
- Kun automaation käynnistyskehotetta muutetaan, päivitä ensin tämän hakemiston kanoninen tiedosto ja kopioi sen koko sisältö vastaavan automaation asetuksiin. Älä päivitä automaation asetuksia eri sisältöön kuin repositorion tiedosto.
- Kun kehote on kopioitu asetuksiin, vertaa tallennettua tekstiä tiedostoon ja varmista, että ne ovat täsmälleen samat. Asetusten päivitys on erillinen manuaalinen vaihe; GitHub-muutos ei päivitä automaation asetuksia automaattisesti.
- Älä muuta automaatioiden aikatauluja tai tehtäväkäsikirjoja pelkän käynnistyskehotteen siirron yhteydessä.
- Jos käsikirjan polku tai versionumero muuttuu, päivitä käynnistyskehote vain samassa muutossarjassa ja tarkista, että se vastaa `data/seurantatila.json`-tiedoston vastaavaa ohjeversiota.
- Säilytä pääuutisseurannan, näytösvahdin ja laatutarkistuksen rajat erillisinä. Älä yhdistä niiden käynnistyskehotteita yhdeksi yleiseksi promptiksi.

Pääuutisseurannan käynnistyskehotetta on päivitetty vastaamaan lähdekatalogin ja tehtäväkohtaisten käyttörekisterien uutta rakennetta. Kopioi päivitetty `paauutisseuranta.txt` kokonaisuudessaan pääautomaation asetuksiin ja varmista, että tallennettu teksti vastaa tiedostoa. Muut käynnistyskehotteet eivät muutu tämän lähdetietomallin uudistuksen vuoksi.
