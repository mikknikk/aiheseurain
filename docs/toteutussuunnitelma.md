# Aiheseuraimen toteutussuunnitelma

**Versio:** 0.3.109  
**Päiväys:** 25.11.2026  
**Tila:** suunnitteluluonnos – hyväksytyt arkkitehtuuriperiaatteet ja ensimmäisen vaiheen tehtävänjakomalli kirjattu, tekniset yksityiskohdat avoinna  
**Perusta:** [Vaatimusmäärittely 0.12.65](vaatimusmaarittely-uudistus.md)

> Tämä dokumentti kokoaa keskustelussa hyväksytyt tekniset suunnitteluratkaisut. Se ei ole lupa toteuttaa järjestelmää, muuttaa nykyisiä automaatioita tai niiden ajastuksia eikä ottaa uutta tuotantoprosessia käyttöön. Toteutustiketit muodostetaan vasta, kun toteutussuunnitelma on kokonaisuutena tarkistettu ja hyväksytty.

## 1. Tavoite

Toteutussuunnitelma määrittelee, miten vaatimusmäärittelyn mukainen Aiheseurain rakennetaan. Se toimii myöhemmin GitHub-tikettien muodostamisen perustana.

Perusratkaisun tulee olla mahdollisimman yksinkertainen. Raportintuotanto erotetaan deterministisestä ohjaus-, vastaanotto- ja julkaisukerroksesta.

Instanssin yleinen aikavyöhyke määritetään instanssin asetuksissa IANA-aikavyöhyketunnisteena, esimerkiksi `Europe/Helsinki`. Se välitetään tehtäväpyynnön `resolved_config.timezone`-kentässä eikä sitä voi ylikirjoittaa tehtävätyypin asetuksilla, profiileilla tai aihekohtaisilla määrityksillä. Asetusta käytetään paikallisen ajan tulkintaan ja raportointijaksojen sekä aikataulujen rajoihin. Aikaleimat säilytetään yksiselitteisinä UTC-aikoina tai ISO 8601 -aikoina asianmukaisine UTC-offseteineen; RSS-itemin `<pubDate>` tuotetaan UTC-ajassa. Suoritusympäristön tai käyttäjän sijaintia ei käytetä aikavyöhykkeen päättelemiseen.

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

Yleinen `timezone` sisällytetään jokaiseen tehtäväpyynnön `resolved_config`-snapshotiin, jotta raportintuottaja käyttää täsmälleen samaa aikavyöhykettä. `period`-objekti ei tarvitse erillistä aikavyöhykekenttää. Lähteen aikaleima, jossa on jo UTC-offset tai yksiselitteinen aikavyöhyketieto, tulkitaan ensisijaisesti sen mukaisesti. Tapahtuman ajankohtaa tulkittaessa myös tapahtumapaikan luotettavasti tunnettu aikavyöhyke on ensisijainen. Jos aikaleimassa ei ole aikavyöhyketietoa eikä tapahtumapaikka ratkaise tulkintaa, käytetään seuraavaa etusijajärjestystä: (1) kyseisen sisältökanavan dokumentoima aikavyöhyke, (2) lähteen dokumentoima aikavyöhyke, (3) lähderekisteriin nimenomaisesti määritelty valinnainen oletusaikavyöhyke, (4) lähteen julkaisumaan tai toimituksen sijainnin perusteella luotettavasti päätelty aikavyöhyke. Lähteen ja sisältökanavan aikavyöhykemääritykset ovat valinnaisia IANA-tunnisteita, ja kummankin yhteydessä kirjataan tiedon alkuperä: lähteen tai kanavan ilmoittama tieto tai ylläpidon tekemä päätelmä. Kanavan määritys voi tarkentaa tai ohittaa lähteen yleisen oletuksen. Lähteen maata ei käytetä automaattisena oletuksena, jos tarkempi tieto on saatavilla; kansainvälisen julkaisijan tai usealla aikavyöhykkeellä toimivan toimituksen aikavyöhykettä ei päätellä pelkän maan perusteella. Jos aikavyöhykettä ei voida luotettavasti määrittää, lähdeaikaa ei arvata eikä sitä käytetä aikarajaukseen ennen kuin tulkinta voidaan ratkaista. Lähteiden ajat muunnetaan Aiheseuraimen yleiseen aikavyöhykkeeseen raporteissa ja käyttöliittymässä. Alkuperäinen lähdeaikaleima, mahdollinen alkuperäinen offset/aikavyöhyke sekä tulkinnassa käytetyn aikavyöhykkeen alkuperä voidaan säilyttää jäljitettävyyttä varten.

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

Järjestelmän tarkistusväli on yksi yhteinen ja kiinteä ajastus tälle työnkululle. Se on eri asia kuin yksittäisen aiheen ja tehtävätyypin suoritusväli: jälkimmäinen määritellään kyseisen yhdistelmän määrityksessä, ja työnkulku käynnistää tehtävän vasta sen eräännyttyä sekä muiden käsittelyehtojen täyttyessä. Näin yhteinen työnkulku voi tarkistaa jonon ja määräajat säännöllisesti ilman, että kaikkia aiheita käsitellään jokaisella tarkistuskerralla. Yhteisen työnkulun kiinteä tarkistusväli on **15 minuuttia**. Väli koskee jonon ja aktiivisen tehtävän määräajan tarkistamista; aihekohtainen suoritusväli säilyy erillisenä. GitHub Actionsin ajastus ei takaa täsmällistä käynnistymistä: ruuhkat voivat viivästyttää ajoa tai estää yksittäisen ajastetun käynnistyksen kokonaan. Siksi 15 minuuttia on tavoiteltu tarkistusväli, ei täsmällinen palvelutasolupaus.

Työnkulku voidaan käynnistää myös manuaalisesti esimerkiksi ylläpitoa, testausta tai poikkeustilanteen selvittämistä varten. Manuaalinen käynnistys suorittaa täsmälleen saman tarkistus- ja käsittelylogiikan kuin ajastettu käynnistys: se tarkistaa aktiivisen tehtävän, määräajan ja jonon sekä noudattaa tehtävän muodostamisen ehtoja. Manuaalinen käynnistys ei ohita aktiivista tehtävää, määräaikoja, tehtävien sarjallisuutta tai aihekohtaisia suoritusvälejä eikä tarjoa erillistä pakotettua aiheen käynnistämistä. Näin myös manuaalinen käynnistys säilyttää yhden aktiivisen tehtävän mallin.


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
7. toimitusmetatietojen skeema;
8. toimituspaketin tulostilakohtaiset skeemat;
9. vastaanottajan kanonisen ajotietueen ja tapahtumahistorian skeemat.

Tehtävätyypin määrityksen rakenne sisältää `schema_version`-, `id`-, `description`-, `config_schema`-, `defaults`-, `overridable_paths`-, `processing`-, `reporting`- ja `instruction`-kentät. `overridable_paths` ilmaisee JSON Pointer -polkuina täsmälleen ne asetuskohdat, joita profiilit ja aihekohtainen määritys saavat ylikirjoittaa. Tehtävätyyppikohtainen asetusskeema määrittelee `resolved_config`-objektin rakenteen, tietotyypit, pakollisuuden, rajat ja tuntemattomien kenttien hylkäämisen.

Määritysprofiilin rakenne sisältää `schema_version`-, `id`-, `task_type`-, `description`-, `settings`- ja `instruction`-kentät. Profiilin `task_type`-arvon on vastattava tehtäväpyynnössä valittua tehtävätyyppiä. Profiili ei peri toista profiilia. Aihekohtainen määritys sisältää `schema_version`-, `topic_id`-, `task_type`-, `enabled`-, `profiles`-, `settings`-, `source_registry`- ja `instruction`-tiedot. Profiiliviittaukset säilyttävät järjestyksen.

Yhteinen lähderekisteri tallennetaan ensimmäisessä versiossa yhteen tiedostoon `data/sources/registry.json`, jonka juurikentät ovat `schema_version` ja `sources`. Keskitetty tiedosto helpottaa koko rekisterin tunnisteiden yksilöllisyyden ja viittausten validointia. Hakemistorakenne ja tiedostopolut määritellään tavoitetilan mukaisesti puhtaalta pöydältä; vanhan toteutuksen tiedostorakennetta ei käytetä lähtökohtana.

Lähteen tietue sisältää kentät `id`, `name`, `publisher`, `source_type`, `description`, `homepage_url`, `languages`, `regions`, `reliability`, `reliability_notes`, valinnaiset `timezone` ja `timezone_basis`, `technical_access` sekä `channels`. Lähdetyypit ovat `news_media`, `official_source`, `social_media`, `forum`, `blog`, `database`, `video_platform`, `event_listing` ja `other`. Luotettavuusluokitus on `high`, `medium`, `low` tai `unassessed`; se on lähteen toimituksellinen arvio, ei tae yksittäisen sisällön oikeellisuudesta. Kielet ilmaistaan BCP 47 -tunnisteilla ja alueet ISO 3166-1 alpha-2 -koodeilla tai arvolla `global`. Tyhjä lista tarkoittaa määrittelemätöntä tietoa.

Jokaisella lähteellä on vähintään yksi sisältökanava. Kanavalla on `channel_id`, `name`, `url`, `channel_type`, `content_scope`, mahdolliset kieli- ja aluetarkennukset, valinnaiset `timezone` ja `timezone_basis` sekä oma `technical_access`. Kanavatyypit ovat `website`, `rss`, `api`, `social_profile`, `video_channel`, `database_endpoint`, `event_calendar` ja `other`. Kanavien valinta on aina eksplisiittinen: pelkkä lähdeviittaus ilman kanavatunnistetta ei tarkoita kaikkien kanavien valitsemista.

Lähdetason `technical_access` kuvaa julkaisijaa tai verkkopalvelua yleisesti ja voi sisältää `access_model`-arvon (`public`, `account_required`, `subscription_required`, `mixed`, `unknown`), `terms_url`-, `api_documentation_url`-, `usage_limit_notes`- ja `notes`-tiedot. Kanavatason tekniset tiedot voivat tarkentaa käyttömallia sekä kuvata `content_format`-arvon (`html`, `rss`, `atom`, `json`, `xml`, `pdf`, `video`, `mixed`, `unknown`), JavaScript-riippuvuuden, sivutustavan (`none`, `page_number`, `cursor`, `infinite_scroll`, `unknown`) ja kanavakohtaiset käyttörajoitteet. Ajokohtaiset HTTP-tilat, vasteajat, avaus- ja lukemisvirheet sekä onnistumiset tallennetaan ajohistoriaan. Aikavyöhyke ja sen määrityksen peruste annetaan aina yhdessä.

Lähde- ja kanavatunnisteet noudattavat hyväksyttyä slug-syntaksia. Lähdetunniste on rekisterissä yksilöllinen ja kanavatunniste globaalisti yksilöllinen. Tunniste säilyy nimen tai osoitteen muuttuessa, eikä poistettua tunnistetta käytetä uudelleen. Kanava kuuluu täsmälleen yhdelle lähteelle.

Tehtävätyypin määrityksessä on `default_sources`- ja `required_sources`-luettelot. Oletuslähteen käyttömerkintä yksilöi `source_id`-tunnisteen, `priority`-arvon, `roles`-roolit ja valitut `channels`. Tärkeys on kokonaisluku 1–5, jossa 1 on tärkein; uuden lähteen oletustärkeys on 3. Roolit ovat `primary`, `discovery`, `verification`, `official_confirmation` ja `context`. Lähdemerkinnän tärkeys ja roolit toimivat kanavien oletusarvoina, ja kanavakohtaiset käyttöasetukset voivat korvata ne sekä sisältää kanavakohtaiset seurantahuomiot. Roolitaulukko korvataan kokonaan. Rekisterin pysyviä perustietoja ei voi muuttaa näillä käyttöasetuksilla. Pakollinen lähde määritellään täsmällisenä `source_id`–`channel_id`-parina, jonka on löydyttävä tehtävätyypin oletuslähteistä.

Aihekohtainen lähdevalinta on aiheen ja tehtävätyypin yhdistelmäkohtainen `source_selection`-objekti, jossa ovat `mode`- ja `entries`-kentät. Jos objekti puuttuu, oletus on `extend` ilman lisämerkintöjä. `inherit`-toimintatapa käyttää oletuslistaa sellaisenaan eikä salli `entries`-merkintöjä. `extend` säilyttää oletukset ja sallii lisäykset sekä käyttöasetusten tarkentamisen; oletuslähteitä ei voi poistaa. `replace` korvaa valinnaiset oletuslähteet aihekohtaisella listalla, mutta pakolliset lähteet säilyvät. Puuttuva pakollinen pari lisätään alkuperäisine oletusasetuksineen; mukana olevan pakollisen parin asetuksia voidaan tarkentaa, mutta sitä ei voi poistaa.

Lopullisen listan järjestys on deterministinen: `inherit`-tilassa oletusjärjestys, `extend`-tilassa oletusjärjestys ja sen jälkeen uudet merkinnät aihekohtaisessa järjestyksessä, `replace`-tilassa aihekohtainen järjestys ja lopuksi puuttuvat pakolliset parit `required_sources`-järjestyksessä. Tärkeys ei määrää listajärjestystä. Sama lähde–kanava-pari saa esiintyä lopullisessa listassa vain kerran.

Validointi tarkistaa lähde- ja kanavatunnisteiden yksilöllisyyden, lähteen vähintään yhden kanavan, kanavan omistajuuden, absoluuttiset HTTP/HTTPS-osoitteet, aikavyöhykkeen ja määritysperusteen parillisuuden, kieli-, alue- ja luokitteluarvojen kelvollisuuden, kaikki rekisteriviittaukset, pakolliset parit, duplikaatit sekä toimintatapojen säännöt. `inherit` ei salli aihekohtaisia merkintöjä, `extend` ei saa poistaa oletuksia ja `replace` ei saa poistaa pakollisia lähteitä. Puuttuvia lähteitä tai kanavia ei korvata automaattisesti.

Rekisterin ulkopuolinen lähdehaku ja uusien lähteiden rekisteröinti määritellään kahtena itsenäisenä asetuksena. `source_discovery.mode` saa arvon `disabled` tai `use_unregistered`: ensimmäinen rajoittaa käytön tehtäväpyynnön rekisteriin, jälkimmäinen sallii raportintuottajan etsiä ja käyttää uusia lähteitä kyseisessä ajossa. `source_registry_addition.mode` saa arvon `disabled`, `propose` tai `automatic`: lähteitä ei tallenneta, niistä muodostetaan ylläpitäjän tarkistettavia ehdotuksia tai ne lisätään rekisteriin automaattisesti validoinnin jälkeen. Molemmat ovat tehtävätyypin asetuksia, joita profiilit ja aihekohtainen määritys voivat ylikirjoittaa aiemmin hyväksytyn asetusten yhdistämisjärjestyksen ja ylikirjoitettavuussääntöjen mukaisesti. Jos lähdehaku on `disabled`, rekisteröintiasetus ei yksin etsi uusia lähteitä eikä sillä ole rekisteröitävää sisältöä.

Raportintuottaja ei koskaan muuta ajossa käytettävää lähderekisteriä. Tehtäväpyynnön `instance_revision` pysyy ajon ajan muuttumattomana snapshotina. Rekisterin ulkopuoliset lähteet voidaan käyttää ajossa lähdehaun salliessa, mutta niiden lähdetiedot ja mahdolliset rekisteröintiehdotukset toimitetaan erillisinä ajon tulostietoina. Ehdotukset käsitellään vasta, kun ajo on päättynyt. `disabled`-tilassa pysyvää ehdotusta ei tallenneta, `propose`-tilassa ehdotus asetetaan ylläpitäjän hyväksyttäväksi ja `automatic`-tilassa ehdotus validoidaan ja lisätään rekisteriin hallitussa päivityksessä. Uusi rekisterirevisio tulee käyttöön vasta seuraavissa ajoissa.

Rekisteröinti edellyttää lähteen perustietojen ja vähintään yhden sisältökanavan validointia sekä duplikaattitarkistusta. Tarkistus vertaa vähintään julkaisijaa ja lähde-/kanavaosoitteita sekä muita käytettävissä olevia tunnistetietoja; olemassa olevaan lähteeseen kuuluva uusi kanava liitetään olemassa olevaan lähteeseen eikä samaa lähdettä luoda uudelleen. Automaattisesti lisätyn lähteen luotettavuusluokitus on `unassessed`, kunnes se on erikseen arvioitu. Alkuperä ja löytämisajankohta säilytetään. `propose`-tilassa ylläpitäjän hyväksyntä vaaditaan ennen rekisteriin lisäämistä; `automatic` ei tarkoita toimituksellisen luotettavuuden automaattista hyväksymistä. Käytettyjen rekisterin ulkopuolisten lähteiden alkuperä ja tila on erotettava ajon tiedoissa rekisteriin kuuluvista lähteistä.

Lähde-ehdotus on lähdekohtainen tietue, jossa ovat pysyvä `proposal_id`, lähteen perustiedot, vähintään yksi sisältökanava, mahdolliset kieli- ja aluetiedot, alustava luotettavuusluokitus, löytämisajankohta ja -alkuperä, perustelu sekä ehdotuksen tuottaneen `run_id`-ajon viite. Ehdotuksen tiedot noudattavat lähderekisterin vastaavia tietomalliperiaatteita, eikä puuttuvia tietoja arvata. Ehdotukset tallennetaan erillisinä tiedostoina polkuun `data/source-proposals/{proposal_id}.json`. Ehdotuksen tilat ovat `pending`, `approved`, `rejected` ja `merged`; vastaanottaja validoi ehdotuksen ja duplikaatit ennen ylläpitäjän käsittelyä. Ylläpitäjän ratkaisu, ajankohta ja perustelu säilytetään. Ensimmäisessä versiossa ehdotukset käsitellään GitHubissa tiedostoina, eikä erillistä käyttöliittymää toteuteta. `propose` on suositeltu oletus; `automatic` on mahdollinen vain asetuksella ja suorittaa silti kaikki validointi- ja duplikaattitarkistukset. Hyväksytty rekisterimuutos vaikuttaa vasta myöhempiin tehtäväpyyntöihin.

