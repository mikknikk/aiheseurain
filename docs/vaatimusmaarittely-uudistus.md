# Aiheseuraimen vaatimusmäärittely – uudistettu tavoitetila

**Versio:** 0.4.0  
**Tila:** luonnos – ei hyväksytty eikä toteutuksen lupa  
**Päiväys:** 20.11.2026  
**Toimintamalli:** ChatGPT  
**Suunnitteluperiaate:** yksinkertainen (simple)  
**Kohderepositorio:** `mikknikk/aiheseurain`

> Tämä dokumentti kuvaa uudistettavan Aiheseuraimen tavoitetilan vaatimuksia. Se ei kuvaa nykyisen repositorion kaikkia toteutuksia eikä muuta niitä. Nykyiset automaatiot, niiden ajastukset, käynnistyskehotteet, kohdekeskustelut, RSS-julkaisut ja tuotantotilat säilyvät ennallaan, kunnes niihin tehdään erikseen hyväksyttyjä muutoksia. Luonnoksen hyväksyminen ja toteutuksen aloittaminen ovat erillisiä päätöksiä.

## 1. Tarkoitus ja rajaus

Aiheseurain on ChatGPT:n avulla toimiva, useita aiheita ja seurantatyyppejä käsittelevä järjestelmä. Se etsii ja arvioi tietoa, tuottaa suomenkielisiä raportteja ja tallentaa ajotiedot, joiden avulla järjestelmän toimintaa voidaan valvoa ja kehittää.

Tämän määrittelyn tavoitteena on kuvata mahdollisimman yksinkertainen toimintamalli, jossa:
- ChatGPT tekee varsinaisen tutkimus- ja raportointityön.
- GitHub säilyttää seurannan määritykset, validointisäännöt, ajotiedot ja julkaistut RSS-syötteet.
- Jokainen ajo palauttaa yhden rakenteisen ajotuloksen.
- RSS-item ja Valvomon tarvitsema ajodata ovat erillisiä mutta samaan ajoon sidottuja tietoja.
- Valvomo on ensisijainen käyttöliittymä järjestelmän toiminnan ymmärtämiseen.
- RSS-lukija ja Kehitysjono säilyvät omissa käyttötarkoituksissaan.

Tämä on vaatimusmäärittely, ei tekninen toteutussuunnitelma. Siinä ei lukita siirtomekanismia, tietokantaa, käyttöliittymäkirjastoa tai muuta yksityiskohtaista teknologiaa, ellei vaatimus sitä edellytä.

## 2. Suunnitteluperiaatteet

1. **Yksinkertaisuus:** ratkaistaan tarve mahdollisimman vähillä komponenteilla, tietovarastoilla ja prosessivaiheilla.
2. **ChatGPT tekee seurannan:** tiedonhaku, lähteiden arviointi, havaintojen yhdistäminen ja raportin kirjoittaminen kuuluvat ChatGPT:lle.
3. **GitHub hallitsee määrittelyjä ja julkaisemista:** aiheiden asetukset, lähderekisterit, raporttien rakenne, skeemat, validointi ja RSS-julkaisun säännöt ylläpidetään GitHubissa.
4. **Yksi yhteinen ajomalli:** kaikki aiheet ja seurantatyypit käyttävät samaa perusprosessia.
5. **Aihekohtainen erillisyys:** yhden aiheen ajo ei saa sekoittaa toisen aiheen lähteitä, havaintoja, raportteja tai tilaa.
6. **Dynaamiset aiheet:** yleinen vaatimusmäärittely ei sisällä kiinteää aihelistaa. Aiheita hallitaan GitHubin määrityksillä.
7. **Määrityspohjaisuus:** aiheiden erot, kuten seurantatiheys, sisältö, tapahtumatyypit ja raporttipohja, kuvataan asetuksilla ja seurantatyypillä.
8. **Muuttumaton julkaisuhistoria:** julkaistuja RSS-itemeitä ei automaattisesti muokata, poisteta eikä korvata. Korjaus julkaistaan uutena iteminä, joka viittaa alkuperäiseen.
9. **Ei tarpeetonta rinnakkaisuutta:** samaa tilatietoa ei ylläpidetä useassa toisistaan riippumattomassa tiedostossa tai tietokannassa.
10. **Turvallinen epäonnistuminen:** epäselvä tai virheellinen tulos ei saa johtaa virheelliseen RSS-julkaisuun tai onnistumisen esittämiseen.

