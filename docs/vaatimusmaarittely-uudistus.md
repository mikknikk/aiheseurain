# Aiheseuraimen vaatimusmäärittely – uudistettu tavoitetila

**Versio:** 0.12.69  
**Tila:** luonnos – yksinkertaistettu toimintamalli hyväksytty suunnittelun pohjaksi; ei toteutuslupa  
**Päiväys:** 25.11.2026  
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

Instanssin yleinen aikavyöhyke määritetään instanssin asetuksissa IANA-aikavyöhyketunnisteena (esimerkiksi `Europe/Helsinki`). Asetus välitetään tehtäväpyynnön `resolved_config.timezone`-kentässä, eikä tehtävätyyppikohtainen määritys, profiili tai aihekohtainen määritys voi ylikirjoittaa sitä. Asetusta käytetään paikallisen ajan tulkintaan, kuten raportointijaksojen ja aikataulujen rajoihin. Aikaleimat säilytetään yksiselitteisinä UTC-aikoina tai ISO 8601 -aikoina asianmukaisine UTC-offseteineen; RSS-itemin `<pubDate>` ilmoitetaan UTC-ajassa. Aikavyöhykettä ei päätellä suoritusympäristöstä tai käyttäjän sijainnista.

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

Ensimmäisessä versiossa instanssilla on yksi yhteinen lähderekisteri tiedostossa `data/sources/registry.json`. Rekisterin juurirakenne sisältää `schema_version`- ja `sources`-kentät. Yksi keskitetty rekisteritiedosto helpottaa lähde- ja kanavatunnisteiden yksilöllisyyden sekä viittausten eheyden tarkistamista. Hakemistorakenne ja tiedostopolut määritellään tavoitetilaa varten puhtaalta pöydältä; vanhan toteutuksen tiedostorakennetta ei käytetä lähtökohtana.

Lähdetietue sisältää vähintään kentät `id`, `name`, `publisher`, `source_type`, `description`, `homepage_url`, `languages`, `regions`, `reliability`, `reliability_notes`, valinnaiset `timezone` ja `timezone_basis`, `technical_access` sekä `channels`. Lähdetyypin sallitut arvot ovat `news_media`, `official_source`, `social_media`, `forum`, `blog`, `database`, `video_platform`, `event_listing` ja `other`. Toimituksellisen luotettavuuden arvot ovat `high`, `medium`, `low` ja `unassessed`; luokitus kuvaa lähteen arvioitua käyttökelpoisuutta eikä takaa yksittäisen julkaisun oikeellisuutta. Kielet ilmaistaan BCP 47 -tunnisteilla ja alueet ISO 3166-1 alpha-2 -maatunnisteilla tai arvolla `global`. Tyhjä kieli- tai aluelista tarkoittaa, ettei tietoa ole määritelty, ei sitä, että lähde kattaisi kaikki kielet tai alueet.

Jokainen lähde sisältää vähintään yhden sisältökanavan. Kanavatietue sisältää kentät `channel_id`, `name`, `url`, `channel_type`, `content_scope`, mahdolliset `languages`- ja `regions`-tarkennukset, valinnaiset `timezone` ja `timezone_basis` sekä kanavakohtaisen `technical_access`-kuvauksen. Kanavatyypin arvot ovat `website`, `rss`, `api`, `social_profile`, `video_channel`, `database_endpoint`, `event_calendar` ja `other`. Kanavan kielet ja alueet voivat tarkentaa lähteen vastaavia tietoja. Lähteen valinta ilman kanavatunnistetta ei tarkoita automaattisesti kaikkien kanavien valitsemista: käytettävät kanavat yksilöidään aina eksplisiittisesti.

Lähdetason tekninen saavutettavuus kuvaa julkaisijaa tai verkkopalvelua yleisesti. Sen tietoja voivat olla `access_model` ( `public`, `account_required`, `subscription_required`, `mixed` tai `unknown` ), `terms_url`, `api_documentation_url`, `usage_limit_notes` ja `notes`. Kanavatason tekninen saavutettavuus voi tarkentaa `access_model`-arvoa ja kuvata sisältömuotoa (`html`, `rss`, `atom`, `json`, `xml`, `pdf`, `video`, `mixed` tai `unknown`), JavaScript-riippuvuutta, sivutustapaa (`none`, `page_number`, `cursor`, `infinite_scroll` tai `unknown`) sekä kanavakohtaisia käyttörajoitteita ja huomioita. Nämä ovat rekisteriin tallennettavia yleisiä ominaisuuksia; yksittäisen ajon HTTP-tilat, vasteajat, avaus- ja lukemisvirheet sekä onnistumiset kuuluvat ajohistoriaan. Aikavyöhyke ja sen määrityksen peruste annetaan yhdessä aina, kun aikavyöhyke määritellään.

Lähteen `id` ja kanavan `channel_id` noudattavat tunnisteiden hyväksyttyä slug-syntaksia. Lähdetunniste on yksilöllinen koko rekisterissä ja kanavatunniste on globaalisti yksilöllinen lähteestä riippumatta. Tunniste säilyy, vaikka nimi tai osoite muuttuu; poistettua tunnistetta ei käytetä uudelleen. Kukin kanava kuuluu täsmälleen yhdelle lähteelle.

Tehtävätyypin määritys sisältää kaksi erillistä lähdeluetteloa: `default_sources` ja `required_sources`. Oletuslähteen käyttömerkintä yksilöi `source_id`-tunnisteen, `priority`-arvon, `roles`-roolit ja eksplisiittisesti valitut `channels`-kanavat. Tärkeys on kokonaisluku 1–5, jossa 1 on tärkein; jos uuden lähteen tärkeyttä ei anneta, käytetään arvoa 3. Roolit ovat `primary`, `discovery`, `verification`, `official_confirmation` ja `context`. Kanavakohtaiset käyttöasetukset voivat tarkentaa lähdemerkinnän tärkeyttä ja rooleja sekä sisältää kanavakohtaisia seurantahuomioita. Kanavakohtainen arvo korvaa vastaavan lähdetason käyttöarvon. Roolitaulukko korvataan kokonaan, sitä ei yhdistetä automaattisesti. Rekisterin pysyviä perustietoja tai teknisiä ominaisuuksia ei voi muuttaa lähdevalinnan käyttöasetuksilla.

Pakollinen lähde määritellään täsmällisenä `source_id`- ja `channel_id`-parina. Pakollisen parin on sisällyttävä tehtävätyypin oletuslähteisiin. Näin pakollisuus kohdistuu yksiselitteiseen sisältökanavaan eikä epämääräisesti kaikkiin saman julkaisijan kanaviin.

Aihekohtainen määritys valitsee lähteet aina aiheen ja tehtävätyypin yhdistelmälle. Sen `source_selection`-objektissa on `mode` ja `entries`; jos objekti puuttuu, oletuksena käytetään `extend`-toimintatapaa ilman aihekohtaisia muutoksia. `inherit` käyttää tehtävätyypin oletuslähteitä sellaisinaan eikä salli `entries`-merkintöjä. `extend` säilyttää oletuslähteet ja sallii uusien lähteiden lisäämisen sekä käyttöasetusten tarkentamisen; oletuslähteitä ei voi poistaa. `replace` korvaa valinnaiset oletuslähteet aihekohtaisella listalla, mutta tehtävätyypin pakolliset lähteet säilyvät aina. Jos pakollinen pari puuttuu korvaavasta listasta, se lisätään alkuperäisine oletusasetuksineen; jos se on mukana, sen asetuksia voidaan tarkentaa mutta sitä ei voi poistaa. `extend` on oletustoimintatapa.

Lopullisen lähdelistan järjestys on deterministinen. `inherit`-tilassa säilyy oletuslistan järjestys. `extend`-tilassa oletusjärjestys säilyy ja uudet merkinnät lisätään aihekohtaisessa järjestyksessä. `replace`-tilassa aihekohtainen järjestys säilyy ja puuttuvat pakolliset parit lisätään `required_sources`-listan järjestyksessä. Tärkeysarvo on erillinen listajärjestyksestä. Sama lähde–kanava-pari saa esiintyä lopullisessa listassa vain kerran; päällekkäisyyksiä ei ratkaista automaattisella arvailulla.

Lähdeviittaukset validoidaan samaa tehtäväpyyntöä varten kiinnitetyn `instance_revision`-revision lähderekisteriä vasten. Validoinnissa tarkistetaan lähde- ja kanavatunnisteiden yksilöllisyys, vähintään yksi kanava lähdettä kohden, kanavan kuuluminen ilmoitettuun lähteeseen, URL-osoitteiden absoluuttinen HTTP/HTTPS-muoto, aikavyöhykkeen ja määritysperusteen parillisuus, kieli-, alue- ja luokitteluarvojen kelvollisuus, kaikkien viittausten löytyminen, pakollisten parien olemassaolo sekä lähde–kanava-parien yksikäsitteisyys. Lisäksi tarkistetaan, että `inherit` ei sisällä aihekohtaisia merkintöjä, `extend` ei poista oletuksia ja `replace` säilyttää pakolliset lähteet. Puuttuvaa lähdettä tai kanavaa ei korvata automaattisesti toisella.

Raportintuottaja voi etsiä uutisoitavaa myös tehtäväpyynnön lähderekisterin ulkopuolisista lähteistä, jos tehtävätyypin asetukset ja aihekohtaiset ylikirjoitukset sallivat sen. Lähteiden etsiminen ja niiden pysyvä rekisteröinti ovat toisistaan riippumattomia asetuksia, jotka ratkaistaan samalla hyväksytyllä yhdistämisjärjestyksellä kuin muut tehtäväasetukset. `source_discovery.mode` määrittää lähdehaun: `disabled` sallii vain rekisteriin kuuluvien lähteiden käytön, kun taas `use_unregistered` sallii raportintuottajan etsiä ja käyttää myös rekisterin ulkopuolisia lähteitä kyseisessä ajossa. `source_registry_addition.mode` määrittää löydettyjen lähteiden pysyvän käsittelyn: `disabled` ei tallenna niitä rekisteriin, `propose` muodostaa ylläpitäjän tarkistettavan lähde-ehdotuksen ja `automatic` lisää lähteen rekisteriin automaattisesti vasta ehdotuksen validoinnin ja duplikaattitarkistuksen jälkeen. Asetukset eivät korvaa toisiaan: jos `source_discovery.mode` on `disabled`, tämän mekanismin kautta ei löydy uusia lähteitä, eikä rekisteröintiasetus yksin käynnistä lähdehakua.

Tehtäväpyynnön `instance_revision` yksilöi ajossa käytettävän muuttumattoman lähderekisterin. Raportintuottaja ei saa muuttaa tätä rekisteriä eikä ajon syötteitä kesken suorituksen. Rekisterin ulkopuolinen lähde voidaan käyttää kyseisessä ajossa, jos lähdehaku on sallittu; sen tiedot ja rekisteröintiehdotus toimitetaan erillään käytetyn rekisterin snapshotista. Ehdotukset käsitellään vasta ajon päätyttyä. `disabled`-tilassa ehdotusta ei tallenneta pysyvästi, `propose`-tilassa se asetetaan ylläpitäjän hyväksyttäväksi ja `automatic`-tilassa se lisätään rekisteriin vasta validoinnin jälkeen hallitussa rekisteripäivityksessä. Uusi rekisteriversio vaikuttaa vasta seuraaviin tehtäväpyyntöihin, ei jo käynnissä olevaan ajoon.

Ennen rekisteriin lisäämistä uuden lähteen perustiedot ja vähintään yksi sisältökanava validoidaan. Lisäksi tarkistetaan, ettei lähde tai kanava ole jo rekisterissä: vertailussa hyödynnetään vähintään julkaisijaa, kanavan ja kotisivun URL-osoitteita sekä muita käytettävissä olevia lähdetietoja, jotta samaa lähdettä ei lisätä rinnakkaisina tietueina. Jos vastaava lähde tai kanava löytyy, ehdotus yhdistetään olemassa olevaan tietueeseen hallitusti eikä luoda duplikaattia. Automaattisesti lisätyn lähteen `reliability` on `unassessed`, ellei sen toimituksellista luotettavuutta ole erikseen arvioitu. Lähteen alkuperä ja löytämisajankohta säilytetään jäljitettävyyttä varten. Rekisteröinti ei itsessään tarkoita lähteen luotettavaksi hyväksymistä. Rekisterin ulkopuoliset lähteet ja niiden käytön perusteet on voitava erottaa rekisteriin kuuluvista lähteistä ajon raportoinnissa ja jälkikäteisessä tarkastelussa.

Rekisterin ulkopuolisesta lähteestä muodostettava ehdotus on lähdekohtainen kokonaisuus, joka sisältää pysyvän `proposal_id`, lähteen perustiedot, vähintään yhden sisältökanavan, mahdolliset kieli- ja aluetiedot, alustavan luotettavuusluokituksen, löytämisajankohdan ja -alkuperän, ehdotuksen perustelun sekä viittauksen sitä tuottaneeseen `run_id`-ajoon. Ehdotuksen lähde- ja kanavatiedot noudattavat lähderekisterin vastaavia tietomalliperiaatteita. Puuttuvia tai varmentamattomia tietoja ei täydennetä arvauksilla; arvioimattoman lähteen luokitus on `unassessed`.

Ehdotukset tallennetaan erillisinä tiedostoina hakemistoon `data/source-proposals/{proposal_id}.json`, eivätkä ne kuulu lähderekisteriin ennen hyväksyntää. Ehdotuksen tilat ovat `pending`, `approved`, `rejected` ja `merged`. Vastaanottaja validoi ehdotuksen rakenteen, lähde- ja kanavatiedot sekä duplikaatit ennen ylläpitäjän käsittelyä. Ylläpitäjä voi hyväksyä ehdotuksen, hylätä sen tai yhdistää sen olemassa olevaan lähteeseen. Käsittelyajankohta ja perustelu säilytetään. Hyväksytty lähde lisätään rekisteriin hallitulla muutoksella; muutos vaikuttaa vain myöhemmin muodostettaviin tehtäväpyyntöihin. Ensimmäisessä versiossa ehdotukset tarkistetaan ja käsitellään GitHubissa tiedostoina; erillistä käyttöliittymää ei edellytetä. `propose` on ensimmäisen version suositeltu oletustila. `automatic`-tila säilyy mahdollisena erikseen määritettynä toimintatapana, mutta se ei ohita validointia tai duplikaattitarkistusta.

Markdown-ohjeita ei validoida JSON Scheman avulla. Niiden tarkistuksiin kuuluvat yksilöllinen ohjetunniste, tiedoston olemassaolo oikeassa repositoriossa ja kiinnitetyssä commitissa, repositoriojuureen suhteutettu turvallinen polku, ohjeiden oikea järjestys ja duplikaattien puuttuminen. Ohjeiden sisällön tulee olla ristiriidaton koneellisten määritysten kanssa. Ohjeiden metatietoa ei kahdenneta Markdown-etusivulla, vaan se pidetään JSON-määrityksissä ja tehtäväpyynnön viittauksissa.

#### Skeemakokonaisuuden rakenne ja validointiperiaatteet

Skeemahakemisto jaetaan neljään tietomallien vastuualueeseen yhteisten osaskeemojen lisäksi:

```text
schemas/
  common/
  configuration/
  task/
  delivery/
  receiver/
```

`common/` sisältää uudelleenkäytettävät osaskeemat. `configuration/` sisältää tehtävätyyppien, asetusten, profiilien, aihekohtaisten määritysten ja lähderekisterin skeemat. `task/` sisältää tehtäväpyynnön ja sen rakenteisten syötteiden skeemat. `delivery/` sisältää tuottajan toimitusmetatietojen, toimituspaketin, raportoitavien havaintojen, lähdetarkistusten ja laaduntarkistusten tulosten skeemat. `receiver/` sisältää vastaanottajan kanonisen ajotietueen ja tapahtumahistorian skeemat. Jokaisella itsenäisesti validoitavalla tietotyypillä on oma pääskeemansa; yhteiset kenttärakenteet toteutetaan paikallisilla `$ref`-viittauksilla.

