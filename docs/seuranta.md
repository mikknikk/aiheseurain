# Uutisseurannan seurantaohje ja julkaisuhistoria

Viimeksi alustettu: 2026-11-16.
Tämä tiedosto on luettava kokonaan ennen jokaista ajoa. Päivitä sitä vain, kun tarkistuksissa tai uutisten tilassa tapahtuu merkityksellinen muutos.

## Yleiset raportointisäännöt

### Tehtäväkohtainen seurantajakso

- Ilmoita jokaisessa seurantaraportissa seurantajakson alku ja loppu muodossa `Seurantajakso: 16.11.2026 klo 12.00 – 26.11.2026 klo 12.00 (Europe/Helsinki)`.
- Jakso alkaa kyseisen tehtävän edellisestä onnistuneesta tarkistuksesta ja päättyy nykyiseen tarkistushetkeen. Älä käytä edellisen automaatioajon ajankohtaa, jos kyseinen tehtävä ei ollut silloin vuorossa.
- Ensimmäisessä tarkistuksessa käytä dokumentoitua seurannan aloituspäivää ja kerro, että kyseessä on ensimmäinen tarkistus.
- Jos tarkkaa aiempaa kellonaikaa ei ole dokumentoitu, ilmoita tunnettu päivämäärä ja merkitse kellonaika tuntemattomaksi. Älä keksi aikaväliä.
- Erota uutisen julkaisu- ja tapahtumapäivä seurantajakson aikavälistä.
- Ilmoita aikaväli myös silloin, kun uutta merkittävää tietoa ei löydy tai RSS:ää ei päivitetä.
- Päivitä tehtäväkohtainen viimeisin onnistunut tarkistus ja sen aikaleima vasta onnistuneen ajon jälkeen.

## Pääautomaation ohjeversion seuranta

- Pääautomaation täydellinen toimintakäsikirja on `docs/paaautomaation-ohje.md`; sen versionumero on dokumentin alussa.
- `data/seurantatila.json`-tiedoston `automation_instructions.current_version` on käsikirjan nykyinen hyväksytty versio. Arvojen on täsmättävä ennen jokaista ajoa.
- `last_successful_run_version` ja `last_successful_run_at` kertovat viimeisimmän onnistuneen ajon käyttämän version ja ajan. Ne päivitetään vain, kun koko ajo ja GitHub-kirjoitusten takaisinlukutarkistukset ovat onnistuneet.
- Käsikirjaa muutettaessa päivitetään sen versionumero ja `current_version` samassa muutossarjassa. Viimeisimmän onnistuneen ajon kenttiä ei muuteta etukäteen. Erillinen näytösvahti säilyttää tämän versionhallintaosion muuttumattomana omissa JSON-päivityksissään.
- GitHub Actions tarkistaa, että käsikirja, JSONin nykyinen versio ja dokumentin polku vastaavat toisiaan.

## Erillisen näytösvahdin ohjeversion seuranta

- Näytösvahdin täydellinen tehtäväohje on `docs/intialaisten-elokuvien-naytosseuranta.md`. Sen MAJOR.MINOR.PATCH-versio on dokumentin alussa.
- `data/seurantatila.json`-tiedoston `separate_screening_watch.automation_instructions.current_version` on hyväksytty nykyversio; sen on vastattava käsikirjaa ennen jokaista ajoa.
- `last_successful_run_version` ja `last_successful_run_at` kirjataan vain onnistuneen näytösvahtiajon jälkeen. Näytösvahti säilyttää pääautomaation ja laatutarkistuksen ohjeversiot ennallaan.
- GitHub Actions tarkistaa käsikirjan version ja JSONin vastaavuuden.

## Laatutarkistuksen ohjeversion seuranta

- Viikoittaisen laatutarkistuksen täydellinen käsikirja on `docs/laatutarkistuksen-ohje.md`.
- `data/seurantatila.json`-tiedoston `quality_check_instructions.current_version` on hyväksytty nykyversio.
- Viimeksi onnistuneesti käytetty versio ja aikaleima päivitetään vain kattavan auditoinnin jälkeen. Laatutarkistus ei korjaa havaintoja eikä muuta muita repositoryn tiedostoja; ainoastaan nämä kaksi onnistuneen ajon metatietokenttää saa päivittää.
- Jos käsikirjan ja JSONin versiot eivät täsmää, automaatio keskeyttää.