## 3. Käyttöliittymät ja niiden tärkeysjärjestys

### 3.1 Valvomo – ensisijainen käyttöliittymä

Valvomo on järjestelmän tärkein käyttöliittymä. Sen tehtävä on vastata kysymyksiin:
- Mitä järjestelmässä tapahtuu juuri nyt?
- Mitkä ajot ovat onnistuneet, epäonnistuneet tai jääneet kesken?
- Mitä aiheita on seurattu ja milloin?
- Kuinka kattavasti lähteet tarkistettiin?
- Syntyikö raportti ja julkaistiinko se?
- Mitä seuraavaksi pitäisi tapahtua?
- Onko järjestelmässä ongelmia, poikkeamia tai kehitystarpeita?

Valvomon tulee pystyä näyttämään myös ajot, joista ei syntynyt RSS-itemiä. Se ei saa päätellä ajon tilaa pelkästään RSS-syötteistä.

Valvomo käyttää rakenteista ajodataa ja muuta GitHubissa ylläpidettyä tietoa. Sen ei pidä tarvita raakaa tutkimustekstiä tai RSS-itemien läpikäyntiä ajotilanteen päättelemiseksi.

### 3.2 RSS-lukija – säilytettävä toissijainen käyttöliittymä

RSS-lukija kokoaa julkaistut raportit luettavaksi. Sen tehtävä on:
- näyttää eri aiheiden julkaistut RSS-itemit;
- tarjota syötekohtainen suodatus ja yhteinen aikajärjestys;
- mahdollistaa raportin lukeminen ja lähteiden avaaminen;
- käsitellä tyhjät syötteet ja virheelliset yksittäiset itemit hallitusti.

RSS-lukija ei ole ajotilanteen tai lähdekattavuuden ensisijainen tietolähde.

### 3.3 Kehitysjono – säilytettävä toissijainen käyttöliittymä

Kehitysjono näyttää GitHub Issues -tehtävät ja niiden tilat. GitHub Issues säilyy kehitystehtävien kanonisena lähteenä. Kehitysjono on Valvomosta erillinen käyttötarkoitus, eikä sen tietomallia pidä sekoittaa seurantojen ajotietoihin.

### 3.4 Yhteinen sivusto

Valvomo, RSS-lukija ja Kehitysjono voivat olla saman GitHub Pages -sivuston osia. Niiden käyttöliittymät ja käyttötarkoitukset pysyvät kuitenkin erillisinä. Yhteinen sivustorunko ei edellytä erillisiä taustapalveluja.

## 4. Aiheiden ja seurantatyyppien hallinta

### 4.1 Dynaamiset aiheet

- Aiheita ei luetella kiinteästi tässä yleisessä määrittelyssä.
- Jokaisella aiheella on oma GitHubissa ylläpidettävä määritystiedosto.
- Aihe voidaan ottaa käyttöön, poistaa käytöstä tai muuttaa määrityksellä ilman yleisen toimintamallin muuttamista.
- Aihekohtainen lähderekisteri ja raporttipohja voidaan ylläpitää erillään muiden aiheiden tiedoista.
- Uusi aihe ei saa vaatia koodimuutosta, jos sen tarpeet voidaan toteuttaa jo olemassa olevalla seurantatyypillä ja raporttipohjalla.

### 4.2 Yhteinen määritys ja aihekohtainen määritys

Määritysmalli on hybridimalli:
- yhteinen määritys sisältää kaikkia aiheita koskevat säännöt, tietosopimukset, julkaisun turvallisuusehdot ja yleiset oletukset;
- aihekohtainen määritys sisältää aiheen tunnisteen ja nimen, seurantatyypin, ohjeet, lähderekisterin, raporttipohjan, aktiivisuuden ja ajotiheyden.

Aihekohtainen määritys ei saa ohittaa yhteisiä turvallisuus-, eheys- tai julkaisusääntöjä.

### 4.3 Seurantatyypit ja raporttipohjat

