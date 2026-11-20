# Kehityskäytännöt

Tämä dokumentti määrittää repositorion dokumentaation, skriptien ja muun ylläpitokoodin kirjoittamisen vähimmäiskäytännöt.

## Dokumentaation luokat ja kirjoitustavat

Dokumentin rakenne valitaan ensisijaisesti sen käyttötarkoituksen mukaan. Kaikkia tiedostoja ei pidä muotoilla samalla tavalla.

### Ihmiselle tarkoitetut dokumentit

Esimerkiksi README, kehityssuunnitelmat, tehtävälistat ja käyttöä selittävät ohjeet.

- Käytä kuvaavaa pääotsikkoa (`#`) ja loogista alaotsikkohierarkiaa.
- Jaa sisältö aihekokonaisuuksiin; suosi lyhyitä kappaleita ja käytä luetteloita vaiheisiin tai rinnakkaisiin asioihin.
- Käytä taulukkoa vain, kun tieto on aidosti vertailtavaa tai muuten taulukkomuotoista.
- Lisää pitkään dokumenttiin sisällysluettelo tai muu navigointitapa, jos se helpottaa olennaisesti löytämistä.

### Automaation toimintakäsikirjat

Esimerkiksi `docs/paaautomaation-ohje.md`, `docs/intialaisten-elokuvien-naytosseuranta.md` ja `docs/laatutarkistuksen-ohje.md`.

- Rakenna ohje loogisiin, nimettyihin osiin ja esitä ehdot, järjestykset, rajaukset ja keskeytysehdot yksiselitteisesti.
- Käytä otsikoita, numeroituja vaiheita ja luetteloita niin, että ohjeen koneellinen ja ihmisen tekemä tulkinta pysyy samana.
- Älä lisää koristeellista muotoilua tai muotoilua, joka voi muuttaa käskyjen, polkujen, tunnisteiden tai ehtojen merkitystä.
- Pidä yksi ensisijainen ohje kutakin automaatiota kohden; viittaa siihen muista tiedostoista sen sijaan, että kopioisit ohjeita.

### Seuranta- ja tekniset dokumentit

Esimerkiksi tapahtumalokit, tietomallien kuvaukset ja lähderekisterien dokumentaatio.

- Valitse esitysmuoto tiedon rakenteen mukaan. Taulukot sopivat vertailuihin ja kenttäkuvauksiin, mutta tapahtumaloki voi olla selkeämpi aikajärjestyksessä.
- Älä kopioi Markdowniin tietoa, jonka koneellisesti ylläpidettävä ensisijainen lähde on JSON- tai skeematiedosto.
- Kerro, mikä on tiedon ensisijainen lähde ja miten sitä ylläpidetään.

### Ajastettujen automaatioiden käynnistyskehotteet

ChatGPT:n ajastettujen tehtävien käynnistyskehotteet ovat erillisiä, tarkasti kopioitavia tekstipohjia. Niiden kanoniset, versioidut tekstit säilytetään repositorion `prompts/`-hakemistossa. Käytännöt ja tiedostorakenne on määritelty dokumentissa [käynnistyskehotteiden versionhallinta](../prompts/README.md).

- Jokaisella ajastetulla tehtävällä on pysyvä `task_id`; jokaisella sen käynnistyskehotteen versiolla on semanttinen versionumero.
- Tallenna jokainen versio omaan muuttumattomaan tiedostoonsa: `prompts/<task_id>/v<version>.txt`. Älä ylikirjoita vanhaa versiota.
- Kehotetiedoston sisältö on täsmälleen ChatGPT:n tehtäväasetuksiin kopioitava teksti. Älä lisää tiedostoon otsikoita tai selityksiä.
- Ylläpidä `prompts/registry.json`-tiedostossa uusinta GitHub-versiota ja erikseen ChatGPT:ssä käyttöön vahvistettua versiota. Älä merkitse uutta versiota käyttöön otetuksi ennen kuin asetusten teksti on täsmäytetty.
- Kehotteen päivitys GitHubissa ei päivitä ChatGPT:n tehtäväasetuksia. Niiden muuttaminen edellyttää käyttäjän nimenomaista lupaa; suojausperiaatteet ovat dokumentissa [automaatioiden hallinnan suojausperiaatteet](automaation-hallintaperiaatteet.md).
- Ajon alussa tarkistetaan tehtävätunniste ja kehotteen versio. Puuttuva tai ristiriitainen versiotieto estää varsinaisen seuranta-ajon.
- Kehote ohjaa ensisijaiseen käsikirjaan. Varsinaiset tehtävärajaukset ja toimintatavat kuuluvat käsikirjaan, eivät käynnistyskehotteen kopioon.
- Palautus vanhaan versioon tehdään hallittuna uutena käyttöönottona; vanhaa tiedostoa ei muuteta eikä historiaa poisteta.

