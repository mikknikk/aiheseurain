# Aiheseuraimen vaatimusmäärittely – uudistettu tavoitetila

**Versio:** 0.12.4  
**Tila:** luonnos – yksinkertaistettu toimintamalli hyväksytty suunnittelun pohjaksi; ei toteutuslupa  
**Päiväys:** 22.11.2026  
**Raporttituottaja:** tuottajariippumaton  
**Suunnitteluperiaate:** mahdollisimman yksinkertainen ja luotettava  
**Kohderepositorio:** `mikknikk/aiheseurain`

> Tämä dokumentti kuvaa Aiheseuraimen tavoitetilan vaatimuksia. Se ei kuvaa nykyisen repositorion kaikkia toteutuksia eikä muuta niitä. Nykyiset automaatiot, niiden ajastukset, käynnistyskehotteet, kohdekeskustelut, RSS-julkaisut ja tuotantotilat säilyvät ennallaan, kunnes niihin tehdään erikseen hyväksyttyjä muutoksia. Vaatimusmäärittelyn hyväksyminen, toteutussuunnitelman hyväksyminen ja toteutuksen aloittaminen ovat erillisiä päätöksiä.

## 1. Tarkoitus ja rajaus

Aiheseurain on useita aiheita ja seurantatyyppejä käsittelevä raporttien vastaanotto-, validointi-, tallennus- ja julkaisujärjestelmä. Raportin voi tuottaa ihminen, tekoäly, ohjelmisto tai muu soveltuva toimija. Aiheseurain ei edellytä tiettyä tuottajaa, kunhan tulos täyttää yhteisen tietosopimuksen.

Aiheseurainin yhteinen ohjelmisto ja yksittäisen käyttöönoton instanssi ovat erillisiä kokonaisuuksia. Yhteisen ohjelmiston tulee olla jaettavissa ja käyttöönotettavissa ilman, että käyttäjäkohtaiset määritykset tai käyttödatan tiedostot kuuluvat ohjelmiston lähdekoodiin. Instanssi käyttää erikseen valittua ohjelmistoversiota. Tässä määrittelyssä asetetaan näille kokonaisuuksille toiminnalliset vaatimukset; repositorioiden tarkka rakenne ja tekninen toteutus ratkaistaan toteutussuunnittelussa.

Järjestelmän ensimmäisen toteutusvaiheen toimintamalli on seuraava:

- Aiheseurain lukee aktiiviset aihekohtaiset määritykset ja valitsee seuraavan erääntyneen aiheen.
- Yksi käynnistys käsittelee enintään yhden aiheen.
- Ajonhallinta luo ajolle yksilöllisen `run_id`-tunnisteen ja ajotietueen.
- Raporttituottaja tutkii aiheen ja toimittaa rakenteisen tuloksen.
- Aiheseurain vastaanottaa, validoi ja tallentaa tuloksen sekä julkaisee hyväksytyn RSS-itemin.
- Jokaisen ajon tulos ja julkaisutilanne jäävät jäljitettäviksi myös silloin, kun uutta RSS-itemiä ei synny tai ajo epäonnistuu.

Aiheiden määritykset, lähderekisterit, raporttipohjat, skeemat ja RSS-julkaisut voidaan hallita GitHubissa. Ajotietojen tallennukseen valitaan toteutussuunnittelussa yksinkertaisin turvallinen ratkaisu. Erillistä tietokantaa tai muuta tietovarastoa ei oteta käyttöön ilman perusteltua tarvetta.

RSS-item ja ajon hallintaan tarvittavat tiedot ovat erillisiä mutta samaan ajoon sidottuja tietoja. Valvomo näyttää ajotilanteen; RSS-lukija näyttää julkaistut raportit. Kehitystehtäviä hallitaan GitHub Projectsissa.

Tämä on vaatimusmäärittely, ei tekninen toteutussuunnitelma. Se ei lukitse tiedonsiirtomekanismia, tietokantaa, käyttöliittymäkirjastoa tai muuta yksityiskohtaista teknologiaa, ellei vaatimus sitä edellytä.

## 2. Suunnitteluperiaatteet

1. **Yksinkertaisuus:** tarve ratkaistaan mahdollisimman vähillä komponenteilla, tietovarastoilla ja prosessivaiheilla.
2. **Tuottajariippumattomuus:** tutkimuksen ja raportin voi tuottaa ihminen, tekoäly, ohjelmisto tai muu soveltuva toimija. Aiheseurain määrittelee tuloksen vaatimukset, ei tuottajan teknologiaa.
3. **Yksi yhteinen ajomalli:** kaikki aiheet ja seurantatyypit käyttävät samaa perusprosessia.
4. **Yksi aihe ajossa:** yksi käynnistys käsittelee enintään yhden aiheen. Useiden aiheiden yhdistämistä samaan ajokertaan tai batch-orkestrointia ei tarvita ensimmäisessä versiossa.
5. **Aihekohtainen erillisyys:** yhden aiheen lähteitä, havaintoja, raportteja tai tilaa ei sekoiteta toiseen aiheeseen.
6. **Dynaamiset aiheet:** yleinen vaatimusmäärittely ei sisällä kiinteää aihelistaa. Aiheita hallitaan määrityksillä.
7. **Määrityspohjaisuus:** aiheiden erot, kuten seurantatiheys, sisältö, tapahtumatyypit ja raporttipohja, kuvataan asetuksilla ja seurantatyypillä.
8. **Dynaaminen ja reilu aihevalinta:** seuraava aihe valitaan aktiivisten määritysten, erääntymisen ja odotusajan perusteella, ei kovakoodatusta aihejärjestyksestä.
9. **Yksi kanoninen ajohistoria:** samaa ajotietoa ei ylläpidetä tarpeettomasti useissa toisistaan riippumattomissa tietovarastoissa.
10. **Muuttumaton julkaisuhistoria:** julkaistuja RSS-itemeitä ei muokata, poistaa eikä korvata. Myöhempi olennainen täydennys tai korjaus julkaistaan uutena iteminä, joka kertoo avoimesti muutoksen ja viittaa alkuperäiseen.
11. **Turvallinen epäonnistuminen:** epäselvä tai virheellinen tulos ei johda virheelliseen RSS-julkaisuun eikä onnistumisen esittämiseen.
12. **Vaiheiden selkeä vastuunjako:** tuottajan tutkimustulos, vastaanoton validointi, tallennus ja julkaisu ovat erillisiä tiloja.
13. **Ohjelmiston ja instanssin erillisyys:** jaettava yhteinen ohjelmisto ei ole sidottu yhden käyttöönoton määrityksiin tai käyttödatan sijaintiin.
14. **Hallitut ohjelmistopäivitykset:** instanssi käyttää yksilöityä ohjelmistoversiota, ja version vaihtaminen on ylläpitäjän hallitsema toimenpide.

## 3. Käyttöliittymät ja niiden tärkeysjärjestys

### 3.1 Valvomo – ensisijainen käyttöliittymä

Valvomo on järjestelmän ensisijainen käyttöliittymä. Ensimmäisen version kolme päänäkymää ovat:

1. **Yleiskuva:** järjestelmän tila, mahdollinen käynnissä oleva ajo, seuraavaksi käsiteltävä aihe ja näkyvät poikkeamat.
2. **Aiheet:** aiheiden aktiivisuus, viimeisin onnistunut seuranta ja seuraava erääntymisaika.
3. **Ajohistoria:** ajon seuranta-aikaväli, tulos, lähteiden tarkistustilanne, raportin ja julkaisun tila sekä mahdolliset virheet.

Valvomon tulee näyttää myös ajot, joista ei syntynyt RSS-itemiä. Ajon tilaa ei saa päätellä pelkästään RSS-syötteistä. Puuttuva tieto esitetään tuntemattomana, ei onnistumisena tai epäonnistumisena.

Lähdekattavuus ja julkaisun tila esitetään ajon tietojen yhteydessä. Niitä varten ei tarvita erillisiä analytiikka- tai mittaristonäkymiä ensimmäisessä versiossa.

### 3.2 RSS-lukija – toissijainen käyttöliittymä

RSS-lukija kokoaa julkaistut raportit luettavaksi. Sen tehtävä on:

- näyttää eri aiheiden julkaistut RSS-itemit;
- tarjota syötekohtainen suodatus ja yhteinen aikajärjestys;
- mahdollistaa raportin lukeminen ja lähteiden avaaminen;
- käsitellä tyhjät syötteet ja virheelliset yksittäiset itemit hallitusti.

RSS-lukija ei ole ajotilanteen tai lähdekattavuuden ensisijainen tietolähde.

### 3.3 Kehitystehtävien hallinta – GitHub Projects

GitHub Issues on kehitystehtävien kanoninen tietolähde ja GitHub Project niiden ensisijainen käyttöliittymä. Issue-labelit ovat tilan, prioriteetin ja komponentin ensisijaiset tiedot, ja Projectin Status- sekä Priority-kentät synkronoidaan niistä. Riippuvuudet tallennetaan GitHub Issuesin natiiveina suhteina.

Aiheseurainissa ei ylläpidetä erillistä omaa Kanban-käyttöliittymää, JSON-välimuistia tai niiden päivitysputkea.

### 3.4 Yhteinen sivusto

Valvomo ja RSS-lukija voivat olla saman GitHub Pages -sivuston osia. Ne ovat silti instanssikohtaisia palvelunäkymiä: yhteinen käyttöliittymäkoodi kuuluu jaettavaan ohjelmistoon, mutta kukin instanssi tarjoaa näkymille vain omat määrityksensä, tietonsa ja julkaisunsa. Kehitystehtäviä hallitaan GitHub Projectsissa, joka ei ole osa Pages-sivustoa.

Ensimmäisessä versiossa sekä Valvomo että RSS-lukija voivat olla julkisia. Valvomoon ei siten toteuteta ensimmäisessä versiossa kirjautumista tai käyttöoikeusjärjestelmää. Tämä edellyttää, ettei julkiseen käyttöliittymään tai sen lukemiin tietoihin sisälly salaisuuksia, yksityisiä tietoja tai muuta luottamuksellista sisältöä. Jos tällaiselle tiedolle syntyy myöhemmin tarve, tietojen erottelu ja käyttöoikeudet suunnitellaan erikseen.

## 4. Aiheiden ja seurantatyyppien hallinta

### 4.1 Dynaamiset aiheet

- Aiheita ei luetella kiinteästi tässä yleisessä määrittelyssä.
- Jokaisella aiheella on oma määritystiedosto.
- Aihe voidaan ottaa käyttöön, poistaa käytöstä tai muuttaa määrityksellä ilman yleisen toimintamallin muuttamista.
- Aihekohtainen lähderekisteri ja raporttipohja voidaan ylläpitää erillään muiden aiheiden tiedoista.
- Uusi aihe ei saa vaatia koodimuutosta, jos sen tarpeet voidaan toteuttaa jo olemassa olevalla seurantatyypillä ja raporttipohjalla.

### 4.2 Yhteinen ja aihekohtainen määritys

Määritysmalli on kaksitasoinen:

- yhteinen määritys sisältää kaikkia aiheita koskevat säännöt, tietosopimukset, julkaisun turvallisuusehdot ja yleiset oletukset;
- aihekohtainen määritys sisältää aiheen tunnisteen ja nimen, seurantatyypin, ohjeet, lähderekisterin, raporttipohjan, aktiivisuuden ja ajotiheyden.

Aihekohtainen määritys ei saa ohittaa yhteisiä turvallisuus-, eheys- tai julkaisusääntöjä.

### 4.3 Seurantatyypit ja raporttipohjat

Kaikki aiheet käyttävät yhteistä suoritusprosessia. Seurantatyyppi määrittelee, millaisia havaintoja etsitään, mitä luokituksia tarvitaan ja mitä erityisiä tarkistuksia tehdään. Raporttipohja määrittelee RSS-raportin rakenteen.

Esimerkiksi tapahtuma- tai näytösseuranta voi käyttää samaa ajomallia kuin uutisseuranta, mutta sen määritys ja raporttipohja voivat käsitellä tapahtumapäiviä, tulevia ja menneitä tapahtumia sekä muutoksia.

Uuden seurantatyypin lisääminen voi vaatia teknistä toteutusta. Sen tulee olla rajattu laajennus yhteiseen järjestelmään, ei kokonaan erillinen automaatioarkkitehtuuri.

### 4.4 Aikataulut ja aiheen valinta

Jokainen käynnistys valitsee enintään yhden aiheen. Ajonhallinta lukee aktiiviset aihekonfiguraatiot ja ajantasaisen seurantatilan sekä valitsee seuraavan kelpoisen aiheen.

Valinta noudattaa seuraavia yksinkertaisia sääntöjä:

1. Pois käytöstä olevat aiheet eivät ole valittavissa.
2. Aihe on valittavissa, kun sen määrityksen mukainen seuranta on erääntynyt tai ajo on käynnistetty erikseen.
3. Erääntyneistä aiheista valitaan pisimpään odottanut.
4. Jos odotusaika on sama, käytetään vakaata järjestystä, jotta valinta on ennakoitava.
5. Jos sopivaa aihetta ei ole, käynnistys päättyy ilman aiheajoa.

Aihekohtainen ajotiheys määritellään määrityksessä. Eri seurantatyypeillä voi olla omat aikataulu- ja sisältösääntönsä, mutta ne eivät muuta yhden aiheen ajomallia.

Ajon epäonnistuminen ei saa merkitä aihetta onnistuneesti käsitellyksi eikä antaa sille perusteetonta etua jonossa. Epäonnistunut ajo tallennetaan, ja uuden yrityksen ajankohta ratkaistaan yksinkertaisella, hallitulla säännöllä. Yhden ongelmallisen aiheen toistuvat yritykset eivät saa estää muiden erääntyneiden aiheiden etenemistä.

Käyttäjän erikseen käynnistämä ajo voidaan erottaa ajastetusta ajosta. Käynnistystapa ja tuottaja kirjataan ajotietoihin, kun ne ovat tiedossa. Nykyisten automaatioiden asetuksia ei muuteta tämän määrittelyn perusteella.

## 5. Ajon suoritusprosessi

Yksi käynnistys käsittelee enintään yhden aiheen ja noudattaa seuraavaa kulkua:

1. **Valinta:** valitaan aktiivinen ja erääntynyt aihe tai erikseen käynnistetty aihe.
2. **Määritysten luku:** luetaan yhteiset säännöt, aiheen määritys, seurantatyypin säännöt ja raporttipohja sekä niiden versiot.
3. **Ajon aloitus:** luodaan yksilöllinen `run_id` ja ajotietue ennen raporttituottajan työn aloittamista.
4. **Tutkimus ja raportointi:** raporttituottaja käsittelee määritellyt lähteet ja etsii seurantajakson aikana syntyneitä olennaisia uusia havaintoja.
5. **Laadun arviointi:** lähteiden luotettavuus, havaintojen uutuus ja raportointikelpoisuus arvioidaan seurantatyypin sääntöjen mukaisesti.
6. **Tuloksen muodostaminen:** tuottaja muodostaa ajotuloksen ja tarvittaessa yhden rakenteisen RSS-itemin. Jos raportoitavaa ei ole, item jätetään pois.
7. **Toimittaminen:** tuottaja toimittaa tuloksen yhteisellä `run_id`-tunnisteella. Vastaanottava järjestelmä vastaa siitä, että jokaisesta käynnistetystä ajosta syntyy ajotietue. Jos tuottaja ei toimita tulosta määräaikaan mennessä, vastaanottava järjestelmä muodostaa itse `failed`-tilaisen ajotietueen. Tietueeseen kirjataan vain todennettavissa oleva epäonnistumisen syy; puuttuvia tietoja ei päätellä tai arvata.
8. **Vastaanotto ja validointi:** Aiheseurain tarkistaa tuloksen rakenteen, tunnisteet, määritysversiot, kohdeaiheen ja julkaisuehdot.
9. **Tallennus ja julkaisu:** ajotiedot tallennetaan. Hyväksytty RSS-item lisätään oikeaan syötteeseen muuttamatta aiempia itemeitä.
10. **Varmistus:** RSS/XML:n kelvollisuus, GUIDien yksilöllisyys, oikea kohdesyöte ja tallennuksen onnistuminen tarkistetaan.
11. **Tilapäivitys:** ajon tulos, vastaanoton tila, julkaisun tila, aiheen viimeisin onnistunut seuranta ja seuraava erääntymisaika päivitetään varmennetun lopputuloksen perusteella.

Ajon epäonnistuminen tai tuloksen puuttuminen ei saa hävittää käynnistetyn ajon tietuetta. Ajon onnistuminen, raportin syntyminen ja RSS-julkaisun onnistuminen ovat erillisiä asioita.

Ensimmäisessä versiossa tehtävät käsitellään sarjallisesti: järjestelmässä on kerrallaan enintään yksi aktiivinen raportointitehtävä, eikä seuraavaa tehtävää käynnistetä ennen kuin edellinen on todettu onnistuneeksi tai kirjattu epäonnistuneeksi. Tämä koskee myös eri aiheita; eri aiheiden rinnakkaista käsittelyä ei toteuteta ensimmäisessä versiossa. Näin ensimmäinen versio ei tarvitse rinnakkaisten tehtävien varaus-, lukitus- tai kilpailutilanteiden hallintaa. Sarjallinen käsittely ei poista tarvetta estää saman ajon kaksoistoimituksia ja kaksoisjulkaisuja: run_id ja idempotentti vastaanotto säilyvät.

Tämä on looginen prosessi. Tiedonsiirron tarkka tekninen mekanismi ja vastaanottorajapinnan toteutus valitaan erillisessä toteutussuunnittelussa. Tuottajan ei edellytetä käyttävän tiettyä palvelua tai kirjoittavan suoraan repositorioon.

## 6. Ajon tulos ja ajotiedot

### 6.1 Ajotietue ja tuottajan tulos

Jokaisesta käynnistetystä ajosta ylläpidetään omaa ajotietuetta. Raporttituottajan toimittama tulos täydentää tätä tietuetta. Tuloksen vähimmäisosat ovat:

- `schema_version`: pakollinen tietosopimuksen version tunniste;
- `run_id`: pakollinen, ennen suoritusta muodostettu ajon yksilöllinen tunniste;
- `run_metadata`: aiheen ja seurannan sisältöä kuvaavat metatiedot;
- `report_item`: valinnainen uusi RSS-item;
- `producer`: valinnaiset tiedot raporttituottajasta, jos ne ovat saatavilla.

Vastaanottava järjestelmä täydentää ajotietuetta vastaanotto-, validointi-, tallennus- ja julkaisutiloilla. Tuottajan tunniste, nimi, ohjelmistoversio tai ohjeversion tunniste eivät ole yleisiä pakollisia kenttiä. Ihmisen tekemä raportti voidaan toimittaa samalla tietosopimuksella ilman ohjelmistokohtaisia metatietoja.

Raporttia ei tuoteta uudelleen vastaanottavassa järjestelmässä eikä tuottaja palauta koko RSS-syötettä.

### 6.2 Ajotietojen vähimmäissisältö

Ajotuloksen tietosopimus versioidaan. Jokaisessa toimitetussa tuloksessa ovat pakollisia:

- tietosopimuksen versio ja `run_id`;
- aiheen tunniste ja seurantatyyppi;
- seurannan aikaväli;
- tuottajan tulostila.

Käynnistin tai vastaanottava järjestelmä kirjaa ajon aloitusajan ja käytetyt määritysversiot. Muut tiedot toimitetaan, jos ne ovat saatavilla tai kyseinen seurantatyyppi niitä edellyttää.

| Tietoryhmä | Tarvittavat tiedot | Tiedon lähde |
|---|---|---|
| Tunnisteet | `run_id`, aiheen tunniste ja seurantatyyppi | Käynnistin ja tuottaja |
| Määritykset | yhteisen ja aihekohtaisen määrityksen sekä raporttipohjan versiot tai yksilöivät tunnisteet | Vastaanottava järjestelmä |
| Ajanjakso | seurannan alku ja loppu sekä ajon aloitus- ja lopetusajat | Tuottaja ja vastaanottava järjestelmä |
| Tuottajan tulos | `success`, `partial`, `no_report` tai `failed` | Tuottaja |
| Havainnot | olennaisten ja raportoitavien havaintojen määrä, jos seurantatyyppi tarvitsee sitä | Tuottaja |
| Lähteet | tarkistetut ja tarkistamatta jääneet lähteet sekä syyt | Tuottaja |
| Laadunvarmistus | laadunarvioinnin tulos, virheet ja varoitukset | Tuottaja |
| Vastaanotto | vastaanotto- ja validointitila sekä turvallinen virheluokka | Vastaanottava järjestelmä |
| Raportti | syntyikö RSS-item, sen GUID ja otsikko, jos ne ovat olemassa | Tuottaja ja vastaanottava järjestelmä |
| Julkaisu | kohdesyöte, julkaisun tila ja julkaisuajankohta | Vastaanottava järjestelmä |

Ajotietojen tarkoitus on kuvata, mitä tapahtui ja millä tuloksella. Niihin ei tallenneta tarpeettomasti koko tutkimusketjua, raakaa keskustelutekstiä tai kaikkia lähdesivuista kopioituja sisältöjä. Ajotiedot eivät ole yksityiskohtainen tekninen tapahtumaloki.

### 6.3 Tuloksen ja käsittelyn tilat

**Tuottajan tulos:**

