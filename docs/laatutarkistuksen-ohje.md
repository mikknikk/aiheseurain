# Järjestelmän viikoittaisen laatutarkistuksen käsikirja

Ohjeversion tunniste: 1.0.7

## 1. Tehtävä ja rajaus

Tämä on automaation **Viikoittainen järjestelmän laatutarkistus** täydellinen ja ensisijainen tehtäväkuvaus. ChatGPT-automaation asetuksissa käytetään vain lyhyttä käynnistyskehotetta, joka hakee tämän käsikirjan GitHubista.

Tarkista `mikknikk/aiheseurain` kerran viikossa ajon aikana luetun main-haaran ja GitHub Actions -ajojen perusteella. Älä nojaa vanhoihin keskusteluihin tai oletuksiin.

Tämä on auditointi, ei korjaava ylläpito. Älä muuta RSS-syötteitä, skriptejä, työnkulkuja, automaatioita tai asetuksia äläkä tee korjaavia issueita tai pull requesteja. Älä korjaa löydöksiä itse. Sallitut main-haaran repository-kirjoitukset ovat vain (1) tämän käsikirjan version ja onnistuneen tarkistuksen aikaleiman kirjaaminen `data/seurantatila.json`-tiedoston `quality_check_instructions`-osioon kohdan 8 mukaisesti sekä (2) auditointiraportin lisääminen `reports/laatutarkistukset/`-hakemistoon kohdan 5 mukaisesti. Älä muuta saman JSONin muita kenttiä.

## 1.1. Ajastusten ja asetusten hallinnan suojaus

Noudata kaikkia Aiheseurainin automaatioita koskevaa [hallintaperiaatetta](automaation-hallintaperiaatteet.md). Laatutarkistuksen suorittaminen ei anna lupaa muuttaa tämän tai muiden automaatioiden ajastusta, aktiivisuutta, aikataulua, käynnistysohjetta, muita asetuksia tai kohdekeskustelua. Auditoinnissa havaitut ongelmat raportoidaan käyttäjälle; niitä ei korjata muuttamalla ajastuksia tai asetuksia. GitHubiin tehty auditointiraportti tai seurantatilan päivitys ei muuta ChatGPT:n tehtäväasetuksia.

## 2. Ajon alun esitarkistus

Lue GitHubista ennen auditointia:
1. `README.md`
2. tämä käsikirja kokonaan
3. `data/seurantatila.json`
4. `docs/tehtavajono.md`
5. `docs/seuranta.md`
6. `docs/saavutettavuus.md`
7. `docs/kehityskaytannot.md`
8. `docs/kehityskohteet.md`

Tarkista, että käsikirjan versionumero vastaa JSONin `quality_check_instructions.current_version`-arvoa ja että `document` osoittaa tähän tiedostoon. Jos jokin esitarkistuksen tiedosto puuttuu, ei ole luettavissa tai versiot eivät täsmää, keskeytä ilman auditointia ja onnistumistietojen muuttamista.

## 3. Tarkastettavat kohteet

Tarkasta ajantasainen main-haara. Tarkastele vähintään:
- README, tehtäväjono ja kaikki seuranta-, lähde-, aihe- ja kehitysohjeet
- `data/seurantatila.json`, `data/naytosten-muutoshistoria.json`, `data/source-catalog.json`, kaikki `data/sources/*.json`-tehtävärekisterit ja `data/lahdetarkistukset.json`
- kaikki `feeds/*.xml`-syötteet
- `scripts/validate_feeds.py` ja sen käyttämä `scripts/validate_source_coverage.py` sekä niiden käyttämät JSON Schema -skeemat, erityisesti `schemas/lahdekatalogi.schema.json`, `schemas/lahderekisteri.schema.json` ja `schemas/lahdetarkistukset.schema.json`
- kaikki `.github/workflows/`-työnkulut
- GitHub Actions -ajojen viimeisin tila ja tarvittaessa aiemmat ajot toistuvien virheiden löytämiseksi.

Ota mukaan myös uudet vastaavat tiedostot, jos niitä on lisätty. Älä rajaa tarkastusta vain vanhaan tiedostoluetteloon.

## 4. Pakolliset laatutarkistukset