## Käynnistyskehotteiden tunnisteet

- Jokaisella kolmella automaatiolla on oma yksilöllinen tunniste kanonisessa `prompts/`-tiedostossa ja sama arvo `data/seurantatila.json`-tiedoston vastaavan ohjeosion `startup_prompt_id`-kentässä.
- Ajon alussa automaatio vertaa aktiivisen käynnistyskehotteensa tunnistetta GitHubin seurantatilaan. Puuttuva tai ristiriitainen tunniste pysäyttää ajon ennen varsinaista seurantaa tai auditointia.
- Kun käynnistyskehotteen sisältöä muutetaan, tunniste vaihdetaan uuteen ja JSON-kenttä päivitetään samassa muutossarjassa. Muiden automaatioiden tunnisteet säilyvät ennallaan.
- Tunnistevertailu havaitsee vanhentuneen live-kehotteen, jos kanonisen kehotteen tunniste on vaihdettu. Se ei todista koko prompt-tekstin identtisyyttä, joten koko teksti kopioidaan asetuksiin ja tarkistetaan edelleen manuaalisesti.
- `scripts/validate_feeds.py` varmistaa, että kaikki kolme kanonista promptia ja niiden JSON-tunnisteet vastaavat toisiaan.

## Lähdekattavuuden koneellinen seuranta

- `data/source-catalog.json` sisältää lähteiden yhteiset perustiedot (nimi, URL, kielet, lähdetyyppi ja alueet) kerran. `data/sources/{task_id}.json` sisältää tehtäväkohtaiset `source_id`-viittaukset sekä kriittisyyden, viimeisimmän tarkistusajan ja käyttörajoitteet. Yhdistä tiedot ID:n perusteella; lähteen tarkistus yhdessä tehtävässä ei tarkoita, että se olisi tarkistettu muissa tehtävissä.
- `schemas/lahdekatalogi.schema.json` ja `schemas/lahderekisteri.schema.json` määrittävät katalogin ja käyttörekisterien rakenteet. `scripts/validate_source_coverage.py` tarkistaa viittausten eheyden ja ajolokin tehtäväkohtaisuuden.
- `data/lahdetarkistukset.json` säilyttää ajokohtaiset tarkistustulokset. Jokaisessa ajossa eritellään tarkistetut lähteet sekä tarkistamatta jääneet lähteet syineen. Osittainen tai epäonnistunut ajo ei saa näyttää täydelliseltä.
- Tehtävätunnisteet `intialaiset_elokuvat_uutiset` ja `intialaiset_elokuvat_naytokset` ovat erilliset. Uutisautomaatio ei lisää näytöslähteiden tarkistuksia omaan ajoonsa.
- `complete` on operatiivinen merkintä siitä, että tehtävän rekisteriin merkityt kriittiset lähteet on käsitelty. Se ei ole todiste täydellisestä maailmanlaajuisesta kattavuudesta. Kieli- ja aluepuutteet kirjataan `coverage_notes`-kenttään.
- `data/seurantatila.json`-tiedoston `sources_checked` säilyy yhteenvetolukuna; lähdekohtaiset tiedot ovat ajolokissa.

## Koneellinen seurantatila ja automaattiset testit

