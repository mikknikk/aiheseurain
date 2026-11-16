# Pääautomaation toimintakäsikirja

Ohjeversion tunniste: 1.0.0
Viimeksi päivitetty: 2026-11-16

Tämä on pääautomaation ensisijainen ja täydellinen toimintakäsikirja. ChatGPT-automaation asetuksissa oleva kehote on vain vakaa käynnistysosoite. Tehtävien sisältöä ja toimintatapoja ylläpidetään tässä repositoriossa, ei rinnakkaisina kopioina automaation asetuksissa.

## 1. Järjestelmän rajat

- Repository: `mikknikk/uutiset`.
- Pääautomaatio käynnistyy päivittäin noin klo 12.00 Europe/Helsinki ja käsittelee täsmälleen yhden yhdeksästä tehtävästä.
- Intialaisten elokuvien näytösseuranta on erillinen päivittäinen automaatio noin klo 05.00 Europe/Helsinki. Se ei kuulu tehtäväkiertoon.
- Pääautomaatio ei tee näytöshakuja eikä muuta `feeds/intialaisten-elokuvien-naytokset.xml`-syötettä tai näytöshistoriaa. Älä sekoita uutis- ja näytösseurantaa.
- Älä luo rinnakkaisia aiheautomaatioita tai muuta aikatauluja tämän käsikirjan perusteella.

## 2. Aloitus, ohjeversion tarkistus ja keskeytysehdot

Noudata joka ajolla tätä järjestystä:

