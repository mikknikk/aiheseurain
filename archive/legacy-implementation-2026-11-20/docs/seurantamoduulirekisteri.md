# Seurantamoduulirekisteri

**Versio:** 1.0.0  
**Liittyvä kehitystehtävä:** [#103 – Toteuta seurantamoduulien rekisteri ja määritysten lataus](https://github.com/mikknikk/aiheseurain/issues/103)  
**Edeltävä sopimus:** [Seurantamoduulin tietosopimus](seurantamoduulin-tietosopimus.md)

Tämä dokumentti kuvaa moduulien teknisen rekisterin ja sen lataajan. Rekisteri kertoo, mistä moduulimääritys löytyy, mitä pysyvää tunnistetta ja versiota sen odotetaan vastaavan sekä onko moduuli aktiivinen. Se ei sisällä aiheen sisältöä eikä käynnistä moduulia.

## 1. Tiedostot ja vastuut

| Tiedosto | Vastuu |
|---|---|
| `data/module-registry.json` | Varsinainen rekisteri. Kymmenen nykyistä moduulia on rekisteröity, kaikki inactive-tilassa. |
| `schemas/seurantamoduulirekisteri.schema.json` | Rekisterin Draft 2020-12 -skeema. |
| `schemas/seurantamoduuli.schema.json` | Moduulimäärityksen yhteinen tietosopimus. |
| `schemas/module-extensions/*.schema.json` | Paikalliset, versioidut prosessilaajennusten skeemat. |
| `scripts/module_registry.py` | Rekisterin deterministinen luku, määritysten lataus ja validointi. |
| `scripts/validate_module_registry.py` | Tuotantorekisterin CI-tarkistus. |
| `tests/fixtures/module-registry.json` | Testirekisteri, joka viittaa erillisiin topic- ja process-esimerkkeihin. |
| `tests/test_module_registry.py` | Rekisterin, latauksen, virhetilanteiden ja eristyksen testit. |

Esimerkkimääritykset eivät ole tuotantorekisterin jäseniä. Niitä käytetään testissä, jotta rekisterin toiminta voidaan todentaa muuttamatta nykyisiä seurantatehtäviä.

## 2. Rekisterimerkintä

Jokainen merkintä sisältää:

- `module_id`: pysyvä moduulitunniste;
- `module_type`: `topic` tai `process`;
- `definition_version`: odotettu määritysjulkaisu;
- `path`: repositorion juureen suhteutettu määritystiedoston polku;
- `status`: `active` tai `inactive`.

Rekisterin `registry_version` ja `contract_version` versioivat rekisterin rakennetta ja sen käyttämää moduulisopimusta. Ne eivät ole yksittäisen moduulin versioita.

Rekisteri ja moduulimääritys pidetään erillään. Rekisterimerkintä on tekninen viite; varsinainen aihe- tai prosessisisältö pysyy moduulin omassa JSON-tiedostossa. Uuden moduulin lisääminen tarkoittaa uuden määrityksen ja rekisterimerkinnän lisäämistä, ei lataajan lähdekoodin muuttamista.

## 3. Lataus ja validointi

Lataaja suorittaa seuraavat vaiheet:

1. Lukee rekisterin ja tarkistaa sen ylätason rakenteen.
2. Tarkistaa jokaisen rekisterimerkinnän erikseen rekisteriskeemalla.
3. Tunnistaa duplikaatit ja hylkää toistuvat pysyvät tunnisteet sekä saman määrityspolun useat käytöt.
4. Ohittaa passiiviset moduulit eikä lisää niitä aktiivisiin määrityksiin.
5. Ratkaisee aktiivisen määrityksen suhteellisen polun ja varmistaa, että tiedosto sijaitsee repositorion sisällä.
6. Lukee JSON-määrityksen ja validoi sen yhteistä moduulisopimusta vasten.
7. Vertaa rekisterin tunnistetta, tyyppiä ja määritysversiota tiedoston omiin arvoihin.
8. Prosessimoduulille etsii paikallisen laajennusskeeman `schema_uri)-tunnisteella ja tarkistaa myös laajennuksen tunnisteen ja version.
9. Palauttaa vain onnistuneesti validoidut aktiiviset määritykset suorittajalle.

Latausjärjestys ja tulosten järjestys ovat deterministisiä: moduulit palautetaan pysyvän tunnisteen ja polun mukaan riippumatta rekisterin rivijärjestyksestä.

## 4. Tilat ja virheiden eristys

Rekisteriin tallennetaan vain tarkoituksellinen käyttötila:

- **active:** moduuli voidaan ladata ja se voi tulla myöhemmin suoritusorkestroinnin valittavaksi, jos kaikki tarkistukset onnistuvat;
- **inactive:** moduuli säilyy rekisterissä, mutta sitä ei ladata aktiiviseksi eikä sitä saa valita uusiin suorituksiin.

**invalid** on latauksen tulostila, ei rekisteriin kirjoitettava käyttötila. Se muodostuu esimerkiksi puuttuvasta tiedostosta, virheellisestä JSONista, tuntemattomasta sopimusversiosta, skeemavirheestä, rekisterin ja määrityksen ristiriidasta tai turvattomasta polusta. Virhe kirjataan kyseisen moduulin tulokseen.

Yksittäisen moduulin määritysvirhe ei pysäytä muiden riippumattomien merkintöjen lataamista. Rekisterin ylätason virhe, kuten tuntematon rekisterirakenneversio tai virheellinen JSON-objekti, estää koko rekisterin tulkinnan ja aiheuttaa selkeän `RegistryError`-virheen. Tällöin lataaja ei arvaa rekisterin tarkoitusta.

## 5. Turvarajat

- Määrityspolku on suhteellinen; absoluuttiset polut ja repositorion ulkopuolelle johtavat polut hylätään myös polun normalisoinnin jälkeen.
- Laajennusskeemat etsitään vain repositorion omasta `schemas/module-extensions/`-hakemistosta.
- `schema_uri` on paikallisen skeeman tunniste, ei lupa hakea skeemaa verkosta.
- Moduulimäärittelyä ei suoriteta koodina. Lataaja käsittelee vain JSON-dataa ja skeemoja.
- Rekisteri ei sisällä ajastuksia, palveluntarjoajavalintoja, tunnuksia, salaisuuksia tai ympäristöasetuksia.
- Lataaja ei käynnistä automaatioita, muuta niiden asetuksia, kirjoita seurantatilaa eikä julkaise sisältöä.

## 6. Testaus ja käyttö

Paikallinen tuotantorekisterin tarkistus:

```bash
python -m scripts.validate_module_registry
```

Rekisterin yksikkötestit:

```bash
python -m unittest tests.test_module_registry -v
```

Koko repositorion testit ajetaan CI:ssä. Testit kattavat aihe- ja prosessimoduulin latauksen, passiivisen moduulin, virheellisen moduulin eristyksen, tuntemattoman moduulisopimusversion, rekisterin ja määrityksen ristiriidan, duplikaatit, polkurajat, ulkoisen skeemaviitteen hylkäämisen ja tulosjärjestyksen.

Rekisterissä on #105:n migraation jälkeen kymmenen nykyistä moduulia, mutta kaikki ovat inactive-tilassa. Näin rekisteri kuvaa nykyisen moduulijoukon ilman, että automaatiot siirtyvät käyttämään uusia määrityksiä. Migraatiovalidaattori tarkistaa passiiviset määritykset väliaikaisen aktiivisen rekisterikopion avulla. Yhtään moduulia ei aktivoida tässä vaiheessa.

## 7. Seuraavat vaiheet

- #104 inventoi nykyiset aiheet ja prosessit sekä suunnittelee hallitun siirtymän. Valmis.
- #105 tuotti nykyisistä aiheista ja näytösvahdista varsinaiset moduulimäärittelyt, lähdeviitteet ja passiiviset rekisterimerkinnät. Aktiivinen käyttöönotto tehdään myöhemmin.
- #106 eriyttää moduulikohtaisen tilan ja tapahtumahistorian. Sen toteutus ja migraatiovalidointi ovat työn alla.
- #107 määrittelee tekoäly- ja tutkimuspalvelujen adapterisopimukset.
- #108 yhdistää moduulien suorittamisen yhteiseen orkestrointiin.
- #109 yleisti nykyisen näytösvahtikyvykkyyden uudelleenkäytettäväksi tapahtumavahdiksi. Valmis; tuotantokäyttöönotto on erillinen päätös.

Tämä rekisteri ei muuta nykyisten automaatioiden ajastuksia, suoritusvälejä, aikavyöhykkeitä, ohjeita, kohdekeskusteluja tai aktiivisuutta eikä ota uusia moduuleja tuotantokäyttöön.


## 8. Seurantakohdeviitteet

Moduulimäärittelyn `target_refs` sisältää moduulin omistamien seurantakohteiden pysyvät tunnisteet. Varsinaiset hakuprofiilit ja kohdekohtaiset rajaukset sijaitsevat `data/targets/`-hakemistossa ja niiden rekisteri on `data/target-registry.json`. Moduuli ei sisällä julkaisukanavan polkua tai teknisiä asetuksia. Kohteen omistavan moduulin tunniste tarkistetaan eheysvalidoinnissa. Julkaisureitityksen omistaa erillinen `data/publication-routing.json`.
