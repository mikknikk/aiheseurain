# Aiheseuraimen toteutussuunnitelma

**Versio:** 0.3.8  
**Päiväys:** 21.11.2026  
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

Tehtäväpyynnön aikamallissa kaikki varsinaiset aikaleimat tallennetaan UTC-muodossa. Paikallinen aikavyöhyke ilmoitetaan erikseen IANA-aikavyöhyketunnisteella, esimerkiksi `Europe/Helsinki`. Näin aikaleimat ovat yksiselitteisiä myös kesä- ja talviaikaan siirryttäessä.

Seuranta-aikavälissä erotetaan kolme tietoa:

- `from`: seurannan alkamishetki;
- `to`: alkuperäinen päättymishetki, joka voi olla `null`, jos aikaväli oli alun perin avoin;
- `cutoff_at`: tarkka UTC-hetki, johon asti aineisto voidaan ottaa mukaan kyseiseen ajoon.

Avoimen `to`-arvon tapauksessa `cutoff_at` rajaa silti ajon aineiston täsmällisesti. Tehtäväpyyntöön sisällytetään lisäksi paikallinen aikavyöhyketunniste, jotta raportintuottaja voi tulkita ja esittää aikavälin aiheen paikallisen ajan mukaisesti.

GitHub Actions ratkaisee tehtävätyypin oletukset, profiilit ja aihekohtaiset asetukset ennen tehtävän tarjoamista. Tehtäväpyyntö sisältää valmiin `resolved_config`-konfiguraatiosnapshotin. Raportintuottajan ei tarvitse hakea tai yhdistellä määritystiedostoja itse. Snapshotin alkuperä ja käytettyjen määritysten versiot tai Git-commit-viite säilytetään jäljitettävyyttä varten. Tehtäväpyyntöön tallennetaan `source_revision`-kenttään se Git-commitin SHA, jonka sisältöä tehtävän muodostamisessa käytettiin. Raportintuottaja hakee Markdown-ohjeet tästä täsmälleen samasta commitista eikä muuttuvasta `main`-haarasta. Näin ohjeet ja määritykset pysyvät tehtävän koko käsittelyn ajan samoina ja ajo voidaan jälkikäteen rekonstruoida. Erillistä ohjeiden kopiointia tehtäväpyyntöön ei tarvita.

Ensimmäisessä vaiheessa ei toteuteta erillistä varausmekanismia, varauksen vanhenemista eikä tehtäväkohtaista lukitusta. Yksi raportintuottaja ja yksi aktiivinen tehtäväpyyntö riittävät. Tehtäväpyynnön yksilöllinen `run_id` ja toimituksen idempotentti käsittely säilytetään.

Tehtävän käsittelyn jumiutumista vastaan toteutetaan ensimmäiseen versioon rajattu palautumismekanismi:

- Tehtäväpyynnöllä on määräaika. Jos raportintuottajan tulosta ei saavu määräaikaan mennessä, ajo käsitellään epäonnistuneena.
- Toimituksen vastaanotto- tai käsittelyvirheen jälkeen sallitaan enintään kolme automaattista käsittely-yritystä.
- Kun yritykset on käytetty tai tehtävän määräaika umpeutuu, epäonnistuminen kirjataan kanoniseen ajohistoriaan ja jonotus etenee seuraavaan tehtävään. Yksittäinen epäonnistunut tehtävä ei saa estää muiden aiheiden käsittelyä.
- Tehtävän määräajan ja uudelleenyritysten tarkan teknisen toteutuksen asetukset täsmennetään tehtävätyypin määrityksissä.
- Ensimmäisessä versiossa epäonnistuneiden tehtävien palautus myöhempään käsittelyyn on rajattu. Älykkäämpi uudelleenkäsittelylogiikka, kuten virheen syyn, aiempien yritysten ja sopivan odotusajan huomioiminen, kuuluu myöhempiin versioihin.
- Tehtävän etenemisen erillistä tilatiedostoa ei lisätä. Tehtäväpyynnön korvaaminen seuraavalla ja ajohistoria muodostavat etenemisen lähteen; seuraava tehtävä muodostetaan vasta, kun nykyisen tehtävän käsittely on ratkaistu onnistuneesti tai se on päätetty epäonnistuneeksi palautumissääntöjen perusteella.

