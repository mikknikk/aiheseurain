# Yleinen tapahtumavahti

**Versio:** 1.0.0  
**Päiväys:** 2026-11-18  
**Liittyvä tiketti:** [#109 – Yleistä nykyinen näytösvahti uudelleenkäytettäväksi tapahtumavahdiksi](https://github.com/mikknikk/aiheseurain/issues/109)

## 1. Tarkoitus ja rajat

Tapahtumavahti on uudelleenkäytettävä kyvykkyys, joka käsittelee eri moduulien määrittelemiä tapahtumia yhteisen elinkaaren kautta. Se ei ole oma automaatio, ajastin eikä tapahtumien hakupalvelu. Se ei myöskään päätä, mitkä tapahtumat ovat aiheen kannalta kiinnostavia: sen tekee aihe- tai prosessimoduuli omilla rajauksillaan ja lähteillään.

Tässä toteutusvaiheessa yhteinen ydin käsittelee sille annettuja havaintoja. Se ei hae verkkosivuja, kutsu tekoälypalveluja, kirjoita GitHubiin eikä käynnistä tuotantoprosesseja. Lähdeadapterit ja ajon orkestrointi ovat erillisiä kyvykkyyksiä.

## 2. Vastuunjako

| Vastuu | Yhteinen tapahtumaydin | Tapahtumatyypin määritys ja sovitin |
|---|---|---|
| Tapahtuman yleinen tietorakenne | Kyllä | Täyttää tyypin vaatimat kentät |
| Tunnisteen säilyttäminen | Käsittelee kanonista tunnistetta | Muodostaa tai ratkaisee kanonisen tunnisteen |
| Duplikaattien käsittely | Yhdistää saman kanonisen tunnisteen havainnot | Määrittää identiteettikentät ja epävarman vastaavuuden säännöt |
| Lähteiden jäljitettävyys | Säilyttää ja deduplikoi lähdetiedot | Muuntaa lähdekohtaiset vahvistustasot |
| Muutosten luokittelu | Vertaa määrityksen seuraamia kenttiä | Määrittää kentän muutostyypin |
| Ristiriidat | Säilyttää ristiriitaiset arvot ja lähteet | Voi tuottaa lisänäyttöä; ei saa peittää ristiriitaa |
| Peruutukset ja tilat | Käsittelee eksplisiittiset tilasiirtymät | Tunnistaa lähteestä, onko tila todella muuttunut |
| Historia | Lisää idempotentit tapahtumat append-only-lokiin | Tuottaa havainnot ja selitteet |
| Haku ja raportointi | Ei kuulu tähän ytimeen | Hakuadapteri tuottaa havaintoja; raportointikerros esittää ne |

## 3. Yhteinen tietomalli

Tapahtumatyypin tunniste ja versio erotetaan yksittäisen tapahtuman tunnisteesta. event_type_id kertoo tapahtuman lajin (esimerkiksi film-screening tai conference-session); canonical_event_id yksilöi seurattavan tapahtuman pysyvästi. Näyttönimi tai URL ei yksin ole pysyvä tunniste.

Nykytilassa jokaisella tapahtumalla on tapahtumatyypin ja kanonisen tapahtuman tunniste, tapahtumatyypin määrityksen mukaiset attribuutit, yleinen tila, identiteettiavain, jäljitettävät lähteet, ensimmäinen ja viimeisin havaintoaika sekä mahdolliset ratkaisemattomat ristiriidat.

Tapahtumahistoria sisältää yksilöllisen deterministisen tunnisteen, havaintoajan, tapahtumatyypin ja tapahtuman tunnisteet, toiminnon, aiemman ja nykyisen tilannekuvan, lähteet sekä selitteen. Historiaan lisätään uusi tapahtuma; aiempia merkintöjä ei muokata tai poisteta.

## 4. Tapahtumatyypin laajennussopimus

Tapahtumatyyppi määritellään JSON-tiedostona, joka validoidaan schemas/event-watch/event-type.schema.json -skeemalla. Määritys kertoo pysyvän tapahtumatyyppitunnisteen ja semanttisen version, identiteetin muodostamiseen käytettävät kentät, pakolliset attribuutit, seurattavat attribuutit ja niiden muutosten luokat sekä sallitut tilat.

Tapahtumatyypin lisääminen edellyttää uuden määrityksen ja tarvittaessa uuden lähdesovittimen lisäämistä. Lähdesovittimet toteuttavat scripts/event_watch.py-tiedoston EventSourceAdapter-sopimuksen: ne tekevät oman hakunsa, vastaavat rajatuista uusintayrityksistä ja palauttavat normalisoidut havainnot. collect_from_adapters eristää yhden lähteen virheen ja palauttaa osittaisen tuloksen sekä epäonnistuneiden lähteiden tunnisteet. Yhteisen ytimen lähdekoodia ei tarvitse muuttaa, jos havainto voidaan tuottaa olemassa olevalla yleisellä sovittimella. Erityinen identiteettilogiikka kapseloidaan tapahtumatyypin sovittimeen, ei yhteiseen ytimeen. Poistaminen tehdään poistamalla tyyppi aktiivisesta moduulirekisteristä erillisessä hyväksytyssä muutoksessa; vanhaa historiaa ei poisteta.

## 5. Yhteisen käsittelyn vaiheet

1. Havaintojen normalisointi: sovitin tuottaa tapahtumatyypin, pysyvän kanonisen tunnisteen, attribuutit, lähteet ja aikavyöhykkeellisen havaintoajan.
2. Validointi: ydin tarkistaa tapahtumatyypin, pakolliset kentät, tilat, lähdeosoitteet ja aikaleimojen aikavyöhykkeet.
3. Ryhmittely: saman kanonisen tunnisteen havainnot ryhmitellään. Eri tapahtumatyyppien havaintoja ei yhdistetä.
4. Lähteiden yhdistäminen: lähteet deduplikoidaan julkaisijan, URL:n ja vahvistustason perusteella.
5. Ristiriitojen käsittely: ristiriitaisia attribuutteja ei ratkaista valitsemalla viimeistä havaintoa. Aiempi tunnettu arvo säilytetään ja ristiriitaiset vaihtoehdot sekä lähteet kirjataan.
6. Muutosten tunnistus: määrityksen seurattuja kenttiä verrataan edelliseen tilaan. Muutokset luokitellaan ajan, paikan tai muiden tietojen muutoksiksi.
7. Tilasiirtymät: nimenomainen peruutus, poistuma, palautuminen ja tapahtuman päättyminen kirjataan erillisinä toimintoina. Ohjelmistosta puuttuminen ei yksin tarkoita peruutusta.
8. Historian päivitys: deterministinen tunniste estää saman muutoksen kahdentamisen uusintakäsittelyssä.
9. Osittainen lähdeajo: epäonnistuneet lähteet kirjataan ajon metatietoihin. Puuttuvia havaintoja ei tulkita poistumiksi eikä aiempaa nykytilaa tyhjennetä.
10. Raportointi ja julkaisu: tapahtumaydin palauttaa nykytilan ja muutokset; erillinen raportointikerros päättää esitystavan ja julkaisun.

## 6. Ensimmäiset tapahtumatyypit ja yhteensopivuus

modules/processes/indian-film-screening-watch/event-type.json on näytösvahtimoduulin oma tapahtumatyyppimääritys; examples/event-types/film-screening.json säilyy yleisen sopimuksen esimerkkinä. Se säilyttää elokuvan, teatterin, kaupungin, näytösajan, esityskielen, tekstityksen ja näytöskohtaisen tilan. scripts/event_watch_adapters.py muuntaa nykyisen näytöstietueen yleiseksi havainnoksi sekä säilyttää alkuperäisen vahvistusluokan. Sovitin pystyy lukemaan nykyiset 111 näytöstietuetta ja 47 historiatapahtumaa yleiseen tilannekuvaan sekä käsittelemään annetut näytöshavainnot yhteisellä reconcile-ytimellä vain muistissa. Testi osoittaa näytöksen muutoksen tunnistamisen muuttamatta vanhaa JSON-tiedostoa.

examples/event-types/conference-session.json on olennaisesti erilainen testitapaus. Se kuvaa konferenssin yksittäistä esitystä, jolla on konferenssi, sessiokoodi, puhujatieto ja huone. Sama yhteinen ydin käsittelee sitä ilman konferenssi- tai elokuvakohtaista ohjelmakoodia.

Nykyinen näytöshistoria data/naytosten-muutoshistoria.json, sen skeema, RSS-syöte, GUIDit, käsikirja ja automaation asetukset pysyvät ennallaan. Varsinainen prosessimoduuli ja tapahtumatyyppimääritys on rekisteröity inactive-tilassa; ne eivät vielä ohjaa tuotantoajoa. Yleinen sovitin ja reconcile_screening_observations ovat tässä vaiheessa vain lukuun ja testaukseen. Tuotantokäyttöönotto, historian migraatio ja näytösvahdin ajon vaihtaminen vaativat erillisen hyväksynnän.

## 7. Validointi ja testaus

Yleisen historian rakenne validoidaan schemas/event-watch/event-history.schema.json -skeemalla. Tapahtumatyypin määritys validoidaan omalla skeemallaan. Testit kattavat uuden tapahtuman ja uusintakäsittelyn, ajan muutoksen, peruutuksen, poistuman ja palautumisen, päättyneen tapahtuman säilyttämisen, ristiriitaiset lähteet, osittaisen lähdevirheen, aikavyöhykkeen pakollisuuden, alkuperäisen tilan muuttumattomuuden, nykyisen näytöshistorian lukevan sovittamisen sekä konferenssitapahtuman käytön samalla ytimellä.

Automaattinen testi osoittaa tietorakenteen ja käsittelylogiikan toiminnan testiaineistolla. Se ei todista ulkoisten lähteiden sisältöä, lähteiden riippumattomuutta eikä tuotantoautomaation käyttäytymistä.

## Muutoshistoria

- 1.0.0 – 2026-11-18: ensimmäinen yleinen tapahtumamalli, tyypitetyt laajennusmääritykset, yhteinen muutosten ja historian käsittely, näytöshistorian lukevan sovittimen rajaus sekä konferenssiesityksen erillinen testitapaus.


## 8. Seurantakohteet ja julkaisureititys

Tapahtumavahtimoduuli on suoritusraja, ei yksittäinen elokuva tai RSS-syöte. Se voi käsitellä useita erillisiä seurantakohteita, kuten elokuvia ja festivaaleja. Kukin kohde voi tuottaa tapahtumahavaintoja, jotka reititetään vain kyseisen kohteen omaan RSS-julkaisukohteeseen. Näytösvahtiesimerkki näyttää kaksi kohdetta ja kaksi erillistä RSS-kanavaa; yhdistelmäsyötettä ei muodosteta. Nykyisen näytösvahtiajon ja RSS-syötteen reititystä ei ole vaihdettu.
