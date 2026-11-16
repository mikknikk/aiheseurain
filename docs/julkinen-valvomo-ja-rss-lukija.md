# Julkinen valvomo ja RSS-lukija

**Tila:** suunnittelu kirjattu; toteutusta ei ole aloitettu  
**Päivitetty:** 2026-11-16

Tämä dokumentti on sekä tekninen tavoitekuvaus että kehitystyön seurantalista. Merkitse tehtävät tehdyiksi vasta, kun toteutus, testit ja muutoksen jälkeinen tarkistus on tehty. Suunnitelman kirjaaminen ei tarkoita, että ominaisuus olisi jo käytössä.

## 1. Kokonaisratkaisu

Tavoitteena on yksi GitHub Pages -sivusto, jonka kaksi ensisijaista osiota ovat:

1. **Seurannan tila (valvomo):** näyttää automaatioiden todellisen etenemisen, viimeisimmät ajot, virheet, aihekierroksen tilanteen ja lähteiden tarkistuksen kattavuuden.
2. **Uutislukija:** kokoaa repositorion RSS-syötteet yhteen käyttöliittymään ja tarjoaa aiheen, ajan ja lukutilan mukaisen selailun.

Myöhempi mahdollinen kolmas osio on **raporttiarkisto**. Sitä ei tarvita ensimmäiseen julkaisuun.

Käyttöliittymä on staattinen GitHub Pages -sivusto. Se lukee automaatioiden tuottamia julkisia JSON-tiedostoja ja RSS-syötteitä, mutta ei tarvitse selaimessa GitHub-kirjoitusoikeuksia, salaisuuksia tai käyttäjätunnistusta. Automaatiot ja niiden tietojen keruu pysyvät erillään käyttöliittymästä.

Tarkat tiedostonimet, teknologiat ja hakemistorakenne päätetään ennen toteutusta nykyisen Pages-julkaisun ja repositorion rakenteen tarkistamisen jälkeen. Sivuston rakentaminen ei saa rikkoa nykyistä RSS-jakelua tai sen kanonisia Pages-osoitteita.

## 2. Valvomo: seurannan tila

### 2.1 Automaatioiden erottelu

Valvomon on esitettävä automaatiot erillisinä kokonaisuuksina:

- **Pääautomaation yhdeksän aiheen kierto:** käsittelee kullakin ajolla vain yhden tehtäväjonossa määritellyn aiheen.
- **Intialaisten elokuvien näytösvahti:** erillinen päivittäinen automaatio; ei kuluta aihekierroksen vuoroa eikä kuulu pääautomaation lähde- tai raportointituloksiin.
- **Viikoittainen laatutarkistus:** erillinen, ensisijaisesti vain luku -auditointi, jonka rajatut seurantatietojen päivitysoikeudet säilyvät nykyisen käsikirjan mukaisina.

Valvomo ei saa yhdistää eri automaatioiden lähdehakuja, tuloksia, onnistumisaikoja tai virheitä yhdeksi harhaanjohtavaksi kokonaisluvuksi.

### 2.2 Ajovaiheet ja niiden tila

Pääautomaation ajosta pyritään näyttämään seuraavat vaiheet silloin, kun kyseinen vaihe kuuluu tehtävän käsittelyyn:

1. Käynnistys ja lähtötilan tarkistus.
2. Tehtävävuoron ja aihealueen valinta.
3. Lähteiden ja hakujen valmistelu.
4. Uutisten ja lähteiden haku.
5. Väitteiden varmistus, ristiriidat ja luotettavuusluokat.
6. Raportin muodostaminen.
7. RSS-/HTML-rakenteen ja julkaisuehtojen validointi.
8. GitHub-julkaisu.
9. Julkaisun takaisinluku ja lopputarkistus.

Näytösvahdille ja laatutarkistukselle määritellään omat vaiheensa niiden käsikirjojen perusteella. Pääautomaation vaihelistaa ei kopioida niihin sellaisenaan.

Kunkin vaiheen mahdolliset tilat:

- \u0060pending\u0060 – ei vielä aloitettu.
- \u0060running\u0060 – käynnissä.
- \u0060success\u0060 – onnistui.
- \u0060failed\u0060 – epäonnistui.
- \u0060skipped\u0060 – ohitettiin perustellusti.
- \u0060warning\u0060 – valmistui, mutta havaittiin huomioitava puute.

