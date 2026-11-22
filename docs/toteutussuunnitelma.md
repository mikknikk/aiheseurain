# Aiheseuraimen toteutussuunnitelma

**Versio:** 0.3.59  
**Päiväys:** 22.11.2026  
**Tila:** suunnitteluluonnos – hyväksytyt arkkitehtuuriperiaatteet ja ensimmäisen vaiheen tehtävänjakomalli kirjattu, tekniset yksityiskohdat avoinna  
**Perusta:** [Vaatimusmäärittely 0.12.16](vaatimusmaarittely-uudistus.md)

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
- `data/tehtava.json` on ainoa varsinainen tehtäväpyyntö ja sisältää kerrallaan yhden aktiivisen tehtävän. Rinnakkaista tehtäväpyynnön tietolähdettä tai vaihtoehtoista tehtäväpakettia ei oteta käyttöön ensimmäisessä versiossa.
- Tehtäväpyyntö sisältää rakenteiset tehtävätiedot, valmiin `resolved_config`-snapshotin sekä viittaukset tarvittaviin Markdown-ohjeisiin ja kyseisen aiheen RSS-historiaan. Ohjetekstejä tai RSS-historiaa ei kopioida tehtäväpyyntöön.
- Raportintuottajan käynnistys-/nouto-ohje on eri asia kuin varsinainen tehtäväpyyntö: se kertoo, miten tehtävä haetaan ja käsitellään, kun taas `data/tehtava.json` sisältää yksittäisen ajon tiedot.
- Tehtäväpyynnön tarkka JSON-rakenne, viittauskenttien nimet ja tilapäivitysten toteutus määritellään myöhemmin toimitussopimuksessa.

Tehtävän jäljitettävyys perustuu kahteen päärevisioon sekä erilliseen RSS-historian lähtörevisioon:

- `software_revision` yksilöi ohjelmistorepon muuttumattoman Git-commitin, jonka ohjelmistokoodia, yhteisiä skeemoja ja ohjelmiston yleisiä ohjeita tehtävän käsittelyssä käytetään.
- `instance_revision` yksilöi instanssirepon muuttumattoman Git-commitin, jonka aihe-, tehtävä-, profiili-, lähderekisteri- ja instanssikohtaisia ohjemäärityksiä tehtävässä käytetään.
- `history.revision` yksilöi RSS-historian tarkan lähtöcommitin instanssirepositoriossa. Se voi olla sama kuin `instance_revision`, mutta voi myös osoittaa aiempaan historian lähtötilaan.

Näitä tunnisteita ei yhdistetä yhdeksi kentäksi: ohjelmiston ja instanssin muutokset ovat toisistaan riippumattomia. Tehtäväpyynnön täsmälliset kentät ja niiden validointisäännöt määritellään toimitussopimuksessa. Kaikki tehtävässä luettavat tiedostot yksilöidään repositoriokohtaisesti ja haetaan kyseisen repositorion ilmoitetusta muuttumattomasta revisiosta. Viittauksen polku ei yksin määritä repositoriota. Tehtäväpyynnön tiedostoviittauksissa käytetään loogista `repository`-tunnistetta: `software` tarkoittaa yhteistä ohjelmistorepositoriota ja `instance` kyseistä instanssirepositoriota. Tunniste ratkaistaan käyttöönoton repositoriomäärityksestä; varsinaisia repositorioiden nimiä ei kovakoodata yhteiseen tietosopimukseen.

Aiheseuraimelle määritellään yksi yleinen `timezone`-asetus, jonka oletusarvo on `Europe/Helsinki`. Asetuksen arvo on IANA-aikavyöhyketunniste. Sitä käytetään kaikissa Aiheseuraimen muodostamissa aikaleimoissa, seuranta-aikaväleissä ja käyttäjälle näytettävissä ajoissa. Lähteelle mahdollisesti määritelty oma aikavyöhyke vaikuttaa vain ilman aikavyöhyketietoa olevan lähdeaineiston ajan tulkintaan; se ei muuta Aiheseuraimen yleistä aikavyöhykettä eikä sen muodostamien aikaleimojen esitystapaa. Aikaleimat esitetään ISO 8601 -muodossa paikallisena päivänä ja kellonaikana sekä aina mukana olevalla numeerisella UTC-offsetilla: `YYYY-MM-DDTHH:mm:ss±HH:mm` (esimerkiksi `2026-11-22T18:30:00+02:00`). Offsetin on vastattava asetetun IANA-aikavyöhykkeen sääntöjä kyseisenä hetkenä; `Z`-merkintää tai aikavyöhykkeettömiä arvoja ei käytetä. Sekunnit ovat pakollisia, eikä desimaaliosia hyväksytä. Arvon on vastattava todellista kalenteripäivää, kellonaikaa ja aikavyöhykkeen offsetia; virheellisiä arvoja ei normalisoida. Aikaleimoja verrataan ja järjestetään niiden yksiselitteisten ajanhetkien perusteella. Kesä- ja talviajan muutokset määräytyvät IANA-aikavyöhyketietojen mukaan.

Yleinen `timezone` sisällytetään jokaiseen tehtäväpyynnön `resolved_config`-snapshotiin, jotta raportintuottaja käyttää täsmälleen samaa aikavyöhykettä. `period`-objekti ei tarvitse erillistä aikavyöhykekenttää. Lähteen aikaleima, jossa on jo UTC-offset tai yksiselitteinen aikavyöhyketieto, tulkitaan ensisijaisesti sen mukaisesti. Jos aikaleimassa ei ole aikavyöhyketietoa, käytetään seuraavaa etusijajärjestystä: (1) lähteen dokumentoima aikavyöhyke, (2) lähderekisteriin nimenomaisesti määritelty aikavyöhyke, (3) lähteen julkaisumaan tai toimituksen sijainnin perusteella luotettavasti päätelty aikavyöhyke. Lähderekisterin aikavyöhyke on valinnainen IANA-tunniste, ja sen yhteydessä kirjataan tiedon alkuperä: lähteen ilmoittama tieto tai ylläpidon tekemä päätelmä. Lähteen maata ei käytetä automaattisena oletuksena, jos tarkempi tieto on saatavilla; kansainvälisen julkaisijan tai usealla aikavyöhykkeellä toimivan toimituksen aikavyöhykettä ei päätellä pelkän maan perusteella. Jos aikavyöhykettä ei voida luotettavasti määrittää, lähdeaikaa ei arvata eikä sitä käytetä aikarajaukseen ennen kuin tulkinta voidaan ratkaista. Lähteiden ajat muunnetaan Aiheseuraimen yleiseen aikavyöhykkeeseen raporteissa ja käyttöliittymässä. Alkuperäinen lähdeaikaleima, mahdollinen alkuperäinen offset/aikavyöhyke sekä tulkinnassa käytetyn aikavyöhykkeen alkuperä voidaan säilyttää jäljitettävyyttä varten.

Tehtäväpyynnön `period`-objekti sisältää:

- `from`: pakollinen yleisen `timezone`-asetuksen mukainen aikaleima, josta seuranta alkaa. Arvon on noudatettava edellä määriteltyä ISO 8601 -muotoa ja sisältää oikea UTC-offset.
- `to`: yleisen `timezone`-asetuksen mukainen aikaleima tai `null`. Jos arvo on aikaleima, sen on noudatettava samaa täsmällistä muotoa ja sen on oltava ajallisesti myöhempi kuin `from`; yhtä suuri tai aikaisempi arvo hylätään. Aikaleima rajaa haun ennalta määrättyyn päätepisteeseen. `null` tarkoittaa, ettei tehtäväpyyntö aseta päätepistettä; raportintuottaja määrittää toteutuneen päättymishetken ja kirjaa sen ajon metadataan.

Erillistä `cutoff_at`- tai `timezone`-kenttää ei ole tehtäväpyynnön `period`-objektissa. Yleinen aikavyöhyke välitetään tehtäväpyynnön `resolved_config.timezone`-asetuksessa. Näin `period` kuvaa vain seurannan aikarajaa. Tehtävän toimitusmääräaika `deadline_at` on tästä erillinen.

GitHub Actions ratkaisee tehtävätyypin oletukset, profiilit ja aihekohtaiset asetukset ennen tehtävän tarjoamista. Tehtäväpyyntö sisältää valmiin `resolved_config`-konfiguraatiosnapshotin. Raportintuottajan ei tarvitse hakea tai yhdistellä määritystiedostoja itse. `software_revision` ja `instance_revision` yksilöivät ohjelmisto- ja instanssirepon käytetyt commitit. Raportintuottaja hakee kaikki tehtävässä tarvittavat tiedostot oikeasta repositoriosta täsmälleen ilmoitetusta commitista eikä muuttuvasta `main`-haarasta.

Tehtäväpyynnön rakenteesta on lisäksi hyväksytty seuraavat periaatteet:

- Juuritason `schema_version` on pakollinen merkkijono, joka käyttää semanttista versionumerointia (esimerkiksi `1.0.0`). Se kuvaa vain tehtäväpyynnön JSON-rakennetta.
- `run_id` on pakollinen, ihmisluettava tunniste muodossa `YYYYMMDD-HHMMSS-{offset}-{topic_id}-{task_type}`, jossa `{offset}` on aina mukana muodossa `pHHMM` tai `mHHMM`. `p` tarkoittaa positiivista ja `m` negatiivista UTC-offsetia; esimerkiksi Suomen talviajan offset on `p0200` ja kesäajan `p0300`. Päivä ja kellonaika muodostetaan yleisen `timezone`-asetuksen paikallisesta ajasta ja offset kyseisen ajanhetken todellisesta IANA-aikavyöhykesäännöstä. Aikaleiman on oltava todellinen kalenteripäivä ja kellonaika; virheellisiä arvoja ei normalisoida. Offset on pakollinen myös silloin, kun paikallinen kellonaika ei ole kaksiselitteinen. Näin syksyn kellonsiirrossa kahdesti esiintyvä paikallinen kellonaika saa eri tunnisteen ilman erillistä järjestysnumeroa. Tunnisteen `topic_id`- ja `task_type`-osien on vastattava täsmälleen tehtäväpyynnön samannimisiä kenttiä. Validointi tehdään muodostamalla yleisen aikavyöhykkeen paikallisesta aikaleimasta, offsetista ja kenttien arvoista odotettu `run_id` ja vertaamalla sitä annettuun tunnisteeseen. Näin tunnisteiden sisäiset yhdysmerkit sallitaan eikä tunnistetta tarvitse jakaa osiin epäluotettavalla tavalla. Ylimääräiset tai poikkeavat osat hylätään. Tunniste ei sisällä profiileja. Ensimmäisessä versiossa yksi raportintuottaja käsittelee tehtäviä sarjallisesti, joten satunnaista tai juoksevaa lisäosaa ei tarvita. Tunnistetta käytetään myös toimitushakemiston nimenä. Jos muodostettu tunniste on jo käytössä, sitä ei saa ylikirjoittaa: ajanhetkeä siirretään seuraavalla yhdellä absoluuttisella sekunnilla (UTC-ajassa) ja uusi paikallinen aika sekä offset muodostetaan uudelleen yleisen aikavyöhykkeen sääntöjen mukaan.
- Erillistä `task_id`-kenttää ei lisätä. `run_id`, `topic_id` ja `task_type` yksilöivät ajon ja sen tehtävän.
- `topic_id`- ja `task_type`-tunnisteissa käytetään samaa syntaksia: sallittuja ovat pienet ASCII-kirjaimet `a–z`, numerot `0–9` ja yhdysmerkki (`-`). Tunnisteen on alettava ja päätyttävä kirjaimeen tai numeroon, eikä yhdysmerkkejä saa olla peräkkäin. Välilyönnit, alaviivat, pisteet, kauttaviivat, ääkköset ja muut erikoismerkit eivät ole sallittuja. Tunnisteille ei aseteta erillistä enimmäispituutta tässä vaiheessa. Virheellinen tunniste hylätään; sitä ei normalisoida automaattisesti. Syntaksin tarkistava säännöllinen lauseke on `^[a-z0-9]+(?:-[a-z0-9]+)*$`.

