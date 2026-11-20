# Aiheseuraimen toteutussuunnitelma

**Versio:** 0.3.0  
**Päiväys:** 20.11.2026  
**Tila:** suunnitteluluonnos – hyväksytyt arkkitehtuuriperiaatteet ja ensimmäisen vaiheen tehtävänjakomalli kirjattu, tekniset yksityiskohdat avoinna  
**Perusta:** [Vaatimusmäärittely 0.10.0](vaatimusmaarittely-uudistus.md)

> Tämä dokumentti kokoaa keskustelussa hyväksytyt tekniset suunnitteluratkaisut. Se ei ole lupa toteuttaa järjestelmää, muuttaa nykyisiä automaatioita tai niiden ajastuksia eikä ottaa uutta tuotantoprosessia käyttöön. Toteutustiketit muodostetaan vasta, kun toteutussuunnitelma on kokonaisuutena tarkistettu ja hyväksytty.

## 1. Tavoite

Toteutussuunnitelma määrittelee, miten vaatimusmäärittelyn mukainen Aiheseurain rakennetaan. Se toimii myöhemmin GitHub-tikettien muodostamisen perustana.

Perusratkaisun tulee olla mahdollisimman yksinkertainen. Raportintuotanto erotetaan deterministisestä ohjaus-, vastaanotto- ja julkaisukerroksesta.

## 2. Hyväksytyt arkkitehtuuriperiaatteet

### 2.1 Raportintuottaja ja GitHub Actions ovat erillisiä

- Raportintuottaja tekee varsinaisen seuranta- ja raportointityön.
- Raportintuottaja tuottaa julkaisuvalmiin RSS-itemin sekä ajon käsittelyyn tarvittavat metatiedot.
- GitHub Actions vastaanottaa toimituksen, validoi sen, tallentaa ajotiedot ja julkaisee hyväksytyn RSS-itemin oikeaan syötteeseen.
- Raportintuottajan ei tarvitse muodostaa tai palauttaa kokonaista RSS-syötettä eikä muokata julkaistuja syötetiedostoja.
- Raportintuottaja on vaihdettavissa, kunhan se noudattaa yhteistä, versioitua toimitussopimusta.

### 2.2 GitHub Actions ei tarvitse tekoälyä

GitHub Actionsin ohjaus- ja julkaisukerros on tavallista determinististä ohjelmistologiikkaa. Se ei tarvitse omaa kielimallia, tekoälyagenttia tai muuta tekoälypalvelua.

Actionsin tehtäviä ovat esimerkiksi:

- määritysten lukeminen;
- erääntyneen aiheen valinta sovittujen sääntöjen mukaan;
- ajo- ja toimitustunnisteiden käsittely;
- toimituspaketin ja RSS-itemin validointi;
- väärän aiheen tai virheellisen tietosopimuksen hylkääminen;
- kaksoiskäsittelyn estäminen;
- ajotietojen tallentaminen;
- RSS-julkaisun tekeminen ja tuloksen varmistaminen;
- virhetilanteiden käsittely.

Raportintuottajan tutkimus- ja raportointikyvykkyys on tästä erillinen. Ohjaus- ja julkaisukerroksen toiminta ei saa edellyttää tekoälypalvelua.

### 2.2.1 Tehtävän tarjoaminen raportintuottajalle

Ensimmäisessä toteutusvaiheessa käytetään yhtä raportintuottajaa. Raportintuottaja toimii pull-mallilla: se käynnistyy omalla ajastuksellaan, lukee GitHubista tehtävänanto-ohjeen ja hakee sen osoittaman tehtäväpyynnön.

