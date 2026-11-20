# Aiheseurain

Aiheseuraimen toimintamalli määritellään uudelleen yksinkertaiseksi ChatGPT-pohjaiseksi seurantajärjestelmäksi.

## Tavoitetila

- [Uudistetun vaatimusmäärittelyn luonnos (0.5.0)](docs/vaatimusmaarittely-uudistus.md) kuvaa uuden tavoitetilan. Se on edelleen luonnos, jota tarkennetaan ennen laajempaa aihekohtaista tuotantototeutusta.
- Kehitysjono käyttää aktiivista [JSON-välimuistia ja päivitystyönkulkua](docs/kehitysjonon-aineisto.md) sekä [GitHubin natiiveihin riippuvuuksiin perustuvaa hallintaa](docs/github-riippuvuuksien-hallinta.md).
- Valvomo on ensisijainen käyttöliittymä. RSS-lukija ja Kehitysjono säilyvät erillisinä käyttötarkoituksina.
- Aiheiden ja seurantatyyppien tulee olla dynaamisia määrityksiä, eivät yleiseen toteutukseen kovakoodattuja.
- ChatGPT tekee tutkimus- ja raportointityön. GitHub vastaanottaa ja validoi rakenteiset ajotulokset sekä julkaisee hyväksytyt RSS-itemit.

## Nykyinen julkaistu sisältö

Nykyiset [GitHub Pages -sivut](https://mikknikk.github.io/aiheseurain/) säilyvät. Kehitysjonon JSON-aineiston päivitys ja sen testit ovat nyt aktiivisia erillisiä GitHub Actions -työnkulkuja. Vanha yleinen Pages/RSS-julkaisuprosessi on edelleen arkistoitu; Kehitysjonon tietopäivitys ei julkaise RSS-syötteitä eikä käynnistä aihekohtaisia seurantatehtäviä.

## Historia ja arkisto

Julkaistut RSS-syötteet, raportit sekä seuranta- ja näytöshistoria on säilytetty alkuperäisissä sijainneissaan. Vanha toteutus, sen työnkulut, koodit, testit, skeemat, esimerkit ja vanhentuneet ohjeet on siirretty hakemistoon [archive/legacy-implementation-2026-11-20](archive/legacy-implementation-2026-11-20/).

Ajastettujen ChatGPT-kehotteiden uusi kanoninen versiohallinta sijaitsee aktiivisessa [prompts-hakemistossa](prompts/). Arkisto on palautettavissa. Vain nykyiset, aktiiviset työnkulut sijaitsevat `.github/workflows/`-hakemistossa; arkistoidut työnkulut eivät käynnisty.

## Kehittämisen periaatteet

- Noudata [saavutettavuusohjeita](docs/saavutettavuus.md); WCAG 2.2 AAA -tasoa ei väitetä ilman testausta.
- Noudata [kehityskäytäntöjä](docs/kehityskaytannot.md).
- Noudata [automaatioiden hallinnan suojausperiaatteita](docs/automaation-hallintaperiaatteet.md): ChatGPT-tehtävien ajastuksia, asetuksia tai kohdekeskusteluja ei muuteta ilman erillistä lupaa.
- Älä muuta tai poista julkaistua RSS-historiaa.
