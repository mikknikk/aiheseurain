# Aiheseurain

Aiheseuraimen toimintamalli määritellään uudelleen yksinkertaiseksi ChatGPT-pohjaiseksi seurantajärjestelmäksi.

## Tavoitetila

- [Uudistetun vaatimusmäärittelyn luonnos (0.5.0)](docs/vaatimusmaarittely-uudistus.md) kuvaa uuden tavoitetilan. Se on edelleen luonnos, jota tarkennetaan ennen laajempaa aihekohtaista tuotantototeutusta.
- Kehitystehtäviä hallitaan GitHub Issuesissa ja [Aiheseurain-GitHub Projectissa](https://github.com/users/mikknikk/projects/3). Issue-labelit ovat tilan, prioriteetin ja komponentin ensisijaiset tiedot; Projectin Status- ja Priority-kentät synkronoidaan niistä automaattisesti.
- GitHub Issuesin natiivit riippuvuudet ovat riippuvuuksien ainoa tietolähde. Katso [riippuvuuksien hallintaohje](docs/github-riippuvuuksien-hallinta.md).
- Project-kenttien automaattinen päivitys on kuvattu [Project-synkronoinnin ohjeessa](docs/github-project-synkronointi.md).
- Valvomo on tavoiteltu ensisijainen käyttöliittymä. RSS-lukija säilyy erillisenä käyttötarkoituksena.
- Aiheiden ja seurantotyyppien tulee olla dynaamisia määrityksiä, eivät yleiseen toteutukseen kovakoodattuja.
- ChatGPT tekee tutkimus- ja raportointityön. GitHub vastaanottaa ja validoi rakenteiset ajotulokset sekä julkaisee hyväksytyt RSS-itemit.

## Nykyinen julkaistu sisältö

Nykyiset [GitHub Pages -sivut](https://mikknikk.github.io/aiheseurain/) säilyvät. Oma Kehitysjono-Kanban-käyttöliittymä ja sen JSON-välimuisti on poistettu käytöstä; kehitystehtäviä tarkastellaan GitHub Projectissa. Projectin Status- ja Priority-synkronointi toimii erillisenä GitHub Actions -työnkulkuna. RSS-syötteitä tai aihekohtaisia seurantatehtäviä tämä synkronointi ei muuta.

## Historia ja arkisto

Kehitysjonon aiempi selainkäyttöliittymä, JSON-välimuisti, niiden muodostus- ja riippuvuusautomaatiot, testit sekä tekniset ohjeet on siirretty palautettavina tiedostoina hakemistoon [archive/kehitysjono-2026-11-20](archive/kehitysjono-2026-11-20/).

Aiempi laajempi toteutus ja julkaistu RSS-/raporttihistoria on säilytetty hakemistossa [archive/legacy-implementation-2026-11-20](archive/legacy-implementation-2026-11-20/). Julkaistua RSS-historiaa ei ole muutettu.

Ajastettujen ChatGPT-kehotteiden uusi kanoninen versiohallinta sijaitsee aktiivisessa [prompts-hakemistossa](prompts/). GitHub Actionsin aktiiviset työnkulut on rajattu nykyisiin toimintoihin; arkistoidut työnkulut eivät käynnisty.

## Kehittämisen periaatteet

- Noudata [saavutettavuusohjeita](docs/saavutettavuus.md); WCAG 2.2 AAA -tasoa ei väitetä ilman testausta.
- Noudata [kehityskäytäntöjä](docs/kehityskaytannot.md).
- Noudata [automaatioiden hallinnan suojausperiaatteita](docs/automaation-hallintaperiaatteet.md): ChatGPT-tehtävien ajastuksia, asetuksia tai kohdekeskusteluja ei muuteta ilman erillistä lupaa.
- Älä muuta tai poista julkaistua RSS-historiaa.