Näytä mahdollisuuksien mukaan aloitus- ja päättymisaika, kesto, lyhyt selite sekä varoituksen tai virheen kuvaus. Linkitä vastaavaan GitHub Actions -ajoon, kun linkki on saatavilla.

Pelkkä GitHub Actions -työn vihreä tila ei riitä osoittamaan koko toimitusketjun onnistumista. Erityisesti RSS-tiedoston kirjoitus, takaisinluku ja sisällön säilyminen on erotettava omiksi tarkistuksikseen.

### 2.3 Aihekierron eteneminen

Valvomon tulee näyttää kaikki yhdeksän aihekierroksen tehtävää todellisessa järjestyksessään, viimeisin onnistunut tarkistus aiheittain, nykyinen tai viimeksi käsitelty tehtävä, seuraavaksi vuorossa oleva tehtävä sekä epäonnistuneet, keskeytyneet ja perustellusti ohitetut vuorot.

Aiheen vuoroa ei saa merkitä valmiiksi pelkän käynnistymisen tai osittaisen haun perusteella. Vuoro siirtyy vasta, kun tehtävän onnistumiskriteerit täyttyvät, tarvittavat julkaisut on tehty ja tulokset on luettu takaisin. Valvomon tieto johdetaan ensisijaisesti repositorion koneellisesta seurantatilasta ja varmennetuista ajotiedoista; sitä ei ylläpidetä käsin erillisenä totuutena.

### 2.4 Lähteiden tarkistus ja kattavuus

Näytä mahdollisuuksien mukaan aihe- ja ajokohtaisesti rekisteröityjen lähteiden määrä, tarkistukseen valittujen lähteiden määrä, onnistuneesti tarkistettujen lähteiden määrä, epäonnistuneet haut ja tekniset virheet, tarkistamatta jääneet lähteet syineen sekä kieli-, alue- ja lähdetyyppijakauma.

Erottele aina **yritykset**, **onnistuneet noudot** ja **sisällöllisesti läpikäydyt lähteet**. Hakukyselyiden määrä tai rekisteröityjen lähteiden lukumäärä ei yksin todista kattavuutta. Prosenttilukua saa käyttää vain, jos sen nimittäjä ja laskentatapa on määritelty ja näkyvissä.

\u0060complete\u0060-merkintä tarkoittaa nykyisen lähderekisterin kriittisten lähteiden operatiivista käsittelyä, ei täydellistä maailmanlaajuista uutiskattavuutta. Näytösvahdin lähteet raportoidaan omassa kokonaisuudessaan.

### 2.5 Virheet, varoitukset ja historia

Valvomo näyttää viimeisimpien ajojen virheet ja varoitukset esimerkiksi seuraavissa luokissa: lähde tai verkkosivu ei ollut käytettävissä; haku jäi osittaiseksi; RSS/XML- tai HTML-validointi epäonnistui; seurantatilan tai tehtäväkierron eheys rikkoutui; GitHub-kirjoitus epäonnistui tai sen tulos jäi epäselväksi; takaisinlukutarkistus epäonnistui; virhe korjattiin automaattisesti uusintayrityksellä.

Erota avoin ongelma, korjattu ongelma ja tilapäinen varoitus. Säilytä riittävä ajohistoria trendien tarkasteluun, mutta älä julkaise raakoja lokitietoja, käyttöoikeustietoja, salaisuuksia tai tarpeettomia teknisiä yksityiskohtia.

### 2.6 Lähderekisterin selaus

Myöhemmässä vaiheessa valvomoon voidaan lisätä lähderekisterin selain, jossa lähteitä voi suodattaa aiheen, kielen, alueen, lähdetyypin ja kriittisyyden perusteella. Näytä lähteen tunniste ja rekisteritiedot sekä viimeisimmän tarkistuksen tulos, jos se on saatavilla.

## 3. RSS-lukija

### 3.1 Perustoiminnot

