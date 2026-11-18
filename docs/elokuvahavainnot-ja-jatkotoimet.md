# Elokuvahavainnot ja kriteerikohtaiset jatkotoimet

**Versio:** 1.0.0  
**Päiväys:** 2026-11-18  
**Liittyvä tiketti:** [#66 – Elokuvahavaintorekisteri ja kriteerikohtaiset jatkotoimet](https://github.com/mikknikk/aiheseurain/issues/66)  
**Seuraava sisältötehtävä:** [#67 – Käyttäjän hyväksymä elokuvien hakukriteeristö](https://github.com/mikknikk/aiheseurain/issues/67)

## 1. Tarkoitus

Tämä kokonaisuus kokoaa yksittäisistä näytöshavainnoista elokuvatasoisen havaintorekisterin ja reitittää käyttäjän hyväksymien hakukriteerien perusteella määritellyt jatkotoimet. Ensimmäinen tekninen toimintotyyppi on Discord-webhook.

Tämä ei korvaa näytösvahtia eikä yleistä tapahtumavahtia. Se ei myöskään määrittele käyttäjän elokuvakiinnostuksen kohteita. Varsinaiset hakukriteerit tulevat myöhemmin tiketistä #67.

## 2. Tietojen omistajuus ja suhde yleiseen tapahtumavahtiin

Kolme tietokokonaisuutta pidetään erillään:

| Tietokokonaisuus | Kanoninen omistaja | Mitä se tallentaa |
|---|---|---|
| Yksittäiset näytökset | #109:n `film-screening`-tapahtumatila ja append-only-historia | Näytös-ID, elokuvan näyttönimi, teatteri, kaupunki, aika, tila ja näytöslähteet |
| Elokuvahavainnot | `data/movie-observations.json` | Elokuvan pysyvä tunniste, nimet, vuosi, ensihavainto, kriteeriosumat, lähteet ja viitteet näytös-ID:ihin |
| Jatkotoimien toimitus | `data/movie-action-outbox.json` | Kriteerikohtainen toimintotapahtuma, idempotenssiavain, yritykset ja toimitustila |

Elokuvarekisteri ei kopioi teatteria, näytösaikaa, näytöksen tilaa tai näytöshistoriaa. Se säilyttää vain viitteen `screening_id)-tunnisteeseen. Näytöksen muuttuminen tai peruuntuminen käsitellään edelleen #109:n tapahtumavahdissa.

Elokuvatasoinen rekisteri on tarkoituksella erillinen, koska sama elokuva voi saada useita näytöksiä, lähteitä ja hakukriteeriosumia. Elokuva ja yksittäinen näytös ovat eri entiteettejä ja niillä on eri elinkaari.

## 3. Elokuvan tunnistaminen

Tunniste muodostetaan seuraavassa järjestyksessä:

1. IMDb-tunniste, jos se on saatavilla.
2. TMDB-tunniste, jos IMDb-tunnistetta ei ole.
3. Varatunniste, joka perustuu normalisoituun nimeen ja julkaisuvuoteen.
4. Jos vuotta ja ulkoista tunnistetta ei ole, luodaan näytöskohtainen epävarma ehdokas. Sitä ei yhdistetä automaattisesti toiseen samannimiseen elokuvaan.

Nimen normalisointi käyttää Unicode NFKC -muotoa, kirjainkoon yhtenäistämistä ja välimerkkien käsittelyä. Eri kirjoitusjärjestelmien kirjaimia ei translitteroida pois.

IMDb-/TMDB-tunniste on korkean luottamuksen tunniste. Nimi- ja vuosivariante on keskitason tunniste; se on deterministinen mutta voidaan merkitä manuaalista tarkistusta vaativaksi, jos lähteet ovat ristiriidassa. Ilman vuotta tai ulkoista tunnistetta käytetään matalan luottamuksen ehdokasta, jonka avaimessa on myös alkuperäinen `screening_id`.

Ristiriitaisia ulkoisia tunnisteita ei yhdistetä. Epävarmat osumat säilytetään erillisinä ja merkitään tarkistettaviksi.

## 4. Elokuvahavaintorekisteri

Rekisterin skeema on `schemas/movie-observation-registry.schema.json`, ja nykyinen tuotantotiedosto on `data/movie-observations.json`.

Yksi elokuvatietue sisältää:

- pysyvän `movie_id)-tunnisteen, ensisijaisen nimen ja nimivariantit;
- julkaisuvuoden ja saatavilla olevat IMDb-/TMDB-tunnisteet;
- ensimmäisen ja viimeisimmän havainnon aikaleimat;
- tunnistuksen luottamustason ja manuaalisen tarkistuksen lipun;
- viitteet kaikkiin liittyviin `screening_id)-tunnisteisiin;
- lähteet ja kaikki osuneet kriteerit versioineen.

Saman kriteerin toistuvat osumat yhdistetään yhdeksi kriteeritietueeksi. Ensimmäinen ja viimeisin osuma-aika, kaikki perustelut sekä lähdeviitteet säilyvät. Rekisterin päivitys on idempotentti ja käyttää SHA-versiotarkistusta.

## 5. Kriteerikohtaiset jatkotoimet

Kriteerit ja niihin liitetyt toiminnot ovat erillinen määritys tiedostossa `data/movie-action-config.json`. Jokaisella toiminnolla on kriteeritunniste, toimintotunniste, semanttinen versio, tyyppi ja aktiivisuustieto. Yhdelle kriteerille voi määrittää nolla tai useita toimintoja.

Toiminto jonoutuu vain, jos elokuvan rekisterissä on vastaava kriteeriosuma ja määrityksen toiminto on käytössä. Eri kriteerien eri toiminnot säilyvät erillisinä. Saman toiminnon idempotenssiavain muodostuu elokuvan, kriteerin, toimintotunnisteen ja toimintoversion yhdistelmästä.

Toimintotapahtuman versioitu payload validoidaan skeemalla `schemas/movie-action-event.schema.json`. Se sisältää elokuvan tunnisteen ja nimen, julkaisuvuoden, ensihavainnon ajan, toimintoa käynnistäneen kriteerin, toimintoversion, näytösviitteet ja lähde-URL:t.

## 6. Outbox ja Discord

`data/movie-action-outbox.json` säilyttää toimintojen toimitustilan. Tila on `pending`, `sent` tai `failed`. Epäonnistunut lähetys säilyy jonossa rajattuja uusintayrityksiä varten. Yritysten määrän, aikaleiman ja virheen luokan voi jäljittää ilman, että virheen sisältö tai webhook-salaisuus kirjataan.

Discord-liitäntä saa webhook-osoitteen ja kuljettimen ajonaikaisesti. Webhook-osoitetta ei tallenneta kriteerimääritykseen, elokuvarekisteriin, payloadiin, outboxiin tai lokiin. Testit käyttävät injektoitua muistissa toimivaa kuljetinta eivätkä tee verkkokutsuja.

## 7. Tuotannon tila ja hyväksyntärajat

Tuotannon toimintomääritys `data/movie-action-config.json` on tarkoituksella tyhjä. Testikriteerit ja niiden Discord-toiminnot ovat vain tiedostossa `tests/fixtures/movie-action-config.json`.

Tässä vaiheessa:

- käyttäjän varsinaisia elokuvakriteerejä ei ole keksitty tai aktivoitu;
- Discord-webhookin tuotantosalaisuutta ei ole lisätty;
- tuotannon outbox on tyhjä;
- näytösvahtia, sen ajastusta, aikavyöhykettä, ohjeita tai kohdekeskustelua ei ole muutettu;
- mikään uusi toiminto ei lähetä tuotantoviestejä.

Tuotantokriteerin ja Discord-toiminnon käyttöönotto vaatii käyttäjän hyväksymän kriteeritunnisteen ja salaisuuden erillisen konfiguroinnin. #67 määrittelee hakukriteeristön; se ei saa aktivoida Discordia ilman hyväksyttyä toimintomääritystä.

## 8. Validointi ja testaus

CI validoi rekisterin, toimintomääritykset, tapahtumapayloadin ja outboxin JSON Schema -skeemoilla. Lisäksi se varmistaa, että tuotannon toimintomääritys on tyhjä ja testifixtuurin tunnisteet alkavat `test-)-etuliitteellä.

Yksikkötestit kattavat ulkoisen tunnisteen ensisijaisuuden, nimi-/vuosivarianteen, epävarmojen tunnistusten erillään pitämisen, kriteeriosumien yhdistämisen, SHA-konfliktit, usean kriteerin toimintojen reitityksen, idempotenssin, Discord-kuljettimen, epäonnistuneen lähetyksen uusinnan ja salaisuuden poissulkemisen.

Automaattiset testit osoittavat tietomallin ja teknisen mekanismin toiminnan. Ne eivät osoita tuotantolähteiden kattavuutta, oikeiden elokuvien tunnistamisen laatua tai Discordin tuotantoyhteyttä.

## Muutoshistoria

- **1.0.0 – 2026-11-18:** ensimmäinen elokuvatason havaintorekisteri, #109:n näytöstapahtumiin perustuva tietojen omistajuus, kriteerikohtainen toimintomalli, Discord-liitännän testisopimus ja tyhjän tuotantokonfiguraation rajaus.