- `data/seurantatila.json` on koneellisesti luettava rinnakkaistila. Sen `rotation.next_task`-arvon pitää vastata [tehtäväjonon](tehtavajono.md) seuraava-tehtävä-merkintää.
- Tiedoston rakenne validoidaan skeemalla `schemas/seurantatila.schema.json` ennen projektikohtaisia eheystarkistuksia. Valvomon tietolähteiden ja julkaisun tarkempi vastuunjako on dokumentissa [Valvomon tietomalli](valvomon-tietomalli.md).
- Päivitä kyseisen tehtävän `last_successful_check`, `last_period_start`, `last_period_end`, `last_result`, `published_items` ja `sources_checked` vasta, kun tarkistus on onnistunut ja kaikki tarvittavat GitHub-kirjoitukset on luettu takaisin.
- Käytä ISO 8601 -aikaleimoja aikavyöhyketietoineen. Älä päättele vanhoja tarkkoja aikoja jälkikäteen. Tuntematon arvo säilyy `null`-arvona.
- Erillisen näytösvahdin tila kirjataan JSON-tiedoston `separate_screening_watch`-osioon. Se ei muuta `rotation.next_task`-arvoa.
- GitHub Actions ajaa `scripts/validate_feeds.py`-testin push- ja pull request -muutoksissa. Testi tarkistaa RSS/XML-rakenteet, GUIDit, item-linkkien kiellon, CDATA-descriptionit, kuvausten sisäisen HTML-rakenteen, linkkien URL-muodot, otsikkotasot, kuvien alt-attribuutit ja lähdeluettelot. Lisäksi se vertaa README:n syötetietoja, tehtäväjonon yhdeksää tehtävää ja JSON-seurantatilan kiertojärjestystä sekä tarkistaa aikaleimojen aikavyöhykkeet, seurantajaksojen johdonmukaisuuden ja näytösvahdin erillisyyden.
- Jos automaattinen testi epäonnistuu, korjaa virhe ennen julkaisun pitämistä valmiina. Testin läpäisy ei kuitenkaan todista uutisten faktatarkkuutta eikä WCAG AAA -vaatimusten täyttymistä.


## Tehtäväjonon muistutus

Tehtävien järjestys ja seuraava vuoro eivät kuulu tähän seurantahistoriaan. Niiden ainoa totuuslähde on [docs/tehtavajono.md](tehtavajono.md). Päivitä tähän tiedostoon tehtäväkohtaiset löydökset, tarkistuspäivät ja seurantahistoria. Jokaisen tehtävän raportissa ilmoitetaan tehtäväkohtainen seurantajakso.


- Ensimmäinen seurantapohja luotu 2026-11-16.
- Aiemmin julkaistuja uutisartikkeleita ei ollut pohjaa luotaessa.
- Ensimmäinen varsinainen uutiskierros aloittaa uutishistorian; älä tulkitse tätä tiedostoa uutisväitteeksi siitä, ettei aiheista olisi uutisoitu.

## Luotettavuusmerkintöjen käyttö

Uusien uutisten lähdeluokka ja väitekohtainen varmennustaso määritellään keskitetysti dokumentissa [Uutislähteiden ja uutisväitteiden luotettavuusluokitus](luotettavuusluokitus.md). Älä tulkitse tämän tiedoston historiallisia merkintöjä takautuvasti uuden mallin mukaisiksi: aiemmat **VIRALLISESTI VAHVISTETTU**, **MEDIAN RAPORTOIMA** ja **VAHVISTAMATON HUH​​U** -merkinnät säilytetään alkuperäisessä muodossaan. Uusissa raporteissa käytetään uuden ohjeen erillisiä lähdeluokka- ja väitekohtaisia merkintöjä.

## Aihekohtainen seuranta

### J. R. R. Tolkien

- RSS: `feeds/tolkien.xml`
- Lähtötilanne 2026-11-16: ensimmäinen tarkistus tehtiin; sitä ennen Tolkien-RSS-syöte oli tyhjä.
- Seuranta: elämäntyö ja perintö, uudet julkaisut ja tutkimus, oikeudenhaltijat, adaptaatiot (elokuva, televisio, pelit), näyttelyt ja tapahtumat. Tarkista erikseen Suomessa järjestettävät Tolkien-aiheiset tapahtumat, kuten näyttelyt, conit, luennot, elokuvanäytökset ja yleisötilaisuudet.
- Erota Tolkienin itse kirjoittamat teokset myöhemmästä toimituksellisesta aineistosta ja adaptaatioista.
- **11.11.2026 – MEDIAN RAPORTOIMA:** Andy Serkis kertoi The Morning Mosh Pit -haastattelussa, että *The Lord of the Rings: The Hunt for Gollum* -elokuvan pääkuvaukset ovat päättyneet. Lausunto julkaistiin 11.11.; toimitukselliset raportit ilmestyivät 12.11. Serkis ei ilmoittanut tarkkaa viimeistä kuvauspäivää, eikä Warner Brosin erillistä kuvausten päättymistä koskevaa tiedotetta saatu tarkistettua. New Zealand Film Map, GamesRadar+ ja The One Ring raportoivat samasta haastattelusta, joten kyse ei ole kolmesta toisistaan riippumattomasta vahvistuksesta. Alkuperäistä videota ei saatu avattua.
  - RSS GUID: `urn:aiheseurain:tolkien:2026-11-12:hunt-for-gollum-wrap`; `feeds/tolkien.xml`.
  - Seuraava tarkistus: virallinen Warner Brosin tai Serkisin tiedote, mahdolliset lisäkuvaukset ja siirtyminen jälkituotantoon.