Useiden samanaikaisten raportintuottajien tai tehtävien tuki voidaan lisätä myöhemmin. Silloin suunnitellaan erikseen atominen varaus, varauksen voimassaolo, vanhentuneen varauksen palautus sekä vanhalla `run_id`:llä saapuvien toimitusten hylkääminen. Ensimmäisen vaiheen ratkaisu ei saa tarpeettomasti estää tätä laajennusta.

### 2.2.1.1 Tehtäväpyynnön muodostamisen ja määräajanvalvonnan ajastus

Tehtäväpyynnön muodostaminen ja aktiivisen tehtävän määräajan valvonta hoidetaan yhdellä säännöllisesti käynnistyvällä GitHub Actions -työnkululla.

- Työnkulku tarkistaa, onko käsiteltävä tehtäväpyyntö jo olemassa.
- Jos tehtäväpyyntöä ei ole ja jonossa on käsiteltävä aihe, työnkulku muodostaa seuraavan tehtäväpyynnön.
- Jos aktiivinen tehtävä on ylittänyt määräaikansa eikä sen tulosta ole saapunut, työnkulku käsittelee tehtävän epäonnistuneena aiemmin sovittujen palautumissääntöjen mukaisesti ja voi sen jälkeen muodostaa seuraavan tehtävän.
- Jos tehtävä on yhä voimassa, työnkulku jättää sen ennalleen. Se ei luo rinnakkaista tehtävää eikä muuta tehtävän sisältöä.
- Raportintuottaja hakee tehtävän omalla aikataulullaan. Sen käynnistyminen ei edellytä erillistä GitHub Actions -ilmoitusta.

Tämä pitää tehtävän muodostamisen ja määräaikojen valvonnan yhdessä paikassa eikä sido niitä raportintuottajan käynnistysrytmiin. Työnkulun tarkka suoritusväli ja mahdollinen manuaalinen käynnistys määritellään myöhemmin tehtävätyyppien ja käyttörajoitusten yhteydessä.

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

Yksi aihe voi käyttää useita profiileja. Esimerkiksi elokuvanäytösvahti voi yhdistää tapahtumavahdin yleiset oletukset, elokuvanäytösprofiilin ja intialaisen elokuvan profiilin. Konserttivahti voi käyttää tapahtumavahdin ja konserttiprofiilin lisäksi esimerkiksi klassisen musiikin profiilia. Ensimmäisessä versiossa profiilien välisiä riippuvuuksia, kieltoja tai erillistä yhteensopivuusmatriisia ei mallinneta. Profiileja voidaan yhdistää ilman, että niiden tarvitsee ilmoittaa yhteensopivuuttaan keskenään.

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
- Tuntemattomat avaimet ja väärän tyyppiset arvot hylätään skeemavalidoinnissa.
- Profiilien omat rakenteet validoidaan niiden skeemoja vasten ja ratkaistu konfiguraatio tehtävätyypin skeemaa vasten. Näin tarkistetaan, että lopullinen asetuskokonaisuus sopii tehtävätyypin määrittelemään rakenteeseen.
- Ylikirjoituksia saa tehdä vain skeemassa sallituissa asetuskohdissa.
- Ensimmäisessä versiossa ei toteuteta yleistä semanttisten ristiriitojen tunnistusta profiilien välillä. Tarvittaessa tällaisia tarkistuksia voidaan lisätä myöhemmin konkreettisen käyttötarpeen perusteella.

GitHub Actions ratkaisee asetukset ennen tehtävän tarjoamista. Raportintuottajalle annetaan valmis, muuttumaton konfiguraatiokokonaisuus osana tehtäväpyyntöä; raportintuottajan ei tarvitse toteuttaa periytymis- tai yhdistelylogiikkaa. Tehtäväpyyntöön tallennetaan myös käytettyjen määritysten versiot tai Git-commit-viite, jotta ajon asetukset voidaan jäljittää ja tarvittaessa rekonstruoida.

