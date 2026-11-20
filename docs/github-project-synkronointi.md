# GitHub Projectin Status-, Priority- ja Component-synkronointi

GitHub Project **Aiheseurain** on kehitystehtävien ensisijainen taulukkonäkymä. GitHub Issuesin labelit ovat tilan, prioriteetin ja komponentin kanoninen tietolähde; Projectin kentät ovat niistä johdettuja näkymätietoja.

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
| `priority:P0` | P0 Kriittinen |
| `priority:P1` | P1 Korkea |
| `priority:P2` | P2 Normaali |
| `priority:P3` | P3 Matala |

**Component**

| Issue-label | Projectin Component |
|---|---|
| `component:automaatio` | Automaatio |
| `component:etusivu` | Etusivu |
| `component:lukija` | Lukija |
| `component:valvomo` | Valvomo |
| `component:kehitysymparisto` | Kehitysympäristö |

Project-kentät ja niiden Single select -vaihtoehdot tunnistetaan asetustiedostoon tallennetuilla ID-tunnisteilla. Näkyviä nimiä ei käytetä kenttien tai vaihtoehtojen etsimiseen, joten nimien muuttaminen ei riko synkronointia. Jos kenttä tai vaihtoehto poistetaan ja luodaan uudelleen, sen ID vaihtuu ja asetustiedosto pitää päivittää.

## Synkronoinnin toiminta

Työnkulku `.github/workflows/sync-project-fields.yml` käynnistyy, kun tavallinen issue avataan tai avataan uudelleen, tai kun siitä lisätään tai poistetaan `status:`-, `priority:`- tai `component:`-label. Se hakee issuen ajantasaiset tiedot, varmistaa että sillä on täsmälleen yksi kutakin näistä kolmesta label-luokasta, lisää kortin Projectiin tarvittaessa ja päivittää Status-, Priority- ja Component-kentät niiden ID-tunnisteilla.

Synkronointi on yksisuuntainen: Projectissa tehty kenttämuutos ei muuta issue-labelia. Issue-label on aina ensisijainen tieto.

Yksittäisen vanhan issuen voi täsmäyttää käsin GitHub Actionsin **Synkronoi GitHub Projectin Status, Priority ja Component** -työnkulussa antamalla `issue_number`-syötteen.

## Oikeudet ja salaisuudet

Työnkulku käyttää repositoryn Actions-salaisuutta `PROJECTS_TOKEN`. Tunnuksella pitää olla Projectin luku- ja kirjoitusoikeus. Tavallinen `GITHUB_TOKEN` lukee issuen ajantasaiset tiedot. Tunnuksia ei tallenneta repositorion tiedostoihin, tulosteisiin tai lokeihin.

## Testaus

Synkronoinnin label-muunnokset ja kenttien ID-määritykset testataan tiedostossa `tests/project-status-sync.test.mjs`. Testit suoritetaan työnkulussa `.github/workflows/test-project-sync.yml`. Testit varmistavat myös, ettei kenttien tai vaihtoehtojen näkyvien nimien muuttuminen vaikuta ID-pohjaiseen synkronointiin.

Project-kenttien kirjoitusoikeuden toimivuus varmennetaan myös todellisella synkronointiajolla. Pelkkä yksikkötesti ei todista, että repositoryn `PROJECTS_TOKEN` pystyy kirjoittamaan käyttäjän Projectiin.
