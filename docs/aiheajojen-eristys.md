# Aiheajojen tekninen eristäminen

**Versio:** 2.3.4  
**Päiväys:** 2026-11-20  
**Liittyvät tiketit:** [#199 – Eristetyn syötepaketin sopimus](https://github.com/mikknikk/aiheseurain/issues/199), [#200 – Eristetty suoritusympäristö](https://github.com/mikknikk/aiheseurain/issues/200), [#201 – Eristyksen CI-estot](https://github.com/mikknikk/aiheseurain/issues/201), [#202 – Pääautomaation siirto moduulikäynnistykseen](https://github.com/mikknikk/aiheseurain/issues/202), [#211 – ChatGPT-tuloksen palautuskanava](https://github.com/mikknikk/aiheseurain/issues/211), [#232 – Siirtymän julkaisu- ja palautustodisteiden pysyvä loki](https://github.com/mikknikk/aiheseurain/issues/232)

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



## Tuotantosiirtymän tekniset turvarajat (#215, #226)

Moduulin rekisterissä oleva `status` ja erillinen tuotantolupa ovat eri asioita. Tuotantopolku vaatii kaikki seuraavat ehdot: eksplisiittinen ajokutsu, moduulin aktiivinen tila, moduulikohtainen lupa tiedostossa `data/module-production-activation.json`, kelvollinen moduulimäärittely sekä pysyvät tallennus- ja julkaisusovittimet. Tuotantoluparekisterin skeema on `schemas/module-production-activation.schema.json`.

Kaikkien moduulien tuotantoluvat ovat oletusarvoisesti `false`. Rekisterin lataus hylkää puuttuvat, ylimääräiset tai virheelliset moduulimerkinnät; tuntematon moduuli ja virheellinen tiedosto estävät ajon. Prosessimoduulia, mukaan lukien intialaisten elokuvien näytösvahtia, ei voi aktivoida topic-julkaisupolkuun. Tämä toteutus ei aktivoi yhtään moduulia.

Julkaisumanifesti sisältää tarkan seurantajakson. GitHub-pohjainen julkaisumanifesti varaa moduuli–seurantajakso-yhdistelmän erillisessä SHA-CAS-indeksissä ennen RSS-julkaisua. Sama run_id voi uusia saman ehdokkaan idempotentisti, mutta eri run_id ei voi varata saman moduulin samaa seurantajaksoa uudelleen. Rinnakkaiset varausyritykset ratkaistaan takaisinluvulla; ristiriita hylätään. Indeksi on moduulikohtainen, joten eri aiheet ja saman aiheen eri jaksot eivät estä toisiaan.

Varaus on tarkoituksella fail-closed: epäselvässä tai keskeneräisessä tilanteessa jakso jää varatuksi, kunnes palautusmenettely selvittää sen. Varausta ei vapauteta automaattisesti, koska se voisi sallia kaksoisjulkaisun. Palautus ja hallittu vanhaan raportointipolkuun siirtyminen arvioidaan erikseen tiketin #227 päätöslogiikalla.


## Keskeytyneen moduulijulkaisun palautus (#227)

`scripts/module_recovery.py` sisältää sivuvaikutuksettoman `recovery_action`-päätösfunktion. Se arvioi yhdessä ajokohtaisen julkaisumanifestin vaiheen, RSS-PR:n tilan, erillisen Pages-deploymentin tilan, julkisen syötteen takaisinluvun, moduulin checkpointin ja vanhan raportointipolun saman seurantajakson julkaisutilan.

Päätökset ovat tarkoituksella erillisiä:
- Avoin RSS-PR: odota; vanhaan polkuun ei saa siirtyä.
- Yhdistetty PR: odota erikseen Pages-deploymentin valmistumista. Vasta onnistunut deployment ja täsmälleen ehdokasta vastaava julkinen RSS oikeuttavat saman `run_id`:n manifesti-, artefakti- ja checkpoint-vaiheen jatkamiseen.
- Julkaistu RSS, mutta puuttuva artefakti tai checkpoint: viimeistele sama ajo idempotentisti; älä tee uutta lähdehakua tai luo uutta GUIDia.
- Suljettu yhdistämätön PR tai ennen PR:n avaamista keskeytynyt valmistelu: vanha polku on mahdollinen vain, jos julkinen takaisinluku osoittaa ehdokkaan puuttuvan, vanhan polun saman jakson julkaisua ei ole ja erillinen hyväksyntä on annettu.
- Epäonnistunut Pages-deployment: toista tai selvitä sama julkaisu; älä luo uutta RSS-itemiä. Epäselvä GitHub-/Pages-vastaus, puuttuva takaisinluku tai ristiriitainen checkpoint: pysäytä molemmat polut ja selvitä tila. Tuntematonta ei tulkita onnistumiseksi.

Päätösfunktio ei käynnistä automaatioita, julkaise RSS:ää, vapauta jaksolukkoa, muuta checkpointia eikä muuta ChatGPT-tehtävien asetuksia. Se ei yksinään todista vanhan polun julkaisutilaa: kutsujan on annettava se luotettavasti tarkistetun RSS:n ja ajohistorian perusteella. Vanhaan polkuun palaaminen vaatii aina eksplisiittisen hyväksynnän.

### Suositeltu aihekohtainen siirtojärjestys

Ehdotettu tekninen järjestys etenee nykyisten moduulimäärittelyjen seurantakohteiden ja lähdeviitteiden määrän sekä toimituksellisen riskin perusteella. Järjestys ei ole aiheiden tärkeysjärjestys eikä aktivoi mitään moduulia:

1. **Taylor Swift** – yksi kohde, 10 lähdettä; sopiva ensimmäinen pilotti selkeällä virallisten lähteiden rungolla.
2. **Sompote Sands** – yksi kohde, 6 lähdettä; rajattu aihe ja arkistolähteisiin nojaava varmennus.
3. **Muumit** – kaksi kohdetta, 8 lähdettä; virallisten toimijoiden ja tapahtumien reititys.
4. **Wakaliwood** – kaksi kohdetta, 5 lähdettä; rajattu kohdejoukko, mutta alueellisten lähteiden saatavuus tarkistetaan.
5. **Euroviisut** – kaksi kilpailukokonaisuutta ja 10 lähdettä; kansallisten valintojen sekä kansainvälisen kattavuuden reititys.
6. **Tolkien** – kaksi kohdetta ja 28 lähdettä; laaja kieli- ja aluekattavuus.
7. **Gurmeet Ram Rahim Singh** – yksi kohde ja 7 lähdettä; oikeudellisten tapahtumien tarkka luokittelu vaatii erityisen katselmoinnin.
8. **Shakkidraamat** – viisi kohdetta ja 7 lähdettä; väitteiden, vastineiden ja useiden samanaikaisten tapausten erottelu.
9. **Intialaisen elokuvan uutiset** – 18 kohdetta ja 40 lähdettä; laajin kieli-, alue-, henkilö- ja tuotantokokonaisuus, joten viimeinen tekninen siirto.

Järjestys on alustava. Kunkin aiheen varjotilan tulokset, lähde- ja kohdeomistajuuden tarkistus sekä palautustestit arvioidaan ennen aiheen omaa hyväksyntäpäätöstä. Jos portti ei täyty, siirtoa ei tehdä eikä seuraava aihe saa periä keskeneräistä tilaa. Näytösvahti ei kuulu järjestykseen.

### Tuotantosiirtymän vähimmäislokitietue

Jokaisesta tuotantosiirtymän tai palautuksen päätöksestä on voitava jälkikäteen rekonstruoida vähintään:

- **Ajon tunnisteet:** `module_id`, moduulimäärittelyn ja sopimuksen versiot, `run_id`, `mode`.
- **Seurantajakso:** aikavyöhykkeelliset alku- ja loppuajat.
- **Ajon tila:** aloitus- ja päättymisaika, viimeinen vaihe, tulostila, virhekoodi, lähdehaun täydellisyys ja laadunvarmistuksen tulos.
- **Julkaisun todisteet:** RSS-PR:n tunniste ja tila, yhdistämiscommit, Pages-deploymentin tunniste ja tila, julkinen syöte-URL, takaisinluvun aika, SHA-256, GUID-lista ja item-määrä.
- **Tallennuksen todisteet:** lähtötilan SHA, artefaktiversio, manifestin vaihehistoria sekä checkpointin ennen/jälkeen run_id ja aikaleima.
- **Palautuspäätös:** havaitut ulkoiset tilat, `recovery_action`-tulos, vanhan polun saman jakson julkaisutila sekä mahdollisen erillisen hyväksynnän tunniste, aika ja perustelu.

Lokiin ei kopioida raporttitekstiä, koko lähdepakettia, salasanoja, tokeneita tai muita salaisuuksia. Nykyiset manifesti- ja ajotulostietueet kattavat osan näistä kentistä; ennen tuotantosiirtymää ulkoisten PR-/deployment-todisteiden pysyvä tallennus on varmistettava erikseen.

Vikainjektiotestit kattavat API-kuittauksen katoamisen RSS-julkaisun jälkeen, jokaisen julkaisumanifestin vaihekirjoituksen jälkeen sekä checkpointin tallennuksen jälkeen. Uusinta käyttää samaa `run_id`:tä ja todentaa, ettei checkpoint-historiaan tai artefakteihin synny duplikaatteja. Lisäksi päätöslogiikan testit kattavat avoimen ja suljetun RSS-PR:n, yhdistetyn julkaisun, epäselvät API-/takaisinlukutilat, vanhan polun jo julkaistun jakson ja mahdottomat vaihejärjestykset.

## Moduulisiirtymän todisteiden auditointiloki (#232)

`scripts/module_transition_evidence.py` erottaa ulkoisten tilojen lukemisen ja auditointitietueiden tallennuksen:

- `GitHubTransitionEvidenceCollector` käyttää GitHubin PR-, deployment- ja contents-rajapinnoissa vain GET-pyyntöjä. Se ei avaa, yhdistä tai sulje PR:iä eikä käynnistä Pages-deploymentia.
- PR-todiste sidotaan täsmälliseen `module_id`-/`run_id`-pariin PR:n otsikon ja rungon avulla. Tietue sisältää PR-numeron, URL:n, tilan, yhdistämisajan ja commit-SHA:n.
- Pages-todiste haetaan erikseen `github-pages`-ympäristön deploymentista, jonka commit-SHA vastaa PR:n yhdistämiscommittia. Puuttuva deployment kirjataan tilana `not_found`; PR:n yhdistäminen ei tarkoita onnistunutta Pages-julkaisua.
- Julkinen RSS luetaan katalogin topic-syöte-URL:sta välimuistin ohittavilla HTTP-otsakkeilla. Tietueeseen tallennetaan vain URL, tarkistusaika, raakasyötteen SHA-256, item-määrä ja GUIDit. RSS-itemien sisältöä ei kopioida.
- Julkaisumanifesti luetaan ja validoidaan erikseen: auditointiin tallennetaan manifestin blob-SHA, artifact-versio, raportti-/artefakti-/tilatiivisteet, seurantajakso sekä vaihehistoria ilman raporttisisältöä. Checkpoint-todiste yhdistää ennen- ja jälkeen-tilan Git-blob-SHA:t, run_id:t, aikaleimat ja manifestivaiheen. Jälkitila luetaan uudelleen runtime-haarasta ja sen run_id varmennetaan.
- Vanhan raportointipolun havainto sisältää tarkistetun lähde-URL:n, jakson, tilan, perustelun ja mahdolliset GUIDit. Kerääjä ei väitä vanhaa julkaisua puuttuvaksi ilman kutsujan tekemää lähdetarkistusta; epäselvä tila kirjataan muodossa `unknown`.
- Palautuspäätös lasketaan uudelleen `recovery_action`-funktiolla ja tallennetaan syötteineen. Mahdollinen vanhaan polkuun palaamisen hyväksyntä kirjataan erillisenä tapahtumana; lokitus ei anna hyväksyntää.

`GitHubTransitionEvidenceStore` tallentaa tapahtumat polkuun `data/module-transition-evidence/{module_id}/{run_id}/`. Tiedostonimi sisältää tapahtumatyypin ja koko tapahtuman SHA-256-tiivisteen. Tietueita ei päivitetä: saman sisällön uusinta palauttaa saman polun, ja ristiriitainen sisältö hylätään. `load_run` kokoaa yhden moduulin/ajon tapahtumat aikajärjestykseen. Skeema on `schemas/module-transition-evidence.schema.json`; `scripts/validate_transition_evidence.py` validoi skeeman ja tietueiden polkuomistajuuden CI:ssä.

Tämä on sovellustason append-only-malli GitHubin runtime-haarassa, ei väite siitä, että ylläpitäjän oikeuksilla tehty haaran historian muuttaminen olisi teknisesti mahdotonta. SHA-256 sitoo tapahtumat niiden sisältöön ja paljastaa tietueen muuttamisen, kun sitä luetaan skeeman ja tunnisteen tarkistavan lukijan kautta.

Auditointilokiin ei tallenneta raporttitekstiä, RSS:n raakasisältöä, lähdepaketteja, promptteja, tunnuksia tai salaisuuksia. Kerääjä on read-only; tallennusluokka tekee vain auditointitietueiden kirjoitukset runtime-haaraan. Näytösvahti ei kuulu topic-auditointiin.

## Lähdeauditointi ja varjotilan vertailu (#214)

ChatGPT-tulossopimuksen metadataan voidaan liittää rakenteinen source_audit. Se kirjaa moduulin omat lähteet tiloilla checked, partial, unavailable tai skipped; unavailable- ja skipped-tilat edellyttävät syytä. Täydentävät lähteet kirjataan erikseen URL-osoitteineen ja varmennustasoineen. Laadunvarmistus hylkää toisen moduulin lähde-ID:t, toistuvat lähdetietueet ja sources_checked-lukumäärän kanssa ristiriitaisen auditoinnin. Tuotantotilassa source_audit on pakollinen. Lähteiden määrälle ei aseteta vähimmäisrajaa.

scripts/compare_shadow_runs.py vertaa yhtä vanhan raportointipolun tulosta ja yhtä ChatGPT-moduulitulosta. Se vaatii saman topic-moduulin ja saman seurantajakson, validoi molempien sopimukset ja tulostaa vertailuraportin stdoutiin. Komennossa ei ole tiedostoon kirjoittavaa valitsinta eikä se käytä GitHub-kirjoitussovittimia.

Vertailu näyttää lähde-ID:t ja tilat, vanhan ja uuden raporttitekstin tiivisteet ja sanamäärät, väite-erojen tekstuaalisen vertailun, GUID-viitteet ja uuden GUID-muodon, epävarmuusmerkinnät sekä julkaisukelpoisuuden esteet. Väitteiden tekstuaalinen vastaavuus ei ole semanttinen faktantarkistus. Vertailu ei aseta lähdemäärälle tai tekstin samankaltaisuudelle numeerista hyväksymisrajaa.

tests/fixtures/shadow-comparison/tolkien.json on synteettinen, rajattu testiaineisto. Se ei ole vanhan automaation live-raportti eikä osoita tutkimustulosten todellista vastaavuutta. Vertailu ja testit eivät muuta RSS:ää, lähderekistereitä, moduulitiloja, checkpointteja tai vuorojonoa. Näytösvahti ja tallennetut ChatGPT-automaatiot pysyvät tämän työn ulkopuolella.

Aja vertailu:

```bash
python scripts/compare_shadow_runs.py --input tests/fixtures/shadow-comparison/tolkien.json
```

Regressiotestit kattavat lähdeaukot ja saavuttamattomat lähteet, tyhjän uutistuloksen, partial- ja failed-tilat, virheellisen tuloksen, uusinnan, keskeytyksen, väärän moduulin, väärän seurantajakson ja kirjoituksettomuuden.


## Aihekohtainen varjosiirtymän orkestrointi (#239, toteutus valmis)

`scripts/shadow_transition.py` yhdistää yhden topic-moduulin read-only-todistekerääjäkutsut, `recovery_action`-päätöksen ja ajokohtaisen auditointivaraston. Syötesopimus sisältää moduulin, run_id:n, moduuliversion, seurantajakson ja eksplisiittisen `mode=shadow`-tilan. Rajapinta hyväksyy vain feed-katalogiin rekisteröidyt topic-syötteet; näytösvahti ei voi käyttää sitä.

Keräämiskutsut suoritetaan ennen auditointikirjoituksia. Jokaisen tapahtuman moduuli- ja run_id tarkistetaan, ja vasta kaikkien havaintojen sekä palautumispäätöksen valmistuttua tapahtumat tallennetaan. Jos harjoitukseen sisältyy checkpoint-jälkitodiste, orkestroija lukee ensin lähtötilan itse `read_checkpoint_baseline`-toiminnolla runtime-haarasta ja vertaa sen blob-SHA:ta, run_id:tä ja checked_at-aikaa jälkitodisteen `before_*`-kenttiin. Jälkitodisteen keräämisen jälkeen orkestroija lukee runtime-haaran uudelleen ja vertaa myös `after_*`-kentät suoraan luettuun jälkitilaan. Callback ei voi määrittää tai korvata kumpaakaan päätetilaa. Ero tai puuttuva lähtö-/jälkitila pysäyttää harjoituksen ennen auditointikirjoituksia. Lopuksi sama ajo luetaan takaisin ja tallennettujen tapahtumien tunnisteet varmennetaan.

Tämä on synteettisillä testituplilla ajettava varjoharjoituksen tekninen rajapinta, ei live-siirtymä eikä tuotantokäyttöönoton hyväksyntä. Auditointitietueiden tallennus on ainoa kirjoitusoperaatio. RSS-syötteitä, moduulien aktivointilippuja, moduulitiloja, checkpointteja, tehtäväjonoa tai ChatGPT-automaation asetuksia ei muuteta.

Varjosiirtymän tekninen toteutus ja synteettiset hyväksymistestit valmistuivat PR:ssä #240, joka yhdistettiin `main`-haaraan 2026-11-20. Viimeisimmän commitin kaikki kolme PR-CI-työnkulkua läpäisivät. Tämä valmistuminen ei ole tuotantosiirtymän hyväksyntä: rajapinta on edelleen shadow-harjoittelua varten, eikä yhtään moduulia aktivoitu tai live-siirtymää tehty.

### Versiohistoria

- **2.3.3 – 2026-11-20:** viimeisteltiin #239:n varjosiirtymän toteutuksen dokumentointi PR:n #240 yhdistämisen jälkeen. Tuotantosiirtymää tai moduulien aktivointia ei tehty.
- **2.3.2 – 2026-11-20 (valmistelu):** sidottiin checkpoint-jälkitodisteen `after_*`-kentät orkestoijan itse lukemaan runtime-haaran jälkitilaan; lisättiin väärän jälkitilan hylkäävä testi.
- **2.3.1 – 2026-11-20 (valmistelu):** sidottiin checkpoint-jälkitodiste orkestoijan itse lukemaan runtime-haaran lähtötilaan; lisättiin väärän lähtö-SHA:n hylkäävä testi. Ei live-siirtymää eikä moduulien aktivointia.
- **2.3.0 – 2026-11-19 (valmistelu):** lisättiin yhden topic-moduulin varjosiirtymän orkestrointirajapinta ja synteettiset regressiotestit. Ei live-siirtymää eikä moduulien aktivointia.

### Versiohistoria

- **2.2.0 – 2026-11-19:** lisättiin PR-, Pages-, julkisen RSS:n, julkaisumanifestin vaihehistorian, checkpointin, vanhan polun ja palautuspäätöksen read-only-todistekerääjä sekä sisällön SHA-256-tiivisteellä nimetyt ajokohtaiset auditointitietueet, skeema, validoija ja CI-testit. Ei live-siirtymää.
- **2.1.0 – 2026-11-19:** lisättiin keskeytyneen moduulijulkaisun fail-closed-palautumispäätökset, vanhaan raportointipolkuun siirtymisen hyväksyntäportti sekä vikainjektiotestit.
- **2.0.0 – 2026-11-19:** lisättiin oletusarvoisesti pois päältä oleva moduulikohtainen tuotantoluparekisteri, fail-closed-validointi sekä moduuli–seurantajakso-yksinoikeus GitHub-julkaisumanifestiin. Mitään moduulia ei aktivoitu.

- **1.9.0 – 2026-11-19:** lisättiin moduulikohtainen lähdeauditointi ja kirjoitukseton vanhan/uuden raporttipolun vertailija synteettisellä Tolkien-testiaineistolla. Vertailu ei käynnistä live-ajoa eikä kirjoita tuotantotiedostoihin.
- **1.8.0 – 2026-11-19:** kytkettiin yhdistetty ChatGPT-tulos alkuperäisen handoffin SHA-256-tarkistukseen, moduuli- ja kohdekohtaiseen laadunvarmistukseen sekä shadow-orkestrointiin. Päähaaran push-työnkulku käsittelee yhden uuden tuloksen ja tallentaa teknisen ajohistorian; se ei julkaise RSS:ää, päivitä checkpointia tai muuta live-automaation asetuksia.
- **1.7.0 – 2026-11-19:** lisättiin yhden moduulin GitHub-pull request -palautuskanava, luotetusta kohdehaarasta suoritettava PR-validointi, vastaanoton skeema- ja moduulirekisteritarkistukset sekä ei-aktiivinen käynnistyskehoteluonnos. Palautus ei julkaise RSS:ää, päivitä checkpointia tai muuta live-automaation asetuksia.

- **1.3.0 – 2026-11-19:** lisättiin yhdeksän aiheen tekninen kiertokoordinaattori, eksplisiittinen tehtävä–moduulikartta, yhden moduulin handoff-runner ja CI-validointi. Toteutus pysyy varjotilan handoff-vaiheessa eikä aktivoi moduuleja tai muuta live-automaatiota.

- **1.2.0 – 2026-11-19:** lisättiin CI:ssä suoritettavat aihemoduulien välisten tietovuotojen, väärien moduuli- ja kohdeomistajuuksien, polkuturvallisuuden, lähdekatalogin täsmällisen suodatuksen sekä runnerin julkisen rajapinnan regressiotestit.
- **1.1.0 – 2026-11-19:** lisättiin Linux/bubblewrap-sandbox, vain luku -syöte ja runner-koodi, rajattu tuloshakemisto, verkoton namespace, aikaraja sekä fail-closed-käyttäytyminen.


## Taylor Swift -moduulin erillinen varjoharjoituksen valmistelu (#246)

Taylor Swiftin harjoitukselle on erillinen valmistelu- ja tulosadapteri: `scripts/taylor_swift_shadow.py` ja `scripts/taylor_swift_shadow_result.py`. Valmistelija muodostaa `module_input_bundle.py`-rakentajalla vain Taylor Swiftin oman kohteen ja lähteet sisältävän ChatGPT-syötepaketin synteettisellä tyhjällä moduulitilalla sekä sitoo yhden seurantajakson ja yhden `run_id`-tunnisteen paketin ja lähtötiedostojen SHA-256-tiivisteisiin. Historiallisesta puutteellisesta checkpointista säilytetään vain viite ja tiiviste; harjoitukselle muodostetaan erillinen tyhjä lähtötila.

Tulosadapteri validoi jo tuotetun ChatGPT-tuloksen olemassa olevaa tulossopimusta vasten; valmistelu- ja tulosartefaktien erilliset sopimukset ovat `schemas/taylor-swift-shadow-preparation.schema.json` ja `schemas/taylor-swift-shadow-result.schema.json`. Se ei käynnistä tutkimusta eikä käytä tuotannon tallennus- tai julkaisusovittimia. Varjoartefaktit voidaan tallentaa vain polkuun `data/shadow-exercises/taylor-swift/{run_id}/`, eikä olemassa olevaa artefaktia ylikirjoiteta. Toteutuksen yksityiskohdat ja rajaukset ovat [Taylor Swift -varjoharjoituksen ohjeessa](taylor-swift-varjoharjoitus.md).

Tämä tekninen valmistelu ei ole lupa varsinaiseen harjoitukseen. Live-tutkimus vaatii käyttäjän erillisen hyväksynnän. Runtime-haaraa, tuotannon julkaisupäiväkirjaa, automaatioasetuksia, ajastuksia, RSS-syötettä, tuotannon checkpointia tai tehtäväjonoa ei muuteta valmistelun yhteydessä.