Tehtävätyyppien, profiilien ja aihekohtaisten määritysten JSON Schema -skeemat validoivat rakenteet ja sallitut ylikirjoitukset. Markdown-ohjeet versioidaan Gitissä ja niihin viitataan tehtäväpyynnöstä.

### 2.3 Toimitustapa: Git push erilliseen vastaanottohaaraan

Raportintuottaja toimittaa tuloksensa Git pushilla erilliseen vastaanottohaaraan. Hyväksytty lähtökohta on esimerkiksi haara `raportit-inbox`.

Ensimmäisessä versiossa hyödynnetään ChatGPT-ympäristössä jo käytössä olevaa GitHub App -yhteyttä. Erillistä GitHub Appia, vastaanottopalvelua tai uutta käyttöoikeusjärjestelyä ei rakenneta tässä vaiheessa. Ratkaisu pidetään tarkoituksella yksinkertaisena, koska samaa ChatGPT-käyttäjäympäristöä käytetään sekä Aiheseuraimen kehittämiseen että raportintuottajan ensimmäiseen versioon.

- Raportintuottajan toimintamalli ohjaa toimitukset `raportit-inbox`-haaraan; se ei puske suoraan `main`-haaraan eikä julkaistavien RSS-syötteiden hakemistoon.
- Nykyisen GitHub App -yhteyden tekninen kirjoitusoikeus voi olla tätä toimintamallia laajempi. Ensimmäisessä versiossa ei väitetä, että käyttöoikeus olisi teknisesti rajattu vain vastaanottohaaraan.
- `main`-haaran suojaus säilytetään, ja kaikki vastaanottohaaran toimitukset validoidaan ennen käsittelyä tai julkaisua.
- Tunnistetietoja ei kopioida raportintuottajan ohjeisiin tai toimituspaketteihin; tunnistautuminen tapahtuu olemassa olevan integraation kautta.
- Erillisen GitHub Appin ja tarkemman käyttöoikeuksien eriyttämisen tarve arvioidaan uudelleen, jos raportintuottajia tai integraatioita tulee lisää tai käyttöoikeusrajausta tarvitaan muuten.
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

- `metadata.json`: pakollinen kaikissa tulostiloissa. Se sisältää vähintään sopimusversion, ajotunnisteen, aiheen tunnisteen, seurantatyypin, seuranta-aikavälin ja tulostilan sekä kyseisen tulostilan edellyttämät lisätiedot;
- `item.xml`: pakollinen `success`-tilassa, jossa julkaistava raportti syntyi. `partial`-tilassa raporttisisältö toimitetaan ensimmäisessä versiossa sovitun tallennusmallin mukaisesti mutta sitä ei julkaista. `no_report`- ja `failed`-tiloissa `item.xml`-tiedostoa ei toimiteta.

Tarkka skeema, tiedostonimien säännöt ja toimituksen täydellisyyskriteerit määritellään erikseen. `no_report`- ja `failed`-tulosten toimitus ei saa edellyttää olematonta RSS-item-tiedostoa.

#### Toimituspaketin tulostilakohtaiset tiedostovaatimukset

Jokainen toimitus sisältää `metadata.json`-tiedoston. RSS-itemin vaatimus riippuu metatietoihin merkitystä tulostilasta:

| Tulostila | `metadata.json` | `item.xml` | Käsittely |
|---|---|---|---|
| `success` | pakollinen | pakollinen | Validoitu raportti julkaistaan oikeassa RSS-syötteessä. |
| `partial` | pakollinen | raporttisisällön toimitus sovitun sopimuksen mukaan | Osittainen tulos tallennetaan, mutta sitä ei julkaista ensimmäisessä versiossa. |
| `no_report` | pakollinen | ei toimiteta | Seuranta onnistui, mutta julkaistavaa raporttia ei löytynyt. |
| `failed` | pakollinen | ei toimiteta | Seuranta epäonnistui; metatietoihin kirjataan virheen luokka ja lyhyt, turvallinen kuvaus. |

