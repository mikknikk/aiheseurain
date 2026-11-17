# Pääautomaation toimintakäsikirja

Ohjeversion tunniste: 1.3.1
Viimeksi päivitetty: 2026-11-17

Tämä on pääautomaation ensisijainen ja täydellinen toimintakäsikirja. ChatGPT-automaation asetuksissa oleva kehote on vain vakaa käynnistysosoite. Tehtävien sisältöä ja toimintatapoja ylläpidetään tässä repositoriossa, ei rinnakkaisina kopioina automaation asetuksissa.

## 1. Järjestelmän rajat

- Repository: `mikknikk/aiheseurain`.
- Pääautomaatio käynnistyy päivittäin noin klo 12.00 Europe/Helsinki ja käsittelee täsmälleen yhden yhdeksästä tehtävästä.
- Intialaisten elokuvien näytösseuranta on erillinen päivittäinen automaatio noin klo 05.00 Europe/Helsinki. Se ei kuulu tehtäväkiertoon.
- Pääautomaatio ei tee näytöshakuja eikä muuta `feeds/intialaisten-elokuvien-naytokset.xml`-syötettä tai näytöshistoriaa. Älä sekoita uutis- ja näytösseurantaa.
- Älä luo rinnakkaisia aiheautomaatioita tai muuta aikatauluja tämän käsikirjan perusteella.

## 1.1. Ajastusten ja asetusten hallinnan suojaus

Noudata kaikkia ajoja koskevaa [automaatioiden hallintaperiaatetta](automaation-hallintaperiaatteet.md). Pääautomaation suorittaminen ei anna lupaa muuttaa tämän tai muiden automaatioiden ajastusta, aktiivisuutta, aikataulua, käynnistysohjetta, muita asetuksia tai kohdekeskustelua. Havaitut ongelmat raportoidaan käyttäjälle; niitä ei korjata muuttamalla ajastusta tai asetuksia ilman käyttäjän nimenomaista valtuutusta. GitHubin ohje- tai seurantatilamuutokset eivät muuta ChatGPT:n tehtäväasetuksia.

## 2. Aloitus, ohjeversion tarkistus ja keskeytysehdot

Noudata joka ajolla tätä järjestystä:

1. Lue `README.md` ja tämä käsikirja kokonaan.
2. Lue `data/seurantatila.json`. Tarkista, että `automation_instructions.document` osoittaa tähän tiedostoon ja että `current_version` vastaa tämän dokumentin Ohjeversion tunnistetta.
3. Jos GitHub ei ole käytettävissä, käsikirja tai seurantatila puuttuu tai versiot eivät täsmää, keskeytä ajo. Älä käytä vanhaa promptia, arvattua versiota tai vanhentunutta ohjetta. Älä tee hakuja, julkaisuja, onnistumismerkintöjä tai vuoron siirtoa.
4. Lue kokonaan `docs/tehtavajono.md`, `docs/seuranta.md`, `docs/lahteet.md` ja `docs/saavutettavuus.md`. Lue yhteinen lähdekatalogi `data/source-catalog.json` sekä valitun tehtävän käyttörekisteri `data/sources/{task_id}.json`. Yhdistä jokainen `source_id` katalogin vastaavaan `id`-tietueeseen. Käytä vain valitun tehtävän rekisteriin määriteltyjä lähteitä; älä tulkitse katalogia kaikkien tehtävien yhteiseksi hakulistaksi.
5. Lue `docs/kehityskaytannot.md`, jos muutat skriptejä tai ylläpitokoodia.
6. Valitse seuraava tehtävä `docs/tehtavajono.md`:stä ja varmista, että se vastaa JSONin `rotation.next_task`-arvoa. Jos arvot eroavat, keskeytä ennen hakuja; älä arvaa kumpi on oikein.
7. Lue valitun aiheen ohjeet ja seurantaloki. Tehtävässä 9 lue kokonaan `docs/intialaisen-elokuvan-ohje.md`, `docs/intialaisen-elokuvan-uutiset.md`, `docs/intialaisen-elokuvan-lahteet.md` ja `docs/intialaisen-elokuvan-seuranta.md`. Älä lue tai muuta näytösvahdin ohjeita tai historiaa uutisautomaatiossa.
8. Lue kaikki kymmenen RSS-tiedostoa kokonaan tai hae niiden kaikki itemit: kahdeksan muuta aihefeed-tiedostoa, `feeds/intialaiset-elokuvat.xml` ja `feeds/intialaisten-elokuvien-naytokset.xml`. Näytösfeed luetaan vain aiemman historian/GUIDien säilyttämiseksi; älä tee siihen liittyviä hakuja tai muutoksia.
9. Vertaa valitun tehtävän feediä aiempiin itemeihin ja GUIDeihin. Varmista globaalisti, ettei uusi GUID toistu missään kymmenestä syötteestä. Älä muuta muiden tehtävien sisältöä.
10. Käytä dokumentaatiota ensisijaisena muistijälkenä, älä aiempien keskustelujen tai vanhan automaatiokehotteen muistikuvaa.

