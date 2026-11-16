# Näytösseurannan muutoshistorian tietomalli

Tämä ohje kuvaa tiedoston `data/naytosten-muutoshistoria.json` rakennetta ja päivittämistä. Tiedosto on näytösseurannan sisäinen koneellisesti luettava tietolähde; RSS-syöte on siitä erillinen lukijoille julkaistava versiohistoria.

## Periaatteet

1. **Tapahtumaloki on vain lisäämällä ylläpidettävä.** Älä muokkaa tai poista aiempia `events`-tapahtumia. Jos aiempaan tapahtumaan jäi virhe, lisää uusi `correction`-tapahtuma ja selitä korjaus.
2. **Nykytila ja historia ovat eri asioita.** `screenings` sisältää kunkin tunnetun näytöksen viimeisimmän tilan. `events` kertoo, mitä havaittiin ja milloin.
3. **Tunniste säilyy muutoksissa.** Anna uudelle näytökselle pysyvä `screening_id`, joka muodostetaan aluksi elokuvan, teatterin ja alkuperäisen näytösajan tunnistetiedoista. Kun näytös siirtyy toiseen kellonaikaan tai saliin, päivitä saman tunnisteen tietue; älä luo muutokselle uutta tunnistetta. Säilytä myös päättyneet, perutut ja ohjelmistosta poistuneet tietueet niiden tilamerkinnöillä, älä poista niitä historiasta.
4. **Älä päättele peruutusta katoamisesta.** Jos näytös poistuu ohjelmistosta eikä peruutusta ole ilmoitettu, käytä tapahtumatyyppiä `removed_from_listing` ja tilaa `removed`. Käytä `cancelled` vain, kun lähde ilmoittaa peruutuksesta.
5. **Säilytä ilmoituksen vahvistustaso.** Käytä täsmälleen yhtä arvoa: `TEATTERIN VAHVISTAMA`, `JÄRJESTÄJÄN ILMOITTAMA` tai `KOLMANNEN OSAPUOLEN ILMOITTAMA`. Älä nosta kolmannen osapuolen ilmoitusta vahvistetuksi.
6. **Kaikki ajat ovat aikavyöhykkeellisiä ISO 8601 -aikoja.** Käytä `Europe/Helsinki`-aikaa ja offsetia, esimerkiksi `2026-11-18T19:45:00+02:00`.
7. **Lähde tallennetaan tapahtumaan.** Tallenna suora URL, julkaisija, tarkistusaika, mahdollinen julkaisuaika ja ilmoituksen vahvistustaso.
8. **Tee päivityksistä uusintakäsittelyä kestäviä.** Muodosta `event_id` deterministisesti tapahtuman tyypistä, näytöstunnisteesta, havaintoajasta ja muutoksen sisällöstä. Tarkista ennen lisäystä, ettei sama `event_id` ole jo lokissa.

## Tiedoston ylätaso

- `schema_version`: tietomallin versio, tällä hetkellä 1.
- `timezone`: aina `Europe/Helsinki`.
- `baseline_status`: aluksi `pending_first_verified_run`; ensimmäisen onnistuneen lähtötilan muodostamisen jälkeen `active`.
- `notes`: ylläpidon huomioita.
- `screenings`: näytösten viimeisimmät tunnetut tiedot.
- `events`: aikajärjestyksessä lisättävät muutoshistoriatapahtumat.

## Näytöstietueen kentät

Pakolliset kentät:
- `screening_id`: pysyvä tunniste.
- `film`: elokuvan nimi.
- `venue`: teatterin tai tapahtumapaikan nimi.
- `city`: paikkakunta.
- `starts_at`: näytöksen päivämäärä ja kellonaika offsetin kanssa.
- `status`: `scheduled`, `cancelled`, `removed` tai `completed`.
- `source_claim_type`: tiedon vahvistustaso.
- `sources`: vähintään yksi lähdetietue.

Lisätiedot kuten `language`, `subtitles`, `booking_url`, `external_show_id` ja `notes` voidaan tallentaa, kun ne on lähteestä varmennettu. Älä päättele puuttuvia tietoja. Esimerkiksi pysyvä tunniste voi olla `ramayana-finnkino-itis-20261116-2015`; jos kellonaika myöhemmin muuttuu, tämä alkuperäinen tunniste säilytetään.

Lähdetietue sisältää:
- `publisher`: lähteen julkaisija.
- `url`: suora lähdeosoite.
- `published_at`: julkaisuaika tai `null`, jos sitä ei tiedetä.
- `checked_at`: aika, jolloin lähde tarkistettiin.
- `claim_type`: yksi kolmesta vahvistustasosta.
- `notes`: mahdollinen ristiriita tai tarkennus.

## Tapahtumatyypit