Objektien sallitut kentät määritellään eksplisiittisesti ja tuntemattomat kentät hylätään myös sisäkkäisissä rakenteissa. Taulukoille määritellään `minItems`- ja `maxItems`-rajat silloin, kun tietomallin tarkoitus asettaa sellaisen rajan. Tunnisteiden yksilöllisyys, viittausten eheys ja muut usean tietueen väliset ehdot tarkistetaan rakenteellisen skeemavalidoinnin jälkeen toiminnallisessa validoinnissa. Skeemojen `description`-kuvausten tulee auttaa ylläpitäjää ymmärtämään kenttien tarkoitus ja rajoitteet. Validointivirheestä raportoidaan tiedosto, virheellisen arvon polku ja virheen syy; korjausehdotus annetaan, kun se voidaan muodostaa luotettavasti. Skeemat määritellään ja viimeistellään tietomalli kerrallaan, ei yhtenä suurena yleisskeemana.

JSON Schema Draft 2020-12 on kaikkien rakenteisten määritysten ja tietosopimusten rakenteellisen validoinnin standardi. Skeemat kuuluvat yhteiseen ohjelmistorepoon; instanssirepoon kuuluvat niiden avulla validoitavat varsinaiset määritykset ja aineistot. Jokaisella itsenäisellä tietotyypillä on oma pääskeemansa. Yhteisiä rakenteita varten käytetään uudelleenkäytettäviä osaskeemoja, esimerkiksi tunnisteille, Git-revisioille, aikaleimoille, tiedostoviittauksille, lähde- ja kanavaviittauksille sekä virhekuvauksille.

Skeemakokonaisuuden alustava hakemistorakenne on:

```text
schemas/
  common/
    ...
  configuration/
    ...
  task/
    ...
  delivery/
    ...
  receiver/
    ...
```

Hakemistojako on hyväksytty; yksittäisten skeematiedostojen nimet ja tarkka sisältö määritellään tietomalli kerrallaan. `configuration/` sisältää tehtävätyypin, asetusten, profiilien, aiheen ja lähderekisterin skeemat; `task/` tehtäväpyynnön ja sen rakenteisten syötteiden skeemat; `delivery/` toimitusmetatietojen, toimituspaketin, havaintojen, lähdetarkistusten ja laaduntarkistusten tulosten skeemat; `receiver/` vastaanottajan ajotietueen ja tapahtumahistorian skeemat. Tiedostonimet ovat englanninkielisiä, pienaakkosin ja yhdysmerkein, ja skeematiedostojen pääte on `.schema.json`. Skeemoilla on vakaat `$id`-tunnisteet, jotka eivät riipu repositorion nimestä tai tiedostopolusta. Ajon aikainen validointi ei hae skeemoja ulkoisista verkkopalveluista, vaan käyttää ohjelmistorevision mukana toimitettua skeemakokonaisuutta.

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

Tapahtumahistoria sisältää esimerkiksi ajon käynnistymisen, määräajan ylittymisen, toimituksen vastaanoton, validoinnin, hyväksynnän tai hylkäyksen, julkaisun sekä uudelleenyritysten ja myöhäisten toimitusten käsittelyn. `run.json` on vastaanottajan ylläpitämä nykytilan yhteenveto. Sen tietoryhmät ovat ajon tunnisteet (`run_id`, `topic_id`, `task_type`), käytetyt ohjelmisto- ja instanssirevisiot, tehtävän ajankohdat ja `period`, vastaanottajan nykyinen käsittely- ja lopputila, hyväksyttyyn toimitukseen ja metadataan viittaaminen, viimeisin validointitulos virheineen, julkaisun tila ja RSS-itemin viittaus sekä tietueen luonti- ja viimeisin varmennettu päivitysaikaleima. Tuottajan metatietoja ei kopioida `run.json`-tiedostoon. Tuottajan `status` ja vastaanottajan ajon tila pysyvät erillisinä; tuottajan `success` ei yksin tarkoita vastaanoton tai julkaisun onnistumista, eikä puuttuvasta toimituksesta päätellä tuottajan tilaa.

`events.jsonl` sisältää yhden JSON-tapahtuman kullakin rivillä. Tapahtuman yhteiset kentät ovat `event_id`, `run_id`, `sequence`, `event_type`, `occurred_at`, `actor` ja `details`. Esimerkkejä tapahtumatyypeistä ovat `run_created`, `task_issued`, `deadline_exceeded`, `delivery_received`, `delivery_validation_started`, `delivery_accepted`, `delivery_rejected`, `publication_started`, `publication_completed`, `run_completed` ja `run_failed`. Kunkin tapahtumatyypin `details`-kentän sallitut tiedot määritellään tapahtumatyypin mukaan.

Tapahtumahistoriaan lisätään vain uusia rivejä; aiempia tapahtumia ei muuteta eikä poisteta. `sequence` on yhden ajon sisällä yksilöllinen ja kasvava, ja `event_id` on yksilöllinen. Aikaleimat noudattavat yhteistä ISO 8601 - ja UTC-offset-mallia. Tapahtuma kuvaa vain todennettua tapahtumaa, ei oletusta. `run.json` muodostetaan tapahtumahistorian ja hyväksyttyjen toimitustietojen perusteella.

Tunnisteiden merkitykset pidetään erillään: `run_id` yksilöi loogisen ajon, `delivery_id` tuottajan toimituksen, `attempt_id` vastaanottajan käsittely-yrityksen ja `event_id` yksittäisen tapahtuman. Tapahtumat viittaavat aina `run_id`-tunnisteeseen; toimitukseen liittyvä tapahtuma voi lisäksi viitata `delivery_id`-tunnisteeseen ja käsittely-yritykseen liittyvä tapahtuma `attempt_id`-tunnisteeseen. Tunnisteita ei käytetä ristiin eikä muodosteta uudelleen saman kohteen uudelleenyrityksissä. Tapahtumien tarkat tyypit, kenttien yksityiskohtaiset rajat ja tietokokonaisuuksien viittauspolut täsmennetään skeematyössä.

Tuottajan toimitusmetatietojen sisältö jäsennetään seuraaviin tietoryhmiin:

- **Tunnisteet ja versiot:** ajon ja toimituksen tunnisteet, tietosopimuksen versio sekä käytetyn ohjelmiston ja instanssin revisiot.
- **Tehtävän kuvaus:** aihe, tehtävätyyppi ja seuranta-aikaväli.
- **Tuottajan tulos:** tuottajan ilmoittama tulostila ja raportin tuottamiseen liittyvät tiedot.
- **Lähdetarkistukset:** käytetyt lähteet ja sisältökanavat, tarkistusyritykset sekä niiden tulokset.

Lähdetarkistusten tietoryhmä jäsentyy kolmeen osaan: (1) ajossa käytetyt lähteet, (2) niistä eksplisiittisesti valitut ja käytetyt sisältökanavat sekä (3) kanavakohtaiset tarkistusyritykset tuloksineen. Myös rekisterin ulkopuoliset lähteet voidaan kuvata tässä ryhmässä erillisinä toimituskohtaisina lähteinä; niitä ei esitetä rekisteriin kuuluvina. Tarkat kentät, tarkistusyrityksen tulosluokat ja yksityiskohtainen tietosisältö täsmennetään erikseen. Ryhmittely ei muuta lähderekisterin pysyvien perustietojen ja ajohistorian toteutuneiden tarkistustulosten vastuunjakoa.

Tarkistusyrityksestä tallennetaan vähintään tarkistusajankohta, tarkistuksen tulos, tieto siitä löytyikö uutta tai tehtävän kannalta relevanttia sisältöä, saatavilla oleva tekninen tulos (esimerkiksi HTTP-tilakoodi) sekä mahdolliset virhe- ja huomiotiedot. Teknisen tarkistuksen onnistuminen erotetaan sisällöllisestä tuloksesta: onnistunut tarkistus ilman uutta sisältöä ei ole epäonnistuminen. Tietoryhmän tarkka kenttärakenne ja sallitut tulosarvot täsmennetään myöhemmin.
- **Havainnot ja laadunvarmistus:** raportoitavien havaintojen yhteenveto ja laaduntarkistuksen tulokset.
- **Tuottajan tiedot:** valinnaiset tiedot käytetystä raportintuottajasta.

Tuottajan tiedot -ryhmän ehdotettu rakenne on:

```json
{
  "producer": {
    "producer_id": "example-producer",
    "producer_type": "ai",
    "name": "Esimerkkituottaja",
    "version": "1.2.0"
  }
}
```

`producer`-ryhmä on valinnainen, ellei tehtävätyyppi sitä erikseen vaadi. Jos ryhmä toimitetaan, `producer_type` on pakollinen ja sen arvo on `human`, `ai`, `software` tai `other`. `producer_id`, `name` ja `version` ovat valinnaisia. Tunniste on pysyvä tuottajan tunniste, nimi ihmiselle luettava kuvaus ja versio käytetyn ohjelmiston tai mallin versiotieto. Ryhmään ei sisällytetä salasanoja, käyttöoikeustunnuksia, henkilötietoja tai muita salaisuuksia.

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

Viidenteen tietoryhmään, **Havainnot ja laadunvarmistus**, kuuluu kaksi osaa:

1. **Raportoitavat havainnot:** raportin sisältämien havaintojen yhteenveto. Siihen voi kuulua havaintojen lukumäärä ja tehtävätyypin kannalta tarpeellinen luokittelu tai ryhmittely sekä olennaisten rajausten, epävarmuuksien ja kattavuuspuutteiden kuvaus. Jos raportoitavia havaintoja ei löytynyt, tämä voidaan ilmaista yhteenvetona. Varsinaista raporttitekstiä tai lähdetarkistusten tietoja ei kopioida metatietoihin.
2. **Laadunvarmistus:** raportintuottajan tekemien laaduntarkistusten tulokset. Tarkistukset voivat koskea esimerkiksi lähdeviitteiden ja väitteiden vastaavuutta, havaintojen jäljitettävyyttä, ristiriitaisten tietojen käsittelyä, epävarmuuden ilmaisemista, duplikaattien hallintaa, seuranta-aikavälin noudattamista sekä raportin rakennetta ja luettavuutta. Metatiedoissa kuvataan tehdyt tarkistukset ja niiden tulokset sekä mahdolliset havaitut puutteet tai tekemättä jääneet pakolliset tarkistukset.

Tehtävätyypin määritys määrittelee, mitä laaduntarkistuksia kyseisessä tehtävässä edellytetään. Tehtävätyypistä riippumattomia pakollisia tarkistuksia ei oleteta. Jokaisesta vaaditusta tarkistuksesta tallennetaan toimitusmetatietoihin oma ajokohtainen tietue. Valinnaisesta tarkistuksesta tallennetaan tietue, jos se suoritetaan. Tarkistuksen nimi ja kuvaus säilyvät tehtävätyypin määrityksessä; toimitustietue viittaa siihen pysyvällä `check_id`-tunnisteella eikä kopioi nimeä tai kuvausta.

Laaduntarkistuksen määrittelytietue sisältää aina kentät `check_id`, `name`, `description`, `required` ja `parameters`. `parameters` on aina objekti; jos tarkistus ei tarvitse asetuksia, sen arvo on tyhjä objekti (`{}`). Parametrien sallittuja JSON-tietotyyppejä ovat merkkijono, numero, kokonaisluku, totuusarvo, taulukko ja objekti. Tarkistuskohtainen skeema määrittelee käytettävät parametrit, niiden tarkat tietotyypit, rajat, sallitut arvot ja mahdollisen pakollisuuden. Tuntemattomat parametrit hylätään.

Parametrien oletusarvot määritellään tarkistuskohtaisessa skeemassa. Määritysten käsittely soveltaa skeemassa määriteltyä oletusarvoa, kun parametria ei ole annettu ja oletusarvo on olemassa; JSON Schema -skeeman kuvaileva `default`-arvo ei yksinään muuta aineistoa automaattisesti. Oletusarvon käyttäminen ei muodosta erillistä ajokohtaista tarkistustulosta. Parametrien tarkat nimet ja rakenteet ovat tarkistuskohtaisia, eivät yleisen tietomallin kiinteä luettelo.

`check_id` on yksilöllinen saman tehtävätyypin tarkistusmäärittelyjen kesken. Sama tunniste voi esiintyä eri tehtävätyypeissä, jos se tarkoittaa samaa käsitteellistä tarkistusta. Tunniste ei riipu nimestä, kuvauksesta, parametreista tai teknisestä toteutuksesta. Pelkkä nimen, kuvauksen tai parametrien yhteensopiva täsmennys ei edellytä tunnisteen vaihtamista; jos tarkistuksen käsitteellinen tarkoitus muuttuu olennaisesti, sille luodaan uusi tunniste. Poistettua tunnistetta ei käytetä uudelleen.

Tarkistuksella ei ole erillistä versionumerokenttää. Käytetty tarkistusmäärittely yksilöityy tehtävätyypin määrityksen kautta, ja sen sisältö voidaan jäljittää tehtäväpyynnön `instance_revision`-revisiosta. `required: true` tarkoittaa, että toimituksessa on oltava kyseisen tarkistuksen ajokohtainen tulostietue. `required: false` tarkoittaa, että tarkistuksen voi jättää suorittamatta ja tällöin tulostietue voidaan jättää pois; jos valinnainen tarkistus suoritetaan, sen tulos kirjataan samalla tulostietuerakenteella. Pakollinen tarkistus voi saada tuloksen `not_applicable`, kun soveltumattomuus perustellaan. Pakollisen tarkistuksen puuttuva tulostietue on toimituksen validointivirhe.

Tarkistusten määrittely, parametrien ratkaiseminen, tarkistusten suorittaminen, tulosten kirjaaminen ja vastaanottajan validointi ovat erillisiä vastuita. Tehtävätyypin määritys ja tarkistuskohtainen skeema määrittelevät vaatimukset; raportintuottaja ratkaisee parametrit, suorittaa soveltuvat tarkistukset ja ilmoittaa ajokohtaiset tulokset; vastaanottaja tarkistaa tietueiden kattavuuden ja rakenteen muuttamatta tuottajan tuloksia. Tarkistusten suoritusjärjestystä tai keskinäisiä riippuvuuksia ei määritellä ensimmäisessä vaiheessa.

Yksittäisen tarkistustietueen kentät ovat:

- `check_id`: tehtävätyypin määrityksessä määritellyn tarkistuksen pysyvä tunniste.
- `result`: tarkistuksen ajokohtainen tulos.
- `checked_at`: ajankohta, jolloin tarkistus suoritettiin tai sen suorittamatta jättäminen todettiin.
- `findings`: tarkistuksessa havaitut yksittäiset ongelmat tai puutteet taulukkona. Onnistuneessa tarkistuksessa taulukko on tyhjä.
- `notes`: valinnaiset muut olennaiset huomiot.
- `reason`: perustelu tilanteessa, jossa tarkistusta ei suoritettu, se ei soveltunut tai sen suoritus epäonnistui.

Sallitut `result`-arvot ovat:

- `passed`: tarkistus suoritettiin eikä ongelmia havaittu.
- `issues_found`: tarkistus suoritettiin ja siinä havaittiin ongelmia tai puutteita.
- `not_run`: tarkistusta ei suoritettu.
- `not_applicable`: tarkistus ei soveltunut kyseiseen raporttiin tai ajoon.
- `execution_error`: tarkistuksen suoritus aloitettiin mutta se ei valmistunut teknisen tai muun suoritusvirheen vuoksi.

`not_run` ja `not_applicable` ilmaisevat eri tilanteita. `execution_error` kuvaa tarkistuksen suoritusongelmaa eikä itsessään raportin laatupuutetta. Tulosarvo `passed` edellyttää tyhjää `findings`-taulukkoa; `issues_found` edellyttää vähintään yhtä havaintoa. `not_run`-, `not_applicable`- ja `execution_error`-tilanteissa `reason` kertoo tilanteen perustelun. `checked_at` kirjataan aina, myös silloin kun todetaan, ettei tarkistusta suoritettu tai ettei se soveltunut.

Jokainen `findings`-taulukon havainto sisältää kentät `description` ja `severity` sekä valinnaisen `location`-kentän. Kuvaus kertoo, mitä havaittiin ja miksi se on ongelma. Vakavuusluokat ovat `critical` (keskeistä luotettavuutta tai käyttökelpoisuutta vaarantava), `major` (merkittävästi sisältöön tai oikeellisuuteen vaikuttava), `minor` (rajallinen ja vähäinen vaikutus) ja `info` (hyödyllinen huomio, joka ei ole varsinainen virhe). Sijainti voi yksilöidä esimerkiksi raportin otsikon, kappaleen tai lähdeviitteen.

