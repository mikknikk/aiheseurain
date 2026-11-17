# Seurantamoduulin tietosopimus

**Sopimusversio:** 1.0.0  
**Liittyvä kehitystehtävä:** [#102 – Määrittele seurantamoduulien tietosopimus ja määritysskeemat](https://github.com/mikknikk/aiheseurain/issues/102)

Tämä dokumentti määrittelee Aiheseuraimen aihe- ja prosessimoduulien koneellisesti luettavan määrityksen. Yhteinen sopimus sisältää vain moduulien tunnistamiseen, versiointiin, yhteisiin kyvykkyyksiin ja rajapintoihin tarvittavat tiedot. Moduulityyppien omat sisältötiedot validoidaan erillisillä tyypitetyillä skeemoilla.

## 1. Sopimuksen tiedostot

| Tiedosto | Vastuu |
|---|---|
| `schemas/seurantamoduuli.schema.json` | Yhteinen moduulin perustietosopimus ja topic/process-tyyppien erottelu |
| `schemas/module-extensions/*.schema.json` | Yksittäisten prosessi- ja myöhemmin muiden moduulilaajennusten omat rakennesäännöt |
| `examples/seurantamoduulit/*.json` | Ihmiselle luettavat, skeemojen avulla validoitavat esimerkkimääritykset |
| `scripts/validate_module_contract.py` | Skeemojen, esimerkkien ja negatiivisten tapausten tarkistus |

Skeemat ovat normatiivinen koneellinen rakenne. Tämä dokumentti selittää kenttien merkityksen, elinkaaren ja yhteensopivuussäännöt; se ei korvaa skeemoja.

## 2. Kolme eri versiota ja tunnistetta

- **`module_id`** on moduulin pysyvä tunniste. Se ei riipu nimestä, kuvauksesta, aihealueen otsikosta tai tiedostopolusta. Tunnistetta ei käytetä uudelleen toiseen moduuliin.
- **`definition_version`** on kyseisen moduulin määrityksen semanttinen MAJOR.MINOR.PATCH-versio. Se kasvaa, kun moduulin omistama määrityssisältö muuttuu. Julkaistu versio on muuttumaton.
- **`contract_version`** kertoo, minkä yhteisen tietosopimuksen rakennetta määritys noudattaa. Se ei kasva pelkästään aiheen tai moduulin sisällön muuttuessa.
- **Rajapinnan `version`** kertoo sisään- tai ulostulon tietosopimuksen version. Se on riippumaton sekä moduulin määrityksestä että yhteisestä moduulisopimuksesta.
- **Kyvykkyyden `minimum_version`** ilmoittaa moduulin edellyttämän kyvykkyyden vähimmäisversion. Se ei nimeä palveluntarjoajaa tai yksittäistä teknologiaa.

Nimi ja kuvaus ovat ihmiselle tarkoitettua esitystekstiä. Niitä saa muuttaa ilman, että moduulin pysyvä tunniste vaihtuu, mutta julkaistua määritysversiota ei kirjoiteta jälkikäteen yli.

## 3. Yhteiset kentät

| Kenttä | Tarkoitus |
|---|---|
| `module_id` | Pysyvä, yksilöllinen moduulitunniste |
| `module_type` | `topic` tai `process` |
| `definition_version` | Moduulin muuttumaton semanttinen versio |
| `name`, `description` | Ihmiselle tarkoitettu nimi ja kuvaus |
| `replaces` | Aiemmat moduulitunnisteet, jotka uusi moduuli korvaa |
| `capabilities` | Vaaditut ja valinnaiset järjestelmäkyvykkyydet sekä vähimmäisversiot |
| `interfaces.input` | Moduulin vastaanottaman pyynnön sopimustunniste ja versio |
| `interfaces.output` | Moduulin tuottaman tuloksen sopimustunniste ja versio |
| `source_refs` | Viittaukset yhteisen lähdekatalogin lähdetunnisteisiin ja niiden rooleihin |
| `search_profiles` | Hakujen tarkoitus, hakutermit, kielet ja alueet |
| `editorial_rules` | Moduulikohtaiset sisällytys-, poissulku-, varmennus-, raportointi- ja epävarmuussäännöt |

Lähdeviittaus sisältää vain `source_id`-arvon ja moduulin kannalta olennaisen roolin. Lähteen nimi, URL, kieli, yleinen luotettavuusluokka ja muut yhteiset perustiedot pysyvät lähdekatalogissa. Tehtäväkohtaisia lähdekäyttörekistereitä ei kopioida moduulimäärittelyyn.

Kielet esitetään kielitunnisteina (esimerkiksi `fi` tai `pt-BR`). Alueet esitetään vakaina isoina tunnisteina, esimerkiksi `FI` tai projektissa sovittuna aluekoodina `GLOBAL`. Hakuprofiili on tarkoituksellinen hakukokonaisuus, ei ajastin.

## 4. Aihemoduuli ja prosessimoduuli

### Aihemoduuli

Aihemoduulin `module_type` on `topic`, ja sillä on `topic`-laajennus. Se kuvaa seurattavan aiheen sisältöä, mukaan otettavia ja pois rajattavia asioita sekä tarvittaessa tunnistettavia henkilöitä, teoksia, organisaatioita tai muita entiteettejä.

Esimerkki: `examples/seurantamoduulit/tolkien.topic.json`.

### Prosessimoduuli

Prosessimoduulin `module_type` on `process`, ja sillä on `process_extension`. Laajennus nimeää oman tunnisteensa ja versionsa sekä osoittaa oman skeemansa `schema_uri)-kentässä. Sen `configuration` validoidaan kyseistä laajennusta vasten erikseen.

Näin prosessimoduulin sisältöä ei yritetä puristaa aiheen `scope`-, `include`- ja `exclude`-kenttiin. Uusi prosessityyppi voi tuoda oman laajennusskeemansa muuttamatta kaikkien muiden moduulien rakennetta. Yhteinen moduulisopimus validoi laajennuksen rajapinnan; rekisterin myöhempi toteutus vastaa laajennuksen tunnistamisesta ja oikean skeeman valinnasta.

Esimerkki: `examples/seurantamoduulit/intialaisten-elokuvien-naytosvahti.process.json` käyttää laajennusta `event-watch.film-screenings`, jonka rakenne määritellään tiedostossa `schemas/module-extensions/event-watch-film-screenings.schema.json`. Esimerkki osoittaa laajennusmekanismin, ei vielä yleistä tapahtumavahtimoottoria eikä tuotantoon siirrettyä näytösvahtia.

## 5. Yhteisten palvelujen ja moduulisisällön raja

Moduulimäärittely kertoo, mitä seuranta tarvitsee ja millaisia tietoja se käsittelee. Se ei valitse teknistä toteuttajaa.

**Moduulimäärittelyyn kuuluvat:** sisältörajaukset, lähdeviittaukset, hakuprofiilit, kieli- ja aluerajaukset, toimitukselliset säännöt, kyvykkyystarpeet sekä sisään- ja ulostulon sopimusversiot.

**Moduulimäärittelyn ulkopuolelle kuuluvat:**
- ajastimen kellonaika, aikavyöhyke, suoritusväli ja käynnistysmekanismi;
- tekoäly- tai tutkimuspalvelun nimi, palveluntarjoajan tunnus tai mallikohtaiset asetukset;
- API-avaimet, salaisuudet, käyttöoikeustunnukset ja muut tunnistetiedot;
- GitHub-, tietokanta-, tiedostojärjestelmä-, RSS- tai muun tallennus- ja julkaisualustan tekniset asetukset;
- suoritusympäristön resurssit, verkkoyhteydet, uudelleenyritysten tekniset parametrit ja käyttöliittymän asetukset.

Yhteinen ydin tai sen adapterit ratkaisevat myöhemmin, millä käytettävissä olevalla palvelulla kyvykkyys toteutetaan. Moduuli ilmoittaa kyvykkyystarpeen, ei palveluntarjoajaa.

## 6. Yhteensopivuus ja tuntemattomat kentät

- Yhteisen skeeman pakolliset kentät vaaditaan kaikilta moduuleilta. Valinnaiset kentät voidaan jättää pois.
- Yhteisen skeeman tuntemattomat kentät hylätään (`additionalProperties: false`). Tämä paljastaa kirjoitusvirheet ja estää teknisten asetusten ujuttamisen moduulimäärittelyyn.
- Prosessilaajennuksen `configuration)-sisältö validoidaan laajennuksen omalla skeemalla. Myös laajennusskeema hylkää tuntemattomat kentät, ellei kyseisen laajennuksen oma versio nimenomaisesti salli niitä.
- Yhteisen sopimuksen MAJOR-version muutos voi rikkoa yhteensopivuuden. MINOR-muutos lisää yhteensopivasti valinnaisia kenttiä tai kyvykkyyksiä; PATCH korjaa sopimuksen tulkintaa muuttamatta sen rakennetta.
- Moduulin määritysversion MAJOR tarkoittaa yhteensopimatonta sisältömuutosta, MINOR taaksepäin yhteensopivaa sisältölaajennusta ja PATCH korjausta, joka ei muuta määrityksen tarkoitettua toimintaa.
- Rajapintasopimusten yhteensopivuus arvioidaan niiden omien versioiden ja sopimusten perusteella. Pelkkä moduulin versionumero ei todista rajapintojen yhteensopivuutta.