## 3. Yhdeksän tehtävän aiheiden rajaukset

Tehtävien kiertojärjestys ja seuraava vuoro määritellään vain tiedostossa `docs/tehtavajono.md`. Älä kopioi tai ylläpidä seuraavaa vuoroa tässä käsikirjassa.

1. **J. R. R. Tolkien:** elämäntyö, kirjallinen perintö, uudet julkaisut ja tutkimus, Tolkien Estate ja oikeudenhaltijat, adaptaatiot (elokuva, TV, pelit), näyttelyt ja tapahtumat. Seuraa erityisesti Suomessa järjestettäviä Tolkien-tapahtumia, kuten näyttelyitä, yleisötapahtumia, con-tapahtumia, luentoja, elokuvanäytöksiä ja muita yleisölle avoimia tilaisuuksia. Erota Tolkienin omat kirjoitukset myöhemmistä toimitetuista julkaisuista ja adaptaatioista.
2. **Taylor Swift:** musiikki, julkaisut, kiertueet, esiintymiset, elokuva/TV, liiketoiminta, palkinnot, hyväntekeväisyys ja julkinen ura. Seuraa myös Suomessa järjestettäviä tai Suomeen liittyviä konsertteja, tapahtumia, fanitapahtumia, kuuntelutilaisuuksia, elokuvanäytöksiä ja näyttelyitä sekä niiden virallisia järjestäjä- ja lipunmyyntitietoja. Vältä vähäpätöistä yksityiselämän juoruilua ja vahvistamattomia suhdeväitteitä.
3. **Saint Dr. Gurmeet Ram Rahim Singh Ji Insan:** julkinen toiminta, viralliset ja oikeudelliset kehitykset, lausunnot, tuotannot, elokuvahankkeet, elokuvien julkaisut, musiikki, kappaleet, musiikkivideot, soundtrackit ja niihin liittyvät julkiset esiintymiset. Seuraa sekä uusia tuotantoja että merkittäviä julkaisu-, levitys- ja vastaanottouutisia. Hae englanniksi, hindiksi ja pandžabiksi sekä nimivariantit/translitteroinnit. Varmista henkilön identiteetti. Erota syytteet, tuomiot, valitukset, viranomaistoimet ja oikeuden ratkaisut.
4. **Muumit:** Tove Janssonin teokset ja perintö, Moomin Characters ja oikeudenhaltijat, kirjat, sarjakuvat, animaatiot, elokuvat, TV, teatteri, pelit, näyttelyt, tapahtumat, lisensointi ja liiketoiminta. Seuraa erityisesti Suomessa järjestettäviä näyttelyitä, museo- ja teemapuistotapahtumia, teatteria, konsertteja, elokuvanäytöksiä, festivaaleja, perhetapahtumia ja muita Muumi-aiheisia yleisötilaisuuksia. Hae suomeksi, ruotsiksi, englanniksi ja japaniksi; käytä myös kirjoitusasuja Muumit/Moomin/Moomins/ムーミン. Erota virallinen uutinen fanisisällöstä.
5. **Wakaliwood:** elokuvateollisuus ja studio, Nabwana I.G.G. ja muut keskeiset tekijät, tuotannot, festivaalit, levitys, näytökset, kansainväliset kiertueet, rahoitus, dokumentit ja Wakaliwoodiin liittyvä Ugandan elokuvakulttuuri. Hae Ugandasta, Itä-Afrikasta ja kansainvälisistä genre- ja festivaalilähteistä sekä soveltuvilla paikalliskielillä. Seuraa myös Suomessa järjestettäviä Wakaliwood-näytöksiä.
6. **Euroviisut:** Eurovision Song Contest, kaikkien maiden kansalliset valinnat ja karsinnat, esikarsinnat, artisti- ja kappalejulkistukset, säännöt, järjestelyt, tulokset, delegaatiot sekä oheis- ja aluekilpailut. Sisällytä Eurovision Song Contest Asia ja muut olennaiset aluekilpailut; älä rajaa seurantaa Euroopan maantieteeseen. Hae eri maiden omilla kielillä ja yleisradioyhtiöiden lähteistä. Seuraa Yleä, UMK:ta, suomalaisia artisteja sekä Suomessa järjestettäviä Euroviisu-konsertteja, fanitapahtumia, katselujuhlia, näyttelyitä, kilpailuja ja muita yleisötilaisuuksia.
7. **Sompote Sands:** thaimaalainen elokuvaohjaaja ja tuottaja, myös Sompote Saengduenchai (สมโพธิ แสงเดือนฉาย) ja muut translitteroinnit. Seuraa elokuvia, tuotantoja, Krua/Chaiyo-studioihin liittyvää relevanttia historiaa, restaurointeja, arkistointia, julkaisuja, näytöksiä, festivaaleja, oikeuksia, levitystä, retrospektiivejä ja tutkimusta. Hae thaiksi ja englanniksi.
8. **Shakkidraamat:** shakkimaailman todelliset ajankohtaiset kiistat, draamat, konfliktit ja kohut – ei fiktiiviset shakkiaiheiset elokuvat tai tavalliset turnaustulokset. Seuraa huijaus- ja vilppisyytöksiä sekä niiden vastineita ja ratkaisuja, pelaajien ja FIDEn tai kansallisten liittojen välisiä jännitteitä, kurinpitomenettelyjä, oikeusjuttuja, järjestö- ja hallintokiistoja, turnausjärjestäjien ja pelaajien konflikteja, sääntö- ja reilun pelin kiistoja sekä merkittäviä henkilöihin, kommentaattoreihin, sisällöntuottajiin ja shakki-instituutioihin liittyviä julkisia kiistoja. Esimerkkejä seurattavista ilmiöistä ovat Carlsenin ja FIDEn jännitteet (mukaan lukien Jeansgate), Kramnikin ja Niemannin kaltaisiin pelaajiin liittyvät vilppisyytökset ja niiden käsittely sekä Danya/Daniel Naroditskyn kuolemaan ja sitä seuranneisiin julkisiin tapahtumiin liittyvät luotettavasti raportoidut kehitykset. Seuraa myös tunnettujen shakkisisällöntuottajien ja -kommentaattorien julkisia somekanavia: olennaiset lausunnot, väitteet, vastineet, keskustelut, yhteistyöt ja konfliktit. Älä kerää rutiinipostauksia. Erota vahvistetut faktat, osapuolten väitteet, vastineet, tutkinta, spekulaatio ja viralliset ratkaisut; käsittele kuolemaan ja henkilöihin kohdistuviin syytöksiin liittyvät tiedot erityisen varovaisesti. Seuraa FIDEä, kansallisia liittoja, järjestäjiä, pelaajia, sisällöntuottajia ja riippumatonta mediaa.
9. **Intialaisen elokuvan uutisraportti:** noudata kokonaan tehtäväkohtaisia intialaisen elokuvan uutisohjeita. Päivitä vain `feeds/intialaiset-elokuvat.xml` ja uutishistorian osio `docs/intialaisen-elokuvan-seuranta.md`:ssä.

