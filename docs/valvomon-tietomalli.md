# Valvomon tietomalli ja julkaisutapa

**Tila:** tietomalli hyväksytty; Valvomon vähimmäisnäkymä (#30) yhdistetty; sivurakenteen erottaminen (#38) toteutuksessa  
**Päivitetty:** 2026-11-16  
**Liittyvät tehtävät:** [#29 – Pages-kartoitus ja tietomalli](https://github.com/mikknikk/uutiset/issues/29), [#30 – Valvomon vähimmäisversio](https://github.com/mikknikk/uutiset/issues/30)

Tämä dokumentti määrittää Valvomon tietolähteet, julkaisutavan, tietojen tulkinnan ja julkistamisen rajat. Käyttöliittymän nykyinen toteutus ja sen tunnetut tietorajoitteet kuvataan luvussa 9.

## 1. Nykyinen GitHub Pages -julkaisu

Repositorion Pages-osoite on [https://mikknikk.github.io/uutiset/](https://mikknikk.github.io/uutiset/). Repositorio on julkinen ja sen oletushaara on `main`.

Kartoitus 16.11.2026:

- Repositorion juurihakemistossa ovat `README.md`, `index.html` (Aiheseurainin etusivu), `valvomo/` (Valvomon sivu), `feeds/`, `data/`, `docs/`, `schemas/`, `scripts/` ja muut projektin hakemistot.
- RSS-tiedostot ovat juuren `feeds/`-hakemistossa, ja niiden kanoniset osoitteet ovat muotoa `https://mikknikk.github.io/uutiset/feeds/{tiedosto}.xml`.
- Repositorion omissa työnkuluissa ei ole Pages-julkaisua tekevää workflow-tiedostoa. `.github/workflows/` sisältää RSS-/dokumentaatiotestit ja viikoittaisen linkkitarkistuksen.
- GitHubin automaattinen `pages build and deployment` -ajo käynnistyi `main`-haaran päivityksistä. Viimeisimmän tarkistetun julkaisun ajo 16.11.2026 (`43939321329`) käytti vaiheita `Build with Jekyll`, `Upload artifact` ja `Deploy to GitHub Pages`; kaikki vaiheet onnistuivat.
- Repositorion juuressa on nyt Aiheseurainin etusivu (`index.html`) ja Valvomo julkaistaan omassa `valvomo/index.html`-tiedostossaan osoitteessa `/valvomo/`. Sivusto on edelleen staattinen, Jekyllillä rakennettava julkaisu, ei oma sovelluskehys tai räätälöity Actions-buildi.

Näiden havaintojen perusteella nykyinen julkaisutapa on GitHub Pagesin haarajulkaisu `main`-haaran juuresta. Pages-buildin ajoloki vahvistaa myös lähdepolun: `actions/jekyll-build-pages` sai asetuksen `source: .` (repositoriojuuri). Pages-asetusten hallintasivua ei tarvinnut muuttaa tai lukea erikseen, koska toteutunut build-ajo vahvistaa käytössä olevan lähdepolun. Nykyinen julkaisutapa ja RSS-polut säilytetään tässä kehitysvaiheessa.

## 2. Sivurakenne ja reitit

- `/` on Aiheseurainin erillinen etusivu.
- `/valvomo/` on Valvomon varsinainen osoite. Valvomon sisältö ja selainlogiikka säilyvät ennallaan; JavaScript ladataan vain Valvomon sivulla.
- Sivut käyttävät samaa Jekyll-sivupohjaa, otsaketta, navigaatiota, alatunnistetta ja CSS-tiedostoa. Nykyisessä navigaatiossa RSS-lukija ja Kehitysjono esitetään tulossa olevina, kunnes niiden omat näkymät valmistuvat.
- Vanha juuriosoite ei enää näytä Valvomoa, vaan etusivu tarjoaa suoran linkin uuteen `/valvomo/`-osoitteeseen. Erillistä uudelleenohjausta ei tehdä, koska juuri on tarkoituksella varattu sivuston etusivulle.

## Hyväksytyt tekniset ratkaisut

1. **Yksi staattinen Pages-sivusto.** Valvomo, RSS-lukija ja Kehitysjono ovat saman sivuston osioita. Nykyisiä RSS-osoitteita ei siirretä.
2. **Nykyinen julkaisutapa säilyy.** Julkaisu jatkuu `main`-haaran juuresta GitHub Pagesin hallitsemalla Jekyll-buildillä. Erillistä `gh-pages`-haaraa tai uutta Pages-deploy-workflow'ta ei oteta käyttöön vain Valvomon vuoksi.
3. **Ei erillistä status-tietokantaa eikä rinnakkaisia tilannekuvakopioita.** Valvomo lukee nykyisiä koneellisia tietolähteitä suoraan Pagesin saman alkuperän JSON-tiedostoina.
4. **Automaatiot säilyttävät kirjoitusvastuunsa.** Pääautomaatio, näytösvahti ja laatutarkistus päivittävät omia nykyisiä seurantatietojaan omien käsikirjojensa mukaisesti. Valvomon selain ei kirjoita repositorioon.
5. **Status ei saa synnyttää erillisiä committeja.** Seurantatiedot päivittyvät samassa repositoriomuutoksessa kuin automaation muu hyväksytty tulos, kun kyseinen automaatio jo päivittää seurantatilan. Valvomon lukeminen ei kirjoita mitään.
6. **Sama-origin JSON on ensisijainen selaimen datalähde.** Valvomo lukee julkaistut tiedostot Pages-osoitteesta. GitHubin julkista APIa käytetään vain tietoihin, joita nykyiset JSON-tiedostot eivät sisällä, kuten GitHub Actions -validointien ja Pages-julkaisujen ajoihin. API-kutsut rajataan, tulokset välimuistitetaan ja virhetilanteet näytetään.
7. **Ei selaimeen tunnuksia tai salaisuuksia.** Julkinen Pages-sivu käyttää vain julkista dataa ja anonyymejä lukuoikeuksia. Raakoja Actions-lokeja tai API-virheiden raakasisältöä ei julkaista.

## 3. Kanoniset tietolähteet

| Tietolähde | Vastuu | Valvomon käyttötarkoitus |
|---|---|---|
| `data/seurantatila.json` | Pääautomaation kiertotila, aihekohtaiset viimeisimmät onnistumiset, näytösvahdin tila sekä automaatio-ohjeiden versiot | Automaatiokortit, viimeisin onnistuminen, seuraava aihe ja ohjeversion tila |
| `data/lahdetarkistukset.json` | Lähdetarkistusten ajokohtaiset tulokset, tarkistetut ja tarkistamatta jääneet lähteet sekä kattavuushuomiot | Lähdetarkistuksen viimeisin tulos ja perustellut kattavuustiedot |
| `data/naytosten-muutoshistoria.json` | Näytösseurannan nykytila ja muutostapahtumat | Vain näytösseurannan historiatiedon erillisiin näkymiin, ei pääautomaation tilan lähteeksi |
| GitHub Actionsin julkinen API | Repositorion omien workflow-ajojen tila ja linkit | RSS-/dokumentaatiotestit, viikoittainen linkkitarkistus ja Pages-julkaisu |

Nykyiset `data/seurantatila.json` ja `data/lahdetarkistukset.json` ovat ensisijaiset tietolähteet. Niiden rinnalle ei luoda `status/overview.json`-, `status/runs.json`-, `status/sources.json`- tai `status/rotation.json`-kopioita: ne toistaisivat jo ylläpidettyä tietoa ja lisäisivät synkronointivirheiden sekä ylimääräisten commitien riskiä.

Myöskään `feeds/index.json` ei kuulu Valvomon tietomalliin. RSS-lukijan syötekatalogi määritellään erikseen RSS-lukijan toteutuksen yhteydessä, ja sen on perustuttava todellisiin RSS-tiedostoihin sekä niiden kanonisiin Pages-osoitteisiin.

## 4. Tietomallien versiointi ja skeemat

- `data/seurantatila.json` käyttää nykyistä `schema_version: 1` -versiota. Sen rakenne validoidaan tiedostolla `schemas/seurantatila.schema.json`.
- `data/lahdetarkistukset.json` käyttää `schema_version: 1` -versiota ja sitä validoidaan jo olemassa olevalla `schemas/lahdetarkistukset.schema.json`-tiedostolla.
- Näytösten muutoshistoria validoidaan erillisellä `schemas/naytosten-muutoshistoria.schema.json`-skeemalla.
- JSON Schema on koneellisesti tarkistettava rakenteen sopimus. `scripts/validate_feeds.py` tarkistaa seurantatilan skeeman ja lisäksi projektin semanttiset ehdot, kuten yhdeksän kiertotehtävän ja syötepolkujen vastaavuuden.
- Rakennetta muuttava laajennus kasvattaa `schema_version)-arvoa, päivittää skeeman, tuottavat automaatiot, validoinnin, dokumentaation ja testit samassa muutossarjassa. Yhteensopiva, valinnainen kenttä voidaan lisätä saman version sisällä vain, jos skeema ja tuottajat käsittelevät sitä turvallisesti.

Skeemat kuvaavat nykyisiä tallennettuja tietoja. Ne eivät väitä, että jokaisesta ajosta olisi jo saatavilla vaihekohtainen tapahtumahistoria.

## 5. Tietojen tulkinta käyttöliittymässä

Valvomon on erotettava viimeisin tunnettu onnistuminen, ajon tulos ja tiedon ajantasaisuus toisistaan.

- **Tuore:** viimeisin onnistunut tarkistus on odotetun aikataulun mukainen.
- **Vanhentunut:** viimeisin onnistuminen ylittää automaation aikataululle määritellyn tuoreusrajan.
- **Tuntematon:** onnistumisaikaa tai tarvittavaa tietoa ei ole tallennettu.
- **Virheellinen/ristiriitainen:** JSON ei lataudu tai ei vastaa skeemaa tai semanttisia ehtoja.

Alustavat tuoreusrajat, joita voidaan säätää toteutuksen yhteydessä:

| Automaation rytmi | Tuoreusraja |
|---|---:|
| Päivittäinen pääautomaatio | 36 tuntia |
| Päivittäinen näytösvahti | 36 tuntia |
| Viikoittainen laatutarkistus | 10 vuorokautta |
| Viikoittainen linkkitarkistus | 10 vuorokautta |

Puuttuva `last_successful_check` tarkoittaa tuntematonta, ei epäonnistunutta eikä käynnissä olevaa ajoa. Viimeisin onnistuminen ei myöskään todista, että uusi ajo olisi käynnissä. Käynnissä-tilaa näytetään vain, jos tuottava automaatio julkaisee siitä erikseen varmennetun tiedon. Nykyisessä seurantatiedostossa ei ole tällaista tietoa.

`data/lahdetarkistukset.json`-tiedoston `complete`, `partial` ja `failed` kuvaavat lähdetarkistuksen kattavuutta, eivät koko automaation julkaisun onnistumista. Tarkistettuja lähteitä, tarkistamatta jääneitä lähteitä ja lähderekisterin kokonaismäärää ei saa sekoittaa keskenään eikä muuttaa kattavuusprosentiksi ilman määriteltyä nimittäjää.

## 6. Julkistettavat tiedot ja rajaukset

Valvomossa saa näyttää vain toiminnan ymmärtämiseen tarvittavat tiedot:

- automaation nimi ja vastuu;
- viimeisin varmennettu onnistumisaika ja seurantajakso;
- viimeisin tulos ja seuraava kiertotehtävä;
- julkaistujen itemien ja tarkistettujen lähteiden määrät, kun ne ovat tiedossa;
- tarkistamatta jääneiden lähteiden tunnisteet ja lyhyet, siistit syyt;
- lähdekattavuuden selitteet;
- julkiset linkit repositorion workflow-ajoihin ja issueihin, kun täsmällinen linkki on olemassa.

Älä julkaise:

- käyttöoikeustokeneita, salaisuuksia, salasanoja tai ympäristömuuttujia;
- käyttäjän sähköpostia, henkilötunnisteita tai tarpeettomia henkilötietoja;
- raakoja Actions-lokeja, raakaa API-virhevastetta tai tarpeettomia sisäisiä debug-tietoja;
- väitteitä käynnissä olevasta ajosta, tarkasta vaihetilasta tai onnistumisesta, joita tietolähde ei todista.

Lähdetarkistusten syyt ovat käyttäjälle tarkoitettuja selitteitä, eivät raakaa virhelokia. Ne pidetään lyhyinä ja niistä poistetaan mahdolliset salaisuudet ennen tallentamista.

## 7. GitHub API ja välimuisti

GitHub Actionsin ajoja haetaan julkisesta repositoriosta vain Valvomon tarvitsemiin workflow-tunnisteisiin rajaten. Käyttöliittymä ei hae raakaa lokisisältöä. API-vastaukset välimuistitetaan selaimessa lyhyeksi ajaksi; alustava päivitysväli on viisi minuuttia. API-rajoituksen tai verkkovirheen aikana näytetään viimeisin onnistunut hakuaika ja selkeä virheilmoitus. Vanhaa API-tulosta ei merkitä tuoreeksi.

Valvomon ensisijainen automaatiotila ei riipu GitHub Actions -APIsta, koska pääautomaatio, näytösvahti ja laatutarkistus ovat ChatGPT:n ajoitettuja tehtäviä, eivät tämän repositorion GitHub Actions -workflown suorituksia. Actions-API kertoo vain GitHubissa suoritettavien testien, linkkitarkistuksen ja Pages-julkaisun tilan.

## 8. Toteutuksen vastuunjako

- **#29:** nykytilan kartoitus, julkaisutavan ja tietomallin päätös, skeemat ja validoinnin perusta.
- **#30:** Valvomon käyttöliittymä, tietolähteiden lukeminen, ajantasaisuuden näyttäminen, virhetilat ja testit. Jos halutaan vaihekohtainen ajoseuranta, sen tuottaminen määritellään erikseen eikä sitä päätellä nykyisistä kentistä.
- **#31:** RSS-lukijan syötekatalogi ja käyttöliittymä; se ei muuta Valvomon tietomallia.
- **#33:** lähderekisterin selaus ja kattavuuden laajennettu näkymä.

Tämä jako pitää tietolähteet yksiselitteisinä ja estää käyttöliittymää muodostumasta toiseksi, käsin ylläpidettäväksi tilatietokannaksi.

## 9. Valvomon ensimmäinen käyttöliittymä

Valvomo julkaistaan omassa `valvomo/index.html`-sivussaan osoitteessa `/valvomo/`, ja repositorion juuren `index.html` on Aiheseurainin etusivu. Molemmat käyttävät yhteistä Jekyll-sivustorunkoa (`_layouts/site.html` ja `_includes/`-osat). Tyylit ja selainlogiikka ovat `assets/`-hakemistossa. Sivusto pysyy staattisena eikä lisää palvelinta, tietokantaa tai selaimen GitHub-kirjoitusoikeuksia.

Käyttöliittymä lukee seuraavat tiedot:

- `data/seurantatila.json`: pääautomaation aihekohtaiset viimeisimmät onnistumiset ja seuraava vuoro, näytösvahdin tila sekä kolmen automaation ohjeversiot.
- `data/lahdetarkistukset.json`: viimeisimmän aiheajon lähdetarkistuksen tulos, tarkistetut lähteet ja tarkistamatta jääneiden lähteiden syyt.
- GitHub Actionsin julkinen API: viimeisimmät RSS-/dokumentaatiotestien, viikoittaisen linkkitarkistuksen ja Pages-julkaisun ajot sekä saatavilla olevat työnvaiheet.

Automaatiokorttien tuoreusrajat ovat 36 tuntia päivittäisille automaatioille ja 10 vuorokautta viikoittaiselle laatutarkistukselle. Puuttuva aikaleima näytetään tuntemattomana. Viimeisin onnistuminen ei tarkoita, että uusi ajo olisi käynnissä.

**Ajovaiheiden rajoite:** nykyiset koneelliset seurantatiedot eivät tallenna ChatGPT-automaation vaihekohtaista ajohistoriaa. Siksi Valvomo ilmoittaa tämän suoraan eikä keksi vaiheita tai päättele niitä GitHub Actions -ajoista. GitHub Actions -vaiheet näytetään vain erillisessä teknisten työnkulkujen osiossa.

GitHub API:n tulokset välimuistitetaan välilehden istunnossa enintään viideksi minuutiksi. API-virhe näytetään erillään automaatioiden tilasta; se ei muuta JSON-tietojen perusteella muodostettua tilaa. Näkymä ei hae raakoja Actions-lokeja.

Valvomon automaattiset JavaScript-testit suoritetaan komennolla `node --test tests/valvomo.test.mjs`. Sivun ja skriptin rakenne tarkistetaan CI-ajossa. Tämä ei korvaa manuaalista näppäimistö-, ruudunlukija-, suurennus- tai kontrastitestausta.