Lähdekohtaiset ajohavainnot sisältävät lähteen tunnisteen, tarkistuksen tilan (`attempted` tai `not_attempted`) ja yksittäiset avausyritykset. Yritys sisältää tunnisteen, ajankohdan, pyydetyn URL-osoitteen, avauksen tuloksen (`opened` tai `failed`), epäonnistumisen syyluokan silloin kun avaus epäonnistui sekä sisällön luettavuuden (`readable`, `partial`, `unreadable` tai `not_assessed`). `not_attempted` ei ole epäonnistuminen eikä kuulu avausyritysten onnistumisprosentin nimittäjään. Avaamisen onnistuminen erotetaan sisällön luettavuudesta ja hyödyllisyydestä. Valvomo laskee tilastot alkuperäisistä havainnoista eikä luota tuottajan valmiiksi laskemiin prosentteihin. Sekä yrityskohtainen että ajokohtainen onnistumisaste esitetään otoskoon ja tarkastelujakson yhteydessä.

Tilastoinnin yksikkö on sisältökanavan avausyritys. Yleiset epäonnistumisen syyluokat ovat `timeout`, `connection_error`, `dns_error`, `tls_error`, `http_client_error`, `http_server_error`, `rate_limited`, `access_restricted`, `content_error` ja `unknown`. Tuntematonta syytä ei arvata, ja tarkempi tekninen tulos säilytetään mahdollisuuksien mukaan. Valvomon oletustarkastelujaksot ovat 30 päivää, 90 päivää ja koko tallennettu historia; tilastoja voidaan suodattaa aiheen, tehtävätyypin, lähteen ja kanavan mukaan. Näytettäviin tunnuslukuihin kuuluvat yritysten, onnistumisten ja epäonnistumisten määrät, onnistumisaste osoittajineen ja nimittäjineen, viimeisimmät onnistumiset ja epäonnistumiset, virheluokkien jakauma ja kehitys tarkastelujaksolla. Prosenttia ei näytetä ilman luotettavaa nimittäjää, ja otoskoko esitetään aina.

Toistuvan epäonnistumisen alustava nostokriteeri on vähintään viisi avausyritystä vähintään kolmessa eri ajossa ja alle 50 prosentin onnistumisaste viimeisten 30 päivän aikana. Viimeisimmät peräkkäiset epäonnistumiset voidaan näyttää erillisenä huomiona. Kriteerit ovat ylläpitäjän arviointipyynnön muodostamista varten, eivät automaattisia käyttörajoituksia tai rekisterimuutoksia. Lähdettä ei poisteta tai poisteta käytöstä tilastojen perusteella.

Lähdevalinnan tasot ovat tehtävätyypin `default_sources` ja `required_sources` sekä aiheen ja tehtävätyypin yhdistelmän `source_selection`. Pakolliset lähteet yksilöidään täsmällisinä lähde–kanava-pareina, ja niiden on löydyttävä oletuslähteistä. Aihekohtainen valinta käyttää `inherit`-, `extend`- tai `replace`-toimintatapaa. `inherit` säilyttää oletukset sellaisinaan; `extend` (oletus) säilyttää oletukset ja sallii lisäykset sekä käyttöasetusten tarkentamisen; `replace` korvaa valinnaiset oletukset aihekohtaisella listalla, mutta pakolliset lähde–kanava-parit säilyvät aina. Puuttuvat pakolliset parit lisätään `replace`-tilassa alkuperäisine oletusasetuksineen. Listajärjestys määräytyy toimintatavan mukaan ja on erillinen tärkeysarvosta. Sama lähde–kanava-pari esiintyy lopullisessa listassa vain kerran. Lähteen perustiedot, tehtäväkohtaiset käyttöasetukset ja ajokohtaiset havainnot pidetään erillään.

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

#### Skeemojen tiedostokokonaisuus ja validoinnin toteutusperiaatteet

Skeemojen ja validoinnin suunnitteluratkaisut on hyväksytty. Toteutus käyttää JSON Schema Draft 2020-12 -standardia. Skeemat sijoitetaan yhteiseen ohjelmistorepoon, kun taas instanssin varsinaiset määritykset ja aineistot pysyvät instanssirepositoriossa. Jokaisella itsenäisellä tietotyypillä on oma pääskeemansa, ja toistuvia rakenteita varten tehdään yhteisiä osaskeemoja.

Skeemojen alustava hakemistorakenne:

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

Tiedostonimet ovat englanninkielisiä, pienaakkosin ja yhdysmerkein. Skeemojen `$id`-tunnisteet ovat vakaita eivätkä riipu repositorion nimestä tai polusta. Skeemojen väliset skeemojen `$ref`-viittaukset ratkaistaan paikallisesti ohjelmistorevision sisältämästä skeemakokonaisuudesta; ajonaikaisia ulkoisia skeemahakuja ei tehdä. Hakemistorakenne ja yksittäisten skeematiedostojen tarkka sisältö toteutetaan myöhemmässä toteutusvaiheessa tämän hyväksytyn mallin mukaisesti.

Skeemakokonaisuus jaetaan neljään vastuualueeseen: (1) määritykset, (2) tehtävän käynnistys, (3) tuottajan toimitus ja (4) vastaanottajan ajohallinta. Tämä jako ohjaa skeemojen ryhmittelyä, eikä se tarkoita yhtä skeematiedostoa kutakin kokonaisuutta kohti. Jokaisella itsenäisellä tietotyypillä on oma pääskeemansa.

Yhteisiä osaskeemoja käytetään toistuville rakenteille. Niihin kuuluvat vähintään tunnisteet, Git-revisiot, aikaleimat, aikavälit, tiedosto- ja repositorioviittaukset, lähde- ja sisältökanavaviittaukset, URL-osoitteet, virhekuvaukset sekä laaduntarkistusten havaintotietueet. Osaskeemojen tarkka tiedostojako ja nimeäminen viimeistellään skeemojen toteutussuunnittelussa.

Kaikilla skeemoilla on vakaa `$id`, joka ei riipu repositorion nimestä tai tiedostopolusta, ja `$schema` ilmoittaa käytetyn JSON Schema -version. Tietoaineiston `schema_version` yksilöi sen käyttämän tietosopimuksen version. `format`-tarkistukset otetaan validointikirjastossa eksplisiittisesti käyttöön.

Tehtävätyypin määrityksen laaduntarkistukset määritellään tietueina, joissa ovat:
- `check_id`: pysyvä, tehtävätyypin sisällä yksilöllinen tunniste;
- `name`: tarkistuksen nimi;
- `description`: tarkistuksen tarkoitus ja sisältö;
- `required`: tieto siitä, kuuluuko tarkistus tehtävätyypin vaadittuun tarkistuskattavuuteen;
- `parameters`: tarkistuksen mahdolliset tehtävätyyppikohtaiset asetukset.

Tarkistuksen tunniste ei riipu sen nimestä tai kuvauksesta. Tunnistetta ei muuteta kuvauksen täsmentyessä, eikä poistettua tunnistetta oteta uudelleen käyttöön. Toimituksen `check_id` viittaa tehtävätyypin määrityksessä määriteltyyn tarkistukseen. Tarkistuksen nimi ja kuvaus säilyvät määrityksessä, eikä niitä kopioida ajokohtaiseen tulostietueeseen.

`parameters` on aina mukana oleva objekti. Asetuksettomassa tarkistuksessa se on tyhjä objekti (`{}`). Parametrien sallittuja JSON-tietotyyppejä ovat merkkijono, numero, kokonaisluku, totuusarvo, taulukko ja objekti; tarkistuskohtainen skeema määrittelee käytettävät kentät, tarkat tyypit, rajat, sallitut arvot ja pakollisuuden. Tuntemattomat parametrit hylätään. Parametrien oletusarvot määritellään tarkistuskohtaisessa skeemassa. Määritysten käsittely soveltaa skeemassa määriteltyä oletusarvoa, jos arvoa ei ole annettu; JSON Schema -skeeman `default`-annotaatio ei yksinään muuta aineistoa. Oletusarvon käyttö ei muodosta erillistä ajokohtaista tulosta. Parametrien tarkat nimet ja rakenteet määritellään tarkistuskohtaisesti.

`check_id` on yksilöllinen tehtävätyypin sisällä. Sama tunniste voi esiintyä eri tehtävätyypeissä, jos kyse on samasta käsitteellisestä tarkistuksesta. Tunniste ei riipu nimestä, kuvauksesta, parametreista tai teknisestä toteutuksesta. Yhteensopiva kuvauksen tai parametrien täsmennys ei edellytä tunnisteen vaihtamista; olennaisesti muuttunut käsitteellinen tarkoitus edellyttää uutta tunnistetta. Poistettua tunnistetta ei käytetä uudelleen. Tarkistuksella ei ole omaa versionumerokenttää: käytetty määrittely tunnistetaan tehtävätyypin määrityksen ja tehtäväpyynnön `instance_revision`-revisiotiedon avulla.

`required: true` edellyttää ajokohtaista tulostietuetta jokaisessa toimituksessa. `required: false` sallii tarkistuksen jättämisen tekemättä ilman tulostietuetta; jos valinnainen tarkistus suoritetaan, sen tulos kirjataan. Pakollinen tarkistus voi saada tuloksen `not_applicable`, kun soveltumattomuus perustellaan. Pakollisen tarkistuksen puuttuva tietue on toimituksen validointivirhe. Tarkistuksen määrittely ja parametrien vaatimukset kuuluvat tehtävätyypin määritykseen ja tarkistuskohtaiseen skeemaan; raportintuottaja ratkaisee parametrit, suorittaa tarkistukset ja kirjaa tulokset; vastaanottaja tarkistaa tulosten kattavuuden ja rakenteen muuttamatta niitä. Tarkistusten suoritusjärjestystä tai keskinäisiä riippuvuuksia ei määritellä ensimmäisessä vaiheessa.

Laaduntarkistuksen ajokohtaisen tulostietueen rakenteellinen skeemavalidointi ja tietueiden väliset toiminnalliset tarkistukset ovat erillisiä vaiheita. Rakenteellinen validointi tarkistaa tietueiden kentät, tyypit ja sallitut arvot. Toiminnallinen validointi tarkistaa muun muassa, että jokaisesta vaaditusta tarkistuksesta on ajokohtainen tietue, `passed`-tuloksen `findings` on tyhjä, `issues_found` sisältää vähintään yhden havainnon ja `not_run`-, `not_applicable`- sekä `execution_error`-tuloksilla on perustelu. Puuttuvaa tietuetta ei tulkita onnistumiseksi. Vastaanottaja tarkistaa kattavuuden ja rakenteen muuttamatta tuottajan ilmoittamia tuloksia.

Toimitusmetatietojen, kanonisen ajotietueen ja tapahtumahistorian skeemat ovat erilliset. Samoin toimituspaketin tulostilakohtaiset vaatimukset tarkistetaan toimituspaketin omilla rakenteellisilla ja toiminnallisilla tarkistuksilla. Skeemojen testaus kattaa jokaisen pääskeeman kelvolliset esimerkit sekä virheelliset tapaukset, skeemojen `$ref`-riippuvuuksien latautumisen, tuntemattomien kenttien hylkäämisen, laaduntarkistusten kirjaamissäännöt ja toimituspaketin puutteellisuuden. GitHub Actions suorittaa skeema- ja validointitestit, kun niitä koskevia tiedostoja muutetaan. Testien epäonnistuminen estää muutoksen hyväksymisen normaalissa CI-prosessissa.

Skeemakokonaisuuden päävastuut ovat:

- tehtävätyypin määrityksen skeema ja sen viittaama tehtävätyyppikohtainen asetusskeema;
- määritysprofiilin ja aihekohtaisen määrityksen skeemat;
- yhteisen lähderekisterin skeema;
- tehtäväpyynnön skeema;
- tuottajan toimitusmetatietojen skeema;
- toimituspaketin tulostilakohtaiset skeemat, vastaanottajan kanonisen ajotietueen skeema sekä append-only-tapahtumahistorian tietuetyypin skeema;
- uudelleenkäytettävät osaskeemat tunnisteille, Git-revisioille, aikaleimoille, tiedostoviittauksille, lähde- ja kanavaviittauksille sekä virhekuvauksille.

Tehtävätyypin asetusskeema määrittelee myös lopullisen `resolved_config`-rakenteen. Profiilin oma rakenne validoidaan profiilin skeemalla ja sen asetukset lisäksi valitun tehtävätyypin asetusskeemalla. Tuottajan toimittamat tulosmetatiedot ja vastaanottajan kirjaama ajonhallinta pysyvät erillisinä tietosopimuksina: toimitusmetatietojen skeema ei korvaa eikä määrittele vastaanottajan kanonista ajotietuetta.

Kaikilla skeematasoilla hylätään tuntemattomat kentät. Sulkevuus toteutetaan Draft 2020-12 -standardin mukaisesti esimerkiksi `additionalProperties: false`- tai tarvittaessa `unevaluatedProperties: false` -määrityksillä. `$ref`- ja `allOf`-rakenteiden yhteydessä varmistetaan erikseen, ettei skeemojen yhdistäminen avaa tuntemattomille kentille pääsyä.

Skeemat versioidaan semanttisesti. Yhteensopiva korjaus kasvattaa PATCH-osaa, uusi taaksepäin yhteensopiva ominaisuus MINOR-osaa ja yhteensopimaton rakenteellinen muutos MAJOR-osaa. Julkaistua skeemaversiota ei muuteta hiljaisesti yhteensopimattomaksi. Tehtäväpyynnön ja toimitusmetatietojen `schema_version`-kentät säilyvät, ja käytetty skeemakokonaisuus yksilöityy lisäksi tehtävän `software_revision`-kentän kautta.

Validointi etenee jäsennyksestä yksittäisten aineistojen skeemavalidointiin, viittausten ja revisioiden tarkistukseen, määritysten yhteensopivuuden tarkistukseen, asetusten yhdistämiseen ja lopullisen `resolved_config`-kokonaisuuden skeemavalidointiin. Tehtäväpyyntö muodostetaan vasta, kun kaikki vaaditut vaiheet onnistuvat. JSON Schema vastaa rakenteellisesta validoinnista; erillinen toiminnallinen validointi tarkistaa muun muassa viitattujen tiedostojen olemassaolon, aikaleimojen offsetien vastaavuuden IANA-aikavyöhykkeeseen, aikavälien järjestyksen ja määritysten väliset ehdot.

Validointikirjastossa otetaan `format`-tarkistukset eksplisiittisesti käyttöön. Käytetään yhtä vakiintunutta Draft 2020-12 -yhteensopivaa kirjastoa, jonka versio ja riippuvuudet kiinnitetään; omaa JSON Schema -tulkkia ei rakenneta. Skeemat eivät hae ulkoisia viittauksia verkosta.

Virheilmoituksissa yksilöidään tiedosto, kenttäpolku, virhetyyppi ja selkokielinen kuvaus. Odotettu ja havaittu arvo näytetään, kun se on mielekästä. Toisistaan riippumattomat virheet kerätään, mutta virheestä riippuvat jatkotarkistukset ohitetaan. Virhe estää tehtäväpyynnön muodostamisen; automaattisia arvauksia, korjauksia tai osittaisia määrityksiä ei tehdä.

Markdown-ohjeiden tarkistukset pidetään erillään JSON Schema -validoinnista. Niihin kuuluvat tiedoston olemassaolo oikeassa repositoriossa ja commitissa, Markdownin jäsennettävyys, otsikkohierarkia, paikallisten linkkien toimivuus sekä ohjetunnisteiden ja versioiden johdonmukaisuus.

Testaus kattaa jokaisen pääskeeman kelvollisen esimerkin sekä virheelliset tapaukset: puuttuvat kentät, väärät tyypit, tuntemattomat kentät, virheelliset tunnisteet/revisiot/aikaleimat/viittaukset, virheelliset asetukset ja kielletyt ylikirjoitukset. Lisäksi testataan koko skeemakokonaisuuden lataus, `$ref`-riippuvuuksien ratkaisu, määritysten yhdistämislogiikka ja lopullinen `resolved_config`. GitHub Actions suorittaa skeema- ja validointitestit, kun niitä koskevia tiedostoja muutetaan.

Markdown-ohjeiden tarkistukset eivät ole JSON Schema -skeemoja. Niiden erillinen tarkistus kattaa tiedoston olemassaolon oikeassa repositoriossa ja commitissa, Markdownin jäsennettävyyden, otsikkohierarkian, paikalliset linkit sekä ohjetunnisteiden ja versioiden johdonmukaisuuden.

### 2.2.3 Raportintekijän yhteinen perusprompti

Yhteinen raportintekijän perusprompti kuuluu ohjelmistorepoon ja kiinnittyy käytettyyn `software_revision`-revisioon. Tehtäväpyynnön `instructions`-taulukossa se on ensimmäisenä, ennen tehtävätyypin ohjetta, järjestettyjä profiiliohjeita ja aihekohtaista ohjetta. Jokaisella ohjeviittauksella on `repository`- ja `path`-tiedot; ohjelmistorepon ohje luetaan `software_revision`- ja instanssirepon ohjeet `instance_revision`-revisiosta.

