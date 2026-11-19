# Aiheajojen tekninen eristäminen

**Versio:** 1.8.0  
**Päiväys:** 2026-11-19  
**Liittyvät tiketit:** [#199 – Eristetyn syötepaketin sopimus](https://github.com/mikknikk/aiheseurain/issues/199), [#200 – Eristetty suoritusympäristö](https://github.com/mikknikk/aiheseurain/issues/200), [#201 – Eristyksen CI-estot](https://github.com/mikknikk/aiheseurain/issues/201), [#202 – Pääautomaation siirto moduulikäynnistykseen](https://github.com/mikknikk/aiheseurain/issues/202), [#211 – ChatGPT-tuloksen palautuskanava](https://github.com/mikknikk/aiheseurain/issues/211)

## Tavoite

Jokainen aiheajo käsittelee vain yhden aihemoduulin sisältöä. Yhteinen koordinaattori valitsee tehtävän ja muodostaa moduulille rajatun syötepaketin. Aihekohtainen suorittaja ei saa lukea muiden aiheiden määrityksiä, lähteitä, kohteita, tilaa tai historiaa.

Yhteinen tekninen ydin sisältää vain yleiset sopimukset: ajon tunnisteen ja seurantajakson, suorituspyynnön, laadunvarmistusrajapinnan, rajatun tuloksen, tallennus- ja julkaisusovittimet sekä virheiden eristyksen. Se ei sisällä aiheiden hakutermejä tai toimituksellisia sisältöohjeita.

Näytösvahti pysyy erillisenä päivittäisenä process-moduulina. Se ei kuulu yhdeksän uutisaiheen kiertoon eikä tämän työn ensimmäiseen tuotantokytkentään.

## Syötepaketin sisältö

scripts/module_input_bundle.py muodostaa yhden moduulin paketin seuraavista tiedoista:

- moduulin oma määritys;
- vain moduulin target_refs-viitteisiin kuuluvat seurantakohteet;
- vain moduulin source_refs-viitteisiin kuuluvat lähteet yhteisestä katalogista;
- saman aiheen lähdekäyttörekisterin tarkistusajat, käyttörajat ja retry_after-arvot;
- vain moduulin viimeisin checkpoint ja oman julkaisusyötteen GUID-viitteet;
- ajon tunniste ja seurantajakso.

Paketista jätetään pois moduulirekisteri, koko kohde- ja lähderekisteri, kaikkien aiheiden seurantatila, yhteiset vanhat tilaviitteet, muiden moduulien historia sekä automaatioiden asetukset ja käynnistyskehotteet. Lähdekatalogista luovutetaan vain moduulin source_refs-listassa nimetyt lähteet.

schemas/module-input-bundle.schema.json määrittelee paketin rakenteen. Paketin rakentaja tarkistaa moduulin, kohteiden, lähteiden ja lähdekäyttörekisterin omistajuuden ennen tietojen luovutusta. Runnerille annettava rakenne on rekursiivisesti vain luku -muotoinen.

Testaa syötepaketti, eristyksen regressiotestit ja sandbox komennolla:

```bash
python -m unittest tests.test_module_input_bundle tests.test_module_isolation_guards tests.test_isolated_module_runner -v
```

Sama testikokonaisuus suoritetaan PR-CI:ssä osana `python -m unittest discover -s tests -v` -komentoa. `tests/test_module_isolation_guards.py` sisältää tarkoituksellisesti virheellisiä testitapauksia, joissa:
- toisen moduulin sisältö ja käyttämätön lähdekatalogin tietue yritetään saada pakettiin;
- moduulirekisteri ohjataan toisen moduulin määritykseen tai repositorion ulkopuoliseen polkuun;
- seurantakohteen omistajaksi vaihdetaan toinen moduuli;
- Tolkien-moduulille yritetään antaa Muumien lähdekäyttörekisteri;
- runnerin julkiseen funktiorajapintaan yritetään edellyttää repositorion juurta tai yhteisten rekisterien polkuja.

Testit käyttävät väliaikaista kopiota data- ja moduulitiedostoista. Ne eivät muuta repositorion varsinaisia rekistereitä, moduuleja, seurantatilaa tai RSS-syötteitä.

## Eristyksen rehellinen rajaus

Syötepaketin muodostaminen rajaa runnerille annettavan tietosisällön sovellusrajapinnassa. Pelkkä pakettirajaus ei estä saman prosessin koodia avaamasta muita tiedostoja; siksi runner suoritetaan lisäksi erillisessä käyttöjärjestelmätason sandboxissa.

Vahvempi prosessieristys on toteutettu tiedostossa `scripts/isolated_module_runner.py`. Runner käynnistetään Linuxissa `bubblewrap`-mount- ja namespace-sandboxissa. Sandboxiin liitetään vain:
- `/input/bundle.json`: validoitu moduulikohtainen syöte, vain luku;
- `/runner/runner.py`: ajettava ohjelmakoodi, vain luku;
- `/output/result.json`: ainoa runnerille kirjoitettavaksi annettu pysyvä tiedosto; hakemisto on vain luku -muotoinen;
- Pythonin suorittamiseen tarvittavat järjestelmäkirjastot, vain luku.

Sandbox käyttää erillisiä user-, PID-, IPC-, UTS- ja network-namespaceja (`--unshare-all`), tyhjennettyä ympäristöä, erillistä `/tmp`-hakemistoa ja eristettyä prosessiryhmää. Päärepon työpuuta, kotihakemistoa, GitHub-tunnuksia, muita moduuleja tai verkkoa ei liitetä sandboxiin. Syöte ja runner-koodi ovat vain luku -muotoisia. Runner voi kirjoittaa vain ennalta luotuun `/output/result.json`-tiedostoon; hakemisto itsessään on vain luku -muotoinen. Tulos luetaan ilman symbolisten linkkien seuraamista vasta prosessin onnistuneen päättymisen jälkeen. Tulostiedoston koko rajataan viiteen mebitavuun, ja runner-prosessille asetetaan CPU-, tiedostokoko-, tiedostokuvaus- ja core-dump-rajat. Aikarajan ylitys, puuttuva bubblewrap tai sandboxin käynnistysvirhe pysäyttää ajon; tavalliseen eristämättömään subprocessiin ei pudota.

Tämä on Linuxin bubblewrap-eristys, ei erillinen virtuaalikone. Runner näkee käyttöjärjestelmän rajatun runtime-näkymän, mutta ei isäntäkoneen yleistä tiedostojärjestelmää. Muilla käyttöjärjestelmillä suoritus estetään, kunnes vastaava sandbox-toteutus lisätään. GitHub Actions asentaa bubblewrapin ja ajaa sandboxin integraatiotestit osana testikokonaisuutta.

Käyttöesimerkki luotetun koordinaattorin puolella:

```python
from scripts.module_input_bundle import build_module_input_bundle
from scripts.isolated_module_runner import run_isolated_module

bundle = build_module_input_bundle(
    "tolkien",
    task_id="tolkien",
    run_id="example-run",
    period_start="2026-11-19T00:00:00+02:00",
    period_end="2026-11-19T23:59:59+02:00",
)
result = run_isolated_module(bundle, runner_source)
```

Runnerin lähdekoodi annetaan merkkijonona, ei repositorion tiedostopolkuna. Runner palauttaa JSON-olion kirjoittamalla `/output/result.json`-tiedoston. Koordinaattori vastaa tuloksen sopimusvalidoinnista ja moduulitilan päivittämisestä; sandbox-funktio ei muuta repositoriota eikä tilatiedostoja.

## Koordinaattorin ja aiheajon vastuut

Koordinaattori saa nähdä tehtäväjonon valintaan tarvittavat tekniset tunnisteet ja tilatiedot. Se ei tee aihekohtaista uutishakua eikä välitä koko tehtäväjonoa aiheajolle. Aiheajo saa vain oman moduulipakettinsa ja palauttaa rajatun tuloksen. Koordinaattori validoi tuloksen ja hoitaa julkaisu- sekä checkpoint-siirtymät yhteisten sopimusten kautta.

Tiketti #199 kattaa syötepaketin sopimuksen, #200 käyttöjärjestelmätason sandboxin ja #201 paketin rajausta, omistajuutta sekä runnerin rajapintaa valvovat CI-regressiotestit. Pääautomaation käynnistyskehotteen ja varsinaisen ChatGPT-ajon siirtäminen tähän malliin tehdään erikseen (#202). GitHub-muutos ei muuta ChatGPT:n tehtäväasetuksia, ajastuksia tai kohdekeskusteluja.


## Aihekierron koordinaattori ja eristetty handoff

`scripts/topic_rotation_coordinator.py` on uutiskierron tekninen aloituspiste. Se:
- lukee `data/seurantatila.json`-tiedoston seuraavan tehtävän tunnisteen;
- varmistaa, että `docs/tehtavajono.md` ja koneellinen tehtäväjärjestys vastaavat toisiaan;
- ratkaisee tehtävän moduuliksi `data/topic-task-map.json`-kytkentäkartan avulla;
- tarkistaa, että valittu moduuli on `topic`-tyyppinen ja sen määritys on kelvollinen;
- muodostaa vain valitun moduulin syötepaketin;
- käynnistää `scripts/topic_dispatch_runner.py`-ohjelman bubblewrap-sandboxissa.

Kytkentäkartta sisältää yhdeksän uutiskierron tehtävää. Intialaisen elokuvan uutistehtävä ohjataan moduuliin `indian-film-news` ja sen omaan lähderekisteriin `intialaiset_elokuvat_uutiset`. Erillistä `indian-film-screening-watch`-prosessimoduulia ei saa lisätä karttaan. Kiertojärjestyksen pitää vastata sekä `docs/tehtavajono.md`- että `data/seurantatila.json`-tiedostoa; ristiriita keskeyttää käynnistyksen.

Koordinaattori ei välitä tehtäväjonoa, moduulirekisteriä tai muiden moduulien määrityksiä runnerille. Runner saa vain `module_input_bundle.py`-paketin, jossa on valitun moduulin määritys, sen omat seurantakohteet, lähteet ja moduulitila. Handoff-runner palauttaa saman rajatun paketin, SHA-256-tiivisteen ja ChatGPT-suoritussopimuksen. CI validoi sekä kytkentäkartan että jonon ja seurantatilan vastaavuuden.

Käynnistys vaatii eksplisiittisen ajotunnisteen ja aikavyöhykkeelliset seurantajakson rajat:

```bash
python -m scripts.validate_topic_dispatch
python -m scripts.topic_rotation_coordinator \
  --run-id topic-shadow-001 \
  --period-start 2026-11-19T00:00:00+02:00 \
  --period-end 2026-11-19T23:59:59+02:00
```

**ChatGPT on varsinainen tutkimuksen suorittaja.** Handoff-paketin `execution_contract.executor` on `chatgpt_scheduled_task`. ChatGPT lukee vain valitun moduulin `input_bundle`-sisällön ja tekee varsinaiset verkkohakunsa omilla käytettävissä olevilla haku- ja selaustyökaluillaan. Ulkoista AI- tai tutkimuspalvelua eikä `data/provider-routing.json`-reititystä tarvita tähän toimintatapaan. Bubblewrap-sandbox koskee vain paikallista handoff-runneria: se ei eristä ChatGPT:n omaa työskentely-ympäristöä käyttöjärjestelmätasolla. Tietosisällön rajaaminen perustuu siihen, että automaatiolle luovutetaan vain yhden moduulin paketti ja sen ohje kieltää muiden moduulien tietojen pyytämisen tai lukemisen. Tämä raja on kuvattava rehellisesti sovellustason eristykseksi, ei LLM:n prosessieristykseksi.

Handoff ei julkaise RSS:ää eikä päivitä moduulin checkpointia. ChatGPT:n rakenteisen tuloksen sopimus on `schemas/chatgpt-module-result.schema.json`. `scripts/chatgpt_module_result.py` validoi moduuli-, versio-, ajo- ja seurantajaksotunnisteet ja muuntaa tuloksen `ModuleExecutionOutput`-arvoksi. Sopimus tukee sekä yhtä moduuliraporttia että useita erillisiä `TargetReport`-kohderaportteja, joiden tunnisteet ja seurantajaksot tarkistetaan ennen orkestrointia. `ChatGPTResultExecutor` toteuttaa `ModuleExecutor`-rajapinnan jo suoritetulle ChatGPT-tutkimukselle. Sovitin ei tee verkkohakuja eikä kutsu ulkoista palvelua. Live-ajon palautuspolku ja tallennetun automaatiotehtävän siirto edellyttävät edelleen erillistä hyväksyntää. Kaikki moduulit pysyvät inactive-tilassa.

GitHub-toteutus ei muuta `prompts/paauutisseuranta.txt`-tiedostoa eikä ChatGPT-tehtävän tallennettua käynnistyskehotetta, ajastusta tai kohdekeskustelua. Käynnistyskehotteen ja live-tehtävän siirto tehdään vasta erikseen hyväksytyssä vaiheessa.

## ChatGPT-tuloksen GitHub-palautuskanava (#211)

ChatGPT palauttaa yhden moduulin tuloksen uutena GitHub-pull requestina. Tulostiedoston polku on `data/chatgpt-inbox/{module_id}/{run_id}.json`. PR saa sisältää täsmälleen yhden uuden JSON-tiedoston; se ei saa muuttaa käsikirjoja, moduuleja, rekistereitä, RSS-syötteitä tai muita tuloksia.

Palautus on valittu PR-malliin, koska käytettävissä oleva GitHub-yhteys ei tarjoa tässä toteutuksessa yleistä `workflow_dispatch`-käynnistystä. PR on auditoitava ja uudelleen tarkistettava toimituskanava:
1. ChatGPT luo tulostiedoston omalla käytettävissä olevalla GitHub-yhteydellään ja avaa PR:n `main`-haaraan. Jos automaatiolla ei ole GitHub-yhteyttä tai kirjoitusoikeutta, se palauttaa JSONin käyttäjälle eikä väitä toimitusta tehdyksi.
2. `.github/workflows/validate-chatgpt-inbox.yml` käynnistyy `pull_request_target`-tapahtumasta. Työnkulku hakee validointikoodin PR:n kohdehaaran SHA:sta, lukee PR:stä vain yhden tiedoston GitHub API:n kautta ja validoi sen luotetulla koodilla. Se ei suorita PR:n sisältämää koodia eikä saa kirjoitusoikeuksia tai salaisuuksia.
3. Validointi tarkistaa JSON-skeeman, moduulin topic-tyypin ja rekisteriversiot, tiedostopolun, run_id:n, seurantajakson sekä handoffin tunnisteiden vastaavuuden. Vain uusi tiedostopolku hyväksytään; olemassa olevaa tulosta ei voi korvata.
4. Tulos tallentuu pysyvästi vastaanottoaineistoksi vasta PR:n hyväksytyn yhdistämisen jälkeen. Päähaaran RSS- ja dokumentaatiotyönkulku validoi kaikki tallennetut vastaanottotulokset uudelleen.

Tuloksen `handoff`-osio kopioi alkuperäisestä handoffista moduuli-, versio-, ajo- ja seurantajaksotunnisteet, pyynnön ajankohdan sekä syötepaketin SHA-256-tiivisteen. Nykyinen vastaanottovalidointi tarkistaa tiivisteen muodon ja metatietojen sisäisen vastaavuuden; se ei vielä vertaa tiivistettä itsenäisesti pysyvästi tallennettuun alkuperäiseen handoffiin. Tämä rajoite on tarkoituksellinen ja dokumentoitu: alkuperäisen handoffin pysyvä tallennus ja riippumaton vertailu kuuluvat jatkotiketteihin #212 ja #213. Palautus-PR:n hyväksyntä ei myöskään ole toimituksellinen julkaisupäätös.

Käynnistyskehotteen palautusohje on luonnoksena tiedostossa `prompts/paauutisseuranta-moduulipalautus-luonnos.txt`. Se ei korvaa `prompts/paauutisseuranta.txt`-tiedostoa eikä muuta tallennetun ChatGPT-automaation asetuksia, ajastusta, aikavyöhykettä tai kohdekeskustelua. Luonnoksen käyttöönotto edellyttää erillistä hyväksyntää.



## ChatGPT-tuloksen kytkentä orkestrointiin (#213)

Yhdistetty vastaanottotulos voidaan käsitellä yhdellä moduulikohtaisella prosessilla komennolla `python scripts/process_chatgpt_result.py`. Päähaaran `.github/workflows/process-chatgpt-result-shadow.yml` käynnistyy vain, kun uusi tulos on ensin yhdistetty `main`-haaraan polkuun `data/chatgpt-inbox/{module_id}/{run_id}.json`. Työnkulku lukee vain yhdistetyn tuloksen, hakee täyden Git-historian ja tarkistaa, että push lisäsi täsmälleen yhden uuden tulostiedoston.

Käsittelijä sitoo tuloksen alkuperäiseen handoffiin:
- tarkistaa nykyisen kiertovuoron ja tehtävä–moduulikartan;
- tarkistaa moduulin tyypin, määritys- ja sopimusversion, run_id:n sekä seurantajakson;
- muodostaa alkuperäisen yhden moduulin syötepaketin uudelleen ja vertaa sen SHA-256-tiivistettä;
- tallentaa handoffin muuttumattoman hyväksyntätietueen runtime-haaraan ensimmäisellä vastaanotolla ja käyttää sitä saman ajon uusintojen vertailuun;
- muuntaa ChatGPT-tuloksen `ModuleExecutionOutput`-arvoksi ja suorittaa moduulin kohteiden omistajuuden sekä raporttien laadunvarmistuksen;
- tallentaa vain teknisen ajon auditointitiedon, ei raporttitekstiä.

Tämä automaatiopolku on tarkoituksella **shadow-tilassa**. Se ei julkaise RSS:ää, päivitä moduulin checkpointia eikä siirrä aihekierrosta. Tuotantojulkaisu ja kierron päivitys kuuluvat myöhempään hyväksyttyyn tuotantosiirtymään (#215). Näytösvahti ei kuulu tähän työnkulkuun. Työnkulku ei muuta ChatGPT:n tallennettuja tehtäviä, käynnistyskehotteita, aikatauluja tai kohdekeskusteluja.

Toimituksellinen julkaisuarvio on määritelty tulossopimuksen valinnaiseksi metatiedoksi ja validoidaan omalla skeemallaan. Se ei yksinään ole julkaisulupa: RSS-ehdokkaan automaattiset GUID-, XML- ja rakennevarmennukset sekä nykyinen julkaisulaadun portti pysyvät erillisinä pakollisina vaiheina.


### Versiohistoria

- **1.8.0 – 2026-11-19:** kytkettiin yhdistetty ChatGPT-tulos alkuperäisen handoffin SHA-256-tarkistukseen, moduuli- ja kohdekohtaiseen laadunvarmistukseen sekä shadow-orkestrointiin. Päähaaran push-työnkulku käsittelee yhden uuden tuloksen ja tallentaa teknisen ajohistorian; se ei julkaise RSS:ää, päivitä checkpointia tai muuta live-automaation asetuksia.
- **1.7.0 – 2026-11-19:** lisättiin yhden moduulin GitHub-pull request -palautuskanava, luotetusta kohdehaarasta suoritettava PR-validointi, vastaanoton skeema- ja moduulirekisteritarkistukset sekä ei-aktiivinen käynnistyskehoteluonnos. Palautus ei julkaise RSS:ää, päivitä checkpointia tai muuta live-automaation asetuksia.

- **1.3.0 – 2026-11-19:** lisättiin yhdeksän aiheen tekninen kiertokoordinaattori, eksplisiittinen tehtävä–moduulikartta, yhden moduulin handoff-runner ja CI-validointi. Toteutus pysyy varjotilan handoff-vaiheessa eikä aktivoi moduuleja tai muuta live-automaatiota.

- **1.2.0 – 2026-11-19:** lisättiin CI:ssä suoritettavat aihemoduulien välisten tietovuotojen, väärien moduuli- ja kohdeomistajuuksien, polkuturvallisuuden, lähdekatalogin täsmällisen suodatuksen sekä runnerin julkisen rajapinnan regressiotestit.
- **1.1.0 – 2026-11-19:** lisättiin Linux/bubblewrap-sandbox, vain luku -syöte ja runner-koodi, rajattu tuloshakemisto, verkoton namespace, aikaraja sekä fail-closed-käyttäytyminen.
