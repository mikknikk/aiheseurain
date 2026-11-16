# Uutisseuranta – yhdeksän tehtävän seurantakierto

Tämä repositorio ylläpitää yhdeksää erillistä seurantatehtävää yhdessä kiertojonossa. Yksi automaatio käynnistyy päivittäin klo 12.00 Europe/Helsinki ja käsittelee kullakin ajolla vain yhden tehtävän. Yhdeksän tehtävän kierto tarkoittaa, että kukin aihe tarkistetaan normaalisti noin yhdeksän päivän välein. Intialaisen elokuvan uutisraportti on jonon tehtävä 9. Intialaisten elokuvien näytösseuranta on erillisen päivittäisen näytösvahdin vastuulla.

## Hakemistorakenne

- `feeds/` – kaikki kymmenen RSS-syötettä (yhdeksän aihekierrossa ja yksi erilliselle näytövahdille).
- `docs/` – suomenkieliset seuranta-, lähde-, ohje- ja saavutettavuusdokumentit.
- `prompts/` – automaatioiden asetuksiin kopioitavat kanoniset käynnistyskehotteet `.txt`-tiedostoina sekä niiden ylläpito-ohje.
- `data/source-catalog.json` – kaikkien lähteiden yhteiset perustiedot kerran; `data/sources/*.json` – kymmenen tehtäväkohtaista lähdekäyttörekisteriä; `data/lahdetarkistukset.json` – ajokohtainen lähdekattavuusloki.
- `schemas/` – koneellisten lähdetietojen ja näytöshistorian skeemat.
- `docs/tehtavajono.md` – yhdeksän tehtävän kiertojärjestys ja seuraava vuoro; yleiset raportointisäännöt ovat docs/seuranta.md:ssä.
- `README.md` – repositorion aloitussivu ja kokonaiskuva.

## Syötteet

Kaikkien syötteiden ensisijainen julkinen jakeluosoite on GitHub Pages. Käytä RSS-lukijoissa ja automaatioiden julkaisemissa linkeissä `https://mikknikk.github.io/uutiset/feeds/{syötetiedosto}.xml`-osoitetta. `raw.githubusercontent.com` ei ole julkinen kanoninen RSS-osoite.

| Aihe | RSS-tiedosto | RSS-osoite (GitHub Pages) |
|---|---|---|
| J. R. R. Tolkien | [tolkien.xml](feeds/tolkien.xml) | https://mikknikk.github.io/uutiset/feeds/tolkien.xml |
| Taylor Swift | [taylor-swift.xml](feeds/taylor-swift.xml) | https://mikknikk.github.io/uutiset/feeds/taylor-swift.xml |
| Saint Dr. Gurmeet Ram Rahim Singh Ji Insan | [gurmeet-ram-rahim-singh.xml](feeds/gurmeet-ram-rahim-singh.xml) | https://mikknikk.github.io/uutiset/feeds/gurmeet-ram-rahim-singh.xml |
| Muumit | [muumit.xml](feeds/muumit.xml) | https://mikknikk.github.io/uutiset/feeds/muumit.xml |
| Wakaliwood | [wakaliwood.xml](feeds/wakaliwood.xml) | https://mikknikk.github.io/uutiset/feeds/wakaliwood.xml |
| Euroviisut ja kansalliset karsinnat | [euroviisut.xml](feeds/euroviisut.xml) | https://mikknikk.github.io/uutiset/feeds/euroviisut.xml |
| Sompote Sands | [sompote-sands.xml](feeds/sompote-sands.xml) | https://mikknikk.github.io/uutiset/feeds/sompote-sands.xml |
| Shakkidraamat | [shakkidraamat.xml](feeds/shakkidraamat.xml) | https://mikknikk.github.io/uutiset/feeds/shakkidraamat.xml |
| Intialaisen elokuvan uutisraportti | [intialaiset-elokuvat.xml](feeds/intialaiset-elokuvat.xml) | https://mikknikk.github.io/uutiset/feeds/intialaiset-elokuvat.xml |
| Intialaisten elokuvien näytökset Suomessa | [intialaisten-elokuvien-naytokset.xml](feeds/intialaisten-elokuvien-naytokset.xml) | https://mikknikk.github.io/uutiset/feeds/intialaisten-elokuvien-naytokset.xml |

