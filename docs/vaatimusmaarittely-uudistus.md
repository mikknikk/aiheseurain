# Aiheseuraimen vaatimusmäärittely – uudistettu tavoitetila

**Versio:** 0.12.34  
**Tila:** luonnos – yksinkertaistettu toimintamalli hyväksytty suunnittelun pohjaksi; ei toteutuslupa  
**Päiväys:** 23.11.2026  
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
- Lähteiden pysyvät perustiedot ylläpidetään yhdessä yhteisessä lähderekisterissä. Samaa lähdettä voidaan käyttää useissa aiheissa ja tehtävätyypeissä. Lähteiden valinta ja käyttöasetukset ratkaistaan tehtävätyypin oletuslähteiden sekä aiheen ja tehtävätyypin yhdistelmäkohtaisen määrityksen perusteella; lähderekisteri pidetään rakenteisesti erillään asetuksista.
- Uusi aihe ei saa vaatia koodimuutosta, jos sen tarpeet voidaan toteuttaa jo olemassa olevalla seurantatyypillä ja raporttipohjalla.

### 4.2 Määritysten tasot

Varsinainen tehtäväkohtainen määritysmalli koostuu kolmesta tasosta:

1. **Tehtävätyypin määritys** määrittelee tehtäväluokan tunnisteen ja kuvauksen, käytettävän skeeman, oletusasetukset, sallitut asetukset ja niiden ylikirjoitettavuuden sekä tehtävätyypin käsittely- ja raportointivaatimukset.
2. **Määritysprofiilit** ovat uudelleenkäytettäviä, itsenäisiä asetuskokonaisuuksia. Tehtävään voidaan liittää useita profiileja, joiden järjestys on merkityksellinen.
3. **Aihekohtainen määritys** yksilöi aiheen, valitsee tehtävätyypin ja käytettävät profiilit sekä sisältää kyseisen aiheen asetukset ja sallitut ylikirjoitukset.

Yleiset järjestelmätason säännöt ja turvallisuusvaatimukset koskevat kaikkia kolmea tasoa. Lähderekisteri on rakenteisesti erillinen aineisto eikä osa asetusten yhdistämismallia. Lähteen perustiedot määritellään yhteisessä rekisterissä kerran; lähteen käyttö määritellään tehtävätyypin oletuslähteissä ja tarvittaessa aiheen ja tehtävätyypin yhdistelmäkohtaisissa lähdemäärityksissä.

### 4.3 Määritysten yhdistäminen ja validointi

Asetukset ratkaistaan aina seuraavassa järjestyksessä:

1. tehtävätyypin oletusasetukset;
2. aihekohtaisessa määrityksessä ilmoitetut profiilit täsmälleen ilmoitetussa järjestyksessä;
3. aihekohtaiset asetukset.

Sisäkkäiset objektit yhdistetään rekursiivisesti. Myöhempi arvo korvaa aiemman saman asetuksen arvon. Taulukot korvataan kokonaan, eikä niitä yhdistetä automaattisesti. Puuttuva asetus periytyy aiemmalta tasolta. `null`-arvolle ei anneta yleistä periytymis- tai poistamismerkitystä, vaan sen sallittu merkitys määritellään kyseisen asetuksen skeemassa.

Ylikirjoitus on sallittu vain tehtävätyypin skeemassa erikseen ylikirjoitettaviksi määritellyissä asetuskohdissa. Profiili tai aihekohtainen määritys ei saa lisätä tuntemattomia asetuksia eikä muuttaa järjestelmätason tai tehtäväpyynnön rakenteellisia arvoja. Suojattuja arvoja ovat vähintään yleinen aikavyöhyke sekä tehtävän tunnisteet, revisiotunnisteet ja tietosopimuksen rakenteelliset vaatimukset. Yleinen aikavyöhyke välitetään tehtäväpyynnön `resolved_config.timezone`-kentässä, mutta profiilit ja aihekohtaiset asetukset eivät voi ylikirjoittaa sitä.

Määritykset validoidaan sekä yksittäin että yhdistettynä kokonaisuutena. Validointi kattaa rakenteen, pakolliset ja sallitut kentät, tietotyypit, tunnisteiden syntaksin, rajat ja ylikirjoitettavuuden. Lisäksi tarkistetaan määritysten väliset välttämättömät yhteensopivuudet ja ristiriidat, kuten tehtävätyypin ja profiilien soveltuvuus sekä pakollisten arvojen löytyminen. Ensimmäisessä versiossa ei toteuteta yleistä dynaamista sääntömoottoria tai käyttäjän määrittelemiä yhdistämisfunktioita.

Oletusarvot määritellään tehtävätyypin määrityksessä. Skeema määrittelee asetusten rakenteen, tyypit, pakollisuuden ja sallitut rajat; skeeman kuvaileva oletusarvotieto ei itsessään lisää arvoa suorituksen konfiguraatioon. Jos pakolliselle asetukselle ei ole tehtävätyypin oletusarvoa, se on annettava profiilissa tai aihekohtaisessa määrityksessä. Puuttuva pakollinen arvo estää tehtävän muodostamisen. Raportintuottaja ei päättele eikä keksi puuttuvia arvoja.

Kun määritykset on luettu niiden ilmoitetuista muuttumattomista Git-revisioista, ne validoidaan, yhdistetään edellä kuvatussa järjestyksessä ja lopullinen kokonaisuus validoidaan tehtävätyypin skeemaa vasten. Vasta tämän jälkeen valmis konfiguraatio tallennetaan tehtäväpyynnön `resolved_config`-kenttään. Se on kyseisen ajon muuttumaton asetussnapshot; raportintuottaja ei hae eikä yhdistä määrityksiä uudelleen suorituksen aikana.

Virheellinen tai ristiriitainen määritys estää uuden tehtäväpyynnön muodostamisen. Virhe kirjataan ajonhallinnan tietoihin syineen ja sijaintitietoineen. Aiemmin aktiivista tehtävää ei korvata virheellisellä pyynnöllä, jono ei saa jäädä epäselvään tilaan eikä järjestelmä tee automaattisia korjauksia, arvaa puuttuvia arvoja tai muodosta osittaista `resolved_config`-kokoonpanoa.

Ensimmäisessä versiossa käytetään vain näitä kolmea määritystasoa. Profiilit eivät peri toisiaan eikä profiiliriippuvuuksia tai rekursiivisia määritysketjuja toteuteta. Käytössä ei ole dynaamista asetusten hakupalvelua, automaattista optimointia eikä käyttäjän määrittelemiä yhdistämisfunktioita. Kaikki asetukset ratkaistaan ennen tehtäväpyynnön muodostamista.

### 4.3.1 Määritysten ja viitattujen aineistojen skeemat

Määritysten rakenteet validoidaan JSON Schema Draft 2020-12 -standardin mukaisesti. Yhteiseen ohjelmistoon kuuluvat skeemat kattavat tehtävätyypin määrityksen, tehtävätyyppikohtaiset asetukset, määritysprofiilin, aihekohtaisen määrityksen, lähderekisterin, tehtäväpyynnön ja toimitusmetatiedot. Varsinaiset määritystiedostot ja lähderekisteriaineistot kuuluvat instanssille.

Ensimmäisessä versiossa määritysprofiili sidotaan yhteen tehtävätyyppiin. Profiilia voidaan käyttää useassa saman tehtävätyypin aiheessa, mutta sitä ei voi käyttää toisen tehtävätyypin yhteydessä. Tehtävätyypin määritys yksilöi asetusskeeman, oletukset, sallitut asetukset, ylikirjoitettavat asetuskohdat sekä käsittely-, raportointi- ja ohjevaatimukset.

Tehtäväpyynnön `inputs`-taulukko sisältää rakenteisten syöteaineistojen viittaukset. Jokainen viittaus yksilöi aineiston tunnisteen, tyypin, repositorion ja polun. Ensimmäisessä versiossa yhteinen lähderekisteri on tällainen erillinen aineisto (`kind: source_registry`), joka luetaan instanssirepositoriosta tehtäväpyynnön `instance_revision`-revisiosta. Lähteen pysyvät perustiedot, kuten nimi, julkaisija, lähdetyyppi, kielet, alueet ja toimituksellinen luotettavuus, ylläpidetään rekisterissä vain kerran. Lähdetasolle kuuluvat myös julkaisijaa tai verkkopalvelua yleisesti koskevat tekniset tiedot ja rajoitteet, kuten yleiset käyttöehdot, kirjautumisvaatimukset sekä yhteiset rajapinta- ja käyttörajoitukset. Sisältökanavalle kuuluvat kyseisen sisältövirran tekniset ominaisuudet ja rajoitteet, kuten kanavan osoitteen toimivuuteen vaikuttavat erityispiirteet, sisältömuoto, JavaScript- tai selainriippuvuudet, sivutus, sisältörajoitukset ja kanavakohtainen kirjautumisen tarve. Ajohistoriaan tallennetaan toteutuneet tarkistustulokset, kuten HTTP-tilat, vasteajat, avaus- ja lukemisvirheet sekä onnistumiset. Rekisteriin ei tallenneta nopeasti vanhenevaa pysyvää saavutettavuusarvosanaa. Lähteellä voi olla useita erillisiä sisältökanavia, joilla kullakin on oma vakaa tunniste ja osoite. Kanavat liittyvät samaan lähteeseen ja julkaisijaan, mutta ne voidaan valita ja arvioida tehtäväkohtaisesti erikseen. Näin esimerkiksi saman uutismedian uutis-, elokuva- ja tapahtumasisällöt voidaan käsitellä erillisinä kanavina ilman, että julkaisijan perustiedot kahdennetaan. Sama lähde ja sen kanavat voivat esiintyä useiden aiheiden ja tehtävätyyppien lähdemäärityksissä. Lähteen tai kanavan käyttöä koskevat tiedot, kuten käytössäolo, tärkeys ja erityiset seurantahuomiot, määritellään tehtävätyypin oletuslähteissä tai aiheen ja tehtävätyypin yhdistelmäkohtaisessa määrityksessä. Toimituksellinen luotettavuus ja julkaisijaa tai verkkopalvelua yleisesti koskevat tekniset tiedot ovat lähdetason ominaisuuksia; yksittäisen sisältökanavan tekniset ominaisuudet ja rajoitteet määritellään kanavatasolla. Toteutuneet tarkistustulokset, kuten HTTP-tilat, vasteajat ja virheet, tallennetaan ajohistoriaan. Rekisteriin ei tallenneta nopeasti vanhenevaa pysyvää saavutettavuusarvosanaa. Kanavan osoite ja sisältöalue yksilöivät tarkemman sisältövirran, ja tärkeys sekä käyttötarkoitus voivat vaihdella tehtäväyhdistelmittäin. Lähteelle voidaan määrittää valinnainen oletusaikavyöhyke ja sen määrityksen peruste. Sisältökanava voi määrittää tätä tarkemman aikavyöhykkeen ja sen perusteen. Sisällön oma aikaleima tai tapahtuman sijaintiin perustuva aikavyöhyke on ensisijainen silloin, kun se on luotettavasti tiedossa. Aikavyöhykkeitä ei päätellä epävarmojen tietojen perusteella.

#### Lähderekisterin ja lähdevalinnan rakenne

Ensimmäisessä versiossa instanssilla on yksi yhteinen lähderekisteri tiedostossa `data/sources/registry.json`. Rekisterin juurirakenne sisältää `schema_version`- ja `sources`-kentät. Yksi keskitetty rekisteritiedosto helpottaa lähde- ja kanavatunnisteiden yksilöllisyyden sekä viittausten eheyden tarkistamista. Tarkka sijoittelu voidaan vielä vahvistaa nykyisen tiedostorakenteen inventaarion yhteydessä, mutta useita rinnakkaisia lähderekistereitä ei oteta ensimmäiseen versioon.