- `issued_at` ja `deadline_at` ovat pakollisia yleisen `timezone`-asetuksen mukaisia aikaleimoja, joiden täsmällinen merkkijonomuoto on `YYYY-MM-DDTHH:mm:ss±HH:mm`. Sekunnit ovat pakollisia; desimaaliosia tai aikavyöhykkeettömiä arvoja ei hyväksytä. Offsetin on vastattava asetetun IANA-aikavyöhykkeen sääntöjä kyseisenä hetkenä. Arvojen on vastattava todellista kalenteripäivää ja kellonaikaa. Aikaleimoja ei normalisoida eikä muunnetta automaattisesti toiseen muotoon. `issued_at` on hetki, jolloin GitHub Actions muodostaa tehtäväpyynnön. `deadline_at` on viimeinen hetki, johon mennessä raportintuottajan on toimitettava tulos. Määräaika lasketaan `issued_at`-hetkestä tehtävätyypin määrityksissä asetetun käsittelyajan perusteella, joten eri tehtävätyypeillä voi olla erilaiset käsittelyajat. `deadline_at`-arvon on oltava aidosti myöhempi kuin `issued_at`; yhtä suuri tai aikaisempi arvo hylätään.
- `history` on pakollinen ja sisältää `repository`-, `path`- ja `revision`-kentät. `path` on oltava täsmälleen merkkijono `rss/{topic_id}/{task_type}.xml`, kun paikkamerkit korvataan saman tehtäväpyynnön `topic_id`- ja `task_type`-arvoilla. Polkua verrataan tähän muodostettuun arvoon sellaisenaan; sitä ei normalisoida eikä korjata automaattisesti. Näin myös väärä aihe tai tehtävätyyppi, absoluuttinen polku, URL-osoite, hakemistohyppy tai muu poikkeava polku hylätään. Polku on repositoriojuureen suhteutettu suhteellinen polku, ei URL eikä haaran nimi. `repository` on pakollinen ja sen arvo on `instance`, koska RSS-historia sijaitsee instanssirepositoriossa. `revision` on pakollinen, täsmälleen 40 merkkiä pitkä Git-commit-SHA, joka sisältää vain heksadesimaalimerkkejä (`0–9`, `a–f`). Se yksilöi täsmälleen sen instanssirepositorion commitin, josta RSS-historia luetaan. Historia luetaan tästä commitista, ei muuttuvasta haaraviittauksesta. `history.revision` on käsitteellisesti erillinen `instance_revision`-kentästä: se voi olla sama commit, mutta voi myös osoittaa aiempaan RSS-historian lähtötilaan.
- Myös `software_revision` ja `instance_revision` ovat kumpikin täsmälleen 40 heksadesimaalimerkkiä sisältäviä Git-commit-SHA-tunnisteita, jotka viittaavat omissa repositorioissaan olemassa oleviin committeihin.
- `profiles` ja `instructions` säilytetään erillisinä taulukoina. Ensimmäinen kuvaa käytetyt koneelliset määritysprofiilit, toinen pakollisesti luettavat Markdown-ohjeet.
- `profiles` on pakollinen taulukko. Tyhjä taulukko sallitaan, jos tehtävä ei käytä profiileja. Jokainen alkio on objekti, jossa ovat pakolliset kentät `id`, `repository` ja `path`. `id` yksilöi tunnetun profiilin, `repository` on aina `instance` ja `path` on profiilin määritystiedoston repositoriojuureen suhteutettu polku. Saman profiilin `id` ei saa esiintyä kahdesti. Taulukon järjestys säilytetään, koska myöhemmin lueteltu profiili voi korvata aiemmin luetellun profiilin asetuksia.
- `instructions` on pakollinen, ei-tyhjä taulukko. Jokaisessa alkiossa ovat pakolliset kentät `id`, `repository` ja repositoriojuureen suhteutettu `path`. `repository` on täsmälleen `software` tai `instance`. Tunnisteen on vastattava tunnettua ohjetta. Ohjeet luetellaan järjestyksessä: yhteinen raportintekijän perusprompti, tehtävätyypin ohje, profiilien ohjeet profiilien järjestyksessä ja aiheen ohje. Sama ohje ei saa esiintyä useita kertoja.

### Ratkaistu määritys (`resolved_config`)

`resolved_config` on aina pakollinen JSON-objekti. Se sisältää aina yleisen `timezone`-asetuksen sekä muut tehtävän suorituksessa tarvittavat, valmiiksi yhdistetyt asetukset. Jos tehtävällä ei ole muita koneellisia lisäasetuksia, objektissa on silti `timezone`. Yleinen `timezone` on järjestelmätason asetus, eikä tehtävätyyppi, profiili tai aihekohtainen määritys saa ylikirjoittaa sitä. Se validoidaan IANA-aikavyöhyketunnisteena ja välitetään raportintuottajalle muuttumattomana. Alkuperäisiä määrityksiä tai profiilien sisältöjä ei kopioida sinne sellaisinaan.

Asetukset yhdistetään tässä järjestyksessä: tehtävätyypin oletukset, profiilit niiden ilmoitetussa järjestyksessä ja lopuksi aihekohtaiset ylikirjoitukset. Sisäkkäiset objektit yhdistetään rekursiivisesti, myöhempi arvo korvaa aiemman saman asetuksen ja taulukot korvataan kokonaan.

- Pakollisten asetusten on löydyttävä ratkaistusta määrityksestä; muuten tehtäväpyyntöä ei muodosteta.
- Valinnaiset asetukset voidaan jättää pois, mutta raportintuottaja ei keksi niille omia oletusarvoja.
- Tuntemattomat asetukset hylätään validoinnissa.
- Oletusarvot määritellään tehtävätyypin tai profiilien alkuperäisissä määrityksissä.
- Sisältö käyttää tavallisia JSON-tietotyyppejä. Tietotyypit, pakollisuus ja arvorajat määritellään tehtävätyypin JSON Schemassa.
- Raportintuottaja ei täydennä puuttuvia asetuksia omilla oletuksillaan.
- Tehtävätyyppi määrittää käytettävän skeeman. Yhteinen skeema haetaan ohjelmistorepon `software_revision`-commitista; `resolved_config`-objektiin ei lisätä erillistä skeemaversiota.
- Ensimmäisessä versiossa järjestelmä ei käsittele salaisia tietoja. Tehtäväpyyntöön ei sisällytetä salasanoja, API-avaimia, käyttöoikeustunnisteita eikä yksityisiä tietoja.
- `resolved_config`-kentälle ei aseteta erillistä keinotekoista kokorajaa. Siihen ei kuitenkaan kopioida Markdown-ohjeita, lähderekistereitä tai raporttihistoriaa; laajoihin aineistoihin viitataan tarvittaessa tunnisteilla tai poluilla.

Ensimmäisessä vaiheessa ei toteuteta erillistä raportintuottajakohtaista tehtävien varausmekanismia, varauksen vanhenemista eikä rinnakkaisten tehtävien lukitusjärjestelmää. Yksi raportintuottaja ja yksi aktiivinen tehtäväpyyntö riittävät. Tämä ei kuitenkaan poista tarvetta koordinoida GitHub Actions -työnkulkuja: tehtävän muodostaminen, määräajan valvonta, toimituksen vastaanotto ja sen käsittely kuuluvat saman instanssin yhteisen sarjallisuuden hallinnan piiriin.

Tehtävän käsittelyn jumiutumista vastaan toteutetaan ensimmäiseen versioon rajattu palautumismekanismi:

- Tehtäväpyynnöllä on määräaika. Jos raportintuottajan tulosta ei saavu määräaikaan mennessä, ajo käsitellään epäonnistuneena.
- Toimituksen vastaanotto- tai käsittelyvirheen jälkeen voidaan tehdä konfiguraation sallimia automaattisia käsittely- ja uudelleenyrityksiä. Yritysten määrä ja laskentatapa määritellään tehtävätyypin määrityksissä ja välitetään tehtäväpyynnön `resolved_config`-kentässä; niitä ei kovakoodata yhteiseen toteutukseen.
- Kun yritykset on käytetty tai tehtävän määräaika umpeutuu, epäonnistuminen kirjataan kanoniseen ajohistoriaan ja jonotus etenee seuraavaan tehtävään. Yksittäinen epäonnistunut tehtävä ei saa estää muiden aiheiden käsittelyä. Määräajan umpeutuminen ei kuitenkaan yksin estä alkuperäisen ajon myöhäisen toimituksen jälkikäsittelyä kohdassa 2.3.2 määritellyin ehdoin.
- Tehtävän määräaika, uudelleenyritysten määrä ja muut vastaavat käsittelyrajat määritellään konfiguraatiossa. Tehtävätyypin määritys ja tarvittaessa profiilit tarjoavat arvot, jotka ratkaistaan tehtäväpyynnön `resolved_config`-kenttään. Raportintuottaja ja vastaanottava toteutus noudattavat näitä arvoja eivätkä käytä omia piilotettuja oletuksiaan.
- Ensimmäisessä versiossa epäonnistuneiden tehtävien palautus myöhempään käsittelyyn on rajattu. Älykkäämpi uudelleenkäsittelylogiikka, kuten virheen syyn, aiempien yritysten ja sopivan odotusajan huomioiminen, kuuluu myöhempiin versioihin.
- Tehtävän etenemisen erillistä tilatiedostoa ei lisätä. Tehtäväpyynnön korvaaminen seuraavalla ja ajohistoria muodostavat etenemisen lähteen; seuraava tehtävä muodostetaan vasta, kun nykyisen tehtävän käsittely on ratkaistu onnistuneesti tai se on päätetty epäonnistuneeksi palautumissääntöjen perusteella.
- Kaikki samaan instanssiin kuuluvat tehtävänmuodostus-, määräajanvalvonta- ja toimituksen vastaanotto-/käsittelyajot on sarjallistettava yhteisen hallintamekanismin kautta. Mekanismin on estettävä samanaikaiset tai päällekkäiset käsittelyt, jotka voisivat muodostaa uuden tehtävän ennen edellisen tehtävän lopullista ratkaisua tai käsitellä kahta tehtävää aktiivisina. Pelkkä aktiivisen tehtäväpyynnön lukeminen ja tarkistaminen ei riitä, jos tarkistus ja sitä seuraava tilapäivitys eivät ole keskenään suojattuja.
- Seuraava tehtävä voidaan muodostaa vasta, kun edellinen ajo on todettu onnistuneeksi tai sen epäonnistuminen on kirjattu kanoniseen ajohistoriaan ja ajon käsittely on päätetty. Myös vastaanoton uudelleenyritykset ja määräajan umpeutumisen käsittely kuuluvat tähän samaan sarjalliseen elinkaareen. Myöhäisen toimituksen rajattu jälkikäsittely voi jatkua tämän jälkeen alkuperäisen `run_id`-tunnisteen perusteella, mutta se ei avaa alkuperäistä tehtäväpyyntöä uudelleen eikä muuta myöhempää aktiivista tehtävää.
- Sarjallisuuden tekninen toteutustapa, kuten GitHub Actionsin työnkulkujen koordinointi ja mahdollinen yhteinen concurrency-/lukitusratkaisu, määritellään teknisessä suunnittelussa. Tässä vaiheessa lukitaan vaatimus ja toimintaperiaate, ei tiettyä GitHub Actions -ominaisuutta tai toteutuskoodia.


### 2.2.2 Käsittelyn valmistuminen ja aktiivisen tehtävän vapauttaminen

Ajon elinkaari erottaa kolme tietoa: raportintuottajan ilmoittaman **tuottajan tuloksen**, vastaanottajan suorittaman **käsittelyn** sekä vastaanottajan muodostaman **ajon lopputilan**. Tuottajan tulos tallennetaan vain toimitetun tuloksen perusteella. Vastaanottajan aikakatkaisu tai muu käsittelyhavainto ei ole tuottajan ilmoittama epäonnistuminen.

Vastaanottajan näkökulmasta ajo onnistuu vasta, kun toimitus on tunnistettu oikeaan `run_id`-ajoon, pakolliset validoinnit läpäisty, raportti hyväksytty ja mahdollinen RSS-julkaisu varmennettu sekä kirjattu. Osittainen raportti voidaan hyväksyä, jos se täyttää julkaisuehdot ja puutteet kuvataan raportissa. Pelkkä vastaanotto tai validoinnin läpäisy ei riitä onnistumiseen.

Aktiivinen käsittely päättyy ja tehtävä vapautetaan, kun:
- hyväksytty toimitus on validoitu ja julkaisu onnistunut;
- toimitus on hylätty eikä konfiguraation sallimia käsittely- tai uudelleenyritysmahdollisuuksia ole jäljellä;
- vastaanoton, tallennuksen, julkaisun tai muun pakollisen vaiheen virhettä ei saada korjattua konfiguroiduissa rajoissa; tai
- määräaika umpeutuu ilman hyväksyttävää toimitusta ja vastaanottaja kirjaa aikakatkaisun.

Aktiivinen tehtävä vapautetaan vasta, kun vastaanottajan käsittely on päätetty ja ajon lopputila kirjattu kanoniseen ajohistoriaan. Seuraavaa tehtävää ei muodosteta tai käynnistetä ennen tätä. Yksittäinen epäonnistunut yritys ei vapauta tehtävää, jos käsittelyä voidaan vielä jatkaa. Epäonnistuminen ei automaattisesti käynnistä uutta erillistä tehtävää.

Uudelleenyritysten määrä, yritysten laskentatapa, määräajat ja muut vastaavat käsittelyrajat ovat konfiguroitavia toimintaparametreja. Niitä ei kovakoodata yhteiseen ohjelmistoon kiinteinä lukumäärinä tai aikarajoina. Arvot määritellään tehtävätyypin määrityksissä ja tarvittaessa profiileissa, yhdistetään normaalin määritysjärjestyksen mukaisesti ja välitetään raportintuottajalle `resolved_config`-kentässä. Toteutus noudattaa ratkaistuja arvoja eikä käytä piilotettuja oletuksia. Arvojen tietotyypit, pakollisuus, sallitut rajat ja mahdolliset oletusarvot määritellään tehtävätyypin skeemassa. Puuttuva tai virheellinen pakollinen arvo estää tehtäväpyynnön muodostamisen.

Epäonnistumisesta kirjataan vastaanottajan havaitsema syy ja siihenastiset käsittelytapahtumat. Tuottajan tulosta ei päätellä vastaanottajan havainnoista. Ajohistoriasta on voitava selvittää käynnistys ja määräaika, toimituksen saapuminen, tuottajan tulos jos toimitettu, vastaanottajan käsittelyvaiheet, validointi, julkaisu, ajon lopputila ja aktiivisen käsittelyn vapautushetki. Tapahtumat säilytetään aikajärjestyksessä, eikä myöhempi tapahtuma korvaa aiempaa.