RSS-lukijan tulee lukea syötekatalogi koneellisesti ylläpidetystä luettelosta, yhdistää kaikkien valittujen syötteiden itemit yhdeksi aikajärjestykseen lajitelluksi virraksi ja näyttää oletuksena uusimmat artikkelit ensin.

Kustakin artikkelista näytetään otsikko, julkaisupäivä, aihe/syöte, ingressi tai kuvaus ja alkuperäisen artikkelin linkki. Kuva näytetään, jos RSS-itemissä on käyttökelpoinen kuva ja sen käyttö on turvallista. Lukutila tarjoaa artikkelin koko sisällön, kun RSS:n description sisältää koko HTML-artikkelin. Lähdelinkit säilytetään selkeinä ja alkuperäisen lähteen attribuutio pidetään näkyvissä.

Lukijan tulee tukea sekä yksittäisen syötteen että kaikkien syötteiden näkymää. Tyhjä syöte ei ole virhe eikä lukijaan lisätä keinotekoisia “ei uutisia” -artikkeleita.

### 3.2 Suodatus ja henkilökohtainen lukutila

Ensimmäisen tai myöhemmän kehitysvaiheen ominaisuuksia ovat aiheen/syötteen valinta, aikasuodattimet (esimerkiksi 24 tuntia, 7 päivää ja 30 päivää), otsikon ja artikkelisisällön tekstihaku, lukemattomien ja luettujen artikkeleiden erottelu, artikkelien tallentaminen myöhempää lukemista varten sekä lajittelu.

Luku- ja tallennustila voidaan aluksi säilyttää selaimen paikallisessa tallennustilassa. Tämä ei synkronoidu laitteiden välillä eikä ole käyttäjätiliin sidottu. Palvelinpuolen käyttäjätunnistusta tai tietokantaa ei lisätä ilman erillistä tarvetta ja suunnitelmaa.

Aihevalikoima johdetaan aina ajantasaisesta syötekatalogista, ei kovakoodatusta luettelosta. Nykyinen yhdeksän aiheen kierto, erillinen intialaisen elokuvan uutisraportti ja näytösfeed on esitettävä käyttäjälle oikein nimettyinä ja toisistaan erillisinä.

### 3.3 Turvallisuus ja HTML-sisältö

RSS:n description voi sisältää HTML:ää. Ulkoista HTML:ää ei saa renderöidä suoraan luotettuna sivun DOM-sisältönä.

- Puhdista HTML sallittujen elementtien ja attribuuttien listalla ennen lukutilassa näyttämistä.
- Estä skriptit, tapahtumankäsittelijät, vaaralliset URL-skeemat, lomakkeet ja mielivaltaiset upotukset.
- Käsittele YouTube-upotukset erikseen rajatulla sallittujen verkkotunnusten ja upotusmuotojen listalla; tarjoa aina myös tavallinen linkki.
- Tarkista kuvien ja linkkien URL-osoitteet sekä ulkoisen sisällön lataamisen yksityisyysvaikutukset.
- Säilytä lähteiden linkit, mutta älä anna lähdeartikkelin HTML:n muuttaa lukijan käyttöliittymää.
- Näytä puhdistettu artikkeli ja tarjoa linkki alkuperäiseen julkaisuun.

Sisältösuojaus ja sanitointi testataan erillisillä haitallisen HTML:n testitapauksilla. RSS-syötteen rakenteellinen validointi ei yksin riitä osoittamaan lukijan turvallisuutta.

## 4. Tietomalli ja datan tuottaminen

Ehdotetut koneellisesti luettavat julkiset tiedostot:

| Tiedosto | Sisältö |
|---|---|
| status/overview.json | Valvomon yhteenveto: automaatioiden viimeisin tila ja viimeisin päivitysaika |
| status/runs.json | Rajattu viimeaikainen ajohistoria ja vaihekohtaiset tulokset |
| status/sources.json | Lähteiden tarkistustulokset ja kattavuuden yhteenveto |
| status/rotation.json | Aihekierron järjestys, viimeisimmät tulokset ja seuraava vuoro |
| feeds/index.json | RSS-syötteiden katalogi: tunniste, nimi, aihe, URL ja automaatiovastuu |

