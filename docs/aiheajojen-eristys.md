# Aiheajojen tekninen eristäminen

**Versio:** 1.1.0  
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

Testaa syötepaketti ja eristetty runner komennolla:

```bash
python -m unittest tests.test_module_input_bundle tests.test_isolated_module_runner -v
```

## Eristyksen rehellinen rajaus

Ensimmäinen toteutus rajaa runnerille annettavan tietosisällön sovellusrajapinnassa. Se estää normaalin runner-kutsun kautta tapahtuvan muiden aiheiden tietojen vuotamisen, mutta ei ole käyttöjärjestelmän tiedostojärjestelmäsandbox: saman prosessin koodi, jolla olisi erikseen pääsy koko repositorion tiedostojärjestelmään, voisi edelleen yrittää avata niitä.

Vahvempi prosessieristys on toteutettu tiedostossa `scripts/isolated_module_runner.py`. Runner käynnistetään Linuxissa `bubblewrap`-mount- ja namespace-sandboxissa. Sandboxiin liitetään vain:
- `/input/bundle.json`: validoitu moduulikohtainen syöte, vain luku;
- `/runner/runner.py`: ajettava ohjelmakoodi, vain luku;
- `/output`: ainoa kirjoitettava pysyvä hakemisto;
- Pythonin suorittamiseen tarvittavat järjestelmäkirjastot, vain luku.

Sandbox käyttää erillisiä user-, PID-, IPC-, UTS- ja network-namespaceja (`--unshare-all`), tyhjennettyä ympäristöä, erillistä `/tmp`-hakemistoa ja eristettyä prosessiryhmää. Päärepon työpuuta, kotihakemistoa, GitHub-tunnuksia, muita moduuleja tai verkkoa ei liitetä sandboxiin. Syöte ja runner-koodi ovat vain luku -muotoisia. Runner voi kirjoittaa vain ennalta luotuun `/output/result.json`-tiedostoon; hakemisto itsessään on vain luku -muotoinen. Tulos luetaan ilman symbolisten linkkien seuraamista vasta prosessin onnistuneen päättymisen jälkeen. Tulostiedoston koko rajataan viiteen mebitavuun, ja runner-prosessille asetetaan CPU-, tiedostokoko-, tiedostokuvaus- ja core-dump-rajat. Aikarajan ylitys, puuttuva bubblewrap tai sandboxin käynnistysvirhe pysäyttää ajon; tavalliseen eristämättömään subprocessiin ei pudota.

Tämä on Linuxin bubblewrap-eristys, ei erillinen virtuaalikone. Runner näkee käyttöjärjestelmän rajatun runtime-näkymän, mutta ei isäntäkoneen yleistä tiedostojärjestelmää. Muilla käyttöjärjestelmillä suoritus estetään, kunnes vastaava sandbox-toteutus lisätään. GitHub Actions asentaa bubblewrapin ja ajaa sandboxin integraatiotestit osana testikokonaisuutta.

Käyttöesimerkki luotetun koordinaattorin puolella:

```python
from scripts.module_input_bundle import build_module_input_bundle
from scripts.isolated_module_runner import run_isolated_module

bundle = build_module_input_bundle(
    "tolkien",
    task_id="tolkien",
    run_id="example-run",
    period_start="2026-11-19T00:00:00+02:00",
    period_end="2026-11-19T23:59:59+02:00",
)
result = run_isolated_module(bundle, runner_source)
```

Runnerin lähdekoodi annetaan merkkijonona, ei repositorion tiedostopolkuna. Runner palauttaa JSON-olion kirjoittamalla `/output/result.json`-tiedoston. Koordinaattori vastaa tuloksen sopimusvalidoinnista ja moduulitilan päivittämisestä; sandbox-funktio ei muuta repositoriota eikä tilatiedostoja.

Tiketti #200 kattaa tämän sandbox-toteutuksen. Tiketti #201 jatkaa kattavia CI-estotestejä ja ristiinviittausten validointia. Tiketti #202 kattaa varsinaisen automaation käynnistysmallin muutoksen.

## Koordinaattorin ja aiheajon vastuut

Koordinaattori saa nähdä tehtäväjonon valintaan tarvittavat tekniset tunnisteet ja tilatiedot. Se ei tee aihekohtaista uutishakua eikä välitä koko tehtäväjonoa aiheajolle. Aiheajo saa vain oman moduulipakettinsa ja palauttaa rajatun tuloksen. Koordinaattori validoi tuloksen ja hoitaa julkaisu- sekä checkpoint-siirtymät yhteisten sopimusten kautta.

Syötepaketin ja sandboxin integraatiotestit suoritetaan CI:ssä. Laajemmat aihemoduulien väliset riippuvuus- ja ristiinviittaustestit kuuluvat tikettiin #201. Pääautomaation käynnistyskehotteen ja varsinaisen ChatGPT-ajon siirtäminen tähän malliin tehdään erikseen (#202). GitHub-muutos ei muuta ChatGPT:n tehtäväasetuksia, ajastuksia tai kohdekeskusteluja.


### Versiohistoria

- **1.1.0 – 2026-11-19:** lisättiin Linux/bubblewrap-sandbox, vain luku -syöte ja runner-koodi, rajattu tuloshakemisto, verkoton namespace, aikaraja sekä fail-closed-käyttäytyminen.