Kahdeksan muuta aihekierroksen syötettä voivat olla tyhjiä, jos uusia olennaisia uutisia ei löydy. Intialaisen elokuvan kaksi syötettä siirrettiin aiemmasta repositoriosta historiallisine itemeineen. Yhteenkään syötteeseen ei lisätä keinotekoisia “ei uutisia” -artikkeleita.

## Pääautomaation lukujärjestys ja tehtäväkierto

Pääautomaation varsinainen tehtävä- ja toimintakuvaus on versionhallittu tiedostossa [docs/paaautomaation-ohje.md](docs/paaautomaation-ohje.md). ChatGPT-automaation asetuksissa käytettävän lyhyen käynnistyskehotteen kanoninen teksti on `prompts/paauutisseuranta.txt`-tiedostossa. Kopioi tiedoston sisältö automaation asetuksiin; pidä tiedosto ja asetuksiin tallennettu kehote täsmälleen samoina. Ohjeversion tunniste ja viimeisimmän onnistuneen ajon käyttämä versio tallennetaan `data/seurantatila.json`-tiedoston `automation_instructions`-osioon. Käynnistyskehotteen tunniste tarkistetaan lisäksi `startup_prompt_id`-kenttää vasten; vanhentunut tai väärä kehote keskeyttää ajon. Jos käsikirjan ja JSONin nykyversiot eivät täsmää, pääautomaatio keskeyttää ajon.

Myös erillisellä näytövahdilla ja viikoittaisella laatutarkistuksella on omat GitHubissa ylläpidettävät käsikirjansa:
- Näytösvahti: `docs/intialaisten-elokuvien-naytosseuranta.md`. Ohjeversion tunniste, käynnistyskehotteen tunniste ja viimeisin onnistunut käyttöaika ovat `separate_screening_watch.automation_instructions`-osiossa.
  Näytösvahti käsittelee tilapäiset virheet rajatuilla uusintayrityksillä; epäonnistunut ajo säilyttää viimeisimmän onnistumisen tarkistuspisteen, ja seuraava ajo palauttaa koko väliin jääneen seurantajakson.
- Laatutarkistus: `docs/laatutarkistuksen-ohje.md`. Ohjeversion tunniste, käynnistyskehotteen tunniste ja viimeisin onnistunut käyttöaika ovat `quality_check_instructions`-osiossa. Laatutarkistus on muuten vain luku -auditointi; se saa päivittää ainoastaan nämä kaksi onnistuneen ajon metatietokenttää.

Pääautomaatio käsittelee päivittäisellä ajollaan vain yhtä tehtäväjonon aihetta. Lue ennen hakua seuraavat tiedostot tässä järjestyksessä:

1. `README.md` – repositorion yleiskuva, tiedostojen vastuut ja julkaisuperiaatteet.
2. `docs/paaautomaation-ohje.md` – pääautomaation täydellinen, versioitu toimintakäsikirja.
3. `docs/tehtavajono.md` – kiertojärjestys ja seuraava tehtävä.
4. `docs/seuranta.md` – tehtäväkohtaiset seurantajaksot, aiempi uutishistoria, koneellinen seurantatila ja raportointisäännöt.
5. `docs/lahteet.md`, `data/source-catalog.json` ja valitun tehtävän `data/sources/{task_id}.json` – yleiset lähdeperiaatteet, yhteiset lähdetiedot ja tehtäväkohtaiset lähdekäytöt.
6. `docs/saavutettavuus.md` – kaikkia julkaisuja koskevat saavutettavuusperiaatteet.
7. `docs/kehityskaytannot.md` – koodimuutoksia koskevat ylläpitokäytännöt; lue ja noudata niitä aina, jos muutat skriptejä.
8. Valitun tehtävän aihekohtaiset ohjeet ja seurantaloki. Tehtävässä 9 lue lisäksi kokonaan `docs/intialaisen-elokuvan-ohje.md`, `docs/intialaisen-elokuvan-uutiset.md`, `docs/intialaisen-elokuvan-lahteet.md` ja `docs/intialaisen-elokuvan-seuranta.md`.

