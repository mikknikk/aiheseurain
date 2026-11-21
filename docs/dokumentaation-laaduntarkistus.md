# Dokumentaation automaattinen laaduntarkistus

## Tarkoitus

Aiheseuraimen dokumentaation laaduntarkistus ehkäisee rakenteellisia virheitä, joita voi syntyä esimerkiksi dokumenttia päivitettäessä tai sisältöä kopioitaessa. Tarkistus suoritetaan GitHub Actionsissa, kun README:tä, docs/-hakemiston Markdown-tiedostoja tai tarkistuksen omaa koodia muutetaan.

Tarkistus täydentää ihmisen tekemää katselmointia. Se ei arvioi tekstin asiasisällön oikeellisuutta, ymmärrettävyyttä tai saavutettavuutta kokonaisuutena eikä väitä WCAG-vaatimusten täyttymistä.

## Tarkistettavat asiat

1. **Pääotsikko:** jokaisessa tarkistettavassa Markdown-tiedostossa on täsmälleen yksi H1-pääotsikko.
2. **Otsikkohierarkia:** otsikkotasoja ei ohiteta, esimerkiksi H1-otsikosta ei siirrytä suoraan H3-otsikkoon.
3. **Versionumeromerkintä:** Versio-merkintä esiintyy dokumentissa enintään kerran. Jos dokumentissa ei käytetä versionumeromerkintää, tarkistus ei vaadi sen lisäämistä.
4. **Toistuva sisältö:** täsmälleen saman otsikon ja saman sisältöosion toistuminen havaitaan kopiointivirheenä.
5. **README-yhteensopivuus:** README:ssä versionumeron yhteydessä linkitetyn versionhallittavan dokumentin versionumeron on vastattava dokumentin omaa versionumeromerkintää.
6. **Sisäiset linkit:** suhteellisten Markdown-linkkien kohdetiedostojen on oltava olemassa. Markdown-kohteiden otsikkoankkurien on vastattava kohdedokumentin otsikkoa.
7. **Testit:** tarkistusskriptin toimintaa testataan sekä kelvollisilla että tarkoituksella virheellisillä esimerkkidokumenteilla.

Ulkoisia verkkolinkkejä ei avata eikä niiden saatavuutta tarkisteta. Tarkistus ei myöskään muuta dokumentteja automaattisesti.

## Käyttö

Tarkistuksen voi ajaa repositorion juuressa komennolla:

    node .github/scripts/check_markdown_docs.mjs

Yksikkötestit suoritetaan komennolla:

    node --test tests/markdown-docs.test.mjs

GitHub Actions suorittaa molemmat komennot dokumentaatiomuutosten yhteydessä. Virheellinen tulos epäonnistuttaa työnkulun.

## Rajaukset

- Tarkistus kattaa README.md-tiedoston ja docs/-hakemiston Markdown-tiedostot.
- Arkistoituja dokumentteja, käynnistyskehotteita ja muita Markdown-tiedostoja ei tarkisteta automaattisesti tällä työnkululla.
- Muutoshistorian merkintöjen sisällöllistä oikeellisuutta ei voida päätellä luotettavasti pelkästä Markdown-rakenteesta; ylläpitäjä vastaa siitä, että dokumentin oma muutoshistoria päivitetään.
- Tarkistuksen läpäisy ei korvaa ihmisen tekemää sisällön, linkkitekstien, saavutettavuuden tai dokumenttien keskinäisen johdonmukaisuuden katselmointia.

## Ylläpito

Kun tarkistussääntöä muutetaan, päivitä vastaavat yksikkötestit ja tämä dokumentti samassa muutoksessa. Skriptin tulee pysyä riippumattomana ulkoisista npm-paketeista, jotta tarkistus toimii suoraan GitHub Actionsin Node.js-ympäristössä. Työnkulun GitHub Actions -toimintojen versiot pidetään ajan tasalla ja niiden tulee käyttää tuettua Node.js-suoritusaikaa.