Nämä ovat alustavia polkuja, eivät vielä olemassa olevia tiedostoja tai hyväksyttyjä skeemoja. Ennen toteutusta määritellään jokaiselle tiedostolle JSON Schema, versiointi, pakolliset kentät, aikaleimojen formaatti, päivitysvastuu ja vanhentuneen datan käsittely.

### 4.1 Datan alkuperä ja vastuut

- Automaatiot tuottavat ajokohtaiset tapahtumat ja lopputulokset oman käsikirjansa mukaisesti.
- Yhteinen julkaisuvaihe kokoaa sallitut, validoidut tiedot julkisiksi JSON-tiedostoiksi.
- GitHub Pagesin selainkäyttöliittymä lukee julkaistua dataa; se ei kirjoita repositorioon.
- RSS-syötteet pysyvät artikkeleiden ensisijaisina jakelutiedostoina.
- feeds/index.json muodostetaan nykyisestä syötekatalogista tai validoidaan sitä vasten, jotta syötteiden nimet ja URL-osoitteet eivät erkane README:stä ja muusta dokumentaatiosta.

Älä lisää jokaiseen automaatioajoon tarpeetonta commitia main-haaraan vain tilan näyttämiseksi. Ennen toteutusta vertaile vähintään seuraavia julkaisutapoja: GitHub Actionsin Pages-artifact, erillinen automaation tuottama status-haara tai julkisen GitHub Actions -rajapinnan lukeminen selaimesta. Huomioi API:n rajoitukset, saatavuus ja käyttöliittymän riippuvuus ulkoisesta rajapinnasta.

Valitse ratkaisu, joka minimoi commit-kohinan, säilyttää automaatioiden erilliset oikeudet ja julkaisee tilatiedot atomisesti. Älä julkaise raakaa lokia tai salaisuuksia.

### 4.2 Päivitys ja vanhentunut tila

Jokaisessa tilannekuvassa on oltava muodostamisaika ja tarvittaessa lähdeajon tunniste. Käyttöliittymän tulee näyttää, milloin tiedot on viimeksi päivitetty. Jos tietoa ei ole saatavilla tai se on liian vanhaa, näytä se vanhentuneena tai tuntemattomana; älä esitä viimeisintä tunnettua onnistumista käynnissä olevana ajona.

Jos julkaisu epäonnistuu, edellinen toimiva tilannekuva säilytetään eikä sivusto saa näyttää keskeneräistä tai virheellistä JSONia onnistuneena tilana.

## 5. Käyttöliittymä, saavutettavuus ja tietosuoja

Sivusto noudattaa repositorion saavutettavuusohjeen WCAG 2.2 AAA -tavoitetta soveltuvin osin. AAA-vaatimusten täyttymistä ei väitetä ilman asianmukaista testausta.

Valvomossa tilat esitetään tekstinä, ei pelkillä väreillä tai kuvakkeilla; dynaamiset tilapäivitykset ilmoitetaan ruudunlukijalle hallitusti; taulukot ja vaihelistat ovat semanttisia; kaavioille tarjotaan tekstimuotoinen vastine ja taulukkomuotoinen data; käyttö onnistuu näppäimistöllä ja fokus näkyy; käyttöliittymä toimii kapealla näytöllä ja suurennettuna.

RSS-lukijassa otsikkohierarkia on looginen, linkkitekstit kuvaavia, lukutila säilyttää artikkelin rakenteen ja kuville tarjotaan vaihtoehtotekstit. Luettu/luettava-tila ei erotu vain värillä.

Tietosuoja:
- Älä julkaise käyttäjätunnuksia, sähköpostiosoitteita, salaisuuksia, käyttöoikeustokeneita tai tarpeettomia henkilötietoja.
- Älä sisällytä julkiseen tilaan raakoja virhevastauksia, jotka voivat paljastaa salaisuuksia tai ympäristötietoja.
- Vältä ulkoisia seurantapikseleitä ja tarpeettomia kolmannen osapuolen pyyntöjä.
- Kerro selkeästi, jos lukutilan paikallinen tallennus käyttää selaimen tallennustilaa.

## 6. Testaus- ja hyväksymiskriteerit

### 6.1 Valvomon testit