## 4. Maailmanlaajuinen lähdehaku ja Suomi

- Hae maailmanlaajuisesti, eri maanosista ja useilla kielillä. Älä rajoitu englanninkieliseen mediaan. Käytä paikalliskieliä, alkuperäisiä kirjoitusasuja, translitterointeja, alueellisia uutistoimistoja, kansallisia yleisradioyhtiöitä, erikoismedioita, virallisia lähteitä ja tapahtumajärjestäjiä. `docs/lahteet.md` on lähtökohta, ei suljettu lista.
- Tarkista jokaisessa kategoriassa erikseen Suomen uutiset ja tapahtumat: suomalaiset toimijat, järjestäjät, tapahtumapaikat, konsertit, elokuvanäytökset, kilpailut, festivaalit ja fanitapahtumat. Tolkienin, Taylor Swiftin, Muumien ja Euroviisujen kohdalla tee lisäksi nimenomainen Suomessa järjestettävien aiheeseen liittyvien tapahtumien haku – älä oleta, että yleinen uutishaku tai virallinen kansainvälinen uutisvirta kattaa tapahtumakalenterit. Tarkista järjestäjien, tapahtumapaikkojen ja lipunmyyjien omat sivut sekä paikalliset tapahtumakalenterit. Nosta uutisarvoinen Suomi-yhteys selvästi esiin. Jos yhteyttä ei löydy, älä mainitse sen puuttumista.
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
- Päivitä `docs/seuranta.md`:hen aihekohtainen tapahtumaloki ja `docs/lahteet.md`:hen uudet olennaiset lähteet sekä niiden käyttöä koskevat muutokset. Tehtävässä 9 päivitä `docs/intialaisen-elokuvan-seuranta.md`: tapahtuma, tapahtuma- ja julkaisupäivä, luotettavuusluokka, tila, lähteet ja niiden riippumattomuus, RSS GUID ja seuraava tarkistustarve. Älä tee päivittäisiä “ei uutisia” -merkintöjä. Päivitä README, jos repositorion rakenne tai automaatioiden työnjako muuttuu.

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