Vanhoja dokumentteja ei muotoilla automaattisesti tämän käytäntömuutoksen yhteydessä. Niitä uudistetaan asteittain, jotta ohjeiden merkitys tai koneellisesti tulkittavat osat eivät muutu vahingossa.

## GitHub Issues -kehitystehtävien labelit

Aiheseuraimen kehitystehtävät tallennetaan GitHub Issues -tehtävinä. GitHub Project **Aiheseurain** näyttää kehitystehtävät. Issue-labelit ovat tehtävien tilan, prioriteetin ja komponentin ensisijainen tietolähde; Status-, Priority- ja Component-kentät synkronoidaan Projectiin automaattisesti ID-tunnisteiden perusteella. Käytä uusissa tehtävissä ja tehtäviä päivitettäessä seuraavaa kolmen luokan mallia.

Jokaisella kehitystehtävällä tulee olla yksi label kustakin luokasta:

| Luokka | Labelit | Merkitys |
|---|---|---|
| Komponentti | `component:automaatio`, `component:etusivu`, `component:lukija`, `component:valvomo`, `component:kehitysymparisto` | Mihin Aiheseuraimen komponenttiin tehtävä kuuluu |
| Prioriteetti | `priority:P0`, `priority:P1`, `priority:P2`, `priority:P3` | Tehtävän prioriteetti |
| Tila | `status:backlog`, `status:ready-for-development`, `status:in-progress`, `status:done` | Tehtävän etenemisen tila |

Säännöt:

- Käytä täsmälleen yllä olevia labelien nimiä. Etuliitteet ovat osa labelia.
- Valitse yksi komponenttilabel, yksi prioriteettilabel ja yksi tilalabel. Älä lisää samasta luokasta useita keskenään ristiriitaisia labeleita.
- Päivitä tilalabelia tehtävän edetessä. Älä käytä vanhoja tilalabeleita kuten `tila:backlog`, `tila:ready`, `tila:in-progress` tai `tila:done`.
- Älä käytä vanhaa `aihe:`-labelperhettä komponentin merkitsemiseen äläkä irrallisia `P0`–`P3`-labeleita prioriteetin merkitsemiseen.
- Uusi komponenttilabel lisätään tähän luetteloon ja Project-synkronoinnin käytäntöihin koordinoidusti. Yleinen `component:`-etuliite mahdollistaa komponenttien tunnistamisen.
- GitHub Projectin Status-, Priority- ja Component-kentät johdetaan issue-labeleista niiden kenttä- ja vaihtoehto-ID-tunnisteiden avulla. Näkyvien nimien muuttaminen ei edellytä koodimuutosta; kentän tai vaihtoehdon uudelleenluonti edellyttää ID-määrityksen päivittämistä. Suljetun issuen tilalabeli tulee silti päivittää asianmukaisesti muotoon `status:done`.

Tätä label-mallia noudatetaan kaikessa uudessa kehitystyössä, tehtävien luonnissa ja olemassa olevien tehtävien päivityksissä. Vanhoja labeleita ei pidä käyttää uusissa tehtävissä.

## Python-skriptien kommentointi

Jokainen uusi skripti kirjoitetaan alusta lähtien yhtä huolellisesti kommentoiduksi kuin `scripts/validate_feeds.py`.

