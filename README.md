# Aiheseurain

Aiheseurain on raporttituottajariippumaton seuranta-, vastaanotto-, validointi- ja julkaisujärjestelmä. Raportin voi tuottaa ihminen, tekoäly tai ohjelmisto.

## Tavoitetila

- [Uudistetun vaatimusmäärittelyn luonnos (0.12.10)](docs/vaatimusmaarittely-uudistus.md) kuvaa yksinkertaistetun tavoitetilan. Yksi käynnistys käsittelee enintään yhden aiheen; batch-ajot ja ulkoiset ilmoitukset on rajattu ensimmäisen version ulkopuolelle. Osittaiset raportit julkaistaan, jos niistä syntyy validoitu item; puutteet kuvataan avoimesti.
- [Toteutussuunnitelma (0.3.51)](docs/toteutussuunnitelma.md) kokoaa hyväksytyt arkkitehtuuriperiaatteet ja avoimet tekniset päätökset. Tehtävän muodostus, määräajan valvonta ja toimituksen vastaanotto/käsittely kuuluvat yhteisen instanssikohtaisen sarjallisuuden hallinnan piiriin. Suunnitelma määrittelee myös rajatun myöhäisten toimitusten jälkikäsittelyn: vanha tulos voidaan hyväksyä alkuperäiselle ajolle vain, jos myöhempää saman aiheen ja seurantatyypin ajoa ei ole käynnistetty. Myöhäisen toimituksen käsittely esitetään aikajärjestyksessä säilyvinä tapahtumina: määräajan ylitys, myöhäinen vastaanotto, validointi, hyväksyntä/hylkäys ja mahdollinen julkaisu. Myöhemmät tapahtumat eivät korvaa aiempia. Suunnitelman hyväksyminen ja toteutuksen aloittaminen ovat erillisiä päätöksiä.
- Kehitystehtäviä hallitaan GitHub Issuesissa ja [Aiheseurain-GitHub Projectissa](https://github.com/users/mikknikk/projects/3). Issue-labelit ovat tilan, prioriteetin ja komponentin ensisijaiset tiedot; Projectin Status- ja Priority-kentät synkronoidaan niistä automaattisesti.
- GitHub Issuesin natiivit riippuvuudet ovat riippuvuuksien ainoa tietolähde. Katso [riippuvuuksien hallintaohje](docs/github-riippuvuuksien-hallinta.md).
- Project-kenttien automaattinen päivitys on kuvattu [Project-synkronoinnin ohjeessa](docs/github-project-synkronointi.md).
- Valvomo ja RSS-lukija ovat instanssikohtaisia käyttöliittymiä, joiden yhteinen toteutuskoodi kuuluu jaettavaan ohjelmistoon. Molemmat voivat olla ensimmäisessä versiossa julkisia; niiden tietolähteisiin ei sisällytetä salaisuuksia tai yksityisiä tietoja.
- Aiheiden ja seurantatyyppien tulee olla dynaamisia määrityksiä, eivät yleiseen toteutukseen kovakoodattuja.
- Raporttituottaja tekee tutkimus- ja raportointityön. Aiheseurain vastaanottaa ja validoi rakenteiset ajotulokset sekä julkaisee hyväksytyt RSS-itemit.

## Nykyinen julkaistu sisältö

Nykyiset [GitHub Pages -sivut](https://mikknikk.github.io/aiheseurain/) säilyvät. Oma Kehitysjono-Kanban-käyttöliittymä ja sen JSON-välimuisti on poistettu käytöstä; kehitystehtäviä tarkastellaan GitHub Projectissa. Projectin Status- ja Priority-synkronointi toimii erillisenä GitHub Actions -työnkulkuna. RSS-syötteitä tai aihekohtaisia seurantatehtäviä tämä synkronointi ei muuta.

## Historia ja arkisto

Kehitysjonon aiempi selainkäyttöliittymä, JSON-välimuisti, niiden muodostus- ja riippuvuusautomaatiot, testit sekä tekniset ohjeet on siirretty palautettavina tiedostoina hakemistoon [archive/kehitysjono-2026-11-20](archive/kehitysjono-2026-11-20/).

Aiempi laajempi toteutus ja julkaistu RSS-/raporttihistoria on säilytetty hakemistossa [archive/legacy-implementation-2026-11-20](archive/legacy-implementation-2026-11-20/). Julkaistua RSS-historiaa ei ole muutettu.

Ajastettujen ChatGPT-kehotteiden uusi kanoninen versiohallinta sijaitsee aktiivisessa [prompts-hakemistossa](prompts/). GitHub Actionsin aktiiviset työnkulut on rajattu nykyisiin toimintoihin; arkistoidut työnkulut eivät käynnisty.

## Kehittämisen periaatteet

- Noudata [saavutettavuusohjeita](docs/saavutettavuus.md); WCAG 2.2 AAA -tasoa ei väitetä ilman testausta.
- Noudata [kehityskäytäntöjä](docs/kehityskaytannot.md).
- Noudata [dokumentaation automaattista laaduntarkistusta](docs/dokumentaation-laaduntarkistus.md).
- Noudata [automaatioiden hallinnan suojausperiaatteita](docs/automaation-hallintaperiaatteet.md): ChatGPT-tehtävien ajastuksia, asetuksia tai kohdekeskusteluja ei muuteta ilman erillistä lupaa.
- Älä muuta tai poista julkaistua RSS-historiaa.