## 6.1. Raporttikohtainen julkaisulaadun portti

Jokainen RSS-syötteen muutos on hyväksytettävä raporttikohtaisessa portissa ennen PR:n yhdistämistä. Noudata kokonaan dokumenttia [RSS-raportin julkaisua edeltävä laadunvarmistus](julkaisuportti.md).

1. Luo jokaiselle muutettavalle syötteelle oma JSON-tarkistusraportti hakemistoon `reports/julkaisuportit/{run_id}.json`. Raportin pitää olla samassa PR:ssä syötemuutoksen kanssa.
2. Arvioi jokainen skeeman määrittelemä kohta. Lähteiden avaaminen, väitteiden vastaavuus, riippumattomuus, epävarmuudet, ajankohdat, seurantajakso, duplikaatit, raportin täydellisyys ja saavutettavuus ovat toimituksellisia arvioita; älä väitä rakennetestin todistavan niitä.
3. Merkitse automaattiset kohdat (`guid_preservation`, `xml_html`, `rss_structure`) hyväksytyiksi vain, kun saman PR:n CI suorittaa niitä vastaavat tarkistukset. CI tarkistaa vanhojen GUIDien säilymisen kohdehaaraan verraten.
4. Jokaisen kohdan tulos on `pass`, `fail` tai `not_applicable`. Ei-soveltuvuudelle annetaan konkreettinen perustelu. Yksikin hylkäys estää hyväksynnän.
5. Jos päätös on `rejected`, älä yhdistä PR:ää, julkaise RSS-muutosta, päivitä viimeisintä onnistunutta tarkistuspistettä tai siirrä tehtäväkierron vuoroa. Korjaa sisältö ja tee uusi tarkistus. Epäonnistunut raportti säilyy PR:n muutoksissa ja CI-artefaktissa tarkasteltavana.
6. Merkitse päätös `approved` vasta, kun kaikki kohdat on hyväksytty. PR:n pakollisen CI-tarkistuksen on silti onnistuttava; hyväksytty toimituksellinen lomake ei ohita automaattisia testejä.
7. Portti koskee kaikkia kymmentä RSS-syötettä. Näytösvahti säilyy erillisenä automaationa, mutta sen syötemuutoksen PR:ssä käytetään samaa julkaisulaadun porttia.