Lähdetietue sisältää vähintään kentät `id`, `name`, `publisher`, `source_type`, `description`, `homepage_url`, `languages`, `regions`, `reliability`, `reliability_notes`, valinnaiset `timezone` ja `timezone_basis`, `technical_access` sekä `channels`. Lähdetyypin sallitut arvot ovat `news_media`, `official_source`, `social_media`, `forum`, `blog`, `database`, `video_platform`, `event_listing` ja `other`. Toimituksellisen luotettavuuden arvot ovat `high`, `medium`, `low` ja `unassessed`; luokitus kuvaa lähteen arvioitua käyttökelpoisuutta eikä takaa yksittäisen julkaisun oikeellisuutta. Kielet ilmaistaan BCP 47 -tunnisteilla ja alueet ISO 3166-1 alpha-2 -maatunnisteilla tai arvolla `global`. Tyhjä kieli- tai aluelista tarkoittaa, ettei tietoa ole määritelty, ei sitä, että lähde kattaisi kaikki kielet tai alueet.

Jokainen lähde sisältää vähintään yhden sisältökanavan. Kanavatietue sisältää kentät `channel_id`, `name`, `url`, `channel_type`, `content_scope`, mahdolliset `languages`- ja `regions`-tarkennukset, valinnaiset `timezone` ja `timezone_basis` sekä kanavakohtaisen `technical_access`-kuvauksen. Kanavatyypin arvot ovat `website`, `rss`, `api`, `social_profile`, `video_channel`, `database_endpoint`, `event_calendar` ja `other`. Kanavan kielet ja alueet voivat tarkentaa lähteen vastaavia tietoja. Lähteen valinta ilman kanavatunnistetta ei tarkoita automaattisesti kaikkien kanavien valitsemista: käytettävät kanavat yksilöidään aina eksplisiittisesti.

Lähdetason tekninen saavutettavuus kuvaa julkaisijaa tai verkkopalvelua yleisesti. Sen tietoja voivat olla `access_model` ( `public`, `account_required`, `subscription_required`, `mixed` tai `unknown` ), `terms_url`, `api_documentation_url`, `usage_limit_notes` ja `notes`. Kanavatason tekninen saavutettavuus voi tarkentaa `access_model`-arvoa ja kuvata sisältömuotoa (`html`, `rss`, `atom`, `json`, `xml`, `pdf`, `video`, `mixed` tai `unknown`), JavaScript-riippuvuutta, sivutustapaa (`none`, `page_number`, `cursor`, `infinite_scroll` tai `unknown`) sekä kanavakohtaisia käyttörajoitteita ja huomioita. Nämä ovat rekisteriin tallennettavia yleisiä ominaisuuksia; yksittäisen ajon HTTP-tilat, vasteajat, avaus- ja lukemisvirheet sekä onnistumiset kuuluvat ajohistoriaan. Aikavyöhyke ja sen määrityksen peruste annetaan yhdessä aina, kun aikavyöhyke määritellään.

Lähteen `id` ja kanavan `channel_id` noudattavat tunnisteiden hyväksyttyä slug-syntaksia. Lähdetunniste on yksilöllinen koko rekisterissä ja kanavatunniste on globaalisti yksilöllinen lähteestä riippumatta. Tunniste säilyy, vaikka nimi tai osoite muuttuu; poistettua tunnistetta ei käytetä uudelleen. Kukin kanava kuuluu täsmälleen yhdelle lähteelle.

Tehtävätyypin määritys sisältää kaksi erillistä lähdeluetteloa: `default_sources` ja `required_sources`. Oletuslähteen käyttömerkintä yksilöi `source_id`-tunnisteen, `priority`-arvon, `roles`-roolit ja eksplisiittisesti valitut `channels`-kanavat. Tärkeys on kokonaisluku 1–5, jossa 1 on tärkein; jos uuden lähteen tärkeyttä ei anneta, käytetään arvoa 3. Roolit ovat `primary`, `discovery`, `verification`, `official_confirmation` ja `context`. Kanavakohtaiset käyttöasetukset voivat tarkentaa lähdemerkinnän tärkeyttä ja rooleja sekä sisältää kanavakohtaisia seurantahuomioita. Kanavakohtainen arvo korvaa vastaavan lähdetason käyttöarvon. Roolitaulukko korvataan kokonaan, sitä ei yhdistetä automaattisesti. Rekisterin pysyviä perustietoja tai teknisiä ominaisuuksia ei voi muuttaa lähdevalinnan käyttöasetuksilla.

Pakollinen lähde määritellään täsmällisenä `source_id`- ja `channel_id`-parina. Pakollisen parin on sisällyttävä tehtävätyypin oletuslähteisiin. Näin pakollisuus kohdistuu yksiselitteiseen sisältökanavaan eikä epämääräisesti kaikkiin saman julkaisijan kanaviin.

Aihekohtainen määritys valitsee lähteet aina aiheen ja tehtävätyypin yhdistelmälle. Sen `source_selection`-objektissa on `mode` ja `entries`; jos objekti puuttuu, oletuksena käytetään `extend`-toimintatapaa ilman aihekohtaisia muutoksia. `inherit` käyttää tehtävätyypin oletuslähteitä sellaisinaan eikä salli `entries`-merkintöjä. `extend` säilyttää oletuslähteet ja sallii uusien lähteiden lisäämisen sekä käyttöasetusten tarkentamisen; oletuslähteitä ei voi poistaa. `replace` korvaa valinnaiset oletuslähteet aihekohtaisella listalla, mutta tehtävätyypin pakolliset lähteet säilyvät aina. Jos pakollinen pari puuttuu korvaavasta listasta, se lisätään alkuperäisine oletusasetuksineen; jos se on mukana, sen asetuksia voidaan tarkentaa mutta sitä ei voi poistaa. `extend` on oletustoimintatapa.

Lopullisen lähdelistan järjestys on deterministinen. `inherit)-tilassa säilyy oletuslistan järjestys. `extend)-tilassa oletusjärjestys säilyy ja uudet merkinnät lisätään aihekohtaisessa järjestyksessä. `replace)-tilassa aihekohtainen järjestys säilyy ja puuttuvat pakolliset parit lisätään `required_sources`-listan järjestyksessä. Tärkeysarvo on erillinen listajärjestyksestä. Sama lähde–kanava-pari saa esiintyä lopullisessa listassa vain kerran; päällekkäisyyksiä ei ratkaista automaattisella arvailulla.

Lähdeviittaukset validoidaan samaa tehtäväpyyntöä varten kiinnitetyn `instance_revision`-revision lähderekisteriä vasten. Validoinnissa tarkistetaan lähde- ja kanavatunnisteiden yksilöllisyys, vähintään yksi kanava lähdettä kohden, kanavan kuuluminen ilmoitettuun lähteeseen, URL-osoitteiden absoluuttinen HTTP/HTTPS-muoto, aikavyöhykkeen ja määritysperusteen parillisuus, kieli-, alue- ja luokitteluarvojen kelvollisuus, kaikkien viittausten löytyminen, pakollisten parien olemassaolo sekä lähde–kanava-parien yksikäsitteisyys. Lisäksi tarkistetaan, että `inherit` ei sisällä aihekohtaisia merkintöjä, `extend` ei poista oletuksia ja `replace` säilyttää pakolliset lähteet. Puuttuvaa lähdettä tai kanavaa ei korvata automaattisesti toisella.

Raportintuottaja voi etsiä uutisoitavaa myös tehtäväpyynnön lähderekisterin ulkopuolisista lähteistä, jos tehtävätyypin asetukset ja aihekohtaiset ylikirjoitukset sallivat sen. Lähteiden etsiminen ja niiden pysyvä rekisteröinti ovat toisistaan riippumattomia asetuksia, jotka ratkaistaan samalla hyväksytyllä yhdistämisjärjestyksellä kuin muut tehtäväasetukset. `source_discovery.mode` määrittää lähdehaun: `disabled` sallii vain rekisteriin kuuluvien lähteiden käytön, kun taas `use_unregistered` sallii raportintuottajan etsiä ja käyttää myös rekisterin ulkopuolisia lähteitä kyseisessä ajossa. `source_registry_addition.mode` määrittää löydettyjen lähteiden pysyvän käsittelyn: `disabled` ei tallenna niitä rekisteriin, `propose` muodostaa ylläpitäjän tarkistettavan lähde-ehdotuksen ja `automatic` lisää lähteen rekisteriin automaattisesti vasta ehdotuksen validoinnin ja duplikaattitarkistuksen jälkeen. Asetukset eivät korvaa toisiaan: jos `source_discovery.mode` on `disabled`, tämän mekanismin kautta ei löydy uusia lähteitä, eikä rekisteröintiasetus yksin käynnistä lähdehakua.

Tehtäväpyynnön `instance_revision` yksilöi ajossa käytettävän muuttumattoman lähderekisterin. Raportintuottaja ei saa muuttaa tätä rekisteriä eikä ajon syötteitä kesken suorituksen. Rekisterin ulkopuolinen lähde voidaan käyttää kyseisessä ajossa, jos lähdehaku on sallittu; sen tiedot ja rekisteröintiehdotus toimitetaan erillään käytetyn rekisterin snapshotista. Ehdotukset käsitellään vasta ajon päätyttyä. `disabled`-tilassa ehdotusta ei tallenneta pysyvästi, `propose`-tilassa se asetetaan ylläpitäjän hyväksyttäväksi ja `automatic`-tilassa se lisätään rekisteriin vasta validoinnin jälkeen hallitussa rekisteripäivityksessä. Uusi rekisteriversio vaikuttaa vasta seuraaviin tehtäväpyyntöihin, ei jo käynnissä olevaan ajoon.

Ennen rekisteriin lisäämistä uuden lähteen perustiedot ja vähintään yksi sisältökanava validoidaan. Lisäksi tarkistetaan, ettei lähde tai kanava ole jo rekisterissä: vertailussa hyödynnetään vähintään julkaisijaa, kanavan ja kotisivun URL-osoitteita sekä muita käytettävissä olevia lähdetietoja, jotta samaa lähdettä ei lisätä rinnakkaisina tietueina. Jos vastaava lähde tai kanava löytyy, ehdotus yhdistetään olemassa olevaan tietueeseen hallitusti eikä luoda duplikaattia. Automaattisesti lisätyn lähteen `reliability` on `unassessed`, ellei sen toimituksellista luotettavuutta ole erikseen arvioitu. Lähteen alkuperä ja löytämisajankohta säilytetään jäljitettävyyttä varten. Rekisteröinti ei itsessään tarkoita lähteen luotettavaksi hyväksymistä. Rekisterin ulkopuoliset lähteet ja niiden käytön perusteet on voitava erottaa rekisteriin kuuluvista lähteistä ajon raportoinnissa ja jälkikäteisessä tarkastelussa.

Markdown-ohjeita ei validoida JSON Scheman avulla. Niiden tarkistuksiin kuuluvat yksilöllinen ohjetunniste, tiedoston olemassaolo oikeassa repositoriossa ja kiinnitetyssä commitissa, repositoriojuureen suhteutettu turvallinen polku, ohjeiden oikea järjestys ja duplikaattien puuttuminen. Ohjeiden sisällön tulee olla ristiriidaton koneellisten määritysten kanssa. Ohjeiden metatietoa ei kahdenneta Markdown-etusivulla, vaan se pidetään JSON-määrityksissä ja tehtäväpyynnön viittauksissa.

#### Skeemakokonaisuuden rakenne ja validointiperiaatteet

JSON Schema Draft 2020-12 on kaikkien rakenteisten määritysten ja tietosopimusten rakenteellisen validoinnin standardi. Skeemat kuuluvat yhteiseen ohjelmistorepoon; instanssirepoon kuuluvat niiden avulla validoitavat varsinaiset määritykset ja aineistot. Jokaisella itsenäisellä tietotyypillä on oma pääskeemansa. Yhteisiä rakenteita varten käytetään uudelleenkäytettäviä osaskeemoja, esimerkiksi tunnisteille, Git-revisioille, aikaleimoille, tiedostoviittauksille, lähde- ja kanavaviittauksille sekä virhekuvauksille.

Skeemakokonaisuuden alustava hakemistorakenne on:

```text
schemas/
  common/
    identifier.schema.json
    revision.schema.json
    timestamp.schema.json
    file-reference.schema.json
    source-reference.schema.json
    error.schema.json
  definitions/
    task-type.schema.json
    task-config.schema.json
    profile.schema.json
    topic.schema.json
    source-registry.schema.json
  contracts/
    task-request.schema.json
    delivery-metadata.schema.json
    delivery-package.schema.json
    run-record.schema.json
  examples/
