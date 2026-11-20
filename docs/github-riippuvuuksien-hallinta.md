# GitHub-issueiden riippuvuuksien hallinta

## Kanoninen tietolähde

GitHub Issues -palvelun natiivit riippuvuussuhteet ovat Aiheseuraimen ainoa pysyvä riippuvuustietolähde. Kehitysjono näyttää saman tiedon kahdesta suunnasta:

- **Edeltävä työ / blocked_by:** tiketti, jonka valmistumista tarkasteltava työ odottaa.
- **Estää / blocking:** tiketit, joiden etenemistä tarkasteltava työ estää.

Jos tiketti A odottaa tikettiä B, A:n `blocked_by`-listassa on B. Käänteinen `blocking`-näkymä johdetaan samasta tiedosta; rinnakkaista riippuvuusrekisteriä ei ylläpidetä.

## Nimenomainen muutospyyntö

Riippuvuuden lisääminen tai poistaminen edellyttää erillistä pyyntölohkoa kohde-issuen kuvauksessa. Tavallinen tikettiviittaus ei muuta riippuvuuksia.

Lisäyspyyntö:

```html
<!-- aiheseurain-dependency-request
{"blocked_by":[66,67]}
-->
```

Poistopyyntö:

```html
<!-- aiheseurain-dependency-request
{"remove_blocked_by":[66]}
-->
```

Samaan pyyntöön voi sisällyttää molemmat kentät, kun sama numero ei esiinny molemmissa. Yhdessä pyynnössä voi olla enintään kymmenen lisäystä ja kymmenen poistoa.

## Välitystyönkulku

`.github/workflows/sync-issue-dependencies.yml) käynnistyy issue-kuvauksen muokkauksesta. Käsittelijä:

1. Ohittaa pull requestit ja työnkulun oman botin tekemät muokkaukset.
2. Etsii täsmälleen yhden pyyntölohkon ja validoi JSONin.
3. Tarkistaa, että kohde ja viitatut numerot ovat olemassa olevia saman repositorion tavallisia issueita.
4. Estää itseensä viittaamisen ja riippuvuussyklit.
5. Lisää tai poistaa vain nimenomaisesti pyydetyt natiivisuhteet.
6. Käsittelee jo olemassa olevan lisäyksen ja jo puuttuvan poiston idempotentisti.
7. Käynnistää onnistuneen muutoksen jälkeen Kehitysjonon välimuistin kohdistetun päivityksen.
8. Poistaa pyyntölohkon vain, jos kuvaus sisältää edelleen täsmälleen saman lohkon. Lisää tämän jälkeen kommentin käsittelyn tuloksesta.

Jos pyyntö epäonnistuu, pyyntölohko säilytetään uudelleenyritystä varten ja tikettiin lisätään virhekommentti. Osittain toteutunut pyyntö voidaan yrittää uudelleen, koska jokainen muutos tarkistetaan ennen kirjoitusta.

## Suoraan GitHubissa tehdyt muutokset

GitHubin käyttöliittymässä tehdyt natiivien riippuvuuksien muutokset eivät välttämättä tuota issue-tapahtumaa. Ne tulevat Kehitysjono-näkymään viimeistään päivittäisessä täydessä täsmäytyksessä. Tarvittaessa täysi täsmäytys voidaan käynnistää käsin Actionsista.

## Rajaukset

Riippuvuuksien välitys ei muuta issue-tiketin tilaa, prioriteettia, komponenttilabeleita, assigneita, otsikkoa tai muuta kuvausta pyyntölohkoa lukuun ottamatta. Se ei muuta ajastettuja ChatGPT-tehtäviä eikä RSS-julkaisua.

Työnkulku tarvitsee seuraavat rajatut oikeudet:

- `contents: read` – käsittelijäskriptin noutaminen.
- `issues: write` – natiivien riippuvuuksien muuttaminen, pyyntölohkon kuluttaminen ja tuloskommentti.
- `actions: write` – kohdistetun välimuistipäivityksen käynnistäminen.

## Testaus ja käyttöönoton varmennus

`tests/issue-dependencies.test.mjs) tarkistaa pyyntölohkon validoinnin, tavallisten tekstiviittausten ohittamisen, syklien tunnistamisen, idempotenssin, puuttuvien tikettien hylkäämisen ja välimuistipäivityksen käynnistyksen.

Automaattiset testit eivät yksin todista, että GitHubin natiivien riippuvuuksien kirjoitusrajapinta toimii juuri tämän repositorion Actions-tokenilla. Ensimmäinen oikea riippuvuusmuutos on varmennettava lukemalla suhde takaisin GitHubin natiivista rajapinnasta ja tarkistamalla työnkulun tuloskommentti.
