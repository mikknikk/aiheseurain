# Aiheseuraimen järjestelmäarkkitehtuuri

**Tarkoitus:** kuvata ensin Aiheseuraimen toimintamalli ilman sidosta yksittäiseen palveluun ja sen jälkeen nykyinen ChatGPT- ja GitHub-toteutus.  
**Nykytilan tarkistus:** 17.11.2026  
**Liittyvä kehitystehtävä:** [#75 – Dokumentoi Aiheseuraimen järjestelmäarkkitehtuuri ja teknologioiden vaihdettavuus](https://github.com/mikknikk/aiheseurain/issues/75)

## 1. Järjestelmän tarkoitus ja rajat

Aiheseurain on aiheohjattu tiedonkeruu-, arviointi-, raportointi- ja julkaisujärjestelmä. Se seuraa useita toisistaan erotettuja aiheita, etsii niihin liittyviä uusia tapahtumia, arvioi lähteitä ja väitteitä, muodostaa suomenkielisiä raportteja sekä säilyttää seurannan tilaa ja julkaistua historiaa.

Järjestelmän suunnitteluperiaate on erottaa toisistaan:

1. **Mitä seurataan:** aiheet, rajaukset, hakukriteerit, lähteet ja aihekohtaiset erityissäännöt.
2. **Miten seuranta tehdään:** yhteinen haku-, arviointi-, varmennus-, raportointi- ja jatkotoimintamalli.
3. **Millä tekniikalla se tehdään:** ajastin, tekoälypalvelu, suoritusympäristö, integraatiot, tallennus, testaus ja julkaisu.

Erottelu mahdollistaa aiheiden kehittämisen ilman, että jokainen muutos vaatii teknisen järjestelmän uudelleenohjelmointia. Se myös rajaa aihekohtaisen poikkeuslogiikan vaikutukset kyseiseen aiheeseen.

## 2. Järjestelmäriippumaton toimintamalli

Seuraava prosessi kuvaa toiminnalliset vaiheet riippumatta siitä, mikä ajastin, tekoälypalvelu tai ohjelmisto ne suorittaa.

```mermaid
flowchart TD
    A["Ajastin tai käyttäjän käynnistys"] --> B["Valitse suoritettava seurantatehtävä"]
    B --> C["Lue aiheen määritys ja yhteiset toimintaperiaatteet"]
    C --> D["Hae lähteitä ja uusia tietoja"]
    D --> E["Avaa alkuperäiset lähteet ja arvioi väitteet"]
    E --> F["Poista duplikaatit ja arvioi uutisarvo"]
    F --> G["Muodosta raportti ja lähdeviitteet"]
    G --> H["Tarkista sisältö, rakenne ja julkaisuehdot"]
    H --> I{"Hyväksytty julkaistavaksi?"}
    I -->|Ei| J["Korjaa tai hylkää raportti"]
    J --> G
    I -->|Kyllä| K["Tallenna raportti ja seurantatila"]
    K --> L["Julkaise sovittuun jakelukanavaan"]
    L --> M["Lue julkaisu takaisin ja varmista tulos"]
    M --> N["Kirjaa ajon tulos ja seuraava tarkistuspiste"]
```

### 2.1 Vaiheiden vastuut

- **Käynnistys ja tehtävän valinta:** ajastin tai käyttäjä käynnistää oikean tehtävän. Tehtävän valinta perustuu määriteltyyn jonoon tai erillisen prosessin omaan aikatauluun.
- **Määritysten lukeminen:** suorittaja lukee tehtävän rajauksen, aiheen lähteet, yhteiset toimintaperiaatteet ja edellisen onnistuneen tarkistuspisteen.
- **Tiedonhaku:** lähteitä haetaan useilla aiheeseen sopivilla kielillä ja alueilla. Rekisteröity lähdelista on hakujen lähtökohta, ei suljettu luettelo.
- **Arviointi ja varmennus:** alkuperäiset julkaisut avataan, väitteet erotetaan lähteiden tulkinnoista ja epävarmuudet kirjataan. Lähteen yleinen luotettavuus ja yksittäisen väitteen varmennus ovat eri asioita.
- **Raportointi:** vain olennaiset uudet tai muuttuneet tapahtumat raportoidaan. Raporttiin liitetään lähteet ja tarkasteltu ajanjakso.
- **Laadunvarmistus:** tarkistetaan toimitukselliset ehdot sekä koneellisesti tarkistettavat rakenteet. Automaattinen skeema- tai XML-testi ei todista väitteen totuutta.
- **Tallennus ja julkaisu:** raportti, ajokohtainen tila ja julkaisu tallennetaan sovittuihin tietolähteisiin. Julkaisun jälkeen sisältö luetaan takaisin.
- **Jäljitettävyys:** onnistunut tarkistus kirjataan vasta, kun vaaditut haut, kirjoitukset ja takaisinlukutarkistukset on tehty.

Prosessi ei edellytä RSS:ää jakelumuotona. RSS on nykyinen julkaisutapa; toinen järjestelmä voisi tuottaa saman sisällön esimerkiksi verkkosivulle tai rajapintaan, kunhan lähteet, ajanjakso ja raporttihistoria säilyvät.

## 3. Kolme arkkitehtuurikerrosta

```mermaid
flowchart TB
    subgraph TOPIC["1. Aihekerros – mitä seurataan"]
      T1["Aiheiden rajaukset ja hakukriteerit"]
      T2["Aihekohtaiset lähteet ja poikkeukset"]
      T3["Tehtäväjono ja seurantajaksot"]
    end
    subgraph COMMON["2. Yhteinen seurantakerros – miten seurataan"]
      C1["Haku ja löydösten käsittely"]
      C2["Lähteiden ja väitteiden arviointi"]
      C3["Deduplikointi ja uutisarvo"]
      C4["Raportointi ja julkaisulaadun tarkistus"]
      C5["Seurantatilan ja historian hallinta"]
    end
    subgraph TECH["3. Tekninen toteutuskerros – millä suoritetaan"]
      X1["Ajastin ja käynnistimet"]
      X2["Tekoäly ja suoritusympäristö"]
      X3["Integraatiot ja tunnukset"]
      X4["Tallennus ja versionhallinta"]
      X5["Testaus ja julkaisu"]
    end
    TOPIC --> COMMON
    TECH --> COMMON
    COMMON --> TECH
```

### 3.1 Aihekerros

Aihekerros määrittelee seurannan kohteen, ei sitä, millä ohjelmistolla seuranta tehdään. Aihekohtaisia määrityksiä ovat esimerkiksi:

- aiheen sisältörajaukset, nimivariantit ja hakusanat;
- kieli- ja aluepainotukset;
- aihekohtaiset lähdevalinnat ja lähteiden käyttörajoitteet;
- uutisarvon ja mukaan ottamisen erityissäännöt;
- erillistä prosessia edellyttävät tehtävät.

Nykyisessä repositoriossa aihekohtaiset ohjeet ovat `docs/`-hakemiston dokumenteissa. Yhteiset lähdetiedot ovat `data/source-catalog.json`-tiedostossa ja tehtäväkohtaiset lähdekäyttövalinnat `data/sources/{task_id}.json`-tiedostoissa. Yhdeksän aihekierroksen järjestys on `docs/tehtavajono.md`-tiedostossa ja sen koneellisesti ylläpidetty rinnakkaistieto on `data/seurantatila.json`-tiedostossa.

Tavoitetilassa aiheiden rajaukset, hakusanat, kieli- ja aluevalinnat sekä lähdeviittaukset voidaan pitää rakenteisina määrityksinä. Kaikkea ei kuitenkaan pidä pakottaa yhteen skeemaan: esimerkiksi intialaisten elokuvien näytösvahti on erillinen prosessi, koska sillä on oma päivittäinen näytöslogiikka, tapahtumahistoria ja jakelusyöte.

### 3.2 Yhteinen seurantakerros

Yhteinen seurantakerros vastaa siitä, että eri aiheet käsitellään yhdenmukaisilla laadun ja jäljitettävyyden periaatteilla. Se ei saa sisältää yksittäiseen aiheeseen sidottuja oletuksia.

Yhteisiä sääntöjä ovat muun muassa:

- seurantajakson määrittely edellisen kyseisen aiheen onnistumisen perusteella;
- alkuperäisten lähteiden avaaminen ja lähteiden riippumattomuuden arviointi;
- lähteen luotettavuusluokan erottaminen väitekohtaisesta varmennuksesta;
- duplikaattien poistaminen ja uutisarvon arviointi;
- suomenkielisen raportin ja kuvaavien lähdeviitteiden muodostaminen;
- julkaisua edeltävä tarkistus ja julkaistun sisällön takaisinluku;
- onnistuneen tarkistuspisteen sekä virheiden ja epävarmuuksien kirjaaminen.

Nykyiset ensisijaiset ohjeet ovat `docs/seuranta.md`, `docs/luotettavuusluokitus.md`, `docs/julkaisuportti.md` ja saavutettavuuden osalta `docs/saavutettavuus.md`. Näitä ei pidä kopioida aihekohtaisiin ohjeisiin kokonaisuudessaan, vaan aiheohjeiden tulee viitata yhteisiin sääntöihin.

### 3.3 Tekninen toteutuskerros

Tekninen kerros käynnistää ja suorittaa prosessin, välittää haut ja kirjoitukset, säilyttää tiedot, validoi rakenteet ja julkaisee tulokset. Se ei määrittele, mitä uutisia yksittäisestä aiheesta etsitään.

Nykyisessä toteutuksessa tekninen kerros jakautuu useaan palveluun ja komponenttiin:

- ChatGPT:n ajastetut tehtävät käynnistävät varsinaiset seurantavuorot.
- ChatGPT:n tekoäly ja käytettävissä olevat työkalut suorittavat tiedonhaun, lähteiden arvioinnin ja raportoinnin.
- GitHub-integraatio välittää repositorion luku- ja kirjoitustoiminnot.
- GitHub-repositorio säilyttää ohjeet, lähderekisterit, seurantatilan, raportit ja RSS-syötteet.
- GitHub Actions suorittaa repositorion testit, erilliset tekniset työnkulut ja Pages-julkaisun.
- GitHub Pages julkaisee staattisen verkkosivuston, RSS-syötteet ja julkiset JSON-tietolähteet.

## 4. Nykyinen tekninen toteutus

### 4.1 Varsinaiset seurantatehtävät

Nykyisessä toteutuksessa on kolme erillistä ChatGPT:n ajastettua tehtävää:

1. **Pääautomaatio:** käsittelee päivittäisellä ajollaan yhden yhdeksästä aihekierron tehtävästä.
2. **Intialaisten elokuvien näytösvahti:** erillinen päivittäinen prosessi, joka etsii Suomessa järjestettäviä näytöksiä ja ylläpitää näytöshistoriaa sekä omaa RSS-syötettä.
3. **Viikoittainen järjestelmän laatutarkistus:** auditointiprosessi, joka tarkistaa dokumentaation, tietomallit, RSS-syötteet, testit ja automaatioiden hallinnan. Se ei ole uutishaku eikä korjaava ylläpitoprosessi.

Jokaisella on oma GitHubissa ylläpidetty käsikirjansa ja kanoninen käynnistyskehotteensa:

| Tehtävä | Ensisijainen käsikirja | Käynnistyskehote |
|---|---|---|
| Pääautomaatio | `docs/paaautomaation-ohje.md` | `prompts/paauutisseuranta.txt` |
| Näytösvahti | `docs/intialaisten-elokuvien-naytosseuranta.md` | `prompts/naytosvahti.txt` |
| Laatutarkistus | `docs/laatutarkistuksen-ohje.md` | `prompts/laatutarkistus.txt` |

Käynnistyskehote on lyhyt aloitusohje, ei automaation täydellinen toimintamäärittely. Ohjeiden versionumerot ja käynnistyskehotteiden tunnisteet tarkistetaan `data/seurantatila.json`-tiedoston avulla. GitHubiin tallennettu käynnistyskehote ei kuitenkaan päivity automaation asetuksiin itsestään; tekstin kopiointi ja asetusten täsmäytys ovat erillisiä toimenpiteitä.

### 4.2 Ajastus ja käynnistysvastuut

Varsinaiset kolme seurantatehtävää käynnistää ChatGPT:n ajoitettujen tehtävien palvelu. Niiden tehtäväasetukset – aktiivisuus, tarkka aikataulu, aikavyöhyke, käynnistysohje ja kohdekeskustelu – sijaitsevat ChatGPT:n automaatioasetuksissa, eivät GitHub-repositorion tiedostoissa.

GitHubissa olevat käsikirjat kuvaavat odotettua rytmiä seuraavasti: pääautomaatio päivittäin noin klo 12.00 Europe/Helsinki, näytösvahti päivittäin noin klo 05.00 Europe/Helsinki ja laatutarkistus kerran viikossa. Nämä ovat käsikirjoihin kirjattuja odotuksia. **Tässä dokumentointikatselmuksessa ei luettu ChatGPT:n tallennettuja tehtäväasetuksia, joten tarkkoja asetettuja kellonaikoja, aikavyöhykkeitä, aktiivisuutta tai kohdekeskusteluja ei väitetä erikseen varmennetuiksi.**

GitHub-tiedostoista ei voi päätellä ChatGPT:n ajastuksen todellista asetusta. Jos ajastus halutaan myöhemmin tarkistaa tai muuttaa, se tehdään erikseen ChatGPT:n tehtäväasetuksissa ja vain käyttäjän nimenomaisella valtuutuksella. GitHubiin tehty dokumentaatiomuutos ei muuta tehtävän asetuksia.

### 4.3 GitHub-integraatio

ChatGPT:n GitHub-integraatio tarjoaa suorittajalle repositorion luku- ja kirjoitustoiminnot. Nykyisessä työnkulussa sitä käytetään muun muassa tiedostojen lukemiseen, dokumenttien ja seurantatietojen päivittämiseen, issueiden käsittelyyn sekä muutosten viemiseen haaroihin ja pull requesteihin.

Integraation tarkka käyttöoikeusjoukko ja käyttäjän valitsemat käytettävissä olevat repositoriot ovat GitHub-sovelluksen ja ChatGPT-yhteyden asetuksia. Ne eivät ole tämän repositorion tiedostoista kokonaan todennettavissa. Siksi tässä ei väitetä, että integraatiolla olisi kaikki GitHub-sovelluksen teknisesti mahdolliset oikeudet. Käyttöoikeudet tulee rajata vain tarvittaviin repositorioihin ja toimintoihin.

GitHub-integraatio ja GitHub Actionsin `GITHUB_TOKEN` ovat eri tunnistusmekanismeja. Integraation kautta tehtävä käyttäjän puolesta tehtävä repositoriotyö ei ole sama asia kuin Actions-työnkulun oma rajattu token.

### 4.4 GitHub-repositorio ja tallennus

Repositorio `mikknikk/aiheseurain` on nykyisen toteutuksen versionhallittu tietovarasto ja julkaisun lähde. Sen keskeiset vastuut ovat:

| Sijainti | Sisältö ja vastuu |
|---|---|
| `docs/` | Ihmiselle ja automaatioille tarkoitetut ensisijaiset ohjeet, seurannan historia ja tietomallien kuvaukset |
| `prompts/` | ChatGPT:n tehtäväasetuksiin kopioitavat kanoniset käynnistyskehotteet |
| `data/source-catalog.json` | Lähteiden yhteiset perustiedot |
| `data/sources/*.json` | Aihe- tai tehtäväkohtaiset lähdekäyttörekisterit |
| `data/seurantatila.json` | Aihekierron, viimeisimpien onnistumisten ja ohjeversioiden koneellisesti luettava tila |
| `data/lahdetarkistukset.json` | Ajokohtaiset lähteiden tarkistustulokset ja kattavuushuomiot |
| `data/naytosten-muutoshistoria.json` | Näytösseurannan nykytila ja tapahtumahistoria |
| `run-history/*/history.json` | Kolmen ChatGPT-automaation erillisiin haaroihin tallentama vaihekohtainen ajohistoria |
| `feeds/*.xml` | Aihekohtaiset uutis-RSS-syötteet ja erillinen näytös-RSS |
| `schemas/` | JSON-tietomallien ja julkaisuraporttien rakennesopimukset |
| `scripts/` ja `.github/` | Validointi, aineiston muodostus ja GitHub Actions -työnkulut |

GitHub Issues on kehitystehtävien kanoninen tietolähde. Kehitysjono ei ylläpidä tiketeistä erillistä käsin päivitettävää tietokantaa, vaan GitHub Actions muodostaa GitHub Issues -tiedoista ja natiiveista riippuvuuksista täydellisen JSON-tilannekuvan.

### 4.5 GitHub Actions: testaus, aineiston muodostus ja julkaisu

GitHub Actions ei suorita varsinaisia uutis- tai näytöshakuja. Se hoitaa repositorion teknisiä tehtäviä:

| Työnkulku | Käynnistin | Vastuu |
|---|---|---|
| `RSS- ja dokumentaatiotestit` (`validate-feeds.yml`) | Push `main`-haaraan, pull request `main`-haaraan tai manuaalinen käynnistys | RSS/XML- ja HTML-rakenteet, dokumentaatio, seurantatila, JavaScript ja yksikkötestit |
| `Kehitysjonon aineisto ja Pages-julkaisu` (`publish-pages.yml`) | Push, pull request, issue-tapahtumat, issue-kommentit, päivittäinen ajastus tai manuaalinen käynnistys | GitHub Issues -aineiston muodostus ja validointi sekä Jekyll/Pages-julkaisu |
| `Synkronoi tikettien riippuvuudet` (`sync-issue-dependencies.yml`) | Issue muokattu | Käsittelee yksiselitteisen natiivin riippuvuuspyynnön ja käynnistää tarvittaessa Pages-aineiston päivityksen |
| `Lähde- ja RSS-linkkien viikoittainen tarkistus` (`check-links.yml`) | Viikoittainen ajastus tai manuaalinen käynnistys | Tarkistaa lähde- ja RSS-linkkien saavutettavuuden ja tallentaa raportin artefaktiksi |

`publish-pages.yml` sisältää päivittäisen varmistusajastuksen `17 3 * * *` UTC, eli Suomen talviaikana klo 05.17 ja kesäaikana klo 06.17. Tämä on GitHub Actionsin Pages-aineiston päivitys- ja julkaisuaika, ei pääautomaation uutishaku. GitHub Actionsin ajastus voi viivästyä ruuhkatilanteessa.

`check-links.yml` sisältää viikoittaisen maanantain ajastuksen `17 6 * * 1` UTC. Sekään ei käynnistä uutisseurantaa. `validate-feeds.yml` käynnistyy koodimuutoksista tai manuaalisesti, eikä sillä ole omaa ajastusta.

### 4.6 Käyttöoikeudet ja salaisuudet

Työnkulut määrittelevät oikeutensa erikseen vähimmän tarpeen periaatteella:

- Pages-julkaisu: `contents: read`, `issues: read`, `pages: write` ja `id-token: write`.
- RSS-/dokumentaatiotestit ja linkkitarkistus: `contents: read`.
- Natiivien issue-riippuvuuksien synkronointi: `contents: read`, `issues: write` ja `actions: write`, koska työnkulku muuttaa riippuvuuksia ja käynnistää Pages-työnkulun.

Actions käyttää työnkululle rajattua `GITHUB_TOKEN`-tunnusta. Tokenia ei kirjoiteta lähdekoodiin eikä julkaista selaimelle. GitHub Actionsin työnkulkuoikeudet eivät määrittele ChatGPT:n GitHub-integraation oikeuksia.

### 4.7 GitHub Pages ja verkkosivusto

GitHub Pages julkaisee staattisen Jekyll-sivuston osoitteessa https://mikknikk.github.io/aiheseurain/. Sivuston osia ovat etusivu, Valvomo, RSS-lukija ja Kehitysjono. Selaimen käyttöliittymät lukevat julkisia RSS- ja JSON-tiedostoja; niillä ei ole GitHub-kirjoitusoikeuksia.

Pages-julkaisu muodostaa Kehitysjonon JSON-aineiston Actions-ajossa ennen Jekyll-rakennusta. Aineisto validoidaan, ja vasta onnistunut build voidaan julkaista. Epäonnistunut build ei julkaise osittaista Kehitysjono-aineistoa.

## 5. Tietovirrat nykyisessä toteutuksessa

```mermaid
flowchart TD
    subgraph CHATGPT["ChatGPT – varsinaiset seurantatehtävät"]
      S1["Päivittäinen pääautomaatio"]
      S2["Päivittäinen näytösvahti"]
      S3["Viikoittainen laatutarkistus"]
      AI["Tekoäly, haut ja raportointi"]
      S1 --> AI
      S2 --> AI
      S3 --> AI
    end
    subgraph GH["GitHub – versionhallinta ja tekniset työnkulut"]
      INT["GitHub-integraatio"]
      REPO["Repositorio: ohjeet, data, lähteet, RSS"]
      ACT["GitHub Actions: testit, aineisto ja julkaisu"]
      SITES["GitHub Pages: staattinen sivusto"]
      INT --> REPO
      REPO --> ACT
      ACT --> SITES
    end
    AI <--> INT
    SITES --> USERS["Lukijat ja ylläpitäjä"]
    REPO --> HISTORY["Seurantatila ja ajohistoria"]
```

Kaavio on käsitteellinen: integraation kautta tapahtuva luku- tai kirjoitustoiminto voi olla yksittäinen vaihe ajon aikana. Se ei tarkoita, että kaikki seurantatyön vaiheet suoritettaisiin GitHub Actionsissa.

## 6. Virhetilanteet ja palautuminen

- **Lähtötiedot puuttuvat tai ovat ristiriidassa:** automaatio keskeyttää ennen hakuja tai julkaisuja. Vanhentunutta ohjetta tai arvattua seurantatilaa ei käytetä.
- **Lähde ei ole käytettävissä:** merkitään lähde tarkistamatta jääneeksi syineen. Hakutuloskatkelmaa ei tulkita alkuperäisen sisällön tarkistamiseksi.
- **Raportti ei täytä julkaisuehtoja:** raporttia korjataan tai se hylätään. RSS-muutosta ei julkaista ilman julkaisulaadun portin hyväksyntää ja vaadittuja testejä.
- **GitHub-kirjoitus epäonnistuu:** julkaisua ei väitetä onnistuneeksi. Kirjoitettu sisältö luetaan takaisin ennen onnistumisen kirjaamista.
- **GitHub Actions -aineiston muodostus epäonnistuu:** Pages-build pysähtyy ennen julkaisua. Viimeisin onnistunut sivustojulkaisu jää käyttöön.
- **Osittainen riippuvuusaineisto:** sitä ei julkaista täydellisenä. Kehitysjono näyttää välimuistin tai virheen rajauksen mukaisesti.
- **Ajastukseen tai automaatioasetukseen liittyvä ongelma:** ongelma raportoidaan; tehtävän ajastusta tai kohdekeskustelua ei muuteta ilman käyttäjän nimenomaista lupaa.

Virheiden käsittelyn yksityiskohtaiset menettelyt ovat kunkin automaation omassa käsikirjassa ja teknisten työnkulkujen dokumentaatiossa.

## 7. Teknologioiden vaihdettavuus ja siirrettävyys

Teknologian vaihtaminen on mahdollista, mutta se ei ole pelkkä palvelun nimen tai asetuksen muuttaminen. Siirto edellyttää, että uusi toteutus pystyy täyttämään nykyiset tietosopimukset, käsittelemään tehtäväkohtaisen tilan oikein ja suorittamaan samat laadunvarmistukset.

| Osa | Siirrettävä sisältö | Vaihdon edellyttämä työ |
|---|---|---|
| Ajastin | Tehtävien rytmi, jonon säännöt ja erillisten prosessien periaatteet | Uusi ajastin, aikavyöhykkeet, päällekkäisten ajojen esto, uusintayritykset ja tehtävien omistajuus |
| Tekoälypalvelu | Aiheohjeet, lähderekisterit, yhteiset toimitukselliset säännöt ja raporttien rakenteet | Promptien ja työkalukutsujen sovitus, haku- ja selainominaisuudet, kontekstin hallinta sekä tulosten laadun vertailu |
| Suoritusympäristö | Prosessin vaiheet ja hyväksymiskriteerit | Käyttöympäristö, riippuvuudet, salaisuuksien hallinta, ajonaikainen valvonta ja virheistä palautuminen |
| GitHub-integraatio | Tietomallit, tiedostopolut ja versionhallinnan työnkulkuperiaatteet | Uusi API-/connector-adapteri, tunnistautuminen, oikeuksien rajaus, konfliktien ja uudelleenyritysten käsittely |
| Tallennus | JSON-skeemat, RSS-rakenne, tunnisteet ja tapahtumahistorian periaatteet | Tallennusadapteri, migraatiot, varmistukset, palautus ja tietojen eheyden tarkistus |
| Julkaisu | Raporttisisältö, lähdeviitteet ja julkaisun hyväksymisehdot | Uusi jakelukanava tai julkaisupalvelu, URL-osoitteet, välimuisti ja lukijoiden siirtymä |
| Testaus ja valvonta | Hyväksymiskriteerit, testitapaukset ja raportointiperiaatteet | Uudet integraatio- ja päästä päähän -testit sekä hälytykset ja käyttötilan seuranta |

### 7.1 Mitä voidaan siirtää sellaisenaan?

Todennäköisimmin siirrettäviä ovat aiheiden kuvaukset, hakukriteerit, lähderekisterit, yhteiset toimitukselliset säännöt, JSON-skeemat, RSS-sisältöjen rakenne, seurantahistorian tietomallit ja dokumentoidut hyväksymiskriteerit. Ne eivät lähtökohtaisesti riipu ChatGPT:n tai GitHub Actionsin käyttöliittymästä.

### 7.2 Mitä täytyy sovittaa uudelleen?

ChatGPT:n tehtäväasetukset, käynnistyskehotteet, mallikohtaiset työkalukutsut ja integraation toimintatavat ovat alustakohtaisia. Niitä ei voi olettaa siirrettäviksi sellaisenaan toiseen tekoälypalveluun. Samoin GitHub Actions -YAML, GitHub API -kutsut, käyttöoikeusmallit ja Pages-julkaisun toteutus ovat GitHubiin sidottuja.

Uuden toteutuksen tulee tarjota vastaavat adapterit ainakin seuraaville rajapinnoille:

- `Scheduler`: käynnistää oikean tehtävän ja estää saman tehtävän päällekkäiset ajot;
- `ResearchProvider`: hakee lähteitä ja avaa alkuperäisiä sisältöjä;
- `AIProcessor`: arvioi lähteitä, muodostaa löydökset ja raportit;
- `RepositoryAdapter`: lukee määritykset ja kirjoittaa hyväksytyt muutokset;
- `StateStore`: säilyttää tarkistuspisteet, historian ja yksilölliset tunnisteet;
- `Publisher`: julkaisee raportit ja varmistaa takaisinluvun;
- `QualityGate`: suorittaa sisällölliset ja rakenteelliset hyväksymistarkistukset.

Nämä ovat arkkitehtuurin rajapintasuosituksia, eivät nykyisessä repositoriossa jo toteutettuja ohjelmistoluokkia tai API-rajapintoja.

### 7.3 Siirron vähimmäisvaatimukset

Ennen tuotantokäyttöä vaihtoehtoisen toteutuksen tulee osoittaa vähintään:

1. Kaikki nykyiset aiheet ja niiden erilliset rajaukset säilyvät.
2. Tehtäväjono ja seurantajaksot jatkuvat oikeista tarkistuspisteistä.
3. Uudet ja aiemmin käsitellyt tapahtumat erotetaan ilman duplikaatteja.
4. Alkuperäiset lähteet, väitteiden varmennustasot ja lähderiippuvuudet säilyvät jäljitettävinä.
5. Kirjoitukset ovat idempotentteja tai niiden uudelleenyritykset eivät tuota päällekkäisiä julkaisuja.
6. Virhe ei siirrä onnistumisen tarkistuspistettä eikä julkaise osittaista aineistoa täydellisenä.
7. Tunnukset ja salaisuudet säilytetään uudessa ympäristössä turvallisesti ja vähimmillä oikeuksilla.
8. Tietomallit voidaan migroida ja palauttaa, ja vanha julkaistu historia säilyy.
9. Uuden toteutuksen integraatio-, regressio- ja päästä päähän -testit kattavat samat kriittiset tapaukset.
10. Vanha ja uusi toteutus voidaan ajaa rajatusti rinnakkain vertailua varten ennen kuin uusi toteutus ottaa tuotantovastuun.

## 8. Tavoitearkkitehtuuri

Tässä luvussa kuvataan järjestelmän tavoiteltu kokonaisuus. Se on suunnittelun tavoitetila, ei kuvaus jo käytössä olevasta toteutuksesta. Tavoitteena on tehdä aiheiden lisäämisestä, suoritusympäristön vaihtamisesta, ajon valvonnasta ja tietojen säilyttämisestä hallittua sitomatta toimituksellisia periaatteita yhteen palveluun.

Tavoitetilassa järjestelmä muodostuu kolmesta erotetusta kokonaisuudesta:

1. **Aihekohtaiset määritykset** kertovat, mitä seurataan, millä rajauksilla ja millä lähteillä.
2. **Yhteinen seurantaprosessi** toteuttaa tehtävien valinnan, haun, arvioinnin, raportoinnin, laadunvarmistuksen ja onnistumisen kirjaamisen.
3. **Tekninen suoritus- ja integraatiokerros** tarjoaa ajastuksen, jonotuksen, suoritusympäristön, ulkoiset yhteydet, tallennuksen, testauksen, valvonnan ja julkaisun.

Kerrokset kommunikoivat määriteltyjen tietosopimusten ja rajapintojen kautta. Aihekohtainen määritys ei sisällä palveluntarjoajan tunnuksia tai ajastimen asetuksia. Tekninen adapteri ei päätä uutisen uutisarvosta eikä muuta aiheen rajausta.

### 8.1 Tavoiteltu kokonaisrakenne ja vastuut

~~~mermaid
flowchart TB
    subgraph CONFIG["Aihekohtaiset määritykset"]
      TOPICS["Aiheiden rajaukset ja hakuprofiilit"]
      SOURCES["Lähdekatalogi ja tehtäväkohtaiset lähdekäytöt"]
      POLICIES["Aihekohtaiset poikkeukset ja raportointiprofiilit"]
    end
    subgraph ORCH["Yhteinen seurantaprosessi"]
      QUEUE["Tehtäväjono ja tehtävän valinta"]
      RUN["Ajon elinkaari ja tarkistuspiste"]
      RESEARCH["Haku ja löydösten käsittely"]
      ASSESS["Lähteiden ja väitteiden arviointi"]
      REPORT["Raportin muodostus"]
      GATE["Julkaisulaadun portti"]
      STATE["Tilapäivitys ja historian kirjaus"]
    end
    subgraph PLATFORM["Tekninen suoritus- ja integraatiokerros"]
      SCHED["Ajastin ja käynnistimet"]
      WORKER["Suoritusympäristö"]
      AI["Tekoäly- ja tutkimuspalvelut"]
      REPO["Versionhallinta- ja repositorioadapteri"]
      STORE["Tallennusadapteri"]
      OBS["Lokitus, mittarit ja hälytykset"]
      PUBLISH["Julkaisuadapteri"]
    end
    CONFIG --> QUEUE
    SCHED --> QUEUE
    QUEUE --> RUN --> RESEARCH --> ASSESS --> REPORT --> GATE
    GATE -->|hyväksytty| STATE
    GATE -->|hylätty| RUN
    RUN <--> WORKER
    RESEARCH <--> AI
    ASSESS <--> AI
    CONFIG <--> REPO
    STATE <--> STORE
    REPORT --> PUBLISH
    RUN --> OBS
    RESEARCH --> OBS
    GATE --> OBS
    PUBLISH --> OBS
~~~

Vastuut:

| Kokonaisuus | Vastuu | Ei kuulu vastuulle |
|---|---|---|
| Aihekohtainen määritys | Seurannan kohde, rajaukset, hakusanat, kielet, alueet, lähdeviittaukset ja erityissäännöt | Salaisuudet, ajastimen toteutus tai palvelukohtaiset API-kutsut |
| Tehtäväjono | Tehtävien järjestys, valintakelpoisuus, prioriteetti ja erillisten prosessien tunnistaminen | Varsinainen tiedonhaku tai raportin kirjoittaminen |
| Ajonhallinta | Ajon tunniste, tila, vaiheiden järjestys, aikakatkaisut ja tarkistuspisteet | Aihekohtainen uutisarvopäätös |
| Tutkimus ja arviointi | Haku, alkuperäislähteiden tarkistus, löydösten deduplikointi ja väitteiden arviointi | Julkaisukanavan tekninen toteutus |
| Laadunvarmistus | Sisällölliset ja rakenteelliset hyväksymisehdot sekä hylkäyksen perustelut | Hylätyn sisällön ohittaminen |
| Tallennus ja historia | Kanonisten tietojen, tarkistuspisteiden ja tapahtumien eheä säilytys | Käyttöliittymän rinnakkaiset totuuden lähteet |
| Julkaisu | Hyväksytyn raportin toimittaminen ja takaisinlukutarkistus | Julkaisuluvan myöntäminen laadunvarmistuksen ohi |
| Valvonta | Ajon etenemisen, virheiden, viiveiden ja palveluiden toimintakyvyn näkyvyys | Puuttuvan tiedon tulkitseminen onnistumiseksi |

Näytösvahti säilyy omana tehtävätyyppinään ja omine tapahtumamalleineen. Se voi käyttää yhteisiä ajonhallinnan, lähteiden, tallennuksen ja julkaisun palveluja, mutta sen päivittäistä näytöslogiikkaa ei yhdistetä uutisaiheiden kiertoon. Laatutarkistus on edelleen auditointitehtävä, jolla on erikseen rajatut luku- ja kirjausoikeudet.

### 8.2 Ajastus, tehtäväjono ja ajon elinkaari

Ajastin käynnistää tehtäväjonon käsittelyn tai yksittäisen erillisprosessin. Ajastin ei itse päätä, mitä aihetta seurataan. Tehtäväjono valitsee suoritettavan tehtävän tallennetun jonotilan, tehtävätyypin ja riippuvuuksien perusteella.

Jokainen suoritus muodostaa yksilöllisen ajon. Ajon vähimmäiselinkaari on:

1. Käynnistys vastaanotetaan ja sille luodaan yksilöllinen ajotunniste.
2. Tehtävä lukitaan tai sille varataan suoritusvuoro, jotta päällekkäiset ajot eivät muuta samaa tarkistuspistettä samanaikaisesti.
3. Ajon määritykset, ohjeversiot, lähdeprofiili ja edellinen onnistunut tarkistuspiste luetaan ja validoidaan.
4. Haku, alkuperäislähteiden tarkistus, arviointi ja raportin muodostus suoritetaan vaiheittain.
5. Laadunvarmistus hyväksyy tai hylkää raportin. Hylkäys ei saa edistää onnistumisen tarkistuspistettä.
6. Hyväksytty raportti julkaistaan idempotentisti ja luetaan takaisin.
7. Vasta onnistuneen takaisinluvun jälkeen päivitetään viimeisin onnistuminen, tehtäväjonon tila ja ajon lopputulos.
8. Ajon tapahtumat, käytetyt määritysversiot, lähdetarkistukset ja julkaisun tunnisteet jäävät jälkikäteen tarkasteltaviksi.

Tehtäväjonon tilat erotetaan yksittäisen ajon tiloista. Jonossa tehtävä voi olla odottava, valittavissa, käynnissä tai estynyt. Ajo voi puolestaan olla käynnissä, onnistunut, epäonnistunut, osittainen tai peruutettu. Näitä ei yhdistetä yhdeksi epäselväksi tilakentäksi.

Ajastuksen tekninen toteutus voidaan vaihtaa, mutta tehtävien aikavyöhykkeet, päällekkäisten ajojen esto, uusintayritykset, tehtävien erillisyys ja käyttäjän valtuutusrajoitukset säilyvät tietosopimuksina. Ajastimen vaihtaminen ei itsessään oikeuta muuttamaan käyttäjän hyväksymää aikataulua.

### 8.3 Kanoniset tallennuspaikat ja tietomallien vastuut

Tavoitetilassa jokaisella tiedolla on yksi ensisijainen omistaja ja kanoninen tallennuspaikka. Käyttöliittymien, raporttien ja välimuistien muodostamat johdetut näkymät eivät muutu rinnakkaisiksi totuuden lähteiksi.

| Tieto | Kanoninen omistaja tavoitetilassa | Tietosisältö ja sääntö |
|---|---|---|
| Aiheiden määritykset | Aihekonfiguraatioiden versioitu rekisteri | Aihe-ID, rajaus, hakuprofiilit, kielet, alueet, poikkeukset ja raportointiprofiili |
| Lähteiden perustiedot | Yhteinen lähdekatalogi | Yksilöllinen lähde-ID, nimi, URL, lähdetyyppi ja yhteinen arvio |
| Tehtäväkohtaiset lähdekäytöt | Tehtäväkohtainen lähderekisteri | Viittaukset lähdekatalogiin, kriittisyys, käyttörajoitteet ja tehtäväkohtaiset asetukset |
| Tehtäväjono | Tehtäväjonon kanoninen tila | Tehtävien järjestys, tyyppi, valintakelpoisuus ja seuraava vuoro |
| Ajon tila ja tarkistuspisteet | Ajonhallinnan tilarekisteri | Ajotunniste, tehtävä, vaiheet, aloitus/lopetus, tulos ja viimeisin onnistunut tarkistuspiste |
| Lähdetarkistukset | Ajon lähdehavaintojen loki | Tarkistetut lähteet, tarkistusajankohta, tulos ja tarkistamatta jäämisen syy |
| Raportit ja julkaisut | Julkaisuarkisto tai kanoninen jakelukanava | Raportin sisältö, yksilöllinen tunniste, seurantajakso, lähteet ja julkaisun tila |
| Tapahtumahistoria | Tehtäväkohtainen append-only-tapahtumaloki | Havaitut lisäykset, muutokset, poistumat ja niiden alkuperä |
| Skeemat ja sopimukset | Versionhallittu skeemarekisteri | Rakenteet, sallitut arvot, yhteensopivuus ja migraatiot |
| Auditointi ja tekninen havaittavuus | Ajon loki- ja mittaripalvelu | Vaiheiden tapahtumat, virhekoodit, kesto, uudelleenyritykset ja hälytykset |

Nykyiset tiedostot ovat näiden tietoluokkien lähtökohta, eivät lupaus siitä, että jokainen tuleva tieto sijoitetaan yhteen suureen JSON-tiedostoon. Tallennusratkaisu voidaan myöhemmin vaihtaa esimerkiksi tietokantaan tai objektitallennukseen, jos volyymi, kyselytarpeet tai säilytysvaatimukset sitä edellyttävät. Vaihdon yhteydessä säilytetään tunnisteet, skeemojen semantiikka, tapahtumien järjestys ja palautettavuus.

Ajon tapahtumaloki on ensisijaisesti vain lisäävä. Korjaus tai uudelleenluokittelu kirjataan uutena tapahtumana, joka viittaa korjattuun tapahtumaan; aiempaa havaintoa ei hävitetä jälkiä jättämättä. Raportin nykytila voidaan muodostaa tapahtumista tai tallentaa suorituskyvyn vuoksi johdettuna näkymänä, mutta johdettu näkymä voidaan aina rakentaa uudelleen kanonisesta historiasta.

### 8.4 Tavoitellut rajapinnat ja teknologioiden vaihdettavuus

Toteutuksen osat kommunikoivat versionhallituilla tietosopimuksilla. Tavoiteltuja loogisia rajapintoja ovat:

| Rajapinta | Syöte | Tuloste / vastuu |
|---|---|---|
| Scheduler | Tehtävän tunniste tai käynnistystapa | Käynnistystapahtuma ja ajastusmetatiedot |
| Queue | Tehtävätyypit, jonotila ja riippuvuudet | Valittu tehtävä ja varaus |
| ConfigurationProvider | Tehtävä-ID ja määritysversio | Validoitu aihe- ja lähdemääritys |
| ResearchProvider | Hakuprofiili, lähteet ja seurantajakso | Lähdeviitteelliset löydökset ja tarkistustulokset |
| AIProcessor | Löydökset, lähdesisällöt ja toimitukselliset säännöt | Arvioidut väitteet, deduplikoidut tapahtumat ja raporttiluonnos |
| QualityGate | Raportti ja hyväksymissäännöt | Hyväksyntä tai hylkäys perusteluineen |
| StateStore | Ajon tapahtumat ja tilapäivitykset | Pysyvä tila, tarkistuspisteet ja historiatiedot |
| Publisher | Hyväksytty julkaisu ja idempotenssiavain | Julkaisutunniste ja takaisinlukutulos |
| Observability | Ajon tapahtumat ja mittarit | Lokit, tilannekuva, hälytykset ja auditointijälki |

Rajapintojen nimet ovat käsitteellisiä sopimuksia, eivät väitteitä nykyisistä ohjelmistoluokista tai valmiista API-rajapinnoista. Niiden konkreettinen toteutus voidaan tehdä funktioina, palveluina tai viestipohjaisina rajapintoina.

Tekoälypalvelu ei ole järjestelmän ainoa paikka, jossa toimitukselliset säännöt sijaitsevat. Aiheiden rajaukset, luotettavuusluokitus, julkaisun hyväksymisehdot ja skeemat ovat erikseen versionhallittuja. Tekoälypalvelun vaihdossa mallikohtaiset kehotteet ja työkalut sovitetaan uudelleen, mutta niiden on tuotettava sama sovittu tietorakenne ja läpäistävä samat laadunvarmistukset.

GitHub on nykyinen versionhallinta- ja yhteistyöalusta. Tavoitearkkitehtuuri ei edellytä sen vaihtamista. Jos versionhallinta tai julkaisualusta myöhemmin vaihtuu, GitHub-kohtainen API- ja Actions-logiikka rajataan adaptereihin; aihe- ja tietomäärityksiä ei kirjoiteta uudelleen vain alustan vaihtamisen vuoksi.

### 8.5 Tietovirrat päästä päähän

```mermaid
sequenceDiagram
    participant T as Ajastin
    participant Q as Tehtäväjono
    participant R as Ajonhallinta
    participant C as Määritykset ja lähteet
    participant H as Haku ja arviointi
    participant G as Laadunvarmistus
    participant S as Tila ja historia
    participant P as Julkaisu
    participant O as Valvonta

    T->>Q: Käynnistys
    Q->>R: Varaa tehtävä
    R->>C: Lue versioidut määritykset
    C-->>R: Määritykset ja tarkistuspiste
    R->>O: Ajo aloitettu
    R->>H: Hae ja arvioi
    H-->>R: Löydökset ja lähdetarkistukset
    R->>G: Raporttiluonnos
    G-->>R: Hyväksyntä tai hylkäys
    alt Hyväksytty
        R->>P: Julkaise idempotentisti
        P-->>R: Julkaisutunniste ja takaisinluku
        R->>S: Kirjaa onnistuminen ja tarkistuspiste
    else Hylätty tai julkaisu epäonnistuu
        R->>S: Kirjaa virhe; säilytä vanha tarkistuspiste
    end
    R->>O: Ajon lopputulos ja mittarit
    R->>Q: Vapauta tehtävä / määritä seuraava tila
```

Jokaisen tietovirran mukana kulkee riittävä alkuperätieto: tehtävä-ID, ajotunniste, määritysversio, seurantajakso, lähde-ID:t ja julkaisun yksilöivä tunniste. Näin raportin voi jäljittää siihen, millä ohjeilla ja lähteillä se muodostettiin. Salaisuuksia, tunnuksia tai tarpeettomia henkilötietoja ei sisällytetä raportteihin tai julkisiin tilatietoihin.

### 8.6 Virheistä palautuminen, jäljitettävyys ja turvallisuus

Tavoitetilan virheenkäsittely perustuu siihen, ettei epäonnistunut tai epäselvä vaihe saa näyttää onnistumiselta.

- **Päällekkäinen käynnistys:** tehtävän varaus tai lukitus estää kaksi ajoa päivittämästä samaa tarkistuspistettä samanaikaisesti. Lukituksen vanheneminen ja vapautus ovat jäljitettäviä.
- **Tilapäinen ulkoinen virhe:** rajatut uusintayritykset käyttävät viiveitä ja enimmäisrajaa. Pysyvä virhe päättää ajon hallitusti.
- **Osittainen haku:** lähdekohtainen tulos kirjataan. Puuttuva lähde tai alue ei muutu hiljaisesti onnistuneeksi tarkistukseksi.
- **Tekoälyn tai jäsennyksen virhe:** virheellinen tulos hylätään sopimuksen vastaisena; sitä ei siirretä julkaisuun.
- **Tallennusvirhe:** onnistumisen tarkistuspistettä ei siirretä. Uusinta käyttää samaa idempotenssiavainta.
- **Julkaisuvirhe tai epäselvä vastaus:** julkaisun tila selvitetään takaisinluvulla ennen uutta yritystä. Sama julkaisu ei saa syntyä kahdesti.
- **Laadunvarmistuksen hylkäys:** raportti ja perustelut säilytetään auditointia varten, mutta julkaisu ja onnistumisen tarkistuspiste jäävät tekemättä.
- **Palautus:** viimeisin tunnettu hyvä tila ja julkaistu aineisto säilytetään. Tietomallin migraatiolla on testattu palautus- tai eteenpäin korjaamisen menettely.

Jokaisesta ajosta tulee voida vastata vähintään: mikä tehtävä suoritettiin, milloin, millä määritys- ja skeemaversiolla, mitkä lähteet tarkistettiin, mitkä jäivät tarkistamatta ja miksi, mitä vaiheita suoritettiin, mikä hyväksyttiin tai hylättiin, mitä julkaistiin ja mikä oli lopputulos.

Käyttöoikeudet jaetaan tehtävä- ja komponenttikohtaisesti vähimmän tarpeen periaatteella. Julkinen verkkosivusto saa lukea vain julkistettavaksi hyväksyttyä aineistoa. Sillä ei ole kirjoitustunnuksia. Tunnukset säilytetään suoritusympäristön salaisuuksien hallinnassa, niitä ei tulosteta lokeihin eikä välitetä tekoälymallille tarpeettomasti. Auditointitehtävällä on vain ne kirjoitusoikeudet, joita sen rajattu tilakirjaus edellyttää.

### 8.7 Testaus, valvonta ja julkaisun hyväksymisehdot

Testaus on kerroksittaista:

1. **Määritysten ja skeemojen testit:** virheelliset aiherajaukset, lähdeviittaukset, tilat ja versiot hylätään ennen ajoa.
2. **Yksikkötestit:** tehtäväjono, aikavälit, deduplikointi, tilasiirtymät, idempotenssi ja virheiden käsittely.
3. **Integraatiotestit:** haku-, tallennus-, versionhallinta- ja julkaisusovittimien sopimukset testataan erikseen.
4. **Regressiotestit:** vanhojen raporttien, GUIDien, tapahtumien ja tarkistuspisteiden säilyminen varmistetaan.
5. **Päästä päähän -testit:** rajattu testiajo osoittaa koko polun käynnistyksestä takaisinluettuun julkaisuun. Testiympäristö ei saa muuttaa tuotannon tehtäväjonoa tai tarkistuspisteitä.
6. **Manuaaliset hyväksyntätestit:** käyttöliittymän saavutettavuus, raportin luettavuus ja todellisten lähteiden asianmukainen tulkinta arvioidaan siltä osin kuin niitä ei voi luotettavasti automatisoida.

Julkaisu hyväksytään vain, kun:

- raportin seurantajakso ja tehtävä ovat yksiselitteiset;
- olennaiset väitteet on arvioitu alkuperäislähteitä vasten ja epävarmuudet ilmaistu;
- lähdeviitteet ovat mukana ja niiden käyttö on jäljitettävissä;
- raportin rakenne, kieli, saavutettavuus ja aiherajaus täyttävät sovitut ehdot;
- skeema-, RSS/XML-, HTML- ja muut soveltuvat rakennetestit läpäisevät;
- julkaisun yksilöllisyys ja vanhan historian säilyminen on varmistettu;
- julkaistu sisältö on luettu takaisin ja vastaa hyväksyttyä sisältöä.

Valvonta näyttää erikseen ajon käynnistymisen, vaiheet, viimeisimmän onnistumisen, varoitukset, virheet, lähdekattavuuden ja julkaisun tilan. Puuttuvaa vaihedataa ei päätellä eikä esitetä onnistuneena. Valvomon julkiset tiedot rajataan niin, etteivät lokit tai virhevastaukset paljasta salaisuuksia.

### 8.8 Nykytilan ja tavoitetilan erot

| Osa | Nykytila (varmennettu tässä dokumentissa) | Tavoitetila | Muutoksen luonne |
|---|---|---|---|
| Aiheiden määritykset | Ohjeet ovat pääosin Markdown-dokumenteissa; osa tilasta ja lähteistä on JSON-muodossa | Selkeästi versioidut, validoidut aihe- ja hakuprofiilit; poikkeukset voivat säilyä dokumentoituina | Rakenteistaminen vaiheittain, ei kaiken pakottaminen yhteen skeemaan |
| Ajastus | ChatGPT:n kolme ajoitettua tehtävää; asetukset ovat ChatGPT-palvelussa | Vaihdettava ajastinadapteri ja eksplisiittinen tehtävien käynnistys-/lukitusmalli | Ajastuksen ja tehtävälogiikan erottaminen |
| Tehtäväjono | Yhdeksän aiheen kierto on dokumentoitu ja koneellinen tila on data/seurantatila.json-tiedostossa | Jonon oma versioitu tietosopimus, tilasiirtymät ja varausmekanismi | Nykyisen tilan täsmentäminen ja rinnakkaisten ajojen esto |
| Suoritus | Haku, arviointi ja raportointi tehdään ChatGPT:ssä; Actions hoitaa teknisiä työnkulkuja | Yhteisen prosessin vaiheet määritellyillä adapterirajapinnoilla | Suorituksen siirrettävyys ja vaiheiden eksplisiittisyys |
| Ajohistoria | ChatGPT-automaatioiden vaihehistoria on erillisissä haaroissa; koneellisten tietojen kattavuus on osittainen | Yhtenäinen ajotunniste, vaihe- ja lähdekohtainen auditointijälki | Tietomallin ja kirjaamisen yhdenmukaistaminen |
| Tallennus | Versionhallittu GitHub-repositorio ja JSON-tiedostot | Kanoniset tallennusrajapinnat; tallennuspalvelu vaihdettavissa tietosopimuksia säilyttäen | Adapteri ja mahdollinen migraatio vasta tarpeen mukaan |
| Julkaisu | RSS ja GitHub Pages; hyväksymisportti ja takaisinlukumenettely | Julkaisukanavasta riippumaton julkaisuadapteri, idempotenssi ja takaisinlukutodiste | Nykyisen laadunvarmistuksen säilyttäminen eri kanavissa |
| Testaus ja valvonta | GitHub Actions -rakennetestit, Pages-julkaisun tarkistukset ja erillinen linkkitarkistus; osa manuaalisesta testauksesta avoinna | Sopimustestit, integraatio- ja päästä päähän -testit sekä ajonaikainen valvonta | Testauksen kattavuuden laajentaminen todellisten tarpeiden mukaan |

Nykytilan taulukko kuvaa repositoriosta ja aiemmin dokumentoiduista toteutuksista varmennettuja asioita. Se ei väitä, että kaikkien ChatGPT-palvelun sisäisiä toteutustietoja tai tallennettuja ajastusasetuksia olisi tarkistettu.

### 8.9 Siirtymävaiheet

Tavoitetilaan siirrytään pienin, palautettavin muutoksin. Nykyistä tuotantopolkua ei korvata ennen kuin uuden osan sopivuus on osoitettu.

1. **Tietosopimusten täsmennys:** inventoidaan nykyiset JSON-tiedostot, Markdown-määritykset, RSS-rakenteet ja ajohistorian tiedot. Määritellään omistajuus, tunnisteet, versiot ja yhteensopivuussäännöt. Nykyisiä kanonisia tiedostoja ei kopioida rinnakkaiseen rekisteriin.
2. **Aihe- ja lähdemääritysten validointi:** rakenteistetaan vain ne kentät, joiden koneellinen käsittely hyödyttää toistettavuutta. Markdown jää ihmiselle sopivaksi selittäväksi dokumentaatioksi ja poikkeusten kuvaukseksi.
3. **Ajon elinkaaren ja tapahtumakirjausten yhdenmukaistaminen:** käytetään yhteistä ajotunnistetta, täsmennetään vaihetilat, lähdehavainnot, idempotenssi ja tarkistuspisteiden päivitysehdot. Nykyinen erillinen näytösvahti säilyy omana tehtävätyyppinään.
4. **Adapterirajapintojen käyttöönotto nykyisen teknologian ympärille:** rajataan ajastin, tutkimuspalvelut, tekoäly, GitHub, tallennus ja julkaisu omiin sovittimiinsa. Ensimmäinen adapteri voi käyttää nykyisiä palveluja; vaihdon edellyttämää uutta palvelua ei tarvitse hankkia.
5. **Integraatio- ja palautumistestit:** testataan virhetilanteet, päällekkäiset ajot, uusintayritykset, osittainen lähdekattavuus, julkaisun epäselvä vastaus ja historian palautus erillisessä testiympäristössä.
6. **Rajattu rinnakkaisvertailu:** uutta toteutusta voidaan ajaa rajatulla aineistolla ilman tuotantokirjoituksia. Raporttien, lähteiden, tarkistuspisteiden ja ajankäytön erot arvioidaan dokumentoidusti.
7. **Hallittu tuotantosiirto:** vasta hyväksyttyjen testien ja erillisen käyttäjän päätöksen jälkeen siirretään tuotantovastuu. Siirtoon sisältyvät tietojen migraatio, palautussuunnitelma, käyttöoikeuksien tarkistus ja vanhan polun alasajo.

Vaiheita ei sidota tässä tiettyihin kalenteripäiviin tai palveluvalintoihin. Kukin vaihe pilkotaan GitHub Issues -tehtäviksi, kun sen edellytykset, laajuus ja hyväksymiskriteerit tunnetaan. Siirtymä ei muuta automaatioiden ajastuksia tai kohdekeskusteluja ilman erillistä nimenomaista lupaa.

### 8.10 Avoimet arkkitehtuuripäätökset

Seuraavia valintoja ei ole vielä perusteltua lukita:

- Tarvitaanko nykyisen ChatGPT-ajastuksen rinnalle tai tilalle erillinen ajastuspalvelu, vai riittääkö nykyinen käynnistysmalli.
- Tarvitaanko pysyvä työjono ja erillinen suorituspalvelu vai voidaanko nykyinen tehtäväkierto säilyttää kevyempänä.
- Milloin JSON-tiedostot eivät enää riitä kanoniseksi tallennukseksi ja millä mitattavilla perusteilla tietokanta olisi perusteltu.
- Kuinka pitkään yksityiskohtaisia ajolokeja, hakutuloksia ja väliaikaisia raporttiluonnoksia säilytetään.
- Tarvitaanko useita tekoäly- tai tutkimuspalveluja rinnakkain, ja miten niiden tuloksia vertaillaan.
- Mitkä tehtävät voidaan suorittaa rinnakkain ilman lähde-, tila- tai julkaisukonflikteja.
- Miten kustannuksia, suoritusrajoja, käyttöoikeuksia ja palvelukatkoja valvotaan.
- Mitkä tavoitetilan osat ovat yhteisiä kaikille tehtävätyypeille ja mitkä jäävät tarkoituksella näytösvahdin kaltaisiksi erillisprosesseiksi.

Päätökset tehdään vasta, kun käytännön kuormitus, virhetilanteet, ylläpitokustannukset ja käyttäjän tarpeet antavat niille perusteen. Teknologian uutuus tai arkkitehtuurin muodollinen monimutkaisuus ei yksin ole syy muutokseen.

## 9. Tosiasiat, päätelmät ja avoimet asiat

### 9.1 Repositoriosta ja työnkuluista varmennetut tosiasiat

- Repositorio sisältää kolme erillistä ChatGPT-automaatiota varten ylläpidettyä käsikirjaa ja käynnistyskehotetta.
- Pääautomaation tehtäväjono, lähdekatalogi, tehtäväkohtaiset lähderekisterit ja seurantatila ovat erillisiä tiedostoja.
- RSS-syötteet, näytöshistoria ja vaihekohtainen ajohistoria tallennetaan eri tiedostoihin tai haaroihin.
- GitHub Actionsissa on erilliset RSS-/dokumentaatiotestien, Pages-julkaisun, riippuvuuksien synkronoinnin ja linkkitarkistuksen työnkulut.
- Pages-julkaisu muodostaa ja validoi Kehitysjonon aineiston ennen Jekyll-julkaisua.
- ChatGPT:n ajastettujen tehtävien asetuksia ei tallenneta GitHub-repositorioon.

### 9.2 Arkkitehtuuripäätelmät ja suositukset

- Aihekohtaiset määritykset kannattaa pitää mahdollisimman rakenteisina ja erottaa yhteisistä toimituksellisista säännöistä.
- Ajastin, tekoälypalvelu, tallennus, GitHub-integraatio ja julkaisu kannattaa mallintaa vaihdettavina adaptereina.
- Teknologian vaihto tulee toteuttaa hallittuna migraationa, ei asetuksen vaihtona.
- Uusi toteutus tulee hyväksyä vasta, kun tietojen eheys, idempotenssi, virhetilanteet ja julkaisun takaisinluku on testattu.

Nämä ovat suunnittelupäätelmiä ja tulevan kehityksen suosituksia, eivät väitteitä jo toteutetuista adaptereista.

### 9.3 Avoimet ja erikseen varmennettavat asiat

- ChatGPT:n kolmen ajoitetun tehtävän tallennetut tarkat aikataulut, aikavyöhykkeet, aktiivisuus ja kohdekeskustelut tulee tarkistaa ChatGPT:n tehtäväasetuksista. Niitä ei voi vahvistaa GitHubin tiedostoista.
- GitHub-integraation käyttäjäkohtainen repositorioiden valinta ja todelliset tehokkaat käyttöoikeudet tulee tarkistaa GitHub-sovelluksen ja ChatGPT-yhteyden asetuksista.
- Vaihtoehtoisen tekoälypalvelun tai ajastimen valintaa ei ole tehty.
- Adapterirajapintoja, migraatiotyökaluja tai toista suoritusympäristöä ei ole tämän dokumentin yhteydessä toteutettu.
- Nykyisten aihekohtaisten ohjeiden täydellinen muuttaminen koneellisesti luettaviksi määrityksiksi vaatisi erillisen kartoituksen. Kaikki poikkeukset eivät välttämättä sovellu rakenteiseen yhteiseen malliin.

## 10. Automaatioiden hallinnan rajat

Tämä arkkitehtuurikuvaus ei anna lupaa muuttaa ChatGPT:n ajastettuja tehtäviä, niiden aktiivisuutta, suoritusvälejä, kellonaikoja, aikavyöhykkeitä, käynnistysohjeita tai kohdekeskusteluja. Se ei myöskään anna lupaa luoda korvaavia automaatioita, vaihtaa tekoälypalvelua, muuttaa GitHub-yhteyden oikeuksia tai ottaa käyttöön uutta suoritusympäristöä.

Kaikkia automaatioita koskeva käyttäjän valtuutukseen perustuva sääntö on määritelty ensisijaisesti dokumentissa [Automaatioiden hallinnan suojausperiaatteet](automaation-hallintaperiaatteet.md). Nykyisten automaatioiden yksityiskohtaiset toimintatavat ovat niiden omissa käsikirjoissa.

## 11. Aiheeseen liittyvät ensisijaiset dokumentit

- [Aloitus ja dokumentaation lukujärjestys](aloitus-ja-lukujarjestys.md)
- [Pääautomaation toimintakäsikirja](paaautomaation-ohje.md)
- [Intialaisten elokuvien näytösseurannan käsikirja](intialaisten-elokuvien-naytosseuranta.md)
- [Viikoittaisen laatutarkistuksen käsikirja](laatutarkistuksen-ohje.md)
- [Seurantaohje](seuranta.md)
- [Lähteet ja hakustrategia](lahteet.md)
- [Uutislähteiden ja uutisväitteiden luotettavuusluokitus](luotettavuusluokitus.md)
- [Tietomallit ja prosessikaaviot](tietomallit-ja-prosessit.md)
- [Kehitysjonon julkaistu aineisto](kehitysjonon-aineisto.md)
- [Automaatioiden hallinnan suojausperiaatteet](automaation-hallintaperiaatteet.md)

## 12. Muutoshistoria

- **1.1.1 – 2026-11-17:** korjattiin luvun 9 alaotsikoiden numerointi.
- **1.1.0 – 2026-11-17:** lisättiin tavoitearkkitehtuuri, komponenttien vastuut ja rajapinnat, tietovirrat, kanonisen tiedon omistajuus, virheistä palautuminen, hyväksymisehdot, nykytila–tavoitetila-vertailu, siirtymävaiheet ja avoimet päätökset.
- **1.0.0 – 2026-11-17:** kuvattiin järjestelmäriippumaton toimintamalli, kolmen arkkitehtuurikerroksen vastuut, nykyinen ChatGPT/GitHub-toteutus, tietovirrat sekä teknologioiden vaihdettavuuden edellytykset. Erotettiin repositoriosta varmennetut tosiasiat, päätelmät ja erikseen tarkistettavat asetukset.