- GitHub Actions valitsee seuraavan aiheen ja muodostaa yhden tehtäväpyynnön raportintuottajan noudettavaksi.
- Tehtäväpyyntö sisältää vähintään yksilöllisen `run_id`-tunnisteen, aiheen tunnisteen ja tehtävän suorittamiseen tarvittavat ohje- ja aikavälitiedot.
- Raportintuottaja ei itse valitse seuraavaa aihetta eikä muuta jonotuksen ohjaustietoja.
- Tehtäväpyyntö valmistellaan ennakkoon; raportintuottajan ei tarvitse käynnistää GitHub Actions -ajoa eikä odottaa erillistä hyväksyntävastausta tehtävää hakiessaan.
- `data/tehtava.json` sisältää kerrallaan yhden tehtävän. Tehtäväpyyntö pysyy muuttumattomana, kunnes kyseisen tehtävän käsittelyn valmistuminen on vahvistettu; vasta sen jälkeen muodostetaan seuraava tehtäväpyyntö.
- Tehtävän tarkka tiedostopolku, tietorakenne ja tilapäivitysten toteutus määritellään myöhemmin.

Tehtäväpyynnön aikaväli esitetään alkuperäisissä tehtävätiedoissa alkamis- ja päättymishetkenä. Avoimeksi jätetty päättymishetki (`null`) tarkoittaa, että seuranta ulottuu tehtävän muodostamishetkeen. Tehtävän muodostamishetken tarkka aikaleima tallennetaan erikseen, jotta aikaväli voidaan myöhemmin todentaa. Aikaleimojen ja paikallisten aikavyöhykkeiden tarkka esitystapa määritellään tietomallissa.

Ensimmäisessä vaiheessa ei toteuteta erillistä varausmekanismia, varauksen vanhenemista eikä tehtäväkohtaista lukitusta. Yksi raportintuottaja ja yksi aktiivinen tehtäväpyyntö riittävät. Tehtäväpyynnön yksilöllinen `run_id` ja toimituksen idempotentti käsittely säilytetään.

Useiden samanaikaisten raportintuottajien tai tehtävien tuki voidaan lisätä myöhemmin. Silloin suunnitellaan erikseen atominen varaus, varauksen voimassaolo, vanhentuneen varauksen palautus sekä vanhalla `run_id`:llä saapuvien toimitusten hylkääminen. Ensimmäisen vaiheen ratkaisu ei saa tarpeettomasti estää tätä laajennusta.

### 2.2.2 Tehtävätyypit, määritysprofiilit ja aihekohtaiset asetukset

Määritykset jaetaan kolmeen tasoon, jotta samankaltaiset aiheet voivat käyttää yhteisiä asetuksia ja erilaiset tehtävät voivat silti noudattaa omia toimintamallejaan:

1. **Tehtävätyyppi** määrittelee tehtäväluokan yhteisen toimintamallin ja oletusasetukset. Esimerkkejä ovat uutisraportti ja tapahtumavahti.
2. **Määritysprofiilit** sisältävät uudelleenkäytettäviä, rajattuja asetuskokonaisuuksia. Yksi tehtävä voi käyttää useita yhteensopivia profiileja.
3. **Aihekohtainen määritys** valitsee tehtävätyypin ja käytettävät profiilit sekä sisältää vain kyseisen aiheen erityisasetukset ja poikkeukset.

Esimerkkihakemistorakenne:

```text
config/
  task-types/
    news-report.json
    event-monitor.json
  profiles/
    concerts.json
    film-screenings.json
    classical-music.json
    indian-cinema.json
  topics/
    tolkien.json
    concert-topic.json
    indian-film-screenings.json
docs/
  topics/
    tolkien.md
    concert-topic.md
    indian-film-screenings.md
data/
  sources/
    ...
```

Hakemistonimet ja tiedostopolut ovat suunnitteluesimerkkejä; lopullinen rakenne vahvistetaan skeemojen ja nykyisen tiedostorakenteen katselmoinnin yhteydessä.

Tehtävätyyppi sisältää yleiset, saman tehtäväluokan tehtäville kuuluvat oletukset. Profiilit täydentävät niitä esimerkiksi tapahtumalajin, sisältöalueen, genren tai muun uudelleenkäytettävän ominaisuuden mukaan. Aihekohtainen määritys sisältää yksittäisen seurannan omat hakusanat, rajaukset ja muut erot. Ihmiselle tarkoitetut pitkät toimitukselliset ja menettelyohjeet pidetään Markdown-tiedostoissa; koneellisesti käsiteltävät asetukset ovat JSON-tiedostoissa.