- JSON-tiedostot validoituvat omia skeemojaan vasten.
- Ajot ja automaatiot pysyvät toisistaan erillisinä.
- Vaiheen failed, warning ja skipped -tilat näkyvät oikein.
- Epäonnistunut tai kesken jäänyt ajo ei siirrä aihekierrosta eikä viimeisintä onnistunutta tarkistusta.
- Lähteiden yritykset, onnistuneet tarkistukset ja tarkistamatta jääneet lähteet eivät sekoitu.
- Vanhentunut tai puuttuva data näkyy tuntemattomana/vanhentuneena.
- Julkiseen JSONiin ei päädy salaisuuksia tai raakaa lokisisältöä.
- Ajolinkit osoittavat oikeaan GitHub Actions -ajoon.

### 6.2 RSS-lukijan testit

- Syötekatalogin jokainen URL vastaa todellista Pages-RSS-osoitetta.
- Kaikkien syötteiden itemit voidaan jäsentää ja lajitella aikajärjestykseen.
- Tyhjät syötteet ja virheelliset yksittäiset itemit käsitellään hallitusti.
- Aihe- ja aikasuodattimet sekä haku toimivat.
- Luettu- ja tallennustila säilyvät selaimen uudelleenlatauksessa, jos paikallinen tallennus on käytössä.
- HTML-sanitointi estää skriptit, vaaralliset attribuutit ja kielletyt upotukset.
- YouTube-upotukset hyväksytään vain määritellyllä turvallisella tavalla.
- Ulkoisen sisällön virhe ei kaada koko lukijaa.

### 6.3 Julkaisun ja viittausten eheystestit

Jokaisessa muutoksessa tarkistetaan myös muutoksen vaikutus koko repositorion viittauksiin:

1. Uusien tiedostojen ja URL-osoitteiden kaikki viittaukset ovat oikein.
2. Muuttuneita tai poistettuja polkuja ei käytetä enää vanhoissa ohjeissa, skripteissä, testeissä tai asetuksissa.
3. README, Pages-julkaisun asetukset, työnkulut, syötekatalogi ja testit osoittavat samoihin tiedostoihin.
4. Testit tarkistavat koneellisesti keskeiset viittaukset ja skeemat.
5. Muutetut tiedostot luetaan takaisin GitHubista ja niiden sisältö tarkistetaan.
6. Pages-julkaisun jälkeen tarkistetaan, että sivusto ja julkiset JSON-/RSS-osoitteet todella toimivat.

Tarkista muutoksen jälkeen myös nykyisen Pages-julkaisun rakenne ja työnkulut; älä oleta, että ehdotetut hakemistot tai julkaisumekanismit ovat jo käytössä.

## 7. Kehitysvaiheet ja etenemisen seuranta

Toteutus tehdään vaiheittain. Jokainen vaihe saa oman testattavan muutoksensa ja hyväksymiskriteerinsä.

### Vaihe 0 – nykytilan kartoitus ja tietomallin hyväksyntä

- [ ] Tarkista nykyinen GitHub Pages -julkaisutyönkulku, sivuston juurihakemisto ja julkaisutapa.
- [ ] Tarkista nykyiset RSS-syötteet, niiden URLit, kaikki automaatiotyönkulut ja koneelliset seurantatiedostot.
- [ ] Päätä sivuston teknologia ja kansiorakenne nykyisen toteutuksen perusteella.
- [ ] Määrittele ja dokumentoi overview.json, runs.json, sources.json, rotation.json ja feeds/index.json -skeemat.
- [ ] Määrittele automaatioiden tiedonkeruun vastuut ja yhteinen julkaisuvaihe.
- [ ] Valitse tilatietojen julkaisumalli (Pages-artifact, erillinen haara tai rajattu API-luku).
- [ ] Määrittele tietojen säilytysajat, vanhentuneen tilan säännöt ja julkistettavien kenttien rajaus.

**Hyväksymiskriteeri:** tietomalli ja julkaisupolku on kuvattu niin tarkasti, että toteutuksen voi tehdä ilman arvailua. Nykyiset automaatiot ja RSS-julkaisu eivät muutu tässä vaiheessa.

### Vaihe 1 – valvomon vähimmäisversio

