# Elokuvien hakukriteeristö

**Versio:** 1.0.1  
**Päiväys:** 2026-11-18  
**Liittyvä tiketti:** [#67 – Käyttäjän hyväksymä elokuvien hakukriteeristö](https://github.com/mikknikk/aiheseurain/issues/67)  
**Jatkotoimet:** [#66 – Elokuvahavaintorekisteri ja kriteerikohtaiset jatkotoimet](elokuvahavainnot-ja-jatkotoimet.md)

## 1. Tarkoitus ja rajaus

Kriteerimoottori arvioi elokuvien metatietoja käyttäjän hyväksymiä, versioituja sääntöjä vasten. Kriteerit määrittelevät mitä etsitään; #66:n toimintomekanismi huolehtii siitä, mitä kriteeriosumalle tehdään.

Tämä toteutus sisältää kriteerien rakenteen, validoinnin ja arviointimoottorin. Se ei sisällä uusia käyttäjän kiinnostuksen kohteita. Tuotannon `data/movie-search-criteria.json` on tarkoituksella tyhjä, kunnes käyttäjä hyväksyy kriteerit.

## 2. Nykyisen intialaisen elokuvaseurannan säilyttäminen

Nykyinen intialaisten elokuvien näytösseuranta säilyy omana, ennallaan toimivana peruspolkunaan. Sen nykyisiä lähteitä, hakurajauksia, ajastusta, aikavyöhykettä, ohjeita tai kohdekeskustelua ei siirretä eikä muuteta tämän kriteerimoottorin yhteydessä.

Uusi kriteerimoottori on peruspolun rinnalle lisättävä laajennus. Se voi myöhemmin tunnistaa muita käyttäjän hyväksymiä elokuvia, mutta se ei korvaa nykyistä intialaisten elokuvien seurantaa eikä muuta sen kattavuutta.

Elokuvan havainto yhdistetään #66:n elokuvatason rekisteriin. Yksittäisen näytöksen tila ja historia pysyvät #109:n `film-screening`-tapahtumavahdissa.

## 3. Ehdotetut kriteeriluokat

Seuraavat ovat kriteerityyppejä, eivät käyttäjälle oletettuja kiinnostuksen kohteita:

| Luokka | Mahdollinen kohdetieto |
|---|---|
| Henkilö | Näyttelijä, ohjaaja, käsikirjoittaja, tuottaja tai muu tekijä |
| Filmografia | Henkilön tiettyyn työhön, rooliin tai uravaiheeseen liittyvä elokuva |
| Tuotantoyhtiö | Tuotantoyhtiön pysyvä tunniste ja nimivariantit |
| Elokuvasarja tai universumi | Sarjan, jatko-osan, esiosan tai muun yhteisen universumin tunniste |
| Maa tai kieli | Alkuperämaa, tuotantomaa tai alkuperäinen kieli |
| Genre tai aihe | Genre, teema tai avainsanajoukko |
| Festivaali tai palkinto | Tietty festivaali, kilpailusarja tai palkintoyhteys |
| Muu | Erillinen, dokumentoitu ja käyttäjän hyväksymä ehto |

Kriteeriluokka auttaa kuvaamaan kriteerin tarkoitusta. Varsinainen osuma perustuu rakenteisiin ehtoihin ja metatietokenttiin, ei pelkkään vapaamuotoiseen kuvaukseen.

## 4. Kriteerin rakenne

Kriteeritiedoston skeema on `schemas/movie-search-criteria.schema.json`. Yksi kriteeri sisältää:

- pysyvän `criterion_id`-tunnisteen ja semanttisen version;
- nimen, kuvauksen ja kriteeriluokan;
- tilan: `draft`, `active`, `paused` tai `retired`;
- voimaantulo- ja mahdollisen päättymisajan;
- sisällyttävät ehdot ja niiden `all`-/`any`-yhdistämispolitiikan;
- poissulkevat ehdot, joista yksikin estää osuman;
- #66:n toimintomäärityksiin viittaavat `action_ids`-tunnisteet;
- luonti- ja päivitysajat.

Kriteerin sisältömuutos kasvattaa versiota, mutta ei muuta pysyvää tunnistetta. Samasta kriteeritunnisteesta voi säilyttää vanhoja versioita; vain yksi versio voi olla aktiivinen kerrallaan. Historialliset kriteeriosumat säilyttävät käytetyn version.

## 5. Ehtojen kentät ja operaattorit

Kriteeri voi arvioida seuraavia metatietokenttiä:

- `title`, `aliases`;
- `director_ids`, `cast_ids`;
- `production_company_ids`, `franchise_ids);
- `countries`, `languages`, `genres`, `keywords`;
- `release_year), `release_type).

Operaattorit:

- `equals`: normalisoitu täsmävertailu tekstimuotoiselle yksittäiselle kentälle;
- `contains_normalized`: normalisoidun arvon täsmäosuma kentässä tai listassa;
- `contains_any_normalized`: vähintään yhden listan arvon osuma;
- `in_range`: numeerisen julkaisuvuoden suljettu vaihteluväli.

Normalisointi käyttää Unicode NFKC -muotoa, kirjainkoon yhtenäistämistä ja välimerkkien poistamista vertailusta. Kirjoitusjärjestelmiä ei translitteroida pois. Ulkoisia henkilö-, elokuva- tai yritystunnisteita suositaan vapaamuotoisten nimien sijaan.

Sisällyttävien ehtojen `all`-politiikka vaatii kaikkien ehtojen täyttymisen; `any`-politiikka vaatii vähintään yhden. Poissulkevat ehdot arvioidaan aina sisällyttämisen jälkeen, ja mikä tahansa poissulkeva osuma estää kriteeriosuman.

## 6. Kriteeriosuman välitys

Elokuvarekisterin `discovery_channels` erottaa löydöksen nykyisestä intialaisen elokuvan peruspolusta (`indian-film-screening-baseline`) ja käyttäjän hyväksymiin uusiin kriteereihin perustuvasta löydöksestä (`user-criteria`). Kun sama elokuva löytyy molempia polkuja pitkin, kanavat yhdistyvät samaan elokuvatietueeseen ilman näytösmerkintöjen monistamista. Raportti voi näyttää kunkin kriteeriosuman perustelun erikseen.

Arviointimoottori palauttaa kriteeriosumasta:

- `criterion_id) ja `criterion_version);
- osuma-ajan;
- selkokielisen perustelun täsmänneistä sisällytysehdoista;
- vähintään yhden lähde-URL:n.

Tulos siirtyy #66:n `criterion_matches`-tietueeksi. #66 säilyttää kriteeriosuman elokuvan historiassa ja reitittää siihen liittyvät toimintotunnisteet. Kriteerimoottori ei lähetä ilmoituksia eikä käsittele webhook-salaisuuksia.

Kriteerin `action_ids`-viitteet tarkistetaan #66:n toimintomäärityksiä vasten. Puuttuva tai ylimääräinen viite estää validoinnin, jotta kriteeri ja toiminto eivät ajaudu eri suuntiin.

## 7. Tuotannon tila ja käyttäjän hyväksyntä

Tuotannon kriteeritiedosto on tyhjä. Testikriteerit ovat vain `tests/fixtures/movie-search-criteria.json`-tiedostossa, ja niiden tunnisteet alkavat `test-`-etuliitteellä.

Ennen tuotantokriteerien lisäämistä käyttäjän on hyväksyttävä ainakin:

- mitä henkilöitä, elokuvia, sarjoja, tuotantoyhtiöitä tai muita kohteita seurataan;
- mitä sisällyttäviä ja poissulkevia ehtoja käytetään;
- millä kielillä ja alueilla lähteitä haetaan, jos rajaus ei ole yleinen;
- mitkä kriteerit ovat aktiivisia ja milloin niiden voimassaolo alkaa;
- mitkä #66:n toiminnot liittyvät kuhunkin kriteeriin.

Mitään näistä arvoista ei päätellä tämän teknisen rungon perusteella. Kriteerien lisääminen ei itsessään aktivoi Discord-toimintoa; myös #66:n toimintomäärityksen ja mahdollisen webhook-salaisuuden käyttöönotto edellyttää erillistä hyväksyntää.

## 8. Validointi ja testaus

CI validoi tuotannon tyhjän kriteerirekisterin, testifixtuurin, ehdot, versiot ja #66:n toimintoviitteet. Yksikkötestit kattavat `all`-/`any`-logiikan, poissulut, voimassaoloajat, keskeytetyt kriteerit, lähdevaatimukset, virheelliset kenttä-/operaattoriyhdistelmät ja toimintoviitteiden ristiriidat.

Testit osoittavat kriteerimoottorin rakenteellisen toiminnan. Ne eivät vahvista minkään todellisen henkilön, elokuvan tai muun aiheen olevan käyttäjän hyväksymä kiinnostuksen kohde.

## Muutoshistoria

- **1.0.1 – 2026-11-18:** lisättiin löydöskanavien erottelu nykyisen intialaisen peruspolun ja käyttäjän hyväksymien uusien kriteerien välillä sekä niiden yhdistäminen samaan elokuvarekisteriin.
- **1.0.0 – 2026-11-18:** määriteltiin versioitu kriteerirakenne, ehdotetut kriteeriluokat, include/exclude-arviointi, #66-toimintoviitteet ja tyhjän tuotantokriteeristön hyväksyntäraja.