Tarkistustietue kuvaa vain ajon lopullisen tuloksen. Jos tarkistusta yritetään useita kertoja, toimitusmetatietoihin tallennetaan lopullinen ajokohtainen tulos eikä kaikkia sisäisiä yrityksiä; olennaiset uusintayritykset voidaan kuvata `notes`-kentässä. Jokaisesta tehtävätyypin määrityksessä vaaditusta tarkistuksesta on toimituksessa oma tietue. Tekemättä jäänyt tarkistus kirjataan arvolla `not_run` perusteluineen ja soveltumaton tarkistus arvolla `not_applicable` perusteluineen. Puuttuvaa tietuetta ei tulkita onnistumiseksi.

Vastuut jakautuvat seuraavasti: tehtävätyypin määritys määrittelee vaaditut tarkistukset ja niiden merkityksen; raportintuottaja suorittaa tarkistukset ja ilmoittaa tulokset; toimitusmetatiedot sisältävät ajokohtaiset tulokset ja havainnot; vastaanottaja tarkistaa, että kaikki vaaditut tarkistustietueet on toimitettu ja että niiden rakenne on kelvollinen. Vastaanottaja voi verrata toimitettuja tietueita tehtävätyypin määrityksen vaadittuihin tarkistuksiin, havaita puuttuvat tietueet ja hylätä rakenteellisesti virheellisen toimituksen, mutta se ei muuta tuottajan ilmoittamia tuloksia eikä päättele puuttuvasta tuloksesta onnistumista. Tuottajan laadunvarmistus ei korvaa vastaanottajan toimituspaketin validointia.

Tuottajan tulostila (`status`) kuuluu kolmanteen tietoryhmään eikä sitä toisteta tässä ryhmässä. Laadunvarmistuksen tulos on siitä erillinen: onnistuneesti tuotetussa raportissa voi olla laaduntarkistuksessa havaittuja puutteita, ja osittainen raportti voi läpäistä kaikki sille soveltuvat tarkistukset.

Tämä ryhmittely määrittelee toimitusmetatietojen kuusi sisällöllistä vastuualueetta. Raportoitavien havaintojen tietomalli, toimituspaketin tiedostoroolit ja tiedostoluettelo, tulostilakohtaiset tiedostovaatimukset sekä vastaanottajan validointivaiheet on täsmennetty seuraavissa alaluvuissa. Vastaanottajan vastaanotto-, validointi-, julkaisu- ja käsittelytilat eivät kuulu tuottajan metatietoihin vaan vastaanottajan ajotietueeseen ja tapahtumahistoriaan.

#### Raportoitavien havaintojen tietomalli

Raportoitavat havainnot ja laaduntarkistusten havainnot ovat erillisiä tietokokonaisuuksia. Raportoitava havainto kuvaa seurannan tulosta; laaduntarkistuksen havainto kuvaa raportintuottajan tekemässä tarkistuksessa havaittua laatupuutetta.

Raportoitavan havainnon tietue sisältää kentät `finding_id`, `title`, `description`, `category`, `source_refs`, `occurred_at` ja `notes`. Yleisesti pakollisia ovat `finding_id`, `title` ja `description`. `finding_id` on yksilöllinen yhden toimituksen sisällä eikä se ole sama kuin laaduntarkistuksen `check_id`. `category` on tehtävätyyppikohtainen; yleistä yhteistä luokitteluluetteloa ei ole. Tehtävätyypin määritys sisältää sallitut kategoriatunnisteet sekä niiden nimet ja kuvaukset. Tunnisteet ovat koneellisesti käsiteltäviä, pienaakkosilla kirjoitettuja ja tarvittaessa yhdysmerkillisiä; havaintotietueeseen tallennetaan vain tunniste. Vastaanottaja tarkistaa, että tunniste kuuluu kyseisen tehtävätyypin sallittuihin kategorioihin. Esimerkkejä mahdollisista uutisseurannan tunnisteista ovat `announcement`, `release`, `event`, `personnel_change`, `controversy` ja `other`; nämä eivät muodosta yleistä pakollista luetteloa. `source_refs` viittaa saman toimituksen lähdetarkistuksissa kuvattuihin lähteisiin ja tarvittaessa sisältökanaviin, ei yksittäiseen tarkistusyritykseen. `occurred_at` ja `notes` ovat valinnaisia. Raportoitavilla havainnoilla ei ole yleistä vakavuusluokkaa.

Rakenteiset havainnot toimitetaan `findings.json`-tiedostossa vain, jos tehtävätyyppi sitä edellyttää. Tiedoston juurena ovat `schema_version` ja `findings`; `findings` on aina taulukko, myös tyhjänä. Tyhjä taulukko ei itsessään tarkoita `no_report`-tilaa. Metatietojen havaintoyhteenvedossa esitetään yhteenveto, määrä, mahdolliset luokkamäärät, rajaukset, epävarmuudet ja kattavuuspuutteet; yksittäisiä havaintotietueita ei kopioida metatietoihin.

#### Toimituspaketin tiedostoroolit ja tiedostoluettelo

Tehtävätyypin määritys määrittelee sallitut ja vaaditut tiedostoroolit. Rooli kuvaa tiedoston tarkoitusta ja polku sen sijaintia. Jokaisella roolilla on tehtävätyypin sisällä pysyvä ja yksilöllinen `file_id`. Roolimäärityksen kentät ovat `file_id`, `name`, `description`, `media_type`, `status_requirements` ja `parameters`. `parameters` on aina objekti; jos rooli ei tarvitse lisäasetuksia, arvo on `{}`. Roolikohtainen skeema määrittelee sallitut parametrit ja niiden tyypit sekä mahdolliset rajat. Tuntemattomat parametrit hylätään. Parametreilla voidaan kuvata esimerkiksi sisältömuotoa, kieltä tai roolikohtaisia sisältörajoituksia, mutta niillä ei määritellä uudelleen tiedoston tunnistetta, polkua, kokoa, tiivistettä tai tulostilakohtaisia vaatimuksia. `status_requirements` määrittelee kullekin tuottajan tulostilalle arvon `required`, `optional` tai `forbidden`. Tämä korvaa erilliset yleisen pakollisuuden ja sallittujen tilojen kentät, jotta päällekkäisiä tai ristiriitaisia sääntöjä ei synny.

`metadata.json` sisältää kaikkien toimitettujen sisältötiedostojen luettelon. Tietue sisältää kentät `file_id`, `path`, `media_type`, `size_bytes` ja `sha256`. Koko tavuina ja SHA-256-tiiviste ovat pakollisia jokaiselle luetteloidulle sisältötiedostolle. `metadata.json` ei sisälly omaan luetteloonsa. Polut ovat toimituspaketin juureen suhteutettuja, käyttävät `/`-erotinta eivätkä saa olla absoluuttisia tai sisältää `..`-siirtymiä tai symbolisia linkkejä. Tyhjät hakemistot eivät kuulu paketin tietosisältöön. Roolin sallittu tiedostomäärä määritellään tehtävätyypissä; oletusarvo on yksi tiedosto roolia kohti.

Toimituspaketin tiedostot yksilöidään toimituspaketin sisäisillä poluilla ja metatietojen tiedostoluettelon avulla. Jokaisella tiedostolla on yksi tiedostoluettelon tietue ja yksi tehtävätyypin mukainen rooli; samaa polkua ei saa ilmoittaa ristiriitaisilla rooleilla. Tiedostopolut ovat yksilöllisiä, ja vastaanottaja tarkistaa roolin, polun, tiedoston olemassaolon, koon ja SHA-256-tiivisteen vastaavuuden. Paketin ulkopuolelle osoittavia viittauksia ei sallita.

Kun tehtävätyyppi tuottaa julkaistavan raportin, raportti toimitetaan `item.xml`-tiedostossa. Tiedosto sisältää yhden RSS-itemin, ja koko raportin HTML-sisältö on itemin `<content:encoded>`-elementissä. Erillistä HTML-raporttitiedostoa ei toimiteta ensimmäisessä versiossa. `item.xml` vaaditaan vain tehtävätyypin ja tuottajan tulostilan sitä edellyttäessä; muut sisältötiedostot sallitaan vain tehtävätyypin määrittelemien tiedostoroolien perusteella.

Korjaus tai olennainen täydennys julkaistaan uutena RSS-iteminä, jolla on oma vastaanottajan luoma UUIDv4-GUID. Uuden itemin toimitusmetatiedoissa yksilöidään alkuperäisen itemin GUID ja ilmoitetaan uuden itemin suhteen tyyppi (korjaus tai täydennys). Raporttisisällössä suhde alkuperäiseen julkaisuun ilmaistaan lukijalle tarpeellisessa määrin. Alkuperäistä itemiä, raporttia tai toimituspakettia ei muuteta. Metatietojen täsmälliset kenttänimet määritellään skeematyössä.

#### Tulostilakohtaiset toimitusvaatimukset

`metadata.json` toimitetaan, jos tuottaja pystyy muodostamaan toimituksen. Jos tuottaja ei pysty muodostamaan edes metatietoja, vastaanottaja kirjaa toimituksen puuttumisen omaan ajohallintaansa eikä päättele tuottajan tulostilaa. `success`- ja `partial`-tilojen sisältötiedostot määräytyvät tehtävätyypin mukaan; jos tehtävätyyppi tuottaa raportin, `partial` edellyttää raporttitiedostoa. `no_report`-tilassa ei toimiteta raporttia eikä raportoitavia havaintoja, mutta lähdetarkistusten ja laaduntarkistusten tulokset voivat sisältyä metatietoihin. `failed`-tilassa ei toimiteta raporttia eikä raportoitavia havaintoja, mutta virhetiedot ja sallitut diagnostiikkatiedostot ovat mahdollisia. Roolien tilavaatimukset ilmaistaan `status_requirements`-kentässä.

#### Vastaanottajan validointivaiheet ja virheluokat

Vastaanottajan validointi etenee seitsemässä vaiheessa: (1) pakettirakenne, (2) metatiedot, (3) tiedostoluettelo, (4) eheys, (5) sisältö, (6) keskinäiset viittaukset ja (7) vastaanoton tulos. Virheluokat ovat `package_structure`, `metadata_invalid`, `file_missing`, `file_unexpected`, `file_reference_invalid`, `file_integrity_failed`, `content_invalid`, `cross_reference_invalid` ja `required_check_missing`. Luetteloa voidaan laajentaa. Koneellinen virheluokka ja ihmiselle luettava kuvaus tallennetaan erikseen. Yleistä virheiden vakavuusluokitusta tai automaattisia hyväksymisrajoja ei tässä vaiheessa määritellä. Vastaanottaja ei muuta tuottajan aineistoa; validoinnin tulos ja virheet tallennetaan vastaanottajan ajohallintaan. Tuottajan `failed`-tulos ja vastaanottajan validointivirhe ovat eri asioita.

#### Vastaanottoprosessin hyväksytyt toimintaperiaatteet

Vastaanottoprosessi käsittelee vain vastaanottohaaraan `raportit-inbox` toimitettuja paketteja. Yksittäinen toimitus sijaitsee polussa `deliveries/{run_id}/{delivery_id}/` ja käsitellään itsenäisenä kokonaisuutena. Vastaanottaja ei muuta alkuperäisen toimituspaketin tiedostoja eikä julkaise sisältöä suoraan `main`-haaraan. Vastaanotto, toimituksen hyväksyminen ja julkaiseminen ovat erillisiä tapahtumia. Yhden toimituksen virhe ei estä muiden toimitusten käsittelyä.

**Validoinnin järjestys ja keskeyttäminen.** Seitsemän validointivaihetta suoritetaan määritellyssä järjestyksessä. Samassa vaiheessa voidaan kirjata useita riippumattomia virheitä, mutta seuraavaan vaiheeseen ei siirrytä, jos sen turvalliset tai loogiset edellytykset eivät täyty. Turvattomasti käsiteltävä pakettirakenne keskeyttää käsittelyn. Toimitettua aineistoa ei korjata eikä muuteta.

**Tunnisteet, revisiot ja skeemat.** `run_id`-, `delivery_id`- ja tehtävätunnisteiden on vastattava toimituspolkua, metatietoja ja vastaanottajan ajotietoja. Skeemaversion on oltava tuettu; tuntematonta tai puuttuvaa versiota ei arvata. `software_revision`- ja `instance_revision`-arvojen on vastattava ajon käynnistyksessä kiinnitettyjä revisioita, ja tehtävätyypin määritysten on oltava saman ajon käyttämää revisiokokonaisuutta. Ristiriita estää hyväksymisen.

**Tiedostoluettelo ja eheys.** `metadata.json` luettelee kaikki toimitetut sisältötiedostot mutta ei itseään, jotta vältetään itseensä kohdistuva tiiviste- ja kehäsuhde. Vastaanottaja tarkistaa roolit ja polut, pakolliset ja kielletyt tiedostot, puuttuvat ja odottamattomat tiedostot, kaksoisviittaukset, tiedostojen olemassaolon, koon ja SHA-256-tiivisteen. Tiedostomäärän ja -koon rajat tarkistetaan ennen sisällön käsittelyä.

**XML-, RSS- ja HTML-turvallisuus.** XML-parseri ei käsittele DTD:tä tai ulkoisia entiteettejä eikä hae ulkoisia resursseja. `item.xml` validoidaan yhden `<item>`-elementin toimitussopimusta, järjestystä, pakollisuutta, attribuutteja ja item-elementin `content`-nimiavaruutta vasten. HTML tarkistetaan sallitun elementti- ja attribuuttiluettelon sekä linkkien osoitemuotojen perusteella. Kiellettyä sisältöä ei poisteta hiljaisesti eikä sisältöä korjata automaattisesti; toimitus hylätään yksilöidyllä virheellä.

**Keskinäiset viittaukset.** Tiedostoviittausten on osoitettava olemassa oleviin luetteloituihin tiedostoihin. Roolien, polkujen, tunnisteiden ja ajotietojen on oltava johdonmukaisia. GUIDin on oltava yksilöllinen julkaisu- ja historiatiedoissa. Korjaus- tai täydennysitemin alkuperäisen GUID-viittauksen on osoitettava olemassa olevaan julkaisuun ja suhteen tyypin oltava sallittu.

**Virheet ja hyväksymisen raja.** Rakenteelliset, tunniste-, revisio-, skeema-, tiedosto-, eheys- ja sisältövirheet ovat pysyviä ja johtavat hylkäykseen. Tilapäinen suoritusympäristö- tai GitHub-virhe voi johtaa rajattuun uudelleenyritykseen; määrät ja viiveet ratkaistaan kohdassa 9.7. Virheestä tallennetaan koneellinen luokka, ihmiselle luettava kuvaus sekä mahdollisuuksien mukaan tiedosto tai polku. Varoitukset eivät ohita pakollisia tarkistuksia. Hyväksyntä edellyttää kaikkien soveltuvien pakollisten tarkistusten läpäisyä eikä itsessään tarkoita julkaisua. Vastaanottajan virhe ei muuta tuottajan tulostilaa.

Vastaanottaja tunnistaa toimituksen sen hakemistopolun ja toimitusmetatietojen perusteella. Se tarkistaa, että `run_id` ja `delivery_id` ovat johdonmukaisia, että ajo on olemassa ja että ajo kuuluu tunnetulle tehtävälle. Tehtävän ja ajon välisten tunnisteiden sekä aikaleimojen on oltava keskenään johdonmukaisia. Tuntemattomaan ajoon tai tehtävään viittaava toimitus hylätään; vastaanottaja ei luo puuttuvia ajoja tai tehtäviä toimituksen perusteella.

Toimituspaketin vähimmäissisältö on `metadata.json` sekä tehtävätyypin edellyttämät sisältötiedostot. `item.xml` on pakollinen vain silloin, kun tehtävätyyppi ja tuottajan tulostila sitä edellyttävät. Sallitut tiedostoroolit ja niiden tilakohtaiset vaatimukset määräytyvät tehtävätyypin määrityksestä. Odottamattomat tiedostot hylätään. Polkujen on pysyttävä toimituspaketin sisällä; absoluuttisia polkuja, `..`-siirtymiä, symbolisia linkkejä tai muita paketin ulkopuolelle osoittavia viittauksia ei hyväksytä. Ensimmäisen version pakettimalli pidetään suppeana eikä siihen sisälly yleistä liite- tai kuvakäsittelyä.