- [ ] Luo sivuston yhteinen runko, navigaatio ja saavutettava ulkoasu.
- [ ] Julkaise koneellisesti luettava yhteenveto automaatioiden viimeisimmästä tilasta.
- [ ] Näytä pääautomaation aihekierros, viimeisin onnistuminen ja seuraava tehtävä.
- [ ] Näytä näytösvahti ja laatutarkistus erillisinä automaatioina.
- [ ] Näytä viimeisimmän ajon vaiheet, varoitukset, virheet ja Actions-linkki.
- [ ] Näytä tiedon viimeisin päivitysaika ja vanhentuneen tiedon tila.
- [ ] Lisää JSON-skeemojen ja käyttöliittymän testit.

**Hyväksymiskriteeri:** valvomo näyttää todellisen, lähteistetyn koneellisen tilan; epäonnistumista ei esitetä onnistumisena eikä automaatioiden tietoja sekoiteta.

### Vaihe 2 – RSS-lukijan vähimmäisversio

- [ ] Luo syötekatalogi nykyisistä kymmenestä RSS-syötteestä.
- [ ] Näytä kaikkien syötteiden artikkelit yhteisessä aikajärjestyksessä.
- [ ] Lisää syötekohtainen suodatus ja artikkelin alkuperäislinkki.
- [ ] Lisää koko artikkelin lukutila turvallisesti puhdistetulla HTML:llä.
- [ ] Lisää RSS-jäsennyksen ja sanitoinnin testit.

**Hyväksymiskriteeri:** kaikki nykyiset syötteet näkyvät oikein, artikkelit eivät sekoitu aiheesta toiseen ja ulkoinen HTML ei voi suorittaa koodia lukijan sivulla.

### Vaihe 3 – lukijan käyttömukavuus ja lähdenäkymä

- [ ] Lisää aikasuodattimet ja otsikko-/sisältöhaku.
- [ ] Lisää selaimeen tallentuva luettu/luettava-tila.
- [ ] Lisää artikkelien tallentaminen myöhempää lukemista varten.
- [ ] Lisää lähderekisterin selaus ja lähdekattavuuden yhteenveto.
- [ ] Lisää kattavuuden tekstimuotoiset selitteet ja tarvittaessa kaaviot.

**Hyväksymiskriteeri:** lukija toimii käytännöllisesti myös suurella artikkelimäärällä ja lähdekattavuuden esitystapa ei liioittele tietojen kattavuutta.

### Vaihe 4 – raporttiarkisto ja jatkokehitys

- [ ] Arvioi erillisen raporttiarkiston hyöty ja päällekkäisyys RSS-lukijan kanssa.
- [ ] Toteuta arkisto vain, jos sille on selkeä käyttötapaus.
- [ ] Lisää mahdolliset pitkän aikavälin trendit, historiakaaviot ja laajennetut lähdenäkymät vasta todellisen datan perusteella.

**Hyväksymiskriteeri:** lisäominaisuudet perustuvat todelliseen käyttötarpeeseen eivätkä lisää tarpeetonta ylläpitokuormaa.

## 8. Rajaukset ja päätökset, joita ei tehdä vielä

- Ei käyttäjätilejä, kirjautumista tai palvelinpuolen henkilökohtaista tietokantaa ensimmäisessä versiossa.
- Ei selaimesta tehtäviä GitHub-kirjoituksia eikä GitHub-salaisuuksien siirtämistä Pages-sivulle.
- Ei raakaa Actions-lokia julkiseksi.
- Ei lähdekattavuuden prosenttilukua ilman määriteltyä nimittäjää ja luotettavaa havaintodataa.
- Ei uusia erillisiä uutisautomaatioita vain käyttöliittymän vuoksi.
- Ei näytösseurannan siirtämistä pääautomaation aihekierrokseen.
- Ei RSS-artikkelien kopiointia toiseen tietolähteeseen, jos RSS jo toimii arkistona riittävän hyvin.
- Ei WCAG 2.2 AAA -vaatimustenmukaisuuden väitettä ennen dokumentoitua testausta.

## 9. Muutosloki

- **2026-11-16:** ensimmäinen tavoitekuvaus ja vaiheistettu kehityssuunnitelma kirjattu. Valvomon ja RSS-lukijan toteutusta ei ole vielä aloitettu.