Perusprompti määrittelee raportintekijän yleisen toimintamallin: tehtäväpyynnön ja `resolved_config`-määrityksen lukemisen, ohjeiden soveltamisjärjestyksen, lähteiden tarkistamisen, lähdeaineiston käsittelyn epäluotettavana sisältönä, epävarmuuden ja puutteiden ilmoittamisen, raportin muodostamisen sekä toimituspaketin vaatimukset. Se kieltää tehtäväpyynnön tunnisteiden tai asetusten muuttamisen ja puuttuvien tietojen keksimisen. Lähteissä olevia ohjeita käsitellään lähdesisältönä, ei raportintekijän järjestelmäohjeina.

Perusprompti sisältää myös vaatimuksen raportoida lähdekohtaiset avausyritykset ja niiden tulokset erillään sisällön laadusta tai relevanssista. Raportintekijä käyttää vain tehtäväpyynnössä yksilöityjä muuttumattomia ohjeversioita. Promptin tarkka teksti ja mahdollinen tuottajakohtainen sovitus suunnitellaan myöhemmin; tämä arkkitehtuuripäätös ei vielä luo promptitiedostoa eikä muuta nykyisiä automaatioita.

### 2.3 Toimitustapa: ChatGPT:n ajastettu tehtävä ja Codex Connector

Hakemistojen nimet kirjoitetaan dokumentoiduissa repositorio- ja polkuesimerkeissä englanniksi. Sama kieli koskee sekä ohjelmistorepositoriota että instanssirepositoriota; suomenkieliset selitteet ja tiedostojen sisältö eivät vaikuta hakemistojen nimeämiseen. Esimerkiksi `docs/`, `scripts/`, `schemas/`, `data/`, `runs/`, `deliveries/`, `prompts/` ja `archive/` noudattavat tätä käytäntöä. Uusia hakemistoja ei nimetä suomeksi samaan rakenteeseen.

Ensimmäisen vaiheen instanssirepositorio on julkinen. RSS-syötteet julkaistaan GitHub Pagesin kautta. Koko instanssirepositorio, sen haarat ja Git-historia ovat julkisia, joten kaikki sinne toimitettava aineisto käsitellään julkisena. Repositorioon tai toimituksiin ei saa sisällyttää salasanoja, API-avaimia, käyttöoikeustunnisteita, yksityisiä tietoja tai muuta luottamuksellista sisältöä.

Ensimmäisen version ainoa raportintuottaja on ChatGPT:n ajastettu tehtävä. Se toimittaa kokonaisen toimituspaketin Git pushina GitHubiin Codex Connector -yhteyden kautta. Käytännön testissä ajastettu tehtävä loi testitiedoston instanssirepositorion erilliseen haaraan; testissä `main`-haara ei muuttunut. Testi osoittaa, että toimitus toimii tässä käyttöympäristössä. Tuotantokäyttöönotossa on silti varmennettava yhteyden oikeudet, vastaanoton työnkulku ja julkaisuhaaran suojaus.

Toimitukset tehdään erilliseen vastaanottohaaraan `raportit-inbox`. Toimituspaketin polku on `deliveries/{run_id}/{delivery_id}/`, ja paketti sisältää `metadata.json`-tiedoston sekä tehtävätyypin edellyttämät sisältötiedostot, kuten `item.xml`. Julkaisu tapahtuu erikseen `main`-haaraan. Tuottaja ei kirjoita suoraan julkaisuhaaraan eikä julkaistaviin RSS-tiedostoihin.

Codex Connector on ChatGPT:n ja GitHubin välinen yhteys, ei instanssirepoon asennettava GitHub App. Ensimmäisessä versiossa ei käytetä erillistä vastaanotto-GitHub Appia. Aiempi vastaanotto-App on poistettu; sen luomista uudelleen voidaan harkita myöhemmin, jos käyttöoikeuksien eriyttämiseen syntyy tarve.

Codex Connectorin GitHub-oikeus ei rajaudu automaattisesti yksittäiseen haaraan. Vastaanottohaara on toimitusten käsittelyraja, ei käyttöoikeusraja. Siksi `main`-julkaisuhaaran suojaus on toteutettava ja varmennettava erillisillä haara- tai ruleset-asetuksilla sekä työnkulun tarkistuksilla. Käyttöönotossa on varmistettava, ettei raportintuottajan käyttämä yhteys voi ohittaa julkaisuhaaran suojauksia. Dokumentaatio ei oleta suojauksen olevan käytössä ennen kuin se on teknisesti asetettu ja tarkistettu.

- GitHub Actions käynnistää toimituksen käsittelyn vastaanottohaaraan tehdyn pushin perusteella.
- Actions tarkistaa paketin ennen kuin mitään julkaistaan tai tallennetaan hyväksyttyihin tuotantotietoihin.
- Vain validoitu ja hyväksytty sisältö siirretään julkaisuhaaraan; virheellinen toimitus ei muuta julkaistuja RSS-syötteitä.
- Git pushin onnistuminen vahvistaa vain toimituksen siirtymisen vastaanottohaaraan; se ei merkitse toimituksen hyväksymistä tai julkaisua.
- Vastaanoton ja validoinnin tulokset kirjataan GitHub Actions -työnkulun sekä vastaanottajan ajotietueen ja tapahtumahistorian avulla. Erillistä HTTP-kuittausrajapintaa ei tarvita ensimmäisessä versiossa.
- Vastaanottaja tarkistaa toimituksen kuulumisen olemassa olevaan ajoon, tunnisteiden johdonmukaisuuden, toimituspaketin rakenteen ja sisällön sekä eheyden. Vastaanottaja muodostaa `attempt_id`-tunnisteen, laskee SHA-256-tiivisteen ja säilyttää alkuperäisen toimituspaketin. Aiemmin hyväksytyt kaksois- ja ristiriitasäännöt koskevat myös GitHubin kautta tehtyjä uudelleenlähetyksiä.
- Codex Connectorin käyttöoikeuksia tai tunnistetietoja ei kopioida raportintuottajan ohjeisiin tai toimituspaketteihin.

#### Vastaanottoprosessin hyväksytyt toimintaperiaatteet

**Validoinnin järjestys ja keskeyttäminen.** Seitsemän validointivaihetta suoritetaan määritellyssä järjestyksessä. Samassa vaiheessa voidaan kirjata useita riippumattomia virheitä, mutta seuraavaan vaiheeseen ei siirrytä, jos sen turvalliset tai loogiset edellytykset eivät täyty. Turvattomasti käsiteltävä pakettirakenne keskeyttää käsittelyn. Toimitettua aineistoa ei korjata eikä muuteta.

**Tunnisteet, revisiot ja skeemat.** `run_id`-, `delivery_id`- ja tehtävätunnisteiden on vastattava toimituspolkua, metatietoja ja vastaanottajan ajotietoja. Skeemaversion on oltava tuettu; tuntematonta tai puuttuvaa versiota ei arvata. `software_revision`- ja `instance_revision`-arvojen on vastattava ajon käynnistyksessä kiinnitettyjä revisioita, ja tehtävätyypin määritysten on oltava saman ajon käyttämää revisiokokonaisuutta. Ristiriita estää hyväksymisen.

**Tiedostoluettelo ja eheys.** `metadata.json` luettelee kaikki toimitetut sisältötiedostot mutta ei itseään, jotta vältetään itseensä kohdistuva tiiviste- ja kehäsuhde. Vastaanottaja tarkistaa roolit ja polut, pakolliset ja kielletyt tiedostot, puuttuvat ja odottamattomat tiedostot, kaksoisviittaukset, tiedostojen olemassaolon, koon ja SHA-256-tiivisteen. Tiedostomäärän ja -koon rajat tarkistetaan ennen sisällön käsittelyä.

**XML-, RSS- ja HTML-turvallisuus.** XML-parseri ei käsittele DTD:tä tai ulkoisia entiteettejä eikä hae ulkoisia resursseja. `item.xml` validoidaan yhden `<item>`-elementin toimitussopimusta, järjestystä, pakollisuutta, attribuutteja ja item-elementin `content`-nimiavaruutta vasten. HTML tarkistetaan sallitun elementti- ja attribuuttiluettelon sekä linkkien osoitemuotojen perusteella. Kiellettyä sisältöä ei poisteta hiljaisesti eikä sisältöä korjata automaattisesti; toimitus hylätään yksilöidyllä virheellä.

**Keskinäiset viittaukset.** Tiedostoviittausten on osoitettava olemassa oleviin luetteloituihin tiedostoihin. Roolien, polkujen, tunnisteiden ja ajotietojen on oltava johdonmukaisia. GUIDin on oltava yksilöllinen julkaisu- ja historiatiedoissa. Korjaus- tai täydennysitemin alkuperäisen GUID-viittauksen on osoitettava olemassa olevaan julkaisuun ja suhteen tyypin oltava sallittu.

**Virheet ja hyväksymisen raja.** Rakenteelliset, tunniste-, revisio-, skeema-, tiedosto-, eheys- ja sisältövirheet ovat pysyviä ja johtavat hylkäykseen. Tilapäinen suoritusympäristö- tai GitHub-virhe voi johtaa rajattuun uudelleenyritykseen; määrät ja viiveet ratkaistaan kohdassa 9.7. Virheestä tallennetaan koneellinen luokka, ihmiselle luettava kuvaus sekä mahdollisuuksien mukaan tiedosto tai polku. Varoitukset eivät ohita pakollisia tarkistuksia. Hyväksyntä edellyttää kaikkien soveltuvien pakollisten tarkistusten läpäisyä eikä itsessään tarkoita julkaisua. Vastaanottajan virhe ei muuta tuottajan tulostilaa.

Vastaanottoprosessin toiminnalliset periaatteet on hyväksytty. Vastaanotto käsittelee vain `raportit-inbox`-haaran toimituksia polussa `deliveries/{run_id}/{delivery_id}/`. Jokainen toimitus käsitellään itsenäisesti, alkuperäistä pakettia muuttamatta. Vastaanotto, hyväksyntä ja julkaisu ovat erillisiä tapahtumia, eikä vastaanottovirhe estä muiden toimitusten käsittelyä.

Vastaanottaja varmistaa, että toimituksen `run_id` ja `delivery_id` vastaavat polkua ja metatietoja, ajo on olemassa ja ajo liittyy tunnettuun tehtävään. Tehtävän, ajon ja toimituksen tunnisteiden sekä aikaleimojen on oltava johdonmukaisia. Tuntemattomaan ajoon tai tehtävään viittaava toimitus hylätään; puuttuvaa ajoa ei luoda toimituksen perusteella.

Paketti sisältää `metadata.json`-tiedoston sekä tehtävätyypin edellyttämät sisältötiedostot. `item.xml` vaaditaan vain tehtävätyypin ja tuottajan tulostilan niin edellyttäessä. Tiedostoroolit ja tulostilakohtaiset vaatimukset tulevat tehtävätyypin määrityksestä. Odottamattomat tiedostot hylätään. Polut ovat paketin sisäisiä: absoluuttiset polut, `..`-siirtymät, symboliset linkit ja paketin ulkopuolelle osoittavat viittaukset eivät ole sallittuja. Ensimmäiseen versioon ei rakenneta yleistä liite- tai kuvakäsittelyä.

Toimituspaketin tiedostot yksilöidään toimituspaketin sisäisillä poluilla ja `metadata.json`-tiedoston tiedostoluettelolla. Jokaisella tiedostolla on yksi tiedostoluettelon tietue ja yksi tehtävätyypin mukainen rooli; samaa polkua ei saa ilmoittaa ristiriitaisilla rooleilla. Vastaanottaja tarkistaa tiedostojen roolit ja polut sekä ilmoitetun koon ja SHA-256-tiivisteen. Paketin ulkopuolelle osoittavia viittauksia ei sallita.

Kun tehtävätyyppi tuottaa julkaistavan raportin, raportti toimitetaan `item.xml`-tiedostossa. Se sisältää yhden RSS-itemin, jonka `<content:encoded>`-elementissä on koko raportin HTML-sisältö. Erillistä HTML-raporttitiedostoa ei toimiteta ensimmäisessä versiossa. `item.xml` vaaditaan vain tehtävätyypin ja tuottajan tulostilan sitä edellyttäessä. Muut sisältötiedostot sallitaan vain tehtävätyypin määrittelemien tiedostoroolien perusteella.

Korjaus tai olennainen täydennys toimitetaan uutena RSS-iteminä, jolla on oma vastaanottajan luoma UUIDv4-GUID. Uuden itemin toimitusmetatiedot yksilöivät alkuperäisen itemin GUIDin ja suhteen tyypin (korjaus tai täydennys); raporttisisältö kertoo yhteyden lukijalle tarpeellisessa määrin. Alkuperäistä itemiä, raporttia tai toimituspakettia ei muuteta. Metatietojen täsmälliset kenttänimet ratkaistaan skeematyössä.

Metatiedot validoidaan skeemaa vasten. Tarkistukset kattavat pakolliset tiedot, tietotyypit, sallitut arvot, skeemaversion ja tunnisteiden vastaavuuden. Tuntematonta skeemaversiota ei tulkita arvaamalla. Jo hyväksyttyä kuuden tietoryhmän toimitusmetatietomallia ei muuteta tällä päätöksellä. Sisältötiedostot validoidaan erillään metatiedoista niiden luettavuuden, koodauksen, syntaksin, tehtävätyypin mukaisen rakenteen, pakollisten elementtien ja keskinäisten viittausten osalta. RSS-itemin toimitustiedosto sisältää täsmälleen yhden `<item>`-elementin eikä kokonaista RSS-syötettä. Itemissä ei käytetä `<link>`-elementtiä; lähteet linkitetään raportin HTML-sisällössä lähteistettävän tiedon yhteydessä ja/tai raportin lopun lähdeluettelossa. RSS-itemin elementit ovat täsmälleen seuraavat tässä järjestyksessä: pakollinen `<title>`, pakollinen `<guid isPermaLink="false">`, pakollinen UTC-aikainen `<pubDate>`, valinnainen lyhyt `<description>` ja pakollinen `<content:encoded>`. Muita RSS-elementtejä, kuten `<author>`, `<category>`, `<comments>`, `<enclosure>` tai `<source>`, ei käytetä. GUIDin ainoa sallittu attribuutti on `isPermaLink="false"`; muille elementeille ei lisätä attribuutteja. `content`-nimiavaruus määritellään item-elementissä muodossa `xmlns:content="http://purl.org/rss/1.0/modules/content/"`, koska tiedosto ei sisällä RSS-kanavan ympäröivää elementtiä. `<guid>` yksilöi itemin eikä toimi linkkinä raporttisivulle. Koko raportti toimitetaan RSS Content -laajennuksen `<content:encoded>`-elementissä HTML-muodossa. `<description>` on vapaaehtoinen lyhyt tiivistelmä eikä siihen kopioida koko raporttia. Raportin HTML-sisällöllä on yhteinen perusrakenne, mutta varsinainen sisältö ja sen jäsentely voivat vaihdella aiheen ja tehtävätyypin mukaan. `<pubDate>` esitetään UTC-ajassa RSS:n päivämäärämuodon mukaisesti; käyttöliittymä voi muuntaa ajan paikalliseen aikavyöhykkeeseen. GUIDin muodostustapa ja säilytys on päätetty: vastaanottaja luo satunnaisen UUIDv4-tunnisteen ja tallentaa sen kanoniseen ajotietueeseen atomisesti RSS-itemin kanssa. HTML:n sallittu tekninen sisältö ja validointikäytäntö on määritelty tässä kohdassa; raportin yhteinen rakenne ja otsikkohierarkian käyttö täsmennetään kohdassa 9.3.

XML ja HTML muodostetaan turvallisesti erillisinä rakenteina. XML tuotetaan XML-kirjastolla; XML-tekstisolmujen sisältö escapetaan kirjaston normaalilla tavalla. `<content:encoded>`-elementin HTML-sisältö sarjoitetaan CDATA-osioon. Jos HTML sisältää merkkijonon `]]>`, CDATA-osio jaetaan XML:n mukaisesti turvallisesti niin, että alkuperäinen sisältö säilyy muuttumattomana.

HTML:n sallittuun elementtijoukkoon kuuluvat otsikot `h1`–`h6`; tekstielementit `p`, `br`, `strong`, `em` ja `blockquote`; listaelementit `ul`, `ol` ja `li`; linkkielementti `a`; sekä rakenteelliset elementit `article`, `section`, `figure`, `figcaption` ja `time`. Kuvien `img`-elementtiä ei sallita ensimmäisessä versiossa, vaan kuvien käyttö rajataan jatkokehitykseen. Sallitut attribuutit ovat `a`-elementillä `href` ja `title` sekä `time`-elementillä `datetime`. Muita attribuutteja ei sallita. JavaScript, tapahtumankäsittelijät, lomakkeet, upotetut objektit, tyylitiedostot ja CSS-tyylimäärittelyt ovat kiellettyjä.

HTML validoidaan ennen toimituksen hyväksymistä. Virheellistä tai sallittujen elementtien ja attribuuttien vastaista HTML:ää ei korjata automaattisesti, vaan toimitus hylätään yksilöidyllä virheellä. Validointi tarkistaa lisäksi linkkien osoitemuodot. HTML:n tarkka yhteinen raporttirakenne, otsikkohierarkian käyttö, saavutettavuus ja aihekohtaisen vaihtelun rajat määritellään erikseen kohdassa 9.3.

Vastaanottaja laskee jokaisen toimitetun sisältötiedoston koon ja SHA-256-tiivisteen ja vertaa niitä metatietoihin. Puuttuva tiedosto, väärä koko tai tiiviste sekä määriteltyjen koko- tai määrärajojen ylitys estävät hyväksymisen. Tiiviste todentaa eheyden, ei lähettäjän henkilöllisyyttä. Vastaanottaja ei suorita toimituspaketin koodia.