Toimitusmetatiedot validoidaan niitä vastaavaa skeemaa vasten. Vastaanottaja tarkistaa pakolliset tiedot, tietotyypit, sallitut arvot, skeemaversion sekä tunnisteiden vastaavuuden toimituspolkuun ja alkuperäiseen ajoon. Tuntematonta skeemaversiota ei tulkita arvaamalla. Metatietojen tarkka kenttärakenne määräytyy erillisessä toimitusmetatietojen tietomallissa; tässä hyväksytty prosessi ei korvaa eikä muuta jo päätettyä kuuden tietoryhmän rakennetta.

Sisältötiedostot validoidaan erillään metatiedoista. Yleinen sisältövalidointi kattaa tiedoston luettavuuden ja koodauksen, syntaksin, tehtävätyypin mukaisen rakenteen, pakolliset sisältöelementit sekä tiedostojen väliset viittaukset. RSS-itemin toimitustiedosto sisältää täsmälleen yhden `<item>`-elementin eikä kokonaista RSS-syötettä. Itemissä ei käytetä `<link>`-elementtiä; lähteet linkitetään raportin HTML-sisällössä lähteistettävän tiedon yhteydessä ja/tai raportin lopun lähdeluettelossa. RSS-itemin elementit ovat täsmälleen seuraavat tässä järjestyksessä: pakollinen `<title>`, pakollinen `<guid isPermaLink="false">`, pakollinen UTC-aikainen `<pubDate>`, valinnainen lyhyt `<description>` ja pakollinen `<content:encoded>`. Muita RSS-elementtejä, kuten `<author>`, `<category>`, `<comments>`, `<enclosure>` tai `<source>`, ei käytetä. GUIDin ainoa sallittu attribuutti on `isPermaLink="false"`; muille elementeille ei lisätä attribuutteja. `content`-nimiavaruus määritellään item-elementissä muodossa `xmlns:content="http://purl.org/rss/1.0/modules/content/"`, koska tiedosto ei sisällä RSS-kanavan ympäröivää elementtiä. `<guid>` yksilöi itemin eikä toimi linkkinä raporttisivulle. Koko raportti toimitetaan RSS Content -laajennuksen `<content:encoded>`-elementissä HTML-muodossa. `<description>` on vapaaehtoinen lyhyt tiivistelmä eikä siihen kopioida koko raporttia. Raportin HTML-sisällöllä on yhteinen perusrakenne, mutta varsinainen sisältö ja sen jäsentely voivat vaihdella aiheen ja tehtävätyypin mukaan. `<pubDate>` esitetään UTC-ajassa RSS:n päivämäärämuodon mukaisesti; käyttöliittymä voi muuntaa ajan paikalliseen aikavyöhykkeeseen. GUIDin muodostus ja säilytys on määritelty erikseen; HTML:n sallittu tekninen sisältö ja validointikäytäntö on määritelty tässä kohdassa; raportin yhteinen rakenne ja otsikkohierarkian käyttö täsmennetään kohdassa 9.3.

XML ja HTML muodostetaan turvallisesti erillisinä rakenteina. XML tuotetaan XML-kirjastolla; XML-tekstisolmujen sisältö escapetaan kirjaston normaalilla tavalla. `<content:encoded>`-elementin HTML-sisältö sarjoitetaan CDATA-osioon. Jos HTML sisältää merkkijonon `]]>`, CDATA-osio jaetaan XML:n mukaisesti turvallisesti niin, että alkuperäinen sisältö säilyy muuttumattomana.

HTML:n sallittuun elementtijoukkoon kuuluvat otsikot `h1`–`h6`; tekstielementit `p`, `br`, `strong`, `em` ja `blockquote`; listaelementit `ul`, `ol` ja `li`; linkkielementti `a`; sekä rakenteelliset elementit `article`, `section`, `figure`, `figcaption` ja `time`. Kuvien `img`-elementtiä ei sallita ensimmäisessä versiossa, vaan kuvien käyttö rajataan jatkokehitykseen. Sallitut attribuutit ovat `a`-elementillä `href` ja `title` sekä `time`-elementillä `datetime`. Muita attribuutteja ei sallita. JavaScript, tapahtumankäsittelijät, lomakkeet, upotetut objektit, tyylitiedostot ja CSS-tyylimäärittelyt ovat kiellettyjä.

HTML validoidaan ennen toimituksen hyväksymistä. Virheellistä tai sallittujen elementtien ja attribuuttien vastaista HTML:ää ei korjata automaattisesti, vaan toimitus hylätään yksilöidyllä virheellä. Validointi tarkistaa lisäksi linkkien osoitemuodot. HTML:n tarkka yhteinen raporttirakenne, otsikkohierarkian käyttö, saavutettavuus ja aihekohtaisen vaihtelun rajat määritellään erikseen kohdassa 9.3.

Eheystarkistuksessa vastaanottaja laskee jokaiselle toimitetulle sisältötiedostolle koon ja SHA-256-tiivisteen ja vertaa niitä metatiedoissa ilmoitettuihin arvoihin. Puuttuva tiedosto, väärä koko tai tiiviste, tai tiedostokohtaisen ja toimituskohtaisen kokorajan ylitys estää hyväksymisen. Tiiviste todentaa sisällön eheyden, ei lähettäjän henkilöllisyyttä. Vastaanottaja ei suorita toimituspaketin sisältämää koodia.

Kaksoistoimitusten käsittely on idempotentti. Saman `delivery_id`-tunnisteen ja saman sisällön uudelleen vastaanottaminen tunnistetaan saman toimituksen uusinnaksi eikä siitä synny uutta julkaisua tai päällekkäisiä sivuvaikutuksia. Saman tunnisteen yhteydessä havaittu eri sisältö on ristiriita ja hylätään. Uusi toimitustunniste voi kuulua samaan ajoon vain toimitussopimuksen sallimissa rajoissa. RSS-itemin GUIDin mahdollinen toistuminen tarkistetaan erikseen julkaisu- ja historiatiedoista. Aiemmin hylätyn toimituksen uusi yritys on erotettava alkuperäisestä käsittely-yrityksestä.

Vastaanoton käsittelyssä erotetaan vähintään vastaanotettu, tarkistuksessa, hyväksytty, julkaisukelpoinen ja julkaistu -tilat sekä hylätty ja tilapäistä uudelleenyritystä odottava tila. Pysyvä rakenteellinen, metatieto-, eheys- tai sisältövirhe johtaa hylkäykseen. Tilapäinen tekninen virhe voi johtaa rajattuun uudelleenyritykseen. Uudelleenyritysten määrä ja viive rajataan; käsittelyn tarkat tekniset parametrit määritellään myöhemmin. Virheestä kirjataan koneellinen virheluokka ja ihmiselle luettava kuvaus. Hylättyä tai keskeneräistä toimitusta ei julkaista.

Vastaanoton kirjanpito tallentaa vähintään ajon ja toimituksen tunnisteet, tehtävän tunnisteen, vastaanottoajan, toimitettujen tiedostojen luettelon ja tiivisteet, käytetyn skeemaversion, validointitulokset, käsittelyn lopputilan sekä mahdolliset virhekoodit ja kuvaukset. Julkaisun yhteydessä tallennetaan myös julkaisuun yhdistävä tunniste ja varmennettu julkaisutila. Kirjanpito säilyttää käsittelyn jäljitettävyyden eikä muuta alkuperäistä toimituspakettia.

Vastaanotto ja julkaisu toteutetaan erillisinä GitHub Actions -työnkulkuvastuina. Vastaanottotyönkulku käynnistyy vastaanottohaaran toimitusmuutoksista, validoi toimituksen ja kirjaa tuloksen. Julkaisutyönkulku voi käsitellä vain hyväksytyn toimituksen, varmistaa hyväksynnän vastaanottajan tallentamista tiedoista ja siirtää sisällön erikseen `main`-haaraan. Julkaisun jälkeen tarkistetaan julkaistun sisällön ja RSS/XML:n kelvollisuus. Vastaanoton onnistuminen ei itsessään käynnistä tai todista julkaisun onnistumista.

Turvallisuusvaatimuksena vastaanottaja käsittelee pakettia epäluotettavana datana, ei ohjeina tai suoritettavana koodina. Tiedostopolut rajataan toimituspaketin sisälle, tiedostokoot ja määrät rajoitetaan ja vastaanottoprosessille annetaan vain välttämättömät oikeudet. `main`-haaran suojaus ja sen kyky estää Codex Connectorin suora ohitus on varmennettava ennen tuotantokäyttöä.

Ensimmäiseen versioon eivät kuulu erillinen HTTPS-vastaanottopalvelu, erillinen vastaanotto-GitHub App, lähettäjän erillinen käyttäjätunnistus, useiden raportintuottajien samanaikainen käsittely, yleinen manuaalinen hyväksymisjärjestelmä, automaattinen toimitusten korjaaminen tai yleinen liitetiedostojen ja kuvien vastaanottomalli.


Toimituspaketti sisältää aina tuottajan toimitusmetatiedot (`metadata.json`) sekä tehtävätyypin määrityksessä edellytetyt sisältötiedostot. Sisältötiedostot voivat olla esimerkiksi julkaistava RSS-item tai rakenteinen havaintoaineisto; niiden tarkat tiedostotyypit ja pakollisuus määräytyvät tehtävätyypin mukaan. Metatiedot kuvaavat toimitusta ja sen sisältöä. Julkaistavan raportin koko HTML-sisältö sisältyy `item.xml`-tiedoston `<content:encoded>`-elementtiin; erillistä HTML-raporttitiedostoa ei toimiteta ensimmäisessä versiossa. Metatietoihin sisältyvät tiedostoviittaukset osoittavat toimituspaketin juureen suhteutettuihin polkuihin. Viittaus ei saa osoittaa toimituspaketin ulkopuolelle, ja viitatun tiedoston on oltava toimituksessa mukana.

Vastaanottaja tarkistaa toimituspaketin eheyden: vaaditut tiedostot ovat mukana, viittaukset ovat kelvollisia, viitatut tiedostot löytyvät ja toimitus ei sisällä tehtävätyypin sääntöjen vastaisia ylimääräisiä tiedostoja. Toimitus hyväksytään vastaanotetuksi vasta, kun sen rakenteelliset ja sisällölliset vaatimukset on validoitu. Vastaanottaja ei korjaa eikä muuta tuottajan alkuperäisiä metatietoja tai sisältötiedostoja. Puutteellinen tai virheellinen toimitus hylätään tai kirjataan virheelliseksi vastaanottajan omiin ajotietoihin; virheen syy ei muuta tuottajan ilmoittamaa tulosta. Tarkat tiedostoluettelot ja metatietojen tiedostoviittauskenttien nimet määritellään myöhemmässä skeemasuunnittelussa.

Raporttia ei tuoteta uudelleen vastaanottavassa järjestelmässä eikä tuottaja palauta koko RSS-syötettä.

### 6.1.1 Vastaanoton ja julkaisun työnkulku

Vastaanoton ja julkaisun käsittely etenee seuraavien tilojen kautta. Tilat kuvaavat vastaanottajan käsittelyä, eivät raportintuottajan ilmoittamaa tulostilaa:

1. **Ajo odottaa toimitusta:** vastaanottaja on luonut ajotietueen ja tehtäväpyyntö on annettu tuottajalle. Ajo odottaa toimitusta. Määräajan umpeutuminen kirjataan erillisenä tapahtumana, eikä se itsessään estä myöhempää toimitusta.
2. **Vastaanotettu:** toimitus on saapunut vastaanottohaaraan. Vastaanottaja kirjaa toimitustunnisteet, vastaanottoajan ja toimituksen sijainnin.
3. **Tarkistuksessa:** vastaanottaja suorittaa kohdan 9.5 mukaiset validointivaiheet.
4. **Hyväksytty:** kaikki pakolliset validointitarkistukset ovat läpäisseet. Hyväksyminen ei vielä tarkoita, että sisältö olisi julkaistu.
5. **Julkaisukelpoinen:** hyväksytty toimitus sisältää tehtävätyypin ja tuottajan tulostilan edellyttämän julkaistavan RSS-itemin, ja se voidaan siirtää julkaisukäsittelyyn.
6. **Julkaistu:** RSS-item, kanonisen ajotietueen julkaisutietojen päivitys ja kyseiseen julkaisuun liittyvät uudet tapahtumahistoriatapahtumat on tallennettu samaan atomiseen Git-commitiin ja tallennuksen sisältö on varmennettu.

Poikkeustilat ja julkaisematta päättyvät käsittelyt ovat:

- **Hylätty:** toimituksessa on pysyvä validointivirhe, joka estää hyväksymisen.
- **Tilapäistä uudelleenyritystä odottava:** tilapäinen tekninen virhe estää käsittelyn jatkamisen. Uudelleenyritysten tarkat määrät ja viiveet määritellään kohdassa 9.7.
- **Käsitelty ilman julkaisua:** toimitus on hyväksytty ja käsitelty, mutta tehtävätyyppi tai tuottajan tulostila ei edellytä RSS-itemiä, esimerkiksi `no_report`-tuloksessa. Tällöin ajoa ei merkitä julkaistuksi eikä sille synny RSS-itemiä.

Vastuut erotetaan seuraavasti:

- **Vastaanottotyönkulku** vastaanottaa toimituksen, kirjaa sen, validoi sen, tekee hyväksymis- tai hylkäyspäätöksen ja toteaa, onko toimitus julkaisukelpoinen.
- **Julkaisutyönkulku** käsittelee vain hyväksytyn ja julkaisukelpoiseksi todetun toimituksen. Se tallentaa julkaisun ja varmentaa tallennuksen.
- Vastaanottava järjestelmä ylläpitää ajon kanonista nykytilaa ja tapahtumahistoriaa. Tapahtumahistoriaan kirjataan toteutuneet vaiheet ja poikkeamat; aiempia tapahtumia ei poisteta tai ylikirjoiteta.

Julkaisu tallennetaan yhtenä atomisena repositoriomuutoksena. Samaan Git-commitiin kuuluvat julkaistava RSS-item, kanonisen ajotietueen päivitys sekä kyseiseen julkaisuun liittyvät tapahtumahistorian lisäykset. Commitin syntyminen ja sen sisältö varmennetaan ennen kuin ajo merkitään julkaistuksi. Jos commitia ei synny, julkaisua ei ole tapahtunut. Jos commitin tulos jää teknisen virheen vuoksi epäselväksi, vastaanottaja tarkistaa repositorion todellisen tilan ennen uutta yritystä.

Määräajan umpeutuminen ei estä myöhäisen toimituksen vastaanottamista. Myöhäinen toimitus liitetään alkuperäiseen `run_id`-ajoon. Määräajan ylitys, myöhäinen vastaanotto, validointi, hyväksyntä tai hylkäys sekä mahdollinen julkaisu kirjataan erillisinä tapahtumina. Myöhempi onnistuminen ei poista aiempaa määräajan ylitystä eikä muuta tapahtumahistorian aikajärjestystä. Julkaisukelpoinen toimitus odottaa julkaisutyönkulkua; jos julkaisu epäonnistuu, tilanne kirjataan ja sitä käsitellään tilapäisenä tai pysyvänä virheenä virheluokituksen mukaisesti.

Tämä työnkulku erottaa toisistaan toimituksen hyväksymisen, julkaisukelpoisuuden ja toteutuneen julkaisun. Näin hyväksyttyä mutta vielä julkaisematta olevaa toimitusta ei esitetä julkaistuna, ja myös julkaisuvaiheen epäonnistuminen jää jäljitettäväksi.
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

Tilastoinnin yksikkö on sisältökanavan yksittäinen avausyritys. Yrityksestä tallennetaan vähintään lähde- ja kanavatunnisteet, `run_id`, ajankohta, pyydetty osoite, avauksen tulos (`opened` tai `failed`), epäonnistumisen luokka silloin kun se voidaan tunnistaa sekä sisällön luettavuus (`readable`, `partial`, `unreadable` tai `not_assessed`). `not_attempted` kuvaa avaamatta jäänyttä kanavaa eikä ole avausyritys tai epäonnistuminen. Sama yritys lasketaan tilastoihin vain kerran. Avaamisen tekninen onnistuminen, sisällön luettavuus ja sisällön hyödyllisyys tai relevanssi ovat erillisiä tuloksia.

Yleiset epäonnistumisen luokat ovat `timeout`, `connection_error`, `dns_error`, `tls_error`, `http_client_error`, `http_server_error`, `rate_limited`, `access_restricted`, `content_error` ja `unknown`. Tarkempi tekninen tulos, kuten HTTP-status, säilytetään mahdollisuuksien mukaan. Luokkaa ei päätellä, jos syy ei ole tiedossa.

