# Kehityskäytännöt

Tämä dokumentti määrittää repositorion skriptien ja muun ylläpitokoodin kirjoittamisen vähimmäiskäytännöt.

## Python-skriptien kommentointi

Jokainen uusi skripti kirjoitetaan alusta lähtien yhtä huolellisesti kommentoiduksi kuin `scripts/validate_feeds.py`.

- Kirjoita kommentit ja docstring-kuvaukset suomeksi.
- Aloita tiedosto docstringillä, joka kertoo ymmärrettävästi skriptin tarkoituksen, tärkeimmät tehtävät ja mahdolliset vaikutukset tiedostoihin tai muihin järjestelmiin.
- Lisää moduulin tärkeisiin osiin, funktioihin ja luokkiin docstring tai selittävä kommentti. Kerro, mitä osa tekee, miksi se on olemassa ja mitä tietoja se käsittelee.
- Selitä erityisesti aloittelijalle vaikeat kohdat, kuten tietorakenteet, tiedostopolut, XML/HTML-käsittely, aikavyöhykkeet, virhetilanteet, ulkoisten rajapintojen käyttö ja tietojen validointi.
- Kommentoi myös toimintalogiikan kannalta olennaiset vaiheet ja päätökset. Älä kuitenkaan lisää kommenttia jokaiselle itsestään selvälle riville.
- Käytä kuvaavia muuttuja-, funktio- ja luokkanimiä. Kommenttien tehtävä on täydentää koodia, ei korvata selkeitä nimiä.
- Pidä kommentit ajan tasalla aina, kun koodin toimintaa muutetaan. Virheellinen tai vanhentunut kommentti on korjattava samalla kertaa.
- Suosi pieniä, ymmärrettäviä funktioita ja selkeää rakennetta. Jos ratkaisu on monimutkainen, selitä sen toimintaperiaate ennen vaikeaa koodiosuutta.
- Säilytä olemassa olevan koodin toiminta, ellei käyttäjä nimenomaisesti pyydä toiminnallista muutosta.

## Tarkistus ennen muutoksen valmistumista

Kun uusi skripti lisätään tai olemassa olevaa muutetaan:

1. Lue skripti kokonaan läpi myös sellaisen ihmisen näkökulmasta, joka osaa Pythonin perusteet mutta ei tunne projektia.
2. Varmista, että tiedoston tarkoitus, tärkeät funktiot, keskeiset vaiheet ja ei-ilmeiset ratkaisut on selitetty suomeksi.
3. Tarkista, että kommentit vastaavat täsmälleen toteutunutta toimintaa.
4. Aja soveltuvat testit ja korjaa havaitut virheet.
5. Päivitä tarvittaessa README ja muu dokumentaatio vastaamaan uutta tai muuttunutta skriptiä.

Tavoitteena on, että myös Pythonia vähemmän osaava ylläpitäjä pystyy seuraamaan skriptin toimintaa, ymmärtämään sen keskeiset ratkaisut ja tekemään siihen turvallisia muutoksia.
