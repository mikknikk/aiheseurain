# Vanhan toteutuksen arkisto

**Arkistointipäivä:** 20.11.2026  
**Lähtökohta:** Aiheseuraimen vaatimusmäärittelyn uudistus, yksinkertainen ChatGPT-toimintamalli.

Tämä hakemisto säilyttää vanhan toteutuksen tiedostot ennen uudelleenrakentamista. Tiedostot on siirretty alkuperäistä hakemistorakennetta jäljitteleviin polkuihin tämän hakemiston alle. Arkistointi ei tarkoita, että sisältö olisi poistettu tai että sen palauttaminen olisi mahdotonta.

## Mitä arkisto sisältää?

- vanhat GitHub Actions -työnkulut ja niiden apuskriptit;
- moduuli-, reititys-, varjoharjoitus-, julkaisu- ja validointitoteutukset;
- vanhat skeemat, testit ja esimerkit;
- vanhentuneet arkkitehtuuri-, aihe- ja käyttöohjeet;
- vanhat automaatiokehotteet.

## Mikä säilytettiin aktiivisessa puussa?

Julkaistut RSS-syötteet, raportit ja historialliset seuranta-aineistot säilytettiin alkuperäisissä sijainneissaan. Nykyinen staattinen sivustolähdekoodi säilytettiin uudelleenrakentamisen lähtökohdaksi. Uusi vaatimusmäärittely sekä yleiset saavutettavuus-, kehitys- ja automaationhallintaohjeet säilytettiin aktiivisina dokumentteina.

## GitHub Actions

Arkistoidut työnkulkutiedostot eivät enää ole `.github/workflows/`-hakemistossa. Ne eivät käynnisty. Vanha Pages-julkaisu ei päivity automaattisesti eikä vanha CI validoi uusia muutoksia ennen kuin korvaavat työnkulut rakennetaan.

Palautus tehdään siirtämällä tarvittavat tiedostot takaisin alkuperäisiin polkuihin erillisessä muutoksessa. Työnkulkuja ei pidä palauttaa sokkona: niiden riippuvuudet, salaisuudet, vaaditut status check -tarkistukset ja tuotantovaikutukset on arvioitava ensin.
