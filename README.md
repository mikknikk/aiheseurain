# Uutisseuranta – kahdeksan aihekohtaista RSS-syötettä

Tämä repositorio ylläpitää kahdeksaa toisistaan erillistä, suomenkielistä uutisseurantaa. Yksi automaatio käynnistyy päivittäin klo 12.00 aikavyöhykkeellä Europe/Helsinki. Kukin ajo käsittelee vain yhden aiheen TRACKING.md-tiedostossa olevan kiertojonon mukaisesti; kahdeksan aiheen kierros kestää kahdeksan päivää.

## Syötteet

| Aihe | RSS-tiedosto | Raaka RSS-osoite |
|---|---|---|
| J. R. R. Tolkien | [tolkien.xml](tolkien.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/tolkien.xml |
| Taylor Swift | [taylor-swift.xml](taylor-swift.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/taylor-swift.xml |
| Saint Dr. Gurmeet Ram Rahim Singh Ji Insan | [gurmeet-ram-rahim-singh.xml](gurmeet-ram-rahim-singh.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/gurmeet-ram-rahim-singh.xml |
| Muumit | [muumit.xml](muumit.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/muumit.xml |
| Wakaliwood | [wakaliwood.xml](wakaliwood.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/wakaliwood.xml |
| Euroviisut ja kansalliset karsinnat | [euroviisut.xml](euroviisut.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/euroviisut.xml |
| Sompote Sands | [sompote-sands.xml](sompote-sands.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/sompote-sands.xml |
| Shakkidraamat | [shakkidraamat.xml](shakkidraamat.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/shakkidraamat.xml |

Syötteet on alustettu tyhjinä RSS 2.0 -tiedostoina. Niihin lisätään vain tarkistetut, olennaiset uutiset; tyhjä syöte ei tarkoita virhettä eikä sinne lisätä keinotekoisia “ei uutisia” -artikkeleita.

## Ajon pakollinen esitietojen lukujärjestys ja aihekierto

Ennen jokaista ajoa lue aina tämänhetkinen versio seuraavista tiedostoista sekä kaikkien kahdeksan RSS-syötteen nykyinen sisältö:

1. `README.md` – kokonaisuus, tiedostopolut ja julkaisuperiaatteet.
2. `TRACKING.md` – aihekohtainen aiempi uutisointi, viimeisin luotettava tilanne ja duplikaattien esto.
3. `SOURCES.md` – lähdepolitiikka ja lähdehakujen lähtöpisteet.
4. `tolkien.xml`, `taylor-swift.xml`, `gurmeet-ram-rahim-singh.xml`, `muumit.xml`, `wakaliwood.xml`, `euroviisut.xml`, `sompote-sands.xml`, `shakkidraamat.xml` – julkaistut uutiset ja GUID-tunnisteet.

Tiedostot ovat ajon ensisijainen muistijälki. Älä nojaa pelkästään edellisen ajon keskustelumuistiin. Tarkista TRACKING.md:n "Aiheajojen kiertojono" -kohta ja tee varsinaiset haut vain siinä seuraavaksi merkitylle yhdelle aiheelle. Onnistuneen ajon jälkeen siirrä vuoro seuraavaan aiheeseen; epäonnistuneen tai kesken jääneen ajon jälkeen pidä sama aihe vuorossa. Nykyinen automaatio käynnistyy kerran päivässä, joten kukin aihe käsitellään noin kahdeksan päivän välein. Päivitä dokumentaatiota, kun seurannan rajaus, lähteet tai uutisten tila muuttuu.

## Dokumentaation ajantasaisuuden loppukatselmus

Aina kun mitä tahansa dokumentaatiotiedostoa muutetaan tai lisätään, tee ennen työn päättämistä koko dokumentaation ajantasaisuuden katselmus:

1. Lue muutoksen jälkeen README.md, TRACKING.md ja SOURCES.md kokonaan sekä kaikki muut aiheeseen liittyvät dokumentit.
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

- `TRACKING.md`: aihekohtainen uutisseurannan tila, aiemmin käsitellyt tapahtumat, luotettavuus, lähteet ja seuraava olennainen tarkistustarve.
- `SOURCES.md`: lähdeluettelo ja hakustrategiat. Lista on lähtökohta, ei suljettu sallittujen lähteiden luettelo.
- RSS-tiedostot: julkaistut uutisartikkelit.


## Laaja kansainvälinen haku ja Suomi-näkökulma

Kaikissa kahdeksassa kategoriassa etsitään uutisia maailmanlaajuisesti. Haku ei rajoitu englanninkieliseen mediaan: käytä aiheen kannalta olennaisia paikalliskieliä, alkuperäisiä kirjoitusasuja, translitterointeja ja alueellisia lähteitä. Tarkista myös Suomen media, viralliset suomalaiset järjestäjät, tapahtumapaikat, levittäjät ja kulttuuritoimijat. Nosta uutisissa selvästi esiin Suomeen liittyvät tapahtumat, suomalaiset toimijat ja Suomessa järjestettävät konsertit, elokuvanäytökset, kilpailut, fanitapahtumat tai muut tapahtumat. Jos tällaista Suomen-yhteyttä ei löydy, älä lisää raporttiin erillistä mainintaa sen puuttumisesta.

Päivitä yllä oleva syötetaulukko ja esitietojen lukujärjestys aina, kun aiheita lisätään. Ennen jokaista ajoa on luettava kaikki kahdeksan RSS-tiedostoa sekä README.md, TRACKING.md ja SOURCES.md.