Kaikki aiheet käyttävät yhteistä suoritusprosessia. Seurantatyyppi määrittelee, millaisia havaintoja etsitään, mitä luokituksia tarvitaan ja mitä erityisiä tarkistuksia tehdään. Raporttipohja määrittelee RSS-raportin rakenteen.

Esimerkiksi tapahtuma- tai näytösseuranta voi käyttää samaa ajomallia kuin uutisseuranta, mutta sen oma määritys ja raporttipohja voivat käsitellä tapahtumapäiviä, tulevia ja menneitä näytöksiä sekä tapahtumien muutoksia.

Uuden seurantatyypin lisääminen voi vaatia teknistä toteutusta. Sen pitää kuitenkin olla rajattu laajennus yhteiseen järjestelmään, ei kokonaan erillinen automaatioarkkitehtuuri.

### 4.4 Aikataulut ja ajovuoro

- Ajotiheys määritellään aihekohtaisesti.
- Yhteinen ajonvalinta käsittelee erääntyvät aiheet niiden määritysten mukaisesti.
- Päivittäistä seurantaa tarvitseva aihe voidaan ajaa päivittäin; harvemmin seurattava aihe voidaan ajaa harvemmin.
- Aiheiden keskinäinen tasapuolisuus ja erääntyneiden ajojen järjestys ratkaistaan yksinkertaisella jonosäännöllä.
- Ajon epäonnistuminen ei saa hiljaisesti merkitä aihetta onnistuneesti käsitellyksi.
- Käyttäjän erikseen käynnistämä ajo voidaan erottaa ajastetusta ajosta.

Näytösseuranta on muiden aiheiden kanssa samanarvoinen seurantakohde yhteisessä järjestelmässä. Sen päivittäinen rytmi ja tapahtumakohtaiset tarpeet määritellään sen omassa konfiguraatiossa ja seurantatyypissä. Sitä ei toteuteta erillisenä rinnakkaisena järjestelmänä vain siksi, että sen ajotiheys tai raporttipohja poikkeaa muista.

ChatGPT:n ajastuksen ja GitHubissa olevan määrityksen välinen tekninen toteutustapa selvitetään erikseen. Tämä määrittely ei oleta, että GitHub-määrityksen muutos muuttaisi automaattisesti ChatGPT:n tehtävän ajastusasetuksia.

## 5. Ajon suoritusprosessi

Jokainen ajo noudattaa samaa loogista kulkua:

1. **Valinta:** valitaan aihe, jonka ajo on erääntynyt tai joka on käynnistetty erikseen.
2. **Määritysten luku:** luetaan yhteiset säännöt ja aiheen oma määritys sekä niiden versiot.
3. **Ajon aloitus:** luodaan yksilöllinen `run_id` ja kirjataan ajon alkutiedot.
4. **Tutkimus:** ChatGPT tarkistaa määritellyt lähteet ja etsii seurantajakson aikana syntyneitä olennaisia uusia havaintoja.
5. **Arviointi:** lähteiden luotettavuus, havaintojen uutuus ja raportointikelpoisuus arvioidaan seurantatyypin sääntöjen mukaisesti.
6. **Raportointi:** jos raportoitavaa on, ChatGPT tuottaa yhden rakenteisen RSS-itemin. Jos raportoitavaa ei ole, RSS-item jätetään pois.
7. **Ajotuloksen muodostus:** ChatGPT tuottaa aina ajotiedot, myös silloin kun raporttia ei synny tai ajo epäonnistuu.
8. **Vastaanotto ja validointi:** GitHub tarkistaa ajotuloksen rakenteen, tunnisteet, määritysversiot, kohdeaiheen ja julkaisemisen ehdot.
9. **Tallennus ja julkaisu:** GitHub tallentaa ajotiedot ja lisää hyväksytyn RSS-itemin oikeaan syötteeseen muuttamatta aiempia itemeitä.
10. **Varmistus:** RSS/XML:n kelvollisuus, GUIDien yksilöllisyys, itemin oikea kohdesyöte ja tallennuksen onnistuminen tarkistetaan.
11. **Tilapäivitys:** aiheen viimeisin onnistunut ajo, seuraava erääntymisaika ja jonotila päivitetään vasta hyväksytyn lopputuloksen perusteella.