Porttiraportit ovat ajokohtaista auditointijälkeä. Niitä ei kirjoiteta `data/seurantatila.json`-tiedoston viimeisimmän onnistumisen kenttien päälle. Epäonnistunut portti ei muuta viimeisintä onnistunutta tarkistuspistettä. Automaattinen tarkistin varmistaa raportin rakenteen, hyväksyntätilan, automaattisten ehtojen tuloksen ja GUIDien säilymisen; se ei arvioi uutisväitteiden totuutta tai lähteiden riippumattomuutta.

## 7. Tehtäväkohtainen raportti

Toimita tiivis suomenkielinen kooste vain tämän ajon valitusta tehtävästä. Ilmoita seurantajakson alku ja loppu Europe/Helsinki-ajassa. Jos löytyi merkittävä uutinen, linkitä julkaistuun uutiseen ja syötteeseen; nosta Suomi-yhteys näkyvästi esiin. Jos merkittävää uutista ei löytynyt eikä julkaisuongelmia ole, kerro lyhyesti, ettei tämän aiheen osalta löytynyt uutta merkittävää uutista. Älä raportoi muiden aiheiden tilanteesta.

## 8. Onnistuminen, vuoron siirtäminen ja versioloki

Ajo on onnistunut vasta, kun valitun aiheen haku ja arviointi on tehty, mahdolliset julkaisut on tallennettu ja takaisinluettu, tarvittavat seuranta-/lähdetiedot on päivitetty ja pakolliset tarkistukset ovat valmiit. Aja `python scripts/validate_feeds.py`, jos komentojen suoritusympäristö on käytettävissä. Jos ei ole, tee vastaavat tarkistukset muilla käytettävissä olevilla keinoilla ja kerro rajoite. Älä väitä automaattista testiä ajetuksi, ellei sitä ajettu.

Myös onnistunut haku ilman julkaistavaa uutista kuluttaa vuoron. Onnistuneen ajon jälkeen siirrä `docs/tehtavajono.md`:n seuraava-tehtävä-merkintä täsmälleen yhden kohdan eteenpäin kiinteässä yhdeksän tehtävän järjestyksessä; yhdeksännen jälkeen palaa Tolkieniin. Jos haku tai pakollinen tarkistus jää olennaisesti kesken tai epäonnistuu, älä siirrä vuoroa.

Päivitä onnistuneen ajon lopuksi `data/seurantatila.json`:
- valitun tehtävän `last_successful_check`, `last_period_start`, `last_period_end`, `last_result` (published/no_news), `published_items`, `sources_checked` ja `errors` (tyhjä taulukko);
- lisää yksi ajo `data/lahdetarkistukset.json`-tiedostoon: `task_id`, aloitus- ja päättymisajat, tila, `registry_source_ids`, tarkistettujen lähteiden ID:t, tarkistamatta jääneet lähteet syineen sekä lyhyet kieli-/aluekattavuuden huomiot. Päivitä `latest_by_task` vastaamaan saman tehtävän uusinta ajoa. Älä merkitse lähdettä tarkistetuksi, jos vain hakutuloskatkelma löytyi tai alkuperäistä sisältöä ei voitu tarkistaa.
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

## 10. Lähteiden kattavuus ja ajokohtainen loki