Valvomo johtaa tilastot kanoniseen ajohistoriaan tallennetuista alkuperäisistä yrityksistä; tuottajan valmiiksi laskemia prosentteja ei käytetä lähdetietona. Tarkastelujaksot ovat oletusarvoisesti viimeiset 30 päivää, viimeiset 90 päivää ja koko tallennettu historia. Tilastoja voidaan suodattaa aiheen, tehtävätyypin, lähteen ja sisältökanavan mukaan. Näytettäviä tietoja ovat yritysten määrä, onnistuneet ja epäonnistuneet avaukset, onnistumisaste osoittajineen ja nimittäjineen, viimeisin onnistuminen ja epäonnistuminen, virheluokkien jakauma sekä kehitys tarkastelujaksolla. Prosenttia ei esitetä ilman luotettavaa nimittäjää, ja otoskoko näytetään aina prosenttiluvun yhteydessä.

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
- RSS-itemin toimitustiedosto sisältää vain yhden `<item>`-elementin; tuottaja ei muodosta eikä palauta kokonaista RSS-syötettä.
- RSS-item sisältää koko raportin.
- Itemissä ei käytetä `<link>`-elementtiä eikä tätä sääntöä voi muuttaa aihe- tai tehtäväkohtaisella asetuksella.
- Lähteet linkitetään raportin HTML-sisällössä lähteistettävän tiedon yhteydessä ja/tai raportin lopun lähdeluettelossa.
- Itemillä on yksilöllinen `<guid>`, joka toimii tunnisteena eikä raporttisivun linkkinä.
- Raportti on suomenkielinen ja sisältää aina seurannan aikavälin. Merkittävät aikavälin ulkopuoliset täydennykset esitetään erillään varsinaisesta seurannasta ja niiden todellinen ajankohta ilmoitetaan.
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

### 7.1 Raportin HTML-perusrakenne

Jokainen raportti esitetään yhden `<article>`-elementin sisällä. Raportin yhteinen perusrakenne sisältää:

- yhden `<h1>`-elementin raportin otsikolle;
- raportin seuranta-aikavälin selkokielisen esityksen raportin alussa;
- raportin varsinaisen sisällön loogisesti jäsenneltyinä `<section>`-osioina;
- lähteiden esittämisen joko havaintojen yhteydessä, erillisessä lähdeosiossa tai näiden yhdistelmänä.

Rakenne on yhteinen looginen malli, ei vaatimus täsmälleen tietystä määrästä `<section>`-elementtejä tai kaikille aiheille samasta osiojaosta. Erillinen raportin lopun lähdeluettelo ei ole pakollinen, mutta jokaisen raportoitavan väitteen lähteet on esitettävä niin, että niiden yhteys havaintoon on tunnistettavissa.

Otsikkohierarkiassa käytetään yhtä `<h1>`-otsikkoa. Pääosiot merkitään `<h2>`-otsikoilla ja niiden alaosiot tarvittaessa tasoilla `<h3>`–`<h6>`. Otsikkotasoja ei hypitä ilman rakenteellista perustetta, eikä tasoa valita visuaalisen ulkoasun perusteella. RSS-itemin `<title>` ja HTML-raportin `<h1>` saavat olla samat, mutta niiden ei tarvitse olla teknisesti identtiset: RSS-otsikko voi olla lyhyempi ja HTML-otsikko kuvailevampi.

Seurannan aikaväli ilmoitetaan jokaisessa raportissa yksiselitteisesti raportin alussa. Päivämäärät esitetään lukijalle ymmärrettävästi. Aikavälin alku- ja loppuhetki voidaan merkitä koneellisesti luettavilla `<time datetime="...">`-elementeillä silloin, kun tarkat ajanhetket ovat tiedossa. Raporttiin ei lisätä sisäisiä tunnisteita tai ajotietoja, elleivät ne ole lukijan kannalta tarpeellisia.

Raportin varsinainen seuranta käsittelee tehtäväpyynnön mukaista aikaväliä. Raporttiin saa lisäksi sisällyttää erillisenä, selvästi nimettynä täydennysosiona merkittäviä uutisia tai havaintoja tämän aikavälin ulkopuolelta, myös edelliseltä seurantajaksolta, jos ne ovat aiemmasta raportista jääneet olennaisesti puuttumaan. Täydennyksiä ei käytetä tavalliseen uutisten jälkikäteiseen kierrättämiseen tai raportin täyttämiseen, vaan niiden on oltava aiheen kannalta merkittäviä ja lukijalle aidosti hyödyllisiä. Täydennysosiossa ilmoitetaan uutisen tai tapahtuman todellinen ajankohta tai ajanjakso, ja tehdään selväksi, että kyse on aiemman tai muuten seurantajakson ulkopuolisen tiedon täydentämisestä. Jos täydennys liittyy aiempaan raporttiin, siihen viitataan mahdollisuuksien mukaan. Täydennys ei muuta raportin varsinaista seuranta-aikaväliä eikä anna ymmärtää, että uutinen olisi tapahtunut nykyisellä seurantajaksolla. Aiemmin julkaistua raporttia ei muuteta; olennainen täydennys julkaistaan uuden raportin osana tai erillisenä korjaus-/täydennysiteminä julkaisusääntöjen mukaisesti.

Lähdelinkkien tekstin tulee kuvata ymmärrettävästi linkin kohdetta myös asiayhteydestä erotettuna. Lähteen ja sitä tukevan havainnon välinen yhteys on voitava tunnistaa. Samaa lähdettä ei tarvitse linkittää kahteen kertaan, jos yhteys on muuten yksiselitteinen.

Raportin saavutettavuuden perustana ovat johdonmukainen otsikkohierarkia, ymmärrettävät kappaleet ja osiot, oikeat listaelementit, kuvaavat linkkitekstit sekä sisältörakenteen ymmärrettävyys ilman visuaalista muotoilua. Päivämäärien koneellista luettavuutta tuetaan `<time>`-elementillä silloin, kun se on käytössä. WCAG 2.2 AAA on tavoitetaso, mutta vaatimustenmukaisuutta ei väitetä ilman asianmukaista testausta.

Yhteinen perusrakenne ei pakota eri seurantatyyppejä samanlaiseen sisältöön. Uutisseuranta voi ryhmitellä havainnot aiheittain, tapahtumaseuranta tuleviin ja menneisiin tapahtumiin, elokuvaseuranta elokuvittain ja henkilöseuranta henkilöittäin tai tapahtumatyypeittäin. Sisältöosioiden nimet, määrä ja järjestys voivat vaihdella; yhteisiä ovat raportin perusrakenne, seuranta-aikavälin ilmoittaminen, otsikkohierarkia, lähteiden jäljitettävä esittäminen sekä mahdollisten aikavälin ulkopuolisten täydennysten selkeä erottaminen varsinaisesta seurannasta.

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
- Valvomo voi nostaa toistuvasti epäonnistuvia lähteitä tarkistettaviksi ja näyttää tilastojen perusteella ehdotuksen lähteen käytöstä poistamisesta. Lähdettä ei poisteta tai poisteta käytöstä automaattisesti pelkän tilaston perusteella; tilapäiset häiriöt, käyttörajoitukset ja pienet otokset huomioidaan, ja käytöstä poistaminen tehdään lähderekisterin hallittuna muutoksena. Toistuvan epäonnistumisen alustava nostokriteeri on vähintään viisi avausyritystä vähintään kolmessa eri ajossa ja alle 50 prosentin onnistumisaste viimeisten 30 päivän aikana. Viimeisimmät peräkkäiset epäonnistumiset voidaan näyttää erillisenä huomiona. Raja-arvot ovat määrityksiä, eivät kovakoodattuja päätöksiä; nostaminen tarkoittaa vain ylläpitäjän arviointipyyntöä.

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

### 9.2 Ensimmäisen version toimituskanava ja luottamusraja

Ensimmäisessä versiossa raportintuottajana toimii ChatGPT:n ajastettu tehtävä, joka toimittaa valmiin toimituspaketin GitHubiin ChatGPT:n Codex Connector -yhteyden kautta. Toimitukset tehdään instanssirepositorion erilliseen vastaanottohaaraan `raportit-inbox`; tuottaja ei kirjoita suoraan `main`-haaraan eikä julkaistaviin RSS-tiedostoihin. Toimituspaketin polku on `deliveries/{run_id}/{delivery_id}/`, ja paketti sisältää vähintään tulostilan edellyttämät tiedostot, kuten `metadata.json` ja tarvittaessa `item.xml`.

Codex Connector on ChatGPT:n ja GitHubin välinen yhteys, ei instanssirepoon asennettava GitHub App. Käytännön toimitustestissä ajastettu ChatGPT-tehtävä pystyi luomaan testitiedoston instanssirepositorion erilliseen haaraan Codex Connectorin kautta. Testissä `main`-haara ei muuttunut. Tämä vahvistaa toimitusmallin toimivuuden kyseisessä käyttöympäristössä; tuotantokäyttöönotossa on silti varmennettava käytössä olevan yhteyden kirjoitusoikeudet ja työnkulun toiminta.

Codex Connectorin repositoriokäyttöoikeus ei rajaudu automaattisesti yksittäiseen haaraan. Erillinen vastaanottohaara on toimitusten käsittelyraja, ei käyttöoikeusraja. Siksi `main`-haara on suojattava erikseen siten, ettei raportintuottajan toimitus voi muuttaa julkaisuhaaraa suoraan tai ohittaa sen suojausta. Suojaus ja sen tosiasiallinen toiminta on varmennettava ennen tuotantokäyttöä. Ensimmäisessä versiossa ei käytetä erillistä vastaanotto-GitHub Appia; sellainen voidaan luoda uudelleen myöhemmin, jos käyttöoikeuksien eriyttämiseen syntyy tarve.

Toimitus ja julkaisu ovat eri vaiheita. Vastaanottohaaraan tehty push tarkoittaa vain toimituksen siirtymistä GitHubiin, ei sen validointia, hyväksymistä tai julkaisemista. Vastaanottohaaraan tehty muutos käynnistää GitHub Actions -käsittelyn, joka kirjaa vastaanoton, validoi toimituspaketin ja kirjaa käsittelyn tuloksen vastaanottajan ajotietoihin ja työnkulun tulokseen. Vain validoitu ja hyväksytty sisältö siirretään erikseen `main`-haaraan. Virheellinen toimitus ei muuta julkaistuja RSS-syötteitä.

Vastaanottaja tarkistaa vähintään, että toimitus kuuluu olemassa olevaan tehtävään, sen `run_id`- ja `delivery_id`-tunnisteet ovat johdonmukaiset, toimituspaketin rakenne ja sisältö täyttävät tehtävätyypin vaatimukset ja toimitus on eheä. Vastaanottaja muodostaa oman käsittely-yrityksen `attempt_id`-tunnisteen, laskee toimitussisällön SHA-256-tiivisteen ja säilyttää vastaanotetun alkuperäisen paketin. Kaksois- ja ristiriitatilanteissa noudatetaan kohdassa 10.2 määriteltyjä sääntöjä.

Erillistä HTTPS-vastaanottopalvelua tai käyttäjäkohtaista tunnistamista ei toteuteta ensimmäisessä versiossa. Codex Connectorin käyttöoikeus perustuu ChatGPT-yhteyteen ja sen GitHubiin myönnettyihin oikeuksiin; se ei yksin tuota toimitukseen luotettavaa tietoa siitä, kuka ihminen käynnisti yksittäisen ajastetun tehtävän. Erillinen lähettäjän tunnistaminen, rajatummat käyttöoikeusrajat ja vaihtoehtoiset toimituskanavat voidaan arvioida myöhemmissä versioissa.

### 9.2.1 Julkinen instanssirepositorio ja vastaanoton käyttöoikeudet

Ensimmäisen vaiheen instanssirepositorio on julkinen. Sen RSS-syötteet julkaistaan GitHub Pagesin kautta. Julkisuus koskee koko repositoriota ja sen Git-historiaa, myös vastaanottohaaraa: kaikki sinne toimitettava aineisto käsitellään julkisena. Repositorioon, toimituspaketteihin, ajohistoriaan tai työnkulkujen tuottamiin julkisiin tiedostoihin ei saa sisällyttää salasanoja, API-avaimia, käyttöoikeustunnisteita, yksityisiä tietoja tai muuta luottamuksellista sisältöä.

Vastaanotto ja julkaisu pidetään erillään. ChatGPT:n ajastettu tehtävä toimittaa paketit Codex Connectorin kautta haaraan `raportit-inbox`. Vastaanotetut paketit tallennetaan hakemistoon `deliveries/{run_id}/{delivery_id}/`. Hyväksytyt ja julkaistavat tiedot tallennetaan erikseen julkaisuhaaraan `main`. GitHub Actions käsittelee vastaanottohaaran toimitukset, validoi ne ja siirtää vain hyväksytyn sisällön julkaisuun. Vastaanottohaaraan tehty push ei itsessään hyväksy eikä julkaise toimitusta.

Vastaanottohaaraan säilytetään kaikki sinne vastaanotetut toimituspaketit, myös validoinnissa hylätyt ja muutoin hyväksymättä jääneet toimitukset. Alkuperäinen paketti säilytetään muuttumattomana, eikä hylättyä toimitusta siirretä `main`-haaraan. Säilytys mahdollistaa toimitusten jälkikäteisen tarkastelun ja Valvomon virhetilanteiden seurannan. Valvomon tulee pystyä näyttämään myös hylättyjen toimitusten tila, validointitulokset ja virhetiedot. Valvomon tarvitsemien tietojen lukutapa ja turvallinen esitysmuoto täsmennetään A10:n jäljellä olevissa kohdissa; vastaanottohaaran raakaa toimituspakettia tai sisäistä tapahtumahistoriaa ei tämän päätöksen perusteella julkaista Pages-sivustolle.

Codex Connectorin GitHub-oikeudet ovat repositoriokohtaisia eivätkä rajaudu itsessään vain vastaanottohaaraan. Siksi `main`-julkaisuhaaran suojaus on toteutettava ja varmennettava erillisillä haara- tai ruleset-asetuksilla sekä työnkulun tarkistuksilla. Käyttöönotossa on varmistettava, ettei raportintuottajan käyttämä yhteys voi ohittaa julkaisuhaaran suojauksia. Ensimmäisessä versiossa ei asenneta erillistä vastaanotto-GitHub Appia.

Instanssirepositorion julkisuus ja Pages-julkaisu eivät muuta yhteisen ohjelmistorepositorion ja instanssirepositorion erillistä vastuunjakoa. Julkinen instanssirepo on ensimmäisen käyttöönoton ratkaisu; luottamuksellisen aineiston käsittely tai yksityinen instanssi edellyttää myöhempää erillistä suunnittelua.

### 9.2.2 Instanssirepositorion RSS-syötteet ja Pages-julkaisun lähde

RSS-syötteen identiteetti muodostuu aiheen ja tehtävätyypin yhdistelmästä. Jokaisella aihe–tehtävätyyppi-yhdistelmällä on oma erillinen RSS-tiedostonsa; saman aiheen eri tehtävätyypit eivät saa päätyä samaan syötteeseen. Syötteet sijoitetaan aihekohtaisiin hakemistoihin muodossa `feeds/{topic_id}/{task_type_id}.xml`. Esimerkiksi intialaisen elokuvan uutiset ja näytösseuranta ovat eri tehtävätyyppejä ja saavat eri syötetiedostot. Syöteluettelo muodostetaan instanssin määrityksistä tai niitä vastaavasta indeksistä, eikä aiheita tai syötteitä kovakoodata yhteiseen käyttöliittymään.

GitHub Pages -sivustoa ei julkaista suoraan instanssirepositorion raakasisällöstä. Erillinen rakennusvaihe muodostaa julkaisuartifactin vain hyväksytystä ja julkaistavaksi tarkoitetusta sisällöstä. Raaka toimituspaketti, vastaanottoaineisto ja sisäinen ajohistoria eivät päädy Pages-artifactiin vahingossa. Julkaistavan artifactin sisältö tarkistetaan ennen Pages-julkaisua.