Tämä on looginen prosessi. Tiedonsiirron tarkka tekninen mekanismi ChatGPT:n ja GitHubin välillä valitaan erillisessä toteutussuunnittelussa. Vaatimus ei saa riippua oletuksesta, että ChatGPT voi käyttää mitä tahansa GitHub-rajapintaa tai kirjoittaa suoraan repositorioon.

## 6. Ajon tulos: raportti ja ajotiedot

### 6.1 Yksi rakenteinen ajotulos

Jokainen ajo tuottaa yhden rakenteisen tuloksen, jossa on kaksi selvästi erotettua osaa:

- `run_metadata`: pakolliset ajotiedot Valvomoa, historiatietoa ja järjestelmän hallintaa varten;
- `report_item`: valinnainen uusi RSS-item.

Näiden osien yhteinen `run_id` yhdistää raportin ja ajon. Raporttia ei tuoteta uudelleen GitHubissa eikä ChatGPT palauta koko RSS-syötettä.

### 6.2 Ajotietojen vähimmäissisältö

Ajotietojen tarkka skeema suunnitellaan myöhemmin, mutta niiden pitää mahdollistaa vähintään seuraavien asioiden näyttäminen ja tarkistaminen:

| Tietoryhmä | Tarvittavat tiedot |
|---|---|
| Tunnisteet | `run_id`, aihe-/moduulitunniste, seurantatyyppi, käynnistystapa |
| Määritykset | käytetty yhteisen määrityksen ja aiheen määrityksen versio |
| Ajanjakso | seurannan alku ja loppu sekä ajon aloitus- ja lopetusajat |
| Tila | jonossa, käynnissä, onnistunut, osittainen tai epäonnistunut |
| Vaiheet | suoritetut vaiheet ja niiden tulokset; pysähtymisvaihe virhetilanteessa |
| Havainnot | löydettyjen olennaisten havaintojen määrä ja raportoitavien havaintojen määrä |
| Lähteet | tarkistetut lähteet, onnistuneet tarkistukset, tarkistamatta jääneet lähteet ja niiden syyt |
| Laadunvarmistus | validoinnin tulos, virheet, varoitukset ja mahdollinen hylkäyksen syy |
| Raportti | syntyikö RSS-item, sen GUID/tunniste ja otsikko, jos ne ovat olemassa |
| Julkaisu | kohdesyöte, julkaisun tila ja julkaisuajankohta |
| Jatko | uudelleenyrityksen tarve, seuraava erääntymisaika ja jonon päivityksen tulos |

Valvomon myöhempää kehitystä varten ajotiedoissa voidaan lisäksi säilyttää vertailukelpoisia lukumääriä ja poikkeamatietoja, kuten lähdekattavuuden muutos tai poikkeuksellisen pitkä ajo. Niiden tulee perustua todellisiin havaintoihin eikä arvattuihin mittareihin.

### 6.3 Ajotiedot eivät ole raakaa lokia

Ajotietojen tarkoitus on kuvata, mitä tapahtui ja millä tuloksella. Niihin ei tallenneta tarpeettomasti koko tutkimusketjua, raakaa keskustelutekstiä tai kaikkia lähdesivuista kopioituja sisältöjä.

Salaisuuksia, käyttöoikeustunnuksia, tarpeettomia henkilötietoja tai raakoja teknisiä virhevastauksia ei saa julkaista Valvomolle näkyvässä datassa. Virheet esitetään turvallisina, ymmärrettävinä virheluokkina ja selitteinä.

## 7. RSS-julkaiseminen

- Jokainen aihe julkaisee omaan RSS-syötteeseensä; aiheita ei sekoiteta samaan syötteeseen.
- RSS-item sisältää koko raportin.
- RSS-itemissä ei käytetä erillistä `<link>`-elementtiä. Lähdelinkit esitetään raportin lopun lähdeluettelossa.
- Itemillä on yksilöllinen GUID.
- Raportti on suomenkielinen ja sisältää aina seurannan aikavälin.
- Lähteiden luotettavuus ja olennaiset epävarmuudet ilmaistaan aihekohtaisen raporttipohjan mukaisesti.
- ChatGPT tuottaa vain yhden uuden itemin kerrallaan.
- GitHub validoi itemin ja lisää sen oikean aiheen syötteeseen.
- GitHub ei pyydä ChatGPT:tä muodostamaan koko RSS-syötettä uudelleen.
- Aiemmin julkaistujen itemien sisältöä, GUID-tunnisteita tai järjestystä ei muuteta automaattisesti.
- Korjaus tehdään uutena erillisenä iteminä, joka viittaa korjattavaan julkaisuun.
- RSS/XML validoidaan jokaisen julkaisun yhteydessä.
- Julkaisu ja ajotietojen tallennus toteutetaan niin, ettei virheellinen tai puoliksi tallennettu julkaisu näy onnistuneena.

