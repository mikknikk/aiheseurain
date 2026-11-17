# Nykyisten moduulien siirron toteutus

**Versio:** 1.0.0  
**Päiväys:** 2026-11-18  
**Liittyvä tiketti:** [#105 – Siirrä nykyiset aiheet ja näytösvahti itsenäisiin moduulimäärittelyihin](https://github.com/mikknikk/aiheseurain/issues/105)  
**Lähtöinventaario:** [Nykyisten moduulien inventaario ja siirtymäsuunnitelma](moduulisiirtyman-inventaario.md)

## 1. Siirron tulos

Nykyisistä seurannoista on muodostettu kymmenen itsenäistä moduulimääritystä: yhdeksän topic-tyyppistä uutisaihetta ja yksi process-tyyppinen näytösvahti. Jokaisella määrityksellä on oma pysyvä tunniste, versio, hakuprofiilit, lähdeviitteet ja omat toimitukselliset säännöt.

Kaikki kymmenen moduulia on lisätty tiedostoon data/module-registry.json tilassa inactive. Rekisterissä ei ole yhtään active-moduulia. Tämä on tarkoituksellinen rinnakkaismigraatio: moduulien olemassaolo ja validointi eivät vielä siirrä nykyisiä automaatioita niiden käyttöön.

## 2. Moduulihakemiston rakenne

| Moduuli | Tyyppi | Määritystiedosto | Lähdeviitteitä |
|---|---|---|---:|
| tolkien | topic | modules/topics/tolkien/module.json | 28 |
| taylor-swift | topic | modules/topics/taylor-swift/module.json | 10 |
| gurmeet-ram-rahim-singh | topic | modules/topics/gurmeet-ram-rahim-singh/module.json | 7 |
| muumit | topic | modules/topics/muumit/module.json | 8 |
| wakaliwood | topic | modules/topics/wakaliwood/module.json | 5 |
| euroviisut | topic | modules/topics/euroviisut/module.json | 10 |
| sompote-sands | topic | modules/topics/sompote-sands/module.json | 6 |
| shakkidraamat | topic | modules/topics/shakkidraamat/module.json | 7 |
| indian-film-news | topic | modules/topics/indian-film-news/module.json | 40 |
| indian-film-screening-watch | process | modules/processes/indian-film-screening-watch/module.json | 11 |

Näytösvahtimoduulin tapahtumatyypin määritys sijaitsee erikseen tiedostossa modules/processes/indian-film-screening-watch/event-type.json. Se käyttää #109:n yleistä film-screening-tapahtumatyyppiä. Prosessilaajennuksen versio on 1.1.0, ja sen tapahtumatyyppiviite sekä identiteettikentät tarkistetaan migraatiovalidoinnissa.

## 3. Tietojen omistajuus

- Moduulin määritys omistaa seurannan kohteen, kuvauksen, rajauksen, sisällytys- ja poissulkusäännöt, seurattavat entiteetit nimivariantteineen, hakuprofiilit, kielet, alueet, lähdeviitteiden roolit sekä aihekohtaiset toimitukselliset erityissäännöt.
- data/source-catalog.json omistaa lähteiden yhteiset perustiedot, URL-osoitteet, kielet, alueet ja A–D-luotettavuusluokat. Näitä tietoja ei kopioida moduuleihin.
- data/sources/{task_id}.json säilyy tehtäväkohtaisen lähdekäytön kanonisena rekisterinä. Moduulin source_refs on validoitu peilaus sen source_id-tunnisteista, rooleista ja critical-tiedon mukaisesta required-arvosta.
- Yleiset toimitukselliset periaatteet, väitteiden varmennus, saavutettavuus, julkaisulaadun portti ja RSS-rakenteet pysyvät yhteisinä.
- Ajastukset, aikavyöhykkeet, ChatGPT-tehtävien tunnisteet, käynnistyskehotteet, kohdekeskustelut, palveluntarjoajat, mallit, tunnukset ja salaisuudet eivät kuulu moduuleihin.

Moduulin source_refs.role kuvaa lähteen tehtävää moduulissa (primary, secondary, discovery tai verification). Se ei korvaa lähdekatalogin reliability_class-arvoa eikä yksin todista lähteen luotettavuutta.

## 4. Hakuprofiilien kattavuus

Jokaisen moduulin ensimmäinen hakuprofiili sisältää tehtäväkohtaisen lähderekisterin lähteistä johdetut kielet ja alueet. Erilliset Suomen profiilit on lisätty niihin aiheisiin, joiden lähderekisterissä on FI-alueen lähteitä ja joiden sisältörajaukset edellyttävät Suomen tapahtumien tai uutisten tarkistamista.

Intialaisen elokuvan uutismoduuli sisältää lähderekisterin kattamat kielet as, bn, en, fi, hi, kn, ml, mr, or, pa, ta ja te. Hakutermeissä on lisäksi näiden kielialueiden paikallisia kirjoitusasuja sekä romanisoituja hakumuotoja. Euroviisujen hakuprofiili sisältää eurooppalaisten kielten lisäksi Eurovision Song Contest Asian keskeisiä Aasian kieliä. Profiilien kieli- ja aluetunnisteet tarkistetaan automaattisesti lähdekatalogin ja tehtäväkohtaisten lähderekisterien perusteella.

Kattavuusyhteenveto kuvaa rekisteriin tallennettuja lähteitä, ei kaikkien kielten tai alueiden uutisvirtojen täydellisyyttä. Lähteiden lisääminen, poistaminen tai niiden luotettavuusluokan muuttaminen vaatii edelleen lähderekisterien normaalin ylläpitomenettelyn.

## 5. Näytösvahti prosessimoduulina

Näytösvahti ei ole uutisaihe eikä kuulu yhdeksän tehtävän kiertoon. Sen moduulimääritys viittaa tapahtumatyypin erilliseen määritykseen, joka määrittelee näytöksen identiteetin, pakolliset attribuutit, seurattavat muutokset ja tilat.

Tapahtumatyypin identiteettikentät ovat title, venue ja starts_at. Näytöskohtainen pysyvä tunniste säilyy yleisen tapahtumaytimen canonical_event_id-arvona silloin, kun vanha näytöstietue sovitetaan yhteiseen malliin. Epävarmoja vastaavuuksia ei yhdistetä automaattisesti. Nykyinen näytöshistoria ja sen lähteiden vahvistusluokat säilyvät kanonisina; tämä moduulimigraatio ei kopioi tai muokkaa näytöshistoriaa.

## 6. Validointi ja laadunvarmistus

Migraation eheys tarkistetaan komennolla:

    python -m scripts.validate_module_migration

Tarkistus varmistaa, että:
- rekisterissä on täsmälleen yhdeksän topic- ja yksi process-moduuli;
- kaikki kymmenen rekisterimerkintää ovat inactive-tilassa;
- jokaisen määrityksen lähdeviitteet vastaavat oikeaa tehtäväkohtaista lähderekisteriä;
- kaikki source_id-tunnisteet löytyvät yhteisestä lähdekatalogista;
- source_refs-roolit ja required-arvot vastaavat katalogin lähdetyyppiä ja lähderekisterin critical-arvoa;
- ensimmäisen hakuprofiilin kielet ja alueet vastaavat sen lähderekisterin lähteiden katalogitietoja;
- kaikki moduulimääritykset läpäisevät yhteisen moduulisopimuksen ja prosessilaajennuksen skeeman;
- näytösvahtimoduulin tapahtumatyyppiviite on paikallinen, kelvollinen ja identiteettikentiltään yhdenmukainen.

Yleinen moduulilataaja ohittaa inactive-moduulien varsinaisen lataamisen tarkoituksella. Migraatiovalidaattori luo siksi tarkistuksen ajaksi väliaikaisen rekisterikopion, jossa merkinnät ovat active, ja validoi sen samalla tuotantolataajalla. Väliaikainen tiedosto poistetaan tarkistuksen lopuksi. Alkuperäisen data/module-registry.json-tiedoston tila ei muutu.

Testit suoritetaan repositorion tavallisessa unittest discover -ajossa. CI käynnistää migraatiovalidaattorin erillisenä pakollisena vaiheena ennen PR:n hyväksymistä.

## 7. Yhteensopivuus ja käyttöönoton rajat

Nykyiset automaatiot ja lukijat jatkavat nykyisten käsikirjojen, lähderekisterien, tehtäväjonon, seurantatilan, RSS-syötteiden ja näytöshistorian käyttöä. Moduulimäärittelyt ovat rinnakkainen koneellisesti validoitava kuvaus, eivät vielä nykyisten automaatioiden uusi suorituslähde. Näin siirtymä ei aiheuta katkosta eikä kahta samanaikaista kirjoittajaa samoihin tietoihin.

Tämän tiketin yhteydessä:
- moduulirekisteriin ei aktivoida yhtään moduulia;
- vanhoja ohjeita, lähderekistereitä tai RSS-syötteitä ei poisteta;
- nykyisten uutisten tai näytösten historiaa ei kopioida uuteen tietovarastoon;
- tehtäväkiertoa tai näytösvahdin päivittäistä erillisyyttä ei muuteta;
- ChatGPT:n automaatioasetuksia, ajastuksia, aikavyöhykkeitä, ohjeita tai kohdekeskusteluja ei muuteta.

Moduulikohtaisen tilan ja historian migraatio on kuvattu [omassa dokumentissaan](moduulikohtainen-tila.md) ja toteutetaan #106:ssa. Seuraavaksi #107 määrittelee tutkimus- ja tekoälypalvelujen adapterit ja #108 toteuttaa yhteisen orkestroinnin. Tuotantomoduulien aktivointi ja nykyisten lukijoiden suoritusvastuun siirto tehdään vasta erillisessä, testatussa käyttöönotossa.

## 8. Palautus

Jos määritysten vertailussa tai validoinnissa ilmenee virhe, palauta moduulimääritykset ja data/module-registry.json edelliseen hyväksyttyyn Git-commit-versioon. Koska vanhoja tiedostoja, ajastuksia, RSS-syötteitä tai historiatietoja ei poisteta eikä muuteta, palautus ei edellytä niiden rekonstruointia. Rekisterimerkinnät voidaan palauttaa tyhjään rekisteriin tai aiempaan passiiviseen versioon ilman tuotantoajojen katkeamista.

## Muutoshistoria

- **1.0.0 – 2026-11-18:** ensimmäinen kymmenen moduulin passiivinen migraatio, lähdeviitteiden vastaavuustarkistus, näytösvahtimoduulin tapahtumatyyppimääritys ja CI-validointi.