Kaikki vastaanottohaaraan saapuneet alkuperäiset toimituspaketit säilytetään siellä muuttumattomina, myös hylätyt ja hyväksymättä jääneet toimitukset. Kun toimitus hyväksytään, sen alkuperäinen paketti kopioidaan lisäksi `main`-haaraan auditointia ja jäljitettävyyttä varten. `main`-haaraan ei kopioida hylättyjä tai hyväksymättömiä toimituksia. Vastaanottajan kanoniset ajotiedot, tapahtumahistoria ja julkaistut RSS-tiedostot ovat alkuperäisestä toimituspaketista erillisiä tietokokonaisuuksia. Valvomon tulee saada näkyviinsä myös vastaanottohaaraan jääneiden hylättyjen toimitusten tilat, validointitulokset ja virhetiedot; niiden tarkka lukutapa ja esitysmuoto ratkaistaan A10:n jäljellä olevassa suunnittelussa. Kaikki instanssirepoon tallennettava aineisto on julkista, joten toimituspaketti ei saa sisältää salaisuuksia tai yksityisiä tietoja.

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
- **RSS `guid`** yksilöi julkaistun raportti-itemin. Vastaanottaja luo RSS-itemin GUIDin satunnaisena UUIDv4-tunnisteena. GUID ei johdu `run_id`-, `task_id`-, `delivery_id`- tai muista tehtävän, ajon tai raportin tiedoista eikä sisällä niistä johdettavaa tietoa. Vastaanottaja tallentaa GUIDin kanoniseen ajotietueeseen samassa atomisessa julkaisutoimessa RSS-itemin kanssa. Saman ajon uudelleenyritykset käyttävät ajotietueeseen tallennettua GUIDia; ne eivät luo uutta tunnistetta. Jokainen erillinen korjaus- tai täydennysitem saa vastaanottajan luoman uuden UUIDv4-GUIDin ja viittaa alkuperäiseen itemiin.

Vastaanottaja laskee toimituksen sisällöstä SHA-256-tiivisteen. Tiiviste lasketaan yhdenmukaisesti kanonisoidusta toimitussisällöstä, jotta sisällöltään saman toimituksen uudelleenlähetys voidaan erottaa saman tunnisteen yhteydessä muuttuneesta sisällöstä. Tiivisteen laskenta ja vertailu kuuluvat vastaanottajalle; tuottajan ilmoittamaa tiivistettä ei käytetä vastaanottajan varmennuksen korvikkeena.

Toimitusten käsittelyssä noudatetaan seuraavia sääntöjä:

1. Sama `delivery_id` ja sama kanonisoitu sisältö tarkoittavat saman toimituksen kaksoisvastaanottoa. Se käsitellään idempotentisti eikä synnytä uutta hyväksyttyä toimitusta tai RSS-itemiä.
2. Sama `delivery_id` mutta eri sisältö on tunnisteristiriita. Uusi sisältö hylätään ja ristiriita kirjataan; aiempaa toimitusta tai julkaisua ei korvata.
3. Eri `delivery_id` samalla `run_id`-tunnisteella ja sama sisältö tarkoittavat vaihtoehtoista toimitusta samalle tulokselle. Se voidaan kirjata kaksois-/vaihtoehtoisena toimituksena, mutta siitä ei synny toista julkaisua.
4. Eri `delivery_id` samalla `run_id`-tunnisteella mutta eri sisältö on ristiriita, jos kyseiselle ajolle on jo hyväksytty toimitus. Myöhempi eri sisältö hylätään eikä hyväksyttyä tulosta korvata.
5. Jos aiempi toimitus on hylätty validoinnissa eikä ajon käsittelyä ole vielä päätetty, toinen eri tunnisteella saapuva toimitus voidaan hyväksyä, jos se läpäisee kaikki normaalit hyväksymisehdot. Ajon päättämisen jälkeen uutta vaihtoehtoista varsinaista raporttitoimitusta ei hyväksytä.

Tunnisteiden vastuut pidetään erillään: `run_id` seuraa ajoa, `delivery_id` tuottajan toimitusta ja `attempt_id` vastaanottajan käsittely-yritystä. Tämä malli ei muuta ensimmäisen version sarjallista käsittelyä eikä edellytä rinnakkaisten tuottajien varaus- tai lukitusmekanismia.


### 10.3 Julkaisun ja julkisen saatavuuden varmennus

Julkaisun onnistumista ei päätellä pelkästään siitä, että tallennuspyyntö tai GitHub Actions -vaihe ilmoittaa onnistumisesta. Varmennus erottaa repositorioon tallentamisen ja sisällön julkisen saatavuuden:

- **Git-tallennus:** julkaisun sisältävä commit on syntynyt ja sen sisältö on luettu takaisin tai muuten luotettavasti varmennettu.
- **Tiedostojen eheys:** RSS-item, kanonisen ajotietueen julkaisutiedot ja kyseisen julkaisun tapahtumahistoria vastaavat samaa ajoa ja toimitusta.
- **GUID:** RSS-itemin GUID vastaa ajotietueeseen atomisesti tallennettua GUIDia eikä sama GUID esiinny toisessa julkaistussa itemissä.
- **RSS-sisältö:** julkaistu syöte on kelvollista XML:ää ja sisältää odotetun itemin oikeassa aihekohtaisessa syötteessä.
- **Pages-julkaisutyönkulku:** GitHub Pages -julkaisun valmistuminen tarkistetaan erillisenä vaiheena.
- **Julkinen saatavuus:** julkaistusta Pages-osoitteesta haetaan RSS-syöte ja tarkistetaan, että odotettu item on saatavilla.

Repositorioon julkaiseminen ja julkinen saatavuus ovat eri tiloja. Jos atominen Git-commit ja sen sisältö on varmennettu mutta Pages-julkaisu viivästyy tai epäonnistuu, RSS-item on julkaistu repositorioon, mutta sitä ei vielä ilmoiteta julkisesti saatavilla olevaksi. Pages-ongelma kirjataan erikseen ja sen selvittämistä voidaan jatkaa ilman uuden RSS-itemin luomista tai jo tehdyn julkaisun toistamista.

### 10.4 Vastaanotto- ja julkaisuprosessin hyväksymiskriteerit

Koko prosessin hyväksymistä varten testataan vähintään seuraavat skenaariot:

| Skenaario | Hyväksymisehto |
|---|---|
| Normaali raportti | Toimitus validoidaan ja julkaistaan täsmälleen kerran. |
| Ei raportoitavaa sisältöä | Ajo käsitellään ilman RSS-itemiä eikä sitä merkitä julkaistuksi. |
| Saman toimituksen uudelleenlähetys | Kaksoistoimitus tunnistetaan eikä uutta julkaisua synny. |
| Ristiriitainen toimitus | Ristiriita havaitaan ja aiemmin hyväksytty sisältö säilyy muuttumattomana. |
| Virheellinen toimitus | Toimitus hylätään eikä RSS-syöte muutu. |
| Tilapäinen tekninen virhe | Käsittely voidaan käynnistää uudelleen turvallisesti ilman kaksoisjulkaisua. |
| Epäselvä commit-tulos | Repositorion todellinen tila tarkistetaan ennen mahdollista uutta kirjoitusta. |
| Myöhäinen toimitus | Toimitus liitetään alkuperäiseen ajoon ja kaikki tapahtumat säilyvät jäljitettävinä. |
| Pages-julkaisun viive tai virhe | Repositorioon julkaiseminen ja julkinen saatavuus erotetaan toisistaan. |
| Julkaisun eheys | RSS-item, GUID, ajotietue ja tapahtumahistoria vastaavat toisiaan. |

Hyväksymiskriteereihin kuuluu lisäksi, että jokainen käsittelyvaihe on jäljitettävissä, virheestä jää riittävät tiedot selvittämistä ja palautumista varten, aiemmin hyväksyttyä tai julkaistua sisältöä ei korvata vahingossa eikä julkaisu voi tapahtua pakollisen validoinnin epäonnistuttua. Eri aiheiden RSS-sisältöjä ei saa sekoittaa.

Näiden kriteerien määrittely ei vielä tarkoita testien toteuttamista, tuotantokäyttöönottoa tai toteutussuunnitelman hyväksymistä kokonaisuutena.

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
- erillinen käyttäjäkohtainen tunnistaminen, HTTPS-vastaanottopalvelu ja useiden raportintuottajien erilliset tunnistus- ja käyttöoikeusrajat;
- erilliset lähdekattavuuden ja julkaisuanalytiikan mittaristot;
- laaja järjestelmän terveysanalyysi.

Näitä voidaan arvioida myöhemmin käytännön tarpeen perusteella. Niiden mahdollisuus ei saa monimutkaistaa ensimmäisen version perusratkaisua.

## 14. Toteutuksen ulkopuolelle rajatut asiat

Tässä vaiheessa ei:

- muuteta nykyisten raporttituottajien tai käynnistimien asetuksia, ajastuksia, suoritusvälejä, aikavyöhykkeitä, ohjeita tai kohteita ilman erillistä lupaa;
- aktivoida seurantamoduuleja tai käynnistetä tuotantojulkaisuja;
- toteuteta uutta teknistä arkkitehtuuria ennen vaatimusmäärittelyn ja toteutussuunnitelman hyväksyntää;
- luoda tarpeettomia rinnakkaisia agentteja, tietokantoja tai julkaisupolkuja;
- rakentaa ensimmäiseen versioon erillistä HTTPS-vastaanottopalvelua tai käyttäjäkohtaista tunnistautumista; ChatGPT:n ajastettu tehtävä toimittaa raportit Codex Connectorin kautta; erillistä vastaanotto-GitHub Appia ei käytetä ensimmäisessä versiossa;
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

Seuraavat tekniset ja toiminnalliset yksityiskohdat ovat avoinna. Luettelo on sama vaatimusmäärittelyssä ja toteutussuunnitelmassa, jotta suunnittelun tilanne pysyy yhdenmukaisena.

### A1. Tietomallit ja skeemat

**A1.** **Skeemojen tarkat rakenteet**
   - **A1.1** Määritellään pääskeemojen täydelliset kenttäluettelot, tietotyypit ja pakollisuus.
   - **A1.2** Määritellään kenttäkohtaiset rajat, sallitut arvot ja taulukoiden täsmälliset rajat.
   - **A1.3** Ratkaistaan yhteisten osaskeemojen lopullinen jako, nimet ja uudelleenkäyttö.
   - **A1.4** Määritellään skeemojen väliset viittaukset ja niiden eheyden tarkistus.
   - **A1.5** Täsmennetään rakenteellisen ja toiminnallisen validoinnin työnjako, virheraportointi ja validointikoodin vastuut.
   - *Rajaus:* skeemahakemiston jako, JSON Schema -versio ja yleiset sulkevuusperiaatteet on päätetty.

**A2.** **Laaduntarkistusten parametrit**
   - **A2.1** Luetellaan kunkin tarkistuksen tarvitsemat parametrit ja niiden tarkoitus.
   - **A2.2** Määritellään parametrien nimet, tyypit, pakollisuus, rajat ja sallitut arvot.
   - **A2.3** Määritellään tarkistuskohtaiset parametriskeemat ja niiden validointiehdot.
   - **A2.4** Päätetään tarkistuskohtaisten oletusarvojen täsmälliset arvot.
   - **A2.5** Määritellään keskinäisten riippuvuuksien ja virheellisten yhdistelmien käsittely.
   - *Rajaus:* parameters on aina objekti, asetukseton arvo on tyhjä objekti ja tuntemattomat parametrit hylätään.

**A3.** **Raportoitavien havaintojen kategoriat**
   - **A3.1** Tunnistetaan kunkin tehtävätyypin tarvitsemat kategoriat.
   - **A3.2** Määritellään tehtävätyyppikohtaiset pysyvät kategoriatunnisteet.
   - **A3.3** Määritellään kategorioiden nimet, kuvaukset ja käyttörajat.
   - **A3.4** Määritellään tuntemattomien tai vanhentuneiden kategorioiden käsittely.
   - **A3.5** Määritellään kategorioiden muuttamisen ja käytöstä poistamisen säännöt.
   - *Rajaus:* yhteistä kaikkien tehtävätyyppien luokittelua ei muodosteta.

**A4.** **Tiedostoroolien parametrit**
   - **A4.1** Luetteloidaan toimituspaketin tiedostoroolit ja niiden tarkoitukset.
   - **A4.2** Määritellään roolikohtaiset parametrit, tyypit ja pakollisuus.
   - **A4.3** Määritellään roolikohtaiset parametriskeemat ja oletusarvot.
   - **A4.4** Määritellään roolien riippuvuudet ja tehtävätyyppikohtaiset rajoitukset.
   - **A4.5** Määritellään puuttuvien, toistuvien ja ristiriitaisten roolien käsittely.
   - *Rajaus:* parameters on aina objekti ja tuntemattomat parametrit hylätään.

**A5.** **Toimitusmetatietojen täydentäminen**
   - **A5.1** Käydään kuusi hyväksyttyä tietoryhmää läpi ja tunnistetaan jäljellä olevat täsmennystarpeet.
   - **A5.2** Määritellään lähde-, kanava- ja tarkistusyritystietojen kentät, tyypit ja viittaukset.
   - **A5.3** Määritellään havaintoyhteenvedon kentät ja niiden suhde tehtävätyypin kategorioihin.
   - **A5.4** Täsmennetään valinnaisten tuottajatietojen sisältö ja rajat.
   - **A5.5** Määritellään kenttien pakollisuus, tyhjien arvojen käsittely ja ryhmien johdonmukaisuussäännöt.
   - **A5.6** Varmistetaan tuottajan ja vastaanottajan tietojen sekä tunnisteiden selkeä erottelu.
   - *Rajaus:* kuusi tietoryhmää sekä producer-ryhmän perusrakenne, valinnaisuus ja producer_type-arvot on päätetty.

**A6.** **Vastaanottajan ajotietomallit**
   - **A6.1** Määritellään run.json-tietueen kentät, tyypit, pakollisuus ja sallitut arvot.
   - **A6.2** Määritellään ajon, tuottajan tuloksen, vastaanoton ja julkaisun tilaluokat ja siirtymät.
   - **A6.3** Määritellään events.jsonl-tapahtumien täydellinen tapahtumatyyppiluettelo.
   - **A6.4** Määritellään tapahtumatyyppien details-rakenteet ja pakolliset tiedot.
   - **A6.5** Määritellään tietueiden ja toimitusmetatietojen viittauskentät.
   - **A6.6** Määritellään tapahtumien järjestys-, aikaleima-, yksilöllisyys- ja append-only-säännöt.
   - **A6.7** Määritellään puuttuvien, ristiriitaisten ja tuntemattomiin toimituksiin viittaavien tietojen käsittely.

### A2. Lähderekisteri ja lähdetilastot

**A7.** **Rekisterin ulkopuolisten lähteiden ehdotukset**
   - **A7.1** Määritellään ehdotustietueen kentät, tyypit ja pakollisuus.
   - **A7.2** Määritellään lähde- ja kanavaehdotusten väliset viittaukset.
   - **A7.3** Täsmennetään alkuperä-, löytämis- ja perustelutietojen sisältö.
   - **A7.4** Määritellään skeema-, URL- ja duplikaattitarkistusten ehdot.
   - **A7.5** Täsmennetään elinkaaren tilasiirtymät, hyväksyntä, hylkäys ja jäljitettävyys.
   - **A7.6** Määritellään hyväksytyn ehdotuksen siirto rekisteriin ja rekisterirevision päivitys.
   - **A7.7** Arvioidaan myöhemmän käyttöliittymän tarve; ensimmäisen version GitHub-käsittely säilyy lähtökohtana.

**A8.** **Lähdekohtaiset tilastot**
   - **A8.1** Määritellään tilastotietueen kentät ja suhde sisältökanavien tarkistusyrityksiin.
   - **A8.2** Määritellään tilastojen laskenta ja päivitys kanonisesta ajohistoriasta.
   - **A8.3** Täsmennetään 30 ja 90 päivän sekä koko historian tunnuslukujen laskentasäännöt.
   - **A8.4** Määritellään virheluokkien ryhmittely ja onnistumisen laskenta.
   - **A8.5** Täsmennetään toistuvien epäonnistumisten huomautusten nostokriteerit.
   - **A8.6** Määritellään tilastojen ja huomautusten esitys Valvomossa sekä puuttuvan aineiston ilmaisu.
   - **A8.7** Määritellään laskennan oikeellisuuden testaus.
   - *Rajaus:* tilastojen perusperiaatteet, tarkastelujaksot ja ylläpitäjän arvioitavat huomautukset on päätetty.

### A3. Integraatiot ja ajonhallinta