Jos ajo onnistuu mutta uutta raportoitavaa ei löydy, ajotiedot tallennetaan ja Valvomo näyttää onnistuneen ajon ilman uutta RSS-julkaisua. Keinotekoisia ”ei uutisia” -RSS-itemeitä ei luoda.

## 8. Valvomon tietotarpeet ja näkymät

Valvomon tietomalli suunnitellaan ennen sen seuraavaa laajaa käyttöliittymäuudistusta. Tietomallin tulee tukea nykyisen Valvomon kehittämistä ja myöhempiä näkymiä ilman, että jokaista uutta näkymää varten muutetaan ChatGPT:n tutkimusprosessia.

### 8.1 Keskeiset näkymät

Valvomon vähimmäiskokonaisuuteen kuuluvat:

1. **Yleiskuva:** järjestelmän tila, käynnissä olevat ja viimeisimmät ajot, ongelmat ja viimeisin päivitysaika.
2. **Aihekohtainen näkymä:** aiheen määritykset, viimeisimmät ajot, seurannan aikavälit, lähdekattavuus, raporttien määrä ja seuraava erääntymisaika.
3. **Ajohistoria:** ajon vaiheet, kesto, tulos, varoitukset, virheet ja linkit mahdollisiin julkaistuihin itemeihin.
4. **Lähdekattavuus:** mitä lähteitä tarkistettiin, mitkä jäivät tarkistamatta ja miksi; kattavuusmittarin nimittäjä ja laskentatapa on määriteltävä.
5. **Julkaisutilanne:** syntyikö item, validoitiinko se, mihin syötteeseen se lisättiin ja varmistettiinko julkaisu.
6. **Poikkeamat ja järjestelmän terveys:** toistuvat virheet, vanhentunut tieto, epäonnistuneet julkaisut ja muut todelliseen ajodataan perustuvat ongelmat.

### 8.2 Valvomon tiedon tulkinta

- Valvomo erottaa ajon onnistumisen, raportin syntymisen ja RSS-julkaisun onnistumisen toisistaan.
- Puuttuva tieto esitetään tuntemattomana, ei onnistumisena tai epäonnistumisena.
- Vanhentunutta tilaa ei esitetä ajantasaisena.
- Käynnissä-tila näytetään vain, jos ajosta on tuore ja todennettava käynnissä-merkintä.
- Osittainen lähdetarkistus ei muutu täydelliseksi vain siksi, että ajo tuotti raportin.
- Ajotietojen mittareille määritellään yksiselitteiset laskentasäännöt. Prosenttilukuja ei näytetä ilman luotettavaa nimittäjää.
- Historiatietoja ei korvata viimeisimmän ajon tilannekuvalla.

### 8.3 Valvomon tietojen säilytys

Ajotiedot säilytetään niin, että Valvomo voi näyttää sekä viimeisimmän tilanteen että aiemmat ajot. Yksi kanoninen ajohistoria riittää; samaa tietoa ei kopioida useisiin rinnakkaisiin tilatiedostoihin. Nykytilan yhteenveto voidaan muodostaa historiasta tai ylläpitää kevyenä johdettuna tietona, jos synkronointi voidaan validoida.

## 9. GitHubin vastuut