Määräajan jälkeen saapunut toimitus käsitellään alkuperäisellä `run_id`-tunnisteella aiemmin määriteltyjen myöhäisen toimituksen ehtojen mukaisesti. Se voi täydentää samaa ajohistoriatietuetta uusilla tapahtumilla, mutta ei avaa vapautettua tehtävää uudelleen eikä muuta myöhemmän käynnistetyn ajon tietoja. Jos myöhempi saman aiheen ja seurantatyypin ajo on jo käynnistetty, myöhäistä toimitusta ei julkaista.
Useiden samanaikaisten raportintuottajien tai tehtävien tuki voidaan lisätä myöhemmin. Silloin suunnitellaan erikseen atominen varaus, varauksen voimassaolo, vanhentuneen varauksen palautus sekä vanhalla `run_id`:llä saapuvien toimitusten hylkääminen. Ensimmäisen vaiheen ratkaisu ei saa tarpeettomasti estää tätä laajennusta.

#### Tehtäväpyynnön juuritason rakenne ja yleiset validointisäännöt

Tehtäväpyyntö on JSON-objekti, jossa ovat täsmälleen seuraavat juuritason kentät:

| Kenttä | Tietotyyppi | Pakollinen | Merkitys |
|---|---|---|---|
| schema_version | merkkijono | Kyllä | Tehtäväpyynnön rakenteen semanttinen versio muodossa MAJOR.MINOR.PATCH, esimerkiksi 1.0.0. |
| run_id | merkkijono | Kyllä | Yksilöllinen ajotunniste. |
| topic_id | merkkijono | Kyllä | Aiheen tunniste. |
| task_type | merkkijono | Kyllä | Tehtävätyypin tunniste. |
| software_revision | merkkijono | Kyllä | Ohjelmistorepon commit-SHA. |
| instance_revision | merkkijono | Kyllä | Instanssirepon commit-SHA. |
| period | objekti | Kyllä | Seuranta-aikavälin alku ja loppu. |
| issued_at | merkkijono | Kyllä | Tehtäväpyynnön muodostamishetki. |
| deadline_at | merkkijono | Kyllä | Toimituksen määräaika. |
| history | objekti | Kyllä | RSS-historian repositorio, polku ja lähtörevisio. |
| inputs | taulukko | Kyllä | Rakenteisten syöteaineistojen viittaukset; tyhjä sallitaan, jos tehtävä ei tarvitse erillisiä aineistoja. |
| profiles | taulukko | Kyllä | Käytettyjen profiilien järjestetty luettelo; tyhjä sallitaan. |
| instructions | taulukko | Kyllä | Pakollisesti luettavien ohjeiden järjestetty, ei-tyhjä luettelo. |
| resolved_config | objekti | Kyllä | Valmiiksi ratkaistu tehtäväkohtainen konfiguraatio. |

Jokainen juuritason kenttä on pakollinen eikä tuntemattomia juuritason kenttiä sallita. `inputs` on aina mukana myös tyhjänä taulukkona, jos tehtävä ei tarvitse erillisiä rakenteisia aineistoja. Myös sisäkkäisissä objekteissa hylätään määrittelemättömät ylimääräiset kentät. resolved_config-objektin sallitut asetukset määräytyvät tehtävätyypin skeemasta; sen yleiset säännöt on kuvattu edellä.

schema_version on täsmälleen kolmen numeerisen osan semanttinen versio muodossa MAJOR.MINOR.PATCH; etuliitteitä, jälkiliitteitä tai build-metatietoja ei käytetä. Se versioi vain tehtäväpyynnön rakennetta ja tulkintasääntöjä, ei ohjelmistoa.

Kaikkien kolmen commit-tunnisteen (software_revision, instance_revision ja history.revision) on oltava täsmälleen 40 merkkiä pitkiä ja koostuttava pienistä heksadesimaalimerkeistä 0–9 ja a–f. Suuraakkoset eivät ole sallittuja. Tunnisteiden on viitattava asianomaisessa repositoriossa olemassa oleviin committeihin.

topic_id- ja task_type-kenttien syntaksi on ^[a-z0-9]+(?:-[a-z0-9]+)*$. run_id muodostetaan näiden kenttien, yleisen aikavyöhykkeen paikallisen ajan ja ajanhetken UTC-offsetin perusteella edellä määritellyllä tavalla. Erillistä task_id-kenttää ei ole.

period sisältää täsmälleen pakolliset from- ja to-kentät. from on aikaleima ja to aikaleima tai null. Aikaleimat noudattavat yleistä ISO 8601 -muotoa YYYY-MM-DDTHH:mm:ss±HH:mm; sekunnit ja oikea numeerinen UTC-offset ovat pakollisia, desimaaliosia ei sallita. Jos to ei ole null, sen on oltava ajallisesti myöhempi kuin from. Seuranta-aikaväli tulkitaan puoliksi avoimena aikavälinä `[from, to)`: alkupiste sisältyy ja loppupiste ei sisälly aikaväliin. Jos `to` on `null`, tunnettu alkupiste sisältyy ja päätepiste on avoin. Objektissa ei ole timezone- eikä cutoff_at-kenttää.

issued_at ja deadline_at noudattavat samaa aikaleimamuotoa ja yleisen resolved_config.timezone-asetuksen offset-sääntöjä. deadline_at on ajallisesti myöhempi kuin issued_at; määräaika lasketaan tehtävätyypin käsittelyaika-asetuksen perusteella.

history sisältää täsmälleen kentät repository, path ja revision. repository on aina instance. path on täsmälleen rss/{topic_id}/{task_type}.xml, kun paikkamerkit korvataan saman tehtäväpyynnön tunnisteilla. revision on RSS-historian lähtöcommit, ja se voi poiketa instance_revision-arvosta.

`inputs`-, `profiles`- ja `instructions`-taulukoiden alkioiden kentät ja järjestys on määritelty edellä. `inputs`-taulukon jokaisessa alkiossa ovat täsmälleen kentät `id`, `kind`, `repository` ja `path`. `id` on yksilöllinen tunniste, `kind` ilmaisee aineiston tyypin (ensimmäisessä versiossa `source_registry`), `repository` on looginen repositoriotunniste ja `path` repositoriojuureen suhteutettu tiedostopolku. Ensimmäisessä versiossa `source_registry`-aineisto luetaan instanssirepositoriosta (`repository: instance`) `instance_revision`-revisiosta. Duplikaatit ja tuntemattomat kentät hylätään. Kaikki viitatut tiedostot luetaan niiden repositorioiden muuttumattomista commit-revisioista: software käyttää software_revision-arvoa ja instance käyttää instance_revision-arvoa. Polku on aina repositoriojuureen suhteutettu tiedostopolku, ei URL tai haaraviittaus.

### 2.2.1.1 Tehtäväpyynnön muodostamisen ja määräajanvalvonnan ajastus

Tehtäväpyynnön muodostaminen ja aktiivisen tehtävän määräajan valvonta hoidetaan yhdellä säännöllisesti käynnistyvällä GitHub Actions -työnkululla.

- Työnkulku tarkistaa, onko käsiteltävä tehtäväpyyntö jo olemassa.
- Jos tehtäväpyyntöä ei ole ja jonossa on käsiteltävä aihe, työnkulku muodostaa seuraavan tehtäväpyynnön.
- Jos aktiivinen tehtävä on ylittänyt määräaikansa eikä sen tulosta ole saapunut, työnkulku käsittelee tehtävän epäonnistuneena aiemmin sovittujen palautumissääntöjen mukaisesti ja voi sen jälkeen muodostaa seuraavan tehtävän.
- Jos tehtävä on yhä voimassa, työnkulku jättää sen ennalleen. Se ei luo rinnakkaista tehtävää eikä muuta tehtävän sisältöä.
- Raportintuottaja hakee tehtävän omalla aikataulullaan. Sen käynnistyminen ei edellytä erillistä GitHub Actions -ilmoitusta.

Tämä pitää tehtävän muodostamisen ja määräaikojen valvonnan yhdessä paikassa eikä sido niitä raportintuottajan käynnistysrytmiin. Työnkulun tarkka suoritusväli ja mahdollinen manuaalinen käynnistys määritellään myöhemmin tehtävätyyppien ja käyttörajoitusten yhteydessä.


#### 2.2.1.2 Sarjallinen tehtävänkäsittely ensimmäisessä versiossa

Ensimmäisessä versiossa GitHub Actions ylläpitää yhtä aktiivista tehtäväpyyntöä ja yksi raportintuottaja käsittelee tehtävät yksi kerrallaan. Sarjallisuus koskee kaikkia aiheita, ei vain saman aiheen ajoja.

- Uusi tehtävä muodostetaan vasta, kun edellinen tehtävä on ratkaistu onnistuneesti tai kirjattu epäonnistuneeksi palautumissääntöjen mukaisesti.
- Käsittelyssä ei ole kahta samanaikaista aktiivista raportointitehtävää. Eri aiheiden rinnakkaista käsittelyä ei tueta ensimmäisessä versiossa.
- Erillistä tehtävien varaus-, lukitus- tai kilpailutilanteiden hallintaa ei siksi tarvita ensimmäisessä versiossa.
- run_id-tunniste, toimituksen idempotentti käsittely ja kaksoisjulkaisujen esto säilyvät tarpeellisina myös sarjallisessa mallissa esimerkiksi saman toimituksen uudelleenyritysten vuoksi.
- Usean tehtävän tai raportintuottajan rinnakkaisuus voidaan suunnitella myöhemmässä vaiheessa, jos sille syntyy todellinen tarve. Silloin arvioidaan erikseen atominen varaus, lukitukset, vanhentuneiden varausten palautus ja rinnakkaisten tilapäivitysten turvallisuus.

Sarjallinen käsittely on ensimmäisen version nimenomainen rajaus, ei oletus siitä, ettei rinnakkaisuutta voisi koskaan lisätä.

### 2.2.2 Tehtävätyypit, määritysprofiilit ja aihekohtaiset asetukset

Määritykset jaetaan kolmeen tasoon:

1. **Tehtävätyypin määritys** sisältää tehtävätyypin tunnisteen ja kuvauksen, skeemaviittauksen, oletusasetukset, sallitut asetukset ja niiden ylikirjoitettavuuden sekä tehtävätyypin käsittely-, raportointi- ja toimitusvaatimukset.
2. **Määritysprofiilit** ovat uudelleenkäytettäviä, itsenäisiä asetuskokonaisuuksia. Profiililla on tunniste, kuvaus ja asetukset. Yksi tehtävä voi käyttää useita profiileja, ja niiden järjestys on merkityksellinen.
3. **Aihekohtainen määritys** sisältää aiheen tunnisteen ja kuvauksen, käytettävän tehtävätyypin, profiilit järjestyksessä, aihekohtaiset asetukset ja sallitut ylikirjoitukset sekä aikaväli- ja ajastustiedot. Lisäksi se voi määritellä kyseisen aiheen ja tehtävätyypin yhdistelmän lähdevalinnan ja lähteiden käyttöasetukset. Lähteiden pysyvät perustiedot eivät kuulu aihekohtaiseen määritykseen, vaan yhteiseen lähderekisteriin.

Tehtävätyypin määritys määrittelee, mitä asetuksia kyseinen tehtävätyyppi hyväksyy ja mitä niistä voidaan ylikirjoittaa. Profiilit eivät voi muuttaa järjestelmätason asetuksia tai lisätä tehtävätyypin skeemassa tuntemattomia asetuksia.

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

Tehtävätyyppi sisältää yleiset, saman tehtäväluokan tehtäville kuuluvat oletukset sekä tehtävätyypin oletuslähteet ja mahdolliset pakolliset lähteet. Profiilit täydentävät tehtävätyypin asetuksia esimerkiksi tapahtumalajin, sisältöalueen, genren tai muun uudelleenkäytettävän ominaisuuden mukaan. Aihekohtainen määritys sisältää yksittäisen seurannan omat hakusanat, rajaukset ja muut erot sekä lähdevalinnan kyseisen aiheen ja tehtävätyypin yhdistelmälle. Ihmiselle tarkoitetut pitkät toimitukselliset ja menettelyohjeet pidetään Markdown-tiedostoissa; koneellisesti käsiteltävät asetukset ovat JSON-tiedostoissa.

Yksi aihe voi käyttää useita profiileja. Esimerkiksi elokuvanäytösvahti voi yhdistää tapahtumavahdin yleiset oletukset, elokuvanäytösprofiilin ja intialaisen elokuvan profiilin. Konserttivahti voi käyttää tapahtumavahdin ja konserttiprofiilin lisäksi esimerkiksi klassisen musiikin profiilia. Ensimmäisessä versiossa profiilien välisiä riippuvuuksia, kieltoja tai erillistä yhteensopivuusmatriisia ei mallinneta. Profiileja voidaan yhdistää ilman, että niiden tarvitsee ilmoittaa yhteensopivuuttaan keskenään.

Ensimmäisessä versiossa profiilit ovat itsenäisiä määrityksiä: profiili ei peri toista profiilia eikä muodosta rekursiivista riippuvuusketjua. Jokainen profiili kuuluu täsmälleen yhdelle tehtävätyypille; sitä voidaan käyttää useassa saman tehtävätyypin aiheessa, mutta ei toisen tehtävätyypin yhteydessä. Tämä pitää yhdistämisen ennustettavana. Profiilien keskinäinen järjestys ilmoitetaan aihekohtaisessa määrityksessä ja ratkaisee mahdolliset päällekkäiset asetukset.

Asetukset ratkaistaan seuraavassa järjestyksessä:

1. tehtävätyypin oletusasetukset;
2. aihekohtaisessa määrityksessä ilmoitetut profiilit täsmälleen annetussa järjestyksessä;
3. aihekohtaiset asetukset.

Yhdistämissäännöt:

- Sisäkkäiset JSON-objektit yhdistetään rekursiivisesti.
- Myöhempi arvo korvaa aiemman saman asetuksen arvon.
- Taulukot korvataan kokonaan; niitä ei yhdistetä automaattisesti.
- Puuttuva asetus periytyy aiemmalta tasolta.
- `null`-arvolle ei ole yleistä periytymis- tai poistamismerkitystä; merkitys määritellään asetuksen skeemassa.
- Tuntemattomat avaimet ja väärän tyyppiset arvot hylätään skeemavalidoinnissa.
- Tehtävätyypin, profiilien ja aihekohtaisten määritysten rakenteet validoidaan kukin omia skeemojaan vasten. Lopullinen yhdistetty `resolved_config` validoidaan tehtävätyypin skeemaa vasten.
- Ylikirjoituksia saa tehdä vain tehtävätyypin skeemassa erikseen sallituissa asetuskohdissa.
- Suojattuja asetuksia ei voi ylikirjoittaa. Niihin kuuluvat yleinen `timezone`, tehtävän tunnisteet (`topic_id`, `task_type`, `run_id`), revisiotunnisteet sekä tehtäväpyynnön rakenteelliset ja tietosopimuksen vaatimukset.
- Ensimmäisessä versiossa tehdään vain määritysten välttämättömät yhteensopivuus- ja ristiriitatarkistukset. Yleistä dynaamista sääntömoottoria tai käyttäjän määrittelemiä yhdistämisfunktioita ei toteuteta.

Oletusarvot määritellään tehtävätyypin määrityksessä, eivät skeeman automaattisesti soveltamina arvoina. Skeema määrittelee rakenteen, tietotyypit, pakollisuuden, rajat ja sallitut ylikirjoitukset. Jos pakolliselle asetukselle ei ole tehtävätyypin oletusarvoa, se on annettava profiilissa tai aihekohtaisessa määrityksessä. Puuttuva pakollinen arvo estää tehtäväpyynnön muodostamisen. `null` hyväksytään vain, jos kyseisen asetuksen skeema sallii sen ja määrittelee sen merkityksen.

Määritykset validoidaan sekä yksittäin että yhdistettynä. Tarkistuksiin kuuluvat rakenteen ja tietotyyppien lisäksi tunnisteiden syntaksi, sallitut rajat, ylikirjoitettavuus, tehtävätyypin ja profiilien soveltuvuus sekä pakollisten arvojen läsnäolo. Ensimmäisessä versiossa ei rakenneta yleistä profiilien yhteensopivuusmatriisia tai automaattista ristiriitojen korjausta.

Yleinen aikavyöhyke on järjestelmätason asetus. Se sisältyy aina tehtäväpyynnön `resolved_config.timezone`-kenttään, mutta profiilit tai aihekohtaiset määritykset eivät voi ylikirjoittaa sitä. Samoin tehtävän tunnisteita, revisioita tai tietosopimuksen rakenteellisia vaatimuksia ei voi muuttaa määritystasoilla.

Määritykset luetaan niissä ilmoitetuista muuttumattomista Git-commit-revisioista. Kukin määritys validoidaan erikseen, asetukset yhdistetään sovitussa järjestyksessä ja lopullinen kokonaisuus validoidaan vielä tehtävätyypin skeemaa vasten. Vasta onnistuneen validoinnin jälkeen GitHub Actions tallentaa valmiin konfiguraation tehtäväpyynnön `resolved_config`-kenttään.

`resolved_config` on ajokohtainen, muuttumaton snapshot kaikista suorituksen asetuksista. Se sisältää aina yleisen `timezone`-asetuksen. Raportintuottaja käyttää ainoastaan tätä valmista kokonaisuutta eikä hae määrityksiä uudelleen tai toteuta omaa yhdistämislogiikkaa. Käytettyjen määritysten Git-revisiot säilyttävät jäljitettävyyden ja mahdollistavat konfiguraation rekonstruoinnin.

Jos jokin määritys on virheellinen, ristiriitainen tai siitä puuttuu pakollinen arvo, tehtäväpyyntöä ei muodosteta. Virhe kirjataan syineen ja sijaintitietoineen. Aiemmin aktiivista tehtävää ei korvata, jono ei jää epäselvään tilaan eikä järjestelmä tee automaattisia korjauksia, päättele puuttuvia arvoja tai muodosta osittaista `resolved_config`-kokoonpanoa.

Tehtävätyyppien, profiilien ja aihekohtaisten määritysten omat JSON Schema -skeemat validoivat niiden rakenteet. Tehtävätyypin skeema määrittelee lisäksi lopullisen `resolved_config`-rakenteen ja sallitut ylikirjoitukset. Markdown-ohjeet versioidaan Gitissä ja niihin viitataan tehtäväpyynnöstä.

Skeemakokonaisuus toteutetaan JSON Schema Draft 2020-12 -standardilla. Yhteiseen ohjelmistorepoon kuuluvat seuraavat skeemat:

1. tehtävätyypin määrityksen skeema;
2. tehtävätyyppikohtainen asetusskeema, jota tehtävätyypin määritys viittaa;
3. määritysprofiilin skeema;
4. aihekohtaisen määrityksen skeema;
5. lähderekisterin skeema;
6. tehtäväpyynnön skeema;
7. toimitusmetatietojen skeema.

Tehtävätyypin määrityksen rakenne sisältää `schema_version`-, `id`-, `description`-, `config_schema`-, `defaults`-, `overridable_paths`-, `processing`-, `reporting`- ja `instruction`-kentät. `overridable_paths` ilmaisee JSON Pointer -polkuina täsmälleen ne asetuskohdat, joita profiilit ja aihekohtainen määritys saavat ylikirjoittaa. Tehtävätyyppikohtainen asetusskeema määrittelee `resolved_config`-objektin rakenteen, tietotyypit, pakollisuuden, rajat ja tuntemattomien kenttien hylkäämisen.

Määritysprofiilin rakenne sisältää `schema_version`-, `id`-, `task_type`-, `description`-, `settings`- ja `instruction`-kentät. Profiilin `task_type`-arvon on vastattava tehtäväpyynnössä valittua tehtävätyyppiä. Profiili ei peri toista profiilia. Aihekohtainen määritys sisältää `schema_version`-, `topic_id`-, `task_type`-, `enabled`-, `profiles`-, `settings`-, `source_registry`- ja `instruction`-tiedot. Profiiliviittaukset säilyttävät järjestyksen.

Yhteinen lähderekisteri sisältää lähteen pysyvät perustiedot: vakaan `id`-tunnisteen, nimen, julkaisijan, lähdetyypin, kielet, alueet, mahdollisen IANA-aikavyöhykkeen ja sen perusteen sekä lähteen yhteiset teknistä saavutettavuutta ja toimituksellista luotettavuutta kuvaavat tiedot. Yhdellä lähteellä voi olla useita sisältökanavia, jotka tallennetaan erillisinä kanavatietueina saman lähteen yhteyteen. Jokaisella kanavalla on oma vakaa tunniste ja osoite; kanava voi kuvata esimerkiksi julkaisijan uutis-, elokuva-, tapahtuma- tai videokanavaa. Kanavien avulla eri sisältövirrat voidaan valita ja arvioida tehtäväkohtaisesti erikseen, vaikka niiden julkaisijan ja lähteen yhteiset perustiedot ylläpidetään vain kerran. Lähteen tunniste säilyy, vaikka nimeä tai osoitetta muutetaan; myös kanavan tunniste säilyy, vaikka kanavan nimeä tai osoitetta muutetaan. `last_checked_at` ja muut ajokohtaiset tarkistushavainnot kuuluvat ajohistoriaan, eivät lähderekisterin pysyvään määritykseen. Tekninen saavutettavuus ja toimituksellinen luotettavuus pidetään erillisinä. Lähteen tai kanavan tärkeys, käyttö kyseisessä tehtävässä ja erityiset seurantahuomiot eivät ole yhteisen perustietueen ominaisuuksia, vaan ne määritellään tehtävätyypin oletuslähteissä tai aiheen ja tehtävätyypin yhdistelmäkohtaisessa lähdemäärityksessä. Tarkka JSON-rakenne ja se, mitkä ominaisuudet voidaan määritellä myös kanavakohtaisesti, ratkaistaan skeemasuunnittelussa.

Lähdekohtaiset ajohavainnot sisältävät lähteen tunnisteen, tarkistuksen tilan (`attempted` tai `not_attempted`) ja yksittäiset avausyritykset. Yritys sisältää tunnisteen, ajankohdan, pyydetyn URL-osoitteen, avauksen tuloksen (`opened` tai `failed`), epäonnistumisen syyluokan silloin kun avaus epäonnistui sekä sisällön luettavuuden (`readable`, `partial`, `unreadable` tai `not_assessed`). `not_attempted` ei ole epäonnistuminen eikä kuulu avausyritysten onnistumisprosentin nimittäjään. Avaamisen onnistuminen erotetaan sisällön luettavuudesta ja hyödyllisyydestä. Valvomo laskee tilastot alkuperäisistä havainnoista eikä luota tuottajan valmiiksi laskemiin prosentteihin. Sekä yrityskohtainen että ajokohtainen onnistumisaste esitetään otoskoon ja tarkastelujakson yhteydessä.

Lähteiden käyttö ratkaistaan kahdessa tasossa. Tehtävätyypin määritys voi sisältää tehtävätyypin yleiset oletuslähteet sekä erikseen nimetyt pakolliset lähteet. Aihekohtainen määritys koskee aina valittua aiheen ja tehtävätyypin yhdistelmää ja valitsee oletuslähteiden käsittelytavan yhdellä kolmesta arvosta: `inherit`, `extend` tai `replace`. `inherit` käyttää tehtävätyypin oletuslähteitä sellaisinaan. `extend` säilyttää oletuslähteet ja sallii aihekohtaisten lähteiden lisäämisen sekä lähteiden yhdistelmäkohtaisten käyttöasetusten muuttamisen. `replace` korvaa tehtävätyypin oletuslähdelistan kokonaan kyseisen yhdistelmän omalla lähdelistalla. `extend` on oletustoimintatapa, jos muuta ei ole nimenomaisesti määritelty. Tehtävätyypin pakolliset lähteet eivät kuulu korvattavaan oletuslähdelistaan, vaan ne säilyvät käytössä myös `replace`-toimintatavassa. Jokainen lopullinen lähdeviittaus yksilöidään yhteisen lähderekisterin vakaalla tunnisteella, eikä sama lähde esiinny lopullisessa lähdelistassa useammin kuin kerran. Käyttöasetukset, kuten käytössäolo, tärkeys ja erityiset seurantahuomiot, voivat vaihdella aiheen ja tehtävätyypin yhdistelmän mukaan. Yhteiset lähteen perustiedot ja ajokohtaiset havainnot pidetään erillään.

Markdown-ohjeille ei tehdä JSON Schemaa. Ohjeiden validointi tarkistaa yksilölliset tunnisteet, tiedoston olemassaolon oikeassa repositoriossa ja kiinnitetyssä commitissa, turvalliset repositoriojuureen suhteutetut polut, ohjeiden järjestyksen ja duplikaattien puuttumisen sekä sen, etteivät ohjeet ole ristiriidassa koneellisten määritysten kanssa. Markdown-etusivua tai muuta rinnakkaista metatietomuotoa ei lisätä.

Kaikki skeemojen `$ref`-viittaukset ratkaistaan samasta kiinnitetystä ohjelmistorevisiosta; ulkoisia tai muuttuvia skeemalähteitä ei käytetä. Määritykset validoidaan yksittäin ja yhdistetty `resolved_config` tehtävätyyppikohtaista asetusskeemaa vasten. Lisäksi ohjelmallisesti tarkistetaan esimerkiksi objektien sisäisten tunnisteiden yksilöllisyys, aikaleimojen offsetien vastaavuus yleiseen IANA-aikavyöhykkeeseen sekä repositorio- ja polkuviittausten eheys. Virhe ilmoittaa tiedoston, kenttäpolun ja syyn ja estää tehtävän muodostamisen.

Tehtäväpyynnön Markdown-ohjeviittaukset kootaan `instructions`-taulukkoon. Jokainen viittaus yksilöi myös repositorion, josta ohje luetaan: ohjelmistorepon yleiset ohjeet sidotaan `software_revision`-tunnisteeseen ja instanssirepon aihe- ja profiilikohtaiset ohjeet `instance_revision`-tunnisteeseen. Taulukko sisältää eksplisiittisen luettelon kaikista kyseisen tehtävän käsittelyssä pakollisesti luettavista ohjeista. Jokaisella käytettävällä profiililla on oma Markdown-ohjetiedostonsa JSON-määrityksen lisäksi. Profiilin Markdown-ohjeen lukeminen on pakollista aina, kun profiilia käytetään.

Ohjeet luetellaan tehtäväpyynnössä tässä järjestyksessä:

1. yhteinen raportintekijän perusprompti ohjelmistoreposta;
2. tehtävätyypin Markdown-ohje;
3. käytettyjen profiilien Markdown-ohjeet siinä järjestyksessä kuin profiilit on ilmoitettu aihekohtaisessa määrityksessä ja yhdistetty konfiguraatioon;
4. aihekohtainen Markdown-ohje.

Jokainen `instructions`-taulukon alkio yksilöi ohjeen `id`-, `repository`- ja `path`-kentillä. Raportintuottaja lukee kaikki luetellut tiedostot eikä päättele muita ohjeita automaattisesti hakemistorakenteesta tai profiilien tunnisteista. Kaikki ohjeet haetaan tehtäväpyynnön `software_revision`- tai `instance_revision`-kentän osoittamasta oikean repositorion Git-commitista. Näin myös profiilien ohjeet pysyvät muuttumattomina koko tehtävän käsittelyn ajan.