**A9.** **Vastaanottoprosessin tekninen viimeistely ja käyttöönotto**
   - *Rajaus:* RSS-itemin täydellinen elementtirakenne ja järjestys (9.1), yhden item-elementin toimitus, link-elementin kielto, vastaanottajan UUIDv4-GUID, atominen tallennus ja GUIDin idempotentti uudelleenkäyttö sekä raportin HTML-perusrakenne ja aikavälin ulkopuolisten merkittävien täydennysten esityssäännöt (9.3), toimituspaketin rajapinta (9.4), vastaanoton validointijärjestys ja hyväksymisehdot (9.5) sekä vastaanoton ja julkaisun työnkulku, tilat, vastuut, atominen tallennus ja myöhäisten toimitusten kirjaaminen (9.6) on päätetty. Sisällöllinen laaduntarkistus tehdään jokaisella seurantakierroksella; erillistä laaduntarkistusajoa ei ole.

**A10.** **Instanssirepositorion ja julkaisusuojauksen käyttöönotto**
   - *Rajaus:* A10.1:n hakemistorakenteen, syöteidentiteetin ja Pages-julkaisun periaatteet on päätetty.
   - **A10.2** Määritellään vastaanotto- ja julkaisuhaarojen vastuut ja sallittu tiedonsiirto.
   - **A10.3** Määritellään main-haaran suojaussäännöt, pakolliset tarkistukset ja poikkeusmenettely.
   - **A10.4** Varmennetaan Codex Connectorin repositoriotasoisten oikeuksien vaikutus haarasuojaukseen.
   - **A10.5** Määritellään Pages-julkaisun käynnistys, virheellisen julkaisun esto ja palautus.
   - **A10.6** Määritellään käyttöönoton oikeus- ja suojaustestit.
   - *Rajaus:* ensimmäisessä versiossa ei käytetä erillistä vastaanotto-GitHub Appia.

**A11.** **Ajojen käynnistäminen**
   - **A11.1** Määritellään 15 minuutin yhteisen tarkistusvälin ajastustapa ja GitHub Actionsin viiveiden käsittely.
   - **A11.2** Määritellään manuaalisen käynnistyksen käyttäytyminen ja yhteiset käsittelysäännöt.
   - **A11.3** Määritellään aihekohtaisten erääntymisten laskenta, aikavyöhyke ja aikavälirajat.
   - **A11.4** Määritellään enintään yhden erääntyneen aiheen valinta ja valinnan reiluus.
   - **A11.5** Määritellään päällekkäisten käynnistysten esto ja sarjallisuuden tekninen toteutus.
   - **A11.6** Määritellään käynnistysvirheiden ja väliin jääneiden käynnistysten havaitseminen ja kirjaaminen.
   - *Rajaus:* erillistä laaduntarkistusajoa ei käynnistetä.

**A12.** **Jonon ja uudelleenyritysten tarkat rajat**
   - **A12.1** Määritellään tehtävän muodostuksen, tuottajan suorituksen, vastaanoton ja julkaisun aikakatkaisut.
   - **A12.2** Määritellään uudelleenyritysten enimmäismäärät vaiheittain ja virheluokittain.
   - **A12.3** Määritellään odotusajat, mahdollinen kasvava viive ja enimmäisodotusaika.
   - **A12.4** Määritellään pysyvien, tilapäisten ja käyttäjän toimenpidettä vaativien virheiden käsittely.
   - **A12.5** Määritellään epäonnistuneen aiheen uusi jonotus ja vaikutus muiden aiheiden etenemiseen.
   - **A12.6** Määritellään keskeytyneen tehtävän tunnistaminen, tilan palautus ja turvallinen jatkaminen.
   - **A12.7** Määritellään manuaalisen uudelleenyrityksen oikeudet, vaikutukset ja jäljitettävyys.

**A13.** **Toimituspakettien säilytys**
   - **A13.1** Määritellään vastaanottohaaran alkuperäisten pakettien säilytysajat.
   - **A13.2** Määritellään hyväksyttyjen, hylättyjen ja keskeneräisten pakettien säilytyserot.
   - **A13.3** Määritellään siivouksen käynnistysehdot, ajastus ja poistoperusteet.
   - **A13.4** Määritellään keskeneräisten ja palautettavien ajojen aineiston suojaaminen.
   - **A13.5** Määritellään auditointi-, palautus- ja poikkeustilanteiden säilytystarpeet.
   - **A13.6** Määritellään tallennustilan seuranta ja toiminta säilytysrajojen ylittyessä.

### A4. Raportintekijä ja käyttöliittymät

**A14.** **Yhteinen raportintekijän perusprompti**
   - **A14.1** Määritellään promptin rakenne ja yleiset vastuut suhteessa tehtäväpyyntöön.
   - **A14.2** Määritellään tehtäväpyynnön, ohjeiden ja rakenteisten syötteiden lukemisjärjestys.
   - **A14.3** Täsmennetään lähteiden käyttöä, epävarmuutta, lähteistämistä ja toimituspaketin muodostamista koskevat ohjeet.
   - **A14.4** Määritellään puuttuvien tietojen, ristiriitaisten ohjeiden ja validointivirheiden käsittely.
   - **A14.5** Määritellään versionhallinta, revisioviittaus ja yhteensopivuusperiaatteet.
   - **A14.6** Määritellään testitapaukset, arviointikriteerit ja sovittaminen tuottajaintegraatioon.

**A15.** **Valvomon toteutus**
   - **A15.1** Määritellään yleiskuvan tietosisältö, järjestys, päivittyminen ja poikkeamat.
   - **A15.2** Määritellään aihelistan kentät, suodatus, järjestäminen ja tilan esitys.
   - **A15.3** Määritellään ajohistorian suodatus, tapahtumien tarkastelu ja virheiden esitys.
   - **A15.4** Määritellään lähdekattavuuden ja lähdetilastojen sijoittuminen Valvomoon.
   - **A15.5** Määritellään navigointi, URL-rakenne, tyhjät, lataus- ja virhetilat.
   - **A15.6** Määritellään tietojen päivitystapa ja riippuvuus instanssin julkisista tiedostoista.
   - **A15.7** Määritellään saavutettavuus-, responsiivisuus- ja käytettävyyskriteerit sekä testaus.

**A16.** **Julkisten käyttöliittymien tietoturvatarkistukset**
   - **A16.1** Luetteloidaan julkisiin tiedostoihin ja rajapintoihin päätyvät tietolähteet.
   - **A16.2** Määritellään salaisuuksien, käyttöoikeustunnusten ja yksityisten tietojen tunnistusmenetelmät.
   - **A16.3** Määritellään tarkistusten kattavuus lähdekoodille, määrityksille, ajotiedoille ja julkaistulle sisällölle.
   - **A16.4** Määritellään löydösten vakavuudet ja ehdot, joilla julkaisu estetään.
   - **A16.5** Määritellään väärien positiivisten käsittely, poikkeusten hyväksyntä ja auditointijälki.
   - **A16.6** Määritellään CI- ja julkaisuprosessin tarkistukset sekä niiden testaus.

### A5. Historiatiedot, toimitusmalli ja myöhemmät käyttöoikeudet

**A17.** **Historiatietojen säilytys**
   - **A17.1** Määritellään ajotietueiden ja tapahtumahistorioiden säilytysajat.
   - **A17.2** Määritellään lokien, virhetietojen ja diagnostiikka-aineistojen säilytysajat.
   - **A17.3** Määritellään väliaineistojen suhde toimituspakettien erilliseen säilytyspolitiikkaan.
   - **A17.4** Määritellään arkistointi, siivous, poisto ja mahdollinen anonymisointi.
   - **A17.5** Määritellään historian palautus, tarkastelu ja raportointikäyttö säilytysajan aikana.
   - **A17.6** Määritellään poistojen jäljitettävyys ja säilytyspoikkeukset.

**A18.** **Ohjelmiston ja instanssin toimitusmalli**
   - **A18.1** Vahvistetaan ohjelmisto- ja instanssirepositorion vastuut ja hakemistorakenteet.
   - **A18.2** Määritellään jakelukanava ja instanssin käyttämän ohjelmistoversion kiinnitystapa.
   - **A18.3** Määritellään päivitysten hyväksyntä, käyttöönotto, palautus ja yhteensopivuuden tarkistus.
   - **A18.4** Määritellään määritysten, aineistojen ja raporttipakettien viittaus- ja siirtomalli.
   - **A18.5** Määritellään ohjelmisto-, skeema- ja instanssirevisioiden yhteensopivuussäännöt.
   - **A18.6** Määritellään uuden instanssin perustamisen, päivittämisen ja palauttamisen käytännöt.

**A19.** **Myöhempi käyttöoikeuksien tekninen toteutus**
   - **A19.1** Tunnistetaan luottamukselliset tietoluokat ja tilanteet, joissa julkinen malli ei riitä.
   - **A19.2** Määritellään julkisen ja rajatun tiedon erottelu repositorioissa, tiedostoissa ja käyttöliittymissä.
   - **A19.3** Arvioidaan tunnistautumisen, roolien ja käyttöoikeuksien hallinnan tarpeet.
   - **A19.4** Määritellään salaisuuksien säilytys suoritusympäristössä erillään julkisesta instanssidatasta.
   - **A19.5** Määritellään auditointi, oikeuksien muutokset ja väärinkäytösten havaitseminen.
   - **A19.6** Rajataan myöhemmät ratkaisut niin, etteivät ne monimutkaista ensimmäistä versiota tarpeettomasti.
   - *Rajaus:* tämä ei ole ensimmäisen version vaatimus.

## 17. Raportintekijän yhteinen perusprompti ja tuottajakohtaiset ohjeet

Yhteinen raportintekijän perusprompti kuuluu jaettavaan ohjelmistoon ja on versionhallittu osa käytettyä `software_revision`-versiota. Tehtäväpyyntö viittaa siihen `instructions`-taulukon ensimmäisenä ohjeena. Perusprompti määrittelee raportintekijän yleiset vastuut ja rajat, tehtäväpyynnön lukemisen, ohjeiden noudattamisen, lähdeaineiston käsittelyn, epävarmuuden ilmaisemisen, raportin muodostamisen ja toimituspaketin vaatimusten noudattamisen.

Perusprompti ei sisällä aihekohtaisia uutis- tai sisältövaatimuksia eikä korvaa tehtävätyypin, profiilien tai aiheen ohjeita. Näiden ohjeiden järjestys on: yhteinen perusprompti, tehtävätyypin ohje, profiiliohjeet aihekohtaisessa järjestyksessä ja aihekohtainen ohje. Raportintekijä käyttää vain tehtäväpyynnön ilmoittamissa muuttumattomissa revisioissa olevia ohjeita eikä hae niiden uusimpia versioita kesken ajon.

Peruspromptin tulee ohjata raportintekijää käsittelemään lähdeaineistoa tietona eikä järjestelmäohjeina, olemaan keksimättä puuttuvia tietoja, säilyttämään tehtäväpyynnön tunnisteet ja asetukset muuttumattomina sekä ilmoittamaan puutteet ja epäonnistumiset rehellisesti. Se määrittelee myös lähdekohtaisten avausyritysten tulosten raportoinnin niin, että todellinen avaamisen onnistuminen, epäonnistumisen syy ja sisällön käyttökelpoisuus pysyvät erillisinä tietoina.

Tuottajakohtaiset toteutusohjeet ja integraation tekniset asetukset voivat täydentää yhteistä peruspromptia, mutta ne eivät saa muuttaa yhteistä tietosopimusta, tehtäväpyynnön määrityksiä tai vastaanottavan järjestelmän julkaisuehtoja. Tuottajakohtaiset tekniset integraatio-ohjeet, ajastukset ja käyttöönottotiedot dokumentoidaan erikseen.

## 18. Muutosloki

- **0.12.69 – 25.11.2026:** täsmennettiin vastaanottohaaran säilytysperiaatetta: kaikki vastaanotetut toimituspaketit, myös hylätyt, säilytetään alkuperäisinä vastaanottohaarassa; vain hyväksytyt toimituspaketit kopioidaan lisäksi `main`-haaraan. Valvomon tulee näyttää myös hylättyjen toimitusten tilat, validointitulokset ja virhetiedot; niiden tekninen lukutapa ja esitysmuoto jätettiin A10:n jatkosuunnitteluun. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.12.68 – 25.11.2026:** hyväksyttiin RSS-syötteen identiteetin muodostaminen aiheen ja tehtävätyypin yhdistelmästä sekä aihe-/tehtävätyyppikohtainen hakemistorakenne `feeds/{topic_id}/{task_type_id}.xml`. Hyväksyttiin Pages-sivuston muodostaminen erillisessä rakennusvaiheessa vain hyväksytystä sisällöstä sekä hyväksytyn alkuperäisen toimituspaketin säilyttäminen myös `main`-haarassa auditointia varten. Synkronoitiin avoimien suunnittelukysymysten tunnisteet A-etuliitteisiksi, poistettiin ratkaistu A10.1 avoimista tehtävistä ja yhdenmukaistettiin luettelot toteutussuunnitelman kanssa. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.12.67 – 25.11.2026:** hyväksyttiin idempotenssin ja virhetilanteiden käsittelyperiaatteet, julkaisun repositoriotason ja julkisen saatavuuden erillinen varmennus sekä vastaanotto- ja julkaisuprosessin päästä päähän -hyväksymiskriteerit. Avoimien kohtien luettelosta poistettiin jo aiemmin hyväksytty 9.3 sekä nyt hyväksytyt 9.7–9.9. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.12.66 – 25.11.2026:** hyväksyttiin vastaanoton ja julkaisun työnkulun tilat ja poikkeustilat, vastaanotto- ja julkaisutyönkulkujen vastuut, julkaisun atomisen Git-commitin rajaus sekä myöhäisten toimitusten erillinen tapahtumakirjaus. Kohta 9.6 poistettiin avoimista kohdista. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.12.65 – 25.11.2026:** hyväksyttiin vastaanoton validoinnin tarkistusjärjestys ja keskeyttämisehdot, tunniste- ja revisiovastaavuudet, tiedostoluettelon rajaus (metadata.json ei sisälly omaan luetteloonsa), eheystarkistukset, XML/HTML/RSS-turvallisuus, keskinäiset viittaukset, virheiden pysyvyys ja uudelleenyritysten periaatteet sekä hyväksymisen raja. Korjattiin 9.4-päätöksen kanssa ristiriitainen vanha kuvaus raporttisisällön erillisistä tiedostoista. Kohta 9.5 poistettiin avoimista kohdista. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.12.64 – 24.11.2026:** hyväksyttiin toimituspaketin rajapinta: `metadata.json` kuvaa toimituksen ja sen tiedostot, `item.xml` sisältää koko raportin RSS-itemin `<content:encoded>`-elementissä eikä erillistä HTML-raporttitiedostoa toimiteta. Täsmennettiin tiedostojen rooli- ja polkuyksilöinti sekä korjaus- ja täydennysitemien suhde alkuperäiseen UUIDv4-GUIDiin; alkuperäistä julkaisua ei muuteta. Kohta 9.4 poistettiin avoimien kohtien luettelosta. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.12.63 – 24.11.2026:** hyväksyttiin raportin yhteinen HTML-perusrakenne, otsikkohierarkia, seuranta-aikavälin ja lähdeviitteiden esittäminen, saavutettavuuden periaatteet sekä aihekohtaisen sisältövaihtelun rajat. Sallittiin lisäksi merkittävien aikavälin ulkopuolisten uutisten ja aiemmasta raportista puuttuneiden olennaisten havaintojen erillinen, selvästi ajoitettu täydennysosio muuttamatta varsinaista seuranta-aikaväliä. Kohta 9.3 poistettiin avoimien kohtien luettelosta. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.12.62 – 24.11.2026:** hyväksyttiin kohdan 9.2 XML- ja HTML-yhteensopivuus: XML-kirjastolla muodostaminen, CDATA-käytäntö ja turvallinen osiointi, sallittujen HTML-elementtien ja attribuuttien lista, HTML:n hylkääminen ilman automaattista korjausta sekä kuvien rajaaminen jatkokehitykseen. Kohta 9.2 poistettiin avoimien kohtien luettelosta. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.12.61 – 24.11.2026:** hyväksyttiin RSS-itemin täydellinen elementtirakenne ja vakiojärjestys: `<title>`, `<guid isPermaLink="false">`, `<pubDate>`, valinnainen `<description>` ja `<content:encoded>`. Rajattiin muut RSS-elementit ja ylimääräiset attribuutit pois sekä määriteltiin `content`-nimiavaruuden ilmoittaminen item-elementissä. Kohta 9.1 poistettiin avoimien kohtien luettelosta; HTML:n yksityiskohtainen rakenne jäi kohtaan 9.3. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.12.59 – 24.11.2026:** päivitettiin avoimien teknisten asioiden luettelo vastaamaan 24.11. hyväksyttyjä RSS-itemin sisältösopimuksen ja UUIDv4-GUIDin ratkaisuja. Poistettiin GUIDin muodostus avoimista asioista ja rajattiin jäljellä oleva työ RSS-elementtien pakollisuuteen, HTML-rakenteen tarkempaan perusmuotoon, työnkulkujen toteutukseen, uudelleenyritysrajoihin ja käyttöönoton varmennuksiin. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.12.54 – 24.11.2026:** täsmennettiin RSS-julkaisemisen sääntöjä: toimitustiedosto sisältää yhden `<item>`-elementin, `<link>`-elementin puuttuminen on kiinteä sääntö ja lähteet linkitetään raportin sisällössä. Rajattiin vastaanottoprosessin avoin RSS-kohta jäljellä oleviin HTML-, GUID- ja elementtikohtaisiin yksityiskohtiin.

