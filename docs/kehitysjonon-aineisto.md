# Kehitysjonon JSON-aineisto ja välimuisti

**Tila:** käytössä oleva Kehitysjonon tietoputki  
**Päivitystyönkulku:** `.github/workflows/update-kanban-data.yml`  
**Muodostusskripti:** `scripts/build_kanban_data.mjs`

## Tietolähteet

GitHub Issues ja GitHubin natiivit `blocked_by`-riippuvuudet ovat kanoninen tietolähde. `data/kehitysjono.json` on niistä muodostettu, julkinen ja uudelleen rakennettavissa oleva välimuisti. Se ei ole käsin ylläpidettävä rekisteri.

JSON sisältää vain käyttöliittymän tarvitsemat tiedot: issue-numeron, otsikon, URL-osoitteen, avoin/suljettu-tilan, labelit ja päivitysajan sekä jokaisen issue-tiketin `blocked_by`-listan. Tikettien kuvauksia, kommentteja, API-tunnuksia tai raakavastauksia ei kopioida aineistoon.

Selain hakee yhden JSON-tiedoston GitHub Pagesista. Selain ei kutsu GitHub APIa eikä sisällä käyttöoikeustunnuksia.

## Päivitysmalli

### Inkrementaalinen päivitys

Päivitystyönkulku kuuntelee GitHubin `issues`-tapahtumaa, ei yleistä repositorion `push`-tapahtumaa. Issue-muutoksista hyväksytään vain Kehitysjonon kannalta olennaiset:

- uuden issuen avaaminen, sulkeminen, uudelleen avaaminen ja poistaminen;
- otsikon tai kuvauksen muokkaus (pelkkä esimerkiksi assigneen tai milestone-tiedon muutos ei käynnistä päivitystä);
- `component:`-, `priority:`- tai `status:`-labelin lisääminen tai poistaminen.

Muut labelit, kommentit, assignee-muutokset ja muut issue-tapahtumat eivät käynnistä JSON-päivitystä. Pull requestit ohitetaan.

Yleinen tiedostomuutos ei käynnistä tätä työnkulkua. Rajattu `push`-käynnistys on käytössä vain, kun itse välimuistin muodostusskripti tai sen päivitystyönkulku muuttuu; silloin tehdään yksi täysi täsmäytys uuden toteutuksen varmistamiseksi. Päivittäinen ajastus ja käsin käynnistettävä täysi täsmäytys ovat erillisiä varmistusmekanismeja.

Muuttuneen tiketin riippuvuudet haetaan uudelleen. Muiden issueiden tietueet ja riippuvuudet säilyvät aiemmasta kelvollisesta välimuistista. Tämä vähentää tavallisten muutosten API-kutsut käytännössä yhteen riippuvuushakuun; issue-tapahtuman koko tietue saadaan tapahtumaviestistä.

Riippuvuuspyynnön käsittelijä käynnistää onnistuneen natiivin riippuvuusmuutoksen jälkeen saman päivitystyönkulun kohdistettuna kyseiseen tikettiin. Näin ChatGPT:n välittämät riippuvuusmuutokset päivittyvät heti ilman kaikkien tikettien läpikäyntiä.

### Täysi täsmäytys

- Täysi täsmäytys tehdään kerran vuorokaudessa klo 03.17 UTC.
- Työnkulun voi käynnistää käsin GitHub Actionsin `workflow_dispatch`-toiminnolla. Kun issue-numeroa ei anneta, tehdään täysi täsmäytys.
- Täysi täsmäytys hakee kaikki avoimet ja suljetut issue-tiketit sekä niiden riippuvuudet. Tämä löytää myös suoraan GitHubin käyttöliittymässä tehdyt natiivien riippuvuuksien muutokset, joista GitHub ei lähetä erillistä issue-tapahtumaa.
- Ylläpitokoodin muutokset käynnistävät täyden muodostuksen.

Täysi täsmäytys on tarkoituksella harvempi kuin tavalliset issue-päivitykset. Jos issueita tulee huomattavasti lisää, aikataulua ja API-kutsujen määrää voidaan tarkentaa mittaustulosten perusteella.

## Välimuistin eheys ja virhetilanteet

- Päivitykset suoritetaan samassa concurrency-ryhmässä, eikä käynnissä olevaa ajoa peruta uuden vuoksi.
- Uusi JSON muodostetaan väliaikaistiedostoon ja nimetään lopulliseksi vasta muodostuksen ja rakennetarkistusten onnistuttua.
- API-virhe, puuttuva riippuvuustieto tai virheellinen vastausrakenne keskeyttää päivityksen. Viimeisin kelvollinen JSON jää käyttöön.
- Vioittunut tai vanhentuneella rakenteella oleva välimuisti voidaan muodostaa uudelleen GitHubin kanonisista tiedoista.
- JSONin `generated_at` kertoo viimeisimmän onnistuneen päivityksen ajan. `full_sync_at` kertoo viimeisimmän onnistuneen täyden täsmäytyksen ajan.
- Aineiston `status` on `complete` vain, kun kaikki vaaditut tiedot on saatu ja tarkistettu. Osittaista aineistoa ei julkaista täydellisenä.
- Työnkulku tallentaa onnistuneen JSONin repositorioon. Pagesin branch-pohjainen julkaisu voi siten palvella tiedostoa suoraan samalla sivustolla.

