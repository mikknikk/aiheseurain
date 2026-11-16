# Tehtäväjono ja seurantavuorot

Tämä tiedosto on tehtäväjonon ensisijainen totuuslähde: se määrittää yhdeksän tehtävän kiertojärjestyksen ja seuraavan vuoron. Yksi automaation käynnistyskerta käsittelee vain yhden tehtävän. Yleiset raportointisäännöt ja koneellisen seurantatilan ohjeet ovat tiedostossa [docs/seuranta.md](seuranta.md). Skriptien kommentointikäytäntö on tiedostossa [docs/kehityskaytannot.md](kehityskaytannot.md).

## Kiinteä kiertojärjestys

1. J. R. R. Tolkien — `feeds/tolkien.xml`
2. Taylor Swift — `feeds/taylor-swift.xml`
3. Saint Dr. Gurmeet Ram Rahim Singh Ji Insan — `feeds/gurmeet-ram-rahim-singh.xml`
4. Muumit — `feeds/muumit.xml`
5. Wakaliwood — `feeds/wakaliwood.xml`
6. Euroviisut ja kansalliset karsinnat — `feeds/euroviisut.xml`
7. Sompote Sands — `feeds/sompote-sands.xml`
8. Shakkidraamat — `feeds/shakkidraamat.xml`
9. Intialaisen elokuvan uutisraportti — `feeds/intialaiset-elokuvat.xml`

## Seuraava tehtävä

**Vuorossa seuraavaksi: J. R. R. Tolkien.**

## Kiertoperiaate

- Käsittele kullakin käynnistyskerralla täsmälleen yksi seuraavaksi merkitty tehtävä. Älä suorita muiden jonotehtävien varsinaisia hakuja samalla ajolla.
- Onnistuneen tehtävän jälkeen siirrä seuraava-tehtävä-merkintä täsmälleen yhden kohdan eteenpäin. Yhdeksännen tehtävän jälkeen kierto alkaa jälleen Tolkienista.
- Jos tehtävän haku, arviointi, mahdollinen julkaisu tai pakollinen takaisinlukutarkistus epäonnistuu tai jää olennaisesti kesken, älä siirrä vuoroa.
- Myös onnistunut tarkistus, jossa ei löydy julkaistavaa uutta tietoa, kuluttaa vuoron.
- Älä muuta tehtävien järjestystä ilman käyttäjän nimenomaista pyyntöä. Älä luo rinnakkaisia automaatioita.
- Nykyinen automaatio käynnistyy päivittäin klo 12.00 Europe/Helsinki. Koska jonossa on yhdeksän tehtävää, kukin tehtävä tarkistetaan normaalisti noin yhdeksän päivän välein. Päivittäinen käynnistys ei tarkoita päivittäistä seurantaa jokaiselle aiheelle.

Intialaisen elokuvan uutisraportti on jonon yhdeksäs tehtävä. Intialaisten elokuvien näytösseuranta ei kuulu tähän jonoon: sitä hoitaa erillinen päivittäinen Intialaisten elokuvien näytösvahti -automaatio. Näytösvahti ei kuluta aihekierroksen vuoroa.
