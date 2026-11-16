# Järjestelmän viikoittaisen laatutarkistuksen käsikirja

Ohjeversion tunniste: 1.0.0

## 1. Tehtävä ja rajaus

Tämä on automaation **Viikoittainen järjestelmän laatutarkistus** täydellinen ja ensisijainen tehtäväkuvaus. ChatGPT-automaation asetuksissa käytetään vain lyhyttä käynnistyskehotetta, joka hakee tämän käsikirjan GitHubista.

Tarkista `mikknikk/uutiset` kerran viikossa ajon aikana luetun main-haaran ja GitHub Actions -ajojen perusteella. Älä nojaa vanhoihin keskusteluihin tai oletuksiin.

Tämä on auditointi, ei korjaava ylläpito. Älä muuta RSS-syötteitä, dokumentaatiota, skriptejä, työnkulkuja, automaatioita tai asetuksia äläkä tee korjaavia committeja, issueita tai pull requesteja. Ainoa sallittu repository-kirjoitus on tämän käsikirjan version ja onnistuneen tarkistuksen aikaleiman kirjaaminen `data/seurantatila.json`-tiedoston `quality_check_instructions`-osioon kohdan 8 mukaisesti. Älä muuta saman JSONin muita kenttiä.

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
- `data/seurantatila.json`, `data/naytosten-muutoshistoria.json`, `data/lahderekisteri.json` ja `data/lahdetarkistukset.json`
- kaikki `feeds/*.xml`-syötteet
- `scripts/validate_feeds.py`
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
- Vertaa ajolokin tarkistettuja ja tarkistamatta jääneitä lähteitä rekisteriin. Etsi puuttuvia kriittisiä lähteitä, tuntemattomia ID:itä ja virheellisiä `latest_by_task`-arvoja.
- Arvioi kieli- ja maantieteelliset puutteet erikseen; älä päättele kattavuutta pelkästä lähteiden määrästä.
- Varmista, että uutisraportin ja erillisen näytösvahdin intialaiset lähteet pysyvät eri tehtävätunnisteiden alla.

### 4.4 Koneellinen tila ja historia
- Tarkista JSON-rakenne, pakolliset kentät ja aikaleimojen ISO 8601 -muoto aikavyöhykkeineen.
- Varmista, että yhdeksän aiheen kierto vastaa `docs/tehtavajono.md`:tä ja seuraava tehtävä täsmää JSONin kanssa.
- Varmista, että näytösvahti on erillinen eikä muuta kiertoa.
- Tarkista näytösseurannan tila, `data/naytosten-muutoshistoria.json` ja `schemas/naytosten-muutoshistoria.schema.json`. `pending_first_verified_run` on hyväksyttävä vain, jos lähtötila on dokumentoidusti vielä muodostamatta ja `screenings` sekä `events` ovat tyhjiä; aktiivisessa tilassa pitää olla täsmälleen yksi `baseline_created`-tapahtuma. Varmista, että GitHub Actions suorittaa JSON Schema -validoinnin.
- Älä hyväksy arvattuja aikaleimoja tai historiatapahtumia.
- Tarkista pääautomaation, näytösvahdin ja laatutarkistuksen ohjeversioiden vastaavuus.

### 4.4 Dokumentaation yhdenmukaisuus
Vertaa README:tä, tehtäväjonoa, seurantadokumentteja, aihekohtaisia ohjeita ja automaatioiden työnjakoa. Pääkierto käsittelee yhden yhdeksästä tehtävästä päivässä; näytösvahti on erillinen päivittäinen tehtävä eikä kuluta kiertovuoroa. Uutis- ja näytös-RSS:t sekä seurantalokit eivät saa sekoittua. Etsi ristiriitaiset, vanhentuneet, päällekkäiset ja puuttuvat ohjeet.

### 4.5 Saavutettavuus
Tarkista `docs/saavutettavuus.md`:n huomiointi, otsikkohierarkia, linkkitekstit, alt-tekstit, kielimääritykset, kontrasti ja mobiilikäyttö siltä osin kuin aineisto mahdollistaa. Älä väitä WCAG 2.2 AAA -vaatimustenmukaisuutta ilman kattavia testituloksia. Erota automaattisesti tarkistetut asiat manuaalisesti tarkistamattomista.

### 4.6 Lähteet ja sisältö
Tarkista puuttuvat lähteet ja syötteet, lähdelinkkien ilmeiset virheet, epäselvät seurantajaksot, duplikaatit ja raporttien sisällölliset poikkeamat. Älä keksi testituloksia, lähteitä, linkkejä, päivämääriä tai tarkistusaikoja. Merkitse saavuttamattomat kohteet tarkistamatta jääneiksi; älä luokittele niitä automaattisesti virheiksi.

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

## 6. Onnistumisehto

Auditointi on onnistunut, kun kaikki pakolliset kohteet on tarkastettu eikä mikään olennainen kohde jää pääsyrajoitteen vuoksi huomaamatta. Jos keskeinen lähde tai GitHub Actions -tulos jäi lukematta, auditointi on keskeneräinen eikä onnistumisaikaa päivitetä. Repositoryn löydökset eivät itsessään tee auditoinnista epäonnistunutta: kattavasti tehty auditointi on onnistunut suoritus, vaikka se löytäisi ongelmia.

## 7. Älä korjaa havaintoja

Älä muuta repositoryn tiedostoja muuten kuin kohdan 8 rajatulla seurantamerkinnällä. Älä muuta automaatioita, ajastuksia, GitHub-asetuksia tai käyttöoikeuksia. Älä tee korjaavia committeja, issueita tai pull requesteja ilman erillistä pyyntöä.

## 8. Ohjeversion ja onnistuneen ajon seuranta

`data/seurantatila.json` sisältää `quality_check_instructions`-olion:
- `document`: tämän käsikirjan polku
- `current_version`: käsikirjan MAJOR.MINOR.PATCH-versio
- `last_successful_run_version`: viimeisimmän kattavan auditoinnin käyttämä versio
- `last_successful_run_at`: saman auditoinnin ISO 8601 -aikaleima aikavyöhykkeineen.

Vasta onnistuneen auditoinnin jälkeen päivitä kaksi viimeistä kenttää. Säilytä JSONin kaikki muut kentät täsmälleen ennallaan ja hae tiedosto takaisin GitHubista varmistaaksesi muutoksen. Keskeneräinen ajo ei muuta onnistumistietoja.

Käsikirjan muutoksen yhteydessä kasvata versionumeroa semanttisesti ja päivitä `quality_check_instructions.current_version` samassa muutossarjassa. Älä muuta viimeisimmän onnistuneen ajon kenttiä etukäteen.

## 9. Ylläpidon periaate

Tämä käsikirja on laatutarkistuksen ainoa ensisijainen tehtävä- ja toimintakuvaus. Automaation asetuksissa on vain lyhyt käynnistyskehote. README ja validator tarkistavat käsikirjan olemassaolon, version ja JSONin versionvastaavuuden.
