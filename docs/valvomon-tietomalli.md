# Valvomon tietomalli ja julkaisutapa

**Tila:** nykyisen Valvomon tietolähteet ja tulkintasäännöt; JSON-tiedostojen visuaalinen kokonaiskuva on dokumentissa [Tietomallit ja prosessikaaviot](tietomallit-ja-prosessit.md)  
**Päivitetty:** 2026-11-17  
**Liittyvät tehtävät:** [#29 – Pages-kartoitus ja tietomalli](https://github.com/mikknikk/aiheseurain/issues/29), [#30 – Valvomon vähimmäisversio](https://github.com/mikknikk/aiheseurain/issues/30), [#37 – ChatGPT-ajohistoria](https://github.com/mikknikk/aiheseurain/issues/37)

Tämä dokumentti määrittää Valvomon tietolähteet, julkaisutavan, tietojen tulkinnan ja julkistamisen rajat. JSON-tiedostojen keskinäiset suhteet ja lähdetietojen prosessikaaviot on kuvattu erillisessä [teknisessä tietomallioppaassa](tietomallit-ja-prosessit.md). Käyttöliittymän nykyinen toteutus ja sen tunnetut tietorajoitteet kuvataan luvussa 9.

## 1. Nykyinen GitHub Pages -julkaisu

Repositorion Pages-osoite on [https://mikknikk.github.io/aiheseurain/](https://mikknikk.github.io/aiheseurain/). Repositorio on julkinen ja sen oletushaara on `main`.

Kartoitus 16.11.2026:

- Repositorion juurihakemistossa ovat `README.md`, `index.html` (Aiheseuraimen etusivu), `valvomo/` (Valvomon sivu), `feeds/`, `data/`, `docs/`, `schemas/`, `scripts/` ja muut projektin hakemistot.
- RSS-tiedostot ovat juuren `feeds/`-hakemistossa, ja niiden kanoniset osoitteet ovat muotoa `https://mikknikk.github.io/aiheseurain/feeds/{tiedosto}.xml`.
- Ennen tiketin #83 toteutusta repositorion omissa työnkuluissa ei ollut Pages-julkaisua tekevää workflow-tiedostoa. GitHubin hallitsema `pages build and deployment` -ajo rakensi `main`-haaran juuren Jekyll-sivuston.
- Tiketin #83 ratkaisu korvaa tämän yhden Pages-julkaisupolun repositorion `.github/workflows/publish-pages.yml`-työnkululla, jotta Actions-ajon aikana muodostettu `data/kehitysjono.json` voidaan sisällyttää samaan sivustoon. Pages-asetuksen Source on vaihdettava GitHub Actionsiin käyttöönoton yhteydessä.
- Repositorion juuressa on nyt Aiheseuraimen etusivu (`index.html`) ja Valvomo julkaistaan omassa `valvomo/index.html`-tiedostossaan osoitteessa `/valvomo/`. Sivusto pysyy staattisena Jekyll-julkaisuna. Rakennus suoritetaan Actionsissa, jotta ajonaikainen Kehitysjono-aineisto voidaan sisällyttää julkaisuun.

Lähtötilanteen Pages-build käytti asetusta `source: .` (repositoriojuuri). Uusi workflow käyttää samaa Jekyll-lähdepolkua, mutta muodostaa Kehitysjonon JSON-aineiston ennen build-vaihetta. Julkaisun lähde vaihtuu GitHub Actionsiin; Pages-osoite, Jekyll-sivusto ja RSS-polut säilyvät.

## 2. Sivurakenne ja reitit

- `/` on Aiheseuraimen erillinen etusivu.
- `/valvomo/` on Valvomon varsinainen osoite. Valvomon sisältö ja selainlogiikka säilyvät ennallaan; JavaScript ladataan vain Valvomon sivulla.
- Sivut käyttävät samaa Jekyll-sivupohjaa, otsaketta, navigaatiota, alatunnistetta ja CSS-tiedostoa. RSS-lukija sijaitsee osoitteessa `/lukija/` ja kehitysjono osoitteessa `/kehitysjono/`.
- Vanha juuriosoite ei enää näytä Valvomoa, vaan etusivu tarjoaa suoran linkin uuteen `/valvomo/`-osoitteeseen. Erillistä uudelleenohjausta ei tehdä, koska juuri on tarkoituksella varattu sivuston etusivulle.

## Hyväksytyt tekniset ratkaisut

1. **Yksi staattinen Pages-sivusto.** Valvomo, RSS-lukija ja Kehitysjono ovat saman sivuston osioita. Nykyisiä RSS-osoitteita ei siirretä.
2. **Yksi Pages-julkaisupolku.** `.github/workflows/publish-pages.yml` korvaa GitHubin hallitseman branch-pohjaisen Jekyll-julkaisun. Se rakentaa saman Jekyll-sivuston ja julkaisee sen samaan Pages-osoitteeseen; erillistä `gh-pages`-haaraa tai rinnakkaista sivustoa ei luoda. Pages-asetuksen Source on GitHub Actions.
3. **Ei erillistä status-tietokantaa eikä rinnakkaisia tilannekuvakopioita.** Valvomo lukee nykyisiä koneellisia tietolähteitä suoraan Pagesin saman alkuperän JSON-tiedostoina.
4. **Automaatiot säilyttävät kirjoitusvastuunsa.** Pääautomaatio, näytösvahti ja laatutarkistus päivittävät omia nykyisiä seurantatietojaan omien käsikirjojensa mukaisesti. Valvomon selain ei kirjoita repositorioon.
5. **Vaihekohtainen ajohistoria tallennetaan erillisiin haaroihin.** ChatGPT-automaatiot päivittävät omia `run-history/*`-haarojaan ajon aikana. Nämä commitit eivät koske `main`-haaraa eivätkä synnytä PR:iä. Varsinaiset julkaisut ja seurantatilan onnistumispisteet pysyvät normaalissa PR- ja CI-prosessissa. Valvomon lukeminen ei kirjoita mitään.
6. **Julkiset JSON-tiedostot ovat ensisijaisia selaimen datalähteitä.** `main`-haaran koneelliset tilatiedostot luetaan Pages-osoitteesta ja vaihekohtainen ajohistoria GitHubin raw-sisältöosoitteista automaatiokohtaisista `run-history/*`-haaroista. GitHubin julkista APIa käytetään GitHub Actions -validointien ja Pages-julkaisujen ajoihin. Tulokset välimuistitetaan ja virhetilanteet näytetään.
7. **Ei selaimeen tunnuksia tai salaisuuksia.** Julkinen Pages-sivu käyttää vain julkista dataa ja anonyymejä lukuoikeuksia. Raakoja Actions-lokeja tai API-virheiden raakasisältöä ei julkaista.

## 3. Kanoniset tietolähteet

| Tietolähde | Vastuu | Valvomon käyttötarkoitus |
|---|---|---|
| `data/seurantatila.json` | Pääautomaation kiertotila, aihekohtaiset viimeisimmät onnistumiset, näytösvahdin tila sekä automaatio-ohjeiden versiot | Automaatiokortit, viimeisin onnistuminen, seuraava aihe ja ohjeversion tila |
| `data/lahdetarkistukset.json` | Lähdetarkistusten ajokohtaiset tulokset, tarkistetut ja tarkistamatta jääneet lähteet sekä kattavuushuomiot | Lähdetarkistuksen viimeisin tulos ja perustellut kattavuustiedot |
| `data/naytosten-muutoshistoria.json` | Näytösseurannan nykytila ja muutostapahtumat | Vain näytösseurannan historiatiedon erillisiin näkymiin, ei pääautomaation tilan lähteeksi |
| `run-history/*/history.json` | ChatGPT-automaatiot kirjaavat ajot ja vaiheet omiin haaroihinsa | Kolmen ChatGPT-automaation nykyinen ja aiempi ajohistoria |
| GitHub Actionsin julkinen API | Repositorion omien workflow-ajojen tila ja linkit | RSS-/dokumentaatiotestit, viikoittainen linkkitarkistus ja Pages-julkaisu |

Nykyiset `data/seurantatila.json` ja `data/lahdetarkistukset.json` ovat automaatioiden viimeisimmän onnistumisen ja lähdekattavuuden tietolähteet. Vaihekohtainen ajohistoria tulee erillisistä `run-history/*`-haaroista, eikä sitä kopioida `main`-haaran JSONiin. Niiden rinnalle ei luoda `status/overview.json`-, `status/runs.json`-, `status/sources.json`- tai `status/rotation.json`-kopioita: ne toistaisivat jo ylläpidettyä tietoa ja lisäisivät synkronointivirheiden sekä ylimääräisten commitien riskiä.

Myöskään `feeds/index.json` ei kuulu Valvomon tietomalliin. RSS-lukijan syötekatalogi määritellään erikseen RSS-lukijan toteutuksen yhteydessä, ja sen on perustuttava todellisiin RSS-tiedostoihin sekä niiden kanonisiin Pages-osoitteisiin.

## 4. Tietomallien versiointi ja skeemat

- `data/seurantatila.json` käyttää nykyistä `schema_version: 1` -versiota. Sen rakenne validoidaan tiedostolla `schemas/seurantatila.schema.json`.
- `data/lahdetarkistukset.json` käyttää `schema_version: 1` -versiota ja sitä validoidaan jo olemassa olevalla `schemas/lahdetarkistukset.schema.json`-tiedostolla.
- Näytösten muutoshistoria validoidaan erillisellä `schemas/naytosten-muutoshistoria.schema.json`-skeemalla.
- JSON Schema on koneellisesti tarkistettava rakenteen sopimus. `scripts/validate_feeds.py` tarkistaa seurantatilan skeeman ja lisäksi projektin semanttiset ehdot, kuten yhdeksän kiertotehtävän ja syötepolkujen vastaavuuden.
- Rakennetta muuttava laajennus kasvattaa `schema_version`-arvoa, päivittää skeeman, tuottavat automaatiot, validoinnin, dokumentaation ja testit samassa muutossarjassa. Yhteensopiva, valinnainen kenttä voidaan lisätä saman version sisällä vain, jos skeema ja tuottajat käsittelevät sitä turvallisesti.

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

Puuttuva `last_successful_check` tarkoittaa tuntematonta, ei epäonnistunutta eikä käynnissä olevaa ajoa. Viimeisin onnistuminen ei todista uuden ajon käynnissäoloa. Käynnissä-tila näytetään vain, jos erilliseen ajohistoriahaaraan on kirjattu tuore `running`-tila. Vanhentunut `running` näytetään mahdollisesti keskeytyneenä, ei käynnissä olevana.

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

Kehitysjono on poikkeus Valvomon selaimen suorista GitHub API -luvuista: se ei tee selainpyyntöjä Issues- tai riippuvuusrajapintoihin. GitHub Actions muodostaa täydellisen `data/kehitysjono.json`-aineiston, joka julkaistaan Pagesissa. Aineiston rakenne, käynnistimet, 15 minuutin varmistusajo, täydellisyysvaatimukset ja paikallinen välimuisti kuvataan ensisijaisesti [Kehitysjonon aineisto-ohjeessa](kehitysjonon-aineisto.md).

GitHub Actionsin ajoja haetaan julkisesta repositoriosta vain Valvomon tarvitsemiin workflow-tunnisteisiin rajaten. Käyttöliittymä ei hae raakaa lokisisältöä. API-vastaukset välimuistitetaan selaimessa lyhyeksi ajaksi; alustava päivitysväli on viisi minuuttia. API-rajoituksen tai verkkovirheen aikana näytetään viimeisin onnistunut hakuaika ja selkeä virheilmoitus. Vanhaa API-tulosta ei merkitä tuoreeksi.

Valvomon ensisijainen automaatiotila ei riipu GitHub Actions -APIsta, koska pääautomaatio, näytösvahti ja laatutarkistus ovat ChatGPT:n ajoitettuja tehtäviä, eivät tämän repositorion GitHub Actions -workflown suorituksia. Actions-API kertoo vain GitHubissa suoritettavien testien, linkkitarkistuksen ja Pages-julkaisun tilan.

## 8. Toteutuksen vastuunjako

- **#29:** nykytilan kartoitus, julkaisutavan ja tietomallin päätös, skeemat ja validoinnin perusta.
- **#30:** Valvomon ensimmäinen käyttöliittymä, koneellisten tietolähteiden lukeminen ja testit.
- **#37:** ChatGPT-automaatioiden ajohistoriahaarojen tietomalli, vaihekirjaukset, Valvomon ajohistorianäkymä ja testit.
- **#31:** RSS-lukijan syötekatalogi ja käyttöliittymä; se ei muuta Valvomon tietomallia.
- **#33:** lähderekisterin selaus ja kattavuuden laajennettu näkymä.

Tämä jako pitää tietolähteet yksiselitteisinä ja estää käyttöliittymää muodostumasta toiseksi, käsin ylläpidettäväksi tilatietokannaksi.

## 9. Valvomon ensimmäinen käyttöliittymä

Valvomo julkaistaan omassa `valvomo/index.html`-sivussaan osoitteessa `/valvomo/`, ja repositorion juuren `index.html` on Aiheseuraimen etusivu. Molemmat käyttävät yhteistä Jekyll-sivustorunkoa (`_layouts/site.html` ja `_includes/`-osat). Tyylit ja selainlogiikka ovat `assets/`-hakemistossa. Sivusto pysyy staattisena eikä lisää palvelinta, tietokantaa tai selaimen GitHub-kirjoitusoikeuksia.

Käyttöliittymä lukee seuraavat tiedot:

- `data/seurantatila.json`: pääautomaation aihekohtaiset viimeisimmät onnistumiset ja seuraava vuoro, näytösvahdin tila sekä kolmen automaation ohjeversiot.
- `run-history/{main-automation,screening-watch,quality-check}/history.json`: ChatGPT-automaatioiden ajot ja vaihekohtaiset tilat.
- `data/lahdetarkistukset.json`: viimeisimmän aiheajon lähdetarkistuksen tulos, tarkistetut lähteet ja tarkistamatta jääneiden lähteiden syyt.
- `data/kehitysjono.json`: Actionsissa GitHub Issues -tietojen ja natiivien riippuvuuksien pohjalta muodostettu, vain täydellisenä julkaistava Kehitysjonon aineisto.
- GitHub Actionsin julkinen API: viimeisimmät RSS-/dokumentaatiotestien, viikoittaisen linkkitarkistuksen ja Pages-julkaisun ajot sekä saatavilla olevat työnvaiheet.

Automaatiokorttien tuoreusrajat ovat 36 tuntia päivittäisille automaatioille ja 10 vuorokautta viikoittaiselle laatutarkistukselle. Puuttuva aikaleima näytetään tuntemattomana. Viimeisin onnistuminen ei tarkoita, että uusi ajo olisi käynnissä.

**Ajovaiheiden lähde:** ChatGPT-automaatiot kirjaavat ajot ja vaiheet omiin `run-history/*`-haaroihinsa. Valvomo näyttää vain näistä tiedostoista luetun, skeeman mukaisen ja riittävän tuoreen tiedon. GitHub Actions -vaiheet näytetään edelleen erillisessä teknisten työnkulkujen osiossa. Puuttuva historiatiedosto tai vanhentunut ajo ei muutu käynnissä-tilaksi.

GitHub API:n tulokset välimuistitetaan välilehden istunnossa enintään viideksi minuutiksi. API-virhe näytetään erillään automaatioiden tilasta; se ei muuta JSON-tietojen perusteella muodostettua tilaa. Näkymä ei hae raakoja Actions-lokeja. Kehitysjonon oma aineisto muodostetaan palvelinpuolella Actionsissa; selaimen paikallinen välimuisti on vain varajärjestely.

Valvomon automaattiset JavaScript-testit suoritetaan komennolla `node --test tests/valvomo.test.mjs`. Sivun ja skriptin rakenne tarkistetaan CI-ajossa. Tämä ei korvaa manuaalista näppäimistö-, ruudunlukija-, suurennus- tai kontrastitestausta.

## 10. Ajohistorian tietolähteet

Valvomo lukee kolmen automaation julkiset `history.json`-tiedostot suoraan niiden erillisistä Git-haaroista. Lukeminen käyttää vain GitHubin raw-sisältöosoitteita eikä selaimessa ole tunnuksia tai kirjoitusoikeuksia. Ajohistoria validoidaan skeemaa ja automaatiotunnistetta vasten. Jokaisesta haarasta näytetään enintään 30 viimeisintä ajoa; Gitin commit-historia säilyttää aiemmat versiot. Vanhentuneen `running`-merkinnän tila näytetään mahdollisesti keskeytyneenä. Tarkat rajat ovat dokumentissa [ChatGPT-automaatioiden ajohistoria](ajohistoria.md).

## 11. Aihekohtaisten seuraavien päivitysten arviot

Valvomo arvioi kunkin yhdeksän aihekierroksen seuraavan käsittelyajan seuraavien tietojen perusteella:

- `docs/tehtavajono.md` määrittää kiinteän aihejärjestyksen ja päivittäisen klo 12.00 Europe/Helsinki -käynnistysajan.
- `data/seurantatila.json` -tiedoston `rotation.next_task` osoittaa jonon seuraavan tehtävän. Muiden aiheiden arvioidut ajat saadaan laskemalla päivittäiset vuorot tästä kohdasta eteenpäin.
- Seurantatiedoston `updated_at` kertoo, kuinka tuoreeseen jonotietoon arvio perustuu. Yli 36 tuntia vanhasta tai virheellisestä tiedosta ei muodosteta kellonaikoja.

Aika lasketaan selaimessa aikavyöhykkeen `Europe/Helsinki` mukaan. Kesä- ja talviaika huomioidaan erikseen; selaimen käyttäjän oma aikavyöhyke ei muuta tulosta. Arvio on seuraava suunniteltu käsittelyvuoro, ei vahvistus siitä, että automaatio käynnistyy tai valmistuu kyseisenä aikana.

Jos jonon seuraavan tehtävän viimeisin tulos on `failed` tai `partial`, Valvomo arvioi vain kyseisen tehtävän seuraavan uusintayrityksen. Myöhempien aiheiden ajat jätetään tuntemattomiksi, koska epäonnistunut vuoro voi siirtää koko loppujonoa. Puuttuva, vanhentunut tai virheellinen jonotieto tuottaa samoin selkeän epävarmuusviestin kellonajan sijasta.

Näytösvahti ei kuulu yhdeksän aiheen kiertoon. Sen koneellinen tieto kertoo rytmin olevan päivittäinen, mutta julkaistussa seurantatilassa ei ole tarkkaa kellonaikaa. Valvomo näyttää siksi vain tiedon päivittäisestä rytmistä eikä keksi näytösvahdille kellonaikaa.

Aihekohtaisten arvioaikojen laskenta on käyttöliittymän johdettua tietoa eikä tarvitse erillistä aikataulutietokantaa. Reaaliaikainen käynnissäolo ja vaihehistoria saadaan kuitenkin vain tiketin #37 mukaisista automaatiokohtaisista ajohistoriahaaroista. Näkymä ei päättele ajon etenemistä aikataulusta tai GitHub Actions -työnkuluista.
