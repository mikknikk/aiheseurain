# Moduulien yhteinen suoritusorkestrointi

**Versio:** 1.0.0  
**Päiväys:** 2026-11-18  
**Liittyvä tiketti:** [#108 – Rakenna yhteinen moduulien suoritusorkestrointi ja vaiheittainen käyttöönotto](https://github.com/mikknikk/aiheseurain/issues/108)

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

## Muutoshistoria

- **1.0.0 – 2026-11-18:** määriteltiin yhteinen suorituspyyntö ja tulos, orkestroinnin elinkaari, varjotila, tuotannon hyväksyntäportti, idempotentit tallennus- ja julkaisurajapinnat sekä yleisen tapahtumavahdin moduuli-integraatio.