| Tyyppi | Käyttö |
|---|---|
| `baseline_created` | Ensimmäinen varmennettu lähtötilanne muodostettiin. Tapahtuma ei koske yhtä näytöstä. |
| `added` | Uusi näytös havaittiin. |
| `time_changed` | Näytöksen päivämäärä tai kellonaika muuttui. |
| `venue_changed` | Näytöspaikka tai teatteri muuttui. |
| `details_changed` | Esityskieli, tekstitys, lipputieto tai muu olennainen tieto muuttui. |
| `cancelled` | Lähde ilmoitti nimenomaisesti näytöksen peruuntuneen. |
| `removed_from_listing` | Näytös katosi ohjelmistosta, mutta peruutusta ei vahvistettu. |
| `reinstated` | Aiemmin poistettu tai perutuksi ilmoitettu näytös palautui ohjelmistoon. |
| `correction` | Aiemman lokimerkinnän virhe korjataan jälkikäteen. |

Jokainen muu kuin lähtötilanteen luontitapahtuma sisältää:
- `event_id`: yksilöllinen, uusintakäsittelyssä vakaa tunniste.
- `observed_at`: hetki, jolloin muutos havaittiin.
- `type`: tapahtumatyyppi.
- `screening_id`: muutoksen kohteena olevan näytöksen pysyvä tunniste.
- `previous`: aiempi tietue tai `null), jos kyseessä on uusi näytös.
- `current`: uusi tietue tai `null), jos näytös poistui eikä uutta nykytilaa ole.
- `sources`: muutoksen todentavat lähteet.
- `note`: lyhyt selitys.

## Ensimmäinen käyttöönotto

Nykyistä RSS-historiaa ei muunnettu automaattisesti näytöskohtaisiksi tapahtumiksi, koska julkaistut HTML-listat eivät takaa kaikkien näytösten ja lähdetietojen yksiselitteistä koneellista tunnistamista. Tiedoston lähtötila on siksi aluksi tyhjä ja merkitty odottavaksi.

Ensimmäisessä onnistuneessa näytösvahdin ajossa:
1. Lue nykyinen muutoshistoria, koko näytös-RSS ja sen viimeisimmät elokuvakohtaiset julkaisut.
2. Tarkista ajantasaiset näytöstiedot lähteistä.
3. Muodosta varmennettu nykytila. Älä tee takautuvia väitteitä siitä, milloin aiemmat muutokset tapahtuivat.
4. Lisää yksi `baseline_created`-tapahtuma, jossa kerrotaan lähtötilan muodostusaika ja näytöstietueiden määrä.
5. Aseta `baseline_status` arvoon `active`.
6. Tallenna kaikki tiedostot ja lue ne takaisin GitHubista. Vasta onnistuneen takaisinluvun jälkeen päivitä näytösvahdin onnistunut tarkistusaika tiedostoon `data/seurantatila.json`.

## Päivittäinen päivitys

Jokaisella seuraavalla ajolla vertaa lähteistä tarkistettua nykytilaa edellisen ajon `screenings)-tietoihin. Lisää jokaisesta todellisesta muutoksesta tapahtuma. Päivitä `screenings)-tietueet vastaamaan viimeisintä tilaa. Älä lisää tapahtumaa muuttumattomasta näytöksestä. Älä myöskään tulkitse ohjelmistosta puuttumista peruutukseksi ilman lähteen vahvistusta.

Kun näytöstietue ja RSS julkaisu päivitetään samalla ajolla, tee muutokset yhtenä loogisena kokonaisuutena. Säilytä vanhat RSS-itemit ja GUIDit. RSS:ään lisätään uusi elokuvakohtainen versio vain, jos julkaistava tieto muuttui. Sisäiseen JSON-lokiin kirjataan jokainen olennainen muutos myös silloin, kun se ei yksin edellytä uutta RSS-versiota.

## JSON Schema ja koneellinen validointi

Tietomallin virallinen rakenteellinen määrittely on `schemas/naytosten-muutoshistoria.schema.json` (JSON Schema Draft 2020-12). Se määrittelee pakolliset kentät, tietotyypit, sallitut tilat ja tapahtumatyypit sekä lähdetietueiden ja tapahtumien rakenteet. `scripts/validate_feeds.py` validoi muutoshistorian ensin tätä skeemaa vasten ja tekee sen jälkeen lisäksi projektikohtaiset eheys- ja ristiriitatarkistukset. `jsonschema`-riippuvuus asennetaan `requirements.txt`-tiedostosta GitHub Actions -työnkulussa.

## Laatutarkistukset

`scripts/validate_feeds.py` tarkistaa JSON Schema -määrittelyn lisäksi aikaleimojen aikavyöhykkeet, tunnisteiden yksilöllisyyden, sallitut tilat ja tapahtumatyypit sekä lähteiden URL-osoitteiden muodon. Automaattinen testi ei kuitenkaan pysty todistamaan, että lähde todella tukee väitettä tai että kaksi eri lähdettä ovat riippumattomia. Nämä tarkistetaan näytösvahdin työohjeen mukaisesti.