Yksi aihe voi käyttää useita profiileja. Esimerkiksi elokuvanäytösvahti voi yhdistää tapahtumavahdin yleiset oletukset, elokuvanäytösprofiilin ja intialaisen elokuvan profiilin. Konserttivahti voi käyttää tapahtumavahdin ja konserttiprofiilin lisäksi esimerkiksi klassisen musiikin profiilia. Profiilien on ilmoitettava yhteensopiva tehtävätyyppi tai muu sovittu yhteensopivuus, jotta niitä ei voi yhdistää virheellisesti keskenään.

Ensimmäisessä versiossa profiilit ovat itsenäisiä määrityksiä: profiili ei peri toista profiilia eikä muodostu mielivaltaiseksi periytymisketjuksi. Tämä pitää yhdistämisen ennustettavana. Profiilien keskinäinen järjestys ilmoitetaan aihekohtaisessa määrityksessä ja ratkaisee mahdolliset päällekkäiset asetukset.

Asetukset ratkaistaan seuraavassa järjestyksessä:

1. tehtävätyypin oletukset;
2. aihekohtaisessa määrityksessä ilmoitetut profiilit annetussa järjestyksessä;
3. aihekohtaiset ylikirjoitukset.

Yhdistämissäännöt:

- Sisäkkäiset JSON-objektit yhdistetään rekursiivisesti.
- Myöhempi arvo korvaa aiemman saman asetuksen arvon.
- Taulukot korvataan kokonaan; niitä ei yhdistetä automaattisesti.
- Puuttuva asetus periytyy aiemmalta tasolta.
- Tuntemattomat avaimet, väärän tyyppiset arvot ja yhteensopimattomat profiilit hylätään validoinnissa.
- Ylikirjoituksia saa tehdä vain skeemassa sallituissa asetuskohdissa.

GitHub Actions ratkaisee asetukset ennen tehtävän tarjoamista. Raportintuottajalle annetaan valmis, muuttumaton konfiguraatiokokonaisuus osana tehtäväpyyntöä; raportintuottajan ei tarvitse toteuttaa periytymis- tai yhdistelylogiikkaa. Tehtäväpyyntöön tallennetaan myös käytettyjen määritysten versiot tai Git-commit-viite, jotta ajon asetukset voidaan jäljittää ja tarvittaessa rekonstruoida.

Tehtävätyyppien, profiilien ja aihekohtaisten määritysten JSON Schema -skeemat validoivat rakenteet ja sallitut ylikirjoitukset. Markdown-ohjeet versioidaan Gitissä ja niihin viitataan tehtäväpyynnöstä.

### 2.3 Toimitustapa: Git push erilliseen vastaanottohaaraan

Raportintuottaja toimittaa tuloksensa Git pushilla erilliseen vastaanottohaaraan. Hyväksytty lähtökohta on esimerkiksi haara `raportit-inbox`.

- Raportintuottaja ei puske suoraan `main`-haaraan eikä julkaistavien RSS-syötteiden hakemistoon.
- Toimitus sijoitetaan omaan hakemistoonsa ajo- tai toimitustunnisteen perusteella.
- GitHub Actions käynnistää toimituksen käsittelyn vastaanottohaaraan tehdyn pushin perusteella.
- Actions tarkistaa paketin ennen kuin mitään julkaistaan tai tallennetaan tuotannon tietoihin.
- Virheellinen toimitus ei saa muuttaa julkaistuja RSS-syötteitä.
- Gitin historia antaa toimituksille jäljitettävyyden.

Esimerkkirakenne:

```text
raportit-inbox/
  <run_id>/
    metadata.json
    item.xml
```

Toimituspaketti sisältää:

- `metadata.json`: sopimusversion, ajotunnisteen, aiheen tunnisteen, seurantatyypin, seuranta-aikavälin, tulostilan ja muut käsittelyssä tarvittavat metatiedot;
- `item.xml`: varsinaisen RSS-itemin, jos ajosta syntyi julkaistavaa raporttia.