- Kirjoita kommentit ja docstring-kuvaukset suomeksi.
- Aloita tiedosto docstringillä, joka kertoo ymmärrettävästi skriptin tarkoituksen, tärkeimmät tehtävät ja mahdolliset vaikutukset tiedostoihin tai muihin järjestelmiin.
- Lisää moduulin tärkeisiin osiin, funktioihin ja luokkiin docstring tai selittävä kommentti. Kerro, mitä osa tekee, miksi se on olemassa ja mitä tietoja se käsittelee.
- Selitä erityisesti aloittelijalle vaikeat kohdat, kuten tietorakenteet, tiedostopolut, XML/HTML-käsittely, aikavyöhykkeet, virhetilanteet, ulkoisten rajapintojen käyttö ja tietojen validointi.
- Kommentoi myös toimintalogiikan kannalta olennaiset vaiheet ja päätökset. Älä kuitenkaan lisää kommenttia jokaiselle itsestään selvälle riville.
- Käytä kuvaavia muuttuja-, funktio- ja luokkanimiä. Kommenttien tehtävä on täydentää koodia, ei korvata selkeitä nimiä.
- Pidä kommentit ajan tasalla aina, kun koodin toimintaa muutetaan. Virheellinen tai vanhentunut kommentti on korjattava samalla kertaa.
- Suosi pieniä, ymmärrettäviä funktioita ja selkeää rakennetta. Jos ratkaisu on monimutkainen, selitä sen toimintaperiaate ennen vaikeaa koodiosuutta.
- Säilytä olemassa olevan koodin toiminta, ellei käyttäjä nimenomaisesti pyydä toiminnallista muutosta.

## Tarkistus ennen muutoksen valmistumista

Kun uusi skripti lisätään tai olemassa olevaa muutetaan:

1. Lue skripti kokonaan läpi myös sellaisen ihmisen näkökulmasta, joka osaa Pythonin perusteet mutta ei tunne projektia.
2. Varmista, että tiedoston tarkoitus, tärkeät funktiot, keskeiset vaiheet ja ei-ilmeiset ratkaisut on selitetty suomeksi.
3. Tarkista, että kommentit vastaavat täsmälleen toteutunutta toimintaa.
4. Aja soveltuvat testit ja korjaa havaitut virheet.
5. Päivitä tarvittaessa README ja muu dokumentaatio vastaamaan uutta tai muuttunutta skriptiä.

Tavoitteena on, että myös Pythonia vähemmän osaava ylläpitäjä pystyy seuraamaan skriptin toimintaa, ymmärtämään sen keskeiset ratkaisut ja tekemään siihen turvallisia muutoksia.

## HTML-sivujen muutosten tarkistus

Jokaisen HTML-sivun muokkauksen jälkeen tarkista päivitetty sivu kokonaisuutena ennen muutoksen valmistumista. Pelkkä lähdekoodin lukeminen tai onnistunut Pages-rakennus ei riitä sivun käytettävyyden varmistamiseen.

Tarkistuksen tulee kattaa vähintään:

1. Sisältöjen ymmärrettävyys ja vastaavuus dokumentaatioon.
2. HTML-rakenne, otsikkotasot, maamerkit ja kielimääritys.
3. Sisäisten linkkien, navigaation ja RSS-linkkien oikeellisuus.
4. Responsiivinen asettelu sekä 320 CSS-pikselin näkymä.
5. Näppäimistökäyttö, näkyvä fokus, linkkien nimet ja muu olennainen saavutettavuus.
6. Tekninen toiminta: selainkonsolin uudet virheet, resurssien latautuminen ja käyttöliittymän toiminta.

Tee tarkistus julkaistusta tai muuten selaimessa renderöidystä sivusta aina, kun käytettävissä on sopiva selainympäristö. Jos renderöityä näkymää tai selainkonsolia ei voida tarkistaa, kirjaa selvästi, mitkä tarkistukset tehtiin lähdekoodista ja automaattisilla testeillä ja mitkä jäivät tekemättä. Älä väitä sivun ulkoasua tai selaintoimintaa varmennetuksi ilman renderöidyn sivun tarkistusta.

Jos jokin manuaalinen saavutettavuustesti, kuten näppäimistö- tai ruudunlukijatestaus, ei ole toteuttajan käytettävissä olevilla välineillä mahdollinen, se merkitään tekemättömäksi ja siirretään erilliseen backlog-tikettiin. Tällainen testausrajoite ei yksin estä muutoksen tai tiketin hyväksyntää, kun muut soveltuvat tarkistukset on tehty, niiden tulokset on dokumentoitu eikä tiedossa ole korjaamatonta vakavaa saavutettavuusongelmaa. Testaamatonta kohtaa ei saa merkitä läpäistyksi, eikä backlog-merkintä ole näyttö vaatimuksen täyttymisestä. Noudata tarkempaa menettelyä dokumentissa [saavutettavuusperiaatteet](saavutettavuus.md).
