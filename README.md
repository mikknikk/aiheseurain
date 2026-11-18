# Aiheseurain – yhdeksän tehtävän seurantakierto

Aiheseurain on henkilökohtainen, moniaiheinen tiedonkeruu- ja seurantapalvelu. Tämä repositorio ylläpitää yhdeksää erillistä seurantatehtävää yhdessä kiertojonossa. Yksi automaatio käynnistyy päivittäin klo 12.00 Europe/Helsinki ja käsittelee kullakin ajolla vain yhden tehtävän. Yhdeksän tehtävän kierto tarkoittaa, että kukin aihe tarkistetaan normaalisti noin yhdeksän päivän välein. Intialaisen elokuvan uutisraportti on jonon tehtävä 9. Intialaisten elokuvien näytösseuranta on erillisen päivittäisen näytösvahdin vastuulla.

GitHub Pagesin etusivu on [Aiheseurain](https://mikknikk.github.io/aiheseurain/). [Valvomo](https://mikknikk.github.io/aiheseurain/valvomo/) näyttää automaatioiden viimeisimmät varmennetut tilat, aihekierroksen ja repositorion tekniset työnkulut. [RSS-lukija](https://mikknikk.github.io/aiheseurain/lukija/) kokoaa kaikki kymmenen syötettä yhteen aikajärjestykseen ja mahdollistaa syötekohtaisen suodatuksen. [Kehitysjono](https://mikknikk.github.io/aiheseurain/kehitysjono/) näyttää GitHub Issues -tehtävät tilasarakkeissa, niiden GitHubiin kirjatut riippuvuudet sekä saavutettavan listanäkymän. Valvomo, RSS-lukija ja Kehitysjono ovat vain luku -näkymiä.

Dokumentaatioon tutustuvan kannattaa aloittaa [Aiheseuraimen dokumentaation lukupolusta](docs/aloitus-ja-lukujarjestys.md). Järjestelmän kerrokset, itsenäiset aihe- ja prosessimoduulit, tietovirrat ja teknologioiden vaihdettavuus kuvataan [järjestelmäarkkitehtuurissa](docs/jarjestelmaarkkitehtuuri.md). Lukupolku etenee yleiskuvasta käytännön toimintaan, lähteisiin, JSON-tietomalleihin, verkkosivustoon ja ylläpitoon.

## Hakemistorakenne

- `index.html` – Aiheseuraimen etusivu; `valvomo/index.html` – Valvomon sivu osoitteessa `/valvomo/`; `lukija/index.html` – RSS-lukijan sivu osoitteessa `/lukija/`; `kehitysjono/index.html` – GitHub Issues -kanban osoitteessa `/kehitysjono/`; `_layouts/`, `_includes/` ja `assets/` – yhteinen sivustorunko ja käyttöliittymän resurssit.
- `feeds/` – kaikki kymmenen RSS-syötettä (yhdeksän aihekierrossa ja yksi erilliselle näytövahdille).
- `docs/` – suomenkieliset seuranta-, lähde-, tekniset tietomalli-, prosessi-, ohje- ja saavutettavuusdokumentit. RSS-julkaisujen tarkistusportti on kuvattu tiedostossa [docs/julkaisuportti.md](docs/julkaisuportti.md), ja julkaisun pysyvä manifesti, Pages-takaisinluku sekä virherajat tiedostossa [docs/rss-julkaisun-palautuminen.md](docs/rss-julkaisun-palautuminen.md). Erillisen RSS-julkaisurepositorion tavoitearkkitehtuuri ja vaiheittainen siirtymä kuvataan tiedostossa [docs/rss-julkaisurepositorio.md](docs/rss-julkaisurepositorio.md); se ei muuta nykyistä tuotantojulkaisua. Ihmiselle tarkoitettu vaiheittainen lukupolku on tiedostossa [docs/aloitus-ja-lukujarjestys.md](docs/aloitus-ja-lukujarjestys.md); järjestelmän kerrokset ja tekninen arkkitehtuuri ovat tiedostossa [docs/jarjestelmaarkkitehtuuri.md](docs/jarjestelmaarkkitehtuuri.md); JSON-tiedostojen yksityiskohtaiset suhteet ovat tiedostossa `docs/tietomallit-ja-prosessit.md`.
- `prompts/` – automaatioiden asetuksiin kopioitavat kanoniset käynnistyskehotteet `.txt`-tiedostoina sekä niiden ylläpito-ohje.
- `data/feed-catalog.json` – RSS-lukijan ja validoinnin yhteinen kymmenen syötteen luettelo; `data/source-catalog.json` – kaikkien lähteiden yhteiset perustiedot ja A–D-luokka kerran; `data/sources/*.json` – kymmenen tehtäväkohtaista lähdekäyttörekisteriä; `data/lahdetarkistukset.json` – ajokohtainen lähdekattavuusloki; `data/module-registry.json` – kymmenen nykyisen aihe- ja prosessimoduulin rekisteri; kaikki merkinnät ovat toistaiseksi inactive-tilassa; `data/target-registry.json` ja `data/targets/*.json` – moduuleista erotetut seurantakohteet; `data/publication-registry.json` ja `data/publications/*.json` – julkaisukohteet; `data/publication-routing.json` – havaintojen ja julkaisukohteiden välinen reititys (tuotantorekisteri ja reititys ovat tyhjiä). `data/provider-routing.json` – tekninen palvelureititys, joka on tyhjä eikä aktivoi palveluntarjoajia.
- `modules/` – kymmenen nykyisen seurannan itsenäiset koneellisesti validoitavat moduulimääritykset; näytösvahtimoduulilla on lisäksi oma tapahtumatyypin määritystiedosto. Kaikki rekisterimerkinnät ovat inactive-tilassa.
- `schemas/` – koneellisten lähdetietojen, julkaisulaadun portin, näytöshistorian, Kehitysjonon, seurantamoduulien, seurantakohteiden, kohderaporttien, julkaisukohteiden, niiden rekisterien ja julkaisureitityksen skeemat.
- `scripts/module_registry.py`, `scripts/validate_module_registry.py` ja `scripts/validate_module_migration.py` – lataavat moduulirekisterin, validoivat määritykset ja tarkistavat nykyisten lähderekisterien vastaavuuden. `scripts/module_state.py` käsittelee moduulikohtaisia checkpoint-siirtymiä ja `scripts/validate_module_state.py` tarkistaa niiden historian ja viitteet. `scripts/provider_contracts.py` ja `scripts/provider_router.py` määrittelevät vaihdettavat AI- ja tutkimuspalvelut. `scripts/publication_journal.py` tarjoaa moduuliorkestroinnin paikallisen manifestisopimuksen. `scripts/rss_publication_manifest.py` tallentaa RSS-julkaisun ehdokasmanifestin GitHub Deployments -historiaan ennen Pages-julkaisua ja varmentaa kaikki julkiset syötteet takaisinluvulla. `scripts/module_orchestrator.py` koordinoi moduulisuorituksen elinkaaren ja määrittelee kohdekohtaisen `TargetReport`-tuloksen. `scripts/publication_routing.py` ratkaisee kohderaporttien RSS-julkaisureitit. `scripts/target_execution.py` lataa moduulin seurantakohteet ja ajaa ne erillisissä suoritusympäristöissä. `scripts/module_run_adapters.py` sisältää paikalliset SHA-tarkistetut tallennus-, ajotulos- ja eristetyn RSS-julkaisun testisovittimet. Elokuvahavaintojen ja kriteerikohtaisten jatkotoimien malli on eriytetty tiedostoihin `scripts/movie_observations.py`, `scripts/movie_actions.py` ja `scripts/movie_criteria.py`. `scripts/event_watch.py` käsittelee yleisiä tapahtumahavaintoja ja `scripts/event_watch_adapters.py` sovittaa näytöshavainnot yleiseen malliin vain muistissa. `docs/seurantamoduulirekisteri.md`, `docs/tapahtumavahti.md`, `docs/seurantakohteet-ja-julkaisukohteet.md` ja `docs/moduulisiirtyman-toteutus.md` kuvaavat kyvykkyydet ja migraation. `scripts/validate_target_publication.py` tarkistaa moduuli-, kohde-, julkaisu- ja reititysviitteiden eheyden.
- `scripts/build_kanban_data.mjs`, `scripts/validate_kanban_data.py` ja `.github/workflows/publish-pages.yml` – muodostavat ja validoivat GitHub Issues -tietojen sekä natiivien riippuvuuksien täydellisen Kehitysjono-aineiston ja julkaisevat saman Jekyll/Pages-sivuston.
- `docs/tehtavajono.md` – yhdeksän tehtävän kiertojärjestys ja seuraava vuoro; yleiset raportointisäännöt ovat docs/seuranta.md:ssä.
- `docs/kehitysjonon-aineisto.md` – Kehitysjonon johdetun JSON-aineiston rakenne, päivityskäynnistimet, virhetilat ja Pages-julkaisun käyttöönotto.
- `README.md` – repositorion aloitussivu ja kokonaiskuva.

## Syötteet

Kaikkien syötteiden ensisijainen julkinen jakeluosoite on GitHub Pages. Käytä RSS-lukijoissa ja automaatioiden julkaisemissa linkeissä `https://mikknikk.github.io/aiheseurain/feeds/{syötetiedosto}.xml`-osoitetta. `raw.githubusercontent.com` ei ole julkinen kanoninen RSS-osoite.

| Aihe | RSS-tiedosto | RSS-osoite (GitHub Pages) |
|---|---|---|
| J. R. R. Tolkien | [tolkien.xml](feeds/tolkien.xml) | https://mikknikk.github.io/aiheseurain/feeds/tolkien.xml |
| Taylor Swift | [taylor-swift.xml](feeds/taylor-swift.xml) | https://mikknikk.github.io/aiheseurain/feeds/taylor-swift.xml |
| Saint Dr. Gurmeet Ram Rahim Singh Ji Insan | [gurmeet-ram-rahim-singh.xml](feeds/gurmeet-ram-rahim-singh.xml) | https://mikknikk.github.io/aiheseurain/feeds/gurmeet-ram-rahim-singh.xml |
| Muumit | [muumit.xml](feeds/muumit.xml) | https://mikknikk.github.io/aiheseurain/feeds/muumit.xml |
| Wakaliwood | [wakaliwood.xml](feeds/wakaliwood.xml) | https://mikknikk.github.io/aiheseurain/feeds/wakaliwood.xml |
| Euroviisut ja kansalliset karsinnat | [euroviisut.xml](feeds/euroviisut.xml) | https://mikknikk.github.io/aiheseurain/feeds/euroviisut.xml |
| Sompote Sands | [sompote-sands.xml](feeds/sompote-sands.xml) | https://mikknikk.github.io/aiheseurain/feeds/sompote-sands.xml |
| Shakkidraamat | [shakkidraamat.xml](feeds/shakkidraamat.xml) | https://mikknikk.github.io/aiheseurain/feeds/shakkidraamat.xml |
| Intialaisen elokuvan uutisraportti | [intialaiset-elokuvat.xml](feeds/intialaiset-elokuvat.xml) | https://mikknikk.github.io/aiheseurain/feeds/intialaiset-elokuvat.xml |
| Intialaisten elokuvien näytökset Suomessa | [intialaisten-elokuvien-naytokset.xml](feeds/intialaisten-elokuvien-naytokset.xml) | https://mikknikk.github.io/aiheseurain/feeds/intialaisten-elokuvien-naytokset.xml |

Kahdeksan muuta aihekierroksen syötettä voivat olla tyhjiä, jos uusia olennaisia uutisia ei löydy. Intialaisen elokuvan kaksi syötettä siirrettiin aiemmasta repositoriosta historiallisine itemeineen. Yhteenkään syötteeseen ei lisätä keinotekoisia “ei uutisia” -artikkeleita.

## Pääautomaation lukujärjestys ja tehtäväkierto

Kaikkia nykyisiä ja tulevia automaatioita koskeva ajastusten, asetusten ja kohdekeskustelujen suojaus on määritelty [automaatioiden hallintaperiaatteissa](docs/automaation-hallintaperiaatteet.md). Automaation suorittaminen ei anna lupaa muuttaa ChatGPT:n ajastettua tehtävää tai sen kohdekeskustelua. GitHubin dokumentaatio ja ChatGPT:n tehtäväasetukset ovat erillisiä; GitHub-muutos ei päivitä tehtäväasetuksia automaattisesti.


Pääautomaation varsinainen tehtävä- ja toimintakuvaus on versionhallittu tiedostossa [docs/paaautomaation-ohje.md](docs/paaautomaation-ohje.md). ChatGPT-automaation asetuksissa käytettävän lyhyen käynnistyskehotteen kanoninen teksti on `prompts/paauutisseuranta.txt`-tiedostossa. Kopioi tiedoston sisältö automaation asetuksiin; pidä tiedosto ja asetuksiin tallennettu kehote täsmälleen samoina. Ohjeversion tunniste ja viimeisimmän onnistuneen ajon käyttämä versio tallennetaan `data/seurantatila.json`-tiedoston `automation_instructions`-osioon. Käynnistyskehotteen tunniste tarkistetaan lisäksi `startup_prompt_id`-kenttää vasten; vanhentunut tai väärä kehote keskeyttää ajon. Jos käsikirjan ja JSONin nykyversiot eivät täsmää, pääautomaatio keskeyttää ajon.

Myös erillisellä näytövahdilla ja viikoittaisella laatutarkistuksella on omat GitHubissa ylläpidettävät käsikirjansa:
- Näytösvahti: `docs/intialaisten-elokuvien-naytosseuranta.md`. Ohjeversion tunniste, käynnistyskehotteen tunniste ja viimeisin onnistunut käyttöaika ovat `separate_screening_watch.automation_instructions`-osiossa.
  Näytösvahti käsittelee tilapäiset virheet rajatuilla uusintayrityksillä; epäonnistunut ajo säilyttää viimeisimmän onnistumisen tarkistuspisteen, ja seuraava ajo palauttaa koko väliin jääneen seurantajakson.
- Laatutarkistus: `docs/laatutarkistuksen-ohje.md`. Ohjeversion tunniste, käynnistyskehotteen tunniste ja viimeisin onnistunut käyttöaika ovat `quality_check_instructions`-osiossa. Laatutarkistus on muuten vain luku -auditointi; se saa päivittää ainoastaan nämä kaksi onnistuneen ajon metatietokenttää.

Pääautomaatio käsittelee päivittäisellä ajollaan vain yhtä tehtäväjonon aihetta. Lue ennen hakua seuraavat tiedostot tässä järjestyksessä:

1. `README.md` – repositorion yleiskuva, tiedostojen vastuut ja julkaisuperiaatteet.
2. `docs/paaautomaation-ohje.md` – pääautomaation täydellinen, versioitu toimintakäsikirja.
3. `docs/tehtavajono.md` – kiertojärjestys ja seuraava tehtävä.
4. `docs/seuranta.md` – tehtäväkohtaiset seurantajaksot, aiempi uutishistoria, koneellinen seurantatila ja raportointisäännöt.
5. `docs/lahteet.md`, `docs/luotettavuusluokitus.md`, `docs/tietomallit-ja-prosessit.md`, `data/source-catalog.json` ja valitun tehtävän `data/sources/{task_id}.json` – yleiset lähdeperiaatteet, luotettavuusluokat, JSON-tietomallien suhteet, yhteiset lähdetiedot ja tehtäväkohtaiset lähdekäytöt.
6. `docs/saavutettavuus.md` – kaikkia julkaisuja koskevat saavutettavuusperiaatteet.
7. `docs/kehityskaytannot.md` – koodimuutoksia koskevat ylläpitokäytännöt; lue ja noudata niitä aina, jos muutat skriptejä.
8. Valitun tehtävän aihekohtaiset ohjeet ja seurantaloki. Tehtävässä 9 lue lisäksi kokonaan `docs/intialaisen-elokuvan-ohje.md`, `docs/intialaisen-elokuvan-uutiset.md`, `docs/intialaisen-elokuvan-lahteet.md` ja `docs/intialaisen-elokuvan-seuranta.md`.

Lue ennen julkaisua kaikki kymmenen RSS-tiedostoa kokonaan tai hae niiden kaikki itemit. Näytösfeed luetaan vain historian säilyttämiseksi; älä tee näytöshakuja tai muuta näytösfeedin sisältöä. Tarkista kaikkien kymmenen syötteen GUIDien yksilöllisyys muuttamatta muiden tehtävien sisältöä. Näytösvahti ja sen dokumentit ovat erillisen automaation vastuulla; pääautomaatio ei tee näytöshakuja eikä muuta näytösfeedin tai näytöshistorian sisältöä. Näytöshistorian tietomalli on dokumentoitu tiedostossa `docs/naytoshistorian-rakenne.md`, ja se kuuluu näytösvahdin lukemistoon.

Dokumenttien vastuut ja tarkempi lukujärjestys on koottu tämän README:n **Tiedostojen vastuut** -osioon. Aiheiden, syötteiden tai automaatioiden muuttuessa päivitä kaikki niitä koskevat ensisijaiset dokumentit ja niitä tarkistavat testit.

## Dokumentaation ajantasaisuuden loppukatselmus

Aina kun mitä tahansa dokumentaatiotiedostoa muutetaan tai lisätään, tee ennen työn päättämistä koko dokumentaation ajantasaisuuden katselmus:

1. Lue muutoksen jälkeen README.md, docs/seuranta.md ja docs/lahteet.md kokonaan sekä kaikki muut aiheeseen liittyvät dokumentit.
2. Tarkista, että kaikki aihe-, tiedosto-, RSS-URL-, aikataulu-, lähde- ja toimintatapatiedot ovat keskenään yhdenmukaisia. Esimerkiksi aiheiden tai syötteiden lisäys tai poisto päivitetään kaikkialle, missä niitä luetellaan.
3. Etsi vanhentuneet, päällekkäiset, ristiriitaiset ja puuttuvat tiedot myös muista dokumenteista; älä tyydy tarkistamaan vain juuri muokattua kohtaa.
4. Korjaa havaitut ristiriidat saman muutossarjan yhteydessä. Jos jokin tieto on tarkoituksella erilainen eri tiedostoissa, selitä ero.
5. Hae kaikki muutetut dokumentit GitHubista takaisin ja varmista, että tallennettu sisältö vastaa tarkistettua versiota.

Dokumentaatiomuutosta ei pidetä valmiina ennen tätä loppukatselmusta.

## Julkaisuperiaatteet

- Pidä aiheet täysin erillään: kuhunkin RSS-syötteeseen vain kyseisen aiheen uutiset.
- Julkaise vain uutta tai olennaisesti muuttunutta, lähteillä varmennettua tietoa.
- Yhdistä saman tapahtuman useat lähteet yhdeksi RSS-artikkeliksi.
- Älä toista muuttumatonta taustatietoa, vanhoja huhuja tai fanispekulaatiota.
- Kirjoita uutisartikkelit suomeksi. Lisää otsikko, julkaisu- ja tapahtumapäivä silloin kun ne ovat tiedossa, lähdelinkit sekä tiedon luotettavuuden luokitus.
- Suosi ensisijaisia lähteitä. Merkittävät väitteet pyri varmistamaan kahdesta toisistaan riippumattomasta toimituksellisesta lähteestä.
- Jos julkaisijan oma haku ei toimi, hae hakukoneella rajauksella kuten `site:yle.fi` tai `site:hs.fi`. Avaa ja tarkista alkuperäinen juttu; hakutuloskatkelma ei yksin riitä.
- Säilytä aiemmat RSS-artikkelit ja niiden GUID-tunnisteet. Päivitä `lastBuildDate` vain, kun syötettä muutetaan.
- Tarkista jokaisen muutoksen jälkeen XML:n kelvollisuus, GUID-tunnisteiden yksilöllisyys, vanhojen artikkeleiden säilyminen ja aiherajaus.
- Älä koskaan väitä tiedoston päivittyneen ennen kuin GitHub-kirjoitus ja muutoksen jälkeinen takaisinluku on onnistunut.

## Kehityksen tilanne

Ajantasainen lista toteutetuista parannuksista ja avoimista kehityskohteista on tiedostossa [docs/kehityskohteet.md](docs/kehityskohteet.md). Päivitä listaa aina kehitystyön edetessä. Koko sivuston ja kehitysjärjestelmän tavoitekuvaus on dokumentissa [docs/kehityssuunnitelma.md](docs/kehityssuunnitelma.md). Kehitystehtävät ja niiden tilat ylläpidetään GitHub Issues -tiketteinä.

## Tiedostojen vastuut

Kullakin dokumentilla on yksi ensisijainen vastuu. Muut dokumentit viittaavat siihen sen sijaan, että kopioisivat saman säännön kokonaisuudessaan.

- `README.md`: repositorion yleiskuva, hakemistorakenne, RSS-syötteiden luettelo, automaatioiden työnjako ja dokumentaation lukujärjestys.
- `docs/paaautomaation-ohje.md`: pääautomaation täydellinen tehtävä- ja toimintakuvaus, raporttikohtainen julkaisulaadun portti sekä sen versionhallinnan säännöt.
- `docs/julkaisuportti.md`: jokaisen RSS-raportin toimituksellinen tarkistuslista, automaattisten testien rajat ja julkaisupäätöksen menettely.
- `docs/automaation-hallintaperiaatteet.md`: kaikkia nykyisiä ja tulevia automaatioita koskeva ajastusten, asetusten ja kohdekeskustelujen käyttäjän valtuutukseen perustuva suojaus.
- `prompts/README.md` ja `prompts/*.txt`: automaatioiden asetuksiin kopioitavat käynnistyskehotteet ja niiden ylläpitomenettely. Tekstit säilytetään sellaisinaan.
- `docs/intialaisten-elokuvien-naytosseuranta.md`: näytösvahdin täydellinen, versioitu tehtävä- ja toimintakuvaus.
- `docs/laatutarkistuksen-ohje.md`: viikoittaisen laatutarkistuksen täydellinen, versioitu tehtävä- ja toimintakuvaus.
- `docs/tehtavajono.md`: yhdeksän tehtävän kiertojärjestys, seuraava vuoro ja vuoron siirtämisen ehdot. Ei yleisiä raportointi- tai koodauskäytäntöjä.
- `docs/seuranta.md`: tehtäväkohtaiset seurantajaksot, onnistuneiden tarkistusten tila, uutistapahtumien historia ja luotettavuusluokat.
- `docs/lahteet.md`: yleiset lähdeperiaatteet ja kaikkien yhdeksän aihekierroksen lähteiden lähtöpisteet. Luettelo ei ole suljettu.
- `docs/luotettavuusluokitus.md`: lähteiden yleiset A–D-luokat, väitekohtaiset varmennustasot ja lähderiippuvuuksien arviointi.
- `docs/saavutettavuus.md`: kaikkien julkaisujen ja Markdown-dokumentaation saavutettavuustavoitteet ja testausperiaatteet.
- `docs/kehitysjonon-aineisto.md`: Kehitysjonon GitHub Issues -pohjaisen aineiston muodostus, julkaisu ja virheistä palautuminen.
- `docs/kehityskaytannot.md`: dokumentaation luokat ja kirjoitustavat, käynnistyskehotteiden ylläpito, skriptien kommentointi, koodin ylläpito ja muutosten tarkistus.
- `docs/kehityskohteet.md`: toteutettujen parannusten tilanne ja avoin kehitystyö.
- `docs/kehityssuunnitelma.md`: Valvomon, RSS-lukijan ja GitHub Issues -pohjaisen kehitysjono-osion tavoitearkkitehtuuri, tietomalliehdotukset, turvallisuus- ja saavutettavuusvaatimukset sekä kehityksen toimintamalli.
- `docs/jarjestelmaarkkitehtuuri.md`: järjestelmäriippumaton toimintamalli, kolmen kerroksen vastuut, nykyinen tekninen toteutus, tavoitearkkitehtuuri, tietovirrat, nykytilan ja tavoitetilan erot, siirtymävaiheet sekä teknologioiden vaihdettavuus.
- `docs/moduulisiirtyman-inventaario.md`: nykyisten yhdeksän uutisaiheen ja erillisen näytösvahdin moduuli-inventaario, tiedostojen siirtokartta, omistajuusrajat, migraation riippuvuudet ja palautusmenettely.
- `docs/moduulisiirtyman-toteutus.md`: kymmenen moduulimäärityksen sisältö, lähdeviitteiden vastaavuus, passiivinen rekisteröinti, validointi, yhteensopivuus ja palautus.
- `docs/moduulikohtainen-tila.md`: moduulikohtaisen checkpointin, ajohistorian, GUID- ja tapahtumaviitteiden sekä idempotentin päivityksen säännöt.
- `docs/palveluadapterit.md`: AIProcessor- ja ResearchProvider-sopimukset, tekninen reititys, kustannusrajat, virheiden uusinta ja tietoturvallinen auditointi.
- `docs/moduuliorchestrointi.md`: moduulisuorituksen pyyntö- ja tulossopimukset, elinkaari, varjotila, tuotannon hyväksyntäportti, paikalliset testisovittimet ja palautus.
- `docs/elokuvahavainnot-ja-jatkotoimet.md`: elokuvatasoisen havaintorekisterin suhde näytöstapahtumiin, elokuvan tunnisteet, kriteeriosumat, toimintojen outbox ja Discord-liitännän turvarajat.
- `docs/elokuvahakukriteerit.md`: käyttäjän hyväksymien elokuvahakukriteerien versiointi, ehto-operaattorit, poissulut ja #66:n toimintoviitteet.
- `docs/seurantamoduulin-tietosopimus.md`: seurantamoduulin kanoninen tietosopimus, versiointi, yhteensopivuus ja elinkaari.\n- `docs/seurantakohteet-ja-julkaisukohteet.md`: seurantamoduulien, seurantakohteiden ja julkaisukohteiden erilliset vastuut sekä havaintojen reitityssopimus.
- `docs/github-riippuvuuksien-hallinta.md`: GitHubin natiivien issue-riippuvuuksien automaattisen lisäämisen ja erikseen pyydetyn poistamisen toimintatapa, pyyntölohko ja oikeusrajaukset.
- `docs/ajohistoria.md`: ChatGPT-automaatioiden erillisten ajohistoriahaarojen tietomalli ja kirjausmenettely.
- `docs/valvomon-tietomalli.md`: nykyinen GitHub Pages -julkaisutapa, Valvomon kanoniset tietolähteet, skeemat, julkistettavat kentät, ajantasaisuuden tulkinta ja API:n käyttöperiaatteet.
- `docs/tietomallit-ja-prosessit.md`: JSON-tiedostojen tarkoitukset ja keskinäiset viittaukset, lähdetietojen kulku, ajolokin tulkinta, näytöshistorian rakenne sekä Mermaid-prosessikaaviot.
- `index.html`: Aiheseuraimen etusivu.
- `valvomo/index.html`: Valvomon käyttöliittymä osoitteessa `/valvomo/`.
- `lukija/index.html` ja `assets/js/reader.js`: RSS-lukijan sivu ja selainpuolen RSS-jäsennys, syötesuodatus sekä HTML-sisällön sanitointi.
- `kehitysjono/index.html` ja `assets/js/kanban.js`: GitHub Issues -pohjainen, vain luku -muotoinen kanban ja sitä vastaava saavutettava taulukkonäkymä; tikettien riippuvuudet luetaan GitHubin omasta riippuvuusrajapinnasta, ja selain käyttää vain julkisia luku-API-rajapintoja sekä paikallista välimuistia.
- `data/feed-catalog.json`: kaikkien kymmenen RSS-syötteen kanoninen katalogi, jota lukija ja RSS-validointi käyttävät.
- `_layouts/site.html`, `_includes/site-header.html`, `_includes/site-footer.html` ja `assets/`: sivujen yhteinen sivustorunko, navigaatio ja selaimen esityskoodi.
- `docs/intialaisen-elokuvan-*.md`: intialaisen elokuvan uutisseurannan aihekohtaiset ohjeet, lähteet ja historia.
- `docs/intialaisten-elokuvien-naytosseuranta.md` ja `docs/naytoshistorian-rakenne.md`: erillisen näytösvahdin työohje ja sen muutoshistorian tietomalli.
- `data/seurantatila.json`: yhteinen tehtäväkierto, tekninen automaatiotila ja ohjeversiot. `data/module-state/*.json`: kymmenen moduulin omat onnistumisen checkpointit, historiaviitteet, lähdetarkistusajot ja RSS-GUIDit.
- `data/naytosten-muutoshistoria.json`: näytösten nykytila ja append-only-muutostapahtumat.
- `schemas/naytosten-muutoshistoria.schema.json`: näytöshistorian JSON Schema Draft 2020-12 -skeema.
- `schemas/seurantamoduuli.schema.json` ja `schemas/module-extensions/`: seurantamoduulien yhteinen sopimus ja tyypitetyt laajennusskeemat.
- `examples/seurantamoduulit/`: aihe- ja prosessimoduulien validoitavat esimerkkimääritykset.
- `schemas/automation-run-history.schema.json`: ChatGPT-automaatioiden yhteisen vaihekohtaisen ajohistorian skeema.
- `scripts/validate_feeds.py`, `scripts/validate_module_contract.py`, `scripts/validate_publication_gate.py` ja `.github/workflows/validate-feeds.yml`: RSS:n rakennetarkistukset, seurantamoduulien tietosopimuksen validointi, raporttikohtainen julkaisulaadun portti ja niiden PR-validointi.
- `tests/test_module_contract.py`: seurantamoduulien sopimuksen positiiviset ja negatiiviset yksikkötestit.
- `reports/julkaisuportit/{run_id}.json` ja `schemas/julkaisuportti.schema.json`: jokaisen RSS-syötemuutoksen ajokohtainen hyväksyntäraportti ja sen rakenne.
- `scripts/check_links.py` ja `.github/workflows/check-links.yml`: erillinen viikoittainen lähde- ja RSS-linkkien verkkotarkistus; raportti tallennetaan GitHub Actions -artefaktiksi.
- `feeds/*.xml`: julkaistut RSS-artikkelit; jokainen syöte sisältää vain sille kuuluvan aiheen.

Yleiset raportointisäännöt ovat `docs/seuranta.md`:ssä, eivät tehtäväjonossa. Dokumentaation ja skriptien kehityskäytännöt ovat `docs/kehityskaytannot.md`:ssä. Automaation asetuksiin kopioitavien käynnistyskehotteiden ensisijaiset tekstit ovat `prompts/`-hakemistossa; automaatioiden tehtäväkäsikirjat pysyvät `docs/`-hakemistossa. Näytösvahti on erillinen automaatio eikä kuulu pääautomaation lukujärjestykseen tai tehtäväkiertoon.

## Laaja kansainvälinen haku ja Suomi-näkökulma

Kaikissa yhdeksässä aihekierroksen tehtävässä etsitään uutisia maailmanlaajuisesti. Haku ei rajoitu englanninkieliseen mediaan: käytä aiheen kannalta olennaisia paikalliskieliä, alkuperäisiä kirjoitusasuja, translitterointeja ja alueellisia lähteitä. Tarkista myös Suomen media, viralliset suomalaiset järjestäjät, tapahtumapaikat, levittäjät ja kulttuuritoimijat. Tolkienin, Taylor Swiftin, Muumien ja Euroviisujen tehtävissä tehdään lisäksi erillinen Suomessa järjestettävien aihekohtaisten tapahtumien haku: konsertit, näyttelyt, elokuvanäytökset, kilpailut, fanitapahtumat, katselujuhlat ja muut yleisötilaisuudet. Jos tällaista Suomen-yhteyttä ei löydy, älä lisää raporttiin erillistä mainintaa sen puuttumisesta.

Kun tehtäviä tai syötteitä lisätään tai poistetaan, päivitä syötetaulukko, tehtäväjono, koneellinen seurantatila ja tämän README:n lukujärjestys. Aihekohtaiset ohjeet luetaan vain kyseisen tehtävän yhteydessä; näytösvahti käyttää omaa erillistä lukujärjestystään.


## Intialaisen elokuvan uutis- ja näytösseuranta

Intialaisen elokuvan uutisraportti on tehtäväjonon tehtävä 9. Suomessa järjestettävien intialaisten elokuvien näytöksiä seuraa erillinen päivittäinen Intialaisten elokuvien näytösvahti, joka ei kuluta aihekierroksen vuoroa.

- Uutisraportin RSS: [intialaiset-elokuvat.xml](feeds/intialaiset-elokuvat.xml) – https://mikknikk.github.io/aiheseurain/feeds/intialaiset-elokuvat.xml
- Näytösten RSS: [intialaisten-elokuvien-naytokset.xml](feeds/intialaisten-elokuvien-naytokset.xml) – https://mikknikk.github.io/aiheseurain/feeds/intialaisten-elokuvien-naytokset.xml
- Ohjeet: `docs/intialaisen-elokuvan-ohje.md`, `docs/intialaisen-elokuvan-uutiset.md` ja `docs/intialaisten-elokuvien-naytosseuranta.md`.
- Seurantaloki: `docs/intialaisen-elokuvan-seuranta.md`.
- Lähderekisteri: `docs/intialaisen-elokuvan-lahteet.md`.

Näytösajat eivät kuulu uutisraportin RSS-itemeihin. Näytösvahti julkaisee vain näytös-RSS-syötteeseen.


## Saavutettavuus

Tämän repositorion saavutettavuuden tavoitetaso on WCAG 2.2 AAA kaikilta soveltuvilta osin, kuten aiemmassa elokuvaraportti-repositoriossa. Tavoitetason saavuttamista ei väitetä ilman asianmukaista testausta. Yksityiskohtaiset vaatimukset ovat tiedostossa [docs/saavutettavuus.md](docs/saavutettavuus.md). [17.11.2026 tehdyn saavutettavuuskatselmoinnin raportti](docs/saavutettavuuskatselmointi-2026-11-17.md) erottaa lähdekoodista tarkistetut asiat vielä tekemättömistä manuaalisista testeistä.

## Raporttikohtainen julkaisulaadun portti

Jokainen RSS-syötemuutos edellyttää saman PR:n mukana toimitettavaa `reports/julkaisuportit/{run_id}.json`-tarkistusraporttia. PR:n CI tarkistaa raportin rakenteen ja hyväksynnän, suorittaa RSS:n rakennetestit ja varmistaa aiempien GUIDien säilymisen. Toimitukselliset arviot tehdään lähteitä lukemalla; rakennetestit eivät todista uutisväitteiden totuutta tai lähteiden riippumattomuutta. Tarkka menettely on dokumentissa [julkaisulaadun portti](docs/julkaisuportti.md).

## RSS-itemien sisältö ja lähteet

RSS-itemissä ei käytetä item-kohtaista `<link>`-elementtiä. Jokaisen itemin koko raportti julkaistaan `<description>`-elementissä CDATA-alueen semanttisena HTML-sisältönä. Raportin lopussa on otsikoitu lähdeluettelo, jossa linkkitekstit kertovat lähteen nimen ja tarvittaessa julkaisupäivän. Kanavatason `<link>` ja Atomin kanavatason `atom:link` ovat sallittuja syötteen metatietoja.

## Näytösseurannan muutoshistoria

Näytösten viimeisin tunnettu tila ja tapahtumapohjainen muutosloki tallennetaan tiedostoon [data/naytosten-muutoshistoria.json](data/naytosten-muutoshistoria.json). Tietomalli ja käyttöönoton rajaukset on kuvattu tiedostossa [docs/naytoshistorian-rakenne.md](docs/naytoshistorian-rakenne.md), ja päivittäisen näytösvahdin on noudatettava [näytösseurannan työohjetta](docs/intialaisten-elokuvien-naytosseuranta.md). Ensimmäinen varmennettu lähtötilanne muodostettiin 16.11.2026 ja `baseline_status` on `active`; vanhoista RSS-teksteistä ei ole arvattu takautuvia tapahtumia.

## Koneellisesti luettava seurantatila

ChatGPT-automaatioiden vaihekohtainen ajohistoria tallennetaan erillisiin `run-history/main-automation`, `run-history/screening-watch` ja `run-history/quality-check` -haaroihin. Valvomo lukee niiden `history.json`-tiedostot julkisina tietoina; ne eivät ole GitHub Actions -ajoja eivätkä muuta `main`-haaran RSS-julkaisuja. Tietomalli ja kirjausmenettely: [docs/ajohistoria.md](docs/ajohistoria.md).

`data/seurantatila.json` säilyttää yhteisen yhdeksän tehtävän kierron, teknisen automaatiotilan ja ohjeversiot. Moduulikohtaiset viimeisimmät onnistumiset ja historiaviitteet ovat `data/module-state/{module_id}.json`-tiedostoissa. Osittainen tai epäonnistunut ajo ei saa siirtää moduulin onnistumisen checkpointia. Näytösvahti jatkaa siirtymävaiheessa vanhan automaatiotilansa päivittämistä; sen migraatiocheckpoint pysyy erillisenä, kunnes kirjoitusvastuu siirretään moduuliorchestratorille. Legacy-tilan eteneminen hyväksytään vain täydellisen lähdetarkistusajon ja hyväksytyn julkaisuraportin perusteella. Seurantajaksojen, aikaleimojen ja päivitysten tarkat säännöt ovat [seurantaohjeessa](docs/seuranta.md) ja [moduulikohtaisen tilan ohjeessa](docs/moduulikohtainen-tila.md).

## Skriptien kehityskäytännöt

Skriptien kommentointi- ja ylläpitovaatimukset on määritelty sitovasti tiedostossa [docs/kehityskaytannot.md](docs/kehityskaytannot.md).

## Automaattiset laatutestit

GitHub Actions asentaa `requirements.txt`-tiedoston riippuvuudet ja suorittaa `scripts/validate_feeds.py`- sekä `scripts/validate_module_contract.py`-testit push- ja pull request -muutoksissa. Seurantavalidoinnin työnkulku tarkistaa RSS:n, dokumentaation, seurantamoduulien sopimukset, julkaisulaadun ja Python-yksikkötestit. Valvomon, RSS-lukijan ja Kehitysjonon JavaScriptin syntaksi- ja logiikkatestit suoritetaan erillisessä `.github/workflows/test-ui.yml`-työnkulussa, eivätkä ne ole seurantajulkaisun pakollinen hyväksyntäportti. `tests/test_workflow_isolation.py` sisältää lisäksi regressiotestin, joka tarkistaa, ettei pakollinen seurantavalidointi riipu UI-työnkulun tuloksesta eikä UI-työnkulku odota seurantavalidointia. Pythonin yksikkötestit tarkistavat lisäksi syötekatalogin rakenteen. Erillinen `.github/workflows/check-links.yml` tarkistaa lähdekatalogin ja RSS-syötteiden linkit viikoittain sekä käsin käynnistettäessä; tulokset ovat ladattavissa työnkulun artefaktina. Näytöshistorian rakenteen tarkistus tehdään lisäksi virallista JSON Schema -määrittelyä vasten. Ne tarkistavat RSS/XML- ja kuvausten HTML-rakenteet, GUIDit, lähdeluettelot, syötteiden aihe-erottelun sekä dokumentaation ja koneellisen seurantatilan keskinäisen yhdenmukaisuuden. Erillinen linkkitarkistus raportoi osoitteiden HTTP-tilat muuttamatta julkaisuja. Tarkempi testikattavuus ja sen rajat on kuvattu [seurantaohjeessa](docs/seuranta.md).

Automaattiset testit eivät todista uutisväitteiden paikkansapitävyyttä, lähteiden riippumattomuutta tai WCAG 2.2 AAA -vaatimusten täyttymistä. Saavutettavuuden manuaaliset testit tehdään erikseen. Lähde- ja RSS-linkkien verkkotarkistus on oma viikoittainen työnkulkunsa eikä kuulu julkaisua estävään rakennetestaukseen.


## Seurantakohteiden mukainen julkaisureititys

Aiheseurain erottaa seurantamoduulin, seurantakohteen ja julkaisukohteen. Yhden seuranta-ajon tuloksena voidaan muodostaa yksi raportti kutakin seurantakohdetta kohti; raportti julkaistaan vain kyseisen kohteen omassa RSS-syötteessä. Yhdistelmäsyötteitä ei muodosteta. RSS-lukijan käyttöliittymä voi silti näyttää erillisten syötteiden artikkelit yhteisessä aikajärjestyksessä; tämä ei ole uusi RSS-syöte. Reitityksen tekninen toteutus ja rajat kuvataan [seurantakohteiden ja julkaisukohteiden oppaassa](docs/seurantakohteet-ja-julkaisukohteet.md). Tuotannon julkaisukohderekisteri ja reititys pysyvät tyhjinä, kunnes ne otetaan erikseen käyttöön.


## Kohdekohtaiset raportit

Moduulisuorittaja voi palauttaa yhden raportin kutakin seurantakohdetta kohti. Raportin tietosopimus on [schemas/target-report.schema.json](schemas/target-report.schema.json), ja sen validointi kuuluu orkestroinnin rakenteelliseen laadunvarmistukseen. Esimerkkisuorittaja kahdelle seurantakohteelle löytyy hakemistosta [examples/target_reports/](examples/target_reports/), mukaan lukien kahden kohteen suorituskehysesimerkki. Yhteensopivuuden vuoksi vanha moduulikohtainen raporttimalli säilyy käytettävissä, kunnes moduuli siirretään kohderaporttimalliin. Tuotantomoduulit ja julkaisureitit pysyvät passiivisina.
