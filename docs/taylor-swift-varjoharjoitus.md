# Taylor Swift -moduulin rajattu varjoharjoitus

**Liittyvä tiketti:** [#246 – Toteuta Taylor Swift -moduulin rajattu varjoharjoitus ilman tuotantojulkaisua](https://github.com/mikknikk/aiheseurain/issues/246)  
**Hyväksyntäaineisto:** [#242 – Taylor Swift -pilotoinnin hyväksyntänäyttö](https://github.com/mikknikk/aiheseurain/issues/242)

## Tarkoitus ja rajaus

Tämä ohje kuvaa Taylor Swift -moduulin teknistä valmistelua ja myöhempää, erikseen hyväksyttävää varjoharjoitusta. Valmistelukoodi ei käynnistä tutkimusta eikä anna lupaa live-ajoon. Varsinainen tutkimus voidaan tehdä vasta, kun käyttäjä on hyväksynyt juuri kyseisen harjoituksen erikseen.

Varjoharjoitus ei ole tuotantosiirtymä. Se ei saa julkaista RSS:ää tai muuttaa Pages-sivua, julkaisumanifestia, moduulin tuotantocheckpointia, moduulitilaa, tuotannon julkaisupäiväkirjaa, tehtäväjonoa tai ChatGPT-automaation asetuksia.

## Nykyinen tekninen lähtökohta

- Moduuli on `taylor-swift`, tyyppiä `topic`, ja rekisterissä `inactive`.
- Tuotantoaktivointilipun pitää olla eksplisiittisesti `false`.
- Moduulilla on yksi oma kohde ja erillinen lähderekisteri.
- Julkaisurekisterin ja julkaisureitityksen pitää olla tyhjiä ennen valmistelua.
- Historiallisessa `data/module-state/taylor-swift.json`-tiedostossa on puuttuvia tietoja. Sitä ei validoida harjoituksen lähtötilaksi, täydennetä eikä käytetä harjoituksen checkpointina.
- `module-runtime-state`-haaraa ei valmistelussa luoda. Runtime-haaran ja tuotannon julkaisupäiväkirjan tilaa ei väitetä varmennetuksi.

## Harjoituskohtainen lähtötila

`scripts/taylor_swift_shadow.py` muodostaa `prepare_taylor_swift_shadow`-funktiolla erillisen tyhjän varjolähtötilan. Se vaatii yhden eksplisiittisen `run_id`-tunnisteen, aikavyöhykkeelliset seurantajakson rajat ja valmisteluhetken.

Valmistelu tarkistaa moduulin ja kohteen omistajuuden, moduulin tyypin ja tilan, lähdeviitteiden vastaavuuden, oman RSS-syötteen rekisteröinnin, aktivointilipun sekä tyhjät julkaisurekisterit ja -reitityksen. Se rakentaa lisäksi olemassa olevalla `module_input_bundle.py`-rakentajalla varsinaisen moduulikohtaisen ChatGPT-syötepaketin synteettisellä tyhjällä moduulitilalla; paketin tiiviste sidotaan valmisteluasiakirjaan. Syötetiedostojen SHA-256-tiivisteet sidotaan valmisteluasiakirjaan. Historiallisesta checkpointista säilytetään vain tiedostoviite ja tiiviste; sen puuttuvia kenttiä ei tulkita eikä korjata.

Tuotanto-RSS:n GUID- ja julkaisupäivistä tehdään varovainen saman päivävälin kaksoistuloseste. Päivämääräosuma ei todista itemin todellista seurantajaksoa, joten epäselvä osuma pysäyttää valmistelun manuaaliseen tarkistukseen. Vastaavasti päivämääräosuman puuttuminen ei yksin riitä osoittamaan, ettei muualla ole saman jakson julkaisua.

Valmisteluasiakirjan sopimus on `schemas/taylor-swift-shadow-preparation.schema.json`; tulosartefaktin sopimus on `schemas/taylor-swift-shadow-result.schema.json`. Se merkitsee aina `execution_authorized`, `research_performed`, `publication_performed` ja `production_state_written` arvoiksi `false`. Lähteiden ajantasaisuutta ei tarkisteta valmisteluvaiheessa.

Esimerkki teknisestä valmistelusta (ei tee tutkimusta):

```python
from pathlib import Path
from scripts.taylor_swift_shadow import prepare_taylor_swift_shadow

preparation = prepare_taylor_swift_shadow(
    run_id="swift-shadow-20261120-01",
    period_start="2026-11-19T00:00:00+02:00",
    period_end="2026-11-19T23:59:59+02:00",
    requested_at="2026-11-20T12:00:00+02:00",
    root=Path("."),
)
```

`write_shadow_artifact` tallentaa valmistelu- tai tulosartefaktin vain polkuun `data/shadow-exercises/taylor-swift/{run_id}/`. Se ei ylikirjoita olemassa olevaa tiedostoa eikä hyväksy toisen moduulin tunnistetta.

## ChatGPT-tuloksen rajattu vastaanotto

`scripts/taylor_swift_shadow_result.py` tarjoaa tulosadapterin jo tuotetulle ChatGPT JSON -tulokselle. Se käyttää olemassa olevaa `schemas/chatgpt-module-result.schema.json`-sopimusta ja `validate_chatgpt_result`-tarkistusta sekä sitoo tuloksen samaan moduuliin, versioon, `run_id`-tunnisteeseen, seurantajaksoon ja valmistelussa laskettuun `handoff_input_sha256`-tiivisteeseen. Kohderaportit rajataan Taylor Swiftin omaan kohteeseen.

Adapteri vaatii erillisen hyväksynnän viitteen. Se ei tee verkkohakuja, kutsu automaatiota, luo ajastusta tai käynnistä harjoitusta. Se palauttaa erillisen varjotulosolion, jonka tuotantojulkaisu- ja tuotantotilakirjaukset ovat eksplisiittisesti `false`.

## Varsinaisen harjoituksen hyväksyntäportti

Varsinaista harjoitusta ei saa käynnistää teknisen valmistelun perusteella. Ennen sitä on:

1. saatava käyttäjän erillinen, nimenomainen hyväksyntä juuri tähän harjoitusajoon;
2. valittava yksi tarkka seurantajakso ja yksilöllinen `run_id`;
3. tarkistettava lähtötilan tiivisteet uudelleen ja varmistettava, että ne vastaavat hyväksyttyä valmistelua;
4. tarkistettava ajantasaiset lähteet sekä saman seurantajakson aiempi julkaisu myös kaikista auktoritatiivisista runtime-/julkaisulokeista;
5. keskeytettävä, jos runtime-tila, kaksoisjulkaisutarkistus tai jokin muu olennainen tila on tuntematon tai ristiriitainen.

Vasta hyväksynnän jälkeen ChatGPT voi tehdä varsinaisen tutkimuksen moduulin omalla lähdepaketilla. Raportti ja auditointitiedot tallennetaan vain harjoitusartefakteina. PR-, Pages- ja julkisen RSS:n tapahtumia ei merkitä onnistuneiksi, jos niitä ei ole tehty.

## Testaus

Valmistelun ja tulosadapterin regressiotestit:

```bash
python -m unittest tests.test_taylor_swift_shadow tests.test_taylor_swift_shadow_result -v
```

Testit kattavat moduuli- ja kohdeomistajuuden, lähdeviitteet, aktivointilipun, julkaisureitityksen, seurantajakson, saman päivävälin mahdollisen tuotantojulkaisun, erillisen lähtötilan, ylikirjoituksen eston sekä tuloksen moduuli-, ajo-, jakso- ja syötehash-sidonnan.

## Mitä tämä toteutus ei osoita

Tekninen valmistelu ei osoita live-tutkimuksen laatua, lähteiden tämänhetkistä saatavuutta, vanhan ja uuden raportin vastaavuutta, runtime-haaran olemassaoloa, julkisen Pages-syötteen takaisinlukua eikä palautuspolun onnistumista. Nämä jäävät erillisen hyväksytyn harjoituksen ja issue #242:n näyttöarvioinnin tehtäväksi.


## Julkaisutilan fail-closed-ennakkotarkistus (#248)

Ennen live-varjoharjoitusta saman täsmällisen seurantajakson aiempi julkaisutila tarkistetaan neljästä erillisestä kanavasta: vanha raportointipolku, runtime-julkaisupäiväkirja, repositorion RSS sekä julkinen Pages-RSS. Tarkistin on `scripts/taylor_swift_publication_preflight.py`; sen tulossopimus on `schemas/taylor-swift-publication-preflight.schema.json`.

Jokaisen havainnon on sisällettävä sama aikavyöhykkeellinen alku- ja loppuaika, tarkistuksen tila, julkaisutila sekä lähdeviite. Luokitus on:

- `published`: vähintään yksi tarkistettu kanava osoittaa julkaisun; harjoitus estetään.
- `unpublished`: kaikki neljä kanavaa on tarkistettu ja jokainen osoittaa saman jakson julkaisemattomaksi; vain tämä tulos avaa varjoharjoituksen julkaisutilaportin.
- `unknown`: vähintään yksi kanava puuttuu, on saavuttamaton tai jää tuntemattomaksi; harjoitus estetään.
- `conflict`: tarkistetut kanavat ovat ristiriidassa; harjoitus estetään ja tila selvitetään.

Puuttuvaa runtime-haaraa ei luoda eikä tulkita julkaisemattomuuden todisteeksi. Tyhjä main-haaran julkaisurekisteri ei korvaa runtime-päiväkirjaa. Tarkistin ei tee verkkohakuja tai kirjoita mitään; havaintojen kerääminen ja lähteiden luotettavuus dokumentoidaan erikseen. Tämä ennakkotarkistus ei itsessään käynnistä harjoitusta eikä anna tuotantojulkaisulupaa.

Testit: `python -m unittest tests.test_taylor_swift_publication_preflight -v`.


## Ennakkotarkistuksen tulos 20.11.2026

PR #249 yhdistettiin `main`-haaraan commitilla `32934e2f48211888cf827a2dae40d3065e5d3e2e`. Kaikki kolme vaadittua CI-työnkulkua läpäisivät.

Harjoitukselle valittiin tarkasteltavaksi jakso 18.11.2026 klo 00.00 – 19.11.2026 klo 23.59.59 Suomen aikaa. Vanhan raportointipolun lähdetarkistuslokissa ei ole tälle jaksolle Taylor Swift -ajoa, ja repositorion Taylor Swift -RSS sisältää vain 16.11.2026 päivättyyn aiheeseen liittyvän aiemman raportin. Nämä kaksi havaintoa eivät kuitenkaan yksin riitä osoittamaan koko julkaisuketjun julkaisemattomuutta.

`module-runtime-state`-haara puuttuu, joten runtime-julkaisupäiväkirjaa ei voitu tarkistaa. Julkisen Pages-RSS:n takaisinlukua ei myöskään saatu vahvistettua. Ennakkotarkistuksen tulos on siksi `unknown`, eikä `execution_allowed`-portti avaudu.

**Päätös:** live-varjoharjoitusta ei käynnistetty. Tutkimusta, varjoartefaktia tai tuotantojulkaisua ei tehty. Puuttuvaa runtime-haaraa ei luoda jälkikäteen, eikä automaatioiden asetuksia muuteta. Harjoitus voidaan suorittaa vasta, kun puuttuvat julkaisutilan havainnot voidaan todentaa ja kaikki neljä kanavaa osoittavat saman jakson julkaisemattomaksi.