Lue ennen julkaisua kaikki kymmenen RSS-tiedostoa kokonaan tai hae niiden kaikki itemit. Näytösfeed luetaan vain historian säilyttämiseksi; älä tee näytöshakuja tai muuta näytösfeedin sisältöä. Tarkista kaikkien kymmenen syötteen GUIDien yksilöllisyys muuttamatta muiden tehtävien sisältöä. Näytösvahti ja sen dokumentit ovat erillisen automaation vastuulla; pääautomaatio ei tee näytöshakuja eikä muuta näytösfeedin tai näytöshistorian sisältöä. Näytöshistorian tietomalli on dokumentoitu tiedostossa `docs/naytoshistorian-rakenne.md`, ja se kuuluu näytösvahdin lukemistoon.

Dokumenttien vastuut ja tarkempi lukujärjestys on koottu tämän README:n **Tiedostojen vastuut** -osioon. Aiheiden, syötteiden tai automaatioiden muuttuessa päivitä kaikki niitä koskevat ensisijaiset dokumentit ja niitä tarkistavat testit.

## Dokumentaation ajantasaisuuden loppukatselmus

Aina kun mitä tahansa dokumentaatiotiedostoa muutetaan tai lisätään, tee ennen työn päättämistä koko dokumentaation ajantasaisuuden katselmus:

1. Lue muutoksen jälkeen README.md, docs/seuranta.md ja docs/lahteet.md kokonaan sekä kaikki muut aiheeseen liittyvät dokumentit.
2. Tarkista, että kaikki aihe-, tiedosto-, RSS-URL-, aikataulu-, lähde- ja toimintatapatiedot ovat keskenään yhdenmukaisia. Esimerkiksi aiheiden tai syötteiden lisäys tai poisto päivitetään kaikkialle, missä niitä luetellaan.
3. Etsi vanhentuneet, päällekkäiset, ristiriitaiset ja puuttuvat tiedot myös muista dokumenteista; älä tyydy tarkistamaan vain juuri muokattua kohtaa.
4. Korjaa havaitut ristiriidat saman muutossarjan yhteydessä. Jos jokin tieto on tarkoituksella erilainen eri tiedostoissa, selitä ero.
5. Hae kaikki muutetut dokumentit GitHubista takaisin ja varmista, että tallennettu sisältö vastaa tarkistettua versiota.

Dokumentaatiomuutosta ei pidetä valmiina ennen tätä loppukatselmusta.

## Julkaisuperiaatteet

