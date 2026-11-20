# Nykyisten seurantojen moduulisiirtymän inventaario ja suunnitelma

**Tarkoitus:** kuvata nykyisten seurantojen omistajuus, ehdotetut moduulirajat, tiedostojen siirtokartta sekä palautettava siirtymä nykyisestä toteutuksesta moduulirekisteriin.  
**Inventaarion päiväys:** 2026-11-17  
**Liittyvä kehitystehtävä:** [#104 – Suunnittele nykyisten aiheiden ja prosessien hallittu moduulisiirtymä](https://github.com/mikknikk/aiheseurain/issues/104)  
**Toteutuksen jatkotehtävä:** [#105 – Siirrä nykyiset aiheet ja näytösvahti itsenäisiin moduulimäärittelyihin](https://github.com/mikknikk/aiheseurain/issues/105)

## 1. Päätulos ja rajaus

Nykyinen kokonaisuus jakautuu **yhdeksään uutisaiheen moduuliin** ja **yhteen erilliseen näytösseurannan prosessimoduuliin**. Yhdeksän uutisaihetta ovat tehtäväjonossa; näytösvahti toimii siitä riippumatta päivittäin. Viikoittainen laatutarkistus on yhteinen järjestelmän auditointitehtävä, ei aihe- eikä sisältömoduuli.

Inventaario perustuu 17.11.2026 main-haarasta luettuihin README-, tehtäväjono-, seuranta-, lähde-, automaatio- ja tietomallidokumentteihin, kymmeneen tehtäväkohtaiseen lähdekäyttörekisteriin, yhteiseen lähdekatalogiin, RSS-syötteiden luetteloon, moduulisopimukseen sekä kahteen olemassa olevaan esimerkkimääritykseen. Tämä on dokumenttipohjainen inventaario; se ei väitä, että ChatGPT:n tehtäväasetukset tai niiden tallennetut aikataulut olisi tarkastettu.

Tämän suunnitelman hyväksyminen tai toteuttaminen **ei aktivoi moduuleja**. #105:n toteutuksessa data/module-registry.json sisältää kymmenen nykyistä moduulia, mutta kaikki merkinnät ovat inactive-tilassa. Rekisteri ei valitse niitä suorituksiin. Nykyisiä automaatioita, ajastuksia, aikavyöhykkeitä, ohjeita, kohdekeskusteluja, RSS-sisältöjä tai seurannan sisältöä ei muuteta tämän inventaarion perusteella.

## 2. Nykyisten moduulien inventaario

Pysyvät tunnisteet ovat #105:ssä toteutettuja moduulitunnisteita. Ne on rekisteröity, mutta kaikki moduulit ovat inactive-tilassa. Tunnisteet on valittu teknisesti vakaiksi; näyttönimet ja kuvaukset voivat muuttua ilman tunnisteen vaihtoa.

| Nykyinen seuranta | Ehdotettu moduuli-ID | Tyyppi | Tehtävä-/lähdetunniste | RSS |
|---|---|---|---|---|
| J. R. R. Tolkien | tolkien | topic | tolkien | feeds/tolkien.xml |
| Taylor Swift | taylor-swift | topic | taylor_swift | feeds/taylor-swift.xml |
| Saint Dr. Gurmeet Ram Rahim Singh Ji Insan | gurmeet-ram-rahim-singh | topic | gurmeet_ram_rahim_singh | feeds/gurmeet-ram-rahim-singh.xml |
| Muumit | muumit | topic | muumit | feeds/muumit.xml |
| Wakaliwood | wakaliwood | topic | wakaliwood | feeds/wakaliwood.xml |
| Euroviisut ja kansalliset karsinnat | euroviisut | topic | euroviisut | feeds/euroviisut.xml |
| Sompote Sands | sompote-sands | topic | sompote_sands | feeds/sompote-sands.xml |
| Shakkidraamat | shakkidraamat | topic | shakkidraamat | feeds/shakkidraamat.xml |
| Intialaisen elokuvan uutisraportti | indian-film-news | topic | intialaiset_elokuvat_uutiset (lähteet); intialaiset_elokuvat (kiertotila) | feeds/intialaiset-elokuvat.xml |
| Intialaisten elokuvien näytösvahti | indian-film-screening-watch | process | intialaiset_elokuvat_naytokset | feeds/intialaisten-elokuvien-naytokset.xml |

### 2.1 Aiheiden sisältörajaukset

Aihemoduulien sisältöä ei pidä laajentaa tai supistaa migraation yhteydessä. Nykyiset rajaukset siirretään sellaisinaan; niiden tiivistäminen tai tulkinnan muuttaminen vaatii erillisen sisältöpäätöksen.

- **Tolkien:** kirjallinen perintö, teokset ja tutkimus, oikeudenhaltijat, viralliset adaptaatiot sekä aiheeseen liittyvät tapahtumat. Erota Tolkienin omat teokset myöhemmästä toimituksellisesta aineistosta ja adaptaatioista. Huomioi Suomessa järjestettävät tapahtumat.
- **Taylor Swift:** musiikki ja julkaisut, kiertueet ja esiintymiset, audiovisuaaliset tuotannot, liiketoiminta, palkinnot, hyväntekeväisyys ja julkinen ura. Huomioi Suomen tapahtumat; vältä vähäarvoista yksityiselämän juoruilua.
- **Gurmeet Ram Rahim Singh:** julkinen toiminta, oikeudelliset ja viralliset tapahtumat, lausunnot, elokuvatuotannot sekä musiikki. Nimi- ja translitterointivariantit on huomioitava; syytteet, tuomiot, valitukset ja viranomaisratkaisut erotetaan täsmällisesti.
- **Muumit:** Tove Janssonin teokset ja perintö, oikeudenhaltijat, kirjat, sarjakuvat, animaatiot, elokuvat, televisio, teatteri, pelit, näyttelyt, tapahtumat, lisensointi ja kulttuurihankkeet. Haku kattaa muun muassa suomen-, englannin- ja japaninkieliset nimimuodot sekä Suomen tapahtumat.
- **Wakaliwood:** studio ja elokuvateollisuus, Nabwana I.G.G. ja muut keskeiset tekijät, tuotannot, festivaalit, levitys, näytökset, kiertueet, rahoitus, dokumentit ja suoraan liittyvä Ugandan elokuvakulttuuri. Vahvistetut tuotantotiedot erotetaan huhuista ja fanisisällöstä.
- **Euroviisut:** Eurovision Song Contest, kaikkien maiden kansalliset valinnat ja karsinnat, artisti- ja kappalejulkistukset, säännöt, järjestelyt, tulokset sekä alueelliset ja oheiskilpailut, mukaan lukien Eurovision Song Contest Asia. Seuranta ei rajaudu Euroopan maantieteeseen; Suomen UMK ja Suomessa järjestettävät tapahtumat huomioidaan.
- **Sompote Sands:** ohjaaja ja tuottaja, nimivariantit, elokuvat, tuotannot, Krua/Chaiyo-studioihin liittyvä historia, restaurointi, arkistointi, julkaisut, esitykset, festivaalit, oikeudet, levitys, retrospektiivit ja tutkimus. Haku kattaa erityisesti thai- ja englanninkieliset lähteet.
- **Shakkidraamat:** todelliset shakkimaailman kiistat ja konfliktit, vilppisyytökset ja vastineet, kurinpitomenettelyt, oikeus- ja hallintokiistat, sääntökiistat sekä merkittävät shakkisisällöntuottajien julkiset lausunnot. Ei fiktiivisiä shakkiteoksia eikä tavallisia turnaustuloksia. Väitteet, näyttö, vastineet ja ratkaisut erotetaan.
- **Intialaisen elokuvan uutiset:** koko Intian eri kielialueiden elokuvateollisuudet, henkilöt, tuotannot, julkaisut, lipputulot, suoratoisto, festivaalit, palkinnot ja alan tapahtumat. Haku kattaa paikalliset kirjoitusjärjestelmät ja translitteroinnit; Suomen elokuvanäytökset eivät kuulu tähän moduuliin.

### 2.2 Erillinen prosessimoduuli

**Intialaisten elokuvien näytösvahti** on process-tyyppinen moduuli, ei uutisaihe. Se etsii Suomessa järjestettäviä intialaisten elokuvien näytöksiä, ennakko- ja erikoisnäytöksiä, festivaaleja ja muita yleisölle avoimia elokuvatapahtumia. Se ylläpitää näytösten nykytilaa ja append-only-muutoshistoriaa, säilyttää myös menneet ja peruutetut näytökset sekä julkaisee erilliseen RSS-syötteeseen.

Näytösvahti käyttää erillistä päivittäistä suorituspolkua eikä kuluta yhdeksän tehtävän kiertoa. Sen lähderekisteri, seurantatila, käsikirja, RSS ja muutoshistoria pysyvät erillisinä uutisaiheen vastaavista tiedoista. Olemassa oleva esimerkkimääritys on vain sopimusesimerkki; se ei ole tuotantomääritys eikä osoita yleisen tapahtumavahdin moottorin olevan valmis.

### 2.3 Lähderekisterien kieli- ja aluekattavuuden lähtötilanne

Seuraava yhteenveto on muodostettu kymmenen tehtäväkohtaisen käyttörekisterin source_id-viittauksista ja yhteisen lähdekatalogin kieli-/aluekentistä 17.11.2026. Määrä tarkoittaa rekisterissä olevia lähdeviittauksia, ei lähteiden laatua, tarkistettujen lähteiden määrää eikä kattavuuden prosenttiosuutta.

| Seuranta | Lähdeviittauksia | Katalogiin merkityt kielet | Katalogiin merkityt alueet |
|---|---:|---|---|
| Tolkien | 28 | de, en, es, eu, fi, fr, it, pt-BR | BR, DE, ES, FI, FR, GLOBAL, IT, LATAM, NZ, UK, US |
| Taylor Swift | 10 | en, fi, pt-BR | BR, FI, GLOBAL, US |
| Gurmeet Ram Rahim Singh | 7 | en, hi, pa | IN-CH, IN-HR, IN-NATIONAL, IN-PB |
| Muumit | 14 | en, fi, ja, sv | FI, GLOBAL, JP, SE, UK |
| Wakaliwood | 5 | en | EAST-AFRICA, UG |
| Euroviisut | 10 | bn, en, fi, ko, ms, ne, sv, th, tl, vi | ASIA, EUROPE, FI, GLOBAL |
| Sompote Sands | 6 | en, ja, th | JP, TH |
| Shakkidraamat | 7 | de, en, fi | EUROPE, FI, GLOBAL, NORTH-AMERICA |
| Intialaisen elokuvan uutiset | 40 | as, bn, en, fi, hi, kn, ml, mr, or, pa, ta, te | FI, IN-AP, IN-AS, IN-KA, IN-KL, IN-MH, IN-NATIONAL, IN-OD, IN-PB, IN-PY, IN-TG, IN-TN, IN-WB |
| Näytösvahti | 11 | en, fi, ta | FI |

Kielikoodit ovat lähdekatalogin tallentamia tunnisteita (esimerkiksi te = telugu, ta = tamili, kn = kannada, ml = malajalam, bn = bengali, mr = marathi, pa = pandžabi, as = assami ja or = odia). Aluekoodit ovat projektin omia luokittelutunnisteita, eivät hallinnollisten rajojen täydellinen kuvaus.

**Havaitut kattavuusaukot ja tulkintarajat:**

- Tolkienin rekisteri kattaa useita Euroopan kieliä ja lähteitä Brasiliasta, mutta rekisterin omat muistiinpanot nimeävät Itä-Euroopan, Aasian ja muun Latinalaisen Amerikan paikalliskieliset toimitukselliset lähteet jatkotyöksi.
- Taylor Swiftin rekisterissä englanti hallitsee; portugali ja suomi ovat mukana, mutta muut kuin englanninkieliset alueelliset lähteet ovat edelleen tunnistettu kehityskohde.
- Gurmeet Ram Rahim Singhin lähteet painottuvat Pohjois-Intiaan ja englantiin, hindiin sekä pandžabiin.
- Muumien rekisterissä on suomi, ruotsi, englanti ja japani, mikä vastaa nykyistä lähdepohjaa; muiden kielialueiden lähteitä ei pidä olettaa katetuiksi.
- Wakaliwoodin lähderekisteri on pieni ja englanninkielinen. Ugandan paikalliskielinen uutis- ja elokuvakulttuurin lähdepohja vaatii jatkotyötä.
- Euroviisujen rekisteri sisältää eurooppalaisten kielten lisäksi useita Aasian kieliä ja alueellisen kilpailun; kaikkien kansallisten yleisradioyhtiöiden ja maiden kattavuus ei silti ole osoitettu.
- Sompote Sandsin rekisteri painottuu thaihin, englantiin ja japaniin. Thaikielisten ensisijaisten arkisto- ja kulttuurilähteiden saatavuus on keskeinen.
- Shakkidraamojen rekisteri painottuu englantiin ja Eurooppaan; Aasian, Afrikan ja Latinalaisen Amerikan lähteet ovat tunnistettu aukko.
- Intialaisen elokuvan uutisrekisteri kattaa laajimman kieli- ja aluejoukon (mm. telugu, tamili, kannada, malajalam, hindi, bengali, marathi, pandžabi, assami ja odia). Se ei kuitenkaan todista, että kaikkien kielialueiden uutisvirrat tai lähteet olisivat kattavia.
- Näytösvahdin lähderekisterin maantieteellinen rajaus on tarkoituksella Suomi. Se on prosessimoduulin rajaus, ei puute.

Nämä tiedot siirretään #105:ssä hakuprofiilien lähtötiedoiksi, mutta lähdekatalogi säilyy yhteisenä totuuslähteenä. Kattavuusaukkojen täyttäminen tai lähteiden lisääminen ei kuulu moduulisiirtymän automaattiseen sisältömigraatioon; se vaatii erillisen toimituksellisen päätöksen.

## 3. Nykyisten tiedostojen ja moduulien siirtokartta

| Nykyinen tieto tai tiedosto | Nykyinen vastuu | Suunniteltu käsittely #105:ssä |
|---|---|---|
| docs/seuranta.md | Aihekohtaiset rajaukset, uutishistoria ja raportointijaksot | Aiheiden sisältörajaukset moduuleihin; uutishistoria jää historialliseen seurantatietoon. Yleiset raportointisäännöt jäävät yhteiseen ohjeeseen. |
| docs/lahteet.md | Yleiset lähdeperiaatteet ja aihekohtaiset hakustrategiat | Yleiset lähdeperiaatteet pysyvät yhteisinä; aihekohtaiset hakuprofiilit ja poikkeukset siirretään moduuleihin vain, kun ne ovat rakenteisesti ilmaistavissa. |
| data/source-catalog.json | Lähteiden yhteiset perustiedot, URL:t, kielet, alueet ja luotettavuusluokka | Säilyy yhteisenä kanonisena katalogina. Moduulit viittaavat lähde-ID-arvoihin; lähteiden perustietoja ei kopioida moduuleihin. |
| data/sources/{task_id}.json (10 tiedostoa) | Tehtäväkohtaiset lähdeviittaukset, kriittisyys, tarkistusajat ja käyttörajoitteet | Säilyy tehtäväkohtaisen lähdekäytön kanonisena tietona siirtymävaiheessa. Moduulin source_refs viittaa samoihin tunnisteisiin; #105 päättää, tarvitaanko myöhemmin erillinen moduulin käyttöprofiili vai pidetäänkö tämä rekisteri. |
| docs/intialaisen-elokuvan-ohje.md | Intialaisen elokuvan uutisseurannan laaja sisältöohje | Sisältörajaukset ja seurattavat kohteet uutismoduulin määritykseen; yleiset toimitukselliset säännöt yhteiseen ohjeeseen. |
| docs/intialaisen-elokuvan-uutiset.md | Uutisraportin haku- ja sisältöohje | Uutismoduulin hakuprofiilit, kielialueet ja raporttikohtaiset vaatimukset; ei näytöshakua. |
| docs/intialaisen-elokuvan-lahteet.md | Intialaisen elokuvan toimitukselliset lähdeohjeet | Uutismoduulin lähdeviitteet ja alue-/kieliprofiilit; näytöksiä koskeva sisältö pidetään erillisen näytösprosessin vastuulla. |
| docs/intialaisen-elokuvan-seuranta.md | Uutishistoria ja näytösseurannan historiallinen osio samassa tiedostossa | Uutishistoria säilytetään uutisprosessin historiassa; näytöshistoria siirretään tai viitataan erillisen näytösvahdin jo kanoniseen data/naytosten-muutoshistoria.json-tietoon. Ei historian kopiointia tai poistamista. |
| docs/intialaisten-elokuvien-naytosseuranta.md | Näytösvahdin ensisijainen käsikirja | Säilyy prosessimoduulin toimintakäsikirjana tai sen selittävänä dokumenttina; moduulimääritykseen siirretään vain rakenteiset asetukset. |
| data/naytosten-muutoshistoria.json ja skeema | Näytösten nykytila ja append-only-muutostapahtumat | Säilyvät näytösprosessin kanonisena historiana; moduulisiirto ei muuta tapahtumien tunnisteita tai järjestystä. |
| data/seurantatila.json | Tehtäväkierto, onnistumispisteet ja automaatioiden ohjeversiot | Säilyy nykyisen tuotantopolun kanonisena tilana siirtymän ajan. Moduulikohtaisen tilarekisterin toteutus kuuluu #106:een. |
| docs/tehtavajono.md | Yhdeksän uutistehtävän kiertojärjestys ja seuraava vuoro | Säilyy tehtäväjonon kanonisena järjestyksenä; moduulirekisteri ei korvaa jonotusta eikä muuta järjestystä. |
| feeds/*.xml ja data/feed-catalog.json | Julkaistut raportit, GUIDit ja syötekatalogi | Säilyvät julkaisu- ja historiatietona. Moduuli viittaa sovittuun julkaisuun; vanhoja itemeitä tai GUIDeja ei siirretä, generoida uudelleen tai poisteta. |
| prompts/*.txt | ChatGPT-automaation asetuksiin kopioitavat käynnistyskehotteet | Pysyvät automaatiokohtaisina käynnistysosoitteina; niitä ei muuteta moduulimigraation yhteydessä ilman erillistä päätöstä ja asetusten manuaalista synkronointia. |
| docs/paaautomaation-ohje.md ja näytösvahdin käsikirja | Nykyisten automaatioiden toiminnan ensisijaiset ohjeet | Yhteiset toimintaperiaatteet ja prosessikohtaiset menettelyt erotellaan. Käsikirjoja ei poisteta ennen kuin korvaava suorituspolku on hyväksytty. |
| modules/topics/*/module.json ja modules/processes/*/module.json | Nykyisten seurantojen koneelliset moduulimääritykset | Kymmenen itsenäistä määritystä; rekisteröity inactive-tilassa ja validoitu nykyisiä lähderekistereitä vasten. |
| modules/processes/indian-film-screening-watch/event-type.json | Näytösvahtimoduulin tapahtumatyyppi | Viittaa #109:n yleiseen film-screening-tyyppiin; passiivinen moduulikohtainen määritys. |
| examples/seurantamoduulit/*.json | Sopimuksen esimerkit | Säilyvät testiesimerkkeinä; eivät ole tuotantomääritysten lähde. |

## 4. Yhteisten, moduulikohtaisten ja teknisten tietojen rajat

### 4.1 Moduulin omistamat sisältötiedot

Aihemoduuli omistaa vain kyseisen aiheen semanttisen määrittelyn: pysyvän moduulitunnisteen, tyypin ja määritysversion; aiheen nimen, kuvauksen, rajauksen, sisällytys- ja poissulkusäännöt; seurattavat henkilöt, teokset ja organisaatiot nimivariantteineen; aihekohtaiset hakuprofiilit, kielet ja alueet; aihekohtaiset lähdeviitteet sekä toimitukselliset poikkeukset.

Prosessimoduuli omistaa vastaavasti prosessin semanttiset asetukset, kuten tapahtumatyypit, maantieteellisen rajauksen, tapahtuman tunnistusavaimet, epävarman yhdistämisen säännöt ja historian säilyttämisen vaatimukset.

### 4.2 Yhteiseen ytimeen kuuluvat tiedot

Seuraavat säännöt ovat yhteisiä, eikä niitä kopioida jokaiseen moduuliin:

- yleinen lähteiden arviointi ja väitteiden varmennuksen periaate;
- raportin kieli- ja saavutettavuuden yleisvaatimukset;
- julkaisulaadun portti, RSS/XML:n rakennetarkistukset ja GUIDien säilyttäminen;
- tehtäväjonon yleinen valinta- ja virheenkäsittely;
- moduulien rekisteröinti, sopimusvalidointi ja moduulien eristäminen;
- yleinen ajon tunniste, vaiheistus, lokitus ja palautumisen periaate.

Yhteinen sääntö säilyy yhdessä ensisijaisessa dokumentissa tai yhteisessä tietosopimuksessa. Moduuli voi viitata sääntöön tai määritellä vain sallitun aiheen vaatiman tarkennuksen.

### 4.3 Tekniseen suoritusympäristöön kuuluvat tiedot

Seuraavia ei tallenneta moduulin sisältömääritykseen:

- ajastukset, kellonajat, aikavyöhykkeet, aktiivisuus ja kohdekeskustelut;
- ChatGPT-tehtävien tunnisteet tai palvelun sisäiset asetukset;
- tekoäly- tai tutkimuspalvelun tarjoaja, mallin nimi tai reititysvalinta;
- API-avaimet, salaisuudet, käyttöoikeustunnukset ja ympäristömuuttujat;
- GitHub-tokenit, Actions-asetukset, julkaisusalaisuudet ja tekniset polut;
- ajokohtaiset onnistumisajat, lukitukset ja väliaikainen käyttötila.

Näitä hallitaan omissa teknisissä asetuksissaan ja tulevissa yhteisen ytimen sopimuksissa. Moduulin sisältöä voi näin muuttaa vaihtamatta ajastinta tai palveluntarjoajaa.

## 5. Havaitut päällekkäisyydet ja ristiriitariskit

1. **Intialaisen elokuvan uutis- ja näytösseurannan historiallinen limittyminen.** docs/intialaisen-elokuvan-seuranta.md sisältää molempien seurantojen osioita, vaikka uutis- ja näytösprosessilla on erilliset lähderekisterit, RSS:t ja koneellinen näytöshistoria. #105:n tulee säilyttää molemmat historiat mutta tehdä omistajuus eksplisiittiseksi.
2. **Sama aihe esiintyy eri tunnisteillä eri tietomalleissa.** Intialaisen elokuvan uutisaiheen tunniste intialaiset_elokuvat on kiertotilan avain, lähderekisterin tunniste on intialaiset_elokuvat_uutiset ja näytösvahdin tunniste on intialaiset_elokuvat_naytokset. Näitä ei saa yhdistää näyttönimen perusteella.
3. **Lähteen perustiedot ja tehtäväkohtainen käyttö ovat eri asioita.** data/source-catalog.json omistaa yhteiset tiedot; kymmenen data/sources/*.json-rekisteriä omistavat tehtäväkohtaisen kriittisyyden ja käyttörajoitteet. Moduulimäärittely ei saa kopioida katalogin tietoja rinnakkaisiksi totuuksiksi.
4. **Yleiset ja aihekohtaiset säännöt ovat sekoittuneet joihinkin käsikirjoihin.** #105:n tulee siirtää vain aihekohtaiset erot moduuliin ja pitää yleiset julkaisun, luotettavuuden ja saavutettavuuden säännöt yhteisinä.
5. **Vanhoissa intialaisen elokuvan dokumenteissa on aiemman repositorion viittauksia.** Ne ovat historiallista dokumentaatiota, eivät automaattisesti nykyisen Aiheseuraimen teknisiä polkuja. Linkkien ja omistajuuden korjaus tehdään hallitusti, ei massakorvauksena.
6. **Näytösvahti ja yleinen tapahtumavahti eivät ole sama toteutus.** #109 yleistää tapahtumakäsittelyä; näytösvahdin elokuvakohtaiset tunnistus- ja historian säännöt säilyvät sen prosessikohtaisena laajennuksena.
7. **Elokuvahavaintojen ja kriteeriosumien käsittely liittyy moduulirajaan mutta ei ole sama asia.** #66:n havaintorekisteri ja #67:n hyväksytyt hakukriteerit sekä jatkotoimet on sovitettava #109:n yleiseen tapahtumamalliin erillisessä suunnittelussa. Niitä ei saa sulauttaa tähän dokumenttiin oletuksella, että kaikki ovat yksi rekisteri.

## 6. Ehdotettu siirtymäjärjestys ja riippuvuudet

| Vaihe | Tehtävä | Riippuvuus / hyväksymisehto |
|---|---|---|
| 0 | Inventaario ja omistajuus | Tämä #104-dokumentti; ei tuotantomuutoksia. |
| 1 | Tapahtumavahtikyvykkyyden yleistäminen | #109; sovitaan yleinen tapahtumasopimus ja näytöslaajennuksen rajat. |
| 2 | Nykyisten aihe- ja prosessimääritysten muodostaminen | #105; käyttää #102:n sopimusta, #103:n rekisteriä ja tämän dokumentin siirtokarttaa. |
| 3 | Moduulikohtaisen tilan, tarkistuspisteiden ja historian erottaminen | #106; nykyinen seurantatila ja append-only-historiat säilyvät siirtymän ajan. |
| 4 | AI- ja tutkimuspalvelujen adapterisopimukset | #107; moduulin sisältö ei saa riippua palveluntarjoajasta. |
| 5 | Yhteinen suoritusorkestrointi ja käyttöönotto | #108; vasta kun moduulit, tila, adapterit ja palautustestit ovat hyväksyttyjä. |

#66 ja #67 liittyvät rinnakkaiseen elokuvaseurannan kehityshaaraan. Niiden tietomallien suhde #109:n tapahtumasopimukseen selvitetään ennen kyseisten toteutusten yhdistämistä. Ne eivät muuta yhdeksän uutisaiheen ja näytösvahdin moduulijakoa.

## 7. Vaiheittainen migraatiomenettely

1. **Lähtötilanteen inventaario:** tallenna siirron lähtöhetken Git-commit, moduulien lähdetiedostot, kaikkien RSS-syötteiden GUID-joukot, lähdekatalogin ja käyttörekisterien tunnisteet, seurantatilan tarkistuspisteet sekä näytöshistorian tapahtumien määrä ja viimeinen tunniste. Älä muuta tuotantotietoja.
2. **Määritysten muodostus erillisessä haarassa:** luo moduulien ehdotetut JSON-määritykset #102:n skeeman mukaisesti. Käytä olemassa olevia lähde-ID:itä; älä kopioi lähteiden nimiä tai URL-osoitteita moduuleihin. Säilytä Markdown-käsikirjat selittävinä ja yksityiskohtaisina lähteinä.
3. **Rakenne- ja semanttinen vertailu:** validoi jokainen määritys #102:n sopimuksella ja #103:n lataajalla. Tarkista tunnisteet, tyyppi, versio, lähdeviitteiden olemassaolo, kieli- ja alueprofiilit, aiheiden sisällytys-/poissulkurajaukset ja erityissäännöt alkuperäisiä käsikirjoja vasten.
4. **Passiivinen rinnakkaisluku:** testaa moduulien lataus ja validointi. Tuotantorekisterissä olevat kymmenen merkintää pysyvät inactive-tilassa. Uusi polku ei saa kirjoittaa RSS:ää, lähdekäyttörekistereitä, tehtäväjonoa, seurantatilaa tai näytöshistoriaa.
5. **Vertailu ja hyväksyntä:** dokumentoi jokaisesta moduulista erot nykyiseen käsikirjaan ja varmista, ettei aiheiden sisältö, tehtävien järjestys, lähteiden käyttö tai julkaistu historia muutu. Käyttäjän hyväksyntää vaativat sisältömuutokset nostetaan erikseen päätettäviksi.
6. **Erillinen käyttöönottopäätös:** tuotantorekisterin aktivointi ja tuotantopolun vaihtaminen tehdään vasta erillisessä #105/#108-vaiheessa, hyväksymiskriteerien täytyttyä ja käyttäjän nimenomaisen käyttöönottohyväksynnän jälkeen. Pelkkä PR:n yhdistäminen ei aktivoi moduulia eikä muuta ChatGPT:n tehtäväasetuksia.

## 8. Palautus ja historian säilyttäminen

- Nykyiset Markdown-ohjeet, lähderekisterit, RSS-syötteet, seurantatila ja näytöshistoria säilytetään muuttumattomina, kunnes uusi toteutus on hyväksytty ja tuotantokäyttö on erikseen päätetty.
- Moduulimääritykset ja rekisterimuutokset toimitetaan versionhallinnan kautta. Epäonnistuneen migraation voi peruuttaa palauttamalla rekisterin ja määritykset edelliseen hyväksyttyyn commit-versioon; vanhaa sisältöä ei tarvitse rekonstruoida.
- Rinnakkaisvaiheessa ei tehdä kaksinkertaisia tuotantokirjoituksia. Uusi toteutus on vain lukeva, kunnes omistajuuden siirto on hyväksytty.
- RSS-artikkelien GUIDit, julkaistut itemit ja syöteosoitteet säilytetään. Niitä ei luoda uudelleen moduulitunnisteen perusteella.
- Näytöshistorian events-loki pysyy append-only-muodossa. Korjaukset tehdään uusina tapahtumina; aiempia tapahtumia ei muokata tai poisteta.
- Moduulin määritysversio ja moduulin pysyvä tunniste eivät korvaa vanhojen ajojen tehtävä-ID:tä tai RSS-GUIDeja. Vanhojen ajojen viittaukset säilytetään alkuperäisinä.
- Jos vertailu tai takaisinlukutarkistus epäonnistuu, tuotantoon siirtymistä ei tehdä. Viimeisin onnistunut tarkistuspiste ja nykyinen julkaisu säilyvät.

## 9. Käyttäjän hyväksyntää edellyttävät päätökset

Tämä inventaario ei tee seuraavia päätöksiä käyttäjän puolesta:

- muutetaanko minkään aiheen sisältörajausta, painotusta, kieliä tai maantieteellistä kattavuutta;
- poistetaanko, yhdistetäänkö tai lisätäänkö seurattavia aiheita, lähteitä tai tapahtumatyyppejä;
- muutetaanko yhdeksän tehtävän kiertojärjestystä tai näytösvahdin erillisyyttä;
- otetaanko moduuleja tuotantorekisteriin ja milloin niiden suoritusvastuu siirtyy;
- muutetaanko automaatioiden ajastuksia, aikavyöhykkeitä, käynnistysohjeita, aktiivisuutta tai kohdekeskusteluja;
- valitaanko uusi tekoäly-, tutkimus-, ajastus- tai tallennuspalvelu.

Tekniset toteutuspäätökset, jotka eivät muuta näitä sisältö- tai käyttöönottovalintoja, voidaan valmistella omissa kehitystehtävissään.

## 10. #105:n toteutuksen tarkistuslista

- [x] Jokaiselle kymmenelle seurannalle on oma validoitu määritystiedosto ja pysyvä tunniste.
- [x] Kaikki yhdeksän uutisaihetta ovat topic-tyyppisiä ja näytösvahti process-tyyppinen.
- [x] Jokaisen moduulin rajaus, hakuprofiilit, kielet, alueet ja erityissäännöt on siirretty nykyisiä ensisijaisia ohjeita vastaavasti ja tarkistettu automaattisesti.
- [x] Kaikki lähdeviitteet osoittavat olemassa oleviin yhteisen katalogin source_id-tunnisteisiin ja oikeisiin tehtäväkohtaisiin lähderekistereihin.
- [x] Yhteisiä sääntöjä tai lähteiden perustietoja ei kopioida moduuleihin rinnakkaisiksi totuuksiksi.
- [x] Intialaisen elokuvan uutis- ja näytösseurannan omistajuus sekä historiat ovat erilliset.
- [x] Tuotantorekisterin kymmenen merkintää pysyvät inactive-tilassa; yhtään moduulia ei aktivoida tämän migraation yhteydessä.
- [x] Migraatiovalidaattori lataa kaikki moduulit väliaikaisen aktiivisen rekisterikopion kautta ja vertaa lähdeviitteet ilman tuotantokirjoituksia.
- [x] RSS-itemit, GUIDit, tehtäväjono, seurantatila ja näytöshistoria säilyvät muuttumattomina.
- [x] Palautus edelliseen hyväksyttyyn määritysversioon on dokumentoitu. Koska vanhoja kanonisia tiedostoja ei muuteta, palautus tapahtuu moduulimäärittelyt ja rekisterimerkinnät sisältävän Git-commitin palautuksena.

## Muutoshistoria

- **1.2.0 – 2026-11-20:** päivitettiin Muumien lähdeviitteiden määrä 14:ään vastaamaan nykyistä tehtäväkohtaista lähderekisteriä; moduulit pysyvät inactive-tilassa.
- **1.1.0 – 2026-11-18:** päivitettiin inventaario vastaamaan #105:n toteutusta: kymmenen moduulia on rekisteröity inactive-tilassa, moduulihakemiston määritykset on lisätty ja näytösvahtimoduuli käyttää #109:n tapahtumatyyppiviitettä.
- **1.0.0 – 2026-11-17:** ensimmäinen nykyisten aihe- ja prosessimoduulien inventaario, tiedostojen siirtokartta, omistajuusrajat, päällekkäisyysriskit, riippuvuudet sekä palautettava migraatiosuunnitelma.
