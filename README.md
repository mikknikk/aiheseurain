# Uutisseuranta – kahdeksan aihekohtaista RSS-syötettä sekä intialainen elokuva

Tämä repositorio ylläpitää kahdeksaa toisistaan erillistä aihekohtaista uutisseurantaa sekä kahta päivittäin suoritettavaa intialaisen elokuvan seurantamoduulia: uutisraportointia ja Suomessa järjestettävien näytösten seurantaa. Yksi automaatio käynnistyy päivittäin klo 12.00 Europe/Helsinki. Kukin ajo käsittelee lisäksi yhden kahdeksasta kiertojonoaiheesta; kierto kestää kahdeksan päivää. Intialaisen elokuvan uutis- ja näytösseuranta suoritetaan joka päivä tämän kierron rinnalla.

## Hakemistorakenne

- `feeds/` – kaikki kymmenen RSS-syötettä.
- `docs/` – suomenkieliset seuranta-, lähde-, ohje- ja saavutettavuusdokumentit.
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

## Ajon pakollinen esitietojen lukujärjestys ja aihekierto

Ennen jokaista ajoa lue aina tämänhetkinen versio seuraavista tiedostoista sekä kaikkien kymmenen RSS-syötteen nykyinen sisältö:

1. `README.md` – kokonaisuus, tiedostopolut ja julkaisuperiaatteet.
2. `docs/seuranta.md` – aihekohtainen aiempi uutisointi, viimeisin luotettava tilanne ja duplikaattien esto.
3. `docs/lahteet.md` – yleinen lähdepolitiikka ja lähdehakujen lähtöpisteet.
4. `docs/intialaisen-elokuvan-ohje.md`, `docs/intialaisen-elokuvan-uutiset.md`, `docs/intialaisten-elokuvien-naytosseuranta.md`, `docs/docs/intialaisen-elokuvan-seuranta.md` ja `docs/docs/intialaisen-elokuvan-lahteet.md` – intialaisen elokuvan uutis- ja näytösseurannan yksityiskohtaiset ohjeet, historia ja lähteet.
5. `feeds/tolkien.xml`, `feeds/taylor-swift.xml`, `feeds/gurmeet-ram-rahim-singh.xml`, `feeds/muumit.xml`, `feeds/wakaliwood.xml`, `feeds/euroviisut.xml`, `feeds/sompote-sands.xml`, `feeds/shakkidraamat.xml`, `feeds/intialaiset-elokuvat.xml` ja `feeds/intialaisten-elokuvien-naytokset.xml` – julkaistut uutiset, näytöspäivitykset ja GUID-tunnisteet.

Tiedostot ovat ajon ensisijainen muistijälki. Älä nojaa pelkästään edellisen ajon keskustelumuistiin. Tarkista docs/seuranta.md:n "Aiheajojen kiertojono" -kohta ja tee varsinaiset haut vain siinä seuraavaksi merkitylle yhdelle aiheelle. Onnistuneen ajon jälkeen siirrä vuoro seuraavaan aiheeseen; epäonnistuneen tai kesken jääneen ajon jälkeen pidä sama aihe vuorossa. Nykyinen automaatio käynnistyy kerran päivässä. Kahdeksan kiertojonoaihetta käsitellään vuorotellen noin kahdeksan päivän välein; intialaisen elokuvan uutis- ja näytösseuranta tehdään jokaisella päivittäisellä ajolla. Päivitä dokumentaatiota, kun seurannan rajaus, lähteet tai uutisten tila muuttuu.

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

- `docs/seuranta.md`: aihekohtainen uutisseurannan tila, aiemmin käsitellyt tapahtumat, luotettavuus, lähteet ja seuraava olennainen tarkistustarve.
- `docs/lahteet.md`: lähdeluettelo ja hakustrategiat. Lista on lähtökohta, ei suljettu sallittujen lähteiden luettelo.
- RSS-tiedostot: julkaistut uutisartikkelit.


## Laaja kansainvälinen haku ja Suomi-näkökulma

Kaikissa kahdeksassa kategoriassa etsitään uutisia maailmanlaajuisesti. Haku ei rajoitu englanninkieliseen mediaan: käytä aiheen kannalta olennaisia paikalliskieliä, alkuperäisiä kirjoitusasuja, translitterointeja ja alueellisia lähteitä. Tarkista myös Suomen media, viralliset suomalaiset järjestäjät, tapahtumapaikat, levittäjät ja kulttuuritoimijat. Nosta uutisissa selvästi esiin Suomeen liittyvät tapahtumat, suomalaiset toimijat ja Suomessa järjestettävät konsertit, elokuvanäytökset, kilpailut, fanitapahtumat tai muut tapahtumat. Jos tällaista Suomen-yhteyttä ei löydy, älä lisää raporttiin erillistä mainintaa sen puuttumisesta.

Päivitä yllä oleva syötetaulukko ja esitietojen lukujärjestys aina, kun aiheita lisätään. Ennen jokaista ajoa on luettava kaikki kymmenen RSS-tiedostoa sekä README.md, docs/seuranta.md, docs/lahteet.md ja kaikki viisi INDIAN_FILM_*.md-dokumenttia.


## Intialaisen elokuvan päivittäiset seurantamoduulit

Sama automaatio tekee jokaisella päivittäisellä ajolla myös koko Intian elokuvateollisuuden uutisraportin ja Suomessa järjestettävien intialaisten elokuvien näytösten tarkistuksen. Moduulit ovat toisistaan erillisiä, mutta eivät erillisiä automaatioita.

- Uutisraportin RSS: [intialaiset-elokuvat.xml](feeds/intialaiset-elokuvat.xml) – https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/intialaiset-elokuvat.xml
- Näytösten RSS: [intialaisten-elokuvien-naytokset.xml](feeds/intialaisten-elokuvien-naytokset.xml) – https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/intialaisten-elokuvien-naytokset.xml
- Ohjeet: `docs/intialaisen-elokuvan-ohje.md`, `docs/intialaisen-elokuvan-uutiset.md` ja `docs/intialaisten-elokuvien-naytosseuranta.md`.
- Seurantaloki: `docs/docs/intialaisen-elokuvan-seuranta.md`.
- Lähderekisteri: `docs/docs/intialaisen-elokuvan-lahteet.md`.

Näytösajat eivät kuulu uutisraportin RSS-itemeihin. Uutisraportti ja näytösseuranta julkaisevat vain omiin syötteisiinsä.


## Saavutettavuus

Tämän repositorion saavutettavuuden tavoitetaso on WCAG 2.2 AAA kaikilta soveltuvilta osin, kuten aiemmassa elokuvaraportti-repositoriossa. Tavoitetason saavuttamista ei väitetä ilman asianmukaista testausta. Yksityiskohtaiset vaatimukset ovat tiedostossa [docs/saavutettavuus.md](docs/saavutettavuus.md).

## RSS-itemien sisältö ja lähteet

RSS-itemissä ei käytetä item-kohtaista `<link>`-elementtiä. Jokaisen itemin koko raportti julkaistaan `<description>`-elementissä CDATA-alueen semanttisena HTML-sisältönä. Raportin lopussa on otsikoitu lähdeluettelo, jossa linkkitekstit kertovat lähteen nimen ja tarvittaessa julkaisupäivän. Kanavatason `<link>` ja Atomin kanavatason `atom:link` ovat sallittuja syötteen metatietoja.
