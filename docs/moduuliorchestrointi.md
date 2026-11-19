# Moduulien yhteinen suoritusorkestrointi

**Versio:** 1.5.0  
**Päiväys:** 2026-11-19  
**Liittyvät tiketit:** [#108 – Rakenna yhteinen moduulien suoritusorkestrointi ja vaiheittainen käyttöönotto](https://github.com/mikknikk/aiheseurain/issues/108), [#212 – GitHub-pysyvät tallennus- ja julkaisusovittimet](https://github.com/mikknikk/aiheseurain/issues/212)

## 1. Vastuut ja erilliset tietokokonaisuudet

Orkestrointi yhdistää moduulin määrityksen, teknisen palvelureitityksen, moduulikohtaisen tilan, laadunvarmistuksen, tapahtumavahtikyvykkyyden ja julkaisun yhdeksi hallituksi ajoksi. Se ei sisällä aihekohtaista hakulogiikkaa eikä valitse palveluntarjoajaa moduulin sisältömäärityksen perusteella.

| Tietokokonaisuus | Kanoninen sijainti | Vastuu |
|---|---|---|
| Moduulin sisältömääritys | modules/ ja data/module-registry.json | Mitä seurataan, moduulin versio, lähteet, rajaukset ja vaaditut kyvykkyydet |
| Tekninen palvelureititys | data/provider-routing.json | AI- ja tutkimusadapterin valinta, aikakatkaisu, uusinnat ja kustannusrajat |
| Moduulin jatkuvuustila | data/module-state/{module_id}.json | Viimeisin varmennettu checkpoint ja moduulin historiaviitteet |
| Tekninen tehtävä- ja automaatiotila | data/seurantatila.json | Yhteinen tehtäväkierto, automaatioiden asetuksiin liittyvät tilat ja ohjeversiot |
| Prosessin omat tapahtumatiedot | Tapahtumatyypin oma tallennus, esim. data/naytosten-muutoshistoria.json | Tapahtumien nykytila ja append-only-tapahtumahistoria |
| Ajon tekninen tulos | ModuleRunResult / RunRecorder | Moduuli-, määritysversio-, sopimusversio- ja run_id-jäljitettävyys |
| Julkaistu tulos | Moduulin RSS-syöte ja julkaisupalvelu | Raportin sisältö ja pysyvät GUIDit |

Yhden tietokokonaisuuden muutos ei saa kirjoittaa toisen omistamaan tietoon ilman sen sopimusta.

## 2. Suorituspyyntö ja tulos

schemas/module-run-request.schema.json määrittelee yhteisen suorituspyynnön:
- module_id ja module_definition_version;
- contract_version;
- pysyvä run_id;
- aikavyöhykkeellinen seurantajakso;
- suoritustila shadow tai production;
- pyynnön aikaleima.

schemas/module-run-result.schema.json määrittelee tuloksen. Se sisältää moduulin ja versioiden tunnisteet, run_id:n, seurantajakson, suoritustilan, elinkaaren vaiheen, alku- ja loppuajat, lähdehaun täydellisyyden, laadunvarmistuksen tuloksen, julkaisun ja checkpointin tilan sekä virhekoodin. Tulokseen ei kopioida pyyntötekstiä, lähdekatkelmia tai tunnuksia.

Suorittajan sisäinen `ModuleExecutionOutput` voi sisältää vanhan moduulikohtaisen `report_content`-kentän tai useita `TargetReport`-arvoja. Kohderaportin versioitu tietosopimus on `schemas/target-report.schema.json`. Jokainen kohderaportti sisältää seurantakohteen tunnisteen ja version, havaintotyypit, aikavyöhykkeellisen seurantajakson, tarkistusajankohdan ja raporttisisällön. Yhden ajon kohde-ID:t ovat yksilöllisiä. Laadunvarmistus tarkistaa kohteen moduuliomistajuuden, rekisteröidyn version, havaintotyyppien sopivuuden ja raportointijakson ennen kuin orkestrointi luovuttaa raportit #136:n julkaisusovittimelle.

Kahden erillisen Tolkien-kohderaportin testiesimerkki on `examples/target_reports/two_target_reports.py`. Se on vain esimerkki- ja testiaineistoa eikä hae tai julkaise tuotantosisältöä.

## 3. Ajon elinkaari

scripts/module_orchestrator.py koordinoi seuraavat vaiheet:

1. **Pyyntövalidointi:** suorituspyyntö validoidaan sopimusskeemalla ja seurantajakson aikaleimat tarkistetaan.
2. **Moduulin ratkaisu:** rekisteristä haetaan moduuli ja validoitu määritys. Oletuslataaja ei lataa inactive-moduulien määrityksiä; varjotila käyttää erillistä include_inactive-lukutilaa.
3. **Versio- ja tilatarkistus:** pyynnön määritys- ja sopimusversioiden pitää vastata rekisteröityä moduulia.
4. **Lähtötilan lukeminen:** tuotantoajossa moduulitila ja prosessin artefaktiversio luetaan ennen suorittamista. Tallennuksen SHA/versio toimii optimistisena rinnakkaisuuslukituksena.
5. **Suoritus:** moduulin oma suorittaja käyttää sille välitettyä provider-routeria. Ydin ei tunne aiheen hakutermejä tai poikkeussääntöjä.
6. **Laadunvarmistus:** yhteinen QualityGate tarkistaa normalisoidun tuloksen ennen julkaisua.
7. **Varjotilan vertailu tai tuotannon julkaisu:** varjotila vertaa tulosta vanhaan käsittelyyn mutta ei julkaise eikä kirjoita tilaa. Tuotantotila julkaisee idempotenssiavaimella ja lukee tuloksen takaisin.
8. **Artefaktien tallennus:** prosessin omat tapahtumatiedot tallennetaan idempotentisti odotettua versiota vasten.
9. **Checkpoint:** moduulikohtainen onnistumisen checkpoint päivitetään vasta, kun lähdehaku, laadunvarmistus, julkaisu ja takaisinlukutarkistus ovat onnistuneet.
10. **Ajotulos:** tulos kirjataan moduulin, määritysversion, sopimusversion ja run_id:n perusteella.

Osittainen lähdehaku, laadunvarmistuksen hylkäys tai julkaisematon tulos ei saa päivittää checkpointia. Jos julkaisu onnistuu mutta artefaktin tai checkpointin tallennus epäonnistuu, ajo palautuu tilassa partial. Sama run_id ja julkaisun idempotenssiavain mahdollistavat turvallisen uusinnan.

## 4. Varjotila

Varjotila on nykyisen ja uuden käsittelyn vertailuun tarkoitettu lukutila. Se:
- saa lukea myös inactive-moduulien validoituja määrityksiä;
- voi käyttää testiadaptereita tai erikseen hyväksyttyä vertailuympäristöä;
- suorittaa moduulin ja yhteisen laadunvarmistusportin;
- tallentaa vertailun ajon tulokseen;
- ei kutsu Publisher-, ArtifactStore- tai ModuleStateStore-kirjoitusrajapintoja;
- ei luo RSS-itemeitä, muuta GUIDeja tai siirrä onnistumisen checkpointia.

Varjotila ei ole tuotantokäyttöönotto eikä anna lupaa muuttaa ajastuksia tai automaatioita.

## 5. Tuotantotilan turvarajat

Tuotantoajo hyväksytään vain, jos molemmat ehdot täyttyvät:
1. moduulin rekisterimerkinnän tila on active;
2. kutsuja antaa erillisen production_authorized-hyväksynnän.

Lisäksi tarvitaan moduulitilan tallennus, artefaktitallennus ja idempotentti julkaisupalvelu. Jos yksikin puuttuu, suoritus pysäytetään ennen moduulin käynnistämistä.

Kaikki nykyiset kymmenen moduulia ovat inactive-tilassa ja data/provider-routing.json on tyhjä. Tässä toteutuksessa ei aktivoida moduuleja, ei luoda tuotantopalvelureittejä eikä muuteta ChatGPT:n automaatioita. Varsinainen käyttöönotto vaatii erillisen käyttäjän hyväksynnän.

## 6. Yleisen tapahtumavahdin liittäminen

EventWatchModuleExecutor lukee prosessimoduulin process_extension.configuration.event_type_ref-viitteen ja lataa sen paikallisen tapahtumatyyppimäärityksen. Se normalisoi havaintojen erän ja kutsuu samaa scripts/event_watch.py-ytimen reconcile-funktiota.

Suorittaja ei sisällä film-screening-tunnistetta tai elokuvakohtaista kenttälogiikkaa. Testit käyttävät samaa suorittajaa sekä film-screening- että conference-session-tapahtumatyypille. Uusi tapahtumatyyppi tarvitsee oman määrityksen ja lähdeadapterin, ei muutosta yhteiseen tapahtumaytimeen.

Näytösvahtimoduulin oma tapahtumahistoria pysyy erillisenä prosessidatana. Moduulikohtainen checkpoint säilyttää vain sen viitteet ja viimeisimmän onnistumisen.

## 7. Virheiden eristäminen ja rinnakkaisuus

run_many suorittaa jokaisen pyynnön omana eristettynä ajonaan ja palauttaa kullekin oman ModuleRunResult-tuloksen. Yhden moduulin virhe ei keskeytä listan muiden moduulien ajoja eikä muuta niiden tilaa.

- Julkaisun idempotenssiavain on module_id:run_id.
- Artefaktitallennus tunnistaa saman moduulin ja run_id:n uusinnan.
- Moduulitilan tallennus käyttää ennen suoritusta luettua GitHub-tiedoston SHA-arvoa.
- Ristiriitainen tai vanhentunut tallennus palautuu konfliktina; aiempaa tilaa ei ylikirjoiteta.
- Palveluntarjoajien timeout- ja rate limit -uusinnat toteutetaan #107:n adapterikerroksessa.
- Ajotuloksen auditointitiedot eivät sisällä raportin tekstiä tai salaisuuksia.

Tämän toteutuksen run_many on järjestyksessä suoritettava erärajapinta. Rinnakkaiset ajot voivat käyttää samoja CAS-sopimuksia, mutta rinnakkaista ajastusta ei oteta käyttöön tässä.

## 8. Vaiheittainen käyttöönotto ja palautus

| Vaihe | Käyttö | Hyväksymisehto |
|---|---|---|
| 0. Nykytila | Vanhat automaatiot ja julkaisut jatkavat ennallaan; moduulit inactive | Nykyinen toiminta ja historia säilyvät |
| 1. Varjotila | Validoitu moduuli suoritetaan erillisessä testiajossa ilman kirjoituksia | Tulokset, lähteet, jaksot ja raporttirakenne voidaan verrata vanhaan |
| 2. Rajattu pilotti | Yksi valittu moduuli aktivoidaan ja tuotantokäyttö hyväksytään erikseen | Julkaisun, artefaktien ja checkpointin idempotenssi sekä palautus on testattu |
| 3. Asteittainen laajennus | Moduuleja aktivoidaan yksi kerrallaan | Jokainen moduuli läpäisee omat varjo- ja tuotantotestinsä |
| 4. Vanhan polun poistaminen | Vanha kirjoituspolku poistetaan vasta kun uusi on ollut vakaa | Historia, GUIDit, lähdetarkistukset ja palautus on hyväksytty |

Palautus tehdään palauttamalla moduuli inactive-tilaan, palauttamalla viimeisin hyväksytty artefakti- ja moduulitilaversio sekä käyttämällä vanhaa automaatiopolkua. Vanhoja käsikirjoja, RSS-syötteitä, GUIDeja tai näytöshistoriaa ei poisteta ennen kuin uusi polku on hyväksytty. Julkaisun idempotenssiavain estää saman ajon kaksoisjulkaisun palautuksen tai uusinnan yhteydessä.

## 9. Testaus ja rajaukset

Yksikkötestit kattavat varjotilan, tuotannon erillisen hyväksynnän, onnistuneen elinkaaren, osittaisen haun, laadunvarmistuksen hylkäyksen, julkaisun takaisinlukutarkistuksen, tallennuskonfliktin, saman run_id:n uusinnan, moduulien eristyksen sekä film-screening- ja conference-session-tapahtumatyypit.

Toteutus tarjoaa yhteisen orkestrointisopimuksen ja testatut portit. Se ei vielä sisällä tuotantokäyttöön tarkoitettua RSS-kirjoittajaa, GitHubin artefaktitallennuksen toteutusta tai automaatioiden käynnistysintegraatiota. Nämä adapterit ja niiden käyttöönottopäätös tehdään erikseen.

## 10. Seurantakohteiden yhteinen suorituskehys

`scripts/target_execution.py` lataa moduulin `target_refs`-viitteet `data/target-registry.json`-rekisteristä ja validoi jokaisen kohdemäärityksen skeemaa, moduuliomistajaa ja versioita vasten. Tuotantotilassa myös rekisterimerkinnän on oltava active; varjotilassa passiivisia kohteita voidaan lukea ilman kirjoituksia.

`TargetExecutionCoordinator` muodostaa jokaiselle kohteelle erillisen `TargetExecutionContext`-ympäristön. Se sisältää kohteen määrityksen, hakuprofiilit, ajon tunnisteen ja seurantajakson. Kohdemääritys ja hakuprofiilit annetaan runnerille rekursiivisesti vain luku -muodossa. Runner kutsutaan erikseen jokaiselle kohteelle, joten yhden kohteen muutos tai virhe ei muuta muiden kohteiden hakukontekstia.

Onnistunut kohdeajo tuottaa `TargetReport`-arvon. Jos jokin kohde epäonnistuu tai sen lähdehaku jää osittaiseksi, koordinaattori palauttaa osittaisen/epäonnistuneen moduulituloksen. Orkestroinnin laadunvarmistus estää tällaisen tuloksen julkaisemisen ja checkpointin päivittämisen.

Verkkohakuton esimerkki on `examples/target_reports/coordinator_demo.py`; se käyttää kahta rekisteröityä Tolkien-kohdetta ja muodostaa synteettiset testiraportit. Kehys ei itsessään tee verkkohakuja eikä aktivoi moduuleja tai kohteita.

## 11. Paikalliset tallennus- ja julkaisusovittimet

Tiketissä #120 lisättiin `scripts/module_run_adapters.py` ja `tests/test_module_run_adapters.py`. Sovittimet on tarkoitettu paikalliseen testaukseen ja varjotilan kehitykseen; ne eivät ole tuotantoon kytkettyjä GitHub- tai RSS-palveluja.

- `JsonFileModuleStateStore` lukee ja validoi moduulitilan, tarkistaa odotetun SHA-version ja käyttää prosessilukkoa sekä atomista tiedostonvaihtoa.
- `JsonFileArtifactStore` tallentaa moduulin prosessi-artefaktit erilliseen JSON-tiedostoon, suojaa versionvaihdon ja käsittelee saman run_id:n uusinnan idempotentisti.
- `JsonlRunRecorder` säilyttää ajon tekniset tunnisteet ja vaiheet. Se jättää pois raporttisisällön, lähdekatkelmat ja salaisuudet.
- `LocalFileRssPublisher` kirjoittaa vain annettuun testihakemistoon, muodostaa GUIDin moduuli- ja run_id-tunnisteista, säilyttää aiemmat itemit ja tarkistaa XML:n takaisinluvulla.
- `StructuralModuleQualityGate` tarkistaa suorittajan tuloksen rakenteelliset ehdot. Se ei korvaa toimituksellista julkaisulaadun arviointia.

Tallennus- ja julkaisutestit käyttävät väliaikaisia hakemistoja. Ne eivät kirjoita repositorion tuotannon moduulitiloihin, RSS-syötteisiin tai näytöshistoriaan. GitHub-pohjaiset tuotantosovittimet, ajastettujen tehtävien integraatio ja tuotantokäyttöönotto jäävät erillisiksi hyväksyttäviksi vaiheiksi.


## 12. GitHub-pysyvät tallennus- ja julkaisusovittimet (#212)

Tiketissä #212 lisättiin GitHubiin perustuvat tuotantosovittimet tiedostoon `scripts/github_module_adapters.py`. Paikalliset JSON-tiedostosovittimet säilyvät testien ja kuivaharjoittelun välineinä.

- `GitHubModuleStateStore` lukee vain pyydetyn moduulin checkpoint-tiedoston ja käyttää GitHubin blob-SHA:ta optimistisen version vertailuun. Kirjoitus luo runtime-haaran tarvittaessa ja hylkää vanhentuneen SHA:n; saman sisällön epäselvä uusinta ratkaistaan takaisinluvulla.
- `GitHubArtifactStore` tallentaa yhden muuttumattoman JSON-artefaktin moduuli-/ajotunnisteen mukaan. Erillinen moduulikohtainen indeksi sitoo ajotunnisteen artefaktiin SHA-tarkistetulla päivityksellä. Artefaktin kirjoitus ennen indeksin päivitystä on tarkoituksellinen: keskeytynyt kirjoitus voidaan uusia idempotentisti, eikä orpoa tiedostoa tulkita valmiiksi artefaktiksi.
- `GitHubPublicationJournal` tallentaa yhden manifestin moduuli-/ajotunnisteelle. Manifestin neljä vaihetta ja aikaleimat säilyvät historiassa. Vaiheita ei voi ohittaa eikä samaa ajoa varata eri raporttisisällölle.
- `GitHubRunRecorder` tallentaa ajon tekniset metatiedot muuttumattomana tiedostona. Raporttisisältö, lähdekatkelmat ja salaisuuskentät jätetään pois.
- `GitHubPagesRssPublisher` ei kirjoita suojattuun main-haaraan eikä julkaise Pagesiin suoraan. Se avaa yhden RSS-syötteen ja hyväksytyn julkaisulaadun porttiraportin sisältävän PR:n. PR:n luomiseen vaaditaan erillinen AIHESEURAIN_GITHUB_TOKEN- tai eksplisiittinen GitHub App/PAT -tunnus: GitHub ei käynnistä PR-työnkulkuja oletusarvoisen Actions GITHUB_TOKEN -tunnuksen tekemistä kirjoituksista. PR käyttää nykyistä RSS/XML- ja julkaisulaatu-CI:tä; vasta PR:n yhdistäminen käynnistää nykyisen Pages-putken. Sovitin hyväksyy julkaisun vasta, kun PR on yhdistetty ja julkisen syötteen SHA-256-sisältötiiviste, GUID-lista ja item-määrä on luettu takaisin ja täsmäävät.
- Kohderaportin reitti ratkaistaan nykyisestä julkaisurekisteristä ja -reitityksestä. Reitin on oltava aktiivinen ja moduulin on oltava topic-tyyppiä. Näytösvahti/prosessimoduuli ei voi käyttää tätä julkaisusovitinta. Yksi julkaisupyyntö sisältää tässä toteutuksessa yhden kohderaportin ja yhden syötteen; usean kohteen orkestrointi vaatii jatkovaiheen.

Runtime-tietueet tallennetaan erilliselle `module-runtime-state`-haaralle polkuihin `data/module-state/`, `data/module-artifacts/`, `data/module-publication-journal/` ja `data/module-run-history/`. Haara luodaan vasta ensimmäisen kirjoituksen yhteydessä main-haaran senhetkisestä kärjestä. Lukeminen ei luo haaraa eikä muuta repositoriota. Tiedostot rajataan 50 MiB:iin; skeemat validoidaan versionoiduilla JSON Schema -tiedostoilla.

GitHub Contents API:n epäselvä kirjoitusvastaus ratkaistaan takaisinluvulla. Rinnakkaisesta, toiseen tiedostoon kohdistuneesta haara-commitista johtuvaa 409/422-konfliktia yritetään rajatusti uudelleen vain, jos kyseinen tiedosto ei ole muuttunut. Saman checkpointin tai manifestin vanhentunut blob-SHA hylätään konfliktina. Sovittimien offline-testit käyttävät muistissa olevaa GitHub-rajapintaa eivätkä tee verkkokirjoituksia.

**Asynkroninen julkaisuraja:** RSS-PR:n avaaminen ei ole julkaisu. Jos PR on vielä avoin tai Pagesin takaisinluku ei ole valmis, sovitin palauttaa varmennuksettoman kuitin. Nykyinen synkroninen `ModuleOrchestrator.run` pysäyttää tällöin etenemisen ennen artefaktien ja checkpointin päivittämistä. Sama ajo voidaan tarkistaa uudelleen PR:n yhdistämisen ja Pages-varmennuksen jälkeen. Orkestroinnin asynkroninen odotus, uudelleenjatkaminen ja usean kohteen erilliset julkaisusiirtymät kuuluvat tikettiin #213. Sovittimia ei ole vielä kytketty live-ajoon.

## 13. Yhden aiheen kiertokoordinaattori (#202)

`scripts/topic_rotation_coordinator.py` valitsee pääkierron seuraavan aiheen teknisistä tunnisteista ja käynnistää vain sen moduulin eristetyn handoff-runnerin. Koordinaattori tarkistaa seuraavan tehtävän `data/seurantatila.json`-tiedostosta ja vertaa sitä `docs/tehtavajono.md`-tiedoston näkyvään vuoroon sekä koko kiertojärjestykseen. `data/topic-task-map.json` yhdistää yhdeksän kiertotehtävää topic-moduuleihin ja oikeisiin lähdekäyttörekistereihin.

Kiertokartta erottaa intialaisen elokuvan uutistehtävän tunnisteen (`intialaiset_elokuvat`) sen varsinaisen lähderekisterin tunnisteesta (`intialaiset_elokuvat_uutiset`). Näytösvahti on prosessimoduuli, eikä sitä hyväksytä kiertokarttaan. Koordinaattori hylkää puuttuvan, toistuvan tai virheellisen kytkennän sekä tehtäväjonon ja JSON-tilan ristiriidan ennen runnerin käynnistystä.

Koordinaattori luo yhteisen `ModuleRunRequest`-sopimuksen shadow-tilassa, muodostaa yhden moduulin `ModuleInputBundle`-paketin ja kutsuu `run_isolated_module`-funktiota. Sandboxin `topic_dispatch_runner.py` tarkistaa paketin rakenteen ja palauttaa sen sekä SHA-256-tiivisteen ulkoiselle tutkimuspalvelulle. Koordinaattori tarkistaa palautetun moduulitunnisteen, ajotunnisteen, paketin sisällön ja tiivisteen ennen handoff-tuloksen palauttamista.

Tämä on tarkoituksella vain handoff-vaihe: se ei vielä tee verkkohakua tai AI-tutkimusta. Handoff-runnerin sandboxissa ei ole verkkoa. `data/provider-routing.json` on tyhjä, joten varsinaista tutkimuspalvelun brokeria ei ole määritelty. Tulos ei ole `ModuleRunResult`-elinkaaren onnistunut tutkimusajo eikä saa julkaista, kirjoittaa artefakteja tai siirtää checkpointia. Seuraava tekninen vaihe on rajatun AI-/tutkimuspalvelubrokerin liittäminen siten, että runnerin tiedostonäkymä pysyy eristettynä ja ulkoiset palvelukutsut kulkevat auditoidun välityksen kautta.

Käyttöönotto on vain kooditasolla. Käynnistyskehotetta, ChatGPT-tehtävän asetuksia, ajastusta tai kohdekeskustelua ei muuteta tässä vaiheessa. Live-automaatio siirretään koordinaattorin käyttöön vasta erillisellä käyttäjän hyväksynnällä.

## Muutoshistoria

- **1.5.0 – 2026-11-19:** lisättiin GitHubin SHA-tarkistetut checkpoint-, artefakti- ja julkaisumanifestisovittimet sekä nykyiseen RSS/Pages-putkeen PR:nä liittyvä julkaisusovitin. Live-moduuleja ei aktivoitu; asynkroninen jatkaminen rajattiin tikettiin #213.
- **1.4.0 – 2026-11-19:** lisättiin yhden aiheen kiertokoordinaattori ja sandboxattu handoff-varjotila. Varsinainen tutkimuspalvelubrokeri ja live-automaation siirto rajattiin erillisiksi vaiheiksi.
- **1.3.0 – 2026-11-18:** lisättiin rekisteristä kohteet lataava ja jokaisen kohteen erikseen suorittava TargetExecutionCoordinator.
- **1.2.0 – 2026-11-18:** lisättiin versioitu kohderaportin tulossopimus, suorittajan usean kohderaportin tulos ja laadunvarmistuksen kohde-, versio-, havaintotyyppi- ja seurantajaksojen tarkistukset.
- **1.1.0 – 2026-11-18:** dokumentoitiin paikalliset SHA-tarkistetut tallennus-, ajotulos- ja RSS-julkaisusovittimet sekä niiden testaus- ja tuotantorajaukset.
- **1.0.0 – 2026-11-18:** määriteltiin yhteinen suorituspyyntö ja tulos, orkestroinnin elinkaari, varjotila, tuotannon hyväksyntäportti, idempotentit tallennus- ja julkaisurajapinnat sekä yleisen tapahtumavahdin moduuli-integraatio.

## Julkaisumanifesti ja palautuminen (versio 1.3.0)

Tuotantotilan orkestrointi vaatii pysyvän `PublicationJournal`-sovittimen. Se luo manifestin ennen ensimmäistä julkaisukirjoitusta. Jos manifestin valmistelu ei onnistu, julkaisua ei aloiteta. Manifestiin ei tallenneta raporttien tai lähteiden varsinaista sisältöä, vaan niiden SHA-256-tiivisteet, moduuli- ja ajotunnisteet, julkaisukohteet, lähtötilan SHA, artefaktiversio ja idempotenssiavain.

Manifestin vaiheet ovat yksisuuntaiset:

1. `prepared` – hyväksytyn raportin ja lähtöversioiden tiedot on kirjattu pysyvästi.
2. `published` – julkaisusovitin on palauttanut kuitin ja julkaisu on luettu takaisin sekä varmennettu.
3. `artifacts_persisted` – moduulin prosessi-artefaktit on tallennettu.
4. `checkpoint_updated` – viimeisin onnistunut checkpoint on tallennettu.

Saman moduuli-/ajotunnisteen ja saman raporttisisällön uusinta käyttää samaa idempotenssiavainta. Jo saavutettua manifestivaihetta ei kirjoiteta taaksepäin. Jos ajo katkeaa julkaisun jälkeen, uusinta voi toistaa julkaisupyynnön samalla avaimella; julkaisusovittimen on tunnistettava jo julkaistu sisältö. Artefakti- ja checkpoint-tallennuksen on vastaavasti oltava idempotentteja. Sama ajotunniste eri raporttisisällöllä hylätään ristiriitana. Lähtötilan SHA ja artefaktiversio säilytetään alkuperäisinä auditointitietoina.

`JsonFilePublicationJournal` on paikallinen atominen tiedostosovitin ja testiväline. Se käyttää lukitusta, väliaikaistiedostoa, `fsync`-varmistusta ja atomista tiedostonvaihtoa. GitHubin pysyvä vastine ja nykyiseen RSS/Pages-putkeen kytketty PR-julkaisusovitin on kuvattu luvussa 12. Julkaisu on asynkroninen: PR:n yhdistäminen ja julkinen takaisinluku ovat erillisiä ehtoja, eikä avoin PR siirrä checkpointia.

### Versiohistoria

- **1.3.0 – 2026-11-19:** lisättiin GitHubin pysyvä julkaisumanifesti, vaihehistorian takaisinluku ja PR-pohjainen RSS-julkaisusovitin; Pagesin julkinen sisältö varmennetaan ennen checkpointin siirtoa.
- **1.2.0 – 2026-11-18:** lisättiin pysyvä julkaisumanifesti, neljän vaiheen yksisuuntaiset tilasiirtymät ja saman ajon ristiriita-/uusintatestit. Tuotantosovitin ja nykyisen Pages-julkaisun kytkentä rajattiin erilliseksi vaiheeksi.