- `success`: tutkimus- ja raportointityö valmistui;
- `partial`: työ valmistui osittain, ja rajoitteet on kuvattu;
- `no_report`: työ valmistui, mutta uutta raportoitavaa ei löytynyt;
- `failed`: tuottajan suoritus epäonnistui.

`no_report` on onnistunut seuranta ilman RSS-itemiä, ei virhe.

`partial` kuvaa osittaista seurantaa. Jos osittaisesta seurannasta syntyy raportti, se julkaistaan RSS-syötteeseen. Raportissa kerrotaan selvästi, mikä jäi tarkistamatta tai puutteelliseksi, miksi näin tapahtui ja miten se vaikuttaa kattavuuteen. Myöhemmät ajot eivät muokkaa julkaistua itemiä: olennainen täydennys tai korjaus julkaistaan uutena, avoimesti alkuperäiseen raporttiin viittaavana iteminä.

**Vastaanottavan järjestelmän käsittelytila** erottaa vähintään vastaanoton, validoinnin, hyväksynnän, hylkäyksen, julkaisun ja julkaisun epäonnistumisen. Ajon elinkaaren hallinnassa voidaan lisäksi käyttää tiloja jonossa, käynnissä, aikakatkaistu ja peruutettu. Jos tuottaja ei toimita tulosta määräaikaan mennessä, vastaanottava järjestelmä muodostaa ajotietueen `failed`-tilaisena ilman tuottajan toimitusta. Tämä vastaanottajan muodostama tietue ei väitä sisältävänsä tuottajan ilmoittamaa tulosta tai virhekuvausta: siihen kirjataan vain vastaanottajan todennettavissa oleva tieto, kuten määräajan umpeutuminen tai muu havaittu toimitus-/yhteysvirhe. Tuntemattomia syitä tai puuttuvia tuottajan metatietoja ei täydennetä arvauksilla.

Tuottajan `success` ei tarkoita, että tulos olisi validoitu tai julkaistu. Julkaisuvirhe ei muuta onnistunutta tutkimustyötä epäonnistuneeksi.

### 6.4 Tietosopimuksen vähimmäistarkistukset

- `schema_version` ja `run_id` ovat pakollisia jokaisessa toimitetussa tuloksessa.
- Aiheen tunniste, seurantatyyppi ja seurannan aikaväli tarkistetaan käynnistyksessä käytettyä määritystä vasten.
- Tuottajan tulostilan on oltava yksi määritellyistä arvoista.
- `report_item` puuttuu, kun tulos on `no_report` tai `failed`.
- `partial`-tilassa syntynyt RSS-item julkaistaan, jos se läpäisee samat rakenteelliset ja turvallisuustarkistukset kuin `success`-item.
- Jos `report_item` on mukana, sen GUID on yksilöllinen ja item täyttää RSS:n sekä aiheen raporttipohjan vaatimukset.
- Tuottajan valinnaisia tunnistetietoja ei vaadita ihmisen tekemältä raportilta.
- Vastaanottava järjestelmä kirjaa vastaanottoajan ja oman käsittelytilansa riippumatta tuottajan metatiedoista.

## 7. RSS-julkaiseminen

- Jokainen aihe julkaisee omaan RSS-syötteeseensä; aiheita ei sekoiteta samaan syötteeseen.
- RSS-item sisältää koko raportin.
- RSS-itemissä ei käytetä erillistä `<link>`-elementtiä. Lähdelinkit esitetään raportin lopun lähdeluettelossa.
- Itemillä on yksilöllinen GUID.
- Raportti on suomenkielinen ja sisältää aina seurannan aikavälin.
- Lähteiden luotettavuus ja olennaiset epävarmuudet ilmaistaan aihekohtaisen raporttipohjan mukaisesti.
- Tuottaja toimittaa enintään yhden uuden itemin yhtä raportoitavaa ajoa kohti.
- Vastaanottava julkaisukerros validoi itemin ja lisää sen oikean aiheen syötteeseen.
- Tuottaja ei muodosta eikä palauta koko RSS-syötettä.
- Aiemmin julkaistujen itemien sisältöä, GUID-tunnisteita tai järjestystä ei muuteta.
- Raporttituottaja lukee aiemmat raportit ennen uuden raportin muodostamista ja välttää saman asian toistamista ilman olennaista uutta tietoa.
- Olennainen täydennys tai korjaus julkaistaan uutena erillisenä iteminä, jossa kerrotaan avoimesti korjauksen tai täydennyksen luonne ja viitataan alkuperäiseen julkaisuun.
- Jokaisella korjauspäivityksellä on oma GUID; alkuperäinen item säilyy muuttumattomana.
- RSS/XML validoidaan jokaisen julkaisun yhteydessä.
- Julkaisu ja ajotietojen tallennus toteutetaan niin, ettei virheellinen tai puoliksi tallennettu julkaisu näy onnistuneena.

Jos ajo onnistuu mutta uutta raportoitavaa ei löydy, ajotiedot tallennetaan ja Valvomo näyttää onnistuneen ajon ilman uutta RSS-julkaisua. Keinotekoisia ”ei uutisia” -RSS-itemeitä ei luoda.

## 8. Valvomon tietotarpeet

Valvomon ensimmäisen version näkymät on kuvattu luvussa 3. Valvomon tietomallin tulee tukea näitä näkymiä yhdestä kanonisesta ajohistoriasta.

- Valvomo erottaa ajon onnistumisen, raportin syntymisen ja RSS-julkaisun onnistumisen toisistaan.
- Puuttuva tieto esitetään tuntemattomana, ei onnistumisena tai epäonnistumisena.
- Vanhentunutta tilaa ei esitetä ajantasaisena.
- Käynnissä-tila näytetään vain, jos ajosta on tuore ja todennettava käynnissä-merkintä.
- Osittainen lähdetarkistus ei muutu täydelliseksi vain siksi, että ajo tuotti raportin.
- Prosenttilukuja ei näytetä ilman luotettavaa nimittäjää.
- Historiatietoja ei korvata viimeisimmän ajon tilannekuvalla.
- Lähdekattavuus, raportin tila ja julkaisun tila näytetään ajon yhteydessä; erillisiä analytiikkanäkymiä ei vaadita ensimmäisessä versiossa.

## 9. Hallinta-, tallennus- ja julkaisuvastuut

Aiheseurain hallitsee yhteisiä ja aihekohtaisia määrityksiä, lähderekistereitä, raporttipohjia, skeemoja, validointia ja RSS-julkaisun sääntöjä. GitHub voi toimia määritysten ja julkaistujen RSS-syötteiden hallintapaikkana.

Ajohistorialle valitaan toteutussuunnittelussa yksi kanoninen tallennusratkaisu. Ensisijainen tavoite on käyttää yksinkertaisinta turvallista ratkaisua, joka täyttää historian, käyttöoikeuksien, tietosuojan ja kirjoitusmäärien tarpeet. Erillistä tietokantaa tai muuta tallennuspalvelua ei vaadita ilman osoitettua tarvetta. Nykytilan yhteenveto voidaan muodostaa historiasta; erillinen yhteenvetotieto on sallittu vain, jos sen johdonmukaisuus voidaan varmistaa.

Vastaanottavan järjestelmän tehtävät ovat:

- lukea yhteiset ja aihekohtaiset määritykset;
- luoda ajotietue ja `run_id`;
- vastaanottaa ja validoida tuottajan tulos;
- tallentaa ajon ja käsittelyn tilat;
- estää saman ajon tai RSS-itemin kaksoiskäsittely;
- julkaista hyväksytty item oikeaan RSS-syötteeseen;
- säilyttää aiemmat julkaisut muuttumattomina;
- tarjota Valvomolle luettavat, rakenteiset ja turvalliset tiedot.

Vastaanottavan järjestelmän validointi on julkaisun portinvartija. Minkään tuottajan sisältöä ei julkaista vain siksi, että se näyttää valmiilta.

### 9.1 Jaettava ohjelmisto ja instanssikohtainen käyttö

- Yhteisen ohjelmiston tulee olla julkaistavissa ja jaettavissa erillään yksittäisen käyttöönoton tiedoista.
- Yhden instanssin omat aiheet, seurantatehtävät, määritykset, profiilit, lähderekisterit, ajohistoria, RSS-syötteet ja muut käyttöönoton tiedot kuuluvat instanssille. Niitä ei käsitellä jaettavan ohjelmiston lähdekoodina tai ohjelmistoversion sisältönä.
- Ohjelmiston tulee pystyä lukemaan ja käsittelemään instanssin tietoja määritellyn rajapinnan ja tietosopimusten kautta. Se ei saa olettaa, että ohjelmistokoodi ja instanssin tiedot sijaitsevat samassa Git-repositoriossa tai määrätyissä suhteellisissa tiedostopoluissa.
- Tehtävän ja sen tuloksen jäljitettävyyden tulee erottaa käytetty ohjelmistorevisio ja instanssidatan revisio toisistaan. Ohjelmistorevisio yksilöi tehtävän käsittelyssä käytetyn ohjelmistokoodin, yhteiset skeemat ja ohjelmiston yleiset ohjeet; instanssidatan revisio yksilöi käytetyt aiheet, tehtävät, profiilit, lähderekisterit, instanssikohtaiset ohjeet sekä RSS-historian lähtötilan.
- Tiedostoviittauksen tulee yksilöidä myös tietolähteen repositorio tai muu sovittu tietovarasto. Pelkkä repositoriojuureen suhteutettu polku ei riitä, jos tehtävässä käytetään sekä ohjelmisto- että instanssirepon tiedostoja.
- Ohjelmisto- ja instanssirevision sekä tiedostoviittausten avulla on voitava yksiselitteisesti selvittää, mistä repositoriosta ja mistä muuttumattomasta revisiosta kukin tehtävän käsittelyssä käytetty tiedosto luettiin.
- Instanssin on voitava käyttää nimenomaisesti valittua ja jäljitettävää ohjelmistoversiota.
- Ohjelmistoversion julkaisu ei saa itsessään muuttaa instanssin käytössä olevaa versiota. Version päivittäminen edellyttää instanssin ylläpitäjän hallitsemaa muutosta.
- Ensimmäisen version ei tarvitse tarjota keskitettyä monen instanssin palvelua tai monivuokraaja-arkkitehtuuria. Vaatimukset koskevat ohjelmiston ja yhden instanssin välistä selkeää erottelua.
- Julkisen ohjelmiston jakelu ei tarkoita, että jokaisen instanssin tietojen pitäisi olla julkisia. Instanssin tietojen näkyvyys ja käyttöoikeudet ratkaistaan niiden sisältöä ja käyttötarkoitusta vastaavasti.
- Valvomo ja RSS-lukija ovat instanssikohtaisia palvelunäkymiä. Niiden yhteinen käyttöliittymäkoodi kuuluu jaettavaan ohjelmistoon, mutta käyttöliittymät näyttävät vain kyseisen instanssin tietoja ja asetuksia.
- Ensimmäisessä versiossa sekä Valvomo että RSS-lukija voivat olla julkisia. Valvomoon ei toteuteta kirjautumista tai käyttöoikeusjärjestelmää.
- Julkisen Valvomon tietolähteisiin, rajapintoihin ja näkymiin ei saa päätyä salaisuuksia, käyttöoikeustunnuksia, yksityisiä tietoja tai muuta luottamuksellista sisältöä. Julkisuuteen soveltumattomia tietoja ei saa tehdä turvallisiksi pelkästään piilottamalla niitä käyttöliittymässä.
- Jos myöhempi käyttötarve edellyttää luottamuksellisen tiedon käsittelyä, tietojen erottelu ja tarvittava käyttöoikeusratkaisu suunnitellaan erikseen; se ei kuulu ensimmäisen version toteutukseen.

## 10. Virhetilanteet ja uudelleenyritykset

Virhetilanteet käsitellään yksinkertaisella ja yksiselitteisellä tavalla:

- **Tutkimusvirhe:** tulos tallennetaan virheellisenä; raporttia ei julkaista.
- **Osittainen seuranta:** tulos ja lähdekattavuuden rajoitteet tallennetaan. Syntynyt osittainen raportti julkaistaan, ja sen puutteet kuvataan avoimesti. Myöhemmät täydennykset tai korjaukset julkaistaan uusina itemeinä.
- **Virheellinen ajotulos:** vastaanottava järjestelmä hylkää tuloksen; RSS-syöte ei muutu.
- **Väärä aihe tai määritysversio:** tulos hylätään, eikä sitä reititetä toiseen aiheeseen arvaamalla.
- **Duplikaatti:** samaa `run_id`-tunnistetta tai RSS-GUIDia ei käsitellä uutena julkaisuna.
- **Julkaisuvirhe:** ajoa ei merkitä julkaistuksi ennen kuin tallennus ja julkaisu on varmennettu.
- **Uudelleenyritys:** saman loogisen ajon turvallinen jatko käyttää samaa tunnistetta; uusi erillinen ajo saa uuden tunnisteen.
- **Aiheen jonotus:** epäonnistunut ajo ei merkitse aihetta onnistuneesti käsitellyksi eikä saa estää muiden erääntyneiden aiheiden etenemistä.
- **Puuttuva tuottajavastaus:** käynnistetty ajotietue säilytetään ja ajo merkitään aikakatkaisun tai muun todennetun syyn perusteella epäonnistuneeksi.

Ensimmäisessä versiossa ei vaadita monimutkaista uudelleenyritysten orkestrointia. Uudelleenyrityksen ajankohta ja rajat määritellään toteutussuunnittelussa niin, ettei virheellinen aihe jää toistuvasti jonon kärkeen.

Valvomo näyttää virheluokan, lyhyen selitteen, epäonnistuneen vaiheen ja sen, onko uusi yritys mahdollinen tai jo tehty.

## 11. Turvallisuus, eheys ja testaus