Esimerkkirakenne:

```json
{
  "instructions": [
    {
      "id": "news-report",
      "repository": "software",
      "path": "docs/task-types/news-report.md"
    },
    {
      "id": "film-screenings",
      "repository": "instance",
      "path": "docs/profiles/film-screenings.md"
    },
    {
      "id": "indian-cinema",
      "repository": "instance",
      "path": "docs/profiles/indian-cinema.md"
    },
    {
      "id": "indian-film-screenings",
      "repository": "instance",
      "path": "docs/topics/indian-film-screenings.md"
    }
  ]
}
```

Esimerkki havainnollistaa viittausten rakennetta, repositoriovalintaa ja lukujärjestystä; lopulliset repositorioiden nimet ja tiedostopolkurakenne vahvistetaan teknisessä määrittelyssä.

### 2.2.3 Raportintekijän yhteinen perusprompti

Yhteinen raportintekijän perusprompti kuuluu ohjelmistorepoon ja kiinnittyy käytettyyn `software_revision`-revisioon. Tehtäväpyynnön `instructions`-taulukossa se on ensimmäisenä, ennen tehtävätyypin ohjetta, järjestettyjä profiiliohjeita ja aihekohtaista ohjetta. Jokaisella ohjeviittauksella on `repository`- ja `path`-tiedot; ohjelmistorepon ohje luetaan `software_revision`- ja instanssirepon ohjeet `instance_revision`-revisiosta.

Perusprompti määrittelee raportintekijän yleisen toimintamallin: tehtäväpyynnön ja `resolved_config`-määrityksen lukemisen, ohjeiden soveltamisjärjestyksen, lähteiden tarkistamisen, lähdeaineiston käsittelyn epäluotettavana sisältönä, epävarmuuden ja puutteiden ilmoittamisen, raportin muodostamisen sekä toimituspaketin vaatimukset. Se kieltää tehtäväpyynnön tunnisteiden tai asetusten muuttamisen ja puuttuvien tietojen keksimisen. Lähteissä olevia ohjeita käsitellään lähdesisältönä, ei raportintekijän järjestelmäohjeina.

Perusprompti sisältää myös vaatimuksen raportoida lähdekohtaiset avausyritykset ja niiden tulokset erillään sisällön laadusta tai relevanssista. Raportintekijä käyttää vain tehtäväpyynnössä yksilöityjä muuttumattomia ohjeversioita. Promptin tarkka teksti ja mahdollinen tuottajakohtainen sovitus suunnitellaan myöhemmin; tämä arkkitehtuuripäätös ei vielä luo promptitiedostoa eikä muuta nykyisiä automaatioita.

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
- `item.xml`: pakollinen sekä `success`- että `partial`-tilassa. `success`-tilassa validoitu raportti julkaistaan. `partial`-tilassa validoitu osittainen raportti julkaistaan, ja itemissä kerrotaan selvästi seurannan puutteellisuudesta sekä sen syistä. `no_report`- ja `failed`-tiloissa `item.xml`-tiedostoa ei toimiteta.

Tarkka skeema, tiedostonimien säännöt ja toimituksen täydellisyyskriteerit määritellään erikseen. `no_report`- ja `failed`-tulosten toimitus ei saa edellyttää olematonta RSS-item-tiedostoa.

#### `metadata.json`-tiedoston vähimmäissisältö

Metatietotiedosto kuvaa yksittäisen ajon tunnistetiedot, käytetyn määrityskokonaisuuden, seuranta-aikavälin ja lopputuloksen. Raportin varsinainen sisältö pidetään erillään metatiedoista.

Pakolliset perustiedot:

- `schema_version`: metatietorakenteen versionumero;
- `run_id`: yksittäisen ajon yksilöllinen tunniste;
- `topic_id`: seurattavan aiheen tunniste;
- `task_type`: käytetyn tehtävätyypin tunniste;
- `software_revision` ja `instance_revision`: kumpikin täsmälleen 40 merkkiä pitkä Git-commit-SHA, joka sisältää vain heksadesimaalimerkkejä (`0–9`, `a–f`). Ensimmäinen viittaa ohjelmistorepossa ja toinen instanssirepossa olevaan commitiin. Niiden osoittamat sisällöt yksilöivät ajossa käytetyn ohjelmiston ja instanssidatan; arvoja ei normalisoida eikä korvata haaraviittauksilla;
- `period`: toteutuneen ajon seuranta-aikavälin kuvaava objekti, joka sisältää `from`-, `to`- ja `cutoff_at`-kentät. Tämä on toimituksen metatietorakenne, ei tehtäväpyynnön `period`-objekti: tehtäväpyynnössä `period` sisältää vain `from`- ja `to`-kentät. Aikavyöhyke määräytyy tehtäväpyynnön `resolved_config.timezone`-kentästä, eikä sitä kopioida metatietojen `period`-objektiin;
- `profiles`: käytettyjen määritysprofiilien tunnisteet taulukkona;
- `sources`: ajossa tarkistettujen lähteiden tiedot taulukkona;
- `status`: ajon lopputila (`success`, `partial`, `no_report` tai `failed`);
- `started_at` ja `completed_at`: ajon aloitus- ja valmistumishetki.

Kaikki metatiedoston varsinaiset aikaleimat esitetään tehtäväpyynnön `resolved_config.timezone`-asetuksen mukaisessa paikallisessa ajassa ISO 8601 -muodossa, ja jokaisessa aikaleimassa on mukana kyseisen ajanhetken numeerinen UTC-offset. `period.from` on seuranta-aikavälin alku, `period.to` tehtäväpyynnön alkuperäinen loppu (joka voi olla `null`) ja `period.cutoff_at` tarkka hetki, johon asti aineisto tosiasiassa otettiin mukaan. `started_at` ja `completed_at` esitetään samassa aikavyöhykkeessä. Metatietoihin ei lisätä erillistä aikavyöhyketunnistekenttää, koska käytetty IANA-aikavyöhyke saadaan tehtäväpyynnön `resolved_config.timezone`-kentästä ja aikaleimojen offsetit voidaan validoida sitä vasten.

Metatietojen aikaleimojen validointisäännöt:

- `started_at` ja `completed_at` ovat pakollisia kaikissa toimitetuissa tulostiloissa (`success`, `partial`, `no_report` ja `failed`).
- `completed_at` ei saa olla ajallisesti aikaisempi kuin `started_at`.
- Jokaisen aikaleiman numeerisen UTC-offsetin on vastattava tehtäväpyynnön `resolved_config.timezone`-asetuksen IANA-sääntöjä kyseisenä ajanhetkenä. Pelkkä kelvollinen ISO 8601 -muoto ei riitä, jos offset ei vastaa kyseistä aikavyöhykettä.
- `period.from` ja `period.to` vastaavat tehtäväpyynnön saman nimisiä arvoja täsmälleen; `period.to` säilyy myös `null`-arvona, jos tehtäväpyynnössä se on `null`.
- `period.cutoff_at` ei saa olla ajallisesti aikaisempi kuin `period.from`.
- Jokaisen `sources`-taulukon `source_id`-arvon on viitattava lähderekisterissä olevaan lähteeseen siinä määritysversiossa, jonka `instance_revision` yksilöi.

Aikaleimojen vertailu tehdään niiden yksiselitteisten ajanhetkien perusteella, ei paikallisten kellonaikamerkkijonojen aakkosjärjestyksessä.

Tehtäväpyynnön ja toimitusmetatietojen vastaavuus tarkistetaan seuraavasti:

| Tehtäväpyyntö (`data/tehtava.json`) | Toimitus (`metadata.json`) | Tarkistus |
|---|---|---|
| `run_id` | `run_id` | Täsmälleen sama |
| `topic_id` | `topic_id` | Täsmälleen sama |
| `task_type` | `task_type` | Täsmälleen sama |
| `software_revision` | `software_revision` | Täsmälleen sama commit-SHA |
| `instance_revision` | `instance_revision` | Täsmälleen sama commit-SHA |
| `profiles` | `profiles` | Samat tunnisteet samassa järjestyksessä |
| `period.from` | `period.from` | Täsmälleen sama |
| `period.to` | `period.to` | Täsmälleen sama, myös `null`-arvo |
| `resolved_config.timezone` | Ei vastaavaa kenttää | Asetusta ei kopioida toimitukseen; sitä käytetään metatietojen aikaleimojen ja offsetien validointiin |

`metadata.period.cutoff_at` on raportintuottajan ilmoittama toteutunut seurannan päättymishetki. Se ei korvaa tehtäväpyynnön `period.to`-arvoa. Tehtäväpyynnön `issued_at`-, `deadline_at`-, `history`-, `instructions`- ja `resolved_config`-kenttiä ei kopioida toimitusmetatietoihin. Sekä `software_revision` että `instance_revision` tallennetaan toimitusmetatietoihin ajon jäljitettävyyttä varten. Tehtäväpyyntö ja toimitusmetatiedot versioidaan erikseen omilla `schema_version`-kentillään. Lähteen alkuperäinen aikaleima, mahdollinen alkuperäinen offset/aikavyöhyke sekä tulkinnassa käytetyn aikavyöhykkeen alkuperä voidaan säilyttää lähdekohtaisessa tiedossa jäljitettävyyttä varten. Lähderekisterin aikavyöhykemääritys on valinnainen; sen puuttuminen ei oikeuta arvaamaan aikavyöhykettä. Lähteiden ajat muunnetaan Aiheseuraimen yleiseen aikavyöhykkeeseen raporteissa ja käyttöliittymässä.

`profiles` sisältää ajossa käytettyjen profiilien tunnisteet samassa järjestyksessä kuin ne yhdistettiin konfiguraatioon. Taulukko voi olla tyhjä, jos aihe ei käytä profiileja. Profiilien sisältöä tai erillisiä versiotunnisteita ei kopioida metatietoihin: `instance_revision` yksilöi käytetyn instanssidatan revision.

`sources` sisältää kaikki lähteet, joiden tarkistamista ajossa yritettiin. Jokaisesta lähteestä tallennetaan lähderekisteriin viittaava `source_id`, tarkistuksen `status` sekä tarvittaessa lähdekohtainen `error`-objekti:

- `success`: lähde saatiin tarkistettua kokonaan; myös onnistunut tarkistus ilman osumia on `success`. Lähdekohtainen `error`-objekti jätetään pois;
- `partial`: lähteestä saatiin tarkistettua vain osa. Lähdekohtainen `error`-objekti on pakollinen ja kuvaa osittaisuuden teknisen syyn tai muun tunnistetun rajoitteen;
- `failed`: lähteen tarkistaminen epäonnistui. Lähdekohtainen `error`-objekti on pakollinen ja kuvaa epäonnistumisen syyn.

Lähdekohtainen `error`-objekti sisältää virheen tai rajoitteen ennalta määritellyn luokan (`category`) ja lyhyen, turvallisen teknisen selityksen (`description`). Luokkien tulee olla rajattu, dokumentoitu joukko, jotta virheitä voidaan tilastoida ja hyödyntää Valvomossa. Luokkien tarkka luettelo määritellään skeemojen ja teknisen suunnittelun yhteydessä. Selityksestä poistetaan salaisuudet, käyttöoikeustunnisteet, raakasisältö ja tarpeettomat henkilötiedot.

Lähdekohtainen `error`-objekti kuuluu vain metatietoihin. Sitä ei näytetä sellaisenaan lukijalle. Jos lähdevirhe tai rajoite vaikuttaa raportin kattavuuteen, raportissa kuvataan erikseen lukijalle ymmärrettävästi, mitä jäi tarkistamatta ja miten se vaikuttaa tuloksen kattavuuteen.

Lähteitä, joita ei yritetty käyttää, ei luetella. `sources` voi olla tyhjä, jos ajossa ei käytetty lähteitä. Lähteen muut tiedot, kuten nimi, osoite ja luotettavuusluokitus, säilyvät lähderekisterissä ja ovat jäljitettävissä `instance_revision`-kentän avulla. Metatietoihin ei kopioida yksittäisten artikkelien URL-osoitteita eikä teknisiä lokitietoja.

Lähteen tarkistustila ja koko ajon lopputila kuvaavat eri asioita. Lähteen `status` kertoo vain kyseisen lähteen tarkistamisen onnistumisesta; ajon `status` kuvaa koko seurantatehtävän onnistumista ja tuloksen käyttökelpoisuutta. Raportintuottaja arvioi kokonaisuuden, eikä yksittäinen lähdevirhe automaattisesti muuta koko ajoa osittaiseksi tai epäonnistuneeksi.

Esimerkiksi yhden lähteen epäonnistuminen ei estä `success`-tilaa, jos muut lähteet tarjoavat seurannan kannalta riittävän kattavan aineiston. Jos tärkeiden lähteiden puuttuminen heikentää seurannan kattavuutta, ajon tila voi olla `partial`. Jos koko seuranta epäonnistuu, tila on `failed`. Jos seuranta onnistuu kattavasti mutta julkaistavaa raportoitavaa ei löydy, tila on `no_report`. Raportintuottaja tekee arvion tehtävän määritysten ja seurannan tavoitellun kattavuuden perusteella.

Koko ajon tason `error`-objekti vaaditaan vain silloin, kun ajon `status` on `failed`. Se sisältää koko ajon epäonnistumisen virheluokan (`category`) ja lyhyen, turvallisen kuvauksen (`description`); objektia ei sallita muissa ajon tulostiloissa. Tämä koko ajon tason objekti on eri asia kuin edellä kuvattu lähdekohtainen `sources[].error`, jota käytetään yksittäisen lähteen `partial`- tai `failed`-tilan selittämiseen. Kummankaan tason kuvaukseen ei sisällytetä salaisuuksia, käyttöoikeustunnisteita, raakaa keskustelusisältöä tai tarpeettomia henkilötietoja.