Saman `delivery_id`-tunnisteen ja saman sisällön uusintatoimitus käsitellään idempotentisti ilman uutta julkaisua tai päällekkäisiä sivuvaikutuksia. Saman tunnisteen eri sisältö hylätään ristiriitaisena. Useat toimitukset samasta ajosta sallitaan vain toimitussopimuksen rajoissa. RSS-itemin GUIDin toistuminen tarkistetaan julkaisu- ja historiatiedoista. Uudelleenyritykset yksilöidään käsittely-yrityksinä.

Vastaanoton tiloissa erotetaan vastaanotettu, tarkistuksessa, hyväksytty, julkaisukelpoinen ja julkaistu sekä hylätty ja tilapäistä uudelleenyritystä odottava. Pysyvä rakenteellinen tai sisältövirhe hylätään; tilapäinen tekninen virhe voi johtaa rajattuun uudelleenyritykseen. Uudelleenyritysten tarkat määrät ja viiveet määritellään teknisessä toteutuksessa. Virheestä tallennetaan koneellinen virheluokka ja ihmiselle luettava kuvaus.

Kirjanpito sisältää vähintään ajo-, toimitus- ja tehtävätunnisteet, vastaanottoajan, tiedostoluettelon ja tiivisteet, käytetyn skeemaversion, validointitulokset, lopputilan sekä virhekoodit ja kuvaukset. Julkaisun yhteydessä kirjataan varmennettu julkaisutulos. Alkuperäinen toimituspaketti säilytetään muuttumattomana.

Vastaanoton validointi ja julkaisu toteutetaan erillisinä GitHub Actions -työnkulkuvastuina. Vastaanotto käynnistyy vastaanottohaaran toimitusmuutoksista, validoi ja kirjaa tuloksen. Julkaisu käsittelee vain vastaanottajan hyväksymän toimituksen, tarkistaa hyväksynnän ja siirtää sisällön erikseen `main`-haaraan. Julkaisun jälkeen varmennetaan julkaistun sisällön ja RSS/XML:n kelvollisuus. `main`-haaran suojaus on varmennettava niin, ettei Codex Connector voi ohittaa sitä.

Turvallisuusperiaatteet edellyttävät, että toimituspakettia käsitellään epäluotettavana datana, polut rajataan paketin sisälle, tiedostojen määrää ja kokoa rajoitetaan, koodia ei suoriteta ja vastaanottoprosessille annetaan vain välttämättömät oikeudet. Ensimmäiseen versioon eivät kuulu erillinen HTTPS-vastaanottopalvelu, vastaanotto-GitHub App, lähettäjän erillinen tunnistaminen, useiden raportintuottajien samanaikainen käsittely, yleinen manuaalinen hyväksymisjärjestelmä, automaattinen korjaaminen tai yleinen liitetiedostojen käsittely.


Erillistä HTTPS-vastaanottopalvelua tai käyttäjäkohtaista tunnistamista ei toteuteta ensimmäisessä versiossa. Laajemmat tunnistus- ja integraatiomallit voidaan arvioida myöhemmissä versioissa.

Esimerkkirakenne vastaanottohaarassa:

```text
raportit-inbox/
  deliveries/
    <run_id>/
      <delivery_id>/
        metadata.json
        item.xml
```

Toimituspaketti sisältää:

- `metadata.json`: pakollinen kaikissa tulostiloissa. Se sisältää vähintään sopimusversion, ajotunnisteen, aiheen tunnisteen, seurantatyypin, seuranta-aikavälin ja tulostilan sekä kyseisen tulostilan edellyttämät lisätiedot;
- `item.xml`: toimitetaan, kun tehtävätyyppi ja tuottajan tulostila edellyttävät julkaistavaa raporttia. `success`-tilassa validoitu raportti julkaistaan; `partial`-tilassa validoitu osittainen raportti julkaistaan, ja itemissä kerrotaan selvästi seurannan puutteellisuudesta sekä sen syistä. `no_report`- ja `failed`-tiloissa raporttia ei toimiteta.

Tarkka skeema, tiedostonimien säännöt ja toimituksen täydellisyyskriteerit määritellään erikseen. Metatietojen sisällölliset tietoryhmät on määritelty kohdassa 2.6.1; kenttäkohtainen rakenne täsmennetään erillisessä tietomallityössä. `no_report`- ja `failed`-tulosten toimitus ei saa edellyttää olematonta RSS-item-tiedostoa.


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

#### 2.4.2 Raportin HTML-perusrakenne

Jokainen RSS-itemin raportti toimitetaan yhtenä `<article>`-elementtinä. Yhteinen looginen perusrakenne sisältää yhden `<h1>`-otsikon, raportin seuranta-aikavälin selkokielisen esityksen raportin alussa, varsinaisen sisällön loogisina `<section>`-osioina sekä lähteet havaintojen yhteydessä ja/tai erillisessä lähdeosiossa. Erillinen lopun lähdeluettelo ei ole pakollinen, mutta jokaisen raportoitavan väitteen lähteet on esitettävä siten, että niiden yhteys havaintoon on tunnistettavissa.

Otsikkohierarkiassa käytetään yhtä `<h1>`-otsikkoa, pääosioissa `<h2>`-otsikoita ja alaosioissa tarvittaessa tasoja `<h3>`–`<h6>`. Otsikkotasoja ei hypitä ilman rakenteellista perustetta, eikä niitä valita ulkoasun perusteella. RSS-itemin `<title>` ja HTML:n `<h1>` saavat olla samat, mutta eivät ole pakotetusti identtiset; RSS-otsikko voi olla lyhyempi ja HTML-otsikko kuvailevampi.

Seuranta-aikaväli on jokaisessa raportissa pakollinen ja esitetään yksiselitteisesti raportin alussa. Tarkat alku- ja loppuhetket voidaan merkitä `<time datetime="...">`-elementeillä. Lukijalle tarpeettomia sisäisiä tunnisteita tai ajotietoja ei näytetä.

Varsinaisen raportin seuranta rajautuu tehtäväpyynnön ilmoittamaan aikaväliin. Raporttiin voidaan kuitenkin sisällyttää erillinen ja selvästi nimetty täydennysosio merkittäville uutisille tai havainnoille aikavälin ulkopuolelta, myös edelliseltä seurantajaksolta, jos olennainen tieto on jäänyt aiemmasta raportista puuttumaan. Täydennyksen tulee olla aiheen kannalta merkittävä ja lukijalle aidosti hyödyllinen; sitä ei käytetä tavalliseen vanhojen uutisten kierrättämiseen. Täydennyksessä ilmoitetaan tiedon todellinen ajankohta tai ajanjakso ja selitetään, että kyse on aikavälin ulkopuolisesta tai aiempaa raporttia täydentävästä tiedosta. Mahdolliseen aiempaan raporttiin viitataan mahdollisuuksien mukaan. Täydennys ei muuta varsinaista seuranta-aikaväliä eikä saa antaa ymmärtää, että uutinen olisi tapahtunut nykyisellä seurantajaksolla. Aiemmin julkaistua itemiä ei muuteta; olennainen täydennys julkaistaan uuden raportin osana tai erillisenä korjaus-/täydennysiteminä.

Lähdelinkkien tekstien tulee olla ymmärrettäviä myös asiayhteydestä erotettuina. Lähteen ja sitä tukevan havainnon yhteys on voitava tunnistaa, eikä samaa lähdettä tarvitse linkittää kahteen kertaan, jos yhteys on muuten selvä.

Saavutettavuuden perustana ovat johdonmukainen otsikkohierarkia, ymmärrettävät kappaleet ja osiot, oikeat listaelementit, kuvaavat linkkitekstit sekä sisällön ymmärrettävyys ilman visuaalista muotoilua. Päivämäärien koneellista luettavuutta tuetaan `<time>`-elementillä, kun se on käytössä. WCAG 2.2 AAA on tavoitetaso, mutta vaatimustenmukaisuutta ei väitetä ilman testausta.

Yhteinen rakenne ei pakota eri seurantatyyppejä samanlaisiin sisältöosioihin. Uutis-, tapahtuma-, elokuva- ja henkilöseurannat voivat ryhmitellä sisältönsä omien tarpeidensa mukaan. Osioiden nimet, määrä ja järjestys saavat vaihdella; yhteisiä ovat perusrakenne, aikavälin ilmoittaminen, otsikkohierarkia, lähteiden jäljitettävyys ja mahdollisten täydennysten selkeä erottaminen.

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

Tallennusmuoto ja hakemistorakenne noudattavat kohdassa 2.6.1 hyväksyttyä periaateratkaisua: ajon tiedot jaetaan tuottajan toimitusmetatietoihin, vastaanottajan kanoniseen ajotietueeseen ja vastaanottajan append-only-tapahtumahistoriaan. Ehdotettu hakemistorakenne on `runs/{run_id}/`; tarkat tietosisällöt ja viittaukset täsmennetään myöhemmin. Tavoitteena on yksi kanoninen ajohistoria, ei rinnakkaisia tietovarastoja. Julkisen tallennuksen soveltuvuutta arvioidaan uudelleen, jos tietosisältö tai käyttöoikeustarpeet muuttuvat.

#### 2.6.1 Kanoninen ajotietue, toimitusmetatiedot ja tapahtumahistoria

Ajon tiedot jaetaan kolmeen erilliseen, toisiinsa viitattuun tietokokonaisuuteen:

1. **Tuottajan toimitusmetatiedot:** raportintuottajan omistama `metadata.json` toimituspaketissa. Se sisältää tuottajan ilmoittaman tuloksen ja siihen liittyvät tiedot.
2. **Kanoninen ajotietue:** vastaanottajan omistama ajon nykytilan ja käsittelyn yhteenveto. Se viittaa hyväksyttyyn toimitukseen ja julkaisuun eikä tarpeettomasti kopioi kaikkia tuottajan toimitusmetatietojen kenttiä.
3. **Ajon tapahtumahistoria:** vastaanottajan omistama, loogisesti append-only-tietokokonaisuus, johon käsittelyvaiheet ja havainnot lisätään aikajärjestyksessä. Aiemmat tapahtumat säilyvät muuttumattomina.

Tietokokonaisuudet liittyvät samaan ajoon `run_id`-tunnisteella. Toimitus- ja käsittely-yritystunnisteita käytetään niiden aiemmin hyväksyttyjen vastuiden mukaisesti. Tuottajan ilmoittama tulostila ja vastaanottajan muodostama ajon lopputila pysyvät erillisinä tietoina, eikä vastaanottaja täydennä puuttuvaa tuottajan tulosta omilla havainnoillaan.

Tuottajan metadata.json-sisältö jäsennetään kuuteen tietoryhmään:

- **Tunnisteet ja versiot:** ajon ja toimituksen tunnisteet, tietosopimuksen versio sekä ohjelmisto- ja instanssirevisiot.
- **Tehtävän kuvaus:** aihe, tehtävätyyppi ja seuranta-aikaväli.
- **Tuottajan tulos:** tuottajan ilmoittama tulostila ja raportin tuottamiseen liittyvät tiedot.
- **Lähdetarkistukset:** käytetyt lähteet ja sisältökanavat, tarkistusyritykset ja niiden tulokset.

Lähdetarkistusten tietoryhmän alustava rakenne koostuu kolmesta osasta: ajossa käytetyistä lähteistä, eksplisiittisesti valituista sisältökanavista sekä kanavakohtaisista tarkistusyrityksistä tuloksineen. Rekisterin ulkopuoliset lähteet kuvataan toimitusmetatiedoissa erillisinä toimituskohtaisina lähteinä, eikä niitä merkitä rekisteriin kuuluviksi. Tarkistusyrityksestä tallennetaan vähintään ajankohta, tulos, tieto uuden tai tehtävän kannalta relevantin sisällön löytymisestä, saatavilla oleva tekninen tulos (esimerkiksi HTTP-tilakoodi) sekä virhe- ja huomiotiedot. Teknisen tarkistuksen onnistuminen erotetaan sisällöllisestä tuloksesta: onnistunut tarkistus ilman uutta sisältöä ei ole epäonnistuminen. Tarkka kenttärakenne ja sallitut tulosarvot täsmennetään erikseen. Tämä ei muuta lähderekisterin pysyvien tietojen ja ajohistorian toteutuneiden tarkistustulosten erottelua.
- **Havainnot ja laadunvarmistus:** raportoitavien havaintojen yhteenveto ja laaduntarkistuksen tulokset.
- **Tuottajan tiedot:** valinnaiset tiedot käytetystä raportintuottajasta.

Tuottajan tietojen perusrakenne on valinnainen `producer`-objekti. Jos objekti toimitetaan, `producer_type` on pakollinen ja sen arvot ovat `human`, `ai`, `software` tai `other`. Valinnaiset kentät ovat `producer_id` (pysyvä tuottajatunniste), `name` (ihmiselle luettava nimi) ja `version` (käytetyn ohjelmiston tai mallin versio). Esimerkkirakenne:

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

Ryhmään ei tallenneta salasanoja, käyttöoikeustunnuksia, henkilötietoja tai muita salaisuuksia.

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

Ryhmittely kuvaa metatietojen sisällölliset vastuualueet. Se ei vielä määritä kaikkia yksittäisiä kenttiä, niiden nimiä, tyyppejä tai pakollisuutta. Kohdassa 2.3 kuvatut jo hyväksytyt metatietojen vähimmäistiedot säilyvät lähtökohtana, ja niiden suhde ryhmiin täsmennetään kenttätason suunnittelussa. Vastaanottajan vastaanotto-, validointi-, julkaisu- ja käsittelytilat eivät kuulu tuottajan metatietoihin.

Viides tietoryhmä, **Havainnot ja laadunvarmistus**, koostuu kahdesta osasta:

1. **Raportoitavat havainnot:** raportin sisältämien havaintojen yhteenveto. Yhteenvetoon voi kuulua havaintojen lukumäärä, tehtävätyypin kannalta tarpeellinen luokittelu tai ryhmittely sekä olennaiset rajaukset, epävarmuudet ja kattavuuspuutteet. Jos raportoitavia havaintoja ei ole, tämä voidaan ilmaista yhteenvedossa. Varsinaista raporttitekstiä tai neljännen tietoryhmän lähde- ja tarkistusyritystietoja ei kopioida tähän.
2. **Laadunvarmistus:** raportintuottajan suorittamien laaduntarkistusten tulokset. Tarkistuskohteita voivat olla lähdeviitteiden ja väitteiden vastaavuus, havaintojen jäljitettävyys, ristiriitaisten tietojen käsittely, epävarmuuden ilmaiseminen, duplikaattien hallinta, seuranta-aikavälin noudattaminen sekä raportin rakenne ja luettavuus. Metatiedoissa kuvataan tehdyt tarkistukset ja niiden tulokset sekä havaitut puutteet ja mahdollisesti tekemättä jääneet pakolliset tarkistukset.

Tehtävätyypin määritys määrittelee kyseisessä tehtävässä vaadittavat laaduntarkistukset; kaikille tehtävätyypeille yhteistä pakollista tarkistusjoukkoa ei oleteta. Jokaisesta määritellystä tarkistuksesta toimitetaan oma ajokohtainen tietue, joka viittaa määrityksen tarkistukseen pysyvällä `check_id`-tunnisteella. Tarkistuksen nimi ja kuvaus säilyvät tehtävätyypin määrityksessä.

Tarkistustietue sisältää kentät `check_id`, `result`, `checked_at`, `findings`, `notes` ja `reason`. `checked_at` ilmoitetaan tehtäväpyynnön `resolved_config.timezone`-asetuksen mukaisena paikallisaikana ISO 8601 -muodossa numeerisella UTC-offsetilla. `findings` on havaintotaulukko; kukin havainto sisältää `description`- ja `severity`-kentät sekä valinnaisen `location`-kentän. `notes` on valinnainen ja `reason` sisältää perustelun, kun tarkistusta ei suoritettu, se ei soveltunut tai sen suoritus epäonnistui.

`result`-kentän sallitut arvot ovat `passed`, `issues_found`, `not_run`, `not_applicable` ja `execution_error`. `passed` edellyttää tyhjää havaintotaulukkoa ja `issues_found` vähintään yhtä havaintoa. `not_run` ja `not_applicable` erotetaan toisistaan; molemmat kirjataan perusteluineen. `execution_error` tarkoittaa, että suoritus aloitettiin mutta se ei valmistunut. Se kuvaa tarkistuksen suoritusongelmaa, ei sellaisenaan raportin laatupuutetta. `checked_at` kirjataan jokaisessa tilanteessa, myös kun tarkistuksen suorittamatta jääminen tai soveltumattomuus todetaan.

Havaintojen `severity`-arvot ovat `critical`, `major`, `minor` ja `info`. Ne kuvaavat vastaavasti keskeistä luotettavuutta tai käyttökelpoisuutta vaarantavaa puutetta, merkittävää sisältöön tai oikeellisuuteen vaikuttavaa puutetta, rajallista vähäistä vaikutusta sekä hyödyllistä huomiota, joka ei ole varsinainen virhe. Yleistä automaattista hyväksymisrajaa ei aseteta vakavuusluokkien perusteella.

Toimitusmetatietoihin tallennetaan vain kunkin tarkistuksen lopullinen ajokohtainen tulos, ei kaikkia sisäisiä uusintayrityksiä; olennaiset uusintayritykset voidaan kuvata `notes`-kentässä. Jokaisesta vaaditusta tarkistuksesta on oma tietue. Puuttuvaa tietuetta ei tulkita onnistumiseksi. Vastaanottaja vertaa toimitettuja tietueita tehtävätyypin määrityksen vaadittuihin tarkistuksiin ja tarkistaa tietueiden rakenteen. Vastaanottaja ei muuta tuottajan tuloksia eikä päättele puuttuvasta tietueesta onnistumista. Tuottajan laadunvarmistus ei korvaa vastaanottajan toimituspaketin validointia.

