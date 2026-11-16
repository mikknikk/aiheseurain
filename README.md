# Uutisseuranta – yhdeksän tehtävän seurantakierto

Tämä repositorio ylläpitää yhdeksää erillistä seurantatehtävää yhdessä kiertojonossa. Yksi automaatio käynnistyy päivittäin klo 12.00 Europe/Helsinki ja käsittelee kullakin ajolla vain yhden tehtävän. Yhdeksän tehtävän kierto tarkoittaa, että kukin aihe tarkistetaan normaalisti noin yhdeksän päivän välein. Intialaisen elokuvan uutisraportti on jonon tehtävä 9. Intialaisten elokuvien näytösseuranta on erillisen päivittäisen näytösvahdin vastuulla.

## Hakemistorakenne

- `feeds/` – kaikki kymmenen RSS-syötettä (yhdeksän aihekierrossa ja yksi erilliselle näytövahdille).
- `docs/` – suomenkieliset seuranta-, lähde-, ohje- ja saavutettavuusdokumentit.
- `docs/tehtavajono.md` – yhdeksän tehtävän kiertojärjestys, seuraava vuoro ja seurantajaksojen raportointisääntö.
- `README.md` – repositorion aloitussivu ja kokonaiskuva.

## Syötteet

| Aihe | RSS-tiedosto | Raaka RSS-osoite |
|---|---|---|
| J. R. R. Tolkien | [tolkien.xml](feeds/tolkien.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/tolkien.xml |
| Taylor Swift | [taylor-swift.xml](feeds/taylor-swift.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/taylor-swift.xml |
| Saint Dr. Gurmeet Ram Rahim Singh Ji Insan | [gurmeet-ram-rahim-singh.xml](feeds/gurmeet-ram-rahim-singh.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/gurmeet-ram-rahim-singh.xml |
| Muumit | [muumit.xml](feeds/muumit.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/muumit.xml |
| Wakaliwood | [wakaliwood.xml](feeds/wakaliwood.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/wakaliwood.xml |
| Euroviisut ja kansalliset karsinnat | [euroviisut.xml](feeds/euroviisut.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/euroviisut.xml |
| Sompote Sands | [sompote-sands.xml](feeds/sompote-sands.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/sompote-sands.xml |
| Shakkidraamat | [shakkidraamat.xml](feeds/shakkidraamat.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/shakkidraamat.xml |
| Intialaisen elokuvan uutisraportti | [intialaiset-elokuvat.xml](feeds/intialaiset-elokuvat.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/intialaiset-elokuvat.xml |
| Intialaisten elokuvien näytökset Suomessa | [intialaisten-elokuvien-naytokset.xml](feeds/intialaisten-elokuvien-naytokset.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/intialaisten-elokuvien-naytokset.xml |

Kahdeksan aihekohtaisen seurannan syötteet voivat olla tyhjiä, jos uusia olennaisia uutisia ei löydy. Intialaisen elokuvan kaksi syötettä siirrettiin aiemmasta repositoriosta historiallisine itemeineen. Yhteenkään syötteeseen ei lisätä keinotekoisia “ei uutisia” -artikkeleita.

## Ajon pakollinen esitietojen lukujärjestys ja tehtäväkierto

Ennen jokaista ajoa lue aina tämänhetkinen versio seuraavista tiedostoista sekä kaikkien kymmenen RSS-syötteen nykyinen sisältö. Näytösfeed luetaan historian säilyttämiseksi, mutta sitä ei käsitellä eikä päivitetä tässä automaatiossa:

1. `README.md` – kokonaisuus, tiedostopolut ja julkaisuperiaatteet.
2. `docs/tehtavajono.md` – tehtävien kiinteä järjestys, seuraava vuoro ja seurantajaksojen aikavälit.
3. `docs/seuranta.md` – aihekohtainen aiempi uutisointi, viimeisin luotettava tilanne ja duplikaattien esto.
4. `docs/lahteet.md` – yleinen lähdepolitiikka ja lähdehakujen lähtöpisteet.
5. `docs/intialaisen-elokuvan-ohje.md`, `docs/intialaisen-elokuvan-uutiset.md`, `docs/intialaisten-elokuvien-naytosseuranta.md`, `docs/intialaisen-elokuvan-seuranta.md` ja `docs/intialaisen-elokuvan-lahteet.md` – intialaisen elokuvan uutis- ja näytösseurannan yksityiskohtaiset ohjeet, historia ja lähteet.
6. `feeds/tolkien.xml`, `feeds/taylor-swift.xml`, `feeds/gurmeet-ram-rahim-singh.xml`, `feeds/muumit.xml`, `feeds/wakaliwood.xml`, `feeds/euroviisut.xml`, `feeds/sompote-sands.xml`, `feeds/shakkidraamat.xml`, `feeds/intialaiset-elokuvat.xml` ja `feeds/intialaisten-elokuvien-naytokset.xml` – julkaistut uutiset, näytöspäivitykset ja GUID-tunnisteet.

Tiedostot ovat ajon ensisijainen muistijälki. Älä nojaa pelkästään edellisen ajon keskustelumuistiin. Tarkista docs/tehtavajono.md:n seuraava tehtävä ja tee varsinaiset haut vain sille yhdelle tehtävälle. Onnistuneen ajon jälkeen siirrä vuoro seuraavaan tehtävään; epäonnistuneen tai kesken jääneen ajon jälkeen pidä sama tehtävä vuorossa. Nykyinen automaatio käynnistyy kerran päivässä, joten yhdeksän tehtävän kierto tarkoittaa normaalisti noin yhdeksän päivän tarkistusväliä kullekin tehtävälle. Erillinen näytösvahti tarkistaa näytökset päivittäin. Ilmoita jokaisessa raportissa tehtäväkohtaisen seurantajakson alku ja loppu. Päivitä dokumentaatiota, kun seurannan rajaus, lähteet tai uutisten tila muuttuu.

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

## Tiedostojen vastuut

- `docs/tehtavajono.md`: tehtäväjärjestys, seuraava vuoro ja seurantajaksojen raportointisääntö.
- `docs/seuranta.md`: aihekohtainen uutisseurannan tila, aiemmin käsitellyt tapahtumat, luotettavuus, lähteet ja seuraava olennainen tarkistustarve.
- `docs/lahteet.md`: lähdeluettelo ja hakustrategiat. Lista on lähtökohta, ei suljettu sallittujen lähteiden luettelo.
- RSS-tiedostot: julkaistut uutisartikkelit.


## Laaja kansainvälinen haku ja Suomi-näkökulma

Kaikissa kahdeksassa kategoriassa etsitään uutisia maailmanlaajuisesti. Haku ei rajoitu englanninkieliseen mediaan: käytä aiheen kannalta olennaisia paikalliskieliä, alkuperäisiä kirjoitusasuja, translitterointeja ja alueellisia lähteitä. Tarkista myös Suomen media, viralliset suomalaiset järjestäjät, tapahtumapaikat, levittäjät ja kulttuuritoimijat. Nosta uutisissa selvästi esiin Suomeen liittyvät tapahtumat, suomalaiset toimijat ja Suomessa järjestettävät konsertit, elokuvanäytökset, kilpailut, fanitapahtumat tai muut tapahtumat. Jos tällaista Suomen-yhteyttä ei löydy, älä lisää raporttiin erillistä mainintaa sen puuttumisesta.

Päivitä yllä oleva syötetaulukko, docs/tehtavajono.md ja esitietojen lukujärjestys aina, kun tehtäviä lisätään tai poistetaan. Ennen jokaista ajoa on luettava kaikki kymmenen RSS-tiedostoa sekä README.md, docs/tehtavajono.md, docs/seuranta.md, docs/lahteet.md, docs/saavutettavuus.md ja kaikki viisi intialaisen elokuvan docs/-dokumenttia.


## Intialaisen elokuvan uutis- ja näytösseuranta

Intialaisen elokuvan uutisraportti on tehtäväjonon tehtävä 9. Suomessa järjestettävien intialaisten elokuvien näytöksiä seuraa erillinen päivittäinen Intialaisten elokuvien näytösvahti, joka ei kuluta aihekierroksen vuoroa.

- Uutisraportin RSS: [intialaiset-elokuvat.xml](feeds/intialaiset-elokuvat.xml) – https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/intialaiset-elokuvat.xml
- Näytösten RSS: [intialaisten-elokuvien-naytokset.xml](feeds/intialaisten-elokuvien-naytokset.xml) – https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/intialaisten-elokuvien-naytokset.xml
- Ohjeet: `docs/intialaisen-elokuvan-ohje.md`, `docs/intialaisen-elokuvan-uutiset.md` ja `docs/intialaisten-elokuvien-naytosseuranta.md`.
- Seurantaloki: `docs/intialaisen-elokuvan-seuranta.md`.
- Lähderekisteri: `docs/intialaisen-elokuvan-lahteet.md`.

Näytösajat eivät kuulu uutisraportin RSS-itemeihin. Näytösvahti julkaisee vain näytös-RSS-syötteeseen.


## Saavutettavuus

Tämän repositorion saavutettavuuden tavoitetaso on WCAG 2.2 AAA kaikilta soveltuvilta osin, kuten aiemmassa elokuvaraportti-repositoriossa. Tavoitetason saavuttamista ei väitetä ilman asianmukaista testausta. Yksityiskohtaiset vaatimukset ovat tiedostossa [docs/saavutettavuus.md](docs/saavutettavuus.md).

## RSS-itemien sisältö ja lähteet

RSS-itemissä ei käytetä item-kohtaista `<link>`-elementtiä. Jokaisen itemin koko raportti julkaistaan `<description>`-elementissä CDATA-alueen semanttisena HTML-sisältönä. Raportin lopussa on otsikoitu lähdeluettelo, jossa linkkitekstit kertovat lähteen nimen ja tarvittaessa julkaisupäivän. Kanavatason `<link>` ja Atomin kanavatason `atom:link` ovat sallittuja syötteen metatietoja.

## Koneellisesti luettava seurantatila

data/seurantatila.json on aihekohtaisten tarkistusten koneellisesti luettava tilatiedosto. Se sisältää yhdeksän kiertotehtävän viimeisimmät onnistuneet tarkistusajat ja seurantajaksot sekä erillisen näytösvahdin tilan. Aikaleimat ovat aluksi null-arvoja, koska vanhoja tehtäväkohtaisia kellonaikoja ei ole luotettavasti vahvistettu. Niitä ei saa täydentää arvauksilla.

Päivitä tilatiedosto vasta onnistuneen tarkistuksen ja mahdollisen RSS-julkaisun jälkeen, kun GitHubiin tehty muutos on luettu takaisin ja tarkistettu. Epäonnistunut tai kesken jäänyt ajo ei muuta viimeisintä onnistunutta tarkistusta eikä tehtäväjonon vuoroa. Käytä ISO 8601 -aikaleimoja aikavyöhyketietoineen. Päivitä rotation.next_task samaan aikaan kuin docs/tehtavajono.md:n seuraava tehtävä.

## Skriptien kehityskäytännöt

Kaikki uudet skriptit kirjoitetaan alusta lähtien suomeksi kommentoituina ja dokumentoituina samalla perusteellisuudella kuin `scripts/validate_feeds.py`. Kommenttien tulee auttaa myös Pythonia vähemmän osaavaa lukijaa ymmärtämään tiedoston tarkoitus, keskeiset funktiot, toimintavaiheet ja ei-ilmeiset ratkaisut. Kommentit pidetään ajan tasalla koodin muuttuessa. Tarkempi sitova ohje ja tarkistuslista: [docs/kehityskaytannot.md](docs/kehityskaytannot.md).

## Automaattiset laatutestit

GitHub Actions suorittaa scripts/validate_feeds.py-testin main-haaraan kohdistuvissa push- ja pull request -muutoksissa. Testi tarkistaa kaikki kymmenen RSS-syötettä: XML:n jäsennettävyyden, item-määrän, GUIDien olemassaolon ja yksilöllisyyden, item-kohtaisten linkkien puuttumisen, CDATA-muotoiset descriptionit sekä kuvausten HTML-rakenteen, linkkien URL-muodot, otsikkotasot ja kuvien alt-attribuutit. Lisäksi testi vertaa README:n syötetaulukkoa, tehtäväjonon yhdeksää tehtävää ja JSON-seurantatilan kiertojärjestystä sekä tarkistaa aikaleimojen aikavyöhykkeet, seurantajaksojen johdonmukaisuuden ja erillisen näytösvahdin määritykset.

Testit eivät varmista uutisväitteiden paikkansapitävyyttä, linkkien saavutettavuutta, lähteiden riippumattomuutta tai WCAG 2.2 AAA -vaatimusten täyttymistä. Saavutettavuuden manuaaliset testit tehdään edelleen erikseen.