- Pidä aiheet täysin erillään: kuhunkin RSS-syötteeseen vain kyseisen aiheen uutiset.
- Julkaise vain uutta tai olennaisesti muuttunutta, lähteillä varmennettua tietoa.
- Yhdistä saman tapahtuman useat lähteet yhdeksi RSS-artikkeliksi.
- Älä toista muuttumatonta taustatietoa, vanhoja huhuja tai fanispekulaatiota.
- Kirjoita uutisartikkelit suomeksi. Lisää otsikko, julkaisu- ja tapahtumapäivä silloin kun ne ovat tiedossa, lähdelinkit sekä tiedon luotettavuuden luokitus.
- Suosi ensisijaisia lähteitä. Merkittävät väitteet pyri varmistamaan kahdesta toisistaan riippumattomasta toimituksellisesta lähteestä.
- Jos julkaisijan oma haku ei toimi, hae hakukoneella rajauksella kuten `site:yle.fi` tai `site:hs.fi`. Avaa ja tarkista alkuperäinen juttu; hakutuloskatkelma ei yksin riitä.
- Säilytä aiemmat RSS-artikkelit ja niiden GUID-tunnisteet. Päivitä `lastBuildDate` vain, kun syötettä muutetaan.
- Tarkista jokaisen muutoksen jälkeen XML:n kelvollisuus, GUID-tunnisteiden yksilöllisyys, vanhojen artikkeleiden säilyminen ja aiherajaus.
- Älä koskaan väitä tiedoston päivittyneen ennen kuin GitHub-kirjoitus ja muutoksen jälkeinen takaisinluku on onnistunut.

## Kehityksen tilanne

Ajantasainen lista toteutetuista parannuksista ja avoimista kehityskohteista on tiedostossa [docs/kehityskohteet.md](docs/kehityskohteet.md). Päivitä listaa aina kehitystyön edetessä. Julkisen valvomon ja RSS-lukijan tavoitekuvaus sekä vaiheittainen toteutusseuranta ovat dokumentissa [docs/julkinen-valvomo-ja-rss-lukija.md](docs/julkinen-valvomo-ja-rss-lukija.md).

## Tiedostojen vastuut

Kullakin dokumentilla on yksi ensisijainen vastuu. Muut dokumentit viittaavat siihen sen sijaan, että kopioisivat saman säännön kokonaisuudessaan.

- `README.md`: repositorion yleiskuva, hakemistorakenne, RSS-syötteiden luettelo, automaatioiden työnjako ja dokumentaation lukujärjestys.
- `docs/paaautomaation-ohje.md`: pääautomaation täydellinen tehtävä- ja toimintakuvaus sekä sen versionhallinnan säännöt.
- `prompts/README.md` ja `prompts/*.txt`: automaatioiden asetuksiin kopioitavat käynnistyskehotteet ja niiden ylläpitomenettely. Tekstit säilytetään sellaisinaan.
- `docs/intialaisten-elokuvien-naytosseuranta.md`: näytösvahdin täydellinen, versioitu tehtävä- ja toimintakuvaus.
- `docs/laatutarkistuksen-ohje.md`: viikoittaisen laatutarkistuksen täydellinen, versioitu tehtävä- ja toimintakuvaus.
- `docs/tehtavajono.md`: yhdeksän tehtävän kiertojärjestys, seuraava vuoro ja vuoron siirtämisen ehdot. Ei yleisiä raportointi- tai koodauskäytäntöjä.
- `docs/seuranta.md`: tehtäväkohtaiset seurantajaksot, onnistuneiden tarkistusten tila, uutistapahtumien historia ja luotettavuusluokat.
- `docs/lahteet.md`: yleiset lähdeperiaatteet ja kaikkien yhdeksän aihekierroksen lähteiden lähtöpisteet. Luettelo ei ole suljettu.
- `docs/saavutettavuus.md`: kaikkien julkaisujen ja Markdown-dokumentaation saavutettavuustavoitteet ja testausperiaatteet.
- `docs/kehityskaytannot.md`: dokumentaation luokat ja kirjoitustavat, käynnistyskehotteiden ylläpito, skriptien kommentointi, koodin ylläpito ja muutosten tarkistus.
- `docs/kehityskohteet.md`: toteutettujen parannusten tilanne ja avoin kehitystyö.
- `docs/julkinen-valvomo-ja-rss-lukija.md`: julkisen GitHub Pages -valvomon ja RSS-lukijan tavoitearkkitehtuuri, tietomalliehdotukset, turvallisuus- ja saavutettavuusvaatimukset sekä vaiheittainen toteutusseuranta.
- `docs/intialaisen-elokuvan-*.md`: intialaisen elokuvan uutisseurannan aihekohtaiset ohjeet, lähteet ja historia.
- `docs/intialaisten-elokuvien-naytosseuranta.md` ja `docs/naytoshistorian-rakenne.md`: erillisen näytösvahdin työohje ja sen muutoshistorian tietomalli.
- `data/seurantatila.json`: koneellisesti luettava tarkistustila, tehtäväkierron rinnakkaistila sekä pääautomaation, näytösvahdin ja laatutarkistuksen ohjeversiot ja viimeksi onnistuneesti käytetyt versiot.
- `data/naytosten-muutoshistoria.json`: näytösten nykytila ja append-only-muutostapahtumat.
- `schemas/naytosten-muutoshistoria.schema.json`: näytöshistorian JSON Schema Draft 2020-12 -skeema.
- `scripts/validate_feeds.py` ja `.github/workflows/validate-feeds.yml`: automaattiset rakennetarkistukset ja niiden suoritus.
- `feeds/*.xml`: julkaistut RSS-artikkelit; jokainen syöte sisältää vain sille kuuluvan aiheen.