Vastuut ovat erilliset: tehtävätyypin määritys kertoo, mitä tarkistuksia vaaditaan ja mitä ne tarkoittavat; raportintuottaja suorittaa tarkistukset ja ilmoittaa tulokset; toimitusmetatiedot sisältävät ajokohtaiset tulokset ja havainnot; vastaanottaja tarkistaa kattavuuden ja rakenteellisen kelvollisuuden. Tuottajan tulostila kuuluu kolmanteen tietoryhmään eikä sitä toisteta tässä. Laadunvarmistuksen tulos on erillinen: onnistuneesti tuotetussa raportissa voi olla havaittuja laatupuutteita, ja osittainen raportti voi läpäistä kaikki sille soveltuvat tarkistukset.

Ehdotettu tiedostorakenne instanssirepositoriossa:

```text
runs/
  {run_id}/
    run.json
    events.jsonl
    deliveries/
      {delivery_id}/
        metadata.json
```

`run.json` sisältää kanonisen ajotietueen, `events.jsonl` tapahtumahistorian ja toimituskohtainen `metadata.json` tuottajan toimittamat metatiedot. RSS-item säilyy omassa RSS-syötetiedostossaan. Rakenne on hyväksytty tallennuksen periaatetasolla; tiedostojen tarkat kentät, tapahtumatyypit, viittausmuodot ja tekniset validointisäännöt täsmennetään myöhemmin ennen skeemojen viimeistelyä.

RSS-julkaisu, kanonisen ajotietueen päivitys ja tarvittavat uudet tapahtumat tallennetaan samaan atomiseen Git-commitiin. Toimitusmetatiedot säilyvät erillisenä tuottajan toimittamana aineistona, ja niiden vastaanotto/hyväksyntä kirjataan vastaanottajan ajotietueeseen ja tapahtumahistoriaan.

#### 2.6.1.1 Vastaanottajan ajotietueen ja tapahtumahistorian tietomalli

`run.json` on vastaanottajan ylläpitämä ajon nykytilan yhteenveto. Sen tietoryhmät ovat:

- ajon tunnisteet: `run_id`, `topic_id` ja `task_type`;
- ohjelmisto- ja instanssirevisiot;
- tehtävän ajankohdat ja `period`;
- vastaanottajan nykyinen käsittely- ja lopputila;
- hyväksyttyyn toimitukseen ja sen metadataan viittaaminen;
- viimeisin validointitulos ja mahdolliset virheet;
- julkaisun tila ja RSS-itemin viittaus;
- tietueen luonti- ja viimeisin varmennettu päivitysaikaleima.

Tuottajan metatietoja ei kopioida `run.json`-tiedostoon. Tuottajan `status` ja vastaanottajan ajon tila ovat eri tietoja: tuottajan `success` ei yksin merkitse vastaanoton tai julkaisun onnistumista. Jos toimitusta ei saada, tuottajan tilaa ei päätellä.

`events.jsonl` sisältää yhden JSON-tapahtuman kullakin rivillä. Yhteiset kentät ovat `event_id`, `run_id`, `sequence`, `event_type`, `occurred_at`, `actor` ja `details`. Esimerkkitapahtumia ovat `run_created`, `task_issued`, `deadline_exceeded`, `delivery_received`, `delivery_validation_started`, `delivery_accepted`, `delivery_rejected`, `publication_started`, `publication_completed`, `run_completed` ja `run_failed`. Kunkin tapahtumatyypin `details`-kentän sallittu sisältö määritellään erikseen.

Tapahtumahistoriaan lisätään vain uusia rivejä. Aiemmat tapahtumat eivät muutu eivätkä katoa. `sequence` on yhden ajon sisällä yksilöllinen ja kasvava; `event_id` on yksilöllinen. Aikaleimat noudattavat yhteistä ISO 8601 -muotoa numeerisine UTC-offsetteineen. Tapahtuma kuvaa todennettua tapahtumaa, ei oletusta. `run.json` muodostetaan tapahtumahistorian ja hyväksyttyjen toimitustietojen perusteella.

Tunnisteiden vastuut ovat erilliset: `run_id` yksilöi loogisen ajon, `delivery_id` tuottajan toimituksen, `attempt_id` vastaanottajan käsittely-yrityksen ja `event_id` yksittäisen tapahtuman. Jokainen tapahtuma viittaa `run_id`-tunnisteeseen; toimitukseen liittyvä tapahtuma voi viitata lisäksi `delivery_id`-tunnisteeseen ja käsittely-yritykseen liittyvä tapahtuma `attempt_id`-tunnisteeseen. Tunnisteita ei käytetä ristiin eikä muodosteta uudelleen saman kohteen uudelleenyrityksissä.

#### 2.6.2 Lähdekohtaiset avaus- ja käyttötilastot

Raportintekijä ilmoittaa jokaisesta lähteestä, jonka avaamista se tosiasiallisesti yritti, lähderekisterin vakaan tunnisteen, yrityksen tuloksen ja mahdollisuuksien mukaan epäonnistumisen luokan. Avaamisen onnistuminen erotetaan sisällön saatavuudesta, laadusta, relevanssista ja raportoitavan tiedon löytymisestä. Avaamatta jääneitä lähteitä ei lasketa onnistuneiksi eikä epäonnistuneiksi avausyrityksiksi. Vastaanottaja validoi lähdehavainnot ja tallentaa ne kanoniseen ajohistoriaan siten, että tilastot voidaan yhdistää saman lähdetunnisteen perusteella eri ajoista.

Valvomon tulee esittää lähdekohtaisesti tarkastelujakson avausyritysten määrä, onnistumiset, epäonnistumiset, onnistumisaste nimittäjineen, viimeisin onnistuminen ja epäonnistuminen sekä kehityssuunta. Epäonnistumiset luokitellaan mahdollisuuksien mukaan esimerkiksi tilapäisiin verkkovirheisiin, pysyvältä vaikuttaviin virheisiin, käyttörajoituksiin/estoihin ja muihin tunnistettuihin syihin. Pieni otos, tuntematon syy tai puuttuva havainto ilmaistaan selvästi.

Valvomo voi nostaa toistuvasti epäonnistuvia lähteitä ylläpitäjän tarkistettaviksi ja ehdottaa niiden poistamista käytöstä. Lähdettä ei poisteta eikä poisteta käytöstä automaattisesti pelkkien tilastojen perusteella: tilapäiset häiriöt, käyttörajoitukset, lähteen muuttunut osoite ja havaintojen määrä on arvioitava. Käytöstä poistaminen tehdään lähderekisterin hallittuna muutoksena, ja syy jää dokumentoiduksi.

Tallennusmuoto ja hakemistorakenne määritellään teknisessä suunnittelussa. Lähdehavaintojen täsmällinen tietorakenne ja tilastojen laskentatapa määritellään ajohistorian ja toimitussopimuksen skeematyössä.


#### 2.6.3 Julkaisun ja ajotietojen tallennuksen palautuminen

RSS-syötteet, vastaanottajan kanoniset ajotietueet ja tapahtumahistoriat sekä tuottajan toimitusmetatiedot sijaitsevat erillisinä tiedostoina samassa instanssirepositoriossa. Yhteinen ohjelmistorepositorio säilyy erillisenä. Sijoittelu mahdollistaa RSS-syötteen ja sitä vastaavan ajotietueen päivittämisen samalla Git-commitilla.

**Julkaisun tallennus muodostaa yhden atomisen repositoriomuutoksen.** Kun hyväksytty toimitus julkaistaan, samaan commitiin sisällytetään:
- oikean aiheen RSS-syötteeseen lisättävä uusi item;
- alkuperäisen ajon kanonisen ajotietueen päivitys;
- julkaisuun ja käsittelyyn liittyvät uudet tapahtumat.

Commit joko sisältää kaikki nämä muutokset tai ei yhtäkään niistä. RSS-itemiä ei katsota julkaistuksi eikä ajoa onnistuneeksi ennen kuin commitin syntyminen ja sen sisältö on varmennettu. Jos tallennus epäonnistuu ennen commitin syntymistä, kumpaakaan muutosta ei käsitellä onnistuneena. Näin samaan instanssirepositorioon sijoittaminen poistaa tarpeen yrittää sovittaa kahta erillistä repositoriocommittia yhteen transaktioon.

**Keskeytyneen työnkulun palautuminen perustuu repositorion todelliseen tilaan.** Jos commit on syntynyt mutta GitHub Actions -ajo keskeytyy tai ei saa onnistumisvastauksesta tietoa, seuraava käsittely ei luota pelkkään edellisen työnkulun tulokseen. Se tarkistaa instanssirepositorion nykyisen sisällön ja etsii alkuperäisen `run_id`-ajon, toimitustunnisteen sekä RSS-itemin GUIDin. Jos ajotietue ja RSS-item vastaavat samaa toimitusta ja commit voidaan todentaa, julkaisu katsotaan onnistuneeksi eikä sitä tehdä uudelleen. Jos commitia ei ole syntynyt, tallennusvaihe voidaan uusia.

**Uudelleenyritys jatkaa samaa loogista ajoa.** Kaikissa saman ajon yrityksissä säilyvät alkuperäinen `run_id` ja toimitustunniste. Yrityskohtainen tunniste yksilöi yksittäisen käsittely-yrityksen ja sen tapahtumat, mutta yritys ei luo uutta ajoa tai uutta RSS-GUIDia. Ennen kirjoittamista vastaanottaja tarkistaa nykyisestä instanssirevisiosta, onko toimitus jo vastaanotettu, käsitelty tai julkaistu. Täsmälleen saman toimituksen toistuva vastaanotto on idempotentti: se ei luo toista ajotietuetta tai RSS-itemiä. Jos sama toimitus- tai GUID-tunniste esiintyy ristiriitaisella sisällöllä, uusi toimitus hylätään ja ristiriita kirjataan; aiempaa julkaistua sisältöä ei korvata.

**Tapahtumahistoria on vain lisäämiseen perustuva.** Kunkin yrityksen aloitus, vaiheet, virheet, tallennusyritykset ja varmennukset kirjataan uusina tapahtumina. Aiemman yrityksen tapahtumia tai vastaanottajan havaintoja ei poisteta eikä ylikirjoiteta. Ajantasainen käsittelytila muodostetaan tapahtumien perusteella, mutta tapahtumien alkuperä ja järjestys säilyvät tarkasteltavina.

**Myöhäinen toimitus käsitellään rajattuna jälkikäsittelynä.** Jos ajo on jo kirjattu epäonnistuneeksi ja tehtävä vapautettu, myöhemmin saapuva toimitus yhdistetään alkuperäiseen `run_id`-ajoon. Se voidaan validoida ja julkaista vain, jos samaa aihetta ja tehtävätyyppiä koskevaa myöhempää ajoa ei ole käynnistetty ja normaalit hyväksymisehdot täyttyvät. Myöhäinen toimitus täydentää alkuperäistä ajotietuetta uusilla tapahtumilla; se ei poista määräajan ylityksen tai epäonnistumisen havaintoa, avaa vapautettua tehtävää uudelleen eikä muuta myöhempien ajojen tietoja tai tiloja. Jos myöhempi ajo on jo käynnistetty, toimitusta ei julkaista ja hylkäys kirjataan.

Julkaistua RSS-itemiä ei muokata tai korvata palautumisen yhteydessä. Sisällöllinen korjaus tai täydennys julkaistaan uutena iteminä omalla GUIDilla ja viittauksella alkuperäiseen julkaisuun.

#### 2.6.4 Toimitusten tunnistaminen ja ristiriitojen käsittely

Ajon, tuottajan toimituksen ja vastaanottajan yksittäisen käsittely-yrityksen tunnisteet erotetaan toisistaan:

- `run_id` yksilöi tehtäväpyynnön ja loogisen ajon. Vastaanottaja luo tunnisteen tehtäväpyyntöä muodostettaessa. Se säilyy kaikissa saman ajon toimitus- ja käsittely-yrityksissä. Yhdellä `run_id`-tunnisteella on yksi kanoninen ajotietue ja enintään yksi hyväksytty varsinaisen raportin toimitus.
- `delivery_id` yksilöi raportintuottajan muodostaman toimituspaketin. Tuottaja luo UUID-tunnisteen ensimmäisen toimituksen yhteydessä ja säilyttää sen saman toimituksen uudelleenlähetyksissä. Uusi tunniste muodostetaan vain aidosti uudelle toimitukselle. Vastaanottaja tunnistaa toimituksen `run_id`- ja `delivery_id`-tunnisteiden yhdistelmästä.
- `attempt_id` yksilöi vastaanottajan käsittely-yrityksen. Vastaanottaja luo uuden UUID-tunnisteen jokaiselle uudelle käsittely- tai uudelleenyritysyritykselle ja yhdistää sen kyseisen yrityksen `run_id`- ja `delivery_id`-tunnisteisiin. Tuottaja ei määrää tätä tunnistetta.
- Vastaanottaja luo RSS-itemin `guid`-tunnisteen satunnaisena UUIDv4-tunnisteena. GUID ei johdu `run_id`-, `task_id`-, `delivery_id`- tai muista tehtävän, ajon tai raportin tiedoista eikä sisällä niistä johdettavaa tietoa. Vastaanottaja tallentaa GUIDin kanoniseen ajotietueeseen samassa atomisessa julkaisutoimessa RSS-itemin kanssa. Saman ajon uudelleenyritykset lukevat ja käyttävät ajotietueeseen tallennettua GUIDia. Erillinen korjaus- tai täydennysitem saa uuden UUIDv4-GUIDin ja viittauksen alkuperäiseen itemiin.

Vastaanottaja laskee toimituksen sisällöstä SHA-256-tiivisteen yhdenmukaisesti kanonisoidusta toimitussisällöstä. Näin saman toimituksen uudelleenlähetys voidaan erottaa tilanteesta, jossa sama tunniste on yhdistetty muuttuneeseen sisältöön. Tiivisteen laskenta ja vertailu ovat vastaanottajan vastuulla.

Ristiriita- ja kaksoistoimitukset käsitellään seuraavasti:

1. Sama `delivery_id` ja sama sisältö: kyseessä on saman toimituksen kaksoisvastaanotto, joka käsitellään idempotentisti ilman uutta julkaisua.
2. Sama `delivery_id` ja eri sisältö: toimitus hylätään tunnisteristiriitana ja ristiriita kirjataan.
3. Eri `delivery_id`, sama `run_id` ja sama sisältö: vaihtoehtoinen toimitus samalle tulokselle; siitä ei tehdä toista julkaisua.
4. Eri `delivery_id`, sama `run_id` ja eri sisältö: jos ajolle on jo hyväksytty toimitus, uusi toimitus hylätään ristiriitaisena eikä hyväksyttyä sisältöä korvata.
5. Jos ensimmäinen toimitus hylätään validoinnissa eikä ajoa ole vielä päätetty, toinen eri tunnisteella toimitettu tulos voidaan hyväksyä normaalien validointien ja hyväksymisehtojen täyttyessä.

Tunnisteet palvelevat eri vastuita: `run_id` yksilöi ajon, `delivery_id` tuottajan toimituksen ja `attempt_id` vastaanottajan käsittely-yrityksen. Ratkaisu säilyttää ensimmäisen version yhden raportintuottajan ja sarjallisen käsittelyn mallin eikä tuo rinnakkaisuuden varausmekanismeja toteutukseen.

### 2.7 Jaettava ohjelmisto ja erilliset instanssit

Aiheseurain suunnitellaan alusta lähtien julkiseksi, jaettavaksi ohjelmistoksi, jonka käyttäjäkohtaiset instanssit ovat siitä erillisiä. Ohjelmiston ja instanssin erottaminen on arkkitehtuurin perusratkaisu, ei myöhempään monen käyttäjän palvelualustaan varautuva lisäominaisuus.

- **Ohjelmistorepo** sisältää yhteisen, uudelleenkäytettävän ohjelmiston: yleisen toimintalogiikan, GitHub Actions -työnkulut, yhteiset skeemat ja tietosopimukset, käyttöliittymien yhteisen toteutuksen, testit sekä kehittäjä- ja käyttöönottodokumentaation. Ohjelmistorepon tulee soveltua jaettavan ohjelmistoversion julkaisemiseen.
- **Instanssirepo** sisältää yhden käyttöönoton omat tiedot ja asetukset: aiheet ja seurantatehtävät, määritysprofiilit, lähderekisterit, instanssin käyttöönottokohtaiset asetukset ja tila sekä kyseisen instanssin RSS-syötteet ja raportti- ja ajohistoria. Instanssirepo ei ole yhteisen ohjelmiston lähdekoodin tai julkaisuversion ensisijainen säilytyspaikka.
- Ohjelmiston ja instanssin välinen raja määritellään versioitujen, dokumentoitujen rajapintojen ja tietosopimusten avulla. Ohjelmisto ei saa olettaa, että instanssin määritykset, lähderekisterit, ajotiedot tai RSS-tiedostot sijaitsevat samassa repositoriossa tai ohjelmistokoodin suhteellisissa poluissa.
- Instanssi käyttää nimenomaisesti valittua ohjelmistoversiota. Uuden ohjelmistoversion julkaiseminen ei päivitä instanssia automaattisesti; instanssin ylläpitäjä päättää päivityksestä ja sen ajankohdasta. Käytössä oleva versio on voitava jäljittää.
- Ensimmäinen toteutus pysyy yksinkertaisena: yksi instanssi, yksi raportintuottaja ja sarjallinen tehtävänkäsittely. Tämä ratkaisu ei edellytä monen instanssin keskitettyä palvelua, monivuokraaja-arkkitehtuuria, käyttäjähallintapalvelua tai rinnakkaisten raportintuottajien varausmekanismia.
- **Valvomo ja RSS-lukija** ovat instanssikohtaisia palvelunäkymiä. Niiden yhteinen lähdekoodi, käyttöliittymäkomponentit ja yleinen toiminnallisuus kuuluvat ohjelmistorepoon. Instanssikohtaiset aiheet, asetukset, raportit, RSS-syötteet, ajotiedot ja muut näytettävät tiedot kuuluvat instanssirepoon.
- Käyttöliittymien on saatava instanssin tiedot määritellyn rajapinnan tai tietosopimuksen kautta. Yhteinen käyttöliittymäkoodi ei saa sisältää yhden instanssin aiheita, syötteitä, raportteja tai muita instanssikohtaisia arvoja kovakoodattuina.
- Ensimmäisessä versiossa sekä Valvomo että RSS-lukija julkaistaan julkisina ilman kirjautumista tai käyttöoikeusjärjestelmää. Tämä on mahdollista, koska ensimmäisen version käyttötarkoitukseen ei kuulu salaisten tai yksityisten tietojen käsittely.
- Julkisen Valvomon ja RSS-lukijan käyttämät tiedostot, rajapinnat ja selaimelle toimitettava sisältö eivät saa sisältää salaisuuksia, käyttöoikeustunnuksia, yksityisiä tietoja tai muuta luottamuksellista sisältöä. Tietojen piilottaminen pelkästään käyttöliittymän esitystasolla ei riitä.
- Jos myöhempi käyttötarve edellyttää luottamuksellisen tiedon käsittelyä, tietojen erottelu ja käyttöoikeuksien tekninen toteutus suunnitellaan erikseen ennen tällaisen tiedon käyttöönottoa.
- Repositorioiden nimet, täsmällinen hakemistorakenne, ohjelmiston jakelukanava ja instanssin käyttöönoton tekninen toteutus ratkaistaan myöhemmässä teknisessä suunnittelussa. Niitä ei lukita tällä arkkitehtuuriperiaatteella.