GitHubin tehtävät ovat:
- säilyttää yhteiset ja aihekohtaiset määritykset;
- säilyttää aihekohtaiset lähderekisterit ja raporttipohjat;
- määritellä ajotuloksen ja RSS-itemin skeemat;
- vastaanottaa ChatGPT:n rakenteinen ajotulos valittavan siirtomekanismin kautta;
- tarkistaa tunnisteet, skeema, määritysversiot, aihekohtaisuus ja julkaisuehdot;
- estää saman ajon tai RSS-itemin julkaiseminen kahdesti;
- tallentaa ajotiedot myös silloin, kun raporttia ei synny;
- lisätä hyväksytty uusi item oikeaan RSS-syötteeseen;
- säilyttää aiemmat julkaisut muuttumattomina;
- validoida RSS ja ajotiedot sekä julkaista hyväksytty muutos;
- tarjota Valvomolle luettavat, rakenteiset ja turvalliset tietolähteet.

GitHubin validointi on julkaisun portinvartija. ChatGPT:n tuottamaa sisältöä ei julkaista vain siksi, että se näyttää valmiilta.

## 10. Virhetilanteet ja uudelleenyritykset

Virhetilanteet käsitellään yksinkertaisella, yksiselitteisellä tavalla:

- **Tutkimusvirhe:** ajotulos kertoo virheen ja sen vaiheen; raporttia ei julkaista, ellei erikseen määritelty osittainen tulos täytä julkaisuehtoja.
- **Osittainen lähdekattavuus:** tallennetaan tarkistetut ja tarkistamatta jääneet lähteet sekä syyt. Valvomo näyttää tuloksen osittaisena.
- **Virheellinen ajotulos:** GitHub hylkää tuloksen; RSS-syöte ei muutu.
- **Väärä aihe tai määritysversio:** tulos hylätään, eikä sitä reititetä toiseen aiheeseen arvaamalla.
- **Duplikaatti:** samaa `run_id`-tunnistetta tai RSS-GUIDia ei käsitellä uutena julkaisuna.
- **Julkaisuvirhe:** ajoa ei merkitä julkaistuksi ennen kuin GitHubin tallennus ja julkinen julkaisu on varmennettu.
- **Uudelleenyritys:** käyttää samaa ajon tunnistetta vain silloin, kun se on saman loogisen ajon turvallinen jatko. Uusi erillinen ajo saa uuden tunnisteen.
- **Jonon päivitys:** epäonnistunut ajo ei saa kadota jonosta eikä siirtää seuraavaa erääntymistä ikään kuin ajo olisi onnistunut.

Valvomo näyttää virheluokan, lyhyen selitteen, epäonnistuneen vaiheen ja sen, onko uudelleenyritys mahdollinen tai jo tehty.

## 11. Turvallisuus, eheys ja testaus

- Testit eivät saa kirjoittaa tuotannon RSS-syötteisiin tai muuttaa tuotannon seurantatilaa.
- Testiaineisto ja tuotantoaineisto pidetään erillään.
- Julkaistujen RSS-itemien muuttumattomuus testataan.
- Ajon tunnisteiden ja GUIDien yksilöllisyys testataan.
- Väärään aiheeseen reitittäminen estetään testeillä.
- RSS/XML:n, ajotuloksen ja määritysten skeemat validoidaan automaattisesti.
- Julkaisun epäonnistuminen ei saa jättää syötettä virheelliseen tai osittaiseen tilaan.
- Valvomo ei saa sisältää GitHub-kirjoitustunnuksia tai muita salaisuuksia.
- Käyttöliittymän saavutettavuus testataan. WCAG 2.2 AAA -vaatimustenmukaisuutta ei väitetä ilman asianmukaisia testejä.
- Uusien skriptien tulee sisältää ymmärrettävät kommentit myös ylläpitäjälle, joka ei ole ohjelmoinnin asiantuntija.

## 12. Toteutuksen ulkopuolelle rajatut asiat

Tässä vaiheessa ei:
- muuteta nykyisiä ChatGPT-automaatiota, niiden ajastuksia, suoritusvälejä, aikavyöhykkeitä, käynnistyskehotteita tai kohdekeskusteluja;
- aktivoida seurantamoduuleja tai käynnistetä tuotantojulkaisuja;
- toteuteta uutta teknistä arkkitehtuuria ennen vaatimusmäärittelyn ja toteutussuunnitelman hyväksyntää;
- luoda tarpeettomia rinnakkaisia agentteja, tietokantoja tai julkaisupolkuja;
- lukita tiedonsiirtomekanismia ennen sen teknisen toteutettavuuden selvittämistä;
- kopioida koko RSS-syötettä ChatGPT:n käsiteltäväksi ja palautettavaksi;
- muokata tai poistaa vanhoja RSS-itemeitä automaattisesti;
- tehdä Valvomosta RSS-lukijan tai Kehitysjonon korvaajaa.