Kaikki edellä luetellut perustiedot, mukaan lukien `profiles` ja `sources`, ovat pakollisia kaikissa tulostiloissa; tyhjä taulukko on sallittu. Normaalissa vastaanotossa `run_id` ja `topic_id` tarkistetaan aktiivista tehtäväpyyntöä vasten. Myöhäisen toimituksen jälkikäsittelyssä tunnisteet tarkistetaan alkuperäisen `run_id`-ajon tallennettuja tietoja vasten. `schema_version` kuvaa metatietorakennetta, eikä sitä pidä sekoittaa tehtävän määritysten tai raportin versioon.

#### Toimituspaketin tulostilakohtaiset tiedostovaatimukset

Jokainen toimitus sisältää `metadata.json`-tiedoston. RSS-itemin vaatimus riippuu metatietoihin merkitystä tulostilasta:

| Tulostila | `metadata.json` | `item.xml` | Käsittely |
|---|---|---|---|
| `success` | pakollinen | pakollinen | Validoitu raportti julkaistaan oikeassa RSS-syötteessä. |
| `partial` | pakollinen | pakollinen | Validoitu osittainen raportti julkaistaan; puutteet ja niiden syyt kerrotaan avoimesti. |
| `no_report` | pakollinen | ei toimiteta | Seuranta onnistui, mutta julkaistavaa raporttia ei löytynyt. |
| `failed` | pakollinen | ei toimiteta | Seuranta epäonnistui; metatietoihin kirjataan virheen luokka ja lyhyt, turvallinen kuvaus. |

`no_report` ja `failed` ovat siis normaaleja, eksplisiittisiä ajotuloksia eivätkä puuttuvasta toimituksesta pääteltäviä tiloja. Myös näistä ajoista syntyy tavallinen toimituspaketti, jonka `metadata.json` kirjataan ajohistoriaan. `failed`-tilan virhekuvaukseen ei saa sisällyttää salaisuuksia, tunnisteita, raakaa keskustelusisältöä tai tarpeettomia henkilötietoja.

Ensimmäisessä versiossa toimituspaketin eheys varmistetaan rakenteellisilla ja sisällöllisillä tarkistuksilla ilman erillistä allekirjoitus- tai tarkistussummajärjestelmää.

- `metadata.json` ja mahdollinen `item.xml` toimitetaan saman `run_id`-tunnisteen omaavassa hakemistossa.
- Vastaanottava GitHub Actions -työnkulku tarkistaa vaadittujen tiedostojen olemassaolon ja toimituksen rakenteen.
- Työnkulku validoi metatietojen rakenteen ja tarkistaa normaalissa vastaanotossa, että toimituksen `run_id` sekä aiheen tunniste vastaavat aktiivista tehtäväpyyntöä. Myöhäisen toimituksen jälkikäsittelyssä vastaavuus tarkistetaan alkuperäisen ajon tallennettuja tietoja vasten.
- `success`- ja `partial`-tiloissa RSS-itemin on oltava mukana ja sen XML/RSS-rakenne validoidaan ennen julkaisua.
- `partial`-itemissä kuvataan selvästi, mikä seurannassa jäi puutteelliseksi, miksi näin tapahtui ja miten puute vaikuttaa raportin kattavuuteen.
- `no_report`- ja `failed`-toimituksissa `item.xml`-tiedostoa ei toimiteta; niiden `metadata.json` sisältää tulostilan edellyttämät tiedot.
- Puutteellinen, virheellinen tai väärään tehtävään kuuluva toimitus hylätään kokonaisuutena. Se ei saa johtaa osittaiseen tallennukseen tai RSS-julkaisuun.

Erilliset kryptografiset allekirjoitukset ja tarkistussummat jätetään ensimmäisen version ulkopuolelle. Niiden tarve arvioidaan myöhemmin, jos uhkamalli tai toimituskanavan luonne sitä edellyttää.


#### 2.3.1 Ajotietue myös ilman tuottajan toimitusta

Ajotietueen muodostamisen ja ylläpidon vastuu kuuluu vastaanottavalle järjestelmälle, ei raportintuottajalle. Ajon alussa luotu kanoninen tietue on olemassa riippumatta siitä, saadaanko tuottajalta toimitus. Tietueessa pidetään käsitteellisesti erillään tuottajan toimittama tulos ja vastaanottajan kirjaamat ajonhallintatiedot. Tuottajan tulososa syntyy vain tuottajan toimituksesta; vastaanottajan oma tietue ja käsittelytilat syntyvät myös ilman toimitusta.

- Raportintuottaja vastaa onnistuneiden tulosten ja omien ilmoittamiensa virheiden toimittamisesta yhteisellä `run_id`-tunnisteella.
- Vastaanottava järjestelmä vastaa siitä, että jokaisesta käynnistetystä ajosta syntyy kanoniseen ajohistoriaan ajotietue.
- Jos toimitusta ei saada tehtäväpyynnön määräaikaan mennessä, määräajan valvonta muodostaa ajolle vastaanottajan kirjaaman `failed`-tilaisen ajotietueen. Tuottajan toimitusta tai `metadata.json`-tiedostoa ei edellytetä tämän tietueen muodostamiseen.
- Tietueeseen kirjataan vain vastaanottavan järjestelmän todentama tieto. Esimerkiksi määräajan umpeutuminen voidaan kirjata, jos se on havaittu; tarkempaa teknistä syytä ei päätellä ilman näyttöä.
- Vastaanottajan muodostamaa epäonnistumistietuetta ei esitetä tuottajan toimittamana tuloksena. Tuottajan tulosmetatiedot ja vastaanottajan kirjaamat ajonhallintatiedot pidetään käsitteellisesti erillään.
- Valvomossa tuottajan tulostila ja vastaanottajan ajon lopputila/käsittelytilat esitetään erillisinä tietoina ja niiden alkuperä ilmaistaan. Jos toimitusta ei ole saatu, tuottajan tulos näytetään puuttuvana/tuntemattomana; vastaanottajan `failed`-merkintä ei täytä tätä kenttää.
- RSS-lukija ei käytä ajonhallinnan tiloja eikä päättele niiden perusteella julkaisujen tai seurannan tilaa. Se näyttää vain hyväksytyt RSS-julkaisut RSS-syötteestä.

Tämä täydentää toimitussopimuksen normaalia `failed`-toimitusta: jos tuottaja itse ilmoittaa epäonnistumisesta, se toimittaa tavanomaisen `metadata.json`-tiedoston. Jos mitään toimitusta ei saada määräaikaan mennessä, vastaanottaja muodostaa ajotietueen itsenäisesti. Molemmissa tapauksissa ajon lopputila on `failed`, mutta tietueen tietolähde ja saatavilla oleva virheselitys ovat erilaiset.

#### 2.3.2 Myöhäisen toimituksen jälkikäsittely

Määräajan umpeuduttua vastaanottaja kirjaa ajon epäonnistuneeksi ja voi muodostaa seuraavan tehtävän. Myöhemmin saapuvaa toimitusta ei kuitenkaan hylätä automaattisesti pelkän myöhästymisen vuoksi.

- Vastaanottaja tunnistaa toimituksen aina sen alkuperäisestä `run_id`-tunnisteesta. Myöhäistä toimitusta ei käsitellä sillä hetkellä aktiivisen tehtävän toimituksena.
- Toimituksen `run_id`, aihe, seurantatyyppi ja muut tehtäväkohtaiset tiedot tarkistetaan alkuperäisen ajon tallennettuja tietoja vasten. Toimitus käy läpi samat rakenteelliset, sisällölliset ja RSS-validoinnit kuin määräajassa saapunut toimitus.
- Myöhäinen toimitus voidaan hyväksyä ja julkaista alkuperäisen ajon tuloksena vain, jos samaa aihetta ja seurantatyyppiä koskevaa myöhempää ajoa ei ole vielä käynnistetty ja kaikki normaalit hyväksymisehdot täyttyvät.
- Jos myöhempi saman aiheen ja seurantatyypin ajo on jo käynnistynyt, myöhäistä toimitusta ei julkaista. Se voidaan säilyttää vastaanottoaineistona jäljitettävyyttä varten, mutta sitä ei saa liittää myöhemmän ajon tulokseen.
- Myöhäinen toimitus ei saa muuttaa myöhemmän ajon tehtäväpyyntöä, tulosta, ajotietuetta, tilaa tai RSS-historiaa. Se ei myöskään poista aiempaa määräajan umpeutumisen tai vastaanottajan epäonnistumisen merkintää.
- Määräajan umpeutuminen ja myöhäisen toimituksen saapuminen kirjataan vastaanottajan erillisinä, aikajärjestyksessä säilyvinä tapahtumina. Tapahtumaketjuun kirjataan lisäksi validoinnin aloitus ja tulos, toimituksen hyväksyminen tai hylkääminen sekä mahdollinen RSS-julkaisu tai julkaisun epäonnistuminen. Vain todennettavissa olevat tapahtumat kirjataan.
- Käsittelyä ei tiivistetä yhdeksi yliajettavaksi `success`- tai `failed`-lopputilaksi, joka hävittäisi tapahtumahistorian. Valvomo näyttää alkuperäisen määräajan ylityksen sekä myöhäisen toimituksen vastaanoton, validoinnin, hyväksynnän/hylkäyksen ja julkaisun erillisinä tapahtumina. Ajantasainen käsittelytilanne voidaan johtaa tapahtumista, mutta aiemmat tapahtumat säilyvät muuttumattomina.
- Jos vastaanottaja on jo muodostanut määräajan umpeutumisen vuoksi epäonnistumistietueen, myöhemmin hyväksytty `metadata.json` täydentää samaa kanonista ajotietuetta erillisenä tuottajan tuloksena. Se ei korvaa eikä kirjoita uudelleen vastaanottajan aiempia tietoja. Määräajan ylitys ja havainto siitä, ettei toimitusta saatu määräajassa, säilyvät muuttumattomina; tuottajan ilmoittama tulostila tallennetaan erikseen vain hyväksytystä toimituksesta.
- Myöhäisen toimituksen vastaanotto, validointi ja julkaisu koordinoidaan yhteisen instanssikohtaisen sarjallisuuden hallinnan kautta. Käsittely on idempotenttia: samaa toimitusta tai RSS-GUIDia ei käsitellä tai julkaista uudelleen.

Myöhäisen toimituksen jälkikäsittely ei tarkoita yleistä epäonnistuneiden ajojen uudelleenavaamista tai uuden yrityksen käynnistämistä. Se käsittelee vain tuottajan alkuperäiselle ajolle toimittaman valmiin tuloksen. Vastaanottajan käsittelyhistoria esitetään erillisinä, aikajärjestyksessä säilyvinä tapahtumina eikä yhtenä lopullisena tilana: määräajan ylitys, myöhäinen vastaanotto, validointi, hyväksyntä tai hylkäys sekä mahdollinen julkaisu tai julkaisun epäonnistuminen säilyvät erillisinä. Myöhempi tapahtuma ei ylikirjoita aiempaa tapahtumaa. Tapahtumien tarkka tekninen tietomalli täsmennetään myöhemmin.

### 2.4 RSS-itemien julkaiseminen ja korjauspäivitykset

Sekä `success`- että `partial`-tilassa syntynyt validoitu RSS-item julkaistaan. Osittainen raportti antaa käyttäjälle ajantasaista luettavaa, vaikka kaikkia lähteitä tai aineistoja ei olisi saatu tarkistettua. Puutteellisuus ja sen syyt on ilmaistava itse raportissa selvästi.

Julkaistut RSS-itemit ovat muuttumattomia:

- Aiemmin julkaistua RSS-itemiä ei muokata, korvata eikä poisteta myöhemmän ajon perusteella.
- Raportintuottaja lukee ennen uuden raportin muodostamista kyseisen aiheen ja tehtävätyypin koko aiemman raporttihistorian ilman aikarajaa ja vertaa uusia havaintoja siihen sisällöllisesti. Vertailu perustuu siihen, käsitteleekö havainto samaa asiaa ja tuoko se siihen olennaista uutta tietoa; pelkkä otsikon tai URL-osoitteen yhtäläisyys tai erilaisuus ei ratkaise asiaa.
- Raportintuottaja arvioi uuden tiedon olennaisuuden toimituksellisesti aiheen, tapahtuman ja tiedon merkityksen perusteella. Ensimmäiseen versioon ei määritellä jäykkiä yleisiä kynnysarvoja eikä yksinomaan otsikoihin, URL-osoitteisiin tai muihin yksittäisiin tunnisteisiin perustuvaa duplikaattisääntöä.
- Jos myöhempi ajo löytää aiempaan raporttiin olennaisen lisäyksen tai korjauksen, se julkaisee uuden RSS-itemin korjauspäivityksenä.
- Korjauspäivitys kertoo avoimesti, että se täydentää tai korjaa aiempaa raporttia, kuvaa mitä muuttui ja viittaa alkuperäiseen raporttiin sen pysyvällä tunnisteella tai URL-osoitteella.
- Uusi, aiemmin raportoimaton asia julkaistaan normaalina uutena iteminä. Korjauspäivitystä ei käytetä pelkkään toiston välttämättömään täydennykseen, jos olennaista uutta tietoa ei ole.
- Jokaisella uudella itemillä on oma yksilöllinen GUID. Alkuperäisen itemin GUID ja sisältö säilyvät ennallaan.

