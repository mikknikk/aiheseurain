# GitHub Projectin Status- ja Priority-synkronointi

GitHub Project **Aiheseurain** on kehitystehtävien ensisijainen taulukkonäkymä. GitHub Issuesin labelit ovat tilan ja prioriteetin kanoninen tietolähde; Projectin kentät ovat niistä johdettuja näkymätietoja.

## Labelien ja Project-kenttien vastaavuus

**Status**

| Issue-label | Projectin Status |
|---|---|
| `status:backlog` | Todo |
| `status:ready-for-development` | Ready for Development |
| `status:in-progress` | In Progress |
| `status:done` | Done |

**Priority**

| Issue-label | Projectin Priority |
|---|---|
| `priority:P0` | P0 |
| `priority:P1` | P1 |
| `priority:P2` | P2 |
| `priority:P3` | P3 |

Priority-kentän Single select -vaihtoehtojen nimien tulee alkaa vastaavalla tunnuksella (esimerkiksi `P1` tai `P1 – Korkea`). Synkronointi hylkää puuttuvan, moninkertaisen tai tuntemattoman prioriteettilabelin tai vastaavan vaihtoehdon puuttumisen.

## Synkronoinnin toiminta

Työnkulku `.github/workflows/sync-project-fields.yml` käynnistyy, kun tavallinen issue avataan tai avataan uudelleen, tai kun siitä lisätään tai poistetaan `status:`- tai `priority:`-label. Se hakee issuen ajantasaiset tiedot, varmistaa että sillä on täsmälleen yksi `component:`-, `status:`- ja `priority:`-label, lisää kortin Projectiin tarvittaessa ja päivittää Status- ja Priority-kentät.

Synkronointi on yksisuuntainen: Projectissa tehty kenttämuutos ei muuta issue-labelia. Issue-label on aina ensisijainen tieto.

Yksittäisen vanhan issuen voi täsmäyttää käsin GitHub Actionsin **Synkronoi GitHub Projectin Status ja Priority** -työnkulussa antamalla `issue_number`-syötteen.

## Oikeudet ja salaisuudet

Työnkulku käyttää repositoryn Actions-salaisuutta `PROJECTS_TOKEN`. Tunnuksella pitää olla Projectin luku- ja kirjoitusoikeus. Tavallinen `GITHUB_TOKEN` lukee issuen ajantasaiset tiedot. Tunnuksia ei tallenneta repositorion tiedostoihin, tulosteisiin tai lokeihin.

## Testaus

Synkronoinnin muunnokset ja kenttien tunnistus testataan tiedostossa `tests/project-status-sync.test.mjs`. Testit suoritetaan työnkulussa `.github/workflows/test-project-sync.yml`.

Projectin kirjoitusoikeuden toimivuus varmennetaan myös todellisella synkronointiajolla. Pelkkä yksikkötesti ei todista, että repositoryn `PROJECTS_TOKEN` pystyy kirjoittamaan käyttäjän Projectiin.