- **0.12.53 – 24.11.2026:** täsmennettiin RSS-itemin toimitusmuoto yhdeksi `<item>`-elementiksi ilman `<link>`-elementtiä ja määriteltiin lähteiden linkitys raporttisisällössä. Päätettiin aloittaa toteutus puhtaalta pöydältä käyttämättä vanhaa arkistoitua toteutusta; poistettiin vanhaan toteutukseen liittyvä inventaario- ja siirtymäkysymys avoimista suunnittelutehtävistä.

- **0.12.51 – 24.11.2026:** yhdenmukaistettiin avoimien suunnittelukysymysten koko luettelo täsmälleen toteutussuunnitelman kanssa. Päivitettiin erityisesti julkaisusuojauksen avoin kohta vastaamaan Codex Connector -mallia.

- **0.12.51 – 24.11.2026:** synkronoitiin avoimet vastaanottoa ja käyttöoikeuksia koskevat suunnittelukysymykset Codex Connector -toimitusmalliin. Poistettiin vanhentunut GitHub App -pohjaisen ensimmäisen version toimituskanavan kuvaus myös toteutuksen ulkopuolelle rajatuista asioista.

- **0.12.51 – 24.11.2026:** yhdenmukaistettiin repositorioiden dokumentoidut hakemistonimet englanninkielisiksi. Toimituspakettien poluksi määriteltiin `deliveries/{run_id}/{delivery_id}/`; samaa nimeämiskäytäntöä sovelletaan ohjelmisto- ja instanssirepositorion hakemistoihin. Repositorioiden todellista sisältöä tai toteutusta ei muutettu.

- **0.12.48 – 24.11.2026:** hyväksyttiin ensimmäisen version toimituskanavaksi ChatGPT:n ajastettu tehtävä ja Codex Connector. Käytännön testi vahvisti toimituksen erilliseen vastaanottohaaraan muuttamatta `main`-haaraa. Määriteltiin vastaanottohaaraksi `raportit-inbox` ja toimituspaketin polku; vastaanotto ja julkaisu erotettiin. Täsmennettiin, että Codex Connectorin oikeudet eivät rajaudu haaraan ja `main` on suojattava erikseen. Erillistä vastaanotto-GitHub Appia ei käytetä ensimmäisessä versiossa; käyttäjä on poistanut aiemman Appin. Toteutusta tai automaatioita ei muutettu.

- **0.12.47 – 24.11.2026:** hyväksyttiin ensimmäisen vaiheen julkinen instanssirepositorio ja GitHub Pages -julkaisu, vastaanotto- ja julkaisuhaarojen erottaminen sekä erillinen vain instanssirepoon asennettava GitHub App (Metadata read, Contents read/write). Täsmennettiin, että koko instanssirepon sisältö ja historia ovat julkisia ja että Contents-kirjoitusoikeus on repositoriotasoinen; julkaisuhaaran suojaus on toteutettava ja varmennettava erikseen. Toteutusta, repositoriota, Appia tai automaatioita ei luotu tai muutettu.

- **0.12.46 – 24.11.2026:** yhdenmukaistettiin vastaanottorajapinnan avoimen suunnittelukohdan sanamuoto toteutussuunnitelman kanssa ja korjattiin `main`-haaran nimen kirjoitusasu. Aiemmin hyväksyttyjä teknisiä ratkaisuja ei muutettu.

- **0.12.45 – 24.11.2026:** hyväksyttiin ensimmäisen version toimituskanavaksi GitHub Appin kautta tehtävä Git push erilliseen vastaanottohaaraan. Rajattiin erillinen HTTPS-vastaanottopalvelu ja käyttäjäkohtainen tunnistaminen ensimmäisen version ulkopuolelle. Täsmennettiin GitHub Appin teknisten oikeuksien tarkistaminen, vastaanoton ja hyväksymisen erottaminen, GitHub Actions -käsittely sekä myöhempiin versioihin jätettävät laajemmat tunnistus- ja integraatiomallit. Toteutusta, skeemoja, testejä tai automaatioita ei luotu tai muutettu.

- **0.12.44 – 24.11.2026:** hyväksyttiin rekisterin ulkopuolisten lähteiden ehdotusten lähdekohtainen rakenne, erillinen tallennuspolku, elinkaaren tilat, validointi ja ensimmäisen version GitHub-pohjainen ylläpitäjäkäsittely. Täsmennettiin lähdekanavakohtaisten avausyritysten tilastotietue, virheluokat, 30/90 päivän ja koko historian tarkastelujaksot, Valvomon tunnusluvut sekä toistuvien epäonnistumisten alustava nostokriteeri. Lähteiden automaattinen poistaminen tai käytöstä poistaminen tilastojen perusteella kiellettiin edelleen. Toteutusta, skeemoja, testejä tai automaatioita ei luotu tai muutettu.

- **0.12.43 – 24.11.2026:** hyväksyttiin tietomalli- ja skeematyön kuuden avoimen kohdan ehdotuspaketti: skeemahakemiston nelijako (`common`, `configuration`, `task`, `delivery`, `receiver`), tietomallikohtaiset pääskeemat ja tarkemmat validointiperiaatteet; raportoitavien havaintojen tehtävätyyppikohtaiset kategoriat; tiedostoroolien `parameters`-objektin yleissäännöt; valinnaisen `producer`-ryhmän rakenne; sekä vastaanottajan `run.json`- ja `events.jsonl`-tietomallien perusrakenne, tunnisteiden vastuut ja append-only-tapahtumahistorian säännöt. Aiemmin hyväksyttyjä laaduntarkistusten parametriperiaatteita täsmennettiin avoimien kohtien kuvauksessa. Skeemoja, toteutusta, testejä tai automaatioita ei luotu tai muutettu.

- **0.12.42 – 24.11.2026:** synkronoitiin avoimien suunnittelukohtien luettelo toteutussuunnitelman kanssa. Yhdistetty luettelo kattaa tietomallit ja skeemat, lähderekisterin, lähdetilastot, integraatiot, ajonhallinnan, raportintekijän, käyttöliittymät, siirtymän ja käyttöönoton. Aiemmin eri dokumenteissa erillisinä esitetyt aiheet yhdenmukaistettiin.

- **0.12.41 – 24.11.2026:** hyväksyttiin raportoitavien havaintojen erillinen tietomalli ja erottaminen laaduntarkistusten havainnoista, toimituskohtaiset tunnisteet, tehtävätyyppikohtaiset kategoriat, lähde- ja kanavaviittaukset sekä valinnainen `findings.json`. Hyväksyttiin tiedostoroolien pysyvät tunnisteet, tulostilakohtainen `required` / `optional` / `forbidden`-malli, toimitettujen tiedostojen luettelo, pakolliset tiedostokoot ja SHA-256-tiivisteet, polkujen turvallisuussäännöt, tulostilojen toimitusvaatimukset sekä vastaanottajan validointivaiheet ja virheluokat. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.12.40 – 24.11.2026:** hyväksyttiin laaduntarkistusten `parameters`-objektin yleiset tietotyyppi- ja validointisäännöt, tyhjän objektin käyttö asetuksettomassa tarkistuksessa, tarkistuskohtaiset skeemat ja oletusarvot, tuntemattomien parametrien hylkääminen, tunnisteiden yksilöllisyys ja pysyvyys, tarkistusmäärittelyn versioinnin sitominen tehtävätyypin määrityksen revisioon, pakollisten ja valinnaisten tarkistusten kirjaamissäännöt sekä määrittelyn, suorittamisen ja validoinnin vastuut. Hyväksyttiin myös toimituspaketin tehtävätyyppikohtainen sisältö, metatietojen ja sisältötiedostojen erottaminen, suhteelliset tiedostoviittaukset sekä vastaanottajan eheysvalidointi ilman tuottajan aineiston muuttamista. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.
- **0.12.39 – 24.11.2026:** hyväksyttiin tietomalli- ja skeematyön yhteiset ratkaisut: skeemojen nelijako, yhteisten osaskeemojen periaate, laaduntarkistusten määritystietueen kentät (`check_id`, `name`, `description`, `required`, `parameters`), tarkistustunnisteiden pysyvyys- ja uudelleenkäyttösäännöt sekä laaduntarkistusten toiminnallisen validoinnin erottaminen rakenteellisesta skeemavalidoinnista. Täsmennettiin, että skeemojen automaattiset testit kuuluvat CI-tarkistuksiin. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.
- **0.12.38 – 24.11.2026:** yhdenmukaistettiin avoimien suunnittelukysymysten luettelo hyväksyttyjen päätösten kanssa. Poistettiin jo ratkaistu lähderekisterin ulkopuolinen lähdehaku avoimista kysymyksistä ja täsmennettiin, mitkä laaduntarkistusten tietomallin osat on päätetty ja mitkä skeema- ja määritysrakenteet ovat yhä avoinna. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.
- **0.12.37 – 24.11.2026:** hyväksyttiin yksittäisen laaduntarkistuksen ajokohtaisen tietueen kentät (`check_id`, `result`, `checked_at`, `findings`, `notes`, `reason`), viisi tulosluokkaa, havaintojen vakavuusluokat ja kirjaamissäännöt. Täsmennettiin vaadittujen tarkistusten kattavuus sekä tehtävätyypin määrityksen, raportintuottajan ja vastaanottajan vastuut. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.
- **0.12.36 – 24.11.2026:** hyväksyttiin, että yksittäiset laaduntarkistukset määritellään tehtävätyypin määrityksessä ja niiden ajokohtaiset tulokset tallennetaan tuottajan toimitusmetatietoihin. Tarkistusten määrittely erotetaan siten toteutuneiden tulosten kirjaamisesta; tarkat kentät ja tulosarvot jätettiin avoimiksi. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.
- **0.12.35 – 23.11.2026:** hyväksyttiin Havainnot ja laadunvarmistus -tietoryhmän kahden osan rakenne: raportoitavien havaintojen yhteenveto sekä raportintuottajan tekemien laaduntarkistusten tulokset. Rajattiin tuottajan tulostila kolmanteen tietoryhmään ja vastaanottajan validointi-, hyväksyntä- ja julkaisutilat tämän ryhmän ulkopuolelle. Tehtävätyypin määritys määrittelee vaadittavat laaduntarkistukset; tarkat kentät ja tulosarvot jäivät avoimiksi. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.12.34 – 23.11.2026:** hyväksyttiin kanavakohtaisen tarkistusyrityksen vähimmäistiedoiksi ajankohta, tulos, tieto uuden tai tehtävän kannalta relevantin sisällön löytymisestä, saatavilla oleva tekninen tulos sekä virhe- ja huomiotiedot. Erotettiin teknisen tarkistuksen onnistuminen sisällöllisestä tuloksesta; onnistunut tarkistus ilman uutta sisältöä ei ole epäonnistuminen. Tarkka kenttärakenne ja sallitut tulosarvot jäivät avoimiksi. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.12.33 – 23.11.2026:** hyväksyttiin Lähdetarkistukset-ryhmän alustava kolmen osan rakenne: käytetyt lähteet, käytetyt sisältökanavat sekä kanavakohtaiset tarkistusyritykset tuloksineen. Rekisterin ulkopuoliset lähteet kuvataan erillisinä toimituskohtaisina lähteinä. Yksittäisten kenttien ja tarkkojen tulosluokkien määrittely jätettiin jatkokeskusteluun. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.12.32 – 23.11.2026:** hyväksyttiin Tuottajan tulos -ryhmän kentiksi `status`, `started_at` ja `completed_at`. Määriteltiin tuottajan tulostilan sallitut arvot, aikaleimojen esitystapa ja se, ettei vastaanottaja päättele puuttuvasta toimituksesta tuottajan tulosta.
- **0.12.31 – 23.11.2026:** hyväksyttiin toimitusmetatietojen Tehtävän kuvaus -ryhmän ainoaksi omaksi kentäksi `period`, jonka rakenne vastaa tehtäväpyynnön `from`- ja `to`-arvoja. `topic_id` ja `task_type` säilyvät vain Tunnisteet ja versiot -ryhmässä, eikä niitä kopioida toiseen ryhmään.
- **0.12.30 – 23.11.2026:** hyväksyttiin tuottajan toimitusmetatietojen tunnisteet ja versiot -ryhmän kentät: `schema_version`, `run_id`, `delivery_id`, `topic_id`, `task_type`, `software_revision` ja `instance_revision`. Täsmennettiin tunnisteiden omistajuus sekä se, ettei vastaanottajan `attempt_id` kuulu tuottajan metatietoihin. Muut tietoryhmät ja niiden kentät jäivät avoimiksi. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.12.29 – 23.11.2026:** hyväksyttiin tuottajan toimitusmetatietojen kuusi sisällöllistä tietoryhmää: tunnisteet ja versiot, tehtävän kuvaus, tuottajan tulos, lähdetarkistukset, havainnot ja laadunvarmistus sekä valinnaiset tuottajan tiedot. Ryhmittely ei vielä lukitse yksittäisiä kenttiä tai niiden pakollisuutta. Vastaanottajan käsittelytilat rajattiin edelleen tuottajan metatietojen ulkopuolelle. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.12.28 – 23.11.2026:** hyväksyttiin tuottajan toimitusmetatietojen, vastaanottajan kanonisen ajotietueen ja vastaanottajan append-only-tapahtumahistorian erottaminen kolmeksi toisiinsa viitatuksi tietokokonaisuudeksi. Täsmennettiin, että tarkat kentät, tapahtumatyypit ja viittaukset ratkaistaan myöhemmässä teknisessä suunnittelussa. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.12.27 – 23.11.2026:** hyväksyttiin ajon, tuottajan toimituksen ja vastaanottajan käsittely-yrityksen erilliset tunnisteet (`run_id`, `delivery_id`, `attempt_id`), alkuperäisen RSS-GUIDin deterministinen muodostaminen `run_id`-tunnisteesta (myöhemmin korvattu versiolla 0.12.58 vastaanottajan luomalla UUIDv4-tunnisteella), vastaanottajan laskema SHA-256-tiiviste kanonisoidusta toimitussisällöstä sekä kaksois- ja ristiriitaisten toimitusten käsittelysäännöt. Määriteltiin myös, milloin validoinnissa hylätyn toimituksen voi korvata toisella toimituksella. Toteutusta, skeemoja tai automaatioita ei muutettu.
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

- **0.12.13 – 22.11.2026:** kirjattiin tehtävätyypin, määritysprofiilien ja aihekohtaisten määritysten kolmitasoinen malli, niiden yhdistämisjärjestys, suojatut asetukset, skeemavalidointi, muuttumaton resolved_config-snapshot sekä virheellisten määritysten käsittely. Profiilien rekursiiviset riippuvuudet ja dynaamiset yhdistämismekanismit rajattiin pois.

- **0.12.12 – 22.11.2026:** määriteltiin tuottajan tuloksen, vastaanottajan käsittelyn ja ajon lopputilan erottelu sekä aktiivisen tehtävän vapauttamisen ehdot. Uudelleenyritysten määrät ja muut vastaavat käsittelyrajat päätettiin konfiguroitaviksi; niitä ei kovakoodata.

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
