# Aiheajojen tekninen eristäminen

**Versio:** 1.0.0  
**Päiväys:** 2026-11-19  
**Liittyvät tiketit:** [#199 – Eristetyn syötepaketin sopimus](https://github.com/mikknikk/aiheseurain/issues/199), [#200 – Eristetty suoritusympäristö](https://github.com/mikknikk/aiheseurain/issues/200), [#201 – Eristyksen CI-estot](https://github.com/mikknikk/aiheseurain/issues/201), [#202 – Pääautomaation siirto moduulikäynnistykseen](https://github.com/mikknikk/aiheseurain/issues/202)

## Tavoite

Jokainen aiheajo käsittelee vain yhden aihemoduulin sisältöä. Yhteinen koordinaattori valitsee tehtävän ja muodostaa moduulille rajatun syötepaketin. Aihekohtainen suorittaja ei saa lukea muiden aiheiden määrityksiä, lähteitä, kohteita, tilaa tai historiaa.

Yhteinen tekninen ydin sisältää vain yleiset sopimukset: ajon tunnisteen ja seurantajakson, suorituspyynnön, laadunvarmistusrajapinnan, rajatun tuloksen, tallennus- ja julkaisusovittimet sekä virheiden eristyksen. Se ei sisällä aiheiden hakutermejä tai toimituksellisia sisältöohjeita.

Näytösvahti pysyy erillisenä päivittäisenä process-moduulina. Se ei kuulu yhdeksän uutisaiheen kiertoon eikä tämän työn ensimmäiseen tuotantokytkentään.

## Syötepaketin sisältö

scripts/module_input_bundle.py muodostaa yhden moduulin paketin seuraavista tiedoista:

- moduulin oma määritys;
- vain moduulin target_refs-viitteisiin kuuluvat seurantakohteet;
- vain moduulin source_refs-viitteisiin kuuluvat lähteet yhteisestä katalogista;
- saman aiheen lähdekäyttörekisterin tarkistusajat, käyttörajat ja retry_after-arvot;
- vain moduulin viimeisin checkpoint ja oman julkaisusyötteen GUID-viitteet;
- ajon tunniste ja seurantajakso.

Paketista jätetään pois moduulirekisteri, koko kohde- ja lähderekisteri, kaikkien aiheiden seurantatila, yhteiset vanhat tilaviitteet, muiden moduulien historia sekä automaatioiden asetukset ja käynnistyskehotteet. Lähdekatalogista luovutetaan vain moduulin source_refs-listassa nimetyt lähteet.

schemas/module-input-bundle.schema.json määrittelee paketin rakenteen. Paketin rakentaja tarkistaa moduulin, kohteiden, lähteiden ja lähdekäyttörekisterin omistajuuden ennen tietojen luovutusta. Runnerille annettava rakenne on rekursiivisesti vain luku -muotoinen.

Testaa paketin sisältö ja sopimus komennolla:

```bash
python -m unittest tests.test_module_input_bundle -v
```

## Eristyksen rehellinen rajaus

Ensimmäinen toteutus rajaa runnerille annettavan tietosisällön sovellusrajapinnassa. Se estää normaalin runner-kutsun kautta tapahtuvan muiden aiheiden tietojen vuotamisen, mutta ei ole käyttöjärjestelmän tiedostojärjestelmäsandbox: saman prosessin koodi, jolla olisi erikseen pääsy koko repositorion tiedostojärjestelmään, voisi edelleen yrittää avata niitä.

Vahvempi eristys toteutetaan erillisessä työtilassa tai prosessissa, johon kopioidaan vain validoitu syötepaketti ja tarvittavat tekniset ajonaikaiset rajapinnat. Runnerille ei anneta päärepon juuripolkua eikä käyttöoikeutta päärepon tiedostoihin. Tätä jatkaa tiketti #200.

## Koordinaattorin ja aiheajon vastuut

Koordinaattori saa nähdä tehtäväjonon valintaan tarvittavat tekniset tunnisteet ja tilatiedot. Se ei tee aihekohtaista uutishakua eikä välitä koko tehtäväjonoa aiheajolle. Aiheajo saa vain oman moduulipakettinsa ja palauttaa rajatun tuloksen. Koordinaattori validoi tuloksen ja hoitaa julkaisu- sekä checkpoint-siirtymät yhteisten sopimusten kautta.

Aihemoduulien väliset riippuvuudet ja syötepaketin sisältörajoitukset testataan CI:ssä (#201). Pääautomaation käynnistyskehotteen ja varsinaisen ChatGPT-ajon siirtäminen tähän malliin tehdään erikseen (#202). GitHub-muutos ei muuta ChatGPT:n tehtäväasetuksia, ajastuksia tai kohdekeskusteluja.
