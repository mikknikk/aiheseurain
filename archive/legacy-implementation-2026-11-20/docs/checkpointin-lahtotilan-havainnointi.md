# Checkpointin lähtötilan havainnointi

**Tila:** varjosiirtymän valmistelun tekninen apuväline  
**Liittyvät tiketit:** [#239 – Kytke siirtymätodisteiden keruu testattuun varjosiirtymän elinkaareen](https://github.com/mikknikk/aiheseurain/issues/239)

## Tarkoitus

Ennen moduulisiirtymän arviointia on luettava moduulin checkpointin lähtötila runtime-haarasta. Lähtötilaa ei saa päätellä päähaaran vanhasta moduulitiedostosta eikä syöttää käsin oletusarvona.

`scripts/checkpoint_baseline.py` tarjoaa tähän read-only-toiminnon `read_checkpoint_baseline`. Se lukee vain polun `data/module-state/{module_id}.json` annetusta runtime-haarasta ja palauttaa:

- moduulitunnisteen ja luetun haaran;
- tiedostopolun ja täsmällisen Git-blob-SHA:n;
- viimeisimmän onnistuneen ajon `run_id`-tunnisteen;
- checkpointin `checked_at`-ajan;
- havainnon ajankohdan.

Jos moduulilla ei ole aiempaa onnistunutta ajoa, `run_id` ja `checked_at` ovat eksplisiittisesti `null`. Puuttuva tiedosto, väärä moduuliomistajuus, virheellinen JSON, virheellinen SHA tai virheellinen aikaleima pysäyttää toiminnon. Tuntematonta tilaa ei tulkita tyhjäksi checkpointiksi.

## Käyttö osana siirtymätodistetta

Varjosiirtymän orkestroija kutsuu `read_checkpoint_baseline`-toimintoa itse aina, kun harjoitukseen sisältyy checkpointin jälkitilan tarkistus. Se ei hyväksy lähtötilaa keräyscallbackilta. Orkestroija vertaa suoraan runtime-haarasta luetun lähtöhavainnon `blob_sha`-, `run_id`- ja `checked_at`-arvoja checkpoint-jälkitodisteen vastaaviin `before_*`-kenttiin. Jälkitodisteen keräämisen jälkeen orkestroija lukee runtime-haaran uudelleen ja vertaa myös `after_*`-kentät suoraan luettuun jälkitilaan. Mikä tahansa ero pysäyttää harjoituksen ennen ensimmäistä auditointikirjoitusta; callback ei voi väärentää kumpaakaan päätetilaa.

Tämä apuväline ei itsessään tee siirtymää, päivitä checkpointia, julkaise RSS:ää, muuta moduulin aktivointia tai tehtäväjonoa eikä koske ChatGPT-automaation asetuksiin. Se ei myöskään yksin todista, että myöhempi checkpoint kuuluu oikeaan julkaisuun; manifestin, RSS:n ja ajon tunnisteiden vastaavuus tarkistetaan erikseen.

## Testit

```bash
python -m unittest tests.test_checkpoint_baseline -v
```

Testit varmistavat onnistuneen lukemisen, ensimmäisen ajon null-lähtötilan, puuttuvan checkpointin fail-closed-käyttäytymisen, moduuliomistajuuden, virheelliset aikaleimat ja SHA:n sekä sen, ettei lukija tee kirjoituksia.
