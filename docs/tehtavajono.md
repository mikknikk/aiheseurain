# Tehtäväjono ja seurantavuorot

Tämä tiedosto on tehtäväjonon ainoa ensisijainen totuuslähde. Jonossa on yhdeksän erillistä seurantatehtävää. Yksi automaation käynnistyskerta käsittelee vain yhden tehtävän.

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

## Seurantajakson aikaväli – pakollinen raportointisääntö

- Ilmoita jokaisessa seurantaraportissa seurantajakson alku ja loppu muodossa `Seurantajakso: 16.11.2026 klo 12.00 – 26.11.2026 klo 12.00 (Europe/Helsinki)`.
- Jakso alkaa kyseisen tehtävän edellisen onnistuneen tarkistuksen ajankohdasta ja päättyy nykyisen tarkistuksen ajankohtaan. Älä käytä edellisen automaation ajankohtaa, jos kyseinen tehtävä ei ollut silloin vuorossa.
- Ensimmäisessä tarkistuksessa käytä dokumentoitua seurannan aloituspäivää ja kerro, että kyseessä on ensimmäinen tarkistus.
- Jos tarkkaa aiempaa kellonaikaa ei ole dokumentoitu, ilmoita tunnettu päivämäärä ja merkitse kellonaika tuntemattomaksi. Älä keksi aikaväliä.
- Erota uutisen julkaisu- ja tapahtumapäivä seurantajakson aikavälistä.
- Ilmoita aikaväli myös silloin, kun uutta merkittävää tietoa ei löydy tai RSS:ää ei päivitetä.
- Päivitä tehtäväkohtainen viimeisin onnistunut tarkistus ja sen aikaleima dokumentaatioon.

Intialaisen elokuvan uutisraportti on jonon yhdeksäs tehtävä. Intialaisten elokuvien näytösseuranta EI kuulu tähän jonoon: sitä hoitaa erillinen päivittäinen Intialaisten elokuvien näytösvahti -automaatio, joka käyttää samaa uutiset-repositoriota. Näytösvahti tarkistaa näytökset päivittäin eikä kuluta aihekierroksen vuoroa.
## Koneellinen seurantatila ja automaattiset testit

- data/seurantatila.json on koneellisesti luettava rinnakkaistila. Sen rotation.next_task-arvon pitää vastata tämän tiedoston seuraava-tehtävä-merkintää.
- Päivitä kyseisen tehtävän last_successful_check, last_period_start, last_period_end, last_result, published_items ja sources_checked vasta, kun tarkistus on onnistunut ja kaikki tarvittavat GitHub-kirjoitukset on luettu takaisin.
- Käytä ISO 8601 -aikaleimoja aikavyöhyketietoineen. Älä päättele vanhoja tarkkoja aikoja jälkikäteen. Tuntematon arvo säilyy null-arvona.
- Erillisen näytösvahdin tila kirjataan JSON-tiedoston separate_screening_watch-osioon. Se ei muuta rotation.next_task-arvoa.
- GitHub Actions ajaa scripts/validate_feeds.py-testin push- ja pull request -muutoksissa. Testi tarkistaa RSS/XML-rakenteet, GUIDit, item-linkkien kiellon, CDATA-descriptionit, lähdeluettelot ja seurantatilan JSONin.
- Jos automaattinen testi epäonnistuu, korjaa virhe ennen julkaisun pitämistä valmiina. Testin läpäisy ei kuitenkaan todista uutisten faktatarkkuutta eikä WCAG AAA -vaatimusten täyttymistä.