## 3. Kehitysympäristön hyväksytty tavoitetila

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

## 4. Ehdotettu toteutuksen vaiheistus

1. Uuden toteutuksen perustaminen puhtaalta pöydältä hyväksytyn tavoitetilan ja tietosopimusten mukaisesti. Vanhan arkistoidun toteutuksen koodia, skeemoja, määrityksiä, testejä, työnkulkuja tai tietorakenteita ei siirretä eikä käytetä uuden toteutuksen lähtökohtana.
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

## 5. Myöhempiin versioihin jätetyt kehitystehtävät

Tässä osiossa pidetään kirjaa asioista, jotka on tietoisesti rajattu ensimmäisen version ulkopuolelle tai joiden toteutusta on päätetty lykätä. Ne eivät ole ensimmäisen version avoimia hyväksymiskriteerejä. Asia siirretään toteutussuunnitelman varsinaiseen työvaiheeseen vasta, kun sen toteutusajankohta ja laajuus päätetään.

| Myöhemmäksi jätetty asia | Miksi myöhemmin | Milloin asiaan palataan |
|---|---|---|
| RSS-historian lukemisen optimointi, kuten indeksointi, hakupalvelu tai tiivistelmä-/välimuistiratkaisu | Ensimmäisessä versiossa raportintuottaja lukee koko kyseisen aiheen ja tehtävätyypin RSS-historian suoraan GitHubista. Erillistä hakukerrosta ei tarvita ennen kuin historian koko tai lukemisen kustannus aiheuttaa todellisen ongelman. | Kun RSS-historian koko, käsittelyaika tai raportintuottajan käytettävissä oleva konteksti tekee koko historian lukemisesta epäkäytännöllistä. Alkuperäinen RSS-historia säilyy tällöinkin vertailun lähteenä. |
| Useat samanaikaiset raportintuottajat, tehtävien varaukset ja rinnakkaisuuden hallinta | Ensimmäisessä versiossa on yksi raportintuottaja ja tehtävät käsitellään sarjallisesti. | Kun käyttöön tulee toinen raportintuottaja tai rinnakkaisille ajoille syntyy todellinen tarve. |
| Erillinen GitHub App tai raportintuottajan teknisesti rajatut kirjoitusoikeudet | Ensimmäinen versio käyttää ChatGPT:n ajastetun tehtävän Codex Connector -yhteyttä. Erillistä vastaanotto-GitHub Appia ei käytetä; se voidaan luoda myöhemmin uudelleen, jos käyttöoikeuksien eriyttämiseen syntyy tarve. | Kun raportintuottajia tai muita integraatioita tulee lisää tai käyttöoikeuksien eriyttäminen muuttuu tarpeelliseksi. |
| Käyttäjäkohtainen tunnistaminen ja erillinen HTTPS-vastaanottopalvelu | Ensimmäisessä versiossa luotetaan Codex Connectorin kautta tehtävään GitHub-toimitukseen; erillistä käyttäjätunnistautumista tai HTTPS-vastaanottopalvelua ei rakenneta. | Kun tuottajia tulee useita, toimituskanava laajenee GitHubin ulkopuolelle tai uhkamalli edellyttää lähettäjäkohtaista tunnistamista. |
| Älykkäämpi epäonnistuneiden tehtävien palautuslogiikka | Ensimmäisessä versiossa käytettävien automaattisten käsittely-yritysten määrät, laskentatavat ja määräajat ovat tehtävätyypin määrityksissä ja tarvittaessa profiileissa määritettäviä konfiguroitavia arvoja; niitä ei kovakoodata. | Kun käytännön ajohistoria osoittaa, että yksinkertainen palautusmalli ei riitä. |
| Ulkoiset ilmoitukset | Ne eivät ole välttämättömiä ensimmäisen version seuranta-, vastaanotto- ja julkaisuketjulle. | Kun ilmoituksille määritellään konkreettinen käyttäjätarve ja kanava. |
| Toimitusten kryptografiset allekirjoitukset ja erilliset tarkistussummat | Ensimmäiseen versioon riittävät toimituspaketin tiedostojen, rakenteen, tunnisteiden ja aktiiviseen tehtävään kuulumisen tarkistukset. | Jos uhkamalli tai toimituskanavan luonne osoittaa vahvemman eheyden todentamisen tarpeelliseksi. |
| Batch-ajot eli usean aiheen käsittely yhdellä käynnistyksellä | Ensimmäisen version yksinkertainen toimintamalli käsittelee enintään yhden aiheen yhdellä käynnistyksellä. | Jos yhden aiheen ajomalli osoittautuu käytännössä rajoittavaksi ja batch-ajolle on selkeä tarve. |

Luetteloa ylläpidetään suunnittelun edetessä. Kun myöhemmäksi jätetty asia otetaan työn alle, se siirretään tästä osiosta asianomaiseen toteutusvaiheeseen ja tarvittaessa avoimiin teknisiin yksityiskohtiin. Näin samaa asiaa ei ylläpidetä kahdessa paikassa ristiriitaisin tilatiedoin.

## 6. Avoimet tekniset yksityiskohdat

Seuraavat tekniset ja toiminnalliset yksityiskohdat ovat avoinna. Luettelo on sama vaatimusmäärittelyssä ja toteutussuunnitelmassa, jotta suunnittelun tilanne pysyy yhdenmukaisena.

### 1. Tietomallit ja skeemat

1. **Skeemojen tarkat rakenteet**
   - 1.1 Määritellään pääskeemojen täydelliset kenttäluettelot, tietotyypit ja pakollisuus.
   - 1.2 Määritellään kenttäkohtaiset rajat, sallitut arvot ja taulukoiden täsmälliset rajat.
   - 1.3 Ratkaistaan yhteisten osaskeemojen lopullinen jako, nimet ja uudelleenkäyttö.
   - 1.4 Määritellään skeemojen väliset viittaukset ja niiden eheyden tarkistus.
   - 1.5 Täsmennetään rakenteellisen ja toiminnallisen validoinnin työnjako, virheraportointi ja validointikoodin vastuut.
   - *Rajaus:* skeemahakemiston jako, JSON Schema -versio ja yleiset sulkevuusperiaatteet on päätetty.

2. **Laaduntarkistusten parametrit**
   - 2.1 Luetellaan kunkin tarkistuksen tarvitsemat parametrit ja niiden tarkoitus.
   - 2.2 Määritellään parametrien nimet, tyypit, pakollisuus, rajat ja sallitut arvot.
   - 2.3 Määritellään tarkistuskohtaiset parametriskeemat ja niiden validointiehdot.
   - 2.4 Päätetään tarkistuskohtaisten oletusarvojen täsmälliset arvot.
   - 2.5 Määritellään keskinäisten riippuvuuksien ja virheellisten yhdistelmien käsittely.
   - *Rajaus:* parameters on aina objekti, asetukseton arvo on tyhjä objekti ja tuntemattomat parametrit hylätään.

3. **Raportoitavien havaintojen kategoriat**
   - 3.1 Tunnistetaan kunkin tehtävätyypin tarvitsemat kategoriat.
   - 3.2 Määritellään tehtävätyyppikohtaiset pysyvät kategoriatunnisteet.
   - 3.3 Määritellään kategorioiden nimet, kuvaukset ja käyttörajat.
   - 3.4 Määritellään tuntemattomien tai vanhentuneiden kategorioiden käsittely.
   - 3.5 Määritellään kategorioiden muuttamisen ja käytöstä poistamisen säännöt.
   - *Rajaus:* yhteistä kaikkien tehtävätyyppien luokittelua ei muodosteta.

4. **Tiedostoroolien parametrit**
   - 4.1 Luetteloidaan toimituspaketin tiedostoroolit ja niiden tarkoitukset.
   - 4.2 Määritellään roolikohtaiset parametrit, tyypit ja pakollisuus.
   - 4.3 Määritellään roolikohtaiset parametriskeemat ja oletusarvot.
   - 4.4 Määritellään roolien riippuvuudet ja tehtävätyyppikohtaiset rajoitukset.
   - 4.5 Määritellään puuttuvien, toistuvien ja ristiriitaisten roolien käsittely.
   - *Rajaus:* parameters on aina objekti ja tuntemattomat parametrit hylätään.

5. **Toimitusmetatietojen täydentäminen**
   - 5.1 Käydään kuusi hyväksyttyä tietoryhmää läpi ja tunnistetaan jäljellä olevat täsmennystarpeet.
   - 5.2 Määritellään lähde-, kanava- ja tarkistusyritystietojen kentät, tyypit ja viittaukset.
   - 5.3 Määritellään havaintoyhteenvedon kentät ja niiden suhde tehtävätyypin kategorioihin.
   - 5.4 Täsmennetään valinnaisten tuottajatietojen sisältö ja rajat.
   - 5.5 Määritellään kenttien pakollisuus, tyhjien arvojen käsittely ja ryhmien johdonmukaisuussäännöt.
   - 5.6 Varmistetaan tuottajan ja vastaanottajan tietojen sekä tunnisteiden selkeä erottelu.
   - *Rajaus:* kuusi tietoryhmää sekä producer-ryhmän perusrakenne, valinnaisuus ja producer_type-arvot on päätetty.

6. **Vastaanottajan ajotietomallit**
   - 6.1 Määritellään run.json-tietueen kentät, tyypit, pakollisuus ja sallitut arvot.
   - 6.2 Määritellään ajon, tuottajan tuloksen, vastaanoton ja julkaisun tilaluokat ja siirtymät.
   - 6.3 Määritellään events.jsonl-tapahtumien täydellinen tapahtumatyyppiluettelo.
   - 6.4 Määritellään tapahtumatyyppien details-rakenteet ja pakolliset tiedot.
   - 6.5 Määritellään tietueiden ja toimitusmetatietojen viittauskentät.
   - 6.6 Määritellään tapahtumien järjestys-, aikaleima-, yksilöllisyys- ja append-only-säännöt.
   - 6.7 Määritellään puuttuvien, ristiriitaisten ja tuntemattomiin toimituksiin viittaavien tietojen käsittely.

### 2. Lähderekisteri ja lähdetilastot

7. **Rekisterin ulkopuolisten lähteiden ehdotukset**
   - 7.1 Määritellään ehdotustietueen kentät, tyypit ja pakollisuus.
   - 7.2 Määritellään lähde- ja kanavaehdotusten väliset viittaukset.
   - 7.3 Täsmennetään alkuperä-, löytämis- ja perustelutietojen sisältö.
   - 7.4 Määritellään skeema-, URL- ja duplikaattitarkistusten ehdot.
   - 7.5 Täsmennetään elinkaaren tilasiirtymät, hyväksyntä, hylkäys ja jäljitettävyys.
   - 7.6 Määritellään hyväksytyn ehdotuksen siirto rekisteriin ja rekisterirevision päivitys.
   - 7.7 Arvioidaan myöhemmän käyttöliittymän tarve; ensimmäisen version GitHub-käsittely säilyy lähtökohtana.

8. **Lähdekohtaiset tilastot**
   - 8.1 Määritellään tilastotietueen kentät ja suhde sisältökanavien tarkistusyrityksiin.
   - 8.2 Määritellään tilastojen laskenta ja päivitys kanonisesta ajohistoriasta.
   - 8.3 Täsmennetään 30 ja 90 päivän sekä koko historian tunnuslukujen laskentasäännöt.
   - 8.4 Määritellään virheluokkien ryhmittely ja onnistumisen laskenta.
   - 8.5 Täsmennetään toistuvien epäonnistumisten huomautusten nostokriteerit.
   - 8.6 Määritellään tilastojen ja huomautusten esitys Valvomossa sekä puuttuvan aineiston ilmaisu.
   - 8.7 Määritellään laskennan oikeellisuuden testaus.
   - *Rajaus:* tilastojen perusperiaatteet, tarkastelujaksot ja ylläpitäjän arvioitavat huomautukset on päätetty.

### 3. Integraatiot ja ajonhallinta

9. **Vastaanottoprosessin tekninen viimeistely ja käyttöönotto**
   - 9.3 **Raportin HTML-perusrakenne:** määritellään yhteiset rakenneosat, otsikkohierarkia, metatietojen ja lähdeviitteiden esitys, saavutettavuus sekä aihekohtaisen vaihtelun rajat.
   - 9.6 **Vastaanoton ja julkaisun työnkulku:** määritellään tilasiirtymät, vaiheiden vastuut, atomisen tallennuksen rajat, julkaisemisen järjestys ja odotustilat.
   - 9.7 **Idempotenssi ja virhetilanteet:** määritellään uudelleenyrityksen tunnistaminen, jo käsitellyn toimituksen vaste, ristiriitaisten toimitusten käsittely sekä pysyvien ja tilapäisten virheiden luokittelu.
   - 9.8 **Julkaisun varmennus:** määritellään itemin tallentumisen, GUIDin ja ajotietueen yhtäpitävyyden, RSS-luettavuuden ja Pages-julkaisun valmistumisen tarkistukset.
   - 9.9 **Käyttöönoton hyväksymiskriteerit:** määritellään päästä päähän -skenaariot, palautumis- ja virhetestit, havaittavuus sekä käyttöönottovalmiuden ehdot.
   - *Rajaus:* RSS-itemin täydellinen elementtirakenne ja järjestys (9.1), yhden item-elementin toimitus, link-elementin kielto, vastaanottajan UUIDv4-GUID, atominen tallennus ja GUIDin idempotentti uudelleenkäyttö sekä raportin HTML-perusrakenne ja aikavälin ulkopuolisten merkittävien täydennysten esityssäännöt (9.3), toimituspaketin rajapinta (9.4) sekä vastaanoton validointijärjestys ja hyväksymisehdot (9.5) on päätetty. Sisällöllinen laaduntarkistus tehdään jokaisella seurantakierroksella; erillistä laaduntarkistusajoa ei ole.

10. **Instanssirepositorion ja julkaisusuojauksen käyttöönotto**
   - 10.1 Määritellään instanssirepositorion lopullinen hakemistorakenne ja Pages-julkaisun lähdepolut.
   - 10.2 Määritellään vastaanotto- ja julkaisuhaarojen vastuut ja sallittu tiedonsiirto.
   - 10.3 Määritellään main-haaran suojaussäännöt, pakolliset tarkistukset ja poikkeusmenettely.
   - 10.4 Varmennetaan Codex Connectorin repositoriotasoisten oikeuksien vaikutus haarasuojaukseen.
   - 10.5 Määritellään Pages-julkaisun käynnistys, virheellisen julkaisun esto ja palautus.
   - 10.6 Määritellään käyttöönoton oikeus- ja suojaustestit.
   - *Rajaus:* ensimmäisessä versiossa ei käytetä erillistä vastaanotto-GitHub Appia.

11. **Ajojen käynnistäminen**
   - 11.1 Määritellään 15 minuutin yhteisen tarkistusvälin ajastustapa ja GitHub Actionsin viiveiden käsittely.
   - 11.2 Määritellään manuaalisen käynnistyksen käyttäytyminen ja yhteiset käsittelysäännöt.
   - 11.3 Määritellään aihekohtaisten erääntymisten laskenta, aikavyöhyke ja aikavälirajat.
   - 11.4 Määritellään enintään yhden erääntyneen aiheen valinta ja valinnan reiluus.
   - 11.5 Määritellään päällekkäisten käynnistysten esto ja sarjallisuuden tekninen toteutus.
   - 11.6 Määritellään käynnistysvirheiden ja väliin jääneiden käynnistysten havaitseminen ja kirjaaminen.
   - *Rajaus:* erillistä laaduntarkistusajoa ei käynnistetä.

12. **Jonon ja uudelleenyritysten tarkat rajat**
   - 12.1 Määritellään tehtävän muodostuksen, tuottajan suorituksen, vastaanoton ja julkaisun aikakatkaisut.
   - 12.2 Määritellään uudelleenyritysten enimmäismäärät vaiheittain ja virheluokittain.
   - 12.3 Määritellään odotusajat, mahdollinen kasvava viive ja enimmäisodotusaika.
   - 12.4 Määritellään pysyvien, tilapäisten ja käyttäjän toimenpidettä vaativien virheiden käsittely.
   - 12.5 Määritellään epäonnistuneen aiheen uusi jonotus ja vaikutus muiden aiheiden etenemiseen.
   - 12.6 Määritellään keskeytyneen tehtävän tunnistaminen, tilan palautus ja turvallinen jatkaminen.
   - 12.7 Määritellään manuaalisen uudelleenyrityksen oikeudet, vaikutukset ja jäljitettävyys.

