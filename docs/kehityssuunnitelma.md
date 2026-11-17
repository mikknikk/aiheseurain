# Aiheseuraimen kehityssuunnitelma

**Tila:** tavoitekuvaus ja kehitysjono määritelty; Valvomon vähimmäisversio (#30) ja siirto omalle sivulleen (#38) on yhdistetty. RSS-lukijan vähimmäisversio (#31) ja Kehitysjonon kanbanin vähimmäisversio (#35) ovat toteutettuina omissa PR-muutoksissaan.  
**Päivitetty:** 2026-11-17

Tämä dokumentti kuvaa koko GitHub Pages -sivuston tavoitetilan, osioiden vastuut, tekniset periaatteet ja vaiheistuksen. Yksittäisten kehitystehtävien ajantasainen tila ylläpidetään GitHub Issues -tiketteinä; tätä dokumenttia ei käytetä rinnakkaisena tehtävälistana. Suunnitelman kirjaaminen ei tarkoita, että ominaisuus olisi jo käytössä.

## 1. Kokonaisratkaisu

Tavoitteena on yksi GitHub Pages -sivusto, jonka kolme toisiinsa liittyvää osiota ovat:

1. **Valvomo:** näyttää automaatioiden todellisen etenemisen, viimeisimmät ajot, virheet, aihekierroksen tilanteen ja lähteiden tarkistuksen kattavuuden.
2. **RSS-lukija:** kokoaa repositorion RSS-syötteet yhteen käyttöliittymään ja tarjoaa aiheen, ajan ja lukutilan mukaisen selailun.
3. **Kehitysjono:** näyttää GitHub Issues -tiketteihin perustuvan kanban-taulun, josta näkee suunnitellut, työn alla olevat, estyneet ja valmiit kehitystehtävät.

Raporttiarkisto on mahdollinen myöhempi ominaisuus, ei oma ensisijainen osionsa. Sen tarve arvioidaan erillisenä kehitystikettinä.

Käyttöliittymä on staattinen GitHub Pages -sivusto. Se lukee automaatioiden tuottamia julkisia JSON-tiedostoja ja RSS-syötteitä, mutta ei tarvitse selaimessa GitHub-kirjoitusoikeuksia, salaisuuksia tai käyttäjätunnistusta. Automaatiot ja niiden tietojen keruu pysyvät erillään käyttöliittymästä.

Sivuston juuri (`/`) toimii Aiheseuraimen etusivuna. Valvomolla on oma osoite `/valvomo/` ja RSS-lukijalla `/lukija/`; Kehitysjonolle varataan oma reitti sen valmistuessa. Kaikki sivut käyttävät samaa Jekyll-sivupohjaa ja navigaatiota. Sivuston rakentaminen ei saa rikkoa nykyistä RSS-jakelua tai sen kanonisia Pages-osoitteita.

## 2. Valvomo: seurannan tila

### 2.1 Automaatioiden erottelu

Valvomon on esitettävä automaatiot erillisinä kokonaisuuksina:

- **Pääautomaation yhdeksän aiheen kierto:** käsittelee kullakin ajolla vain yhden tehtäväjonossa määritellyn aiheen.
- **Intialaisten elokuvien näytösvahti:** erillinen päivittäinen automaatio; ei kuluta aihekierroksen vuoroa eikä kuulu pääautomaation lähde- tai raportointituloksiin.
- **Viikoittainen laatutarkistus:** erillinen, ensisijaisesti vain luku -auditointi, jonka rajatut seurantatietojen päivitysoikeudet säilyvät nykyisen käsikirjan mukaisina.

Valvomo ei saa yhdistää eri automaatioiden lähdehakuja, tuloksia, onnistumisaikoja tai virheitä yhdeksi harhaanjohtavaksi kokonaisluvuksi.

### 2.2 Ajovaiheet ja niiden tila

Pääautomaation ajosta pyritään näyttämään seuraavat vaiheet silloin, kun kyseinen vaihe kuuluu tehtävän käsittelyyn:

1. Käynnistys ja lähtötilan tarkistus.
2. Tehtävävuoron ja aihealueen valinta.
3. Lähteiden ja hakujen valmistelu.
4. Uutisten ja lähteiden haku.
5. Väitteiden varmistus, ristiriidat ja luotettavuusluokat.
6. Raportin muodostaminen.
7. RSS-/HTML-rakenteen ja julkaisuehtojen validointi.
8. GitHub-julkaisu.
9. Julkaisun takaisinluku ja lopputarkistus.

Näytösvahdille ja laatutarkistukselle määritellään omat vaiheensa niiden käsikirjojen perusteella. Pääautomaation vaihelistaa ei kopioida niihin sellaisenaan.

Kunkin vaiheen mahdolliset tilat:

- `pending` – ei vielä aloitettu.
- `running` – käynnissä.
- `success` – onnistui.
- `failed` – epäonnistui.
- `skipped` – ohitettiin perustellusti.
- `warning` – valmistui, mutta havaittiin huomioitava puute.

Näytä mahdollisuuksien mukaan aloitus- ja päättymisaika, kesto, lyhyt selite sekä varoituksen tai virheen kuvaus. Linkitä vastaavaan GitHub Actions -ajoon, kun linkki on saatavilla.

Pelkkä GitHub Actions -työn vihreä tila ei riitä osoittamaan koko toimitusketjun onnistumista. Erityisesti RSS-tiedoston kirjoitus, takaisinluku ja sisällön säilyminen on erotettava omiksi tarkistuksikseen.

### 2.3 Aihekierron eteneminen

Valvomon tulee näyttää kaikki yhdeksän aihekierroksen tehtävää todellisessa järjestyksessään, viimeisin onnistunut tarkistus aiheittain, nykyinen tai viimeksi käsitelty tehtävä, seuraavaksi vuorossa oleva tehtävä sekä epäonnistuneet, keskeytyneet ja perustellusti ohitetut vuorot.

Aiheen vuoroa ei saa merkitä valmiiksi pelkän käynnistymisen tai osittaisen haun perusteella. Vuoro siirtyy vasta, kun tehtävän onnistumiskriteerit täyttyvät, tarvittavat julkaisut on tehty ja tulokset on luettu takaisin. Valvomon tieto johdetaan ensisijaisesti repositorion koneellisesta seurantatilasta ja varmennetuista ajotiedoista; sitä ei ylläpidetä käsin erillisenä totuutena.


Valvomo näyttää kullekin aiheelle myös arvioidun seuraavan käsittelyajan. Arvio perustuu `rotation.next_task` -kenttään, kiinteään jonojärjestykseen ja dokumentoituun päivittäiseen klo 12.00 Europe/Helsinki -aikatauluun. Se on nimenomaisesti arvio, ei vahvistettu ajoaika. Vanhentunut tai puuttuva jonotieto sekä epäonnistunut seuraava vuoro tuottavat epävarmuusviestin; epäonnistuneen vuoron jälkeen myöhempien aiheiden aikoja ei ennusteta. Erillinen päivittäinen näytösvahti näytetään omalla rytmillään, mutta sille ei näytetä kellonaikaa, jota seurantatieto ei sisällä. Tämä voidaan toteuttaa nykyisellä seurantatilalla ilman tiketin #37 vaihekohtaista ajohistoriaa.

### 2.4 Lähteiden tarkistus ja kattavuus

Näytä mahdollisuuksien mukaan aihe- ja ajokohtaisesti rekisteröityjen lähteiden määrä, tarkistukseen valittujen lähteiden määrä, onnistuneesti tarkistettujen lähteiden määrä, epäonnistuneet haut ja tekniset virheet, tarkistamatta jääneet lähteet syineen sekä kieli-, alue- ja lähdetyyppijakauma.

Erottele aina **yritykset**, **onnistuneet noudot** ja **sisällöllisesti läpikäydyt lähteet**. Hakukyselyiden määrä tai rekisteröityjen lähteiden lukumäärä ei yksin todista kattavuutta. Prosenttilukua saa käyttää vain, jos sen nimittäjä ja laskentatapa on määritelty ja näkyvissä.

`complete`-merkintä tarkoittaa nykyisen lähderekisterin kriittisten lähteiden operatiivista käsittelyä, ei täydellistä maailmanlaajuista uutiskattavuutta. Näytösvahdin lähteet raportoidaan omassa kokonaisuudessaan.

### 2.5 Virheet, varoitukset ja historia

Valvomo näyttää viimeisimpien ajojen virheet ja varoitukset esimerkiksi seuraavissa luokissa: lähde tai verkkosivu ei ollut käytettävissä; haku jäi osittaiseksi; RSS/XML- tai HTML-validointi epäonnistui; seurantatilan tai tehtäväkierron eheys rikkoutui; GitHub-kirjoitus epäonnistui tai sen tulos jäi epäselväksi; takaisinlukutarkistus epäonnistui; virhe korjattiin automaattisesti uusintayrityksellä.

Erota avoin ongelma, korjattu ongelma ja tilapäinen varoitus. Säilytä riittävä ajohistoria trendien tarkasteluun, mutta älä julkaise raakoja lokitietoja, käyttöoikeustietoja, salaisuuksia tai tarpeettomia teknisiä yksityiskohtia.

### 2.6 Lähderekisterin selaus

Myöhemmässä vaiheessa valvomoon voidaan lisätä lähderekisterin selain, jossa lähteitä voi suodattaa aiheen, kielen, alueen, lähdetyypin ja kriittisyyden perusteella. Näytä lähteen tunniste ja rekisteritiedot sekä viimeisimmän tarkistuksen tulos, jos se on saatavilla.

## 3. RSS-lukija

### 3.1 Perustoiminnot

RSS-lukijan vähimmäisversio on toteutettu sivulle `/lukija/` omana päävalikon osionaan. Lukija lukee syötekatalogin `data/feed-catalog.json`, hakee kaikki kymmenen RSS-syötettä GitHub Pagesista ja yhdistää niiden itemit yhdeksi uusimmat ensin näyttäväksi artikkelivirraksi.

Artikkelikortissa näytetään otsikko, julkaisupäivä, syötteen nimi, tekstimuotoinen ingressi ja koko puhdistettu artikkeli avattavassa lukutilassa. Lähdelinkit säilyvät artikkelin sisällössä, ja ensimmäinen turvallinen lähdelinkki nostetaan lisäksi näkyviin alkuperäisen lähteen linkkinä. Käyttäjä voi valita kaikki syötteet tai yhden katalogissa määritellyn syötteen. Tyhjät syötteet eivät ole virhe eikä niihin lisätä keinotekoisia artikkeleita.

Ulkoisia kuvia ei ladata MVP-versiossa: näin lukija ei tee artikkelien avaamisen yhteydessä huomaamattomia kolmannen osapuolen verkkopyyntöjä. Kuvien hallittu näyttäminen voidaan arvioida myöhemmässä kehityksessä erikseen.

### 3.2 Suodatus ja henkilökohtainen lukutila

Syötekohtainen suodatus kuuluu jo vähimmäisversioon. Myöhempiä ominaisuuksia ovat aikasuodattimet (esimerkiksi 24 tuntia, 7 päivää ja 30 päivää), otsikon ja artikkelisisällön tekstihaku, lukemattomien ja luettujen artikkeleiden erottelu, artikkelien tallentaminen myöhempää lukemista varten, lajittelun valinta ja käyttäjäkohtaiset asetukset.

Luku- ja tallennustila voidaan aluksi säilyttää selaimen paikallisessa tallennustilassa. Tämä ei synkronoidu laitteiden välillä eikä ole käyttäjätiliin sidottu. Palvelinpuolen käyttäjätunnistusta tai tietokantaa ei lisätä ilman erillistä tarvetta ja suunnitelmaa.

Aihevalikoima johdetaan aina ajantasaisesta syötekatalogista, ei kovakoodatusta luettelosta. Nykyinen yhdeksän aiheen kierto, erillinen intialaisen elokuvan uutisraportti ja näytösfeed on esitettävä käyttäjälle oikein nimettyinä ja toisistaan erillisinä.

### 3.3 Turvallisuus ja HTML-sisältö

RSS:n description voi sisältää HTML:ää. Ulkoista HTML:ää ei saa renderöidä suoraan luotettuna sivun DOM-sisältönä.

- Lukija jäsentää RSS:n XML:n passiivisesti ja rakentaa artikkelin HTML:n uudelleen sallittujen elementtien listasta. Alkuperäisiä elementtejä tai attribuutteja ei siirretä sivulle.
- Skriptit, tyylit, tapahtumankäsittelijät, vaaralliset URL-skeemat, lomakkeet, SVG/MathML, mediaelementit ja mielivaltaiset upotukset poistetaan.
- Linkeistä hyväksytään vain täydelliset HTTP- ja HTTPS-osoitteet ilman käyttäjätunnuksia tai salasanoja. Muut attribuutit hylätään; linkeille lisätään `rel="noopener noreferrer"`.
- Ulkoisia kuvia, tyylejä tai upotuksia ei ladata MVP-versiossa, mikä vähentää seurantaa ja kolmansien osapuolten verkkopyyntöjä.
- Säilytä lähteiden linkit, mutta älä anna lähdeartikkelin HTML:n muuttaa lukijan käyttöliittymää.
- Näytä puhdistettu artikkeli ja tarjoa turvallinen linkki alkuperäiseen julkaisuun.

Sisältösuojaus ja sanitointi testataan erillisillä haitallisen HTML:n testitapauksilla. RSS-syötteen rakenteellinen validointi ei yksin riitä osoittamaan lukijan turvallisuutta.

## 4. Kehitysjono: GitHub Issues -pohjainen kanban

### 4.1 Tietolähde ja vastuunjako

GitHub Issues on kehitystehtävien ensisijainen ja kanoninen tietolähde. Jokainen tehtävä on yksi GitHub-issue, jonka pysyvä tunniste on repositorion issue-numero (esimerkiksi `#42`). Valvomon kehitysjono-osio lukee avoimet ja suljetut tiketit GitHubin julkisesta rajapinnasta ja esittää ne kanban-tauluna.

- Tiketit luodaan, niitä muokataan ja ne suljetaan GitHubissa. Kanban-näkymä on aluksi vain luku -käyttöliittymä; selaimessa ei ole GitHub-kirjoitusoikeuksia eikä tunnisteita tai salaisuuksia.
- GitHub-issue on aina tiketin ensisijainen sisältö. Kanban ei ylläpidä erillistä kopiota tiketin otsikosta, kuvauksesta, tilasta tai prioriteetista.
- Tikettien kommentit ja muutoshistoria säilyvät GitHubissa.
- Jokaisella tikettiviittauksella käytetään muotoa `#numero` ja linkkiä kyseiseen issueen.
- Suljettu tiketti tarkoittaa valmista tai tietoisesti tekemättä jätettyä tehtävää; sulkemisen syy kirjataan tikettiin. Pelkkä sulkeminen ei saa peittää keskeneräistä toteutusta.

### 4.2 Kanban-tilat

Kullakin avoimella tiketillä on täsmälleen yksi tilatunniste:

| Tunniste | Kanban-sarake | Merkitys |
|---|---|---|
| `tila:backlog` | Backlog | Tunnistettu kehitystarve, jota ei ole vielä valmisteltu toteutukseen |
| `tila:ready` | Valmis työn alle | Rajaus ja hyväksymiskriteerit ovat riittävän selvät toteutuksen aloittamiseen |
| `tila:in-progress` | Työn alla | Työtä tehdään aktiivisesti |
| `tila:blocked` | Estynyt | Työ odottaa päätöstä, riippuvuutta tai muuta estettä |
| `tila:done` | Valmis | Hyväksymiskriteerit täyttyvät; tiketti suljetaan |

Tilan vaihtuessa vanha tilatunniste poistetaan ja uusi lisätään. Valmiiksi merkitty tiketti suljetaan. Jos suljettu tiketti avataan uudelleen, sille asetetaan tilanteeseen sopiva avoimen työn tilatunniste.

### 4.2.1 Tiketin tilan päivittäminen työn edetessä

Tiketin `tila:*`-labelin on kuvattava työn todellista vaihetta. Tiketin käsittelijä päivittää labelin aina, kun työ siirtyy vaiheesta toiseen:

1. **Työ aloitetaan:** vaihda tilaksi `tila:in-progress` heti, kun tiketti otetaan aktiiviseen toteutukseen. Poista samalla aiempi `tila:ready`- tai `tila:backlog`-label.
2. **Työ estyy:** jos toteutus ei voi jatkua ratkaisemattoman riippuvuuden, päätöksen tai muun esteen vuoksi, käytä `tila:blocked`-labelia ja kirjaa este tikettiin. Kun este poistuu, palauta tiketti tilanteen mukaan `tila:in-progress`- tai `tila:ready`-tilaan.
3. **Työ keskeytyy ilman estettä:** älä jätä tikettiä virheellisesti työn alle. Palauta se `tila:ready`-tilaan, jos toteutus on edelleen aloitusvalmis, tai `tila:backlog`-tilaan, jos määrittely tai päätökset ovat jälleen kesken. Kerro tarvittaessa keskeytyksen syy tiketin kommentissa.
4. **Työ valmistuu:** vaihda tilaksi `tila:done` vasta, kun hyväksymiskriteerit täyttyvät, muutokset on yhdistetty kohdehaaraan ja olennaiset tarkistukset on tehty. Sulje tiketti tämän jälkeen.

Tiketillä säilytetään aina täsmälleen yksi `tila:*`-label. Tilan vaihdossa vanha tilalabel poistetaan ja uusi lisätään samassa päivityksessä. Prioriteetti- ja aihelabelit säilytetään. Pelkkä toteutuksen valmistuminen työhaarassa tai PR:n avaaminen ei oikeuta `tila:done`-labeliin. Jos tiketti suljetaan tekemättä työtä, älä esitä sitä toteutettuna: sulkemisen syy ja tilalabelin oikeellisuus arvioidaan erikseen.

### 4.3 Prioriteetit

Jokaisella tiketillä on täsmälleen yksi prioriteettitunniste:

| Tunniste | Merkitys |
|---|---|
| `P0` | Kriittinen: estää järjestelmän keskeisen toiminnan tai aiheuttaa vakavan riskin |
| `P1` | Korkea: tärkeä lähiajan työ, jolla on selvä vaikutus luotettavuuteen tai käytettävyyteen |
| `P2` | Normaali: tarpeellinen kehitys, joka voidaan ajoittaa muiden töiden jälkeen |
| `P3` | Matala: hyödyllinen parannus tai myöhempi idea |

Prioriteetti kuvaa työn tärkeyttä, ei sen tilaa eikä automaattisesti toteutusjärjestystä. Prioriteettia voidaan muuttaa perustellusti.

### 4.4 Tiketin sisältö

Tiketin kuvauksessa käytetään yhteistä rakennetta:

- **Tavoite:** mitä halutaan saavuttaa ja miksi.
- **Tausta:** keskustelu, havainto, raportti tai dokumentti, josta tarve syntyi.
- **Rajaus:** mitä tähän tikettiin kuuluu ja mitä ei.
- **Hyväksymiskriteerit:** konkreettiset ehdot, joiden täyttyessä tiketti voidaan sulkea.
- **Riippuvuudet:** muut tiketit tai päätökset, jotka pitää tehdä ensin.
- **Huomiot:** tekniset, tietoturvaan, saavutettavuuteen tai ylläpitoon liittyvät reunaehdot.

Kaikkiin tiketteihin ei tarvitse täyttää jokaista kohtaa heti. Backlog-tiketti voi olla alustava, mutta se täydennetään ennen siirtämistä Valmis työn alle -tilaan. Epäselvää ideaa ei pidä naamioida valmiiksi määritellyksi toteutustehtäväksi.

### 4.5 Kanban-näkymän toiminta

- Näytä tilasarakkeet tässä dokumentissa määritellyssä järjestyksessä.
- Näytä kortissa vähintään issue-numero, otsikko ja prioriteetti; mahdolliset aihealueet voidaan esittää lisätunnisteina.
- Tarjoa linkki GitHub-issueen, jossa tikettiä voi lukea ja muokata.
- Mahdollista suodatus prioriteetin ja aihealueen mukaan sekä tekstihaku.
- Näytä myös suljetut tiketit Valmis-näkymässä tai erillisellä valinnalla.
- Näytä latausvirhe ja viimeisin onnistunut päivitysaika. Jos GitHubin rajapinta ei vastaa, älä esitä vanhaa näkymää tuoreena.
- Käytä GitHubin APIa vain julkisten issue-tietojen lukemiseen. Huomioi sivutus, API-rajoitukset ja välimuisti.
- Kanbanin saavutettavan vaihtoehdon tulee tarjota sama tieto myös tavallisena otsikoituna listana tai taulukkona; drag-and-drop ei saa olla ainoa tapa ymmärtää tai muuttaa tilaa.


### 4.5.1 Tikettien väliset riippuvuudet

Kehitysjono lukee riippuvuudet GitHubin omasta Issues-riippuvuusrajapinnasta (dependencies/blocked_by). GitHubin tietomallissa riippuvuus on suunnattu suhde: jos tiketti A on estetty tiketistä B, A:n blocked_by-listassa on B. Sama suhde esitetään B:n näkökulmasta blocking-suhteena A:han. Käyttöliittymä johtaa käänteisen näkymän tästä samasta lähdetiedosta; se ei ylläpidä rinnakkaista riippuvuusrekisteriä.

- **Edeltävä työ / estetty tästä:** tiketti, jonka valmistumista tarkasteltava työ odottaa (blocked_by).
- **Estää / mahdollistaa jatkotyön:** tiketit, joiden etenemistä tarkasteltava työ estää (blocking). Näiden töiden eteneminen voi jatkua, kun edeltävä työ valmistuu.
- Riippuvuudet haetaan käyttäjän pyynnöstä erikseen, jotta sivun tavallinen lataus ei tee yhtä API-kutsua jokaista tikettiä kohti.
- Kortissa ja taulukossa näytetään edeltävien ja estettyjen töiden lukumäärät sekä painike, jolla yksittäisen tiketin suhteet avataan. Yksityiskohtanäkymä näyttää linkit myös suodatuksen ulkopuolella oleviin tiketteihin.
- Yhdysviivoja ei käytetä, koska sarakkeiden välinen suuri tai suodattuva verkko olisi helposti sekava ja pienillä näytöillä vaikeasti seurattava. Suhteen suunta ilmaistaan tekstillä ja ryhmitellyillä listoilla.
- Jos osa API-kutsuista epäonnistuu tai GitHub rajoittaa pyyntöjä, käyttöliittymä kertoo tietojen olevan osittaisia. Puuttuvaa tietoa ei tulkita riippuvuuden puuttumiseksi.
- Näkymä on vain luku -muotoinen. Riippuvuuksien lisääminen, poistaminen tai muuttaminen tehdään GitHubissa; niiden näyttäminen ei muuta tikettien tiloja.
- Riippuvuustiedot tallennetaan vain selaimen välimuistiin käyttömukavuuden vuoksi. GitHub on ainoa kanoninen lähde.


### 4.6 Tunnisteiden hallinta ja eheys

GitHub-repositorioon luodaan tilaa ja prioriteettia kuvaavat tunnisteet ennen tikettien laajaa siirtoa. Jokaisella tiketillä on täsmälleen yksi `tila:*`-tunniste ja yksi `P*`-prioriteettitunniste. Muut tunnisteet kuvaavat aihealuetta tai tehtävätyyppiä, eivätkä korvaa näitä kahta pakollista luokitusta.

Validointi tai erillinen laadunvalvonta tarkistaa myöhemmin, ettei avoimelta tiketeiltä puutu tilaa tai prioriteettia eikä samalla tiketillä ole useita ristiriitaisia arvoja. Virheelliset luokitukset näytetään huomautuksena, eikä niitä korjata arvaamalla.

### 4.7 Vanhojen suunnitelmien siirtäminen

Aiemmissa keskusteluissa ja dokumenteissa sovitut tai ehdotetut keskeneräiset kehityskohteet kootaan GitHub Issues -backlogiin. Siirrossa:

1. Etsi vanhat suunnitelmat ja erottele hyväksytyt päätökset, ehdotukset, avoimet työt ja jo toteutetut asiat.
2. Yhdistä päällekkäiset ideat yhdeksi tiketiksi; älä luo samaa työtä moneen kertaan.
3. Säilytä alkuperäinen tausta ja päätöksen tila tiketin kuvauksessa.
4. Älä luo avoimia tikettejä jo toteutetuista ominaisuuksista. Tarvittaessa niistä voidaan tehdä suljettuja historiatietueita, jos se auttaa ymmärtämään päätöksiä.
5. Anna jokaiselle tikettiin siirretylle työlle GitHubin issue-numero ja viittaa jatkokeskusteluissa siihen.
6. Säilytä `docs/kehityskohteet.md` siirtymän ajan lähteenä; kun siirto on tarkistettu, muuta se lyhyeksi yhteenvedoksi ja ohjeeksi käyttää GitHub Issues -backlogia.

Ensimmäiseen backlogiin kuuluvat vähintään aiemmin tunnistetut Valvomon tietomalli ja ajotiedot, RSS-lukijan ominaisuudet ja turvallinen HTML-käsittely, lähderekisterin selain, raporttiarkiston tarpeen arviointi, lähdekattavuuden parantaminen, uutisten luotettavuusluokituksen täsmennys, linkkitarkistuksen tulosten seuranta sekä saavutettavuuden manuaalinen testaus. Nämä pilkotaan erillisiksi tiketeiksi vain, jos niillä on omat tavoitteet ja hyväksymiskriteerit.

## 5. Tietomalli ja datan tuottaminen

Valvomon tietomalli ja nykyisen GitHub Pages -julkaisun kartoitus on määritelty ensisijaisesti dokumentissa [Valvomon tietomalli ja julkaisutapa](valvomon-tietomalli.md).

Kanoniset tietolähteet ovat:

- `data/seurantatila.json`: pääautomaation aihekierros, aihekohtaiset viimeisimmät onnistumiset, erillinen näytösvahti sekä automaatio-ohjeiden versiot.
- `data/lahdetarkistukset.json`: lähdetarkistusten ajokohtaiset tulokset ja lähdekohtainen kattavuus.
- `data/naytosten-muutoshistoria.json`: näytösseurannan oma nykytila ja muutostapahtumat.
- GitHub Actionsin julkinen API: tämän repositorion testien, viikoittaisen linkkitarkistuksen ja Pages-julkaisun tilat.

Näiden tietolähteiden päälle ei rakenneta rinnakkaisia `status/overview.json`-, `runs.json`-, `sources.json`- tai `rotation.json`-kopioita. Valvomo muodostaa esitysnäkymän selaimessa alkuperäisistä tiedoista. Näin vältetään ylimääräinen tietokanta, turhat status-commitit ja eri tiedostojen väliset synkronointivirheet.

`data/seurantatila.json` validoidaan skeemalla `schemas/seurantatila.schema.json`. Lähdetarkistusloki ja näytöshistoria validoidaan omilla jo olemassa olevilla skeemoillaan. Rakennemuutokset tehdään versionhallittuina ja päivitetään tuottajiin, skeemoihin, validointiin ja dokumentaatioon samassa muutossarjassa.

Nykyinen Pages-julkaisu säilyy `main`-haaran juuresta GitHubin hallitsemalla Jekyll-buildillä. Erillistä julkaisun haaraa tai uutta Pages-deploy-workflow'ta ei lisätä vain Valvomon vuoksi. Automaatioiden seurantatiedot julkaistaan nykyisten hyväksyttyjen repositoriomuutosten mukana; selainkäyttöliittymä lukee vain julkisia tietoja eikä sisällä kirjoitusoikeuksia tai salaisuuksia.

Viimeisimmän onnistumisen puuttuminen näytetään tuntemattomana, aikataulun ylittänyt onnistuminen vanhentuneena. Viimeisintä onnistumista ei tulkita käynnissä olevaksi ajoksi. Nykyiset koneelliset tiedot eivät sisällä vaihekohtaista ajohistoriaa, joten vaihetiloja ei näytetä ennen kuin automaatiot tuottavat niistä erikseen varmennetun tiedon. Tuoreusrajat ja GitHub API:n välimuistiperiaatteet on määritelty Valvomon tietomallidokumentissa.

## 6. Käyttöliittymä, saavutettavuus ja tietosuoja

Sivusto noudattaa repositorion saavutettavuusohjeen WCAG 2.2 AAA -tavoitetta soveltuvin osin. AAA-vaatimusten täyttymistä ei väitetä ilman asianmukaista testausta.

Valvomossa tilat esitetään tekstinä, ei pelkillä väreillä tai kuvakkeilla; dynaamiset tilapäivitykset ilmoitetaan ruudunlukijalle hallitusti; taulukot ja vaihelistat ovat semanttisia; kaavioille tarjotaan tekstimuotoinen vastine ja taulukkomuotoinen data; käyttö onnistuu näppäimistöllä ja fokus näkyy; käyttöliittymä toimii kapealla näytöllä ja suurennettuna.

RSS-lukijassa otsikkohierarkia on looginen, linkkitekstit kuvaavia, lukutila säilyttää artikkelin rakenteen ja kuville tarjotaan vaihtoehtotekstit. Luettu/luettava-tila ei erotu vain värillä.

Tietosuoja:
- Älä julkaise käyttäjätunnuksia, sähköpostiosoitteita, salaisuuksia, käyttöoikeustokeneita tai tarpeettomia henkilötietoja.
- Älä sisällytä julkiseen tilaan raakoja virhevastauksia, jotka voivat paljastaa salaisuuksia tai ympäristötietoja.
- Vältä ulkoisia seurantapikseleitä ja tarpeettomia kolmannen osapuolen pyyntöjä.
- Kerro selkeästi, jos lukutilan paikallinen tallennus käyttää selaimen tallennustilaa.

## 7. Testaus- ja hyväksymiskriteerit

### 6.1 Valvomon testit

- JSON-tiedostot validoituvat omia skeemojaan vasten.
- Ajot ja automaatiot pysyvät toisistaan erillisinä.
- Vaiheen failed, warning ja skipped -tilat näkyvät oikein.
- Epäonnistunut tai kesken jäänyt ajo ei siirrä aihekierrosta eikä viimeisintä onnistunutta tarkistusta.
- Lähteiden yritykset, onnistuneet tarkistukset ja tarkistamatta jääneet lähteet eivät sekoitu.
- Vanhentunut tai puuttuva data näkyy tuntemattomana/vanhentuneena.
- Julkiseen JSONiin ei päädy salaisuuksia tai raakaa lokisisältöä.
- Ajolinkit osoittavat oikeaan GitHub Actions -ajoon.

### 6.2 RSS-lukijan testit

- Syötekatalogin jokainen URL vastaa todellista Pages-RSS-osoitetta.
- Kaikkien syötteiden itemit voidaan jäsentää ja lajitella aikajärjestykseen.
- Tyhjät syötteet ja virheelliset yksittäiset itemit käsitellään hallitusti.
- Aihe- ja aikasuodattimet sekä haku toimivat.
- Luettu- ja tallennustila säilyvät selaimen uudelleenlatauksessa, jos paikallinen tallennus on käytössä.
- HTML-sanitointi estää skriptit, vaaralliset attribuutit ja kielletyt upotukset.
- YouTube-upotukset hyväksytään vain määritellyllä turvallisella tavalla.
- Ulkoisen sisällön virhe ei kaada koko lukijaa.

### 6.3 Julkaisun ja viittausten eheystestit

Jokaisessa muutoksessa tarkistetaan myös muutoksen vaikutus koko repositorion viittauksiin:

1. Uusien tiedostojen ja URL-osoitteiden kaikki viittaukset ovat oikein.
2. Muuttuneita tai poistettuja polkuja ei käytetä enää vanhoissa ohjeissa, skripteissä, testeissä tai asetuksissa.
3. README, Pages-julkaisun asetukset, työnkulut, syötekatalogi ja testit osoittavat samoihin tiedostoihin.
4. Testit tarkistavat koneellisesti keskeiset viittaukset ja skeemat.
5. Muutetut tiedostot luetaan takaisin GitHubista ja niiden sisältö tarkistetaan.
6. Pages-julkaisun jälkeen tarkistetaan, että sivusto ja julkiset JSON-/RSS-osoitteet todella toimivat.

Tarkista muutoksen jälkeen myös nykyisen Pages-julkaisun rakenne ja työnkulut; älä oleta, että ehdotetut hakemistot tai julkaisumekanismit ovat jo käytössä.

## 8. Kehitysvaiheet ja etenemisen seuranta

Toteutus tehdään vaiheittain. Jokainen vaihe saa oman testattavan muutoksensa ja hyväksymiskriteerinsä. Vaiheiden järjestys on toteutuksen suunnittelujärjestys; GitHub Issues -tikettien prioriteetit ja riippuvuudet ohjaavat käytännön etenemistä.

### Vaihe 0 – nykytilan kartoitus, tikettien perustaminen ja tietomallin hyväksyntä

- [x] Kartoita nykyinen GitHub Pages -julkaisu, Jekyll-build ja repositorion työnkulut; Pages-asetuksen tarkka kansiovalinta on merkitty erikseen UI-varmistettavaksi.
- [x] Luo GitHubiin kanban-tilojen ja prioriteettien tunnisteet.
- [x] Siirrä aiemmissa keskusteluissa ja kehitysdokumenteissa olevat avoimet suunnitelmat GitHub Issues -backlogiin ja tarkista, ettei päällekkäisiä tikettejä synny.
- [ ] Tarkista nykyiset RSS-syötteet, niiden URLit, kaikki automaatiotyönkulut ja koneelliset seurantatiedostot.
- [x] Päätä sivuston teknologia ja kansiorakenne nykyisen toteutuksen perusteella: GitHub Pagesin nykyinen Jekyll-julkaisu ja staattinen sivustorunko.
- [x] Määrittele ja dokumentoi nykyisten kanonisten seurantatiedostojen tietomalli ja JSON Schema -validointi; vältä rinnakkaisia status- ja syötekatalogikopioita.
- [x] Määrittele automaatioiden nykyiset tiedonkeruuvastuut ja julkaisutapa; vaihekohtaisen ajotiedon keruu jää Valvomon toteutusvaiheeseen.
- [x] Valitse nykyisten JSON-tiedostojen lukeminen Pagesistä ja rajattu GitHub Actions API -luku workflow-tiloille; erillistä status-haaraa tai Pages-artifactia ei lisätä.
- [x] Määrittele vanhentuneen ja puuttuvan tiedon esitystapa sekä julkisten kenttien rajaus. Ajohistorian säilytyksen laajennus ratkaistaan vasta, jos tietolähteisiin lisätään uutta historiatietoa.

**Hyväksymiskriteeri:** backlog sisältää tunnisteelliset, taustoitettuja ja priorisoituja avoimia kehitystehtäviä; tietomalli ja julkaisupolku on kuvattu niin tarkasti, että toteutuksen voi tehdä ilman arvailua. Nykyiset automaatiot ja RSS-julkaisu eivät muutu tässä vaiheessa.

### Vaihe 1 – Valvomon vähimmäisversio (tiketti #30)

- [ ] Luo sivuston yhteinen runko, navigaatio ja saavutettava ulkoasu.
- [ ] Julkaise koneellisesti luettava yhteenveto automaatioiden viimeisimmästä tilasta.
- [ ] Näytä pääautomaation aihekierros, viimeisin onnistuminen ja seuraava tehtävä.
- [ ] Näytä näytösvahti ja laatutarkistus erillisinä automaatioina.
- [ ] Näytä saatavilla olevat ajovaiheet, varoitukset, virheet ja Actions-linkit; älä päättele puuttuvia vaiheita.
- [ ] Näytä tiedon viimeisin päivitysaika ja vanhentuneen tiedon tila.
- [ ] Lisää JSON-skeemojen, käyttöliittymän ja virhetilojen testit.

**Toteutustilanne:** [PR #30 – Valvomon vähimmäisversio](https://github.com/mikknikk/aiheseurain/pull/30) on yhdistetty. Valvomon erottaminen juurietusivusta omalle `/valvomo/`-sivulleen toteutetaan tiketin #38 PR:ssä. Nykyiset automaatiot eivät vielä tallenna vaihekohtaista ajohistoriaa, joten ensimmäinen versio näyttää tämän rajoitteen suoraan.

**Hyväksymiskriteeri:** Valvomo näyttää todellisen, validoituun dataan perustuvan tilan; epäonnistumista ei esitetä onnistumisena eikä automaatioiden tietoja sekoiteta.

### Vaihe 2 – RSS-lukijan vähimmäisversio (tiketti #31)

- [ ] Luo syötekatalogi nykyisistä kymmenestä RSS-syötteestä.
- [ ] Näytä kaikkien syötteiden artikkelit yhteisessä aikajärjestyksessä.
- [ ] Lisää syötekohtainen suodatus ja artikkelin alkuperäislinkki.
- [ ] Lisää koko artikkelin lukutila turvallisesti puhdistetulla HTML:llä.
- [ ] Lisää RSS-jäsennyksen ja sanitoinnin testit.

**Hyväksymiskriteeri:** kaikki nykyiset syötteet näkyvät oikein, artikkelit eivät sekoitu aiheesta toiseen ja ulkoinen HTML ei voi suorittaa koodia lukijan sivulla.

### Vaihe 3 – Kehitysjonon kanban-näkymän vähimmäisversio (tiketti #35)

- [x] Näytä GitHub Issues -tiketit sovituissa tilasarakkeissa ja prioriteeteittain.
- [x] Lisää otsikko-/numerohaku, aihealue- ja prioriteettisuodatus sekä linkit alkuperäisiin tiketteihin.
- [x] Näytä viimeisin onnistunut päivitysaika, API-virheet ja välimuistissa olevan tiedon ikä.
- [x] Tarjoa kanbanin rinnalla saavutettava taulukkonäkymä.
- [x] Rajaa selainkäyttöliittymä vain luku -toiminnoksi; GitHubiin ei lähetetä kirjoituspyyntöjä eikä sivulle lisätä tunnuksia tai tokeneita.

**Toteutustilanne:** vähimmäisversio on toteutettu PR:ssä. Näkymä hakee avoimet ja suljetut issuet GitHubin julkisesta APIsta, jättää pull requestit pois, näyttää suljetut tehtävät Valmis-sarakkeessa ja käsittelee puuttuvat tai ristiriitaiset tilat erillisenä huomautuksena. Aihealue suodatetaan aihe-alkuisilla GitHub-labeleilla. Selaimen paikallinen välimuisti auttaa API-katkoissa; yli tunnin ikäinen tieto merkitään vanhentuneeksi eikä sitä esitetä tuoreena.

**Hyväksymiskriteeri:** näkymä esittää GitHubin issue-tiedot oikein ja ajantasaisuuden rajat näkyvästi; muokkaus tapahtuu GitHubissa.

### Vaihe 4 – lukijan käyttömukavuus ja lähdenäkymä

- [ ] Lisää aikasuodattimet ja otsikko-/sisältöhaku.
- [ ] Lisää selaimeen tallentuva luettu/luettava-tila.
- [ ] Lisää artikkelien tallentaminen myöhempää lukemista varten.
- [ ] Lisää lähderekisterin selaus ja lähdekattavuuden yhteenveto.
- [ ] Lisää kattavuuden tekstimuotoiset selitteet ja tarvittaessa kaaviot.

**Hyväksymiskriteeri:** lukija toimii käytännöllisesti myös suurella artikkelimäärällä ja lähdekattavuuden esitystapa ei liioittele tietojen kattavuutta.

### Vaihe 5 – raporttiarkisto ja jatkokehitys

- [ ] Arvioi erillisen raporttiarkiston hyöty ja päällekkäisyys RSS-lukijan kanssa.
- [ ] Toteuta arkisto vain, jos sille on selkeä käyttötapaus.
- [ ] Lisää mahdolliset pitkän aikavälin trendit, historiakaaviot ja laajennetut lähdenäkymät vasta todellisen datan perusteella.

**Hyväksymiskriteeri:** lisäominaisuudet perustuvat todelliseen käyttötarpeeseen eivätkä lisää tarpeetonta ylläpitokuormaa.

## 9. Rajaukset ja päätökset, joita ei tehdä vielä

- Ei käyttäjätilejä, kirjautumista tai palvelinpuolen henkilökohtaista tietokantaa ensimmäisessä versiossa.
- Ei selaimesta tehtäviä GitHub-kirjoituksia eikä GitHub-salaisuuksien siirtämistä Pages-sivulle.
- Ei raakaa Actions-lokia julkiseksi.
- Ei lähdekattavuuden prosenttilukua ilman määriteltyä nimittäjää ja luotettavaa havaintodataa.
- Ei uusia erillisiä uutisautomaatioita vain käyttöliittymän vuoksi.
- Ei näytösseurannan siirtämistä pääautomaation aihekierrokseen.
- Ei RSS-artikkelien kopiointia toiseen tietolähteeseen, jos RSS jo toimii arkistona riittävän hyvin.
- Ei WCAG 2.2 AAA -vaatimustenmukaisuuden väitettä ennen dokumentoitua testausta.
- Ei erillistä tiketöintitietokantaa tai selainpuolen GitHub-kirjoitusoikeuksia; GitHub Issues on kehitystehtävien ensisijainen tietolähde.

## 10. Muutosloki

- **2026-11-17:** Tikettien riippuvuuksien näyttö lisätään GitHubin omien blocked_by-suhteiden pohjalta; käyttöliittymä näyttää kortti- ja taulukkoyhteenvedot sekä valitun tiketin yksityiskohtaiset riippuvuudet.
- **2026-11-16:** Kehitysjonon kanbanin vähimmäisversio toteutettiin omalle `/kehitysjono/`-sivulleen. GitHub Issues säilyy ainoana tehtävätietojen lähteenä; Pages-näkymä on vain luku -muotoinen ja tarjoaa kanbanin rinnalla taulukkonäkymän.
- **2026-11-16:** Valvomo erotettiin juurietusivusta omalle `/valvomo/`-sivulleen. Etusivu varattiin Aiheseuraimen palveluvalikolle; yhteinen Jekyll-sivupohja ja nykyinen Pages-julkaisutapa säilyvät.

- **2026-11-16:** ensimmäinen tavoitekuvaus ja vaiheistettu kehityssuunnitelma kirjattu Valvomolle ja RSS-lukijalle.
- **2026-11-16:** kehitysjono lisätty kolmanneksi osioksi. GitHub Issues määritelty tikettien ensisijaiseksi tietolähteeksi; yksittäisten tikettien siirto backlogiin on seuraava työvaihe.
- **2026-11-16:** nykyinen Pages-julkaisutapa ja Valvomon tietomalli kartoitettu. Kanoniset seurantatiedostot säilyvät tietolähteinä; erillisiä päällekkäisiä status-JSONeja ei luoda.
- **2026-11-16:** Valvomon vähimmäisversio (#30) yhdistetty. Kehitysvaiheiden järjestys päivitetty vastaamaan Valvomon, RSS-lukijan ja kehitysjonon tikettien prioriteetteja.
