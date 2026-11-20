# Aiheseurain

Aiheseuraimen toimintamalli määritellään uudelleen yksinkertaiseksi ChatGPT-pohjaiseksi seurantajärjestelmäksi.

## Tavoitetila

- [Uudistetun vaatimusmäärittelyn luonnos (0.3.0)](docs/vaatimusmaarittely-uudistus.md) kuvaa uuden tavoitetilan. Se on luonnos, jota tarkennetaan ennen uuden toteutuksen rakentamista.
- Valvomo on ensisijainen käyttöliittymä. RSS-lukija ja Kehitysjono säilyvät erillisinä käyttötarkoituksina.
- Aiheiden ja seurantatyyppien tulee olla dynaamisia määrityksiä, eivät yleiseen toteutukseen kovakoodattuja.
- ChatGPT tekee tutkimus- ja raportointityön. GitHub vastaanottaa ja validoi rakenteiset ajotulokset sekä julkaisee hyväksytyt RSS-itemit.

## Nykyinen julkaistu sisältö

Nykyiset [GitHub Pages -sivut](https://mikknikk.github.io/aiheseurain/) ja [RSS-syötteet](feeds/) on säilytetty. Vanhat Pages-julkaisu- ja CI-työnkulut on siirretty arkistoon osana uudelleenkäynnistystä. Siksi sivusto pysyy viimeisimmässä julkaistussa tilassaan, kunnes uusi julkaisupolku rakennetaan.

## Historia ja arkisto

Julkaistut RSS-syötteet, raportit sekä seuranta- ja näytöshistoria on säilytetty alkuperäisissä sijainneissaan. Vanha toteutus, sen työnkulut, koodit, testit, skeemat, esimerkit, kehotteet ja vanhentuneet ohjeet on siirretty hakemistoon [archive/legacy-implementation-2026-11-20](archive/legacy-implementation-2026-11-20/).

Arkisto on palautettavissa. Arkistoidut GitHub Actions -tiedostot eivät enää sijaitse `.github/workflows/`-hakemistossa eivätkä siksi käynnisty.

## Kehittämisen periaatteet

- Noudata [saavutettavuusohjeita](docs/saavutettavuus.md); WCAG 2.2 AAA -tasoa ei väitetä ilman testausta.
- Noudata [kehityskäytäntöjä](docs/kehityskaytannot.md).
- Noudata [automaatioiden hallinnan suojausperiaatteita](docs/automaation-hallintaperiaatteet.md): ChatGPT-tehtävien ajastuksia, asetuksia tai kohdekeskusteluja ei muuteta ilman erillistä lupaa.
- Älä muuta tai poista julkaistua RSS-historiaa.