Skeeman rakenteellinen validointi ei yksin todista, että lähdeviittaukset ovat olemassa, kyvykkyydet ovat saatavilla tai moduulin sisältö on toimituksellisesti oikein. Rekisteri ja suoritusorkestrointi lisäävät nämä eheys- ja toimintatarkistukset myöhemmissä vaiheissa.

## 7. Deaktivointi, korvaaminen ja vanhat ajot

Julkaistua moduulimäärittelyä ei muokata paikallaan. Jokainen julkaistu ajo yksilöidään vähintään moduulitunnisteella, määrityksen versiolla, yhteisen sopimuksen versiolla sekä ajon käyttämällä rajapintaversiolla. Myöhempi suoritusrekisteri tallentaa myös määrityksen sisällön tiivisteen, jotta sama versiotunniste ei voi huomaamatta viitata muuttuneeseen sisältöön.

Deaktivointi on moduulin rekisteritilan muutos, ei syy poistaa tai muokata vanhaa määritystä. Rekisteri (tiketti #103) omistaa aktiivisuus- ja deaktivointitiedot sekä niiden tapahtumahistorian. Passivoitu moduuli ei kelpaa uusiin ajoihin, mutta sen aiemmat määritysversiot ja ajoviitteet säilyvät tulkittavina.

Korvaava moduuli saa oman pysyvän tunnisteensa ja ilmoittaa `replaces)-kentässä korvaamansa tunnisteet. Korvaaminen ei siirrä vanhoja ajoja uuden moduulin alle eikä muuta vanhan moduulin historiaa. Saman moduulin sisältömuutos tehdään uutena `definition_version)-julkaisuna.