### 4.1 GitHub Actions ja testit
- Selvitä olennaisten työnkulkujen viimeisin ajo, tulos, ajankohta ja virheet.
- Etsi toistuvat epäonnistumiset, ohitetut vaiheet ja testit, joita ei tosiasiassa suoritettu.
- Älä tulkitse vihreää työnkulkua faktatarkkuuden tai saavutettavuuden täydelliseksi todisteeksi.

### 4.2 RSS-syötteet
Tarkista jokaisesta syötteestä XML/RSS-rakenne, GUIDien olemassaolo ja yksilöllisyys kaikkien syötteiden välillä, CDATA-kuvaukset, item-tason `<link>`-elementtien puuttuminen, lähdeluetteloiden olemassaolo, kuvausten sisäisen HTML:n rakenne, kelvolliset linkit, alt-tekstit, otsikkotasot, aiherajaus, duplikaatit sekä tyhjät, virheelliset tai vanhentuneet raportit. Älä muokkaa syötteitä.

### 4.3 Koneellinen tila, lähderekisteri ja ajoloki
- Tarkista lähderekisterin pysyvät ID:t, URL:t, tehtävärajaukset, kieli-/aluekuvaukset ja kriittisyysmerkinnät.
- Vertaa uusien ajolokimerkintöjen `checked_source_ids`- ja `unchecked_sources`-luetteloita `registry_source_ids`-kenttään; näiden joukkojen pitää vastata toisiaan täsmälleen. Vertaa `registry_source_ids`-kenttää kyseisen ajon lähderekisteriin ja tarkista tuntemattomat ID:t sekä virheelliset `latest_by_task`-arvot. Vanhoissa ajomerkinnöissä, joilta `registry_source_ids` puuttuu, älä oleta nykyisen rekisterin vastaavan ajonaikaista rekisteriä. Tarkista lähderekisterin `updated_at`, ajon aikaleimat ja Git-historia, jos saatavilla; jos alkuperäistä lähdejoukkoa ei voi varmistaa, kirjaa se historialliseksi epävarmuudeksi äläkä luokittele lähteitä puuttuviksi ilman näyttöä.
- Arvioi kieli- ja maantieteelliset puutteet erikseen; älä päättele kattavuutta pelkästä lähteiden määrästä.
- Varmista, että uutisraportin ja erillisen näytösvahdin intialaiset lähteet pysyvät eri tehtävätunnisteiden alla.

### 4.4 Koneellinen tila ja historia
- Tarkista JSON-rakenne, pakolliset kentät ja aikaleimojen ISO 8601 -muoto aikavyöhykkeineen.
- Varmista, että yhdeksän aiheen kierto vastaa `docs/tehtavajono.md`:tä ja seuraava tehtävä täsmää JSONin kanssa.
- Varmista, että näytösvahti on erillinen eikä muuta kiertoa.
- Tarkista näytösseurannan tila, `data/naytosten-muutoshistoria.json` ja `schemas/naytosten-muutoshistoria.schema.json`. `pending_first_verified_run` on hyväksyttävä vain, jos lähtötila on dokumentoidusti vielä muodostamatta ja `screenings` sekä `events` ovat tyhjiä; aktiivisessa tilassa pitää olla täsmälleen yksi `baseline_created`-tapahtuma. Varmista, että GitHub Actions suorittaa JSON Schema -validoinnin.
- Älä hyväksy arvattuja aikaleimoja tai historiatapahtumia.
- Tarkista pääautomaation, näytösvahdin ja laatutarkistuksen ohjeversioiden vastaavuus.

### 4.5 Dokumentaation yhdenmukaisuus
Vertaa README:tä, tehtäväjonoa, seurantadokumentteja, aihekohtaisia ohjeita ja automaatioiden työnjakoa. Pääkierto käsittelee yhden yhdeksästä tehtävästä päivässä; näytösvahti on erillinen päivittäinen tehtävä eikä kuluta kiertovuoroa. Uutis- ja näytös-RSS:t sekä seurantalokit eivät saa sekoittua. Etsi ristiriitaiset, vanhentuneet, päällekkäiset ja puuttuvat ohjeet.

