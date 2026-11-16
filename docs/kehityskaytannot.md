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

### Automaation käynnistyskehotteet

Automaation asetuksiin kopioitavat käynnistyskehotteet ovat erillisiä tekstipohjia, eivät tehtäväkäsikirjoja. Niiden kanoniset versiot säilytetään repositorion `prompts/`-hakemistossa `.txt`-tiedostoina.

- Säilytä käynnistyskehotteet täsmälleen sellaisina teksteinä, jotka automaation asetuksiin kopioidaan. Älä lisää Markdown-otsikoita, selityksiä tai muuta sisältöä varsinaisen kehotteen sisään.
- Käytä `prompts/README.md`-tiedostoa hakemiston selityksiin, automaatioiden ja tiedostojen yhdistämiseen sekä päivitysmenettelyyn.
- Kun käynnistyskehotetta muutetaan, päivitä ensin repositorion kanoninen teksti ja kopioi sama sisältö automaation asetuksiin. Tarkista lopuksi, että asetuksiin tallennettu teksti vastaa tiedostoa.
- Käynnistyskehote käynnistää tehtävän ja ohjaa ensisijaiseen käsikirjaan. Varsinaiset tehtävärajaukset ja toimintatavat kuuluvat käsikirjaan.

Vanhoja dokumentteja ei muotoilla automaattisesti tämän käytäntömuutoksen yhteydessä. Niitä uudistetaan asteittain, jotta ohjeiden merkitys tai koneellisesti tulkittavat osat eivät muutu vahingossa.

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