## 8. Esimerkkien ja testien käyttö

Aihe- ja prosessiesimerkit ovat sopimuksen testiaineistoa, eivät aktiivinen moduulirekisteri. Niiden lähdeviittaukset havainnollistavat viittaustapaa; ne eivät muuta nykyisiä lähderekistereitä tai automaatioiden asetuksia.

Aja paikallisesti:

```bash
python scripts/validate_module_contract.py
python -m unittest tests.test_module_contract -v
```

CI suorittaa saman validoinnin PR-testeissä. Testit kattavat:
- kelvollisen aihemoduulin ja prosessimoduulin;
- puuttuvan pysyvän tunnisteen;
- virheellisen semanttisen version;
- väärän moduulityypin laajennuksen;
- tuntemattoman tai palveluntarjoajakohtaisen juuritason kentän;
- tuntemattoman prosessilaajennuksen kentän;
- prosessilaajennukseen sopimattoman tapahtumatyypin.

Testit todistavat skeeman ja esimerkkien rakenteellisen yhteensopivuuden. Ne eivät vielä testaa moduulirekisteriä, lähde-ID:iden olemassaoloa, kyvykkyyksien toteutusta, ajonaikaista reititystä tai tuotantomoduulien migraatiota.

## 9. Seuraavat toteutusvaiheet

- #103 toteuttaa rekisterin, joka lukee ja validoi määritykset, ratkaisee laajennusskeemat ja hallitsee moduulien aktiivisuutta.
- #104 kartoittaa nykyisten aiheiden ja erillisten prosessien siirtymän.
- #105 siirtää nykyiset aiheet ja näytösvahdin varsinaisiin moduulimäärittelyihin.
- #106 erottaa moduulikohtaisen tilan, tarkistuspisteet ja tapahtumahistorian.
- #107 määrittelee tekoäly- ja tutkimuspalvelujen adapterisopimukset.
- #108 toteuttaa yhteisen suoritusorkestroinnin vaiheittaisen käyttöönoton.

Tämä tietosopimus ei muuta nykyisten automaatioiden ajastuksia, suoritusvälejä, aikavyöhykkeitä, ohjeita, kohdekeskusteluja tai aktiivisuutta. Se ei ota uusia moduuleja tuotantokäyttöön.