- **9.11.2026 – MEDIAN RAPORTOIMA:** Tolkien-tutkija David Bratman kuoli 9.11.2026 69-vuotiaana. File 770 (9.11.) ja Elfenomeno (10.11.) raportoivat kuolemasta ja hänen pitkästä Tolkien-tutkimuksen urastaan. Mythopoeic Societyn kotisivun hakutulosotteessa näkyi järjestön suru-uutinen, mutta ilmoitusta ei saatu esiin avatulla sivulla; sitä ei lasketa suoraksi ensisijaislähteen tarkistukseksi.
  - RSS GUID: `urn:aiheseurain:tolkien:2026-11-10:david-bratman`; `feeds/tolkien.xml`.
  - Seuraava tarkistus: mahdolliset merkittävät muistotilaisuudet, muistokirjoitukset tai hänen työnsä postuumit julkaisut.
- **16.11.2026 – VIRALLISESTI VAHVISTETTU:** EHU:n julkaisema TARTALO-konferenssin ohjelma vahvistaa neljä Tolkien-aiheista tutkimusesitelmää ja kuvittaja Anke Eissmannin keynote-puheenvuoron Vitoria-Gasteizissa 18. ja 20.11.2026.
  - RSS GUID: `urn:aiheseurain:tolkien:2026-11-16:tartalo-conference`; `feeds/tolkien.xml`.
  - Seuraava tarkistus: tapahtuman toteutuminen 20.11. jälkeen sekä mahdolliset tallenteet, julkaisut tai konferenssijulkaisut.

### Taylor Swift

- RSS: `feeds/taylor-swift.xml`
- Seurantahistoria käynnistyi 2026-11-16; RSS:ssä on yksi julkaistu uutinen.
- Seuranta: musiikki ja julkaisut, kiertueet ja esiintymiset, elokuva/TV, liiketoiminta, palkinnot, hyväntekeväisyys ja julkinen ura. Hae erikseen Suomessa järjestettävät konsertit, fanitapahtumat, kuuntelutilaisuudet, elokuvanäytökset, näyttelyt ja muut viralliset tapahtumat.
- Vältä vähäarvoista yksityiselämää koskevaa juoruilua ja vahvistamattomia parisuhdeväitteitä.
- **16.11.2026 – VIRALLISESTI VAHVISTETTU:** Recording Academy julkisti 69. Grammy-gaalan ehdokkaat. Taylor Swift sai viisi ehdokkuutta: vuoden albumi (*The Life of a Showgirl*), vuoden levytys (*The Fate of Ophelia*), vuoden laulu (*I Knew It, I Knew You*, elokuvasta *Toy Story 5*), paras audiovisuaaliselle tuotannolle kirjoitettu laulu (sama kappale) sekä paras pop-duo- tai yhtye-esitys (*The Life of a Showgirl* yhdessä Sabrina Carpenterin kanssa). Hänen albuminsa on viides peräkkäinen vuoden albumi -ehdokkuuden saanut studioalbumi; AP:n mukaan vain Kendrick Lamar on aiemmin yltänyt vastaavaan sarjaan.
  - Lähteet: Recording Academy (palkintojärjestäjä), Universal Music Group (levy-yhtiön ensisijainen tiedote), Associated Press ja Reuters (riippumattomat toimitukselliset vahvistukset) sekä UOL Splash (Brasilia, brasilianportugali; rinnakkaisraportti ja uusi alueellinen rekisterilähde).
  - Seurantajakso: 16.11.2026 (kellonaika ei tiedossa) – 17.11.2026 klo 13:03 (Europe/Helsinki).
  - RSS GUID: `urn:aiheseurain:taylor-swift:2026-11-16:grammy-2027-nominations`; `feeds/taylor-swift.xml`.
  - Seuraava tarkistus: 7.2.2027 järjestettävän gaalan voittajat sekä mahdolliset olennaiset uudet julkaisu-, esiintymis- ja tapahtumatiedot.

