# Kehitysjonon julkaistu aineisto

**Tila:** toteutuksen kuvaus; julkaisu edellyttää Pages-lähteen vaihtamista GitHub Actionsiin  
**Liittyvä tiketti:** [#83 – Siirrä Kehitysjonon tietojen haku GitHub Actionsin muodostamaan aineistoon](https://github.com/mikknikk/aiheseurain/issues/83)

## 1. Tietolähteet ja vastuut

GitHub Issues ja GitHubin natiivit issue-riippuvuudet ovat ainoat kanoniset tietolähteet. Kehitysjonon selain ei hae niitä suoraan eikä ylläpidä erillistä tietokantaa.

GitHub Actions muodostaa näistä lähteistä yhden johdetun JSON-tilannekuvan:

- `scripts/build_kanban_data.mjs` hakee kaikki avoimet ja suljetut issue-tiketit sekä kunkin tiketin `blocked_by`-suhteet.
- `schemas/kehitysjono.schema.json` määrittelee julkaistavan aineiston rakenteen.
- `scripts/validate_kanban_data.py` validoi muodostetun JSONin skeemaa ja projektikohtaisia eheysvaatimuksia vasten ennen Pages-buildiä.
- `data/kehitysjono.json` syntyy Pages-buildin työtilaan ajon aikana. Sitä ei ylläpidetä käsin eikä commitata repositorioon.
- `assets/js/kanban.js` lukee aineiston GitHub Pagesista ja muodostaa siitä Kanban- ja listanäkymän sekä riippuvuusverkon.

Aineisto sisältää vain käyttöliittymän tarvitsemat kentät: issue-numero, otsikko, URL, avoin/suljettu-tila, labelit ja päivitysaika sekä riippuvuussuhteiden edeltäjät. Siihen ei kopioida tikettien kuvauksia, kommentteja, raakaa API-virhevastetta tai käyttöoikeustietoja.

## 2. Rakenne ja täydellisyys

JSON-aineiston `schema_version` on `1`. Pakollisia ylätason kenttiä ovat:

- `generated_at`: UTC-muotoinen ISO 8601 -muodostusaika;
- `status`: vain `complete` voidaan julkaista;
- `issue_count`: mukana olevien tavallisten issueiden määrä;
- `dependency_relation_count`: kaikkien `blocked_by`-suhteiden määrä;
- `issues`: kaikki avoimet ja suljetut issue-tiketit;
- `dependencies`: yksi riippuvuustietue jokaista aineiston issuea kohti.

Pull requestit suodatetaan issue-listasta pois. Haku sivutetaan sekä issueille että riippuvuuksille. Riippuvuuksien haku rajataan neljään rinnakkaiseen työntekijään.

Muodostus keskeytyy, jos yksikin sivu, riippuvuustietue tai rakennetarkistus epäonnistuu. Osittaista aineistoa ei merkitä täydelliseksi eikä sitä julkaista. Pages-julkaisun vaiheet suoritetaan vasta onnistuneen muodostuksen jälkeen, joten epäonnistunut ajo jättää viimeisimmän onnistuneen sivustojulkaisun voimaan.

Skeema tarkistetaan tavallisessa CI-ajossa. Jokainen julkaisuajo validoi muodostetun JSONin skeemaa ja semanttisia ehtoja vasten sekä varmistaa, että tiedosto päätyy Jekyll-buildin julkaistavaan hakemistoon. Aineiston tuottajan testit tarkistavat sivutuksen, riippuvuudet, muodostusajan, täydellisyystilan ja virheestä keskeyttämisen.

## 3. Päivitysten käynnistyminen

`.github/workflows/publish-pages.yml` käynnistyy seuraavista tapahtumista:

- `push` `main`-haaraan: tavalliset sivuston sisältömuutokset;
- issue avataan, sitä muokataan, suljetaan, avataan uudelleen, sille lisätään tai poistetaan label tai se poistetaan;
- issue-kommentti luodaan tai sitä muokataan; tämä kattaa myös riippuvuuksien välitystyönkulun (#79) onnistumisviestin;
- varmistava ajastus 15 minuutin välein;
- manuaalinen `workflow_dispatch`.

GitHubin issue-webhookien ei oleteta kattavan kaikkia natiivien riippuvuuksien muutoksia. #79:n välitystyönkulun kommentti käynnistää päivityksen heti sen jälkeen, kun välitys on valmis. Suoraan GitHubissa tehdyt riippuvuusmuutokset varmistetaan viimeistään seuraavalla 15 minuutin ajolla.

Kaikki Pages-ajot käyttävät samaa `github-pages`-concurrency-ryhmää, eikä käynnissä olevaa ajoa peruta uuden vuoksi. Näin julkaisut eivät aja päällekkäin. Jokainen ajo hakee lähdetiedot uudelleen vasta oman vuoronsa alussa; vanhemman ajon tulos ei voi valmistua uudemman ajon jälkeen ja korvata sitä.

## 4. Selain ja välimuisti

Selain hakee yhden saman alkuperän JSON-tiedoston. Tavallinen sivun lataus ei tee GitHubin Issues- tai riippuvuusrajapintaan pyyntöjä. Käyttöliittymän haku, prioriteetti- ja aihealue-suodattimet, Kanban-/listanäkymä sekä riippuvuuksien tarkastelu säilyvät.

Julkaistun aineiston muodostusaika näytetään käyttäjälle. Yli tunnin ikäinen aineisto merkitään vanhentuneeksi. Selaimen paikallinen välimuisti säilyy varajärjestelynä, mutta se merkitään aina paikalliseksi ja sen tallennusaika näytetään. Verkkovirhe ei muuta vanhaa aineistoa tuoreeksi.

Jos julkaistua aineistoa ei voida hakea eikä käyttökelpoista paikallista välimuistia ole, näkymä kertoo selvästi, ettei tikettejä voida näyttää. Osittaista riippuvuustietoa ei päätellä tyhjiksi suhteiksi.

## 5. Pages-julkaisun käyttöönotto

GitHub Pagesin nykyinen `Deploy from a branch` -julkaisutapa ei voi sisällyttää Actions-ajon aikana muodostettua, repositorioon committoimatonta JSON-tiedostoa sivustoon. Siksi nykyinen GitHubin hallitsema Jekyll-julkaisu korvataan yhdellä repositorion omalla Pages-workflow'lla. Kyse ei ole rinnakkaisesta sivustosta tai erillisestä julkaisuhaarasta: sama Jekyll-sivusto, osoite ja polut säilyvät.

Kun PR:n muutokset on yhdistetty, repositorion ylläpitäjän on vaihdettava GitHubissa:

1. Avaa `Settings` → `Pages`.
2. Avaa `Build and deployment` -osion `Source`-valinta.
3. Valitse `GitHub Actions`.

Tämä asetusmuutos on tehtävä erikseen GitHubin asetuksissa. Ennen vaihtoa vanha branch-pohjainen julkaisu säilyttää sivuston, mutta uusi `deploy-pages`-vaihe ei voi julkaista. Asetuksen vaihdon jälkeen `publish-pages.yml` rakentaa Jekyll-sivuston, sisällyttää juuri muodostetun JSON-aineiston ja julkaisee saman Pages-sivuston.

Pull request -ajossa workflow muodostaa aineiston ja rakentaa sivuston testiksi, mutta ei julkaise Pagesiin. Julkaisu tapahtuu `main`-haaran, issue-tapahtumien, ajastuksen tai manuaalisen käynnistyksen yhteydessä.

## 6. Käyttöoikeudet ja rajaukset

Workflow käyttää vain `contents: read`, `issues: read`, `pages: write` ja `id-token: write` -oikeuksia. Selaimeen ei toimiteta GitHub-tokenia eikä selaimessa ole kirjoitusrajapintoja. Aineiston muodostuksen virheviestit eivät sisällä raakaa API-vastausta.

Tämä toteutus ei muuta ChatGPT-automaatiotehtävien ajastuksia, suoritusvälejä, aikavyöhykkeitä, ohjeita tai kohdekeskusteluja. Se ei myöskään muuta issueiden tiloja tai riippuvuuksia.