13. **Toimituspakettien säilytys**
   - 13.1 Määritellään vastaanottohaaran alkuperäisten pakettien säilytysajat.
   - 13.2 Määritellään hyväksyttyjen, hylättyjen ja keskeneräisten pakettien säilytyserot.
   - 13.3 Määritellään siivouksen käynnistysehdot, ajastus ja poistoperusteet.
   - 13.4 Määritellään keskeneräisten ja palautettavien ajojen aineiston suojaaminen.
   - 13.5 Määritellään auditointi-, palautus- ja poikkeustilanteiden säilytystarpeet.
   - 13.6 Määritellään tallennustilan seuranta ja toiminta säilytysrajojen ylittyessä.

### 4. Raportintekijä ja käyttöliittymät

14. **Yhteinen raportintekijän perusprompti**
   - 14.1 Määritellään promptin rakenne ja yleiset vastuut suhteessa tehtäväpyyntöön.
   - 14.2 Määritellään tehtäväpyynnön, ohjeiden ja rakenteisten syötteiden lukemisjärjestys.
   - 14.3 Täsmennetään lähteiden käyttöä, epävarmuutta, lähteistämistä ja toimituspaketin muodostamista koskevat ohjeet.
   - 14.4 Määritellään puuttuvien tietojen, ristiriitaisten ohjeiden ja validointivirheiden käsittely.
   - 14.5 Määritellään versionhallinta, revisioviittaus ja yhteensopivuusperiaatteet.
   - 14.6 Määritellään testitapaukset, arviointikriteerit ja sovittaminen tuottajaintegraatioon.

15. **Valvomon toteutus**
   - 15.1 Määritellään yleiskuvan tietosisältö, järjestys, päivittyminen ja poikkeamat.
   - 15.2 Määritellään aihelistan kentät, suodatus, järjestäminen ja tilan esitys.
   - 15.3 Määritellään ajohistorian suodatus, tapahtumien tarkastelu ja virheiden esitys.
   - 15.4 Määritellään lähdekattavuuden ja lähdetilastojen sijoittuminen Valvomoon.
   - 15.5 Määritellään navigointi, URL-rakenne, tyhjät, lataus- ja virhetilat.
   - 15.6 Määritellään tietojen päivitystapa ja riippuvuus instanssin julkisista tiedostoista.
   - 15.7 Määritellään saavutettavuus-, responsiivisuus- ja käytettävyyskriteerit sekä testaus.

16. **Julkisten käyttöliittymien tietoturvatarkistukset**
   - 16.1 Luetteloidaan julkisiin tiedostoihin ja rajapintoihin päätyvät tietolähteet.
   - 16.2 Määritellään salaisuuksien, käyttöoikeustunnusten ja yksityisten tietojen tunnistusmenetelmät.
   - 16.3 Määritellään tarkistusten kattavuus lähdekoodille, määrityksille, ajotiedoille ja julkaistulle sisällölle.
   - 16.4 Määritellään löydösten vakavuudet ja ehdot, joilla julkaisu estetään.
   - 16.5 Määritellään väärien positiivisten käsittely, poikkeusten hyväksyntä ja auditointijälki.
   - 16.6 Määritellään CI- ja julkaisuprosessin tarkistukset sekä niiden testaus.

### 5. Historiatiedot, toimitusmalli ja myöhemmät käyttöoikeudet

17. **Historiatietojen säilytys**
   - 17.1 Määritellään ajotietueiden ja tapahtumahistorioiden säilytysajat.
   - 17.2 Määritellään lokien, virhetietojen ja diagnostiikka-aineistojen säilytysajat.
   - 17.3 Määritellään väliaineistojen suhde toimituspakettien erilliseen säilytyspolitiikkaan.
   - 17.4 Määritellään arkistointi, siivous, poisto ja mahdollinen anonymisointi.
   - 17.5 Määritellään historian palautus, tarkastelu ja raportointikäyttö säilytysajan aikana.
   - 17.6 Määritellään poistojen jäljitettävyys ja säilytyspoikkeukset.

18. **Ohjelmiston ja instanssin toimitusmalli**
   - 18.1 Vahvistetaan ohjelmisto- ja instanssirepositorion vastuut ja hakemistorakenteet.
   - 18.2 Määritellään jakelukanava ja instanssin käyttämän ohjelmistoversion kiinnitystapa.
   - 18.3 Määritellään päivitysten hyväksyntä, käyttöönotto, palautus ja yhteensopivuuden tarkistus.
   - 18.4 Määritellään määritysten, aineistojen ja raporttipakettien viittaus- ja siirtomalli.
   - 18.5 Määritellään ohjelmisto-, skeema- ja instanssirevisioiden yhteensopivuussäännöt.
   - 18.6 Määritellään uuden instanssin perustamisen, päivittämisen ja palauttamisen käytännöt.

19. **Myöhempi käyttöoikeuksien tekninen toteutus**
   - 19.1 Tunnistetaan luottamukselliset tietoluokat ja tilanteet, joissa julkinen malli ei riitä.
   - 19.2 Määritellään julkisen ja rajatun tiedon erottelu repositorioissa, tiedostoissa ja käyttöliittymissä.
   - 19.3 Arvioidaan tunnistautumisen, roolien ja käyttöoikeuksien hallinnan tarpeet.
   - 19.4 Määritellään salaisuuksien säilytys suoritusympäristössä erillään julkisesta instanssidatasta.
   - 19.5 Määritellään auditointi, oikeuksien muutokset ja väärinkäytösten havaitseminen.
   - 19.6 Rajataan myöhemmät ratkaisut niin, etteivät ne monimutkaista ensimmäistä versiota tarpeettomasti.
   - *Rajaus:* tämä ei ole ensimmäisen version vaatimus.

### Versiohistoria

- **0.3.109 (25.11.2026):** hyväksyttiin vastaanoton validoinnin järjestys ja keskeyttämisehdot, tunnisteiden ja ajolle kiinnitettyjen revisioiden vastaavuus, tiedostoluettelon rajaus (metadata.json ei sisälly omaan luetteloonsa), eheystarkistukset, XML/HTML/RSS-turvallisuus, keskinäisten viittausten tarkistus, pysyvien ja tilapäisten virheiden erottelu sekä hyväksymisen raja. Kohta 9.5 poistettiin avoimista kohdista. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.3.108 (24.11.2026):** hyväksyttiin toimituspaketin rajapinta: `metadata.json` kuvaa toimituksen ja tiedostoluettelon, `item.xml` sisältää koko raportin `<content:encoded>`-elementissä eikä erillistä HTML-raporttitiedostoa toimiteta. Täsmennettiin tiedostojen rooli- ja polkuyksilöinti sekä korjaus- ja täydennysitemien viittaus alkuperäiseen UUIDv4-GUIDiin; alkuperäinen julkaisu säilyy muuttumattomana. Kohta 9.4 poistettiin avoimien kohtien luettelosta. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.3.107 (24.11.2026):** hyväksyttiin raportin HTML-perusrakenne, otsikkohierarkia, seuranta-aikavälin ja lähdeviitteiden esittäminen, saavutettavuuden periaatteet sekä aihekohtainen sisältövaihtelu. Sallittiin erilliset, selvästi ajoitetut täydennykset merkittäville aikavälin ulkopuolisille uutisille ja aiemmasta raportista puuttuneille havainnoille. Kohta 9.3 poistettiin avoimien kohtien luettelosta. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.3.106 (24.11.2026):** hyväksyttiin kohdan 9.2 XML- ja HTML-yhteensopivuus: XML-kirjastolla muodostaminen, CDATA-käytäntö ja turvallinen osiointi, sallittujen HTML-elementtien ja attribuuttien lista, HTML:n hylkääminen ilman automaattista korjausta sekä kuvien rajaaminen jatkokehitykseen. Kohta 9.2 poistettiin avoimien kohtien luettelosta. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.3.105 (24.11.2026): hyväksyttiin RSS-itemin täydellinen elementtirakenne ja vakiojärjestys: `<title>`, `<guid isPermaLink="false">`, `<pubDate>`, valinnainen `<description>` ja `<content:encoded>`. Rajattiin muut RSS-elementit ja ylimääräiset attribuutit pois sekä määriteltiin `content`-nimiavaruuden ilmoittaminen item-elementissä. Kohta 9.1 poistettiin avoimien kohtien luettelosta; HTML:n yksityiskohtainen rakenne jäi kohtaan 9.3. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.3.104 (24.11.2026):** jaettiin kaikki 19 avointa suunnittelukokonaisuutta numeroiduiksi alikohdiksi. Hyväksytyt ratkaisut erotettiin edelleen avoimista yksityiskohdista. Sama alakohtainen luettelo synkronoitiin vaatimusmäärittelyyn. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.


- **0.3.103 (24.11.2026):** päivitettiin avoimien teknisten asioiden luettelo vastaamaan 24.11. hyväksyttyjä RSS-itemin sisältösopimuksen ja UUIDv4-GUIDin ratkaisuja. Poistettiin GUIDin muodostus avoimista asioista ja rajattiin jäljellä oleva työ RSS-elementtien pakollisuuteen, HTML-rakenteen tarkempaan perusmuotoon, työnkulkujen toteutukseen, uudelleenyritysrajoihin ja käyttöönoton varmennuksiin. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.3.98 (24.11.2026):** synkronoitiin RSS-itemin toimitusmuodon ja linkityksen kiinteät säännöt sekä rajattiin avoimeksi jäävät RSS-yksityiskohdat vastaamaan vaatimusmäärittelyä.

- **0.3.97 (24.11.2026):** täsmennettiin RSS-itemin toimitusmuoto yhdeksi `<item>`-elementiksi ilman `<link>`-elementtiä ja määriteltiin lähteiden linkitys raporttisisällössä. Päätettiin aloittaa toteutus puhtaalta pöydältä käyttämättä vanhaa arkistoitua toteutusta; poistettiin vanhan toteutuksen inventaario-, hyödyntämis- ja siirtymävaiheet suunnitelmasta sekä avoimista tehtävistä.

- **0.3.96 (24.11.2026):** korjattiin vastaanottoprosessin uuden alaotsikon hierarkiataso dokumentaation laaduntarkistuksen havainnon perusteella. **0.3.95 (24.11.2026):** kirjattiin vaatimusmäärittelyn kanssa yhdenmukaisesti vastaanottoprosessin 12 hyväksyttyä kokonaisuutta. RSS-itemin tarkka sisältösopimus jätettiin avoimeksi; vastaanoton ja julkaisun työnkulkujen tekninen toteutus, uudelleenyritysrajat ja käyttöönoton varmennukset säilyvät suunnittelutehtävinä. Toteutusta, skeemoja, testejä tai automaatioita ei luotu tai muutettu.

- **0.3.94 (24.11.2026):** synkronoitiin toteutussuunnitelman perustaviittaus vaatimusmäärittelyn uusimpaan versioon 0.12.51. Avoimien suunnittelukysymysten luettelo vastaa nyt täsmälleen vaatimusmäärittelyä.

- **0.3.94 (24.11.2026):** synkronoitiin vaatimusmäärittelyn avoimet vastaanottoa ja käyttöoikeuksia koskevat suunnittelukysymykset Codex Connector -toimitusmalliin. Korjattiin myöhempiin versioihin jätettyjen GitHub App - ja tunnistautumiskuvausten ristiriidat. Toteutusta ei aloitettu.

- **0.3.94 (24.11.2026):** yhdenmukaistettiin repositorioiden dokumentoidut hakemistonimet englanninkielisiksi. Toimituspakettien polku muutettiin muotoon `deliveries/{run_id}/{delivery_id}/`, ja ajohistorian esimerkkirakenteen `deliveries/` säilytettiin saman käytännön mukaisena. Hakemistojen nimeämiskäytäntö kirjattiin. Repositorioiden todellista sisältöä tai toteutusta ei muutettu.

- **0.3.94 (24.11.2026):** yhdenmukaistettiin repositorioiden dokumentoidut hakemistonimet englanninkielisiksi. Toimituspakettien polku muutettiin muotoon `deliveries/{run_id}/{delivery_id}/`, ja ajohistorian esimerkkirakenteen `deliveries/` säilytettiin saman käytännön mukaisena. Hakemistojen nimeämiskäytäntö kirjattiin. Repositorioiden todellista sisältöä tai toteutusta ei muutettu.

- **0.3.91 (24.11.2026):** hyväksyttiin ensimmäisen vaiheen raportintuottajaksi ChatGPT:n ajastettu tehtävä ja toimituskanavaksi Codex Connector. Käytännön testi vahvisti toimituksen erilliseen vastaanottohaaraan muuttamatta `main`-haaraa. Määriteltiin vastaanottohaaraksi `raportit-inbox`, toimituspaketin hakemistorakenne sekä vastaanoton ja julkaisun erottelu. Täsmennettiin Codex Connectorin repositoriotasoisen käyttöoikeuden vuoksi `main`-haaran erillinen suojaustarve. Erillistä vastaanotto-GitHub Appia ei käytetä ensimmäisessä versiossa; aiempi App on poistettu. Toteutusta, skeemoja, testejä tai automaatioita ei luotu tai muutettu.

- **0.3.90 (24.11.2026):** hyväksyttiin julkinen instanssirepositorio ja GitHub Pages -julkaisu, erilliset vastaanotto- ja julkaisuhaarat sekä instanssirepoon rajattu GitHub App, jolla on vain Metadata read- ja Contents read/write -oikeudet. Täsmennettiin, että koko repositorio ja sen historia ovat julkisia sekä että Contents-kirjoitusoikeus on repositoriotasoinen ja julkaisuhaaran suojaus on toteutettava erikseen. Toteutusta, repositoriota, Appia tai automaatioita ei luotu tai muutettu.

- **0.3.89 (24.11.2026):** päivitettiin vaatimusmäärittelyn perustaviittaus versioon 0.12.46 ja synkronoitiin toteutussuunnitelman versiotieto. Muita suunnitteluratkaisuja ei muutettu.

- **0.3.88 (24.11.2026):** yhdenmukaistettiin vastaanottorajapinnan avoimen suunnittelukohdan sanamuoto vaatimusmäärittelyn kanssa ja korjattiin `main`-haaran nimen kirjoitusasu. Aiemmin hyväksyttyjä teknisiä ratkaisuja ei muutettu.

- **0.3.87 (24.11.2026):** hyväksyttiin ensimmäisen version toimituskanavaksi nykyisen GitHub App -yhteyden kautta tehtävä Git push erilliseen vastaanottohaaraan. Täsmennettiin, ettei käyttäjäkohtaista tunnistamista tai erillistä HTTPS-vastaanottopalvelua toteuteta ensimmäisessä versiossa, että Appin tosiasialliset oikeudet tarkistetaan ja että pushin onnistuminen ei tarkoita toimituksen hyväksymistä tai julkaisua. Vastaanoton ja validoinnin tulokset kirjataan GitHub Actionsin ja vastaanottajan ajotietojen kautta. Laajemmat tunnistus- ja käyttöoikeusmallit jätettiin myöhempiin versioihin. Toteutusta, skeemoja, testejä tai automaatioita ei luotu tai muutettu.
- **0.3.86 (24.11.2026):** hyväksyttiin rekisterin ulkopuolisten lähteiden ehdotusten tietoryhmät, erillinen `data/source-proposals/`-tallennus, ehdotusten elinkaaren tilat ja ensimmäisen version GitHub-pohjainen käsittely. Täsmennettiin kanavakohtaisten avausyritysten tilastointi, virheluokat, 30/90 päivän ja koko historian tarkastelujaksot, Valvomon tunnusluvut sekä toistuvien epäonnistumisten alustava nostokriteeri. Lähteiden automaattista poistamista tai käytöstä poistamista tilastojen perusteella ei sallita. Toteutusta, skeemoja, testejä tai automaatioita ei luotu tai muutettu.

- **0.3.85 (24.11.2026):** kirjattiin hyväksytty tietomalli- ja skeematyön ehdotuspaketti: skeemahakemiston vastuualuejako, tietomallikohtaiset skeemat ja validointiperiaatteet, tehtävätyyppikohtaiset raportoitavien havaintojen kategoriat, tiedostoroolien `parameters`-objektin säännöt, `producer`-ryhmän perusrakenne sekä vastaanottajan `run.json`- ja `events.jsonl`-mallien tietoryhmät, tapahtumien yhteiset kentät, tunnistevastuut ja append-only-kirjaamissäännöt. Avoimet kohdat rajattiin jäljellä oleviin kenttä- ja skeemakohtaisiin yksityiskohtiin. Skeemoja, toteutusta, testejä tai automaatioita ei luotu tai muutettu.

- **0.3.84 (24.11.2026):** synkronoitiin avoimien teknisten yksityiskohtien luettelo vaatimusmäärittelyn kanssa. Yhteinen luettelo kattaa tietomallit ja skeemat, lähderekisterin, lähdetilastot, integraatiot, ajonhallinnan, raportintekijän, käyttöliittymät, siirtymän ja käyttöönoton.

- **0.3.83 (24.11.2026):** hyväksyttiin raportoitavien havaintojen erillinen tietomalli, tehtävätyyppikohtaiset kategoriat, lähde- ja kanavaviittaukset sekä valinnainen `findings.json`. Hyväksyttiin tiedostoroolien pysyvät tunnisteet ja tulostilakohtainen `required` / `optional` / `forbidden`-malli, toimitettujen tiedostojen luettelo, tiedostokoon ja SHA-256-tiivisteen pakollisuus, polkuturvallisuus, tulostilojen toimitusvaatimukset sekä vastaanottajan seitsemänvaiheinen validointi ja virheluokat. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.