Näin RSS-historia pysyy muuttumattomana eikä lukijan tarvitse luottaa aiemmin luetun itemin jälkikäteiseen muuttumiseen.

### 2.4.1 Aiemman raporttihistorian lukeminen

Raportintuottaja tarvitsee ennen uuden raportin muodostamista koko kyseisen aiheen ja tehtävätyypin aiemman RSS-raporttihistorian. Historia luetaan suoraan GitHub-repositoriosta GitHub API:n kautta, ei GitHub Pages -julkaisusta, jotta raportintuottaja ei ole riippuvainen Pages-julkaisun viiveestä.

- Tehtäväpyyntö yksilöi RSS-historian instanssirepositorion `repository`-tunnisteella, tiedostopolulla ja commit-SHA:lla.
- Raportintuottaja hakee tiedoston täsmälleen `history.revision`-kentän osoittamasta commitista, ei muuttuvasta `main`-haarasta.
- Näin raportintuottaja saa koko kyseisen aiheen siihen tehtäväpyyntöön lukitun julkaistun historian, eikä historian sisältö muutu tehtävän käsittelyn aikana.
- RSS-historiaa ei kopioida tehtäväpyyntöön; tehtäväpyyntö sisältää vain tiedoston yksilöinnin ja historian revision.

RSS-historian tiedostopolku muodostetaan aina tehtäväpyynnön `topic_id`- ja `task_type`-arvoista muodossa `rss/{topic_id}/{task_type}.xml`. Saman aiheen ja tehtävätyypin kaikki tehtävät käyttävät samaa RSS-syötettä profiileista riippumatta. Eri profiilien yhdistelmillä tai eri profiileja käyttävillä tehtävillä syntyneet raportit julkaistaan siis samaan syötteeseen, jos `topic_id` ja `task_type` ovat samat. Profiilit kuvaavat tehtävän määrityksiä eivätkä itsessään määritä julkaisukanavaa. Erillinen syöte perustetaan vain, jos kokonaisuus mallinnetaan erilliseksi aiheeksi tai tehtävätyypiksi.

### 2.5 Vastaanotto ja julkaisu käsitellään hallitusti

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

### 2.6 Ajotietojen tallennus

Ajotiedot tallennetaan tässä vaiheessa julkiseen GitHub-repositorioon. Tämä on hyväksytty nykyisen suunnitteluvaiheen ratkaisu.

Julkiseen tallennukseen saa sisällyttää vain tarkoitukseen sopivia ajotietoja. Sinne ei tallenneta salaisuuksia, käyttöoikeustunnuksia, tarpeettomia henkilötietoja, raakaa keskustelusisältöä tai tarpeettomasti kopioitua lähdesisältöä.

Tallennusmuoto ja hakemistorakenne määritellään teknisessä suunnittelussa. Tavoitteena on yksi kanoninen ajohistoria, ei rinnakkaisia tietovarastoja. **Ajotietueiden hakemistorakenne jätetään tässä vaiheessa avoimeksi**; sitä ei lukita esimerkinomaisella polulla eikä päivämäärä-, aihe- tai tehtävätyyppiryhmittelyllä. Julkisen tallennuksen soveltuvuutta arvioidaan uudelleen, jos tietosisältö tai käyttöoikeustarpeet muuttuvat.

#### 2.6.1 Kanoninen ajotietue ja tapahtumahistoria

Jokaisesta käynnistetystä ajosta ylläpidetään yhtä vastaanottavan järjestelmän omistamaa kanonista ajotietuetta. Sen tietosisältö erottaa vähintään tehtävän tiedot, raportintekijän toimittaman tuloksen, vastaanottajan käsittelytiedot, tapahtumahistorian, julkaisun tiedot ja vastaanottajan muodostaman ajon lopputilan. Raportintekijän tulosta ei päätellä vastaanottajan havainnoista eikä vastaanottajan käsittelytilaa raportintekijän ilmoituksesta.

Tapahtumahistoria on loogisesti vain lisäämiseen perustuva ja säilyttää aiemmat tapahtumat muuttumattomina. Jokaisessa tapahtumassa on yksilöivä tunniste tai muu yksiselitteinen järjestysavain, tapahtumatyyppi, tapahtuma-aika, kirjaamis-/havaintoaika tarvittaessa, alkuperä sekä tapahtuman olennaiset tiedot. Tapahtumien järjestystä ei ratkaista pelkästään aikaleimojen perusteella. Tapahtumien alustavia tyyppejä ovat ajon muodostaminen ja käynnistys, tehtävän tarjoaminen, määräajan ylittyminen, toimituksen vastaanotto, validoinnin tulos, tuottajan tuloksen kirjaaminen, hyväksyminen tai hylkääminen, julkaisun aloitus ja tulos, ajon päättäminen sekä tehtävän vapauttaminen. Lopulliset tunnisteet ja JSON-rakenne määritellään skeematyössä.

Ajon lopputilan muodostaa vastaanottava järjestelmä todennettujen käsittelytapahtumien perusteella. Raportintekijän nykyiset tulostilat (`success`, `partial`, `no_report`, `failed`) säilyvät erillisinä tuottajan tietoina. Määräajan ylittyminen on tapahtuma, ei yksinään lopullinen tila. Myöhäinen toimitus täydentää alkuperäistä tietuetta uusilla tapahtumilla eikä poista aiempia havaintoja tai avaa vapautettua tehtävää uudelleen.

#### 2.6.2 Lähdekohtaiset avaus- ja käyttötilastot

Raportintekijä ilmoittaa jokaisesta lähteestä, jonka avaamista se tosiasiallisesti yritti, lähderekisterin vakaan tunnisteen, yrityksen tuloksen ja mahdollisuuksien mukaan epäonnistumisen luokan. Avaamisen onnistuminen erotetaan sisällön saatavuudesta, laadusta, relevanssista ja raportoitavan tiedon löytymisestä. Avaamatta jääneitä lähteitä ei lasketa onnistuneiksi eikä epäonnistuneiksi avausyrityksiksi. Vastaanottaja validoi lähdehavainnot ja tallentaa ne kanoniseen ajohistoriaan siten, että tilastot voidaan yhdistää saman lähdetunnisteen perusteella eri ajoista.

Valvomon tulee esittää lähdekohtaisesti tarkastelujakson avausyritysten määrä, onnistumiset, epäonnistumiset, onnistumisaste nimittäjineen, viimeisin onnistuminen ja epäonnistuminen sekä kehityssuunta. Epäonnistumiset luokitellaan mahdollisuuksien mukaan esimerkiksi tilapäisiin verkkovirheisiin, pysyvältä vaikuttaviin virheisiin, käyttörajoituksiin/estoihin ja muihin tunnistettuihin syihin. Pieni otos, tuntematon syy tai puuttuva havainto ilmaistaan selvästi.

Valvomo voi nostaa toistuvasti epäonnistuvia lähteitä ylläpitäjän tarkistettaviksi ja ehdottaa niiden poistamista käytöstä. Lähdettä ei poisteta eikä poisteta käytöstä automaattisesti pelkkien tilastojen perusteella: tilapäiset häiriöt, käyttörajoitukset, lähteen muuttunut osoite ja havaintojen määrä on arvioitava. Käytöstä poistaminen tehdään lähderekisterin hallittuna muutoksena, ja syy jää dokumentoiduksi.

Tallennusmuoto ja hakemistorakenne määritellään teknisessä suunnittelussa. Lähdehavaintojen täsmällinen tietorakenne ja tilastojen laskentatapa määritellään ajohistorian ja toimitussopimuksen skeematyössä.


### 2.7 Jaettava ohjelmisto ja erilliset instanssit

Aiheseurain suunnitellaan alusta lähtien julkiseksi, jaettavaksi ohjelmistoksi, jonka käyttäjäkohtaiset instanssit ovat siitä erillisiä. Ohjelmiston ja instanssin erottaminen on arkkitehtuurin perusratkaisu, ei myöhempään monen käyttäjän palvelualustaan varautuva lisäominaisuus.

- **Ohjelmistorepo** sisältää yhteisen, uudelleenkäytettävän ohjelmiston: yleisen toimintalogiikan, GitHub Actions -työnkulut, yhteiset skeemat ja tietosopimukset, käyttöliittymien yhteisen toteutuksen, testit sekä kehittäjä- ja käyttöönottodokumentaation. Ohjelmistorepon tulee soveltua jaettavan ohjelmistoversion julkaisemiseen.
- **Instanssirepo** sisältää yhden käyttöönoton omat tiedot ja asetukset: aiheet ja seurantatehtävät, määritysprofiilit, lähderekisterit, instanssin käyttöönottokohtaiset asetukset ja tila sekä kyseisen instanssin RSS-syötteet ja raportti- ja ajohistoria. Instanssirepo ei ole yhteisen ohjelmiston lähdekoodin tai julkaisuversion ensisijainen säilytyspaikka.
- Ohjelmiston ja instanssin välinen raja määritellään versioitujen, dokumentoitujen rajapintojen ja tietosopimusten avulla. Ohjelmisto ei saa olettaa, että instanssin määritykset, lähderekisterit, ajotiedot tai RSS-tiedostot sijaitsevat samassa repositoriossa tai ohjelmistokoodin suhteellisissa poluissa.
- Instanssi käyttää nimenomaisesti valittua ohjelmistoversiota. Uuden ohjelmistoversion julkaiseminen ei päivitä instanssia automaattisesti; instanssin ylläpitäjä päättää päivityksestä ja sen ajankohdasta. Käytössä oleva versio on voitava jäljittää.
- Ensimmäinen toteutus pysyy yksinkertaisena: yksi instanssi, yksi raportintuottaja ja sarjallinen tehtävänkäsittely. Tämä ratkaisu ei edellytä monen instanssin keskitettyä palvelua, monivuokraaja-arkkitehtuuria, käyttäjähallintapalvelua tai rinnakkaisten raportintuottajien varausmekanismia.
- Nykyinen repositorio sisältää siirtymävaiheessa sekä ohjelmistoon että nykyiseen käyttöönottoon liittyviä osia. Niiden välitöntä siirtämistä tai poistamista ei tehdä tämän päätöksen perusteella. Nykyinen sisältö inventoidaan, ohjelmisto- ja instanssikohtaiset osat luokitellaan ja erottamisen migraatio suunnitellaan erikseen ennen tiedostojen siirtämistä tai repositorioiden perustamista.
- **Valvomo ja RSS-lukija** ovat instanssikohtaisia palvelunäkymiä. Niiden yhteinen lähdekoodi, käyttöliittymäkomponentit ja yleinen toiminnallisuus kuuluvat ohjelmistorepoon. Instanssikohtaiset aiheet, asetukset, raportit, RSS-syötteet, ajotiedot ja muut näytettävät tiedot kuuluvat instanssirepoon.
- Käyttöliittymien on saatava instanssin tiedot määritellyn rajapinnan tai tietosopimuksen kautta. Yhteinen käyttöliittymäkoodi ei saa sisältää yhden instanssin aiheita, syötteitä, raportteja tai muita instanssikohtaisia arvoja kovakoodattuina.
- Ensimmäisessä versiossa sekä Valvomo että RSS-lukija julkaistaan julkisina ilman kirjautumista tai käyttöoikeusjärjestelmää. Tämä on mahdollista, koska ensimmäisen version käyttötarkoitukseen ei kuulu salaisten tai yksityisten tietojen käsittely.
- Julkisen Valvomon ja RSS-lukijan käyttämät tiedostot, rajapinnat ja selaimelle toimitettava sisältö eivät saa sisältää salaisuuksia, käyttöoikeustunnuksia, yksityisiä tietoja tai muuta luottamuksellista sisältöä. Tietojen piilottaminen pelkästään käyttöliittymän esitystasolla ei riitä.
- Jos myöhempi käyttötarve edellyttää luottamuksellisen tiedon käsittelyä, tietojen erottelu ja käyttöoikeuksien tekninen toteutus suunnitellaan erikseen ennen tällaisen tiedon käyttöönottoa.
- Repositorioiden nimet, täsmällinen hakemistorakenne, ohjelmiston jakelukanava ja instanssin käyttöönoton tekninen toteutus ratkaistaan myöhemmässä teknisessä suunnittelussa. Niitä ei lukita tällä arkkitehtuuriperiaatteella.

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
7. Git-tageja käytetään rajatusti hyväksyttyjen kehityksen kiintopisteiden ja ohjelmistoversioiden merkitsemiseen:
   - Tavallisista dokumentti- tai koodimuutoksista tai toteutussuunnitelman yksittäisistä väliversioista ei luoda tageja automaattisesti.
   - Kun koko toteutussuunnitelma on tarkistettu ja hyväksytty, sen hyväksytty lähtötilanne merkitään annoted Git-tagilla. Tagin nimi ja kuvaus yksilöivät hyväksytyn suunnittelutilanteen.
   - Varsinaiset ohjelmistoversiotagit otetaan käyttöön vasta ohjelmiston toteutuksen alettua. Versiotunnisteet noudattavat semanttista versionumerointia, esimerkiksi `v0.1.0`.
   - Julkisesta ohjelmistoversiosta voidaan lisäksi luoda GitHub Release. Tagit eivät korvaa commit-historiaa, GitHub Issues -tehtäviä tai toteutussuunnitelman versionumerointia.
   - Tagin luominen on erillinen toimenpide: hyväksytyn suunnitteluratkaisun kirjaaminen tähän dokumenttiin ei itsessään luo tagia.

