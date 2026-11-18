# Seurantamoduulit, seurantakohteet ja julkaisukohteet

**Versio:** 1.4.0  
**Päiväys:** 2026-11-18  
**Liittyvä tiketti:** [#133](https://github.com/mikknikk/aiheseurain/issues/133)

## Kolme itsenäistä käsitettä

- **Seurantamoduuli** (modules/, data/module-registry.json) omistaa suoritettavan prosessin, kyvykkyydet, lähdeviitteet ja toimitukselliset säännöt. Se ei sisällä kohdekohtaisia hakuja eikä julkaisukanavan asetuksia.
- **Seurantakohde** (data/targets/, data/target-registry.json) yksilöi henkilön, teoksen, elokuvan, tapahtumakokoelman tai muun kiinnostuksen kohteen. Se omistaa hakuprofiilit, kieli- ja aluerajaukset sekä kohdekohtaiset sisällytys- ja poissulkuehdot. Kohde viittaa omistavaan moduuliin, mutta ei määrittele julkaisupaikkaa.
- **Julkaisukohde** (data/publications/, data/publication-registry.json) määrittelee jakelukanavan, muodon ja teknisen kohdepolun. Se ei sisällä hakuehtoja tai toimituksellista logiikkaa.

## Reitityssopimus

data/publication-routing.json yhdistää moduulin, seurantakohteen ja täsmälleen yhden julkaisukohteen. Reitti voi lisäksi rajata havaintotyypit. Jokaisella seurantakohteella on yksi oma RSS-syöte, johon kaikki kyseisen kohteen raportit julkaistaan. Eri seurantakohteiden raportteja ei kopioida yhteiseen yhdistelmäsyötteeseen. Tuotannon julkaisurekisteri ja reititys ovat tässä vaiheessa tyhjiä: esimerkit eivät muuta nykyisiä RSS-syötteitä.

## Esimerkki

examples/seurantakohteet/naytosvahti.json näyttää yhden näytösvahtimoduulin kaksi erillistä kohdetta: yksittäisten elokuvien näytökset ja festivaalit. examples/julkaisukohteet/ sisältää kummallekin oman RSS-kanavan. examples/julkaisureititys/naytosvahti.json reitittää kummankin kohteen vain omaan syötteeseensä. Esimerkkien example.invalid-osoitteet ovat tarkoituksella ei-tuotannollisia.

## Tunnisteet, versiot ja omistajuus

Kaikilla kolmella käsitteellä on oma pysyvä tunniste ja semanttinen versio. Muutokset kohteen hakuehtoihin eivät muuta moduulin versiota; julkaisukanavan polun tai formaatin muutos ei muuta kohteen versiota. Reititys on oma versionoitu kokonaisuutensa. Nimiä ja tiedostopolkuja ei käytetä viittausavaimina.

## Validointi

Aja python scripts/validate_target_publication.py. Tarkistus validoi kuusi JSON Schema -sopimusta sekä moduuli-, kohde-, julkaisu- ja reititysviitteet. Yksikkötestit ajetaan komennolla python -m unittest tests.test_target_publication -v. Tarkistus hylkää puuttuvat tiedostot, tuntemattomat tunnisteet, kohteen väärän moduuliomistajan ja reitin tuntemattoman julkaisukohteen.

## Siirtymä ja tuotannon rajat

Nykyiset kymmenen moduulimääritystä viittaavat nyt erillisiin seurantakohteisiin. Kohteet on rekisteröity inactive-tilaan. Nykyisen intialaisten elokuvien näytösvahdin käsikirja, sen historiallinen RSS-syöte, näytöshistoria ja automaatio pysyvät nykyisessä tuotantopolussa. Uudet julkaisukohteet ja reitit otetaan käyttöön vasta erillisessä hyväksytyssä migraatiossa.

Tämä rakenne ei muuta ChatGPT-automaatiota, ajastuksia, aikavyöhykkeitä, ohjeita tai kohdekeskusteluja.


## Julkaisureitityksen ajonaikainen sovitin

Toteutuksen ensimmäinen tekninen osa on `scripts/publication_routing.py`. Se lukee tuotannon moduuli-, seurantakohde-, julkaisukohde- ja reititysrekisterit erillisinä sekä tarkistaa viittausten eheyden ennen reitin käyttöä.

- `load_publication_context()` lataa ja validoi rekisterit.
- `resolve_publication_plan()` ratkaisee yhden kohdekohtaisen raportin kanavat moduulin, seurantakohteen ja raportin havaintotyyppien perusteella.
- `preview_publication_plan()` palauttaa kuivaharjoittelun tuloksen eikä kirjoita tiedostoja.
- `LocalRoutedRssPublisher` on paikallinen RSS-sovitin, joka julkaisee kohderaportin vain kohteelle määriteltyyn omaan syötteeseen. Sovittimelle annetaan kirjoitusjuuri erikseen; se ei aktivoi tai kirjoita tuotantokohteisiin itsestään.

Saman moduulin, seurantakohteen, ajon ja sen ainoan julkaisukohteen yhdistelmä tuottaa vakaan GUIDin. Reititys hylkää useita julkaisukohteita sisältävän reitin sekä saman seurantakohteen eri julkaisukanaviin jakavan määrityksen. Uusinta-ajo ei lisää samaa raporttia uudelleen, ja saman GUIDin eri sisältö hylätään ristiriitana. Julkaisusovitin ja reitityksen ratkaisu ovat erillisiä luokkia ja vaiheita.

Orkestrointi välittää tulossopimuksen `target_reports`-kentän validoidut raportit reititetylle julkaisusovittimelle. Siirtymävaiheessa se tunnistaa myös vanhan metadataan sijoitetun listan. Julkaisusovittimelle välitetään kustakin raportista `target_id`, `observation_types` ja `report_content`. Jos kohderaportteja ei anneta, aiempi moduulikohtainen julkaisupolku jatkaa ennallaan. Tuotannon rekisterit ovat yhä tyhjiä eikä mikään uusi reitti tai kohde ole aktivoitu. Testit: `python -m unittest tests.test_publication_routing -v`.


## Kohdekohtaisen raportin sopimus

Moduulisuorittaja voi palauttaa useita `TargetReport`-arvoja yhden ajon tuloksessa. Jokainen raportti kuuluu täsmälleen yhdelle moduulin rekisteröimälle seurantakohteelle. Raportin tietosopimus on `schemas/target-report.schema.json`, ja Python-malli on `TargetReport` tiedostossa `scripts/module_orchestrator.py`.

Raportti sisältää:
- seurantakohteen pysyvän tunnisteen ja version
- vähintään yhden havaintotyypin
- täsmälleen suorituspyynnön mukaisen seurantajakson
- ajon tarkistusajankohdan
- kohdekohtaisen raporttisisällön.

`StructuralModuleQualityGate` tarkistaa skeeman, moduulin `target_refs`-viitteet, kohteen rekisteröidyn version ja moduuliomistajuuden, havaintotyyppien sopivuuden sekä ajanjakson ja tarkistusajankohdan yhdenmukaisuuden. Saman ajon kohderaporttien tunnisteet eivät saa toistua.

Orkestrointi välittää validoidut kohderaportit #136:n reititetylle julkaisusovittimelle. Jos suorittaja ei vielä tuota kohderaportteja, vanha moduulikohtainen `report_content`-polku toimii siirtymävaiheen yhteensopivuustilana. Esimerkkisuorittaja kahdelle Tolkien-kohteelle: `examples/target_reports/two_target_reports.py`. Testit: `python -m unittest tests.test_target_report_contract -v`.


## Muutoshistoria

- **1.4.0 – 2026-11-18:** rajattiin jokainen seurantakohde yhteen omaan RSS-julkaisukohteeseen; yhdistelmäsyötteet poistettiin esimerkeistä ja reitityksen sopimuksesta (#142).
- **1.3.0 – 2026-11-18:** lisättiin moduulin kohteet rekisteristä lataava ja erikseen suorittava yhteinen suorituskehys.
- **1.2.0 – 2026-11-18:** dokumentoitiin kohdekohtaisen raportin sopimus, suorittajan tulosmalli ja laadunvarmistuksen tarkistukset.
- **1.1.0 – 2026-11-18:** dokumentoitiin julkaisureitityksen ajonaikainen sovitin ja orkestroinnin reititysintegraatio.
- **1.0.0 – 2026-11-18:** erotettiin seurantamoduuli, seurantakohde ja julkaisukohde omiksi tietokokonaisuuksikseen.


## Seurantakohteiden suorituskehys

`scripts/target_execution.py` lataa moduulin kohteet rekisteristä ja antaa moduulin omalle runnerille yhden kohteen kerrallaan. Jokainen `TargetExecutionContext` sisältää vain kyseisen kohteen määrityksen ja hakuprofiilit, moduulin ja ajon tunnisteet sekä pyydetyn seurantajakson. Kohdemäärityksen sisäinen rakenne annetaan runnerille vain luku -muodossa.

Runner palauttaa `TargetExecutionResult`-arvon, josta koordinaattori muodostaa #138:n mukaisen `TargetReport`-arvon. Kohdekohtaiset virheet eristetään: jos yksikin kohde jää keskeneräiseksi, moduulin tulos on osittainen eikä sitä julkaista. Tuotantotilassa passiiviset seurantakohteet estetään jo ennen runnerin kutsumista.

Esimerkkisuorittaja `examples/target_reports/coordinator_demo.py` näyttää kahden Tolkien-kohteen erilliset hakuprofiilit ja raportit ilman verkkohakua. Testit: `python -m unittest tests.test_target_execution -v`.