`no_report` ja `failed` ovat siis normaaleja, eksplisiittisiä ajotuloksia eivätkä puuttuvasta toimituksesta pääteltäviä tiloja. Myös näistä ajoista syntyy tavallinen toimituspaketti, jonka `metadata.json` kirjataan ajohistoriaan. `failed`-tilan virhekuvaukseen ei saa sisällyttää salaisuuksia, tunnisteita, raakaa keskustelusisältöä tai tarpeettomia henkilötietoja.

Ensimmäisessä versiossa toimituspaketin eheys varmistetaan rakenteellisilla ja sisällöllisillä tarkistuksilla ilman erillistä allekirjoitus- tai tarkistussummajärjestelmää.

- `metadata.json` ja mahdollinen `item.xml` toimitetaan saman `run_id`-tunnisteen omaavassa hakemistossa.
- Vastaanottava GitHub Actions -työnkulku tarkistaa vaadittujen tiedostojen olemassaolon ja toimituksen rakenteen.
- Työnkulku validoi metatietojen rakenteen ja tarkistaa, että toimituksen `run_id` sekä aiheen tunniste vastaavat aktiivista tehtäväpyyntöä.
- Jos tulostila edellyttää julkaistavaa raporttia, RSS-itemin on oltava mukana ja sen XML/RSS-rakenne validoidaan ennen julkaisua.
- `no_report`- ja `failed`-toimituksissa `item.xml`-tiedostoa ei toimiteta; niiden `metadata.json` sisältää tulostilan edellyttämät tiedot.
- Puutteellinen, virheellinen tai väärään tehtävään kuuluva toimitus hylätään kokonaisuutena. Se ei saa johtaa osittaiseen tallennukseen tai RSS-julkaisuun.

Erilliset kryptografiset allekirjoitukset ja tarkistussummat jätetään ensimmäisen version ulkopuolelle. Niiden tarve arvioidaan myöhemmin, jos uhkamalli tai toimituskanavan luonne sitä edellyttää.

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

Käsittely suunnitellaan yhdeksi hallituksi työnkuluksi. Julkaisun onnistumista ei saa rakentaa sen varaan, että GitHub Actionsin omalla `GITHUB_TOKEN`-tunnisteella tehty push käynnistäisi automaattisesti uuden työnkulun: tällaiset tapahtumat eivät normaalisti käynnistä uusia työnkulkuja.

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
4. `SECURITY.md` kuvaa haavoittuvuuksien ilmoitus- ja käsittelytavan.
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
- miten nykyisen GitHub App -yhteyden tosiasialliset oikeudet ja `main`-haaran suojaus varmistetaan käyttöönotossa; ensimmäisessä versiossa ei edellytetä teknistä, vain `raportit-inbox`-haaraan rajattua kirjoitusoikeutta;
- miten toimituspaketin tarkat tulostilakohtaiset tiedostovaatimukset ja skeemat määritellään; eheys- ja täydellisyysperiaatteet on päätetty kohdassa 2.3;
- miten `metadata.json`-tiedoston tarkka skeema määritellään;
- miten vastaanottohaaran toimituksia säilytetään ja siivotaan turvallisesti;
- miten julkaisun ja ajotietojen tallennuksen virhetilanteista palaudutaan;
- miten ajotietojen julkisuus rajataan ja tarkistetaan automaattisesti;
- mitkä vanhan toteutuksen komponentit kannattaa säilyttää.

## 7. Hyväksymismenettely

Tämä dokumentti täydentyy teknisten yksityiskohtien ratkaisun ja nykyisen toteutuksen katselmoinnin perusteella. Käyttäjä tarkistaa ja hyväksyy toteutussuunnitelman kokonaisuutena ennen tikettien luomista.

Toteutussuunnitelman hyväksyminen, tikettien luominen, toteutuksen aloittaminen ja tuotantoon siirtyminen ovat erillisiä vaiheita. Nykyisten automaatioiden ajastuksia, ohjeita, kehotteita tai kohdekeskusteluja ei muuteta ilman erillistä lupaa.