- Testit eivät saa kirjoittaa tuotannon RSS-syötteisiin tai muuttaa tuotannon seurantatilaa.
- Määritysten eheys tarkistetaan ennen ajoa. Virheellinen tai ristiriitainen määritys estää ajon.
- Samaa aihetta ei saa käsitellä samanaikaisesti ristiriitaisissa ajoissa tai tilapäivityksissä.
- Aihekohtainen varaus tai muu yksinkertainen suojaus estää saman aiheen päällekkäiset ajot.
- Ajon ja julkaisun käsittely on idempotenttia: sama tulos ei saa synnyttää päällekkäisiä ajotietueita tai RSS-julkaisuja.
- Määritysten ja julkaisujen palautus tunnettuun kelvolliseen tilaan on voitava tehdä versionhallinnan avulla ilman aiempien julkaistujen itemien muuttamista.
- Jokaisen ajon yhteydessä tallennetaan käytettyjen yhteisten ja aihekohtaisten määritysten sekä seurantatyypin ja raporttipohjan versiot tai yksilöivät tunnisteet.
- Julkiset tiedot, ylläpidon tiedot ja salaisuudet erotetaan toisistaan. Käyttöliittymä ja julkiset tiedostot eivät saa paljastaa yksityisiä ajotietoja tai käyttöoikeustunnuksia.
- Tietoja kerätään ja säilytetään vain määriteltyyn käyttötarkoitukseen tarvittava määrä.
- Testiaineisto ja tuotantoaineisto pidetään erillään.
- Julkaistujen RSS-itemien muuttumattomuus testataan.
- Ajon tunnisteiden ja GUIDien yksilöllisyys testataan.
- Väärään aiheeseen reitittäminen estetään testeillä.
- RSS/XML:n, ajotuloksen ja määritysten skeemat validoidaan automaattisesti.
- Julkaisun epäonnistuminen ei saa jättää syötettä virheelliseen tai osittaiseen tilaan.
- Valvomo ei saa sisältää GitHub-kirjoitustunnuksia tai muita salaisuuksia.
- Ensimmäisen version julkinen Valvomo näyttää vain julkisuuteen soveltuvia instanssin tietoja. Salaisuuksia tai yksityisiä tietoja ei saa sisällyttää käyttöliittymän lukemiin julkisiin tiedostoihin tai rajapintoihin, vaikka niitä ei näytettäisi näkymässä.
- Käyttöliittymän saavutettavuus testataan. WCAG 2.2 AAA -vaatimustenmukaisuutta ei väitetä ilman asianmukaisia testejä.
- Uusien skriptien tulee sisältää ymmärrettävät kommentit myös ylläpitäjälle, joka ei ole ohjelmoinnin asiantuntija.

## 12. Kehitystehtävien hallinta GitHub Projectsissa

GitHub Issues on kehitystehtävien kanoninen tietolähde ja GitHub Project niiden ensisijainen käyttöliittymä. Erillistä omaa Kanban-sivua, kehitystehtävien JSON-välimuistia tai sen muodostavaa päivitysputkea ei ylläpidetä.

### 12.1 Tehtävien tila ja prioriteetti

- Jokaisella kehitystehtävällä on täsmälleen yksi component:-, priority:- ja status:-label.
- Issue-labelit ovat tilan, prioriteetin ja komponentin ensisijaiset tiedot. Projectin Status- ja Priority-kentät ovat niistä johdettuja näkymätietoja.
- GitHub Actions synkronoi Status- ja Priority-kentät, kun issue avataan, avataan uudelleen tai sen status:- tai priority:-labelia muutetaan.
- Synkronointi on yksisuuntainen: Project-kentän käsin muuttaminen ei muuta issue-labelia.
- Synkronoinnin virheestä ei saa päätellä, että Projectin kenttä olisi ajan tasalla. Virhe on näkyvä ja korjattavissa uudella synkronointiajolla.

### 12.2 Riippuvuuksien tietomalli

- GitHub Issuesin natiivit Blocked by- ja Blocking-suhteet ovat ainoa pysyvä riippuvuustietolähde.
- Jos tiketti A odottaa tiketin B valmistumista, A:n Blocked by -suhteessa on B. GitHub ylläpitää suhteen käänteisen suunnan.
- Riippuvuuksia hallitaan suoraan GitHub Issuesin tai GitHub Projectsin käyttöliittymästä. Tavallinen tekstimaininta toisesta tiketistä ei luo suhdetta.
- GitHub Project näyttää natiivin estotiedon korteilla. Erillistä riippuvuusrekisteriä tai pyyntölohkoautomaatiota ei käytetä.

### 12.3 Rajaus

Aiheseurain ei rakenna GitHub Projectsin päälle omaa rinnakkaista Kanban-käyttöliittymää tai välimuistia. Mahdolliset myöhemmät laajennukset arvioidaan ensin GitHub Projectsin ja Issuesin natiivien ominaisuuksien avulla.

## 13. Myöhempään vaiheeseen siirrettävät ominaisuudet

Seuraavat ominaisuudet eivät kuulu ensimmäisen version toteutusvaatimuksiin:

- useiden aiheiden käsittely saman ajokerran tai batchin sisällä;
- batch-tunnisteet, ajokerran kokonaistilat ja batch-keskeytyksistä palautuminen;
- monimutkainen jonopisteytys ja useiden prioriteettitekijöiden optimointi;
- osittaisten raporttien myöhempi automaattinen uudelleenjulkaisu tai aiempien itemien muokkaaminen;
- ulkoiset ilmoitukset ja niiden kanavat, vastaanottajat, salaisuuksien hallinta ja uudelleenyritykset;
- erilliset lähdekattavuuden ja julkaisuanalytiikan mittaristot;
- laaja järjestelmän terveysanalyysi.

Näitä voidaan arvioida myöhemmin käytännön tarpeen perusteella. Niiden mahdollisuus ei saa monimutkaistaa ensimmäisen version perusratkaisua.

## 14. Toteutuksen ulkopuolelle rajatut asiat

Tässä vaiheessa ei:

- muuteta nykyisten raporttituottajien tai käynnistimien asetuksia, ajastuksia, suoritusvälejä, aikavyöhykkeitä, ohjeita tai kohteita ilman erillistä lupaa;
- aktivoida seurantamoduuleja tai käynnistetä tuotantojulkaisuja;
- toteuteta uutta teknistä arkkitehtuuria ennen vaatimusmäärittelyn ja toteutussuunnitelman hyväksyntää;
- luoda tarpeettomia rinnakkaisia agentteja, tietokantoja tai julkaisupolkuja;
- lukita tiedonsiirtomekanismia ennen sen teknisen toteutettavuuden selvittämistä;
- kopioida koko RSS-syötettä raporttituottajan käsiteltäväksi ja palautettavaksi;
- muokata tai poistaa vanhoja RSS-itemeitä automaattisesti;
- tehdä Valvomosta RSS-lukijan tai GitHub Projectsin korvaajaa.

## 15. Hyväksymiskriteerit

Vaatimusmäärittely täyttää tavoitteensa, kun toteutuksen suunnittelussa voidaan osoittaa, että:

1. Raportin voi tuottaa ihminen, tekoäly, ohjelmisto tai muu soveltuva toimija; yleinen tietosopimus ei edellytä tiettyä tuottajaa.
2. Aiheiden lisääminen ja muuttaminen tapahtuu määrityksillä ilman yleisen toimintamallin muuttamista, jos olemassa oleva seurantatyyppi riittää.
3. Kaikki aiheet käyttävät samaa perusajoprosessia ja seurantatyypit erottuvat määritysten ja raporttipohjien avulla.
4. Yksi käynnistys käsittelee enintään yhden aiheen.
5. Seuraava aihe valitaan aktiivisista määrityksistä ja seurantatilasta; aiheiden järjestystä ei ole kovakoodattu.
6. Valinta huomioi erääntymisen ja odotusajan niin, ettei jokin kelpoinen aihe jää jatkuvasti muiden ohittamaksi.
7. Jokaisesta käynnistetystä ajosta jää ajotietue, vaikka tuottaja ei pystyisi toimittamaan tulosta; RSS-item on valinnainen.
8. Ajotietue ja tuottajan tulos yhdistetään `run_id`-tunnisteella.
9. Raporttituottaja toimittaa enintään yhden uuden rakenteisen RSS-itemin yhtä raportoitavaa ajoa kohti, ei kokonaista RSS-syötettä.
10. Tuottajan tulos, vastaanoton validointi ja RSS-julkaisun tila ovat erillisiä tietoja.
11. Onnistunut ajo ilman raportoitavaa (`no_report`) tallennetaan onnistuneena ajona ilman RSS-itemiä.
12. Osittainen seuranta tallennetaan, ja syntynyt osittainen raportti julkaistaan selkein puutteita kuvaavin merkinnöin.
13. Vastaanottava julkaisukerros validoi ja lisää hyväksytyn itemin oikeaan aihekohtaiseen syötteeseen.
14. Julkaistujen itemien historia säilyy muuttumattomana.
15. Valvomo näyttää yleiskuvan, aiheiden tilanteen ja ajohistorian myös silloin, kun RSS-itemiä ei synny.
16. Lähdekattavuus, raportin tila, julkaisun tila ja virheet voidaan tarkastella ajon yhteydessä.
17. Yksi kanoninen ajohistoria riittää, eikä samaa tilatietoa ylläpidetä tarpeettomasti rinnakkaisissa tietovarastoissa.
18. Saman aiheen päällekkäiset ajot eivät voi aiheuttaa ristiriitaisia tilapäivityksiä tai kaksoisjulkaisuja.
19. Saman tuloksen uudelleenlähetys ei luo uutta ajotietuetta tai RSS-julkaisua.
20. Käytetyt määritysversiot voidaan jäljittää myös silloin, kun raporttituottaja ei itse tunne tai ilmoita niitä.
21. Virheellinen tai hyväksymisehtoja täyttämätön raportti ei päädy RSS-julkaisuun.
22. Julkiseen raporttiin, RSS-syötteeseen tai Valvomon julkiseen dataan ei päädy salaisuuksia tai tarpeettomia henkilötietoja.
23. Valvomo ja RSS-lukija käyttävät yhteistä ohjelmistototeutusta mutta näyttävät vain oman instanssinsa tietoja, määrityksiä ja julkaisuja.
24. Ensimmäisen version Valvomo ja RSS-lukija voivat olla julkisia ilman kirjautumista; julkisiin tietolähteisiin ei sisällytetä salaisuuksia, yksityisiä tietoja tai muuta luottamuksellista sisältöä.
25. Testaus estää tuotantodatan tahattoman muuttamisen.
26. Toteutus ei edellytä tarpeettoman monimutkaista rinnakkaisarkkitehtuuria.
27. Ulkoiset ilmoitukset ja batch-ajot eivät ole ensimmäisen version toteutusvaatimuksia.
28. Yhteinen ohjelmisto voidaan julkaista ja ottaa käyttöön erillään yksittäisen instanssin määrityksistä ja käyttödatan tiedostoista.
29. Instanssikohtaiset aiheet, asetukset, lähderekisterit, ajohistoria ja RSS-julkaisut eivät ole jaettavan ohjelmistoversion osia.
30. Ohjelmisto toimii instanssin tietojen kanssa dokumentoidun rajapinnan ja tietosopimusten kautta olettamatta niiden sijaitsevan samassa repositoriossa tai hakemistorakenteessa.
31. Instanssin käyttämä ohjelmistoversio on yksilöitävissä, eikä uuden version julkaisu päivitä sitä automaattisesti.
32. Ensimmäinen toteutus voi käyttää yhtä instanssia ilman keskitettyä monen instanssin palvelua.

## 16. Avoimet suunnittelukysymykset

Seuraavat tekniset yksityiskohdat ratkaistaan toteutussuunnittelussa. Ne eivät muuta tässä määriteltyä yksinkertaista toimintamallia.

1. **Ajotuloksen täsmällinen skeema:** kenttätyypit, pakollisuus, formaattirajoitteet ja esimerkkitulokset määritellään versioidussa skeemassa.
2. **Vastaanottorajapinnan toteutus:** tekninen siirtotapa ja tunnistautuminen valitaan turvallisten vaihtoehtojen perusteella.
3. **Ajojen käynnistäminen:** käynnistimien, ajastusten ja aihekohtaisten erääntymisten tekninen yhteensovitus ratkaistaan erikseen. Nykyisiä tehtäviä ei muuteta tämän määrittelyn perusteella.
4. **Jonon ja uudelleenyritysten tarkat rajat:** valinnan periaate on erääntyminen ja odotusaika. Aikakatkaisut ja uudelleenyritysten rajat täsmennetään toteutussuunnittelussa.
5. **Ajotietojen tallennus:** valitaan yksi yksinkertaisin turvallinen kanoninen tallennusratkaisu. Erillisen tietovaraston tarve osoitetaan ennen sen käyttöönottoa.
6. **Valvomon toteutus:** kolmen perusnäkymän tarkka käyttöliittymärakenne suunnitellaan myöhemmin.
7. **Historiatietojen säilytys:** ajon perustietojen, mahdollisten lokien ja väliaineistojen säilytysajat määritellään tietotarpeen ja tietosuojan perusteella.
8. **Nykyisen toteutuksen siirtymä:** nykyiset osat inventoidaan ja arvioidaan ennen hyödyntämistä tai poistamista. Mitään ei poisteta ilman erillistä suunnitelmaa.
9. **Mahdollinen myöhempi käyttöoikeuksien tekninen toteutus:** jos instanssin myöhempi käyttötarve edellyttää luottamuksellisen tiedon käsittelyä, julkisen ja rajatun tiedon erottelu sekä käyttöoikeudet suunnitellaan ennen tällaisen tiedon käyttöönottoa. Tämä ei kuulu ensimmäiseen versioon.
10. **Ohjelmiston ja instanssin toimitusmalli:** repositorioiden nimet, tarkka hakemistorakenne, jakelukanava, version kiinnittämisen mekanismi sekä ohjelmiston ja instanssin välinen tekninen tiedonsiirto määritellään toteutussuunnittelussa.

## 17. Tuottajakohtaiset toteutusohjeet

Tämä vaatimusmäärittely määrittelee raporttituottajien yhteisen tulossopimuksen ja Aiheseuraimen vastaanottavan järjestelmän vaatimukset. Se ei määrittele yksittäisen tuottajan sisäisiä ohjeita, kehotteita, ohjelmistoversioita, ajastuksia tai niiden versionhallintaa. Kukin tuottajaintegraatio dokumentoi ja hallitsee nämä asiat omassa toteutusohjeessaan. Tuottajakohtainen ohje ei saa muuttaa tässä määriteltyä yhteistä tietosopimusta tai vastaanottavan järjestelmän julkaisuehtoja.

## 18. Muutosloki