Tarkka skeema, tiedostonimien säännöt ja toimituksen täydellisyyskriteerit määritellään erikseen. `no_report`- ja `failed`-tulosten toimitus ei saa edellyttää olematonta RSS-item-tiedostoa.

### 2.4 Vastaanotto ja julkaisu käsitellään hallitusti

GitHub Actions vastaa koko vastaanottavan käsittelyn loogisesta ketjusta:

1. tunnistaa uuden toimituksen;
2. lukee toimituspaketin;
3. validoi metatiedot ja mahdollisen RSS-itemin;
4. tarkistaa ajon ja aiheen vastaavuuden;
5. estää saman toimituksen tai GUIDin kaksoiskäsittelyn;
6. tallentaa ajotiedot;
7. julkaisee hyväksytyn itemin oikeaan aihekohtaiseen RSS-syötteeseen;
8. varmistaa RSS/XML:n ja tallennuksen onnistumisen;
9. kirjaa käsittelyn lopputuloksen.

Käsittely suunnitellaan yhdeksi hallituksi työnkuluksi. Julkaisun onnistumista ei saa rakentaa sen varaan, että GitHub Actionsin omalla `GITHUB_TOKEN)-tunnisteella tehty push käynnistäisi automaattisesti uuden työnkulun: tällaiset tapahtumat eivät normaalisti käynnistä uusia työnkulkuja.

Julkaisun ja ajotietojen tallennuksen osittaiset epäonnistumiset käsitellään idempotentisti. Ajoa ei merkitä julkaistuksi ennen kuin julkaisu on varmennettu.

### 2.5 Ajotietojen tallennus

Ajotiedot tallennetaan tässä vaiheessa julkiseen GitHub-repositorioon. Tämä on hyväksytty nykyisen suunnitteluvaiheen ratkaisu.

Julkiseen tallennukseen saa sisällyttää vain tarkoitukseen sopivia ajotietoja. Sinne ei tallenneta salaisuuksia, käyttöoikeustunnuksia, tarpeettomia henkilötietoja, raakaa keskustelusisältöä tai tarpeettomasti kopioitua lähdesisältöä.

Tallennusmuoto ja hakemistorakenne määritellään teknisessä suunnittelussa. Tavoitteena on yksi kanoninen ajohistoria, ei rinnakkaisia tietovarastoja. Julkisen tallennuksen soveltuvuutta arvioidaan uudelleen, jos tietosisältö tai käyttöoikeustarpeet muuttuvat.

## 3. Nykyisen toteutuksen hyödyntäminen

Aiemman toteutuksen osia ei palauteta kokonaisuutena sellaisenaan. Ennen toteutuspäätöksiä tehdään komponenttikohtainen katselmointi.

Katselmoinnissa arvioidaan erikseen ainakin:

- aihe- ja seurantatyyppimääritykset;
- raportin ja ajotuloksen tietosopimukset;
- RSS-julkaisun validointi ja idempotenssi;
- ajohistorian tietomalli;
- Valvomon tietolähteet ja näkymät;
- RSS-lukijan nykyinen toteutus;
- testit ja GitHub Actions -työnkulut.

Osa voidaan säilyttää, osa yksinkertaistaa ja osa toteuttaa uudelleen. Uudelleenkäyttö ei saa tuoda takaisin tarpeettomia riippuvuuksia tai monimutkaisuutta.

## 4. Kehitysympäristön hyväksytty tavoitetila

Toteutussuunnitelmaan sisältyvät seuraavat käyttäjän hyväksymät GitHub-käytännöt:

1. `main`-haaran suojaus: estetään poistaminen ja force push. Suojaus ei tässä vaiheessa pakota pull request -työskentelyyn, koska suora työskentely `main`-haaraan on edelleen sovittu käytäntö.
2. Dependabot seuraa käytössä olevia riippuvuuksia. Päivitykset tulevat ehdotuksina, eivät automaattisesti tuotantoon.
3. GitHub Actions -riippuvuudet kiinnitetään commit-SHA:han ja työnkulkujen oikeudet rajataan vähimmäistarpeeseen.
4. `SECURITY.md) kuvaa haavoittuvuuksien ilmoitus- ja käsittelytavan.
5. Automaattisia laatutarkistuksia laajennetaan RSS/XML:ään, JSON-skeemoihin, dokumenttilinkkeihin, määritysten eheyteen ja soveltuviin saavutettavuustarkistuksiin.
6. Julkaisu- ja muutoskäytännöt määritellään: merkittävien muutosten CHANGELOG, versioidut GitHub Releases -julkaisut ja commit-viestikäytäntö.