## 13. Hyväksymiskriteerit

Vaatimusmäärittely täyttää tavoitteensa, kun toteutuksen suunnittelussa voidaan osoittaa, että:

1. ChatGPT vastaa varsinaisesta aihekohtaisesta tutkimuksesta ja raportin tuottamisesta.
2. Aiheiden lisääminen ja muuttaminen tapahtuu ensisijaisesti GitHubin määrityksillä.
3. Kaikki aiheet käyttävät samaa perusajoprosessia ja seurantatyypit erottuvat määritysten ja raporttipohjien avulla.
4. Myös päivittäinen näytösseuranta on samanarvoinen aihekohtainen ajo, ei erillinen rinnakkaisarkkitehtuuri.
5. Jokainen ajo tuottaa ajotiedot; RSS-item on valinnainen.
6. ChatGPT tuottaa enintään yhden uuden rakenteisen RSS-itemin yhtä raportoitavaa ajoa kohti, ei kokonaista RSS-syötettä.
7. GitHub validoi ja lisää hyväksytyn itemin oikeaan syötteeseen.
8. Julkaistujen itemien historia säilyy muuttumattomana.
9. Valvomo pystyy näyttämään ajot, vaiheet, tulokset, lähdekattavuuden, julkaisut ja virheet myös ilman uutta RSS-itemiä.
10. RSS-lukija ja Kehitysjono säilyvät toimivina erillisinä käyttöliittyminä.
11. Virheet, uusintayritykset ja jonon eteneminen ovat yksiselitteisiä.
12. Testaus estää tuotantodatan tahattoman muuttamisen.
13. Toteutus ei edellytä tarpeettoman monimutkaista rinnakkaisarkkitehtuuria.

## 14. Avoimet suunnittelukysymykset

Seuraavat asiat ratkaistaan vasta tämän vaatimusmäärittelyn tarkastelun ja hyväksymisen jälkeen:

1. **Ajotuloksen täsmällinen skeema:** kentät, pakollisuus, versiointi ja esimerkkitulos.
2. **Ajotietojen tallennusmuoto:** yksi ajotietue per ajo, tapahtumahistoria vai näiden yksinkertainen yhdistelmä.
3. **ChatGPT–GitHub-siirto:** mikä käytettävissä oleva tekninen tapa siirtää ajotulos turvallisesti GitHubiin.
4. **Ajojen käynnistäminen:** miten GitHubissa olevat ajotiheydet ja ChatGPT:n ajastetut tehtävät sovitetaan yhteen muuttamatta nykyisiä tehtäviä ilman lupaa.
5. **Jonon valintasääntö:** miten eri ajotiheyksillä erääntyvät aiheet järjestetään ja miten epäonnistunut ajo vaikuttaa seuraaviin.
6. **Valvomon näkymien priorisointi:** mitkä näkymät kuuluvat ensimmäiseen toteutusvaiheeseen.
7. **Historiatietojen säilytys:** kuinka paljon yksityiskohtaista ajohistoriaa säilytetään ja miten vanha tieto arkistoidaan.
8. **Nykyisen toteutuksen siirtymä:** mitkä nykyisen repositorion osat voidaan hyödyntää, mitkä ovat tarpeettoman monimutkaisia ja mitkä pitää korvata. Mitään ei poisteta ennen erillistä suunnitelmaa.

## 15. Ajastettujen käynnistyskehotteiden versionhallinta

Jokaisella Aiheseuraimen ajastetulla ChatGPT-tehtävällä on yksilöllinen tehtävätunniste ja oma kanoninen käynnistyskehote. Kehotteen sisältöä hallitaan GitHubissa versioituna tekstinä. Tehtävän tunniste ja kehotteen versio ovat eri asioita: tehtävätunniste pysyy samana, kun saman tehtävän kehotetta päivitetään.

Vaatimukset:

- Kanoniset käynnistyskehotteet säilytetään repositorion `prompts/`-hakemistossa. Jokaisesta julkaistusta versiosta säilytetään muuttumaton oma tiedosto muodossa `prompts/<task_id>/v<version>.txt`.
- Kehotetiedosto sisältää täsmälleen ChatGPT-tehtävän asetuksiin kopioitavan tekstin. Tiedostoon ei lisätä otsikoita, kommentteja tai muuta kehotteeseen kuulumatonta sisältöä.
- Jokaisella kehotteella on semanttinen versionumero (`MAJOR.MINOR.PATCH`). PATCH tarkoittaa rajattua korjausta, MINOR yhteensopivaa toiminnallista lisäystä ja MAJOR yhteensopimatonta tai tehtävän toimintaa olennaisesti muuttavaa muutosta.
- `prompts/registry.json` ylläpitää tehtävätunnisteen, GitHubissa olevan uusimman kanonisen version, ChatGPT-tehtävässä käytössä olevaksi vahvistetun version, vahvistuksen ajankohdan ja tilan. Uuden järjestelmän tehtävät lisätään rekisteriin vasta, kun ne määritellään; vanhan järjestelmän tehtäviä ei palauteta automaattisesti.
- ChatGPT-tehtävän asetuksissa oleva versio on erillinen tieto. GitHubissa julkaistu uusi versio ei tarkoita, että ChatGPT-tehtävä olisi jo päivitetty.
- Kehotteen muuttaminen edellyttää käyttäjän nimenomaista lupaa ChatGPT-tehtävän asetusten muuttamiseen. GitHubin kanonisen tekstin päivittäminen ja ChatGPT-asetusten muuttaminen ovat erillisiä vaiheita.
- Käytössä olevan version teksti täsmäytetään ChatGPT-tehtävän asetuksiin tallennettuun tekstiin. Vasta täsmäytyksen jälkeen rekisteriin merkitään uusi versio käyttöön vahvistetuksi.
- Ajon alussa tarkistetaan tehtävätunniste ja kehotteen versio. Jos tunniste tai versio puuttuu, on ristiriidassa rekisterin kanssa tai käytössä olevan kehotteen vastaavuutta ei ole vahvistettu, ajo keskeytetään ennen seurantatyötä ja ristiriita raportoidaan.
- Vanhoja kehotetiedostoja ei ylikirjoiteta eikä poisteta. Palautus aiempaan versioon tehdään uutena rekisteröitynä käyttöönottona; historiatiedosto säilyy.
- Kehotteen muutos ei saa muuttaa ajastusta, aikavyöhykettä tai kohdekeskustelua. Niihin sovelletaan erillistä automaatioiden hallinnan suojausperiaatetta.

Kehotteiden tarkka tiedostorakenne, rekisterin kentät ja päivitysmenettely kuvataan dokumentissa [käynnistyskehotteiden versionhallinta](../prompts/README.md).

## 16. Muutosloki

- **0.4.0 – 20.11.2026:** palautettu ajastettujen ChatGPT-käynnistyskehotteiden tehtäväkohtainen versionhallinta. Määritelty muuttumattomat versiotiedostot, tehtävärekisteri, ChatGPT:ssä käytössä olevan version erillinen vahvistaminen sekä ajon alun versiotarkistus.
- **0.3.0 – 20.11.2026:** lisätty ajojen rakenteiset ajotiedot RSS-itemin rinnalle, Valvomo ensisijaiseksi käyttöliittymäksi sekä Valvomon tietotarpeet, näkymät ja historiatiedot. RSS-lukija ja Kehitysjono säilytetty toissijaisina käyttöliittyminä. Täsmennetty yhteinen ajoprosessi, aihekohtaiset ajotiheydet ja näytösseurannan asema samanarvoisena aiheena. Täsmennetty, että siirtomekanismi ja tekninen toteutus ratkaistaan myöhemmin.
- **0.2.0 – 20.11.2026:** ensimmäinen vaatimusluonnos: ChatGPT-toimintamalli, yksinkertaisuusperiaate, yhteinen ja aihekohtainen konfiguraatio, seurantatyypit ja raporttipohjat, yhden RSS-itemin rajapinta, muuttumaton RSS-historia, GitHubin validointi ja virhetilanteet.