- **0.3.82 (24.11.2026):** hyväksyttiin laaduntarkistusten parametrien yleinen tietomalli ja tarkistuskohtaiset skeemat, tyhjän `parameters`-objektin sääntö, oletusarvojen soveltaminen, tuntemattomien parametrien hylkääminen, tunnisteiden yksilöllisyys ja pysyvyys, määrittelyn revisioseuranta, pakollisten ja valinnaisten tarkistusten tulostietuevaatimukset sekä määrittelyn, suorittamisen ja vastaanottajan validoinnin vastuurajat. Hyväksyttiin myös toimituspaketin tehtävätyyppikohtainen sisältö, metatietojen ja sisältötiedostojen erottaminen, suhteelliset tiedostoviittaukset sekä vastaanottajan eheysvalidointi muuttamatta tuottajan aineistoa. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.
- **0.3.81 (24.11.2026):** hyväksyttiin tietomalli- ja skeematyön nelijako, yhteisten osaskeemojen vähimmäisalueet, tehtävätyypin laaduntarkistusten määritystietueen kentät (`check_id`, `name`, `description`, `required`, `parameters`), tunnisteiden pysyvyys- ja uudelleenkäyttösäännöt sekä laaduntarkistusten rakenteellisen ja toiminnallisen validoinnin erottaminen. Täsmennettiin skeemojen `$id`- ja `$schema`-vaatimukset, `format`-tarkistukset ja CI-testauksen kattavuus. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.
- **0.3.80 (24.11.2026):** yhdenmukaistettiin avoimien teknisten yksityiskohtien luettelo hyväksyttyjen päätösten kanssa. Täsmennettiin lähderekisterin ulkopuolisten lähteiden ehdotuksia koskevan avoimen työn rajaus sekä laaduntarkistusten määrittelyn ja ajokohtaisten tulosten jo päätetyt osat. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.
- **0.3.79 (24.11.2026):** hyväksyttiin laaduntarkistusten ajokohtaisten tietueiden kentät, tulosluokat, havaintojen vakavuusluokat, kirjaamissäännöt, vaadittujen tarkistusten kattavuus ja tuottajan sekä vastaanottajan vastuunjako. Yleistä automaattista hyväksymisrajaa vakavuusluokille ei asetettu. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.
- **0.3.78 (24.11.2026):** hyväksyttiin, että yksittäiset laaduntarkistukset määritellään tehtävätyypin määrityksessä ja niiden ajokohtaiset tulokset tallennetaan tuottajan toimitusmetatietoihin. Tarkistusten määrittely erotetaan toteutuneiden tulosten kirjaamisesta; tarkat kentät ja tulosarvot jätettiin avoimiksi. Toteutusta, skeemoja, testejä tai automaatioita ei muutettu.
- **0.3.77 (23.11.2026):** hyväksyttiin Havainnot ja laadunvarmistus -tietoryhmän kahden osan rakenne: raportoitavien havaintojen yhteenveto sekä raportintuottajan tekemien laaduntarkistusten tulokset. Täsmennettiin, että tehtävätyypin määritys määrittelee vaadittavat tarkistukset, tuottajan tulostila kuuluu kolmanteen ryhmään ja vastaanottajan käsittelytilat jäävät tuottajan metatietojen ulkopuolelle. Tarkat kentät ja tulosarvot jätettiin avoimiksi. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.3.76 (23.11.2026):** hyväksyttiin kanavakohtaisen tarkistusyrityksen vähimmäistiedoiksi ajankohta, tulos, tieto uuden tai tehtävän kannalta relevantin sisällön löytymisestä, saatavilla oleva tekninen tulos sekä virhe- ja huomiotiedot. Erotettiin teknisen tarkistuksen onnistuminen sisällöllisestä tuloksesta. Tarkka kenttärakenne ja sallitut tulosarvot jätettiin avoimiksi. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.3.75 (23.11.2026):** hyväksyttiin Lähdetarkistukset-ryhmän alustava kolmen osan rakenne: käytetyt lähteet, käytetyt sisältökanavat sekä kanavakohtaiset tarkistusyritykset tuloksineen. Rekisterin ulkopuoliset lähteet kuvataan erillisinä toimituskohtaisina lähteinä; tarkat kentät ja tulosluokat jätettiin jatkokeskusteluun. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.3.74 (23.11.2026):** hyväksyttiin Tuottajan tulos -ryhmän kentiksi `status`, `started_at` ja `completed_at`. Määriteltiin tuottajan tulostilan sallitut arvot, aikaleimojen esitystapa ja tuottajan tuloksen erottaminen vastaanottajan ajonhallintatiedoista.
- **0.3.73 (23.11.2026):** hyväksyttiin toimitusmetatietojen Tehtävän kuvaus -ryhmän ainoaksi omaksi kentäksi `period`, joka sisältää seurannan alku- ja loppuarvot tehtäväpyynnön rakennetta vastaavasti. `topic_id` ja `task_type` säilyvät vain Tunnisteet ja versiot -ryhmässä.
- **0.3.72 (23.11.2026):** hyväksyttiin tuottajan toimitusmetatietojen tunnisteet ja versiot -ryhmän kentät: `schema_version`, `run_id`, `delivery_id`, `topic_id`, `task_type`, `software_revision` ja `instance_revision`. Täsmennettiin tunnisteiden omistajuus sekä rajattiin vastaanottajan `attempt_id` tuottajan metatietojen ulkopuolelle. Muiden tietoryhmien kentät jäivät avoimiksi. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.3.71 (23.11.2026):** hyväksyttiin tuottajan toimitusmetatietojen kuusi sisällöllistä tietoryhmää: tunnisteet ja versiot, tehtävän kuvaus, tuottajan tulos, lähdetarkistukset, havainnot ja laadunvarmistus sekä valinnaiset tuottajan tiedot. Ryhmittely ei lukitse vielä yksittäisiä kenttiä, niiden nimiä, tyyppejä tai pakollisuutta; aiemmin hyväksytyt vähimmäistiedot säilyvät lähtökohtana. Vastaanottajan käsittelytilat rajattiin tuottajan metatietojen ulkopuolelle. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.3.70 (23.11.2026):** hyväksyttiin tuottajan toimitusmetatietojen, vastaanottajan kanonisen ajotietueen ja vastaanottajan append-only-tapahtumahistorian erottaminen kolmeksi toisiinsa viitatuksi tietokokonaisuudeksi sekä ehdotettu `runs/{run_id}/`-hakemistorakenne (`run.json`, `events.jsonl` ja toimituskohtainen `metadata.json`). Tarkat kentät, tapahtumatyypit ja viittaukset jätettiin avoimeksi tekniseen suunnitteluun. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.3.69 (23.11.2026):** päivitettiin avoimien teknisten yksityiskohtien luettelo vastaamaan hyväksyttyjä ratkaisuja. Poistettiin vanhentunut tallennuksen palautumista koskeva avoin kohta ja täsmennettiin, että palautumisen periaatteet sekä toimitusten tunnistemalli on jo hyväksytty. Ryhmiteltiin jäljellä olevat kymmenen kokonaisuutta selkeämmin. Korjattiin vaatimusmäärittelyn perustaksi versio 0.12.27. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.3.68 (23.11.2026):** hyväksyttiin erilliset `run_id`-, `delivery_id`- ja `attempt_id`-tunnisteet, deterministinen RSS-GUIDin muodostaminen `run_id`-tunnisteesta (myöhemmin korvattu versiolla 0.3.102 vastaanottajan luomalla UUIDv4-tunnisteella), vastaanottajan laskema SHA-256-tiiviste kanonisoidusta toimitussisällöstä sekä kaksois- ja ristiriitaisten toimitusten käsittelysäännöt. Täsmennettiin vaihtoehtoisen toimituksen hyväksymisen rajat ennen ajon päättämistä. Toteutusta, skeemoja tai automaatioita ei muutettu.
- **0.3.67 (23.11.2026): hyväksyttiin RSS-julkaisujen ja kanonisten ajotietueiden sijoittaminen samaan instanssirepositorioon ja niiden päivittäminen yhdellä atomisella Git-commitilla. Määriteltiin palautuminen tilanteista, joissa tallennus epäonnistuu tai työnkulku keskeytyy commitin jälkeen, samaan `run_id`- ja toimitustunnisteeseen perustuva idempotentti uudelleenyritys, yrityskohtaisten tapahtumien append-only-säilytys, ristiriitaisten tunnisteiden käsittely sekä myöhäisen toimituksen rajattu jälkikäsittely. RSS ja ajotietue säilyvät erillisinä tiedostoina ja tietokokonaisuuksina; toteutusta tai automaatioita ei muutettu.
- **0.3.66 (23.11.2026):** hyväksyttiin yhteisen tarkistustyönkulun kiinteäksi tarkistusväliksi 15 minuuttia. Erotettiin se edelleen aihe- ja tehtävätyyppikohtaisista suoritusväleistä ja kirjattiin GitHub Actionsin ajastusviiveiden sekä yksittäisten käynnistymättä jäämisten mahdollisuus. Nykyisiä automaatioita tai niiden ajastuksia ei muutettu.
- **0.3.64 (23.11.2026):** hyväksyttiin rekisterin ulkopuolisten lähteiden haun ja rekisteröinnin erilliset asetukset, niiden periytyminen ja ylikirjoitus, muuttumaton `instance_revision`-snapshot, ajon jälkeinen ehdotusten käsittely, automaattisen rekisteröinnin validointi ja duplikaattien esto sekä `unassessed`-luokitus ja lähteen alkuperä-/löytämistietojen säilyttäminen. Skeemoja, toteutusta tai tikettejä ei luotu.
- **0.3.63 (23.11.2026):** hyväksyttiin yhteisen lähderekisterin ja sisältökanavien tarkempi rakenne, lähde- ja kanavatunnisteiden yksilöllisyys, lähde- ja kanavatason tekniset tiedot, tehtävätyypin oletus- ja pakolliset lähde–kanava-parit sekä aihekohtaiset `inherit`-, `extend`- ja `replace`-toimintatavat, niiden järjestys- ja yhdistämissäännöt ja validointiperiaatteet. Raportintuottajan lähderekisterin ulkopuolinen lähdehaku ja uusien lähteiden rekisteröinti jätettiin avoimeksi. Skeemoja tai toteutusta ei luotu tässä suunnittelumuutoksessa.
- **0.3.62 (23.11.2026):** hyväksyttiin JSON Schema Draft 2020-12 -skeemakokonaisuuden hakemistorakenne ja vastuut, yhteiset osaskeemat, skeemojen paikallinen viittausmalli ja semanttinen versiointi, tuntemattomien kenttien hylkääminen, rakenteellisen ja toiminnallisen validoinnin vaiheistus, virheiden raportointi, Markdown-ohjeiden erilliset tarkistukset, kiinnitetty validointikirjasto sekä skeemojen ja määritysten kattavat testausperiaatteet. Skeematiedostoja tai validointitoteutusta ei luotu tässä suunnittelumuutoksessa.
- **0.3.61 (23.11.2026):** hyväksyttiin teknisen saavutettavuuden tietojen jako lähde-, kanava- ja ajohistoriatasolle. Lähdetaso kuvaa julkaisijan tai verkkopalvelun yleisiä teknisiä ominaisuuksia ja rajoitteita, kanavataso yksittäisen sisältövirran ominaisuuksia, ja ajohistoria toteutuneita tarkistustuloksia. Pysyvää, nopeasti vanhenevaa saavutettavuusarvosanaa ei ylläpidetä.
- **0.3.60 (23.11.2026):** hyväksyttiin lähteen valinnainen oletusaikavyöhyke ja sen määrityksen peruste sekä sisältökanavan tarkempi aikavyöhykemääritys. Sisällön oma aikaleima tai tapahtumapaikan aikavyöhyke on ensisijainen, kun se on luotettavasti tiedossa.
- **0.3.59 (22.11.2026):** täsmennettiin yhteisen lähderekisterin tukevan saman lähteen erillisiä sisältökanavia omine vakaine tunnisteineen ja osoitteineen. Kanavat voidaan valita ja arvioida tehtäväkohtaisesti erikseen; tarkka skeemarakenne jätettiin skeemasuunnitteluun.
- **0.3.58 (22.11.2026):** hyväksyttiin yhteinen lähderekisteri, tehtävätyypin oletuslähteet ja mahdolliset pakolliset lähteet sekä aiheen ja tehtävätyypin yhdistelmäkohtaiset lähdemääritykset. Määriteltiin `inherit`-, `extend`- ja `replace`-toimintatavat ja pakollisten lähteiden säilyminen myös oletuslistan korvaamisessa.

- **0.3.57 (22.11.2026):** määriteltiin JSON Schema Draft 2020-12 -skeemakokonaisuus, tehtävätyyppikohtaiset asetusskeemat, tehtävätyyppiin sidotut profiilit, Markdown-ohjeiden erillinen validointi ja tehtäväpyynnön rakenteisten aineistojen `inputs`-viittaukset. Lähderekisterin aihekohtainen rajaus jätettiin avoimeksi jatkokeskusteluun.

- **0.3.56 (22.11.2026):** yhdenmukaistettiin tehtäväpyynnön ohjejärjestys ja aikavälin puoliksi avoin tulkinta yhteisen peruspromptin sekä raportointijaksojen rajojen osalta.

- **0.3.55 (22.11.2026):** lisättiin ohjelmistorepoon kuuluva yhteinen raportintekijän perusprompti ja sen ohjeviittausten järjestys, tehtäväpyynnön aikavälin puoliksi avoin tulkinta, kanonisen ajotietueen säilyvän tapahtumahistorian periaatteet sekä lähdekohtaiset avausyritystilastot ja Valvomon lähdenäkymä. Ajotietueiden hakemistorakenne jätettiin avoimeksi; lähteiden automaattista käytöstä poistamista ei sallita pelkkien tilastojen perusteella.

- **0.3.54 (22.11.2026):** määriteltiin kolmitasoinen määritysmalli ja sen yhdistämisjärjestys, suojatut asetukset, erillinen skeema- ja oletusarvovastuu, yksittäisten ja yhdistettyjen määritysten validointi sekä muuttumaton `resolved_config`-snapshot. Täsmennettiin virheellisten määritysten käsittely ja rajattiin rekursiiviset profiiliriippuvuudet sekä dynaamiset yhdistämismekanismit pois.

- **0.3.53 (22.11.2026):** määriteltiin käsittelyn valmistuminen ja aktiivisen tehtävän vapauttaminen. Tuottajan tulos, vastaanottajan käsittely ja ajon lopputila erotettiin. Uudelleenyritysten määrät ja muut vastaavat käsittelyrajat määriteltiin konfiguroitaviksi, eikä niitä kovakoodata.

- **0.3.52 (22.11.2026):** hyväksyttiin tehtäväpyynnön täsmällinen ylätason rakenne ja kenttäkohtaiset tietovaatimukset. Täsmennettiin profiiliviittaukset objekteiksi, joissa ovat id, repository ja path, ohjeviittausten sallitut repositoriot, lowercase-commit-SHA-muoto sekä tuntemattomien ylimääräisten kenttien hylkääminen.

- **0.3.51 (22.11.2026):** hyväksyttiin myöhäisen toimituksen vastaanottokäsittelyn esittäminen erillisinä, aikajärjestyksessä säilyvinä tapahtumina. Tapahtumaketju kattaa määräajan ylityksen, myöhäisen vastaanoton, validoinnin, hyväksynnän/hylkäyksen ja mahdollisen julkaisun; aiempia tapahtumia ei ylikirjoiteta.

- **0.3.50 (22.11.2026):** täsmennettiin myöhäisen hyväksytyn toimituksen suhde jo muodostettuun kanoniseen ajotietueeseen: toimitus täydentää tietuetta erillisenä tuottajan tuloksena eikä korvaa vastaanottajan aiempia määräajan ylityksen ja toimituksen puuttumisen havaintoja.

- **0.3.49 (22.11.2026):** määriteltiin myöhäisen toimituksen rajattu jälkikäsittely alkuperäisen `run_id`-tunnisteen perusteella. Julkaisu sallitaan vain, jos myöhempää saman aiheen ja seurantatyypin ajoa ei ole käynnistetty; myöhäinen toimitus ei muuta myöhempien ajojen tietoja tai tiloja.

- **0.3.48 (22.11.2026):** yhtenäistettiin vaatimusmäärittelyn kanssa tehtävän muodostuksen, määräajan valvonnan ja toimituksen vastaanoton yhteinen sarjallisuusvaatimus.

- **0.3.47 (22.11.2026):** täsmennettiin, että tehtävän muodostus, määräajan valvonta ja toimituksen vastaanotto/käsittely kuuluvat yhteisen instanssikohtaisen sarjallisuuden hallinnan piiriin. Tekninen koordinointitapa jätettiin myöhempään suunnitteluun.

## 7. Hyväksymismenettely

Tämä dokumentti täydentyy teknisten yksityiskohtien ratkaisun perusteella. Uusi toteutus suunnitellaan ja rakennetaan puhtaalta pöydältä; vanhaa arkistoitua toteutusta ei käytetä lähtökohtana. Käyttäjä tarkistaa ja hyväksyy toteutussuunnitelman kokonaisuutena ennen tikettien luomista.

Toteutussuunnitelman hyväksyminen, tikettien luominen, toteutuksen aloittaminen ja tuotantoon siirtyminen ovat erillisiä vaiheita. Nykyisten automaatioiden ajastuksia, ohjeita, kehotteita tai kohdekeskusteluja ei muuteta ilman erillistä lupaa.