### Saint Dr. Gurmeet Ram Rahim Singh Ji Insan

- RSS: `feeds/gurmeet-ram-rahim-singh.xml`
- Seurantahistoria käynnistyi 2026-11-16; RSS:ssä on yksi julkaistu uutinen.
- Seuranta: julkinen toiminta, oikeudelliset ja viralliset tapahtumat, lausunnot, tuotannot/elokuvahankkeet ja julkaisut sekä musiikki, kappaleet, musiikkivideot ja soundtrackit. Kirjaa myös merkittävät musiikin julkaisu-, levitys- ja vastaanottouutiset.
- Käytä nimen variantteja ja translitterointeja. Varmista, ettei uutinen koske samannimistä henkilöä.
- Oikeusasioissa erottele täsmällisesti syytteet, tuomiot, valitukset, viranomaistoimet ja tuomioistuinratkaisut. Älä esitä syytettä tuomiona.
- **18.11.2026 – ENSISIJAISELLÄ LÄHTEELLÄ VAHVISTETTU (istuntolistauksen sisältö):** Intian korkeimman oikeuden 18.11.2026 päivätty päivittäinen istuntolista sisältää Chief Justice’s Courtin kohdassa 120 rikosasian valituksen Crl.A. No. 3785/2026. Valittaja on Aridaman; vastaajiksi on merkitty Baba Gurmeet Singh @ Maharaj Gurmeet Singh @ Gurmeet Ram Rahim Singh sekä toinen vastaaja. Samassa kohdassa on IA No. 225562/2026 lisäasiakirjojen, tietojen tai liitteiden toimittamista varten. Listan lopussa näkyy New Delhi 17.11.2026 klo 19.49.57.
- **Taustaväite – YHDEN TOIMITUKSELLISEN LÄHTEEN RAPORTOIMA:** valitus koskee Gurmeet Ram Rahim Singhin vapauttavaa ratkaisua toimittaja Ram Chander Chhatrapatin vuoden 2002 murhajutussa. Hindustan Times (11.8.2026) raportoi Punjab and Haryana High Courtin 7.3.2026 vapauttavasta ratkaisusta. Amar Ujala (12.8.2026) ja The Tribune / PTI (10.8.2026) julkaisivat samasta elokuun oikeustapahtumasta rinnakkaiset raportit, mutta niiden alkuperäisen raportointityön riippumattomuutta ei voitu osoittaa; The Tribune -juttu on lisäksi PTI-syndikoitu. Taustaväite on siksi merkitty yhden toimituksellisen lähteen raportoimaksi. High Courtin alkuperäistä tuomioasiakirjaa ei saatu avattua tässä ajossa.
- **Menettelyn tila ja epävarmuus:** virallinen 18.11. lista sijoittaa asian otsikon *For Admission and I.R.* alle. Hindustan Times ja The Tribune / PTI kuvasivat käsittelyä lopulliseen käsittelyyn 16.11. alkavalla viikolla määrätyksi; Amar Ujala ilmoitti päivämääräksi 16.11. Alkuperäisen elokuun oikeusmääräyksen tekstiä ei saatu tarkistettua. Avatut asiakirjat eivät selitä eroa. Uusimpien määräysten sivulla ei näkynyt asianumerolla Crl.A. No. 3785/2026 annettua määräystä; tapaustilan hakulomake vaati JavaScriptin ja CAPTCHA-vastauksen. Istunnon toteutumista tai ratkaisua ei päätellä.
- **Seurantajakso:** 16.11.2026 (ensimmäinen tarkistus; aloituskellonaika tuntematon) – 18.11.2026 klo 14.00.19 (Europe/Helsinki).
- **RSS GUID:** `urn:aiheseurain:gurmeet-ram-rahim-singh:2026-11-18:aridaman-appeal-cause-list`; `feeds/gurmeet-ram-rahim-singh.xml`.
- **Lähdekattavuus:** ajo on osittainen. Korkeimman oikeuden alkuperäinen lista tarkistettiin, mutta Punjab and Haryana High Courtin ja CBI:n viralliset sivut aikakatkaistiin ja The Hindu esti suoran avauksen robots.txt-säännöllä. Englanninkielisten lähteiden lisäksi tarkistettiin hindinkielinen Amar Ujala ja tehtiin pandžabinkieliset haut. Dera Sacha Saudan ja Saint Dr. MSG Insanin viralliset sivut avattiin täydentävinä, rekisteriin kuulumattomina lähteinä; niissä ei näkynyt 16.–18.11. uutta aiheeseen liittyvää ilmoitusta.
- **Muut seurantateemat:** tarkistetuissa lähteissä ja englannin-, hindin- ja pandžabinkielisissä hauissa ei löytynyt jaksolle osuvaa vahvistettua uutta väliaikaista vapautusta, elokuva- tai musiikkijulkaisua.
- **RSS-julkaisun lähteet:** [Intian korkeimman oikeuden istuntolista](https://api.sci.gov.in/jonew/cl/2026-11-18/F_J_2.pdf), [uusimmat määräykset](https://www.sci.gov.in/latest-orders/), [tapaustilan hakulomake](https://www.sci.gov.in/case-status-case-no/), [Hindustan Times](https://www.hindustantimes.com/cities/chandigarh-news/2002-journalist-murder-case-sc-agrees-to-hear-plea-against-dera-sacha-sauda-chief-s-acquittal-101786387552625.html), [Amar Ujala](https://www.amarujala.com/amp/haryana/sirsa/ramchandra-chhatrapati-murder-case-anshul-moves-supreme-court-against-high-court-verdict-2026-08-12) ja [The Tribune / PTI](https://www.tribuneindia.com/news/haryana/supreme-court-agrees-to-hear-plea-against-dera-sacha-sauda-chiefs-acquittal-in-2002-murder-case/).

### Muumit

- RSS: `feeds/muumit.xml`
- Seurantahistoria käynnistyi 2026-11-16; RSS:ssä on yksi julkaistu uutinen.
- Seuranta: Tove Janssonin teokset ja perintö, Moomin Characters ja oikeudenhaltijat, kirjat, sarjakuvat, animaatiot, elokuvat, televisio, teatteri, pelit, näyttelyt, tapahtumat, lisensointi ja kulttuurihankkeet. Tarkista erikseen Suomessa järjestettävät Muumi-näyttelyt, museo- ja teemapuistotapahtumat, teatteri, konsertit, elokuvanäytökset, festivaalit ja perhetapahtumat.
- Käytä hakusanoja Muumit, Moomin, Moomins ja ムーミン sekä tarvittaessa paikallisia kielimuotoja.
- Erota virallinen uutinen fanisisällöstä.
- **16.11.2026 – VIRALLISESTI VAHVISTETTU:** Moominin virallinen japanilainen sivusto ilmoitti julkaisujuhlasta pelille *Muumit: Muumilaakson kesäjuhlat*. Maksuton tapahtuma järjestetään Cocoon Cityssä Saitamassa 21.–22.11.2026; ohjelmassa on pelin kokeilua ja muuta teemaan liittyvää toimintaa.
- Lähde: Moomin Official Website, https://www.moomin.co.jp/news/events/6ae85147d7289 (ensisijainen). Shochikun aiempi tiedote tapahtumasta on saman järjestäjätahon viestintää, ei riippumaton vahvistus.
- RSS GUID: `urn:aiheseurain:muumit:2026-11-16:cocoon-city-launch-event`.
- Seuraava tarkistus: tarkista tapahtuman toteutuminen ja mahdolliset merkittävät jatkouutiset 22.11. jälkeen.

### Wakaliwood

- RSS: `feeds/wakaliwood.xml`
- Lähtötilanne 2026-11-16: uusi seuranta; julkaistuja RSS-artikkeleita ei vielä ole.
- Seuranta: Wakaliwood-elokuvateollisuus ja -studio, Nabwana I.G.G. ja muut keskeiset tekijät, uudet ja vanhat tuotannot silloin kun niihin liittyy uusi kehitys, festivaalit, levityssopimukset, näytökset, kansainväliset kiertueet, rahoitus, dokumentit ja Ugandan elokuvakulttuurin uutiset, jotka liittyvät suoraan Wakaliwoodiin.
- Erota vahvistetut tuotantotiedot, festivaaliohjelmat, huhut ja fanisisältö.
- Tapahtumaloki: ei vielä merkintöjä.

### Euroviisut ja kansalliset karsinnat

- RSS: `feeds/euroviisut.xml`
- Seurantahistoria käynnistyi 2026-11-16; RSS:ssä on yksi julkaistu uutinen.
- Seuranta kattaa Eurovision Song Contestin, kaikki osallistujamaiden kansalliset valinnat ja karsinnat, esikarsinnat, valintaprosessit, artisti- ja kappalejulkistukset, sääntömuutokset, järjestelyt, lähetykset, tulokset, delegaatiot sekä oheis- ja aluekilpailut.
- Sisällytä Eurovision Song Contest Asia ja sen mahdolliset kansalliset karsinnat/valinnat sekä muut Eurovision-brändiin tai euroviisuyhteisöön liittyvät alueelliset kilpailut. Älä rajaa seurantaa Euroopan maantieteeseen.
- Seuraa kaikkia maita ja kielialueita, ei vain Suomen tai suurten osallistujamaiden uutisia. Suomen UMK, Yle, suomalaiset artistit ja Suomessa järjestettävät Euroviisu-konsertit, fanitapahtumat, katselujuhlat, näyttelyt, kilpailut ja muut yleisötilaisuudet nostetaan esiin, kun niistä on uutista. Tarkista tapahtumat myös järjestäjien, tapahtumapaikkojen ja lipunmyyjien omista kalentereista.
- Erota viralliset EBU-/järjestäjätiedot, kansallisten yleisradioyhtiöiden ilmoitukset, median raportit ja fanihuhut.
- **14.11.2026 – VIRALLISESTI VAHVISTETTU:** Filippiinejä edustanut CARMELLE voitti ensimmäisen Eurovision Song Contest Asian kappaleella *Sobra-Sobra* ja sai 211 pistettä (93 raadilta, 118 yleisöltä). Finaalissa oli 11 maan edustajat; EBU:n mukaan ääniä annettiin 183 maasta ja alueelta.
- Ensisijainen lähde: EBU/Eurovisionin virallinen tiedote, https://www.eurovision.com/newsroom/release/carmelle-from-philippines-wins-inaugural-eurovision-song-contest-asia-in-bangkok/. Riippumattomat toimitukselliset vahvistukset: AFP (https://origin-zh9p7m-www.afp.com/en/philippines-wins-eurovisions-first-asia-contest) ja Associated Press (https://apnews.com/article/099ca558c4638949e637d3a8f8061d6d).
- RSS GUID: `urn:aiheseurain:euroviisut:2026-11-14:esc-asia-first-winner-carmelle`.
- Seuraava tarkistus: seuraa EBU:n ja osallistuneiden yleisradioyhtiöiden vahvistuksia mahdollisesta vuoden 2027 jatkokilpailusta; mediassa esitettyä kiinnostusta ei tule käsitellä vahvistettuna osallistujalistana.

### Sompote Sands

- RSS: `feeds/sompote-sands.xml`
- Lähtötilanne 2026-11-16: uusi seuranta; julkaistuja RSS-artikkeleita ei vielä ole.
- Seuranta: thaimaalainen elokuvaohjaaja ja tuottaja Sompote Sands (myös Sompote Saengduenchai ja muut asianmukaiset translitteroinnit), hänen elokuvansa ja tuotantonsa, Krua/Chaiyo-elokuvastudioihin liittyvä relevantti historia, elokuvien restaurointi, arkistointi, julkaisut, esitykset, festivaalit, oikeudet, kansainvälinen levitys, retrospektiivit ja hänen työnsä uusi tutkimus tai kulttuurinen vastaanotto.
- Hae thaiksi ja englanniksi sekä muilla asiaankuuluvilla kielillä. Varmista henkilön ja teosten nimien kirjoitusasut luotettavista lähteistä.
- Tapahtumaloki: ei vielä merkintöjä.

### Shakkidraamat

- RSS: `feeds/shakkidraamat.xml`
- Lähtötilanne 2026-11-16: uusi seuranta; julkaistuja RSS-artikkeleita ei vielä ole.
- Seuranta: shakkimaailman todelliset ajankohtaiset kiistat, draamat, konfliktit ja kohut – ei fiktiiviset shakkiaiheiset elokuvat eikä tavalliset turnaustulokset. Mukaan kuuluvat huijaus- ja vilppisyytökset sekä vastineet ja ratkaisut, pelaajien ja FIDEn/liittojen jännitteet (esim. Carlsen–FIDE ja Jeansgate), Kramnikin ja Hans Niemannin tapaiset vilppikiistat, Danya/Daniel Naroditskyn kuolemaan liittyvät luotettavasti raportoidut kehitykset, kurinpitomenettelyt, oikeusjutut, järjestö- ja hallintokiistat, turnaus- ja sääntökiistat sekä julkiset konfliktit. Seuraa myös tunnettujen shakkisisällöntuottajien ja -kommentaattorien olennaisia julkisia somelausuntoja, keskusteluja ja konflikteja; älä kerää rutiinipostauksia.
- Käsittele väitteet neutraalisti ja täsmällisesti. Erota vahvistettu näyttö, väitteet, vastineet, tutkinta, väliaikaiset päätökset ja lopulliset ratkaisut. Älä esitä syytöstä todettuna vilppinä ilman ratkaisua tai vahvaa näyttöä.
- Seuraa maailmanlaajuisesti eri kielillä; huomioi FIDE, kansalliset liitot, turnausjärjestäjät, pelaajien lausunnot ja riippumaton shakki- ja yleismedia.
- Tapahtumaloki: ei vielä merkintöjä.

## Suomi-seuranta kaikissa aiheissa

Tarkista jokaisessa kategoriassa myös Suomen uutisointi ja tapahtumakalenterit sekä suomalaiset järjestäjät, toimijat, tapahtumapaikat ja yleisradio-/kulttuuriorganisaatiot. Kirjaa ja raportoi Suomi-yhteys, jos se on olennainen: esimerkiksi suomalainen toimija, Suomessa järjestettävä konsertti, elokuvanäytös, kilpailu tai yleisötapahtuma. Jos Suomi-yhteyttä ei löydy, älä tee siitä erillistä huomautusta.

## Merkittävän uutistapahtuman seurantamerkintä

Lisää tarvittaessa kunkin aiheen alle:
- tapahtuma ja olennaisin uusi tieto
- tapahtuman päivämäärä ja uutisen julkaisupäivä erikseen
- luotettavuusluokka ja tämänhetkinen varmistustilanne
- lähteet sekä tieto siitä, ovatko lähteet toisistaan riippumattomia
- RSS-artikkelin GUID ja tiedostonimi
- seuraava olennainen tarkistustarve

Älä lisää päivittäisiä “ei uutisia” -merkintöjä. Kirjaa hakurajoite vain, jos se vaikutti olennaisesti kyseisen ajon kattavuuteen.


## Intialaisen elokuvan seuranta (tehtäväkierron mukainen)

Intialaisen elokuvan uutisraportti on docs/tehtavajono.md:n yhdeksäs tehtävä. Intialaisten elokuvien näytösseuranta on erillisen päivittäisen näytösvahdin vastuulla eikä kuulu aihekierrokseen. Yksityiskohtainen uutis- ja näytöshistoria on tiedostossa `docs/intialaisen-elokuvan-seuranta.md`. Lähteet ovat tiedostossa `docs/intialaisen-elokuvan-lahteet.md`. Uutisraportti julkaistaan tiedostoon `feeds/intialaiset-elokuvat.xml` ja näytöspäivitykset tiedostoon `feeds/intialaisten-elokuvien-naytokset.xml`.