1. Lue `README.md` ja tämä käsikirja kokonaan.
2. Lue `data/seurantatila.json`. Tarkista, että `automation_instructions.document` osoittaa tähän tiedostoon ja että `current_version` vastaa tämän dokumentin Ohjeversion tunnistetta.
3. Jos GitHub ei ole käytettävissä, käsikirja tai seurantatila puuttuu tai versiot eivät täsmää, keskeytä ajo. Älä käytä vanhaa promptia, arvattua versiota tai vanhentunutta ohjetta. Älä tee hakuja, julkaisuja, onnistumismerkintöjä tai vuoron siirtoa.
4. Lue kokonaan `docs/tehtavajono.md`, `docs/seuranta.md`, `docs/lahteet.md` ja `docs/saavutettavuus.md`.
5. Lue `docs/kehityskaytannot.md), jos muutat skriptejä tai ylläpitokoodia.
6. Valitse seuraava tehtävä `docs/tehtavajono.md`:stä ja varmista, että se vastaa JSONin `rotation.next_task`-arvoa. Jos arvot eroavat, keskeytä ennen hakuja; älä arvaa kumpi on oikein.
7. Lue valitun aiheen ohjeet ja seurantaloki. Tehtävässä 9 lue kokonaan `docs/intialaisen-elokuvan-ohje.md`, `docs/intialaisen-elokuvan-uutiset.md`, `docs/intialaisen-elokuvan-lahteet.md` ja `docs/intialaisen-elokuvan-seuranta.md`. Älä lue tai muuta näytösvahdin ohjeita tai historiaa uutisautomaatiossa.
8. Lue valitun tehtävän RSS-syöte ja vertaa aiempia itemeitä/GUIDeja. Lue muita syötteitä vain deduplikoinnin ja aiherajauksen kannalta tarpeellisessa laajuudessa; älä muuta muiden tehtävien sisältöä.
9. Käytä dokumentaatiota ensisijaisena muistijälkenä, älä aiempien keskustelujen tai vanhan automaatiokehotteen muistikuvaa.

## 3. Yhdeksän tehtävän aiheiden rajaukset

Tehtävien kiertojärjestys ja seuraava vuoro määritellään vain tiedostossa `docs/tehtavajono.md`. Älä kopioi tai ylläpidä seuraavaa vuoroa tässä käsikirjassa.

1. **J. R. R. Tolkien:** elämäntyö, kirjallinen perintö, uudet julkaisut ja tutkimus, Tolkien Estate ja oikeudenhaltijat, adaptaatiot (elokuva, TV, pelit), näyttelyt ja tapahtumat. Erota Tolkienin omat kirjoitukset myöhemmistä toimitetuista julkaisuista ja adaptaatioista.
2. **Taylor Swift:** musiikki, julkaisut, kiertueet, esiintymiset, elokuva/TV, liiketoiminta, palkinnot, hyväntekeväisyys ja julkinen ura. Vältä vähäpätöistä yksityiselämän juoruilua ja vahvistamattomia suhdeväitteitä.
3. **Saint Dr. Gurmeet Ram Rahim Singh Ji Insan:** julkinen toiminta, viralliset ja oikeudelliset kehitykset, lausunnot, tuotannot, elokuvahankkeet ja julkaisut. Hae englanniksi, hindiksi ja pandžabiksi sekä nimivariantit/translitteroinnit. Varmista henkilön identiteetti. Erota syytteet, tuomiot, valitukset, viranomaistoimet ja oikeuden ratkaisut.
4. **Muumit:** Tove Janssonin teokset ja perintö, Moomin Characters ja oikeudenhaltijat, kirjat, sarjakuvat, animaatiot, elokuvat, TV, teatteri, pelit, näyttelyt, tapahtumat, lisensointi ja liiketoiminta. Hae suomeksi, ruotsiksi, englanniksi ja japaniksi; käytä myös kirjoitusasuja Muumit/Moomin/Moomins/ムーミン. Erota virallinen uutinen fanisisällöstä.
5. **Wakaliwood:** elokuvateollisuus ja studio, Nabwana I.G.G. ja muut keskeiset tekijät, tuotannot, festivaalit, levitys, näytökset, kansainväliset kiertueet, rahoitus, dokumentit ja Wakaliwoodiin liittyvä Ugandan elokuvakulttuuri. Hae Ugandasta, Itä-Afrikasta ja kansainvälisistä genre- ja festivaalilähteistä sekä soveltuvilla paikalliskielillä.
6. **Euroviisut:** Eurovision Song Contest, kaikkien maiden kansalliset valinnat ja karsinnat, esikarsinnat, artisti- ja kappalejulkistukset, säännöt, järjestelyt, tulokset, delegaatiot sekä oheis- ja aluekilpailut. Sisällytä Eurovision Song Contest Asia ja muut olennaiset aluekilpailut; älä rajaa seurantaa Euroopan maantieteeseen. Hae eri maiden omilla kielillä ja yleisradioyhtiöiden lähteistä. Seuraa Yleä, UMK:ta, suomalaisia artisteja ja Suomessa järjestettäviä tapahtumia.
7. **Sompote Sands:** thaimaalainen elokuvaohjaaja ja tuottaja, myös Sompote Saengduenchai (สมโพธิ แสงเดือนฉาย) ja muut translitteroinnit. Seuraa elokuvia, tuotantoja, studiohistoriaa, restaurointeja, arkistointia, julkaisuja, näytöksiä, festivaaleja, oikeuksia, levitystä, retrospektiivejä ja tutkimusta. Hae thaiksi ja englanniksi.
8. **Shakkidraamat:** merkittävät shakin kiistat, huijaus-/vilppisyytökset, kurinpitomenettelyt, oikeusjutut, järjestö- ja hallintokiistat, pelaajien/järjestäjien konfliktit, turnausten vakavat tapahtumat sekä sääntö- ja reilun pelin kiistat. Seuraa FIDEä, kansallisia liittoja, järjestäjiä, pelaajien lausuntoja ja riippumatonta mediaa. Erota väitteet, vastineet, tutkinta, väliaikaiset päätökset ja lopulliset ratkaisut.
9. **Intialaisen elokuvan uutisraportti:** noudata kokonaan tehtäväkohtaisia intialaisen elokuvan uutisohjeita. Päivitä vain `feeds/intialaiset-elokuvat.xml` ja uutishistorian osio `docs/intialaisen-elokuvan-seuranta.md`:ssä.

## 4. Maailmanlaajuinen lähdehaku ja Suomi

- Hae maailmanlaajuisesti, eri maanosista ja useilla kielillä. Älä rajoitu englanninkieliseen mediaan. Käytä paikalliskieliä, alkuperäisiä kirjoitusasuja, translitterointeja, alueellisia uutistoimistoja, kansallisia yleisradioyhtiöitä, erikoismedioita, virallisia lähteitä ja tapahtumajärjestäjiä. `docs/lahteet.md` on lähtökohta, ei suljettu lista.
- Tarkista jokaisessa kategoriassa erikseen Suomen uutiset ja tapahtumat: suomalaiset toimijat, järjestäjät, tapahtumapaikat, konsertit, elokuvanäytökset, kilpailut, festivaalit ja fanitapahtumat. Nosta uutisarvoinen Suomi-yhteys selvästi esiin. Jos yhteyttä ei löydy, älä mainitse sen puuttumista.
- Jos sivuston sisäinen haku ei toimi, käytä hakukoneita sivustorajauksilla (esim. `site:yle.fi`, `site:hs.fi` ja paikallisten medioiden domainit). Avaa alkuperäinen juttu ja tarkista sisältö sekä päivämäärä; hakutuloskatkelma ei yksin riitä.
- Suosi ensisijaisia lähteitä (viralliset tiedotteet, tekijät, oikeudenhaltijat, viranomaiset, tuomioistuimet, EBU/yleisradioyhtiöt, liitot, festivaalit ja järjestäjät). Pyri varmistamaan tärkeät uutiset kahdesta riippumattomasta toimituksellisesta lähteestä. Saman uutistoimiston kopiot eivät ole riippumattomia.
- Erota julkaisupäivä ja tapahtumapäivä. Tarkista nimet, roolit, luvut ja lainaukset. Älä keksi väitteitä, lähteitä, päivämääriä tai URL-osoitteita. Jos alkuperäistä sisältöä ei voi tarkistaa, älä esitä sitä vahvistettuna.
- Luotettavuusluokat: **VIRALLISESTI VAHVISTETTU**, **MEDIAN RAPORTOIMA**, **VAHVISTAMATON HUH​​U**. Älä julkaise huhua uutisena. Oikeus-, kurinpito- ja vilppiasioissa käytä täsmällisiä menettelytermejä.

## 5. Uutisarvo, seurantajakso ja deduplikointi

- Raportoi ensisijaisesti edellisen kyseisen tehtävän onnistuneen tarkistuksen jälkeen tapahtuneet olennaiset kehitykset. Seurantajakso alkaa kyseisen tehtävän edellisestä onnistuneesta tarkistuksesta ja päättyy nykyiseen tarkistushetkeen Europe/Helsinki-ajassa. Älä käytä edellisen automaatioajon aikaa, jos kyseinen aihe ei ollut silloin vuorossa.
- Ensimmäisellä tarkistuksella käytä dokumentoitua aloituspäivää. Jos aiempaa kellonaikaa ei tunneta, kerro tunnettu päivämäärä ja merkitse kellonaika tuntemattomaksi. Älä arvaa. Noudata `docs/seuranta.md`:n tarkempia sääntöjä.
- Vanhempi uutinen voidaan julkaista vain, jos se on selvästi jäänyt käsittelemättä ja on edelleen uutisarvoinen; ilmoita alkuperäinen päiväys.
- Julkaise vain olennaisia uusia tai merkittävästi muuttuneita, lähteistettyjä tapahtumia. Yhdistä saman tapahtuman lähteet yhdeksi RSS-itemiksi.
- Älä toista muuttumatonta taustatietoa, vanhoja huhuja, fanispekulaatiota, markkinointihypetystä, vähäarvoisia yksityiselämäjuoruja tai päivittäisiä “ei uutisia” -itemeitä.
- Jos aiempi väite osoittautuu vääräksi tai saa olennaisen vahvistuksen/kiistämisen, julkaise selkeä korjaus/päivitys ja viittaa aiempaan itemiin.
- Päivitä `docs/seuranta.md`:hen aihekohtainen tapahtumaloki. Tehtävässä 9 päivitä `docs/intialaisen-elokuvan-seuranta.md`: tapahtuma, tapahtuma- ja julkaisupäivä, luotettavuusluokka, tila, lähteet ja niiden riippumattomuus, RSS GUID ja seuraava tarkistustarve. Älä tee päivittäisiä “ei uutisia” -merkintöjä.

## 6. RSS-julkaisu ja tarkistukset

- Säilytä rakenne: dokumentit `docs/`-kansiossa, syötteet `feeds/`-kansiossa. Älä luo juureen uusia dokumentti- tai feed-tiedostoja äläkä poista tai korvaa muita tiedostoja.
- Jokaisessa syötteessä julkaistaan vain oman aiheen uutisia. Kirjoita suomeksi. `description` sisältää koko uutisartikkelin HTML:n, ei pelkkää tiivistelmää; lisää otsikko, päivämäärät, lähteet suorine linkkeineen ja luotettavuusluokitus.
- Käytä yksilöllisiä GUIDeja, oikeaa pubDatea, säilytä vanhat itemit ja päivitä lastBuildDate. Älä lisää keinotekoisia “ei uutisia” -itemeitä.
- Päivitä vain valitun tehtävän omaa RSS-syötettä. Älä koskaan muuta näytösfeedin sisältöä.
- Jokaisen kirjoituksen jälkeen hae muuttuneet tiedostot GitHubista takaisin ja tarkista XML:n kelvollisuus, GUIDien yksilöllisyys, vanhojen itemien säilyminen, HTML:n escaping/CDATA ja aiherajaus.
- RSS-itemissä ei saa olla item-kohtaista `<link>`-elementtiä. Koko raportti ja otsikoitu lähdeluettelo kuuluvat `<description>`-elementtiin CDATA-alueena. Kanavatason `<link>` ja `atom:link rel="self"` ovat sallittuja.
- Jokaisen itemin lopussa on otsikoitu lähdeluettelo, jossa ovat olennaiset lähteet yksilöivinä, kuvaavina linkkeinä.
- Noudata `docs/saavutettavuus.md`:n ohjeita: selkeä suomi, semanttinen HTML, looginen otsikkohierarkia, kuvaavat linkit ja alt-tekstit. Tavoittele WCAG 2.2 AAA -tasoa soveltuvin osin, mutta älä väitä tasoa saavutetuksi ilman asianmukaista testausta.
- Jos julkaisu epäonnistuu, toimita valmis artikkeli ja nimeä epäonnistunut tiedosto. Älä väitä julkaisua onnistuneeksi ilman GitHub-kirjoitusta ja takaisinlukutarkistusta.

## 7. Tehtäväkohtainen raportti

Toimita tiivis suomenkielinen kooste vain tämän ajon valitusta tehtävästä. Ilmoita seurantajakson alku ja loppu Europe/Helsinki-ajassa. Jos löytyi merkittävä uutinen, linkitä julkaistuun uutiseen ja syötteeseen; nosta Suomi-yhteys näkyvästi esiin. Jos merkittävää uutista ei löytynyt eikä julkaisuongelmia ole, kerro lyhyesti, ettei tämän aiheen osalta löytynyt uutta merkittävää uutista. Älä raportoi muiden aiheiden tilanteesta.

## 8. Onnistuminen, vuoron siirtäminen ja versioloki

Ajo on onnistunut vasta, kun valitun aiheen haku ja arviointi on tehty, mahdolliset julkaisut on tallennettu ja takaisinluettu, tarvittavat seuranta-/lähdetiedot on päivitetty ja pakolliset tarkistukset ovat valmiit. Aja `python scripts/validate_feeds.py`, jos komentojen suoritusympäristö on käytettävissä. Jos ei ole, tee vastaavat tarkistukset muilla käytettävissä olevilla keinoilla ja kerro rajoite. Älä väitä automaattista testiä ajetuksi, ellei sitä ajettu.

Myös onnistunut haku ilman julkaistavaa uutista kuluttaa vuoron. Onnistuneen ajon jälkeen siirrä `docs/tehtavajono.md`:n seuraava-tehtävä-merkintä täsmälleen yhden kohdan eteenpäin kiinteässä yhdeksän tehtävän järjestyksessä; yhdeksännen jälkeen palaa Tolkieniin. Jos haku tai pakollinen tarkistus jää olennaisesti kesken tai epäonnistuu, älä siirrä vuoroa.

Päivitä onnistuneen ajon lopuksi `data/seurantatila.json`:
- valitun tehtävän `last_successful_check`, `last_period_start`, `last_period_end`, `last_result` (published/no_news), `published_items`, `sources_checked` ja `errors` (tyhjä taulukko);
- ylätason `updated_at` ja `rotation.next_task`, joiden pitää vastata tehtäväjonon seuraavaa vuoroa;
- `automation_instructions.last_successful_run_version` ja `last_successful_run_at`. Kirjaa täsmälleen se `current_version`, jonka vastaavuus käsikirjaan tarkistettiin ajon alussa.

Hae kaikki muutetut tiedostot takaisin GitHubista ja varmista tallennetut arvot. Jos ajo epäonnistuu tai jää kesken, älä muuta tehtävän onnistumisaikaa, ohjeversion viimeisimmän onnistuneen ajon merkintää tai kierron seuraavaa tehtävää. Virheen voi kirjata `errors`-kenttään korvaamatta viimeisintä onnistunutta tilaa.

## 9. Dokumentaation loppukatselmus

Aina kun dokumentaatiota muutetaan tai lisätään:
1. Lue muutoksen jälkeen `README.md`, `docs/seuranta.md` ja `docs/lahteet.md` kokonaan sekä kaikki muut aiheeseen liittyvät dokumentit.
2. Tarkista aiheet, RSS-tiedostot ja URL-osoitteet, aikataulut, lähdeohjeet, vastuut ja toimintatavat ristiin.
3. Etsi vanhentuneet, puuttuvat, päällekkäiset ja ristiriitaiset tiedot myös muista dokumenteista.
4. Korjaa ristiriidat saman työvaiheen aikana tai dokumentoi tarkoitukselliset erot.
5. Hae muutetut dokumentit GitHubista takaisin ja varmista tallennettu sisältö.

## 10. Versionumeron muuttaminen

- Käytä semanttista versiota MAJOR.MINOR.PATCH.
- PATCH tarkoittaa täsmennystä/virheenkorjausta, MINOR uutta taaksepäin yhteensopivaa sääntöä ja MAJOR olennaista muutosta tehtävän rakenteeseen, rajaukseen tai toimintalogiikkaan.
- Kun tämän käsikirjan sitovia ohjeita muutetaan, päivitä versionumero ja saman muutoksen yhteydessä `data/seurantatila.json`:n `automation_instructions.current_version`. Automaattisen testin pitää hylätä niiden ristiriita.
- Älä muuta `last_successful_run_version`-arvoa käsikirjaa päivitettäessä. Se kertoo viimeisimmän onnistuneen ajon version ja päivittyy vasta seuraavan onnistuneen ajon yhteydessä.
- Jokainen onnistunut pääautomaation ajo kirjaa käytetyn version ja ajoajan koneelliseen seurantatilaan. Näin tulos voidaan jälkikäteen yhdistää täsmälliseen ohjeversioon.
- Tämä versionhallinta koskee pääautomaatiota. Erillisen näytösvahdin ohjeita, promptia tai ajastusta ei muuteta tässä työssä.