- **0.12.4 – 22.11.2026:** hyväksytty ensimmäisen version sarjallinen tehtävänkäsittely: kerrallaan on enintään yksi aktiivinen tehtävä, seuraava käynnistyy vasta edellisen ratkettua, eikä eri aiheiden rinnakkaisuutta tai siihen liittyvää varaus-/lukitusmekanismia toteuteta.
- **0.12.3 – 22.11.2026:** täsmennetty ajotietueen muodostamisen vastuunjakoa: vastaanottava järjestelmä muodostaa jokaisesta käynnistetystä ajosta tietueen myös silloin, kun tuottaja ei toimita tulosta määräaikaan mennessä. Tällöin vastaanottaja merkitsee tietueen `failed`-tilaiseksi ja kirjaa vain todennettavissa olevan epäonnistumisen syyn.
- **0.12.2 – 22.11.2026:** täsmennetty tehtävän jäljitettävyyttä erillisillä ohjelmisto- ja instanssidatan revisioilla sekä repositoriokohtaisilla tiedostoviittauksilla.
- **0.12.1 – 22.11.2026:** täsmennetty Valvomon ja RSS-lukijan instanssikohtaisuus: käyttöliittymien yhteinen koodi kuuluu jaettavaan ohjelmistoon, mutta näkymät käyttävät vain oman instanssin tietoja. Hyväksytty molempien käyttöliittymien julkisuus ensimmäisessä versiossa ilman kirjautumista; julkisiin tietolähteisiin ei saa sisällyttää salaisuuksia tai yksityisiä tietoja.
- **0.12.0 – 22.11.2026:** lisätty vaatimus jaettavan yhteisen ohjelmiston ja erillisten instanssikohtaisten tietojen erottelusta. Määritelty ohjelmiston riippumattomuus instanssin repositoriosta ja tiedostopoluista sekä instanssin ohjelmistoversion kiinnittäminen ja hallittu päivittäminen. Täsmennetty, ettei ohjelmiston julkinen jakelu edellytä instanssidatan julkisuutta eikä ensimmäinen versio vaadi monen instanssin palvelualustaa.
- **0.11.0 – 21.11.2026:** päätetty julkaista myös `partial`-tilassa syntyvät validoidut raportit. Raportissa kuvataan avoimesti seurannan puutteet ja niiden syyt. Julkaistuja RSS-itemeitä ei päivitetä jälkikäteen; olennaiset täydennykset ja korjaukset julkaistaan uusina itemeinä, jotka viittaavat alkuperäiseen raporttiin. Raportintuottaja lukee aiemmat raportit ja välttää toiston ilman olennaista uutta tietoa.
- **0.10.0 – 20.11.2026:** yksinkertaistettu toimintamalli hyväksytty suunnittelun pohjaksi. Yksi käynnistys käsittelee enintään yhden aiheen; batch-ajot ja niiden tunnisteet sekä keskeytyksistä palautumisen erityislogiikka poistettu ensimmäisen version vaatimuksista. Aihevalinta yksinkertaistettu erääntymiseen ja odotusaikaan perustuvaksi. Ajohistorialle määritelty yksi kanoninen tallennusratkaisu ja erillinen tietovarasto vain perustellusta tarpeesta. Osittaisen seurannan tallennus säilytetty, mutta osittaisten raporttien julkaiseminen sekä ulkoiset ilmoitukset siirretty myöhempään vaiheeseen. Valvomo rajattu kolmeen perusnäkymään ja hyväksymiskriteerit kirjoitettu uudelleen.
- **0.9.1 – 20.11.2026:** täsmennetty, ettei GitHub ole vaatimusmäärittelyssä ajotietojen pakollinen tietovarasto. Määritysten ja RSS-julkaisujen hallinta voidaan pitää GitHubissa, mutta ajotietojen säilytysratkaisu jätetään tietosuoja-, käyttöoikeus- ja historiatarpeiden perusteella toteutussuunnitteluun.
- **0.9.0 – 20.11.2026:** poistettu yleisestä vaatimusmäärittelystä ChatGPT-toteutuksen yksityiskohtaiset ohjeet. Tuottajakohtaiset asetukset, kehotteet ja niiden versionhallinta rajattu kunkin integraation omaan dokumentaatioon. Täsmennetty yhteisen tulossopimuksen ja tuottajakohtaisten ohjeiden vastuunjako.
- **0.8.0 – 20.11.2026:** lisätty konfiguraatioihin ja seurantatilaan perustuva dynaaminen aihevalinta, usean yhteensopivan aiheen käsittely samassa ajokerrassa, ajokerran ja aihekohtaisten ajojen erottelu, reilu jonotus, Aiheseuraimen omat resurssirajat, jatkamispäätökset sekä keskeytyksestä palautuminen.
- **0.7.1 – 20.11.2026:** täsmennetty tuottajan tuloksen ja vastaanottavan järjestelmän käsittelytilojen erottelu, ajotietueen muodostuminen myös puuttuvan tuottajavastauksen tilanteessa, tuloksen tilaluokat, tietosopimuksen pakolliset kentät sekä tietojen vastuutahot.
- **0.7.0 – 20.11.2026:** muutettu vaatimusmäärittely tuottajariippumattomaksi. Raporttituottajaksi hyväksytään myös ihminen; raportin tuottaminen, toimittaminen, validointi ja julkaiseminen erotettu toisistaan. Täsmennetty tietosopimuksen versiointi, valinnaiset tuottajametatiedot, määritysten eheys, rinnakkaisten ajojen hallinta, palautuminen, tietosuoja, käyttöoikeudet, jäljitettävyys ja avoimien teknisten kysymysten rajaus.
- **0.6.0 – 20.11.2026:** päätetty käyttää kehitystehtävien käyttöliittymänä GitHub Projectsia. Oma Kanban-käyttöliittymä, JSON-välimuisti ja niiden automaatiot rajattu pois; Status- ja Priority-kentät johdetaan issue-labeleista ja riippuvuudet hallitaan GitHubin natiiveina suhteina.
- **0.5.0 – 20.11.2026:** lisätty alun perin Kehitysjonon päivittyvän JSON-välimuistin ja GitHubin natiivien riippuvuuksien vaatimukset sekä konfiguroitavat ulkoiset ilmoitukset ja niiden turvallisuus- ja tilaseuranta.
- **0.4.0 – 20.11.2026:** palautettu ajastettujen ChatGPT-käynnistyskehotteiden tehtäväkohtainen versionhallinta. Määritelty muuttumattomat versiotiedostot, tehtävärekisteri, ChatGPT:ssä käytössä olevan version erillinen vahvistaminen sekä ajon alun versiotarkistus.
- **0.3.0 – 20.11.2026:** lisätty ajojen rakenteiset ajotiedot RSS-itemin rinnalle, Valvomo ensisijaiseksi käyttöliittymäksi sekä Valvomon tietotarpeet, näkymät ja historiatiedot. RSS-lukija ja Kehitysjono säilytetty toissijaisina käyttöliittyminä. Täsmennetty yhteinen ajoprosessi, aihekohtaiset ajotiheydet ja näytösseurannan asema samanarvoisena aiheena. Täsmennetty, että siirtomekanismi ja tekninen toteutus ratkaistaan myöhemmin.
- **0.2.0 – 20.11.2026:** ensimmäinen vaatimusluonnos: ChatGPT-toimintamalli, yksinkertaisuusperiaate, yhteinen ja aihekohtainen konfiguraatio, seurantatyypit ja raporttipohjat, yhden RSS-itemin rajapinta, muuttumaton RSS-historia, GitHubin validointi ja virhetilanteet.