### 4.6 Saavutettavuus
Tarkista `docs/saavutettavuus.md`:n huomiointi, otsikkohierarkia, linkkitekstit, alt-tekstit, kielimääritykset, kontrasti ja mobiilikäyttö siltä osin kuin aineisto mahdollistaa. Tarkista myös manuaalisten testien kirjaukset, ympäristöt, tulokset ja avoimet löydökset. Jos kirjauksia ei ole, ilmoita manuaalinen testaus tekemättömäksi; tyhjä testipohja ei ole testitulos. Älä väitä WCAG 2.2 AAA -vaatimustenmukaisuutta ilman kattavia testituloksia. Erota automaattisesti tarkistetut asiat manuaalisesti tarkistamattomista.

### 4.7 Kehitysjonon tikettien tilalabelit

Tarkista jokaisesta tarkasteluun kuuluvasta avoimesta ja hiljattain suljetusta tiketistä GitHub-tilan, toteutuneiden PR:ien ja `tila:*`-labelin vastaavuus. Kanoninen tilamalli ja käsittelysäännöt ovat [kehityssuunnitelman kohdissa 4.2 ja 4.2.1](kehityssuunnitelma.md).

Tarkista erityisesti:
- aktiivisesti toteutettava avoin tiketti on `tila:in-progress`;
- toteutuksen aloittamista odottava, määrittelyltään valmis avoin tiketti on `tila:ready`;
- estynyt työ on `tila:blocked` ja este on kuvattu;
- vielä määrittelyä tai päätöstä odottava avoin työ on `tila:backlog`;
- toteutettu ja hyväksymiskriteerien mukaisesti varmennettu sekä yhdistetty työ on suljettu ja merkitty `tila:done`;
- tiketillä on täsmälleen yksi `tila:*`-label, eikä vanhaa tilalabelia ole jäänyt uuden rinnalle;
- tiketin tilaa ei ole merkitty valmiiksi pelkän PR:n avaamisen tai keskeneräisen työhaaratyön perusteella.