Nämä ovat tavoitetilan päätöksiä, eivät vielä toteutettuja käytäntöjä. Niiden käyttöönotto suunnitellaan vaiheittain. PR-pakkoa tai automaattisia riippuvuuspäivityksiä tuotantoon ei oteta käyttöön ilman erillistä hyväksyntää.

## 5. Ehdotettu toteutuksen vaiheistus

1. Nykyisen toteutuksen ja arkiston komponenttikohtainen inventaario.
2. Tehtävätyyppien, määritysprofiilien ja aihekohtaisten määritysten sekä toimitussopimuksen skeemojen määrittely, mukaan lukien tehtäväpyynnön, toimituksen ja kanonisen ajohistorian erilliset tietosopimukset.
3. Yhteisen raportintekijän peruspromptin ja tehtäväpyynnön ohjeviittausten määrittely ja versionhallinta.
4. Ajonhallinta: yhden aiheen valinta, `run_id`, ajotietue ja koko instanssin kattava sarjallisen käsittelyn suoja, joka sallii vain yhden aktiivisen raportointitehtävän kerrallaan.
5. Vastaanottohaara ja Git push -toimituspaketin käsittely.
6. Validointi, kanoninen ajohistoria, lähdekohtaisten avausyritysten tallennus ja idempotentti RSS-julkaisu.
7. Valvomon kolme perusnäkymää sekä lähdekohtaiset avaus- ja käyttötilastot.
8. RSS-lukijan yhteensopivuuden varmistaminen.
9. Hyväksyttyjen GitHub-käytäntöjen ja laajennettujen laatutarkistusten käyttöönotto.
10. Nykyisten automaatioiden mahdollisen siirtymän erillinen suunnittelu ja hyväksyntä.

Vaiheistus on suunnitteluehdotus. Se ei anna lupaa käynnistää tuotantoa tai muuttaa nykyisiä automaatioita.

## 6. Myöhempiin versioihin jätetyt kehitystehtävät

Tässä osiossa pidetään kirjaa asioista, jotka on tietoisesti rajattu ensimmäisen version ulkopuolelle tai joiden toteutusta on päätetty lykätä. Ne eivät ole ensimmäisen version avoimia hyväksymiskriteerejä. Asia siirretään toteutussuunnitelman varsinaiseen työvaiheeseen vasta, kun sen toteutusajankohta ja laajuus päätetään.

| Myöhemmäksi jätetty asia | Miksi myöhemmin | Milloin asiaan palataan |
|---|---|---|
| RSS-historian lukemisen optimointi, kuten indeksointi, hakupalvelu tai tiivistelmä-/välimuistiratkaisu | Ensimmäisessä versiossa raportintuottaja lukee koko kyseisen aiheen ja tehtävätyypin RSS-historian suoraan GitHubista. Erillistä hakukerrosta ei tarvita ennen kuin historian koko tai lukemisen kustannus aiheuttaa todellisen ongelman. | Kun RSS-historian koko, käsittelyaika tai raportintuottajan käytettävissä oleva konteksti tekee koko historian lukemisesta epäkäytännöllistä. Alkuperäinen RSS-historia säilyy tällöinkin vertailun lähteenä. |
| Useat samanaikaiset raportintuottajat, tehtävien varaukset ja rinnakkaisuuden hallinta | Ensimmäisessä versiossa on yksi raportintuottaja ja tehtävät käsitellään sarjallisesti. | Kun käyttöön tulee toinen raportintuottaja tai rinnakkaisille ajoille syntyy todellinen tarve. |
| Erillinen GitHub App tai raportintuottajan teknisesti rajatut kirjoitusoikeudet | Ensimmäinen versio käyttää nykyistä GitHub App -yhteyttä; erillistä käyttöoikeusjärjestelyä ei rakenneta ennakolta. | Kun raportintuottajia tai muita integraatioita tulee lisää tai käyttöoikeuksien eriyttäminen muuttuu tarpeelliseksi. |
| Älykkäämpi epäonnistuneiden tehtävien palautuslogiikka | Ensimmäisessä versiossa käytettävien automaattisten käsittely-yritysten määrät, laskentatavat ja määräajat ovat tehtävätyypin määrityksissä ja tarvittaessa profiileissa määritettäviä konfiguroitavia arvoja; niitä ei kovakoodata. | Kun käytännön ajohistoria osoittaa, että yksinkertainen palautusmalli ei riitä. |
| Ulkoiset ilmoitukset | Ne eivät ole välttämättömiä ensimmäisen version seuranta-, vastaanotto- ja julkaisuketjulle. | Kun ilmoituksille määritellään konkreettinen käyttäjätarve ja kanava. |
| Toimitusten kryptografiset allekirjoitukset ja erilliset tarkistussummat | Ensimmäiseen versioon riittävät toimituspaketin tiedostojen, rakenteen, tunnisteiden ja aktiiviseen tehtävään kuulumisen tarkistukset. | Jos uhkamalli tai toimituskanavan luonne osoittaa vahvemman eheyden todentamisen tarpeelliseksi. |
| Batch-ajot eli usean aiheen käsittely yhdellä käynnistyksellä | Ensimmäisen version yksinkertainen toimintamalli käsittelee enintään yhden aiheen yhdellä käynnistyksellä. | Jos yhden aiheen ajomalli osoittautuu käytännössä rajoittavaksi ja batch-ajolle on selkeä tarve. |

Luetteloa ylläpidetään suunnittelun edetessä. Kun myöhemmäksi jätetty asia otetaan työn alle, se siirretään tästä osiosta asianomaiseen toteutusvaiheeseen ja tarvittaessa avoimiin teknisiin yksityiskohtiin. Näin samaa asiaa ei ylläpidetä kahdessa paikassa ristiriitaisin tilatiedoin.

## 7. Avoimet tekniset yksityiskohdat

Seuraavat asiat täsmennetään ennen tikettien muodostamista:

- miten skeemojen tarkat JSON Schema Draft 2020-12 -tiedostot, kenttäkohtaiset rajat ja validointitoteutus määritellään; skeemakokonaisuuden vastuut ja tehtäväpyynnön `inputs`-rakenne on päätetty kohdissa 2.2.1 ja 2.2.2;
- miten yhteisen lähderekisterin ja tehtävätyypin oletuslähteiden tarkka tiedostorakenne, lähdeviittausten skeema sekä `inherit`-, `extend`- ja `replace`-toimintatapojen kentät ja validointisäännöt määritellään;
- miten nykyisen GitHub App -yhteyden tosiasialliset oikeudet ja `main`-haaran suojaus varmistetaan käyttöönotossa; ensimmäisessä versiossa ei edellytetä teknistä, vain `raportit-inbox`-haaraan rajattua kirjoitusoikeutta;
- miten toimituspaketin tarkat tulostilakohtaiset tiedostovaatimukset ja skeemat määritellään; eheys- ja täydellisyysperiaatteet on päätetty kohdassa 2.3;
- miten `metadata.json`-tiedoston tarkka skeema määritellään, mukaan lukien tuottajan tuloksen ja vastaanottajan ajonhallinnan erottelu, tapahtumien rakenne ja lähdekohtaiset avausyritysten havainnot;
- miten raportintekijän yhteinen perusprompti kirjoitetaan, testataan ja versioidaan ohjelmistorepossa sekä miten se sovitetaan tuottajaintegraation käyttöön;
- miten lähdekohtaisten avausyritysten onnistumiset, epäonnistumiset, virheluokat ja tarkastelujaksot esitetään tilastoina sekä millä periaatteilla toistuvasti epäonnistuva lähde ehdotetaan poistettavaksi käytöstä;
- miten vastaanottohaaran toimituksia säilytetään ja siivotaan turvallisesti;
- miten julkaisun ja ajotietojen tallennuksen virhetilanteista palaudutaan;
- miten julkisten käyttöliittymien ja niiden lukemien tietolähteiden sisältö tarkistetaan automaattisesti niin, ettei niihin päädy salaisuuksia tai yksityisiä tietoja;
- mitkä vanhan toteutuksen komponentit kannattaa säilyttää.

### Versiohistoria

- **0.3.59 (22.11.2026):** täsmennettiin yhteisen lähderekisterin tukevan saman lähteen erillisiä sisältökanavia omine vakaine tunnisteineen ja osoitteineen. Kanavat voidaan valita ja arvioida tehtäväkohtaisesti erikseen; tarkka skeemarakenne jätettiin skeemasuunnitteluun.
- **0.3.58 (22.11.2026):** hyväksyttiin yhteinen lähderekisteri, tehtävätyypin oletuslähteet ja mahdolliset pakolliset lähteet sekä aiheen ja tehtävätyypin yhdistelmäkohtaiset lähdemääritykset. Määriteltiin `inherit`-, `extend`- ja `replace`-toimintatavat ja pakollisten lähteiden säilyminen myös oletuslistan korvaamisessa.

- **0.3.57 (22.11.2026):** määriteltiin JSON Schema Draft 2020-12 -skeemakokonaisuus, tehtävätyyppikohtaiset asetusskeemat, tehtävätyyppiin sidotut profiilit, Markdown-ohjeiden erillinen validointi ja tehtäväpyynnön rakenteisten aineistojen `inputs`-viittaukset. Lähderekisterin aihekohtainen rajaus jätettiin avoimeksi jatkokeskusteluun.

- **0.3.56 (22.11.2026):** yhdenmukaistettiin tehtäväpyynnön ohjejärjestys ja aikavälin puoliksi avoin tulkinta yhteisen peruspromptin sekä raportointijaksojen rajojen osalta.

- **0.3.55 (22.11.2026):** lisättiin ohjelmistorepoon kuuluva yhteinen raportintekijän perusprompti ja sen ohjeviittausten järjestys, tehtäväpyynnön aikavälin puoliksi avoin tulkinta, kanonisen ajotietueen säilyvän tapahtumahistorian periaatteet sekä lähdekohtaiset avausyritystilastot ja Valvomon lähdenäkymä. Ajotietueiden hakemistorakenne jätettiin avoimeksi; lähteiden automaattista käytöstä poistamista ei sallita pelkkien tilastojen perusteella.

- **0.3.54 (22.11.2026):** määriteltiin kolmitasoinen määritysmalli ja sen yhdistämisjärjestys, suojatut asetukset, erillinen skeema- ja oletusarvovastuu, yksittäisten ja yhdistettyjen määritysten validointi sekä muuttumaton `resolved_config`-snapshot. Täsmennettiin virheellisten määritysten käsittely ja rajattiin rekursiiviset profiiliriippuvuudet sekä dynaamiset yhdistämismekanismit pois.\n\n- **0.3.53 (22.11.2026):** määriteltiin käsittelyn valmistuminen ja aktiivisen tehtävän vapauttaminen. Tuottajan tulos, vastaanottajan käsittely ja ajon lopputila erotettiin. Uudelleenyritysten määrät ja muut vastaavat käsittelyrajat määriteltiin konfiguroitaviksi, eikä niitä kovakoodata.

- **0.3.52 (22.11.2026):** hyväksyttiin tehtäväpyynnön täsmällinen ylätason rakenne ja kenttäkohtaiset tietovaatimukset. Täsmennettiin profiiliviittaukset objekteiksi, joissa ovat id, repository ja path, ohjeviittausten sallitut repositoriot, lowercase-commit-SHA-muoto sekä tuntemattomien ylimääräisten kenttien hylkääminen.

- **0.3.51 (22.11.2026):** hyväksyttiin myöhäisen toimituksen vastaanottokäsittelyn esittäminen erillisinä, aikajärjestyksessä säilyvinä tapahtumina. Tapahtumaketju kattaa määräajan ylityksen, myöhäisen vastaanoton, validoinnin, hyväksynnän/hylkäyksen ja mahdollisen julkaisun; aiempia tapahtumia ei ylikirjoiteta.

- **0.3.50 (22.11.2026):** täsmennettiin myöhäisen hyväksytyn toimituksen suhde jo muodostettuun kanoniseen ajotietueeseen: toimitus täydentää tietuetta erillisenä tuottajan tuloksena eikä korvaa vastaanottajan aiempia määräajan ylityksen ja toimituksen puuttumisen havaintoja.

- **0.3.49 (22.11.2026):** määriteltiin myöhäisen toimituksen rajattu jälkikäsittely alkuperäisen `run_id`-tunnisteen perusteella. Julkaisu sallitaan vain, jos myöhempää saman aiheen ja seurantatyypin ajoa ei ole käynnistetty; myöhäinen toimitus ei muuta myöhempien ajojen tietoja tai tiloja.

- **0.3.48 (22.11.2026):** yhtenäistettiin vaatimusmäärittelyn kanssa tehtävän muodostuksen, määräajan valvonnan ja toimituksen vastaanoton yhteinen sarjallisuusvaatimus.

- **0.3.47 (22.11.2026):** täsmennettiin, että tehtävän muodostus, määräajan valvonta ja toimituksen vastaanotto/käsittely kuuluvat yhteisen instanssikohtaisen sarjallisuuden hallinnan piiriin. Tekninen koordinointitapa jätettiin myöhempään suunnitteluun.

## 8. Hyväksymismenettely

Tämä dokumentti täydentyy teknisten yksityiskohtien ratkaisun ja nykyisen toteutuksen katselmoinnin perusteella. Käyttäjä tarkistaa ja hyväksyy toteutussuunnitelman kokonaisuutena ennen tikettien luomista.

Toteutussuunnitelman hyväksyminen, tikettien luominen, toteutuksen aloittaminen ja tuotantoon siirtyminen ovat erillisiä vaiheita. Nykyisten automaatioiden ajastuksia, ohjeita, kehotteita tai kohdekeskusteluja ei muuteta ilman erillistä lupaa.