Yleiset raportointisäännöt ovat `docs/seuranta.md`:ssä, eivät tehtäväjonossa. Dokumentaation ja skriptien kehityskäytännöt ovat `docs/kehityskaytannot.md`:ssä. Automaation asetuksiin kopioitavien käynnistyskehotteiden ensisijaiset tekstit ovat `prompts/`-hakemistossa; automaatioiden tehtäväkäsikirjat pysyvät `docs/`-hakemistossa. Näytösvahti on erillinen automaatio eikä kuulu pääautomaation lukujärjestykseen tai tehtäväkiertoon.

## Laaja kansainvälinen haku ja Suomi-näkökulma

Kaikissa yhdeksässä aihekierroksen tehtävässä etsitään uutisia maailmanlaajuisesti. Haku ei rajoitu englanninkieliseen mediaan: käytä aiheen kannalta olennaisia paikalliskieliä, alkuperäisiä kirjoitusasuja, translitterointeja ja alueellisia lähteitä. Tarkista myös Suomen media, viralliset suomalaiset järjestäjät, tapahtumapaikat, levittäjät ja kulttuuritoimijat. Tolkienin, Taylor Swiftin, Muumien ja Euroviisujen tehtävissä tehdään lisäksi erillinen Suomessa järjestettävien aihekohtaisten tapahtumien haku: konsertit, näyttelyt, elokuvanäytökset, kilpailut, fanitapahtumat, katselujuhlat ja muut yleisötilaisuudet. Jos tällaista Suomen-yhteyttä ei löydy, älä lisää raporttiin erillistä mainintaa sen puuttumisesta.

Kun tehtäviä tai syötteitä lisätään tai poistetaan, päivitä syötetaulukko, tehtäväjono, koneellinen seurantatila ja tämän README:n lukujärjestys. Aihekohtaiset ohjeet luetaan vain kyseisen tehtävän yhteydessä; näytösvahti käyttää omaa erillistä lukujärjestystään.


## Intialaisen elokuvan uutis- ja näytösseuranta

Intialaisen elokuvan uutisraportti on tehtäväjonon tehtävä 9. Suomessa järjestettävien intialaisten elokuvien näytöksiä seuraa erillinen päivittäinen Intialaisten elokuvien näytösvahti, joka ei kuluta aihekierroksen vuoroa.

- Uutisraportin RSS: [intialaiset-elokuvat.xml](feeds/intialaiset-elokuvat.xml) – https://mikknikk.github.io/uutiset/feeds/intialaiset-elokuvat.xml
- Näytösten RSS: [intialaisten-elokuvien-naytokset.xml](feeds/intialaisten-elokuvien-naytokset.xml) – https://mikknikk.github.io/uutiset/feeds/intialaisten-elokuvien-naytokset.xml
- Ohjeet: `docs/intialaisen-elokuvan-ohje.md`, `docs/intialaisen-elokuvan-uutiset.md` ja `docs/intialaisten-elokuvien-naytosseuranta.md`.
- Seurantaloki: `docs/intialaisen-elokuvan-seuranta.md`.
- Lähderekisteri: `docs/intialaisen-elokuvan-lahteet.md`.

