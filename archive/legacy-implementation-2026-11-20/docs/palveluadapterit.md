# Tekoäly- ja tutkimuspalvelujen adapterisopimukset

**Versio:** 1.0.0  
**Päiväys:** 2026-11-18  
**Liittyvä tiketti:** [#107 – Määrittele ja toteuta tekoäly- ja tutkimuspalvelujen adapterisopimukset](https://github.com/mikknikk/aiheseurain/issues/107)

## 1. Periaate

Aiheseuraimen moduuli määrittelee seurattavan aiheen, hakuprofiilit, lähdeviitteet ja toimitukselliset vaatimukset. Se ei valitse tekoälymallia, tutkimuspalvelua, palveluntarjoajaa, tunnistautumistapaa tai reititystä.

Yhteinen ydin käyttää kahta erillistä sopimusta:
- **AIProcessor** käsittelee toimitettua aineistoa ja tuottaa normalisoidun tuloksen.
- **ResearchProvider** hakee lähteitä ja avaa lähteitä lähdetunnisteellä.

Tekninen reititys sijaitsee data/provider-routing.json-tiedostossa. Moduulimäärittelyjä tai moduulikohtaisia tiloja ei tarvitse muuttaa, kun palveluntarjoaja vaihdetaan.

## 2. AIProcessor-sopimus

AIRequest sisältää moduulin ja ajon tunnisteet, käsiteltävän sisällön, lähdeviitteet, tuloskielen ja vaaditut kyvykkyydet. AIResult palauttaa sisällön, kaikki alkuperäiset lähdeviitteet, epävarmuusluokan, kustannusarvion ja mahdolliset huomautukset.

Tulos ei saa kadottaa pyynnön lähdeviitteitä. Epävarmuusluokka on low, medium, high tai unknown. Tekoälyn tuottama teksti ei itsessään muuta lähteen vahvistusluokkaa eikä tee väitteestä virallisesti vahvistettua.

## 3. ResearchProvider-sopimus

ResearchQuery sisältää moduulin ja ajon tunnisteet, hakutermit, kielet, alueet, sallitut source_id-tunnisteet ja tulosrajan. ResearchResult palauttaa lähteet, haun kattavuustiedon, epäonnistuneiden lähteiden tunnisteet ja kustannusarvion.

ResearchSource säilyttää vähintään:
- yhteisen lähdekatalogin source_id-tunnisteen ja alkuperäisen URL-osoitteen;
- otsikon, katkelman, kielen ja alueen;
- lähdekatalogin A–D-luotettavuusluokan;
- väitteen vahvistustason (officially_confirmed, media_reported, unconfirmed_rumor tai unknown);
- tarkistusajan aikavyöhykkeineen ja mahdollisen julkaisupäivän.

Adapteri ei saa palauttaa pyydetyn lähderekisterin ulkopuolisia lähteitä, jos pyyntö rajaa sallitut source_id-tunnisteet.

## 4. Reititys ja kyvykkyydet

data/provider-routing.json erottaa palveluntarjoajien tekniset asetukset moduulien sisällöstä. Reitti voi valita AIProcessorin ja ResearchProviderin moduulikohtaisesti tai yhteisen oletusreitin kautta. Reititin tarkistaa:
- palveluntarjoajan tyypin ja aktiivisuuden;
- rekisteröidyn adapterin ja sen adapter_id-tunnisteen;
- moduulin vaatimat kyvykkyydet sekä konfiguraatiossa että adapterissa;
- palvelun aikakatkaisun, uusintakäytännön ja ajokohtaisen kustannusrajan.

Sopimusversiot ovat erillisiä moduulimääritysten versioista. Adapterin vaihtaminen ei muuta moduulin sisältöä tai moduulikohtaista tilaa.

## 5. Virheenkäsittely

| Virhe | Automaattinen uusinta | Käsittely |
|---|---|---|
| Aikakatkaisu | Kyllä, rajatusti | Uusinta enimmäisyritysten ja viiverajan puitteissa |
| Palvelu tilapäisesti poissa | Kyllä, rajatusti | Eksponentiaalinen viive |
| Rate limit | Kyllä, jos retry-after mahtuu enimmäisviiveeseen | Palvelun ilmoittamaa odotusaikaa noudatetaan |
| Tunnistautumisvirhe | Ei | Pysäytä palvelukutsu; älä paljasta tunnuksia |
| Sopimusrikkomus | Ei | Hylkää vastaus |
| Kustannusraja | Ei | Estä kutsu ennen suorittamista, jos arvio ylittää jäljellä olevan budjetin |

Uusintayritysten määrä ja viiveet ovat rajattuja. Aikakatkaisu välitetään adapterille eksplisiittisenä parametrina. Kustannusarvio tarkistetaan ennen kutsua ja toteutunut kustannus kirjataan ajon budjettiin.

## 6. Tietoturva ja auditointi

Reitityskonfiguraatio saa sisältää vain ympäristömuuttujien nimiä credential_env-kentässä. API-avaimia, salasanoja, tokeneita tai niiden arvoja ei tallenneta JSON-tiedostoihin, moduulimäärittelyihin tai auditointimerkintöihin.

ProviderCallRecord sisältää moduulin ja ajon tunnisteen, palveluntarjoajan tunnisteen, tyypin, onnistumis-/virhetilan, yritysten määrän, kustannusarvion ja virhekoodin. Se ei sisällä pyyntötekstiä, lähdekatkelmia, tunnuksia tai vastausten sisältöä.

## 7. Testiadapterit ja nykyinen käyttöönotto

scripts/providers/testing.py sisältää kaksi determinististä AIProcessor-testitoteutusta ja kaksi ResearchProvider-testitoteutusta. Ne eivät käytä verkkoa, tunnuksia tai ulkoisia palveluja. Testit kattavat reitityksen, lähdeviitteiden säilymisen, epävarmuuden, aikakatkaisun, rate limitin, tunnistautumisvirheen, kustannusrajan, kyvykkyydet ja auditointitietojen minimoinnin.

Tuotannon data/provider-routing.json on tarkoituksella tyhjä: providers-lista ja routes-kartta ovat tyhjiä eikä oletusreittiä ole. Yhtään todellista palveluntarjoajaa tai mallia ei ole aktivoitu.

Tämä ei vielä integroi GitHub Actionsia tai ChatGPT-ajastettuja tehtäviä kutsumaan tiettyä mallia. Nykyinen ChatGPT-keskustelu ei ole repositorion koodille käytettävissä oleva yleinen API-palvelu. Todellinen palveluadapteri vaatii erillisen toteutuksen, hyväksytyn palvelun, tunnusten turvallisen välityksen ja erillisen käyttöönoton. Tämän tiketin testiadapterit osoittavat sopimusten vaihdettavuuden, eivät tuotantoyhteyttä.

## 8. Validointi

Tuotannon reitityskonfiguraatio tarkistetaan komennolla:

    python -m scripts.validate_provider_routing

Yksikkötestit suoritetaan tavallisessa unittest discover -ajossa. Konfiguraatioskeema estää tuntemattomat kentät, kuten api_key, sekä tunnusarvojen tallentamisen credential_env-kenttään.

## Muutoshistoria

- **1.0.0 – 2026-11-18:** määriteltiin AIProcessor- ja ResearchProvider-sopimukset, tekninen reititys, kustannusrajat, rajatut uusinnat, auditointitietojen minimointi ja kaksi testiadapteria kummallekin sopimukselle.
