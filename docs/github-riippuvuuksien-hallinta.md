# GitHub-tikettien riippuvuuksien hallinta

## Kanoninen tietolähde

GitHub Issues -palvelun natiivit riippuvuussuhteet ovat Aiheseuraimen ainoa pysyvä riippuvuustietolähde. Kehitysjono lukee saman GitHub-rajapinnan tietoja. Repositorioon ei tallenneta rinnakkaista riippuvuusrekisteriä.

Jos tiketti A on estetty tiketistä B, A:n `blocked_by`-listassa on B. Riippuvuuden suunta on siis aina: **kohdetiketti odottaa edeltävää tikettiä**. Pelkkä maininta toisesta tiketistä, aiheeseen liittyminen tai jatkokehityksen mahdollistaminen ei ole automaattisesti estävä riippuvuus.

## Riippuvuuden lisääminen tai poistaminen ChatGPT:n kautta

ChatGPT voi pyytää muutosta muokkaamalla kohde-issuen kuvausta GitHub-yhteyden nykyisillä issue-muokkausoikeuksilla. Kuvaus sisältää tällöin erillisen HTML-kommentin:

```html
<!-- aiheseurain-dependency-request
{"blocked_by":[66, 67]}
-->
```

Tämä lisää kohdetiketin `blocked_by`-listaan tiketit #66 ja #67. Pyyntölohko ei ole käyttäjälle näkyvää tavallista sisältöä. Tavallinen `#66`-viittaus tai muu tekstimaininta ei käynnistä muutosta.

Riippuvuuden poistaminen vaatii erillisen, nimenomaisen pyynnön:

```html
<!-- aiheseurain-dependency-request
{"remove_blocked_by":[66]}
-->
```

Saman pyynnön voi sisältää molemmat kentät, jos lisättävät ja poistettavat numerot ovat eri tikettejä. Sama numero ei saa esiintyä molemmissa. Yhdessä pyynnössä voi olla enintään kymmenen lisäystä ja kymmenen poistoa.

## Välityksen toiminta

GitHub Actions käynnistyy, kun issue-kuvausta muokataan. Työnkulku:

1. Käsittelee vain tavallisen issue-tiketin; pull requestit ja työnkulun oman botin tekemät muokkaukset ohitetaan.
2. Etsii kuvauksesta täsmälleen yhden pyyntölohkon ja tarkistaa sen JSON-rakenteen.
3. Varmistaa, että kohde ja jokainen viitattu numero ovat olemassa olevia saman repositorion issue-tikettejä. Pull requestia ei hyväksytä riippuvuuden päätepisteeksi.
4. Tarkistaa lisäysten suunnan ja koko olemassa olevan edeltäjäketjun mahdolliset syklit.
5. Lisää tai poistaa vain erikseen pyydetyt natiivisuhteet. Jo olemassa oleva lisäys ja jo puuttuva poisto käsitellään idempotentisti.
6. Hakee tiketin kuvauksen uudelleen ja poistaa käsitellyn pyyntölohkon vain, jos se on edelleen sama kuin käsittelyn alussa. Näin väliin tullutta käyttäjän muokkausta ei ylikirjoiteta.
7. Lisää tikettiin kommentin, jossa kerrotaan lisätyt, jo olemassa olleet, poistetut ja jo puuttuneet suhteet.

Jos pyyntö on virheellinen, tiketti puuttuu, syntyisi sykli tai GitHubin rajapinta hylkää kirjoituksen, työnkulku jättää pyyntölohkon tikettiin uudelleenyritystä varten ja lisää virheestä kommentin. Osittaista onnistumista ei esitetä kokonaan onnistuneena: jo tehdyt muutokset ovat idempotentteja, joten sama pyyntö voidaan yrittää uudelleen turvallisesti.

## Käyttöoikeudet ja rajaukset

Työnkulun `GITHUB_TOKEN` käyttää vain seuraavia repositoriotason oikeuksia:

- `contents: read` – käsittelijäskriptin noutaminen repositoriosta.
- `issues: write` – natiivien riippuvuuksien lisääminen/poistaminen, pyyntölohkon kuluttaminen ja tuloskommentti.

GitHub Actions ei tarjoa riippuvuusrajapinnalle tätä kapeampaa erillistä oikeutta; `issues: write` on siksi teknisesti tarvittava oikeustaso. Työnkulku ei käytä henkilökohtaista käyttöoikeustunnusta, organisaation salaisuuksia tai laajempia oikeuksia.

Välitys ei muuta tiketin tilaa, prioriteettia, aihealuetta, assigneita, otsikkoa tai muita kuvauksen osia. Se ei sulje tikettejä, yhdistä pull requesteja eikä muuta automaatioiden ajastuksia tai ohjeita.

## Testaus ja rajoitukset

Node-testit tarkistavat pyyntölohkon validoinnin, tavallisten tekstiviittausten ohittamisen, syklien tunnistamisen, olemassa olevien suhteiden idempotenssin, nimenomaiset poistot sekä virheellisten päätepisteiden hylkäämisen.

CI-testit eivät itsessään todista, että GitHubin kirjoitusrajapinta on käytettävissä juuri kyseisen repositorion Actions-tokenilla. Käyttöönoton jälkeen ensimmäinen oikea pyyntö on varmennettava lukemalla suhde takaisin GitHubin natiivista `dependencies/blocked_by`-rajapinnasta ja tarkistamalla työnkulun tuloskommentti.