Näytösajat eivät kuulu uutisraportin RSS-itemeihin. Näytösvahti julkaisee vain näytös-RSS-syötteeseen.


## Saavutettavuus

Tämän repositorion saavutettavuuden tavoitetaso on WCAG 2.2 AAA kaikilta soveltuvilta osin, kuten aiemmassa elokuvaraportti-repositoriossa. Tavoitetason saavuttamista ei väitetä ilman asianmukaista testausta. Yksityiskohtaiset vaatimukset ovat tiedostossa [docs/saavutettavuus.md](docs/saavutettavuus.md).

## RSS-itemien sisältö ja lähteet

RSS-itemissä ei käytetä item-kohtaista `<link>`-elementtiä. Jokaisen itemin koko raportti julkaistaan `<description>`-elementissä CDATA-alueen semanttisena HTML-sisältönä. Raportin lopussa on otsikoitu lähdeluettelo, jossa linkkitekstit kertovat lähteen nimen ja tarvittaessa julkaisupäivän. Kanavatason `<link>` ja Atomin kanavatason `atom:link` ovat sallittuja syötteen metatietoja.

## Näytösseurannan muutoshistoria

Näytösten viimeisin tunnettu tila ja tapahtumapohjainen muutosloki tallennetaan tiedostoon [data/naytosten-muutoshistoria.json](data/naytosten-muutoshistoria.json). Tietomalli ja käyttöönoton rajaukset on kuvattu tiedostossa [docs/naytoshistorian-rakenne.md](docs/naytoshistorian-rakenne.md), ja päivittäisen näytösvahdin on noudatettava [näytösseurannan työohjetta](docs/intialaisten-elokuvien-naytosseuranta.md). Ensimmäinen varmennettu lähtötilanne muodostettiin 16.11.2026 ja `baseline_status` on `active`; vanhoista RSS-teksteistä ei ole arvattu takautuvia tapahtumia.

## Koneellisesti luettava seurantatila

`data/seurantatila.json` tallentaa yhdeksän kiertotehtävän ja erillisen näytösvahdin koneellisesti luettavan tilan. Sen tehtäväkierron on vastattava `docs/tehtavajono.md`:tä. Seurantajaksojen, aikaleimojen ja päivitysten tarkat säännöt ovat [seurantaohjeessa](docs/seuranta.md).

## Skriptien kehityskäytännöt

Skriptien kommentointi- ja ylläpitovaatimukset on määritelty sitovasti tiedostossa [docs/kehityskaytannot.md](docs/kehityskaytannot.md).

## Automaattiset laatutestit

GitHub Actions asentaa `requirements.txt`-tiedoston riippuvuudet ja suorittaa `scripts/validate_feeds.py`-testit push- ja pull request -muutoksissa. Näytöshistorian rakenteen tarkistus tehdään lisäksi virallista JSON Schema -määrittelyä vasten. Ne tarkistavat RSS/XML- ja kuvausten HTML-rakenteet, GUIDit, lähdeluettelot, syötteiden aihe-erottelun sekä dokumentaation ja koneellisen seurantatilan keskinäisen yhdenmukaisuuden. Tarkempi testikattavuus ja sen rajat on kuvattu [seurantaohjeessa](docs/seuranta.md).

Automaattiset testit eivät todista uutisväitteiden paikkansapitävyyttä, lähteiden riippumattomuutta tai WCAG 2.2 AAA -vaatimusten täyttymistä. Saavutettavuuden manuaaliset testit tehdään erikseen.