- Kaikki lähteiden yhteiset perustiedot ylläpidetään kerran tiedostossa `data/source-catalog.json` (`schemas/lahdekatalogi.schema.json`). Kymmenen tehtäväkohtaista käyttörekisteriä ovat `data/sources/{task_id}.json` (`schemas/lahderekisteri.schema.json`); niissä on vain `source_id`-viittaus sekä tehtäväkohtaiset `critical`-, `last_checked_at`- ja `access_limit`-kentät. Yhdistä viittaukset katalogiin ID:n perusteella. Katalogin lähteitä ei pidä automaattisesti tarkistaa kaikissa tehtävissä. Intialaisen elokuvan uutisilla ja erillisellä näytösseurannalla on eri käyttörekisterit ja tehtävätunnisteet.
- Rekisterin lähde on lähtöpiste, ei suljettu lista eikä luotettavuusleima. Lisää löydetyt olennaiset lähteet rekisteriin vasta, kun nimi, URL, aihe, kieli/alue ja lähdetyyppi on tarkistettu. Älä keksi osoitteita.
- `data/lahdetarkistukset.json` säilyttää ajokohtaisen jäljen. Lue valitun tehtävän käyttörekisteri ennen lähdehakua ja tallenna sen `source_id`-arvot ajon alun lähdejoukoksi. Lue sama rekisteri uudelleen juuri ennen ajolokin kirjoittamista. Kirjaa `registry_source_ids`-kenttään näiden kahden lukukerran ID-joukkojen unioni, jotta myös ajon aikana lisätyt viittaukset jäävät näkyviin. Kirjaa jokainen `registry_source_ids`-arvo täsmälleen joko `checked_source_ids`- tai `unchecked_sources`-kenttään. Jos lähde lisättiin rekisteriin ajon alettua eikä sitä ehditty tarkistaa, kirjaa se tarkistamatta jääneeksi ja syyksi, että se lisättiin ajon aikana. Älä poista lähdeviittauksia käyttörekisteristä kesken aktiivisen ajon; tee rekisterin ylläpitomuutokset vasta ajon päätyttyä. Älä merkitse lähdettä tarkistetuksi, jos vain hakutuloskatkelma löytyi tai alkuperäistä sisältöä ei voitu tarkistaa. Osittainen tai epäonnistunut ajo merkitään vastaavasti; se ei saa näyttää täydelliseltä kattavuudelta.
- `complete` tarkoittaa, että ajon aikana havaitun lähdejoukon kriittiset lähteet on käsitelty; se ei todista kaikkien mahdollisten lähteiden tai koko kieli-/maantieteellisen alueen kattavuutta. Ajon aikana lisätty ei-kriittinen lähde voidaan kirjata tarkistamatta jääneeksi perusteluineen ilman, että se yksin muuttaa ajon osittaiseksi. Kirjaa kattavuushuomiot ja tunnistetut puutteet.
- `data/seurantatila.json`-tiedoston `sources_checked` säilyy yhteenvetolukuna. Yksittäiset lähteet ja epäonnistumissyyt löytyvät ajolokista.
- Älä muuta toisen tehtävän tai toisen automaation lokia. Pääautomaation uutisajo ei kirjaa näytösvahtia eikä tee näytöslähteiden tarkistuksia.

## 11. Versionumeron muuttaminen