```

Rakenne on suunnitteluratkaisu; yksittäisten tiedostojen tarkka sisältö ja lopullinen sijoittelu määritellään toteutussuunnittelun skeematyössä. Tiedostonimet ovat englanninkielisiä, pienaakkosin ja yhdysmerkein, ja skeematiedostojen pääte on `.schema.json`. Skeemoilla on vakaat `$id`-tunnisteet, jotka eivät riipu repositorion nimestä tai tiedostopolusta. Ajon aikainen validointi ei hae skeemoja ulkoisista verkkopalveluista, vaan käyttää ohjelmistorevision mukana toimitettua skeemakokonaisuutta.

Skeemojen vastuut jakautuvat seuraavasti:

- **Tehtävätyypin määrityksen skeema** määrittelee tehtävätyypin tunnisteen ja kuvauksen, asetusskeeman viittauksen, oletusasetukset, sallitut ja ylikirjoitettavat asetuskohdat sekä käsittely-, raportointi- ja toimitusvaatimukset.
- **Tehtävätyyppikohtainen asetusskeema** määrittelee lopullisen `resolved_config`-rakenteen, asetusten tyypit, pakollisuuden, rajat ja ylikirjoitettavuuden. Tehtävätyypin määritys viittaa tähän skeemaan.
- **Profiilin skeema** validoi profiilin oman rakenteen. Profiilin asetukset validoidaan lisäksi siihen tehtävätyyppiin kuuluvalla asetusskeemalla.
- **Aihekohtaisen määrityksen skeema** validoi aiheen, tehtävätyypin, järjestetyt profiiliviittaukset, asetukset sekä lähdevalinnan ja muut aihekohtaiset määritystiedot.
- **Lähderekisterin skeema** validoi lähteiden perustiedot ja sisältökanavat. Ajokohtaiset tarkistushavainnot ja lähteiden käyttöasetukset eivät kuulu tähän rekisteriin.
- **Tehtäväpyynnön skeema** validoi hyväksytyn tehtäväpyynnön juurirakenteen ja sen sisäiset tietorakenteet.
- **Toimitusmetatietojen skeema** validoi tuottajan toimittamat tulosmetatiedot ja lähdehavainnot. Se pidetään erillään vastaanottajan ylläpitämän kanonisen ajotietueen skeemasta.
- **Toimituspaketin skeema(t)** määrittelevät toimituksen tulostilakohtaiset tiedostot ja niiden väliset vaatimukset. **Kanonisen ajotietueen skeema** määrittelee vastaanottajan ajonhallintatiedot ja säilyvän tapahtumahistorian.

Tuntemattomat ylimääräiset kentät hylätään kaikilla skeematasoilla. Tämä toteutetaan Draft 2020-12 -standardin mukaisilla sulkevuusmäärityksillä, kuten `additionalProperties: false` tai yhdistetyissä skeemoissa tarvittaessa `unevaluatedProperties: false`, niin että myös `$ref`- ja `allOf`-rakenteiden käyttäytyminen on yksiselitteinen. Skeemojen tarkassa koostamisessa vältetään ratkaisuja, joissa osaskeemojen käyttö vahingossa sallisi tuntemattomia kenttiä.

Skeemojen versiointi noudattaa semanttista versionumerointia. Yhteensopiva korjaus tai täsmennys kasvattaa PATCH-osaa; uusi taaksepäin yhteensopiva ominaisuus kasvattaa MINOR-osaa; yhteensopimaton rakenteellinen muutos kasvattaa MAJOR-osaa. Julkaistua skeemaversiota ei muuteta hiljaisesti yhteensopimattomaksi. Tehtäväpyynnön ja toimitusmetatietojen omat `schema_version`-kentät säilyvät. Käytetty skeemakokonaisuus yksilöidään lisäksi ohjelmistorevision avulla, joka sitoo skeemat muuttumattomaan ohjelmistocommitiin.

Validointi toteutetaan vaiheittain:

1. JSON-aineiston jäsennys ja syntaksin tarkistus.
2. Yksittäisen määrityksen tai tietosopimuksen rakenteellinen skeemavalidointi.
3. Viittausten, tiedostojen, repositorioiden ja kiinnitettyjen commit-revisioiden tarkistus.
4. Määritysten välisten yhteensopivuuksien, tehtävätyypin ja profiilien soveltuvuuden sekä muiden välttämättömien ristiriitojen tarkistus.
5. Asetusten yhdistäminen hyväksytyssä järjestyksessä.
6. Lopullisen `resolved_config`-kokonaisuuden validointi tehtävätyyppikohtaisella asetusskeemalla.
7. Tehtäväpyynnön muodostaminen vasta kaikkien vaadittujen tarkistusten onnistuttua.

Rakenteellinen JSON Schema -validointi erotetaan toiminnallisista tarkistuksista. Skeema tarkistaa tietorakenteen, tyypit, pakolliset kentät ja rakenteelliset rajat. Erillinen validointilogiikka tarkistaa esimerkiksi viitattujen tiedostojen olemassaolon oikeassa repositoriossa ja commitissa, aikaleiman offsetin vastaavuuden yleiseen IANA-aikavyöhykkeeseen, aikavälin järjestyksen, viittausten keskinäisen yhteensopivuuden sekä määritysten yhdistämissäännöt. Aikaleimojen `format`-tarkistukset otetaan validointikirjastossa eksplisiittisesti käyttöön; pelkkään `format`-avainsanan olemassaoloon ei luoteta, koska sen tarkistaminen ei kaikissa toteutuksissa automaattisesti johda virheellisen arvon hylkäämiseen.

Validointivirheen tulee yksilöidä tiedosto ja kenttäpolku, esimerkiksi `resolved_config.sources[2].channel_id`, sekä virhetyyppi ja selkokielinen kuvaus. Odotettu ja havaittu arvo ilmoitetaan, kun se on mielekästä ja turvallista. Toisistaan riippumattomat virheet kerätään samaan tarkistuskertaan; virheestä riippuvat jatkotarkistukset ohitetaan, jotta käyttäjälle ei esitetä harhaanjohtavia seurausvirheitä. Virheellinen määritys estää tehtäväpyynnön muodostamisen, virhe kirjataan syineen ja sijaintitietoineen, eikä järjestelmä arvaa tai korjaa arvoja automaattisesti tai muodosta osittaista konfiguraatiota.

Markdown-ohjeita ei validoida JSON Scheman avulla. Niille tehdään erilliset tarkistukset, jotka kattavat tiedoston olemassaolon oikeassa repositoriossa ja commitissa, Markdownin jäsennettävyyden, otsikkohierarkian, paikallisten linkkien toimivuuden sekä ohjetunnisteiden ja versiotietojen johdonmukaisuuden.

Validointikirjastoksi valitaan toteutuskielelle yksi vakiintunut JSON Schema Draft 2020-12 -yhteensopiva kirjasto. Oma JSON Schema -tulkki ei kuulu ensimmäiseen versioon. Kirjaston versio ja sen riippuvuudet kiinnitetään. Skeemakokonaisuuden lataus, `$ref`-riippuvuuksien ratkaisu, määritysten yhdistämislogiikka ja lopullisen `resolved_config`-arvon validointi testataan.

Jokaiselle pääskeemalle laaditaan kelvollinen esimerkkiaineisto. Testeissä on myös virheellisiä esimerkkejä, jotka kattavat vähintään puuttuvat pakolliset kentät, väärät tietotyypit, tuntemattomat kentät, virheelliset tunnisteet, revisiot ja aikaleimat, rikkinäiset viittaukset, virheelliset asetukset sekä kielletyt ylikirjoitukset. GitHub Actions tarkistaa skeemat ja niiden testit aina, kun skeemoihin tai niitä koskevaan validointikoodiin tehdään muutoksia.

### 4.4 Seurantatyypit ja raporttipohjat

Kaikki aiheet käyttävät yhteistä suoritusprosessia. Seurantatyyppi määrittelee, millaisia havaintoja etsitään, mitä luokituksia tarvitaan ja mitä erityisiä tarkistuksia tehdään. Raporttipohja määrittelee RSS-raportin rakenteen.

Esimerkiksi tapahtuma- tai näytösseuranta voi käyttää samaa ajomallia kuin uutisseuranta, mutta sen määritys ja raporttipohja voivat käsitellä tapahtumapäiviä, tulevia ja menneitä tapahtumia sekä muutoksia.

Uuden seurantatyypin lisääminen voi vaatia teknistä toteutusta. Sen tulee olla rajattu laajennus yhteiseen järjestelmään, ei kokonaan erillinen automaatioarkkitehtuuri.

### 4.5 Aikataulut ja aiheen valinta

Jokainen käynnistys valitsee enintään yhden aiheen. Ajonhallinta lukee aktiiviset aihekonfiguraatiot ja ajantasaisen seurantatilan sekä valitsee seuraavan kelpoisen aiheen.

Valinta noudattaa seuraavia yksinkertaisia sääntöjä:

1. Pois käytöstä olevat aiheet eivät ole valittavissa.
2. Aihe on valittavissa, kun sen määrityksen mukainen seuranta on erääntynyt tai ajo on käynnistetty erikseen.
3. Erääntyneistä aiheista valitaan pisimpään odottanut.
4. Jos odotusaika on sama, käytetään vakaata järjestystä, jotta valinta on ennakoitava.
5. Jos sopivaa aihetta ei ole, käynnistys päättyy ilman aiheajoa.

Aihekohtainen ajotiheys määritellään määrityksessä. Eri seurantatyypeillä voi olla omat aikataulu- ja sisältösääntönsä, mutta ne eivät muuta yhden aiheen ajomallia.

Tehtävien ajastuksessa erotetaan kaksi asiaa: järjestelmän yhteinen tarkistusväli sekä aiheen ja tehtävätyypin yhdistelmäkohtainen suoritusväli. Yksi yhteinen ajastettu työnkulku tarkistaa säännöllisesti tehtäväjonon ja aktiivisen tehtävän määräajan. Yksittäisen aiheen tehtävä käynnistetään vasta, kun sen oma suoritusväli on erääntynyt ja muut käsittelyehdot sallivat sen. Yhteisen tarkistustyönkulun kiinteä tarkistusväli on **15 minuuttia**. Tämä väli koskee tehtäväjonon ja aktiivisen tehtävän määräajan tarkistamista, ei yksittäisen aiheen suoritusväliä. GitHub Actionsin ajastettu työnkulku voi ruuhkatilanteissa käynnistyä myöhässä tai jäädä käynnistymättä; 15 minuuttia on ajastuksen tavoiteltu väli, ei takuu täsmällisestä käynnistys- tai reagointiajasta.

Yhteisen tarkistustyönkulun voi käynnistää myös manuaalisesti esimerkiksi ylläpitoa tai tilanteen selvittämistä varten. Manuaalinen käynnistys käyttää samoja jono-, määräaika-, validointi- ja sarjallisuussääntöjä kuin ajastettu käynnistys. Se ei ohita aktiivista tehtävää, käynnistä rinnakkaista tehtävää eikä pakota tiettyä aihetta ajoon näiden sääntöjen vastaisesti.

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

Ensimmäisessä versiossa tehtävät käsitellään sarjallisesti: järjestelmässä on kerrallaan enintään yksi aktiivinen raportointitehtävä, eikä seuraavaa tehtävää käynnistetä ennen kuin edellinen on todettu onnistuneeksi tai kirjattu epäonnistuneeksi. Tämä koskee myös eri aiheita; eri aiheiden rinnakkaista käsittelyä ei toteuteta ensimmäisessä versiossa. Erillistä rinnakkaisten raportointitehtävien varaus-, lukitus- tai kilpailutilanteiden hallintaa ei tarvita. Sen sijaan tehtävän muodostus, määräajan valvonta ja toimituksen vastaanotto/käsittely on koordinoitava yhteisen instanssikohtaisen sarjallisuuden hallinnan kautta, jotta erilliset automaatioajot eivät voi käsitellä useita tehtäviä samanaikaisesti tai ohittaa edellisen tehtävän päättymistä. Sarjallinen käsittely ei poista tarvetta estää saman ajon kaksoistoimituksia ja kaksoisjulkaisuja: `run_id` ja idempotentti vastaanotto säilyvät.

Määräajan umpeutuminen ei yksinään tee tuottajan myöhemmin saapuvasta tuloksesta julkaisukelvotonta. Myöhäinen toimitus voidaan käsitellä alkuperäisen `run_id`-tunnisteensa perusteella ja hyväksyä sekä julkaista alkuperäisen ajon tuloksena, jos toimitus läpäisee kaikki normaalit validoinnit eikä samaa aihetta ja seurantatyyppiä koskevaa myöhempää ajoa ole vielä käynnistetty. Myöhäinen toimitus ei saa muuttaa myöhemmän ajon tehtäväpyyntöä, tulosta, ajotietuetta tai tilaa. Määräajan umpeutuminen ja sen jälkeen saapunut toimitus kirjataan erillisinä vastaanottajan todentamina tapahtumina; aiempaa määräajan umpeutumisen merkintää ei poisteta eikä vastaanottajan kirjaamaa epäonnistumista esitetä tuottajan tuloksena. Jos myöhempi saman aiheen ja seurantatyypin ajo on jo käynnistynyt tai jokin muu hyväksymisehto ei täyty, myöhäistä toimitusta ei julkaista. Vastaanotto, validointi ja mahdollinen jälkikäsittely koordinoidaan edelleen yhteisen instanssikohtaisen sarjallisuuden hallinnan kautta.



### 5.2 Käsittelyn valmistuminen ja tehtävän vapauttaminen

Ajon elinkaaressa erotetaan kolme asiaa:

- **Tuottajan tulos** kuvaa raportintuottajan itsensä ilmoittamaa tutkimus- ja raportointitulosta. Se tallennetaan vain, jos tuottaja toimittaa tuloksen.
- **Vastaanottajan käsittely** kuvaa toimituksen vastaanottoa, validointia, hyväksymistä tai hylkäämistä sekä julkaisua.
- **Ajon lopputila** kuvaa vastaanottajan muodostamaa kokonaisarviota siitä, päättyikö ajo onnistuneesti vai epäonnistuneesti.

Tuottajan tulos ei yksin ratkaise vastaanottajan käsittelyn onnistumista. Vastaavasti vastaanottajan aikakatkaisu tai muu havainto ei osoita, että raportintuottaja olisi itse ilmoittanut epäonnistumisesta.

Ajo onnistuu vastaanottajan näkökulmasta vain, kun toimitus on yhdistetty oikeaan `run_id`-ajoon, kaikki pakolliset validoinnit läpäistään, raportti hyväksytään käsiteltäväksi ja mahdollinen RSS-julkaisu onnistuu sekä julkaisutulos kirjataan ajohistoriaan. Pelkkä toimituksen vastaanotto tai validoinnin läpäisy ei vielä merkitse onnistumista. Julkaistavissa oleva osittainen tulos voidaan hyväksyä, kun se täyttää julkaisuehdot ja raportin puutteet kuvataan avoimesti.

Ajo päättyy vastaanottajan aktiivisen käsittelyn kannalta, kun jokin seuraavista toteutuu:

1. toimitus on validoitu ja hyväksytty, julkaisu on onnistunut ja lopputila kirjattu;
2. toimitus hylätään pakollisessa tarkistuksessa eikä sallittuja käsittely- tai uudelleenyritysmahdollisuuksia ole jäljellä;
3. vastaanotto, tallennus, julkaisu tai muu pakollinen käsittelyvaihe epäonnistuu pysyvästi eikä käsittelyä saada jatkettua konfiguroiduissa rajoissa; tai
4. tehtävän määräaika umpeutuu ilman hyväksyttävää toimitusta, jolloin vastaanottaja kirjaa aikakatkaisun ja oman epäonnistumishavaintonsa.

Aktiivinen tehtävä vapautetaan vasta, kun vastaanottajan käsittely on päätetty ja ajon lopputila on kirjattu kanoniseen ajohistoriaan. Seuraavaa tehtävää ei käynnistetä ennen tätä. Yksittäinen epäonnistunut käsittely-yritys ei vapauta tehtävää, jos käsittelyä voidaan vielä jatkaa. Kun käsittely on päätetty, jono voi edetä myös epäonnistumisen jälkeen. Epäonnistuminen ei itsessään käynnistä uutta tehtävää.

Uudelleenyritysten määrä, yritysten laskentatapa, määräajat ja muut vastaavat käsittelyrajat ovat konfiguroitavia toimintaparametreja. Niitä ei kovakoodata kiinteiksi lukumääriksi tai aikarajoiksi. Soveltuva tehtävätyypin määritys ja tarvittaessa profiili määrittävät arvot; asetusten yhdistämisen jälkeen käytetyt arvot sisältyvät tehtäväpyynnön `resolved_config`-kokoonpanoon. Yhteinen toteutus noudattaa ratkaistuja arvoja eikä keksi niille omia oletuksia. Konfiguraation sallitut tyypit, rajat ja oletusarvot määritellään tehtävätyypin skeemassa ja määrityksissä. Jos pakollinen arvo puuttuu tai on virheellinen, tehtävää ei muodosteta.

Kun käsittely päättyy epäonnistuneena, vastaanottaja kirjaa havaitun syyn ja siihenastiset tapahtumat. Tuottajan tulosta ei päätellä vastaanottajan havainnoista. Ajohistoriasta on voitava erottaa tehtävän käynnistys ja määräaika, toimituksen saapuminen, tuottajan ilmoittama tulos, vastaanottajan käsittelyvaiheet, validointi, julkaisu, ajon lopputila sekä aktiivisen käsittelyn vapautushetki. Tapahtumat säilytetään aikajärjestyksessä; myöhemmät tapahtumat eivät korvaa aiempia.

Aikakatkaisun jälkeen saapuva toimitus käsitellään alkuperäisen `run_id`-tunnisteen perusteella aiemmin määritellyin myöhäisen toimituksen ehdoin. Myöhäinen toimitus voi täydentää samaa ajohistoriatietuetta uusilla tapahtumilla, mutta se ei avaa jo vapautettua tehtävää uudelleen, muuta jo käynnistetyn myöhemmän ajon tietoja eikä siirrä aktiivista tehtävää taaksepäin. Jos myöhempi saman aiheen ja seurantatyypin ajo on jo käynnistetty, myöhäistä toimitusta ei julkaista.

Tämä on looginen prosessi. Tiedonsiirron tarkka tekninen mekanismi ja vastaanottorajapinnan toteutus valitaan erillisessä toteutussuunnittelussa. Tuottajan ei edellytetä käyttävän tiettyä palvelua tai kirjoittavan suoraan repositorioon.

### 5.1 Tehtäväpyynnön tietosopimus

Raportintuottajalle annetaan yksi muuttumaton, rakenteinen JSON-tehtäväpyyntö kutakin ajoa varten. Tehtäväpyyntö yksilöi ajon, aiheen ja seurantatyypin, käytetyt ohjelmisto- ja instanssirevisiot, seuranta-aikavälin, muodostamishetken ja toimituksen määräajan sekä RSS-historian, käytetyt profiilit, luettavat ohjeet ja valmiiksi ratkaistun suorituskokoonpanon.

Tehtäväpyynnön juuritason kentät ovat:

- schema_version: tehtäväpyynnön rakenteen semanttinen versio;
- run_id: yksilöllinen ajotunniste;
- topic_id ja task_type: aiheen ja tehtävätyypin tunnisteet;
- software_revision ja instance_revision: käytettyjen ohjelmisto- ja instanssirevisioiden commit-tunnisteet;
- period: seuranta-aikavälin from- ja to-arvot;
- issued_at ja deadline_at: tehtäväpyynnön muodostamishetki ja toimituksen määräaika;
- history: RSS-historian repositorio, polku ja lähtörevisio;
- profiles: käytettyjen määritysprofiilien järjestetty luettelo;
- inputs: tehtävän tarvitsemien rakenteisten syöteaineistojen järjestetty viittausluettelo, esimerkiksi lähderekisteri;
- instructions: pakollisesti luettavien ohjeiden järjestetty luettelo; siihen sisältyy yhteinen raportintekijän perusprompti ensimmäisenä, sitten tehtävätyypin ohje, järjestetyt profiiliohjeet ja aihekohtainen ohje;
- resolved_config: tehtävän suoritukseen tarvittavat valmiiksi ratkaistut asetukset.

Tehtäväpyynnön tunnisteet, aikaleimat, repositorioviittaukset ja profiilien sekä ohjeiden järjestys ovat yksiselitteisiä ja validoitavia. Yhteinen raportintekijän perusprompti kuuluu ohjelmistorepoon ja yksilöidään `software_revision`-revisioon sidotulla ohjeviittauksella. Se ei korvaa tehtävätyypin, profiilien tai aiheen ohjeita. `period` tulkitaan puoliksi avoimena aikavälinä `[from, to)`: alkupiste sisältyy ja loppupiste ei sisälly aikaväliin; peräkkäiset jaksot eivät siten mene päällekkäin. resolved_config sisältää aina yleisen IANA-aikavyöhykkeen. Tehtäväpyyntö ei sisällä ohjetekstejä, rakenteisia syöteaineistoja tai RSS-historiaa itsessään, vaan viittaukset niiden muuttumattomiin lähteisiin. `inputs` erottaa rakenteiset aineistot `instructions`-taulukon Markdown-ohjeista, `profiles`-taulukon määritysprofiileista ja `resolved_config`-objektin asetuksista. Tehtäväpyynnön tarkat tietotyypit, pakollisuus, kenttäkohtaiset rajat ja validointisäännöt määritellään toteutussuunnitelman tehtäväpyyntöä koskevassa kohdassa ja myöhemmin toimitussopimuksen skeemassa. Määrittelemättömät ylimääräiset kentät hylätään. Tehtäväpyyntöä ei muuteta muodostamisen jälkeen; ajon eteneminen ja vastaanottajan tapahtumat kirjataan erilliseen ajohistoriaan.

## 6. Ajon tulos ja ajotiedot

### 6.1 Ajotietue, toimitusmetatiedot ja tapahtumahistoria

Ajon tiedot jaetaan kolmeen erilliseen, toisiinsa viitattuun tietokokonaisuuteen, joiden omistajuus ja tehtävät pidetään erillään:

1. **Tuottajan toimitusmetatiedot** ovat raportintuottajan vastuulla ja kuvaavat sen toimittamaa tulosta. Ne toimitetaan osana toimituspakettia erillisessä `metadata.json`-tiedostossa. Jos tuottaja ei toimita tulosta, toimitusmetatietoja ei ole eikä vastaanottaja saa päätellä tai esittää niitä tuottajan ilmoittamina.
2. **Kanoninen ajotietue** on vastaanottavan järjestelmän vastuulla. Se yksilöi ajon ja kokoaa vastaanottajan tarvitseman ajon nykytilan, käsittelytiedot sekä viittaukset hyväksyttyyn toimitukseen ja julkaisuun. Siihen ei kopioida tarpeettomasti kaikkia toimitusmetatietojen kenttiä, vaan tuottajan tiedot säilyvät erillisinä ja niihin viitataan.
3. **Ajon tapahtumahistoria** on vastaanottavan järjestelmän vastuulla. Se tallentaa ajon käsittelyvaiheet ja havainnot aikajärjestyksessä. Historia on loogisesti vain lisäämiseen perustuva: aiempia tapahtumia ei poisteta eikä ylikirjoiteta, vaan myöhemmät tapahtumat täydentävät kokonaisuutta.

Tietokokonaisuudet liittyvät samaan ajoon `run_id`-tunnisteen avulla ja niissä käytetään toimituksen sekä käsittely-yrityksen tunnisteita silloin, kun ne ovat kyseisessä kokonaisuudessa tarpeen. Tuottajan tulostila (`success`, `partial`, `no_report` tai tuottajan ilmoittama `failed`) ja vastaanottajan ajon lopputila/käsittelytila ovat eri tietoja ja niiden alkuperä säilytetään.

Tapahtumahistoria sisältää esimerkiksi ajon käynnistymisen, määräajan ylittymisen, toimituksen vastaanoton, validoinnin, hyväksynnän tai hylkäyksen, julkaisun sekä uudelleenyritysten ja myöhäisten toimitusten käsittelyn. Tapahtumien tarkat tyypit, kentät, järjestämisen tekniset säännöt ja tietokokonaisuuksien väliset tarkat viittaukset määritellään myöhemmässä teknisessä suunnittelussa.

Tuottajan toimitusmetatietojen sisältö jäsennetään seuraaviin tietoryhmiin:

- **Tunnisteet ja versiot:** ajon ja toimituksen tunnisteet, tietosopimuksen versio sekä käytetyn ohjelmiston ja instanssin revisiot.
- **Tehtävän kuvaus:** aihe, tehtävätyyppi ja seuranta-aikaväli.
- **Tuottajan tulos:** tuottajan ilmoittama tulostila ja raportin tuottamiseen liittyvät tiedot.
- **Lähdetarkistukset:** käytetyt lähteet ja sisältökanavat, tarkistusyritykset sekä niiden tulokset.

Lähdetarkistusten tietoryhmä jäsentyy kolmeen osaan: (1) ajossa käytetyt lähteet, (2) niistä eksplisiittisesti valitut ja käytetyt sisältökanavat sekä (3) kanavakohtaiset tarkistusyritykset tuloksineen. Myös rekisterin ulkopuoliset lähteet voidaan kuvata tässä ryhmässä erillisinä toimituskohtaisina lähteinä; niitä ei esitetä rekisteriin kuuluvina. Tarkat kentät, tarkistusyrityksen tulosluokat ja yksityiskohtainen tietosisältö täsmennetään erikseen. Ryhmittely ei muuta lähderekisterin pysyvien perustietojen ja ajohistorian toteutuneiden tarkistustulosten vastuunjakoa.

Tarkistusyrityksestä tallennetaan vähintään tarkistusajankohta, tarkistuksen tulos, tieto siitä löytyikö uutta tai tehtävän kannalta relevanttia sisältöä, saatavilla oleva tekninen tulos (esimerkiksi HTTP-tilakoodi) sekä mahdolliset virhe- ja huomiotiedot. Teknisen tarkistuksen onnistuminen erotetaan sisällöllisestä tuloksesta: onnistunut tarkistus ilman uutta sisältöä ei ole epäonnistuminen. Tietoryhmän tarkka kenttärakenne ja sallitut tulosarvot täsmennetään myöhemmin.
- **Havainnot ja laadunvarmistus:** raportoitavien havaintojen yhteenveto ja laaduntarkistuksen tulokset.
- **Tuottajan tiedot:** valinnaiset tiedot käytetystä raportintuottajasta.

Ensimmäiseen tietoryhmään kuuluvat seuraavat kentät:

- `schema_version`: toimitusmetatietojen tietosopimuksen versio.
- `run_id`: ajon tunniste, jonka vastaanottaja on muodostanut tehtäväpyyntöä varten; tuottaja säilyttää sen muuttumattomana toimituksessa.
- `delivery_id`: tuottajan toimituspaketin tunniste. Tuottaja muodostaa sen ensimmäiselle toimitukselle ja säilyttää saman tunnisteen saman toimituksen uudelleenlähetyksissä.
- `topic_id`: seurattavan aiheen tunniste.
- `task_type`: suoritetun tehtävätyypin tunniste.
- `software_revision`: tehtäväpyynnössä ilmoitettu käytetyn yhteisen ohjelmiston muuttumaton Git-commit.
- `instance_revision`: tehtäväpyynnössä ilmoitettu käytetyn instanssin muuttumaton Git-commit.

Tuottaja ei muodosta uutta `run_id`-tunnistetta eikä muuta tehtäväpyynnön tunnisteita tai revisioita. Vastaanottajan käsittely-yrityksen `attempt_id` ei kuulu tuottajan toimitusmetatietoihin: sen muodostaa ja kirjaa vastaanottaja omaan ajonhallintaansa.

Toiseen tietoryhmään, **Tehtävän kuvaus**, kuuluu kenttä `period`, joka kuvaa seurannan aikaväliä. Se sisältää tehtäväpyynnön mukaiset `from`- ja `to`-arvot; `to` voi olla `null`, jos seurannan päätepiste ei ole ennalta tiedossa. `topic_id` ja `task_type` kuvaavat tehtävän tunnistetta ja kuuluvat vain ensimmäiseen tietoryhmään, joten niitä ei toisteta metatiedoissa.

Kolmanteen tietoryhmään, **Tuottajan tulos**, kuuluvat seuraavat kentät:

- `status`: tuottajan ilmoittama tulostila. Sallitut arvot ovat `success`, `partial`, `no_report` ja `failed`.
- `started_at`: hetki, jolloin tuottaja aloitti tehtävän suorittamisen.
- `completed_at`: hetki, jolloin tuottajan suoritus päättyi.

Aikaleimat ilmoitetaan ISO 8601 -muodossa tehtäväpyynnön `resolved_config.timezone`-asetuksen mukaisessa paikallisessa ajassa ja kyseisen ajanhetken numeerisella UTC-offsetilla. Tuottajan `status` kuvaa vain tuottajan omaa tulosta. Jos toimitusta ei saada, tuottajan tulos jää puuttuvaksi; vastaanottaja kirjaa oman epäonnistumishavaintonsa erilliseen ajotietueeseen eikä päättele siitä tuottajan `status`-arvoa. Vastaanottajan vastaanotto-, validointi- ja julkaisutilat eivät kuulu tähän ryhmään.

Tämä ryhmittely määrittelee toimitusmetatietojen sisällölliset vastuualueet, ei vielä kaikkia yksittäisiä kenttiä, niiden tarkkoja nimiä tai pakollisuutta. Jo aiemmin määritellyt metatietojen vähimmäistiedot säilyvät voimassa. Vastaanottajan vastaanotto-, validointi-, julkaisu- ja käsittelytilat eivät kuulu tuottajan metatietoihin vaan vastaanottajan ajotietueeseen ja tapahtumahistoriaan.

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
| Lähteiden avausyritykset | lähderekisterin vakaa tunniste, yrityksen tulos, ajankohta ja tunnistettu epäonnistumisen luokka | Tuottaja; vastaanottaja validoi ja tallentaa |
| Laadunvarmistus | laadunarvioinnin tulos, virheet ja varoitukset | Tuottaja |
| Vastaanotto | vastaanotto- ja validointitila sekä turvallinen virheluokka | Vastaanottava järjestelmä |
| Raportti | syntyikö RSS-item, sen GUID ja otsikko, jos ne ovat olemassa | Tuottaja ja vastaanottava järjestelmä |
| Julkaisu | kohdesyöte, julkaisun tila ja julkaisuajankohta | Vastaanottava järjestelmä |

Ajotietojen tarkoitus on kuvata, mitä tapahtui ja millä tuloksella. Niihin ei tallenneta tarpeettomasti koko tutkimusketjua, raakaa keskustelutekstiä tai kaikkia lähdesivuista kopioituja sisältöjä. Ajotiedot eivät ole yksityiskohtainen tekninen tapahtumaloki.

Lähteiden tarkistamisesta tallennetaan lisäksi lähdekohtaiset käyttötilastot. Jokaisesta tehtävän aikana tosiasiallisesti avatuksi tai avausyrityksen kohteeksi joutuneesta lähteestä kirjataan vähintään lähderekisterin vakaa tunniste, yrityksen ajankohta, avauksen tulos ja epäonnistumisen luokka silloin kun se voidaan todeta. Avausyrityksen onnistuminen erotetaan sisällön laadusta, relevanssista ja siitä, löytyikö lähteestä raportoitavaa tietoa. Avaamatta jäänyttä lähdettä ei lasketa onnistuneeksi eikä epäonnistuneeksi avausyritykseksi.

Valvomon lähdetilastojen tulee voida esittää lähdekohtaisesti tarkistusyritysten, onnistuneiden avausten ja epäonnistuneiden avausten määrät, onnistumisaste nimittäjineen, viimeisin onnistuminen ja epäonnistuminen sekä kehitys valitulla tarkastelujaksolla. Tilastoissa erotellaan mahdollisuuksien mukaan tilapäiset tekniset virheet, pysyvältä vaikuttavat virheet, käyttörajoitukset/estot ja muut tunnistetut syyt. Tuntemattomia syitä ei arvata. Pieniä otoksia tai puuttuvaa tietoa ei esitetä harhaanjohtavina prosentteina.

Lähdetilastot perustuvat raportintekijän ilmoittamiin lähdekohtaisiin havaintoihin, jotka vastaanottaja validoi ja tallentaa osaksi ajon kanonista historiaa. Sama lähde yksilöidään lähderekisterin vakaalla tunnisteella, jotta tilastoja voidaan koota eri ajoista. Lähteen URL:n tai nimen muuttuminen ei saa huomaamatta yhdistää eri lähteitä tai katkaista tunnistetta.

### 6.3 Tuloksen ja käsittelyn tilat

**Tuottajan tulos:**

- `success`: tutkimus- ja raportointityö valmistui;
- `partial`: työ valmistui osittain, ja rajoitteet on kuvattu;
- `no_report`: työ valmistui, mutta uutta raportoitavaa ei löytynyt;
- `failed`: tuottaja ilmoittaa oman suorituksensa epäonnistuneen. Tämä arvo kuvaa vain tuottajan toimittamaa tulosta; vastaanottaja voi kirjata ajon epäonnistuneeksi myös ilman tuottajan tulosta.

`no_report` on onnistunut seuranta ilman RSS-itemiä, ei virhe.

`partial` kuvaa osittaista seurantaa. Jos osittaisesta seurannasta syntyy raportti, se julkaistaan RSS-syötteeseen. Raportissa kerrotaan selvästi, mikä jäi tarkistamatta tai puutteelliseksi, miksi näin tapahtui ja miten se vaikuttaa kattavuuteen. Myöhemmät ajot eivät muokkaa julkaistua itemiä: olennainen täydennys tai korjaus julkaistaan uutena, avoimesti alkuperäiseen raporttiin viittaavana iteminä.

**Vastaanottavan järjestelmän käsittelyä ei kuvata myöhäisen toimituksen tapauksessa yhdellä yliajettavalla lopputilalla.** Vastaanottaja kirjaa ajon käsittelyn erillisinä, aikajärjestyksessä säilyvinä tapahtumina. Tapahtumia ovat vähintään vastaanoton määräajan umpeutuminen tai muu toimituksen puuttumisen havainto, myöhäisen toimituksen vastaanotto, validoinnin aloitus ja tulos, toimituksen hyväksyminen tai hylkääminen sekä mahdollinen RSS-julkaisu tai julkaisun epäonnistuminen. Tapahtumat kirjataan vain, kun vastaanottaja voi todentaa ne. Aiemmat tapahtumat säilyvät muuttumattomina, eikä myöhempi tapahtuma korvaa niitä.

Valvomo näyttää tapahtumaketjusta sekä alkuperäisen määräajan ylityksen että myöhäisen toimituksen myöhemmät käsittelyvaiheet. Ajon ajantasainen käsittelytilanne voidaan esittää tapahtumien perusteella, mutta sitä ei saa muodostaa siten, että alkuperäinen määräajan ylitys katoaa tai että vastaanottajan tapahtuma esitetään tuottajan tuloksena. Myöhäisen toimituksen hyväksyminen ei jälkikäteen muuta määräaikaan liittynyttä havaintoa onnistumiseksi.

Ajon elinkaaren hallinnassa voidaan lisäksi käyttää tiloja jonossa, käynnissä, aikakatkaistu ja peruutettu. Jos tuottaja ei toimita tulosta määräaikaan mennessä, vastaanottava järjestelmä muodostaa ajotietueen `failed`-tilaisena ilman tuottajan toimitusta. Tämä vastaanottajan muodostama tietue ei väitä sisältävänsä tuottajan ilmoittamaa tulosta tai virhekuvausta: siihen kirjataan vain vastaanottajan todennettavissa oleva tieto, kuten määräajan umpeutuminen tai muu havaittu toimitus-/yhteysvirhe. Tuntemattomia syitä tai puuttuvia tuottajan metatietoja ei täydennetä arvauksilla.

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
- Valvomo erottaa tuottajan ilmoittaman tulostilan vastaanottajan muodostamasta ajon lopputilasta ja käsittelytapahtumista. Näkymä ilmaisee, mistä tiedot ovat peräisin; jos tuottajan toimitusta ei ole, tuottajan tulostila esitetään puuttuvana/tuntemattomana eikä vastaanottajan `failed`-merkintää näytetä tuottajan tuloksena.
- Myöhäisen toimituksen käsittely esitetään aikajärjestyksessä säilyvinä tapahtumina. Valvomo näyttää erikseen määräajan ylityksen, myöhäisen vastaanoton, validoinnin, hyväksynnän tai hylkäyksen sekä mahdollisen julkaisun. Myöhempi tapahtuma ei peitä aiempaa tapahtumaa eikä muuta sen merkitystä.
- Vastaanottajan muodostama ajotietue ilman tuottajan toimitusta näkyy ajohistoriassa normaalina ajona, jonka tuottajan tulos puuttuu ja jonka vastaanottajan todentama lopputila ja syy näytetään erikseen.
- Vanhentunutta tilaa ei esitetä ajantasaisena.
- Käynnissä-tila näytetään vain, jos ajosta on tuore ja todennettava käynnissä-merkintä.
- Osittainen lähdetarkistus ei muutu täydelliseksi vain siksi, että ajo tuotti raportin.
- Prosenttilukuja ei näytetä ilman luotettavaa nimittäjää.
- Historiatietoja ei korvata viimeisimmän ajon tilannekuvalla.
- Lähdekattavuus, raportin tila ja julkaisun tila näytetään ajon yhteydessä; erillisiä analytiikkanäkymiä ei vaadita ensimmäisessä versiossa.
- Valvomo tarjoaa lisäksi lähdekohtaisen tilastonäkymän tai vastaavan suodatettavan yhteenvedon, josta näkee lähteiden avausyritysten määrät, onnistumiset, epäonnistumiset, onnistumisasteen, viimeisimmät tulokset ja kehityksen tarkastelujaksolla.
- Tilastoissa erotetaan lähteen avaamisen onnistuminen siitä, löytyikö lähteestä käyttökelpoista tai raportoitavaa sisältöä. Avaamatta jääneitä lähteitä ei lasketa epäonnistuneiksi avausyrityksiksi.
- Valvomo voi nostaa toistuvasti epäonnistuvia lähteitä tarkistettaviksi ja näyttää tilastojen perusteella ehdotuksen lähteen käytöstä poistamisesta. Lähdettä ei poisteta tai poisteta käytöstä automaattisesti pelkän tilaston perusteella; tilapäiset häiriöt, käyttörajoitukset ja pienet otokset huomioidaan, ja käytöstä poistaminen tehdään lähderekisterin hallittuna muutoksena.

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
- **Myöhäinen tuottajatoimitus:** toimitus tunnistetaan alkuperäisellä `run_id`-tunnisteella. Se voidaan validoida ja julkaista alkuperäisen ajon tuloksena vain, jos samaa aihetta ja seurantatyyppiä koskevaa myöhempää ajoa ei ole käynnistetty ja kaikki normaalit hyväksymisehdot täyttyvät. Myöhäinen toimitus ei muuta myöhempien ajojen tietoja tai tiloja; määräajan umpeutuminen ja myöhäinen vastaanotto säilyvät erillisinä ajotapahtumina.

Ensimmäisessä versiossa ei vaadita monimutkaista uudelleenyritysten orkestrointia. Uudelleenyritysten määrä, laskentatapa, ajankohta ja muut käsittelyrajat määritellään konfiguraatiossa ja välitetään tehtävän `resolved_config`-kokoonpanossa; niitä ei kovakoodata. Toimintamalli ei saa jättää virheellistä aihetta toistuvasti jonon kärkeen.

Valvomo näyttää virheluokan, lyhyen selitteen, epäonnistuneen vaiheen ja sen, onko uusi yritys mahdollinen tai jo tehty.

### 10.1 Tallennuksen eheys ja palautuminen

RSS-julkaisut sekä vastaanottajan kanoniset ajotietueet ja ajon tapahtumahistoriat tallennetaan samaan instanssirepositorioon. Ne säilyvät erillisinä tiedostoina ja tietokokonaisuuksina: RSS-syöte sisältää julkaistut raportit, ajotietue ajon nykytilan ja käsittelyn yhteenvedon sekä tapahtumahistoria aikajärjestyksessä säilyvät käsittelytapahtumat. Tuottajan toimitusmetatiedot säilyvät omassa toimituspaketissaan. Yhteinen ohjelmistorepositorio pysyy tästä erillisenä.

Kun ajo julkaistaan, RSS-syötteen muutos, vastaavan kanonisen ajotietueen päivitys ja siihen liittyvät uudet tapahtumat sisällytetään samaan Git-commitiin. Näin ne tulevat näkyviin yhtenä atomisena repositoriomuutoksena: commit joko sisältää molemmat päivitykset tai ei kumpaakaan. Ajoa ei merkitä julkaistuksi ennen kuin commitin onnistuminen ja sen sisältö on varmennettu.

Jos tallennusyritys epäonnistuu ennen commitin syntymistä, kumpaakaan muutosta ei katsota julkaistuksi. Jos commit on syntynyt mutta työnkulku ei saanut onnistumisesta vahvistusta tai keskeytyi, seuraava käsittely tarkistaa instanssirepositorion todellisen tilan. Se etsii alkuperäisen `run_id`-ajon, toimitustunnisteen ja RSS-itemin GUIDin perusteella, vastaavatko ajotietue ja RSS-item samaa toimitusta. Varmennettu commit käsitellään onnistuneena, vaikka alkuperäinen työnkulku ei ehtinyt vahvistaa sitä. Uutta julkaisua ei tehdä vain siksi, että aiempi työnkulku keskeytyi.

Uudelleenyritys jatkaa samaa loogista ajoa samalla `run_id`- ja toimitustunnisteella. Yrityskohtainen tunniste ja yritystapahtumat erottavat käsittely-yritykset toisistaan, mutta uusi yritys ei muodosta uutta ajoa tai uutta GUIDia. Ennen jokaista kirjoitusta vastaanottaja tarkistaa, onko sama toimitus jo käsitelty ja onko sen RSS-item jo julkaistu. Täsmälleen saman toimituksen toistuva vastaanotto käsitellään idempotentisti ilman uutta ajotietuetta tai RSS-itemiä. Jos sama tunniste tai GUID liittyy ristiriitaiseen sisältöön, toimitus hylätään ja ristiriita kirjataan; aiempaa julkaistua itemiä ei korvata.

Tapahtumahistoria säilyy loogisesti vain lisäämiseen perustuvana. Uudelleenyritykset, tallennusyritykset, niiden varmennukset ja epäonnistumiset lisätään uusina tapahtumina. Aiemman yrityksen tapahtumia tai vastaanottajan havaintoja ei poisteta eikä ylikirjoiteta. Ajantasainen käsittelytila voidaan muodostaa tapahtumista, mutta se ei saa hävittää niiden alkuperäistä aikajärjestystä tai alkuperätietoa.

Jos ajotietue on jo kirjattu epäonnistuneeksi ja tehtävä vapautettu, myöhemmin saapuva toimitus käsitellään alkuperäisen `run_id`-tunnisteen perusteella rajattuna jälkikäsittelynä. Se voidaan validoida ja julkaista alkuperäisen ajon tuloksena vain, jos samaa aihetta ja tehtävätyyppiä koskevaa myöhempää ajoa ei ole käynnistetty ja kaikki normaalit hyväksymisehdot täyttyvät. Myöhäinen toimitus täydentää alkuperäistä ajotietuetta uusilla tapahtumilla; se ei poista aikakatkaisua tai muuta aiempaa havaintoa, avaa vapautettua tehtävää uudelleen eikä muuta myöhempien ajojen tietoja tai tiloja. Jos myöhempi ajo on jo käynnistetty, myöhäinen toimitus hylätään julkaisemisen osalta ja sen käsittely kirjataan.

Julkaistua RSS-itemiä ei koskaan muokata tai korvata palautumisen yhteydessä. Sisällöllinen korjaus tai täydennys julkaistaan uutena iteminä omalla GUIDilla ja viittauksella alkuperäiseen julkaisuun.

### 10.2 Toimitusten tunnistaminen ja ristiriitojen käsittely

Ajon, tuottajan toimituksen ja vastaanottajan yksittäisen käsittely-yrityksen tunnisteet ovat erillisiä, koska ne kuvaavat eri asioita ja niiden elinkaaret poikkeavat toisistaan.

- **`run_id`** yksilöi tehtäväpyynnön ja loogisen ajon. Vastaanottaja luo sen tehtäväpyyntöä muodostettaessa. Tunniste säilyy kaikissa saman ajon toimitus- ja käsittely-yrityksissä. Yhdellä `run_id`-tunnisteella on yksi kanoninen ajotietue ja enintään yksi hyväksytty varsinaisen raportin toimitus.
- **`delivery_id`** yksilöi raportintuottajan muodostaman toimituspaketin. Raportintuottaja luo tunnisteen ensimmäisen toimituksen yhteydessä. Saman toimituksen uudelleenlähetyksissä tunniste säilyy; uusi tunniste luodaan vain aidosti uudelle toimitukselle. Vastaanottaja käsittelee toimitusta `run_id`- ja `delivery_id`-tunnisteiden yhdistelmän perusteella.
- **`attempt_id`** yksilöi vastaanottajan käsittely-yrityksen. Vastaanottaja luo uuden UUID-tunnisteen jokaiselle uudelle käsittely- tai uudelleenyritysyritykselle. Tunniste yhdistetään kyseisen yrityksen `run_id`- ja `delivery_id`-tunnisteisiin. Raportintuottaja ei luo eikä määrää `attempt_id`-tunnistetta.
- **RSS `guid`** yksilöi julkaistun raportti-itemin. Alkuperäisen raportin GUID muodostetaan deterministisesti `run_id`-tunnisteesta, esimerkiksi muodossa `urn:aiheseurain:run:{run_id}`. Saman ajon uudelleenyritykset käyttävät samaa GUIDia. Myöhempi sisällöllinen korjaus tai täydennys julkaistaan uutena iteminä omalla GUIDilla ja viittauksella alkuperäiseen itemiin.

Vastaanottaja laskee toimituksen sisällöstä SHA-256-tiivisteen. Tiiviste lasketaan yhdenmukaisesti kanonisoidusta toimitussisällöstä, jotta sisällöltään saman toimituksen uudelleenlähetys voidaan erottaa saman tunnisteen yhteydessä muuttuneesta sisällöstä. Tiivisteen laskenta ja vertailu kuuluvat vastaanottajalle; tuottajan ilmoittamaa tiivistettä ei käytetä vastaanottajan varmennuksen korvikkeena.

Toimitusten käsittelyssä noudatetaan seuraavia sääntöjä:

1. Sama `delivery_id` ja sama kanonisoitu sisältö tarkoittavat saman toimituksen kaksoisvastaanottoa. Se käsitellään idempotentisti eikä synnytä uutta hyväksyttyä toimitusta tai RSS-itemiä.
2. Sama `delivery_id` mutta eri sisältö on tunnisteristiriita. Uusi sisältö hylätään ja ristiriita kirjataan; aiempaa toimitusta tai julkaisua ei korvata.
3. Eri `delivery_id` samalla `run_id`-tunnisteella ja sama sisältö tarkoittavat vaihtoehtoista toimitusta samalle tulokselle. Se voidaan kirjata kaksois-/vaihtoehtoisena toimituksena, mutta siitä ei synny toista julkaisua.
4. Eri `delivery_id` samalla `run_id`-tunnisteella mutta eri sisältö on ristiriita, jos kyseiselle ajolle on jo hyväksytty toimitus. Myöhempi eri sisältö hylätään eikä hyväksyttyä tulosta korvata.
5. Jos aiempi toimitus on hylätty validoinnissa eikä ajon käsittelyä ole vielä päätetty, toinen eri tunnisteella saapuva toimitus voidaan hyväksyä, jos se läpäisee kaikki normaalit hyväksymisehdot. Ajon päättämisen jälkeen uutta vaihtoehtoista varsinaista raporttitoimitusta ei hyväksytä.

Tunnisteiden vastuut pidetään erillään: `run_id` seuraa ajoa, `delivery_id` tuottajan toimitusta ja `attempt_id` vastaanottajan käsittely-yritystä. Tämä malli ei muuta ensimmäisen version sarjallista käsittelyä eikä edellytä rinnakkaisten tuottajien varaus- tai lukitusmekanismia.

## 11. Turvallisuus, eheys ja testaus

- Testit eivät saa kirjoittaa tuotannon RSS-syötteisiin tai muuttaa tuotannon seurantatilaa.
- Määritysten eheys tarkistetaan ennen ajoa. Virheellinen tai ristiriitainen määritys estää ajon.
- Koko instanssissa saa olla ensimmäisessä versiossa kerrallaan enintään yksi aktiivinen raportointitehtävä. Seuraava tehtävä käynnistetään vasta, kun edellinen on ratkaistu onnistuneesti tai kirjattu epäonnistuneeksi.
- Eri aiheiden rinnakkaista käsittelyä tai tehtävien varaus-, lukitus- tai kilpailutilanteiden hallintaa ei toteuteta ensimmäisessä versiossa.
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
33. Määräajan jälkeen saapuva tulos voidaan hyväksyä alkuperäiselle ajolle, jos myöhempää saman aiheen ja seurantatyypin ajoa ei ole käynnistetty; se ei saa vaikuttaa myöhempien ajojen tietoihin tai tiloihin.

## 16. Avoimet suunnittelukysymykset

Seuraavat tekniset yksityiskohdat ratkaistaan toteutussuunnittelussa. Ne eivät muuta tässä määriteltyä yksinkertaista toimintamallia.

1. **Ajotuloksen täsmällinen skeema:** kenttätyypit, pakollisuus, formaattirajoitteet ja esimerkkitulokset määritellään versioidussa skeemassa.
2. **Vastaanottorajapinnan toteutus:** tekninen siirtotapa ja tunnistautuminen valitaan turvallisten vaihtoehtojen perusteella.
3. **Ajojen käynnistäminen:** käynnistimien, ajastusten ja aihekohtaisten erääntymisten tekninen yhteensovitus ratkaistaan erikseen. Nykyisiä tehtäviä ei muuteta tämän määrittelyn perusteella.
4. **Jonon ja uudelleenyritysten tarkat rajat:** valinnan periaate on erääntyminen ja odotusaika. Aikakatkaisut ja uudelleenyritysten rajat täsmennetään toteutussuunnittelussa.
5. **Ajotietojen tietomallit:** tuottajan toimitusmetatietojen, vastaanottajan kanonisen ajotietueen ja append-only-tapahtumahistorian tarkat kentät, tapahtumatyypit ja keskinäiset viittaukset täsmennetään teknisessä suunnittelussa.
6. **Valvomon toteutus:** kolmen perusnäkymän tarkka käyttöliittymärakenne suunnitellaan myöhemmin.
7. **Historiatietojen säilytys:** ajon perustietojen, mahdollisten lokien ja väliaineistojen säilytysajat määritellään tietotarpeen ja tietosuojan perusteella.
8. **Nykyisen toteutuksen siirtymä:** nykyiset osat inventoidaan ja arvioidaan ennen hyödyntämistä tai poistamista. Mitään ei poisteta ilman erillistä suunnitelmaa.
9. **Mahdollinen myöhempi käyttöoikeuksien tekninen toteutus:** jos instanssin myöhempi käyttötarve edellyttää luottamuksellisen tiedon käsittelyä, julkisen ja rajatun tiedon erottelu sekä käyttöoikeudet suunnitellaan ennen tällaisen tiedon käyttöönottoa. Tämä ei kuulu ensimmäiseen versioon.
10. **Ohjelmiston ja instanssin toimitusmalli:** repositorioiden nimet, tarkka hakemistorakenne, jakelukanava, version kiinnittämisen mekanismi sekä ohjelmiston ja instanssin välinen tekninen tiedonsiirto määritellään toteutussuunnittelussa.
11. **Lähderekisterin ulkopuolinen lähdehaku:** saako raportintuottaja etsiä uutisoitavaa myös tehtäväpyynnössä ilmoittamattomista lähteistä, millä rajauksilla tällaisia lähteitä voi käyttää ja miten löydetyt lähteet dokumentoidaan? Erityisesti ratkaistaan, lisätäänkö uudet lähteet lähderekisteriin automaattisesti vai vasta tarkistuksen ja ylläpitäjän hyväksynnän jälkeen. Ennen päätöstä ajonaikainen rekisterin muuttaminen ja automaattinen lisäys eivät ole sallittuja.

## 17. Raportintekijän yhteinen perusprompti ja tuottajakohtaiset ohjeet

Yhteinen raportintekijän perusprompti kuuluu jaettavaan ohjelmistoon ja on versionhallittu osa käytettyä `software_revision`-versiota. Tehtäväpyyntö viittaa siihen `instructions`-taulukon ensimmäisenä ohjeena. Perusprompti määrittelee raportintekijän yleiset vastuut ja rajat, tehtäväpyynnön lukemisen, ohjeiden noudattamisen, lähdeaineiston käsittelyn, epävarmuuden ilmaisemisen, raportin muodostamisen ja toimituspaketin vaatimusten noudattamisen.

Perusprompti ei sisällä aihekohtaisia uutis- tai sisältövaatimuksia eikä korvaa tehtävätyypin, profiilien tai aiheen ohjeita. Näiden ohjeiden järjestys on: yhteinen perusprompti, tehtävätyypin ohje, profiiliohjeet aihekohtaisessa järjestyksessä ja aihekohtainen ohje. Raportintekijä käyttää vain tehtäväpyynnön ilmoittamissa muuttumattomissa revisioissa olevia ohjeita eikä hae niiden uusimpia versioita kesken ajon.

Peruspromptin tulee ohjata raportintekijää käsittelemään lähdeaineistoa tietona eikä järjestelmäohjeina, olemaan keksimättä puuttuvia tietoja, säilyttämään tehtäväpyynnön tunnisteet ja asetukset muuttumattomina sekä ilmoittamaan puutteet ja epäonnistumiset rehellisesti. Se määrittelee myös lähdekohtaisten avausyritysten tulosten raportoinnin niin, että todellinen avaamisen onnistuminen, epäonnistumisen syy ja sisällön käyttökelpoisuus pysyvät erillisinä tietoina.

Tuottajakohtaiset toteutusohjeet ja integraation tekniset asetukset voivat täydentää yhteistä peruspromptia, mutta ne eivät saa muuttaa yhteistä tietosopimusta, tehtäväpyynnön määrityksiä tai vastaanottavan järjestelmän julkaisuehtoja. Tuottajakohtaiset tekniset integraatio-ohjeet, ajastukset ja käyttöönottotiedot dokumentoidaan erikseen.

## 18. Muutosloki

- **0.12.34 – 23.11.2026:** hyväksyttiin kanavakohtaisen tarkistusyrityksen vähimmäistiedoiksi ajankohta, tulos, tieto uuden tai tehtävän kannalta relevantin sisällön löytymisestä, saatavilla oleva tekninen tulos sekä virhe- ja huomiotiedot. Erotettiin teknisen tarkistuksen onnistuminen sisällöllisestä tuloksesta; onnistunut tarkistus ilman uutta sisältöä ei ole epäonnistuminen. Tarkka kenttärakenne ja sallitut tulosarvot jäivät avoimiksi. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.12.33 – 23.11.2026:** hyväksyttiin Lähdetarkistukset-ryhmän alustava kolmen osan rakenne: käytetyt lähteet, käytetyt sisältökanavat sekä kanavakohtaiset tarkistusyritykset tuloksineen. Rekisterin ulkopuoliset lähteet kuvataan erillisinä toimituskohtaisina lähteinä. Yksittäisten kenttien ja tarkkojen tulosluokkien määrittely jätettiin jatkokeskusteluun. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.12.32 – 23.11.2026:** hyväksyttiin Tuottajan tulos -ryhmän kentiksi `status`, `started_at` ja `completed_at`. Määriteltiin tuottajan tulostilan sallitut arvot, aikaleimojen esitystapa ja se, ettei vastaanottaja päättele puuttuvasta toimituksesta tuottajan tulosta.\n- **0.12.31 – 23.11.2026:** hyväksyttiin toimitusmetatietojen Tehtävän kuvaus -ryhmän ainoaksi omaksi kentäksi `period`, jonka rakenne vastaa tehtäväpyynnön `from`- ja `to`-arvoja. `topic_id` ja `task_type` säilyvät vain Tunnisteet ja versiot -ryhmässä, eikä niitä kopioida toiseen ryhmään.\n- **0.12.30 – 23.11.2026:** hyväksyttiin tuottajan toimitusmetatietojen tunnisteet ja versiot -ryhmän kentät: `schema_version`, `run_id`, `delivery_id`, `topic_id`, `task_type`, `software_revision` ja `instance_revision`. Täsmennettiin tunnisteiden omistajuus sekä se, ettei vastaanottajan `attempt_id` kuulu tuottajan metatietoihin. Muut tietoryhmät ja niiden kentät jäivät avoimiksi. Toteutusta, skeemoja tai automaatioita ei muutettu.\n- **0.12.29 – 23.11.2026:** hyväksyttiin tuottajan toimitusmetatietojen kuusi sisällöllistä tietoryhmää: tunnisteet ja versiot, tehtävän kuvaus, tuottajan tulos, lähdetarkistukset, havainnot ja laadunvarmistus sekä valinnaiset tuottajan tiedot. Ryhmittely ei vielä lukitse yksittäisiä kenttiä tai niiden pakollisuutta. Vastaanottajan käsittelytilat rajattiin edelleen tuottajan metatietojen ulkopuolelle. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.12.28 – 23.11.2026:** hyväksyttiin tuottajan toimitusmetatietojen, vastaanottajan kanonisen ajotietueen ja vastaanottajan append-only-tapahtumahistorian erottaminen kolmeksi toisiinsa viitatuksi tietokokonaisuudeksi. Täsmennettiin, että tarkat kentät, tapahtumatyypit ja viittaukset ratkaistaan myöhemmässä teknisessä suunnittelussa. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.12.27 – 23.11.2026:** hyväksyttiin ajon, tuottajan toimituksen ja vastaanottajan käsittely-yrityksen erilliset tunnisteet (`run_id`, `delivery_id`, `attempt_id`), alkuperäisen RSS-GUIDin deterministinen muodostaminen `run_id`-tunnisteesta, vastaanottajan laskema SHA-256-tiiviste kanonisoidusta toimitussisällöstä sekä kaksois- ja ristiriitaisten toimitusten käsittelysäännöt. Määriteltiin myös, milloin validoinnissa hylätyn toimituksen voi korvata toisella toimituksella. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.12.26 – 23.11.2026:** hyväksyttiin RSS-julkaisun ja kanonisen ajotietueen tallentaminen samaan instanssirepositorioon ja niiden atominen päivitys yhdellä Git-commitilla. Määriteltiin varmennukseen perustuva palautuminen keskeytyneistä ja osittain onnistuneista tallennuksista, saman toimituksen idempotentti uudelleenkäsittely, yrityskohtaisten tapahtumien säilyttäminen, ristiriitaisten tunnisteiden hylkääminen sekä myöhäisen toimituksen rajattu jälkikäsittely. RSS-itemit ja ajotietueet pysyvät erillisinä tietokokonaisuuksina; toteutusta tai automaatioita ei muutettu.
- **0.12.25 – 23.11.2026:** hyväksyttiin yhteisen tarkistustyönkulun kiinteäksi tarkistusväliksi 15 minuuttia. Täsmennettiin, että väli koskee tehtäväjonon ja aktiivisen tehtävän määräajan tarkistamista eikä muuta aihe- ja tehtävätyyppikohtaisia suoritusvälejä. Kirjattiin GitHub Actionsin ajastusviiveitä ja mahdollisia käynnistymättä jäämisiä koskeva rajoitus. Nykyisiä automaatioita tai niiden ajastuksia ei muutettu.
- **0.12.23 – 23.11.2026:** hyväksyttiin rekisterin ulkopuolisten lähteiden käytön ja rekisteröinnin erilliset asetukset (`source_discovery` ja `source_registry_addition`), niiden yhdistäminen tehtävätyypin oletuksista profiilien kautta aihekohtaisiin asetuksiin, muuttumattoman `instance_revision`-snapshotin säilyttäminen, ajon jälkeinen ehdotusten käsittely, automaattisen rekisteröinnin validointi ja duplikaattien esto sekä uusien lähteiden `unassessed`-luotettavuusluokitus ja alkuperä-/löytämistietojen säilyttäminen. Skeemoja tai toteutusta ei luotu tässä suunnittelumuutoksessa.
- **0.12.22 – 23.11.2026:** hyväksyttiin yhteisen lähderekisterin ja sisältökanavien tarkempi tietosisältö, yksilölliset tunnisteet, teknisten saavutettavuustietojen lähde- ja kanavatasot, tehtävätyypin oletus- ja pakolliset lähde–kanava-parit sekä aihekohtaiset `inherit`-, `extend`- ja `replace`-toimintatavat, niiden järjestys- ja yhdistämissäännöt sekä validointiperiaatteet. Raportintuottajan mahdollisuus käyttää rekisterin ulkopuolisia lähteitä ja niiden automaattinen rekisteröinti jätettiin erikseen ratkaistavaksi. Skeemoja tai toteutusta ei luotu tässä suunnittelumuutoksessa.
- **0.12.21 – 23.11.2026:** hyväksyttiin JSON Schema Draft 2020-12 -skeemojen vastuut ja hakemistorakenteen periaatteet, yhteisten osaskeemojen käyttö, skeemojen ja toimitus-/ajotietosopimusten erottelu, skeemojen semanttinen versiointi, tuntemattomien kenttien hylkääminen, vaiheittainen rakenteellinen ja toiminnallinen validointi, virheiden raportointi, Markdown-ohjeiden erilliset tarkistukset sekä kiinnitetyn validointikirjaston ja kattavan skeematestauksen periaatteet. Skeematiedostoja tai validointitoteutusta ei vielä luotu.
- **0.12.20 – 23.11.2026:** hyväksyttiin teknisen saavutettavuuden tietojen jako lähde-, kanava- ja ajohistoriatasolle. Lähdetaso kuvaa julkaisijan tai verkkopalvelun yleisiä ominaisuuksia ja rajoitteita, kanavataso yksittäisen sisältövirran teknisiä ominaisuuksia, ja ajohistoria toteutuneita tarkistustuloksia. Pysyvää, nopeasti vanhenevaa saavutettavuusarvosanaa ei ylläpidetä.
- **0.12.19 – 23.11.2026:** hyväksyttiin lähteen valinnainen oletusaikavyöhyke ja sen määrityksen peruste sekä sisältökanavan mahdollisuus tarkentaa aikavyöhykettä. Sisällön oma aikaleima tai tapahtumapaikan aikavyöhyke on ensisijainen, kun se on luotettavasti tiedossa; epävarmoja aikavyöhykkeitä ei päätellä.
- **0.12.18 – 22.11.2026:** täsmennettiin, että yhteinen lähderekisteri tukee saman lähteen erillisiä sisältökanavia omine vakaine tunnisteineen ja osoitteineen. Kanavat liittyvät samaan lähteeseen, mutta ne voidaan valita ja arvioida tehtäväkohtaisesti erikseen.
- **0.12.17 – 22.11.2026:** hyväksyttiin yhteinen lähderekisteri sekä tehtävätyypin oletuslähteiden ja aiheen sekä tehtävätyypin yhdistelmäkohtaisten lähdemääritysten malli. Aihekohtainen määritys voi periä, täydentää tai korvata oletuslähdelistan; tehtävätyypin pakolliset lähteet säilyvät korvaamisesta huolimatta.

- **0.12.16 – 22.11.2026:** hyväksyttiin määritysten ja toimituksen JSON Schema Draft 2020-12 -skeemakokonaisuuden periaatteet, tehtävätyyppikohtaiset asetusskeemat, tehtävätyyppiin sidotut profiilit, Markdown-ohjeiden erillinen validointi sekä tehtäväpyynnön rakenteisten aineistojen `inputs`-viittaukset. Lähderekisterin aihekohtainen rajaus jätettiin erikseen keskusteltavaksi.

- **0.12.15 – 22.11.2026:** täsmennettiin yhteisen peruspromptin paikka tehtäväpyynnön ohjejärjestyksessä ja yhdenmukaistettiin lähdehavaintojen tietosisältö sekä Valvomon lähdetilastojen vaatimukset.

- **0.12.14 – 22.11.2026:** täsmennettiin tehtäväpyynnön yhteisen raportintekijän peruspromptin viittaus ja ohjeiden järjestys, seuranta-aikavälin puoliksi avoin tulkinta, lähdekohtaiset avausyritysten mittarit sekä Valvomon lähdetilastot ja hallittu käytöstä poistamisen arviointi.

- **0.12.13 – 22.11.2026:** kirjattiin tehtävätyypin, määritysprofiilien ja aihekohtaisten määritysten kolmitasoinen malli, niiden yhdistämisjärjestys, suojatut asetukset, skeemavalidointi, muuttumaton resolved_config-snapshot sekä virheellisten määritysten käsittely. Profiilien rekursiiviset riippuvuudet ja dynaamiset yhdistämismekanismit rajattiin pois.\n\n- **0.12.12 – 22.11.2026:** määriteltiin tuottajan tuloksen, vastaanottajan käsittelyn ja ajon lopputilan erottelu sekä aktiivisen tehtävän vapauttamisen ehdot. Uudelleenyritysten määrät ja muut vastaavat käsittelyrajat päätettiin konfiguroitaviksi; niitä ei kovakoodata.

- **0.12.11 – 22.11.2026:** hyväksytty tehtäväpyynnön ylätason tietorakenne ja kenttien määrittelyperiaatteet: pakollinen semanttinen schema_version, yksilöllinen run_id, ohjelmisto- ja instanssirevisiot, aikaväli ja määräajat, RSS-historian viittaus, järjestetyt profiili- ja ohjeviittaukset sekä valmiiksi ratkaistu resolved_config. Määrittelemättömät ylimääräiset kentät hylätään.

- **0.12.10 – 22.11.2026:** hyväksytty myöhäisen toimituksen käsittelyn esittäminen erillisinä, aikajärjestyksessä säilyvinä vastaanottajan tapahtumina. Määräajan ylitys, myöhäinen vastaanotto, validointi, hyväksyntä/hylkäys ja mahdollinen julkaisu säilyvät erillisinä tietoina; myöhempi tapahtuma ei korvaa aiempaa.

- **0.12.9 – 22.11.2026:** täsmennetty, että myöhäinen hyväksytty tuottajan toimitus täydentää jo muodostettua kanonista ajotietuetta erillisenä tuottajan tuloksena eikä korvaa vastaanottajan aiemmin kirjaamia määräajan ylityksen ja toimituksen puuttumisen havaintoja.

- **0.12.8 – 22.11.2026:** hyväksytty rajattu myöhäisten toimitusten jälkikäsittely: määräajan jälkeen saapunut tulos voidaan validoida ja julkaista alkuperäiselle `run_id`-ajolle, jos myöhempää saman aiheen ja seurantatyypin ajoa ei ole käynnistetty. Myöhäinen toimitus ei muuta myöhempien ajojen tietoja tai tiloja, ja määräajan umpeutuminen sekä myöhäinen vastaanotto kirjataan erillisinä tapahtumina.

- **0.12.7 – 22.11.2026:** täsmennetty, että tehtävän muodostus, määräajan valvonta ja toimituksen vastaanotto/käsittely koordinoidaan yhteisen instanssikohtaisen sarjallisuuden hallinnan kautta, vaikka rinnakkaisten raportointitehtävien varaus- ja lukitusmekanismia ei tarvita.

- **0.12.6 – 22.11.2026:** yhtenäistetty turvallisuus- ja eheysvaatimukset koko instanssin kattavaan sarjalliseen käsittelyyn sekä täsmennetty kaksoistoimitusten ja -julkaisujen eston periaate.
- **0.12.5 – 22.11.2026:** erotettu tuottajan toimittama tulos vastaanottajan ylläpitämästä ajotietueesta ja ajonhallintatiedoista. Valvomon on ilmaistava tietojen alkuperä ja näytettävä tuottajan tulos puuttuvana, jos toimitusta ei saatu.
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