Nämä ovat tavoitetilan päätöksiä, eivät vielä toteutettuja käytäntöjä. Niiden käyttöönotto suunnitellaan vaiheittain. PR-pakkoa tai automaattisia riippuvuuspäivityksiä tuotantoon ei oteta käyttöön ilman erillistä hyväksyntää.

## 5. Ehdotettu toteutuksen vaiheistus

1. Nykyisen toteutuksen ja arkiston komponenttikohtainen inventaario.
2. Tehtävätyyppien, määritysprofiilien ja aihekohtaisten määritysten sekä toimitussopimuksen skeemojen määrittely.
3. Ajonhallinta: yhden aiheen valinta, `run_id`, ajotietue ja aihekohtainen päällekkäisyyksien esto.
4. Vastaanottohaara ja Git push -toimituspaketin käsittely.
5. Validointi, kanoninen ajohistoria ja idempotentti RSS-julkaisu.
6. Valvomon kolme näkymää ja niiden tietolähteet.
7. RSS-lukijan yhteensopivuuden varmistaminen.
8. Hyväksyttyjen GitHub-käytäntöjen ja laajennettujen laatutarkistusten käyttöönotto.
9. Nykyisten automaatioiden mahdollisen siirtymän erillinen suunnittelu ja hyväksyntä.

Vaiheistus on suunnitteluehdotus. Se ei anna lupaa käynnistää tuotantoa tai muuttaa nykyisiä automaatioita.

## 6. Avoimet tekniset yksityiskohdat

Seuraavat asiat täsmennetään ennen tikettien muodostamista:

- miten tehtäväpyynnön tarkka skeema, aikavälien ja aikavyöhykkeiden esitystapa sekä käsittelyn valmistumisen kirjaaminen määritellään;
- miten tehtävätyyppien, profiilien ja aihekohtaisten määritysten tarkat JSON Schema -skeemat, sallitut ylikirjoitukset ja Markdown-ohjeiden viittaukset määritellään;
- millä tunnistautumistavalla raportintuottaja saa push-oikeuden vain vastaanottohaaraan;
- miten vastaanottohaaran toimituspaketin eheys ja täydellisyys varmistetaan;
- miten `metadata.json)-tiedoston tarkka skeema määritellään;
- miten `no_report`- ja `failed`-tulokset toimitetaan ilman RSS-itemiä;
- miten vastaanottohaaran toimituksia säilytetään ja siivotaan turvallisesti;
- miten julkaisun ja ajotietojen tallennuksen virhetilanteista palaudutaan;
- miten ajotietojen julkisuus rajataan ja tarkistetaan automaattisesti;
- mitkä vanhan toteutuksen komponentit kannattaa säilyttää.

## 7. Hyväksymismenettely

Tämä dokumentti täydentyy teknisten yksityiskohtien ratkaisun ja nykyisen toteutuksen katselmoinnin perusteella. Käyttäjä tarkistaa ja hyväksyy toteutussuunnitelman kokonaisuutena ennen tikettien luomista.

Toteutussuunnitelman hyväksyminen, tikettien luominen, toteutuksen aloittaminen ja tuotantoon siirtyminen ovat erillisiä vaiheita. Nykyisten automaatioiden ajastuksia, ohjeita, kehotteita tai kohdekeskusteluja ei muuteta ilman erillistä lupaa.
