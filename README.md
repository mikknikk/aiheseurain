# Uutisseuranta – neljä aihekohtaista RSS-syötettä

Tämä repositorio ylläpitää neljää toisistaan erillistä, suomenkielistä uutisseurantaa. Päivittäinen ajo on ajastettu klo 12.00 aikavyöhykkeellä Europe/Helsinki.

## Syötteet

| Aihe | RSS-tiedosto | Raaka RSS-osoite |
|---|---|---|
| J. R. R. Tolkien | [tolkien.xml](tolkien.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/tolkien.xml |
| Taylor Swift | [taylor-swift.xml](taylor-swift.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/taylor-swift.xml |
| Saint Dr. Gurmeet Ram Rahim Singh Ji Insan | [gurmeet-ram-rahim-singh.xml](gurmeet-ram-rahim-singh.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/gurmeet-ram-rahim-singh.xml |
| Muumit | [muumit.xml](muumit.xml) | https://raw.githubusercontent.com/mikknikk/uutiset/main/muumit.xml |

Syötteet on alustettu tyhjinä RSS 2.0 -tiedostoina. Niihin lisätään vain tarkistetut, olennaiset uutiset; tyhjä syöte ei tarkoita virhettä eikä sinne lisätä keinotekoisia “ei uutisia” -artikkeleita.

## Ajon pakollinen esitietojen lukujärjestys

Ennen jokaista ajoa lue aina tämänhetkinen versio seuraavista tiedostoista sekä kaikkien neljän RSS-syötteen nykyinen sisältö:

1. `README.md` – kokonaisuus, tiedostopolut ja julkaisuperiaatteet.
2. `TRACKING.md` – aihekohtainen aiempi uutisointi, viimeisin luotettava tilanne ja duplikaattien esto.
3. `SOURCES.md` – lähdepolitiikka ja lähdehakujen lähtöpisteet.
4. `tolkien.xml`, `taylor-swift.xml`, `gurmeet-ram-rahim-singh.xml`, `muumit.xml` – julkaistut uutiset ja GUID-tunnisteet.

Tiedostot ovat ajon ensisijainen muistijälki. Älä nojaa pelkästään edellisen ajon keskustelumuistiin. Päivitä dokumentaatiota, kun seurannan rajaus, lähteet tai uutisten tila muuttuu.

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