Kirjaa raporttiin ristiriidat, puuttuvat tai moninkertaiset tilalabelit sekä niiden täsmälliset issue-linkit. Erota todettu ristiriita tilanteesta, jossa tiketin aktiivista käsittelyä ei voida päätellä luotettavasti. Älä muuta tilalabeleita tämän auditointikohdan perusteella omin päin: sallitut automaattiset muutokset rajautuvat erikseen dokumentoituihin kehitysjonon auditoinnin sääntöihin ja niitä toteuttaviin hyväksyttyihin tiketteihin (esimerkiksi #62 ja #63). Muiden ristiriitojen korjaus jää toteuttajalle tai käyttäjän päätettäväksi.

Kun laatutarkistus itse ottaa tiketin toteutukseen, sen on noudatettava samaa työn aloitus- ja valmistumissääntöä kuin muunkin toteutustyön yhteydessä. Pelkkä auditointi ei kuitenkaan tarkoita, että kaikki havaitut tiketit otetaan työn alle.

### 4.9 Nimen kirjoitusasu ja taivutus

Tarkista koko repositorion käyttäjälle näkyvä suomenkielinen sisältö, mukaan lukien README, dokumentaatio, verkkosivujen tekstit, RSS-syötteet ja raportit, Aiheseurain-nimen oikean kirjoitusasun ja taivutuksen osalta.

Nimen perusmuoto on **Aiheseurain** ja genetiivi **Aiheseuraimen**. Nimeä taivutetaan vartalolla *Aiheseuraime-*, esimerkiksi *Aiheseuraimen*, *Aiheseuraimessa* ja *Aiheseuraimelle*. Muotoa *Aiheseurainin* ei käytetä. Tarkista myös muut mahdolliset virheelliset taivutusmuodot asiayhteyden perusteella.

Kirjaa löydetyt virheet raporttiin täsmällisine tiedostopolkuineen ja riveineen sekä ehdota oikeaa muotoa. Älä muuta tiedostoja laatutarkistuksen yhteydessä; korjaukset tehdään erillisessä hyväksytyssä muutoksessa. Älä merkitse virhettä, jos kyse on kirjaimellisesta esimerkistä, jossa väärä muoto on nimenomaan dokumentoitu vältettäväksi muodoksi.

### 4.8 Lähteet ja sisältö
Tarkista puuttuvat lähteet ja syötteet, lähdelinkkien ilmeiset virheet, epäselvät seurantajaksot, duplikaatit ja raporttien sisällölliset poikkeamat. Tarkista viimeisin viikoittaisen linkkitarkistuksen artefakti, jos se on saatavilla. Erota 404/410-virheet uudelleenohjauksista, estetyistä pyynnöistä (401/403), nopeusrajoituksista (429), palvelinvirheistä ja verkkoyhteysongelmista. Älä tulkitse estettyä tai tilapäisesti saavuttamatonta sivua automaattisesti rikkinäiseksi. Jos tarkistus tai artefakti puuttuu, kirjaa se tarkistamatta jääneeksi. Älä keksi testituloksia, lähteitä, linkkejä, päivämääriä tai tarkistusaikoja.

## 5. Raportointi

Toimita jokaisella viikoittaisella ajolla suomenkielinen raportti, myös silloin kun kaikki on kunnossa. Raportissa on:
1. tarkistuksen päivämäärä ja kellonaika (Europe/Helsinki)
2. tarkastetut ja tarkistamatta jääneet kohteet
3. läpäistyt tarkistukset
4. ongelmat vakavuusjärjestyksessä (kriittinen, korkea, keskitaso, matala)
5. epävarmuudet ja testauksen rajat
6. suositellut korjaukset
7. täsmälliset GitHub-linkit havaintoihin ja lähteisiin.

Jos ongelmia ei löydy, sano se selvästi ja kerro mitä tarkistettiin. Erota todellinen virhe, kehitysehdotus ja pääsyrajoite.

### 5.1 Raporttien tallentaminen

Tallenna jokaisen raportointivaiheeseen edenneen auditointiajon raportti repositorion hakemistoon `reports/laatutarkistukset/`. Raportti on Markdown-tiedosto, jonka nimi muodostetaan ajon paikallisesta alkamis-/valmistumisajasta muodossa `YYYY-MM-DDTHHMMSS+ZZZZ.md`, esimerkiksi `2026-11-16T204020+0200.md`. Käytä aikaleimaa `Europe/Helsinki`-aikavyöhykkeellä. Jos samalle aikaleimalle on jo tiedosto, älä ylikirjoita sitä: lisää tiedostonimeen juokseva järjestysnumero (`-02`, `-03` jne.).

Jokaisessa raportissa on:
- auditoinnin tila: onnistunut, keskeneräinen tai keskeytetty
- päivämäärä, aikaleima ja käytetty käsikirjan versio
- tarkastuksen kattavuus sekä tarkistetut ja tarkistamatta jääneet kohteet
- läpäistyiksi todetut tarkistukset; älä päättele niitä pelkästä auditoinnin onnistumisesta
- löydökset vakavuusjärjestyksessä sekä niiden tila (uusi, avoin, korjattu tai suljettu)
- epävarmuudet, puuttuvat tiedot ja testauksen rajat
- suositellut jatkotoimet sekä täsmälliset linkit, jos ne ovat tiedossa.

Kirjaa vain ajon aikana todennetut tiedot. Jos tietoa ei ole saatavilla, sano se suoraan; älä täydennä raporttia arvaamalla. Merkitse ensimmäisessä raportissa löydökset uusiksi. Seuraavissa raporteissa seuraa aiempia löydöksiä niiden tunnisteen tai yksiselitteisen otsikon avulla. Älä muokkaa tai poista vanhoja raportteja jälkikäteen: korjaantuminen ja tilan muutos kirjataan seuraavaan raporttiin.

Myös keskeneräinen tai keskeytynyt auditointi voidaan raportoida, jos raportointiin on riittävästi varmennettua tietoa. Tällaisen raportin tila on ilmoitettava selvästi, eikä se oikeuta onnistumistietojen päivittämiseen.

## 6. Onnistumisehto

Auditointi on onnistunut, kun kaikki pakolliset kohteet on tarkastettu eikä mikään olennainen kohde jää pääsyrajoitteen vuoksi huomaamatta. Jos keskeinen lähde tai GitHub Actions -tulos jäi lukematta, auditointi on keskeneräinen eikä onnistumisaikaa päivitetä. Repositoryn löydökset eivät itsessään tee auditoinnista epäonnistunutta: kattavasti tehty auditointi on onnistunut suoritus, vaikka se löytäisi ongelmia.

## 7. Älä korjaa havaintoja

Älä muuta repositoryn tiedostoja muuten kuin kohdan 5.1 raportin lisäämisellä ja kohdan 8 rajatulla seurantamerkinnällä. Älä korjaa havaintoja, muuta automaatioita, ajastuksia, GitHub-asetuksia tai käyttöoikeuksia. Älä tee korjaavia issueita tai pull requesteja ilman erillistä pyyntöä.

## 8. Ohjeversion ja onnistuneen ajon seuranta

`data/seurantatila.json` sisältää `quality_check_instructions`-olion:
- `document`: tämän käsikirjan polku
- `current_version`: käsikirjan MAJOR.MINOR.PATCH-versio
- `last_successful_run_version`: viimeisimmän kattavan auditoinnin käyttämä versio
- `last_successful_run_at`: saman auditoinnin ISO 8601 -aikaleima aikavyöhykkeineen.

Vasta onnistuneen auditoinnin jälkeen päivitä kaksi viimeistä kenttää. Säilytä JSONin kaikki muut kentät täsmälleen ennallaan ja hae tiedosto takaisin GitHubista varmistaaksesi muutoksen. Keskeneräinen tai keskeytynyt ajo ei muuta onnistumistietoja. Lisää raportti saman auditointiajon muutossarjaan; onnistuneen auditoinnin raportti ja onnistumistietojen päivitys julkaistaan yhdessä normaalin PR- ja CI-prosessin kautta. Raportti kirjataan sillä käsikirjan versiolla, jota auditoinnissa tosiasiassa käytettiin. Jos käsikirjan versio muuttuu raporttia laadittaessa, älä merkitse uutta versiota jo suoritetun auditoinnin käyttämäksi versioksi.

Käsikirjan muutoksen yhteydessä kasvata versionumeroa semanttisesti ja päivitä `quality_check_instructions.current_version` samassa muutossarjassa. Älä muuta viimeisimmän onnistuneen ajon kenttiä etukäteen.

## 9. Ylläpidon periaate

Tämä käsikirja on laatutarkistuksen ainoa ensisijainen tehtävä- ja toimintakuvaus. Automaation asetuksissa on vain lyhyt käynnistyskehote. README ja validator tarkistavat käsikirjan olemassaolon, version ja JSONin versionvastaavuuden.

## 10. ChatGPT-ajon vaihekohtainen ajohistoria

Noudata yhteistä [ajohistorian tietomallia](ajohistoria.md). Laatutarkistuksen historiatiedosto on haarassa `run-history/quality-check`, polussa `history.json`, ja tunniste on `quality_check`.

Kirjaa ajo heti käynnistyessä tilaan `running` yksilöllisellä ajotunnisteella. Päivitä samaa ajoa vähintään vaiheissa `preflight`, `repository_audit`, `tests_workflows`, `accessibility`, `backlog_audit`, `report`, `state_update`, `pull_request`, `ci`, `merge` ja `verification`; merkitse soveltumattomat vaiheet `skipped` vain perustellusti. Kirjaa aikaleimat, tulokset, lyhyet virheet ja varoitukset.

Ajohistorian kirjoitus tehdään vain omaan `run-history/quality-check`-haaraan GitHubin Contents APIlla tai vastaavalla käytettävissä olevalla GitHub-kirjoitustoiminnolla. Älä koskaan kirjoita ajohistoriaa `main`-haaraan äläkä tee siitä erillistä PR:ää. Jokaisen kirjoituksen jälkeen lue `history.json` samasta haarasta takaisin ja varmista ajotunniste sekä JSON-rakenne. Säilytä viimeiset 30 ajoa. Älä kirjaa salaisuuksia tai raakaa lokisisältöä.

Tämä erillinen ajohistoriahaara on ainoa lisäys laatutarkistuksen muuten vain luku -muotoiseen auditointiin. `main`-haaran sallittuja kirjoituksia koskevat rajoitukset pysyvät ennallaan: vain auditointiraportti ja onnistuneen auditoinnin kaksi sallittua metatietokenttää. Jos ajohistorian kirjoitusoikeus puuttuu tai kirjoituksen onnistumista ei voida varmistaa, raportoi rajoite äläkä väitä vaihekirjausta tallennetuksi.