## Oikeudet ja rajaukset

Päivitystyönkulku käyttää `contents: write`-oikeutta vain JSON-välimuistin tallentamiseen ja `issues: read`-oikeutta lähdetietojen hakemiseen. Riippuvuuksien erillinen välitystyönkulku käyttää lisäksi `issues: write`-oikeutta natiivien suhteiden hallintaan sekä `actions: write`-oikeutta kohdistetun välimuistipäivityksen käynnistämiseen.

Tämä tietoputki ei muuta ChatGPT-automaatiotehtäviä, ajastuksia, käynnistyskehotteita tai kohdekeskusteluja. Se ei käynnistä aihekohtaisia seurantatehtäviä eikä julkaise RSS-raportteja.

## GitHub Projectin tila- ja prioriteettisynkronointi

GitHub Project **Aiheseurain** toimii Kehitysjonon visuaalisena Kanban-näkymänä. Issue-labelit ovat tilan ja prioriteetin ensisijaiset tietolähteet; Projectin Status- ja Priority-kentät ovat niistä johdettuja näkymätietoja.

Määritys on tiedostossa `.github/project-status-sync.json`. Se sisältää Projectin ja Status-kentän asetukset sekä Priority-kentän nimen, ei salaisuuksia. Priority-kentän tunniste ja vaihtoehtojen tunnisteet haetaan Projectista kentän nimen perusteella, joten niitä ei tarvitse kopioida asetustiedostoon.

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

Priority-kentän Single select -vaihtoehtojen nimien tulee alkaa vastaavalla tunnuksella (esimerkiksi `P1` tai `P1 – Korkea`). Synkronointi hylkää puuttuvan, moninkertaisen tai tuntemattoman prioriteettilabelin sekä tilanteen, jossa kentästä ei löydy täsmälleen yhtä vastaavaa vaihtoehtoa.

Kun tavalliseen issueen lisätään tai siitä poistetaan `status:`-label tai `priority:`-label, päivitystyönkulku hakee issuen ajantasaiset labelit ja päivittää vastaavat Project-kentät. Uuden issuen avaamisen ja uudelleen avaamisen yhteydessä molemmat kentät synkronoidaan. Jos issue ei vielä ole Projectissa, se lisätään sinne automaattisesti. Prioriteetin vaihdossa uuden labelin lisääminen käynnistää lopullisen synkronoinnin.

Synkronointi on tarkoituksella yksisuuntainen: Projectissa tehty Status- tai Priority-muutos ei muuta issue-labelia. Issue-label on kanoninen tieto. Issuella pitää olla täsmälleen yksi tunnettu `status:`- ja yksi `priority:`-label; puuttuva, moninkertainen tai tuntematon label aiheuttaa näkyvän työnkulkuvirheen eikä arvoa arvata.

Työnkulku käyttää repositoryn Actions-salaisuutta `PROJECTS_TOKEN`. Sen GitHub-tokenilla pitää olla Projectin luku- ja kirjoitusoikeus (classic PAT: `project`-scope). Tavallinen `GITHUB_TOKEN` hakee issue-tiketin ajantasaiset tiedot. Tunnusta ei tallenneta repositoryn tiedostoihin eikä lokitulosteisiin.

Tämä synkronointi ei muuta issueiden label-sääntöjä, riippuvuuksia, JSON-välimuistin rakennetta tai ChatGPT-automaatiotehtäviä.

## Testaus

Testit sijaitsevat tiedostoissa:

- `tests/kanban.test.mjs`: label-luokittelu, suodatus, riippuvuusverkon molemmat suunnat ja aineiston tuoreustiedot.
- `tests/kanban-data.test.mjs`: täysi muodostus, inkrementaalinen päivitys, poisto, täsmäytyksen valinta ja virheellisten riippuvuustietojen hylkääminen.
- `tests/issue-dependencies.test.mjs`: riippuvuuspyynnön tulkinta, syklistä kieltäytyminen, idempotentit muutokset ja päivitystyönkulun käynnistys.
- `tests/project-status-sync.test.mjs`: Projectin tila- ja prioriteettikenttien label-muunnokset sekä kentän dynaaminen haku.

Testit suoritetaan GitHub Actionsin `Testaa Kehitysjonon aineisto ja riippuvuudet)-työnkulussa.