- Käytä semanttista versiota MAJOR.MINOR.PATCH.
- PATCH tarkoittaa täsmennystä/virheenkorjausta, MINOR uutta taaksepäin yhteensopivaa sääntöä ja MAJOR olennaista muutosta tehtävän rakenteeseen, rajaukseen tai toimintalogiikkaan.
- Kun tämän käsikirjan sitovia ohjeita muutetaan, päivitä versionumero ja saman muutoksen yhteydessä `data/seurantatila.json`:n `automation_instructions.current_version`. Automaattisen testin pitää hylätä niiden ristiriita.
- Älä muuta `last_successful_run_version`-arvoa käsikirjaa päivitettäessä. Se kertoo viimeisimmän onnistuneen ajon version ja päivittyy vasta seuraavan onnistuneen ajon yhteydessä.
- Jokainen onnistunut pääautomaation ajo kirjaa käytetyn version ja ajoajan koneelliseen seurantatilaan. Näin tulos voidaan jälkikäteen yhdistää täsmälliseen ohjeversioon.
- Tämä versionhallinta koskee pääautomaatiota. Näytösvahdin tehtävä, hakusäännöt ja ajastus säilyvät ennallaan. Sen kehotteeseen lisättiin vain yhteensopivuusvarmistus: se säilyttää `automation_instructions`-osion muuttumattomana, kun se päivittää samaa JSON-seurantatiedostoa.
- Versio 1.0.1: täsmennettiin erillisen näytösvahdin JSON-kenttien säilytys uuden pääautomaation versionhallintaosion käyttöönoton jälkeen.
- Versio 1.0.2: säilytettiin aiempi vaatimus lukea kaikki kymmenen RSS-syötettä jokaisella ajolla ja täsmennettiin globaalin GUID-tarkistuksen sekä lähderekisterin ylläpidon vastuut.
- Versio 1.0.3: otettiin käyttöön yhtenäinen lähderekisteri ja ajokohtainen lähdetarkistusloki; uutiskierron intialaiset uutislähteet erotettiin näytösvahtia varten olevista lähteistä.
- Versio 1.0.4: jaettiin lähderekisterit tehtäväkohtaisiin JSON-tiedostoihin yhteisen skeeman alle, täsmennettiin valitun tehtävän rekisterin lukemista ja päivitettiin ajokohtaisen lähdekattavuuslokin validointi.
- Versio 1.2.0: erotettiin lähteiden yhteiset perustiedot yhteen lähdekatalogiin ja tehtäväkohtaiset käyttöasetukset kymmeneen viittausrekisteriin; päivitettiin skeemat, validointi, ajolokien tarkistus ja automaatio-ohje.
- Versio 1.1.0: laajennettiin Tolkienin, Taylor Swiftin, Muumien ja Euroviisujen Suomen-tapahtumaseurantaa; täsmennettiin Gurmeet Ram Rahim Singhin musiikkiseurantaa sekä Shakkidraamojen todellisten kiistojen ja shakkisisällöntuottajien sosiaalisen median seurantaa.
- Versio 1.2.2: otettiin käyttöön kaikkia automaatioita koskeva käyttäjän valtuutukseen perustuva ajastusten, asetusten ja kohdekeskustelujen suojaus; ohjeen yksityiskohdat ovat yhteisessä hallintaperiaatedokumentissa.

## 12. ChatGPT-ajon vaihekohtainen ajohistoria

Noudata yhteistä [ajohistorian tietomallia](ajohistoria.md). Pääautomaation historiatiedosto on haarassa `run-history/main-automation`, polussa `history.json`, ja tunniste on `main_automation`.

Kirjaa ajo heti käynnistyessä tilaan `running` yksilöllisellä ajotunnisteella. Päivitä samaa ajoa jokaisen merkittävän vaiheen alussa ja lopussa. Käytä vähintään vaiheita `preflight`, `task_selection`, `research`, `source_verification`, `report_drafting`, `publication_gate`, `rss_validation`, `pull_request`, `ci`, `merge` ja `verification`; merkitse soveltumattomat vaiheet `skipped` vain perustellusti. Kirjaa vaiheiden aikaleimat, tulokset sekä lyhyet virheet ja varoitukset.

Ajohistorian kirjoitus tehdään vain omaan `run-history/main-automation`-haaraan GitHubin Contents APIlla tai vastaavalla käytettävissä olevalla GitHub-kirjoitustoiminnolla. Älä koskaan kirjoita ajohistoriaa `main`-haaraan äläkä tee siitä erillistä PR:ää. Jokaisen kirjoituksen jälkeen lue `history.json` samasta haarasta takaisin ja varmista ajotunniste sekä JSON-rakenne. Säilytä viimeiset 30 ajoa. Älä kirjaa salaisuuksia tai raakaa lokisisältöä.

Päätä ajo `succeeded`, `failed` tai `partial` vasta, kun tulos on tiedossa. Jos kirjoitusoikeus puuttuu tai kirjoituksen onnistumista ei voida varmistaa, älä väitä ajohistoriaa päivitetyksi; raportoi rajoite. Ajohistorian kirjaus ei muuta RSS-julkaisun, CI:n, onnistumisen tai tehtäväkierron varsinaisia ehtoja.
