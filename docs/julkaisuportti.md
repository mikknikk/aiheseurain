# RSS-raportin julkaisua edeltävä laadunvarmistus

Jokainen RSS-syötteen muutos tarvitsee oman hyväksytyn julkaisuportriraportin ennen PR:n yhdistämistä. Portti koskee kaikkia kymmentä syötettä, myös erillisen näytösvahdin syötettä. Se ei muuta näytösvahdin erillistä ajastusta tai työnjakoa.

## Tarkistuslomakkeen sijainti

Tallenna jokaisen raportin tarkistus JSON-tiedostona polkuun:

`reports/julkaisuportit/{run_id}.json`

Yksi tiedosto koskee yhtä RSS-syötettä. Jos sama PR muuttaa useita syötteitä, jokaiselle syötteelle tarvitaan oma tarkistusraportti. Käytä yksilöllistä ajotunnistetta ja kirjaa tarkistuksen aikaleima aikavyöhykkeineen. `task_id` tarkoittaa `data/feed-catalog.json`-tiedoston syöte-ID:tä, ei lähderekisterin tehtävätunnistetta. Näytösfeedin ID on `intialaisten-elokuvien-naytokset`.

## Tarkistuskohdat

Jokaisella kohdalla on oltava tulos `pass`, `fail` tai `not_applicable`. Ei-soveltuvalle kohdalle kirjoitetaan perustelu. Lähteiden avaamisen, väitteiden vastaavuuden ja riippumattomuuden kohdissa `evidence`-taulukko on pakollinen ja sen pitää sisältää tarkistettavat lähde- tai väiteviitteet. Yksikin `fail` estää hyväksynnän.

| Tunniste | Tarkistettava asia | Luonne |
|---|---|---|
| `sources_opened` | Jokaisen olennaisen väitteen alkuperäinen lähdesivu on avattu ja tarkistettu. Hakutuloskatkelma ei riitä. Lisää näyttöön tarkistetut lähde-URL:t tai lähdetunnisteet. | Toimituksellinen |
| `claim_support` | Raportin väitteet, nimet, luvut ja lainaukset vastaavat lähteitä. Lisää näyttöön väite- ja lähdeviittaukset. | Toimituksellinen |
| `claim_assessments` | Uudessa porttiraportissa jokainen olennainen väite on kuvattu `claim_assessments`-kentässä, sille on valittu sallittu varmennustaso ja lähteille on merkitty katalogin mukainen A–D-luokka, rooli ja riippumattomuus. | Rakenteellinen + toimituksellinen |
| `source_independence` | Vahvistuksiksi lasketut toimitukselliset lähteet ovat aidosti riippumattomia; saman uutistoimiston kopioita tai saman tiedotteen toisintoja ei lasketa erikseen. Lisää näyttöön vertailtujen lähteiden tunnisteet tai URL:t. | Toimituksellinen |
| `uncertainty` | Ristiriidat, epävarmuudet, väitteet ja viralliset ratkaisut erotetaan täsmällisesti. | Toimituksellinen |
| `dates` | Julkaisupäivä, tapahtuma-aika ja lähteen raportointiaika eivät sekoitu. | Toimituksellinen |
| `tracking_period` | Raportin seurantajakso vastaa tehtävän edellistä onnistunutta tarkistusta ja nykyistä päättymisaikaa. | Toimituksellinen |
| `duplicates` | Sama tapahtuma ei toistu ilman olennaista päivitystä; tarvittaessa aiempaan itemiin viitataan. | Toimituksellinen |
| `guid_preservation` | Kaikkien aiempien itemien GUIDit säilyvät muuttumattomina. | Automaattinen |
| `xml_html` | RSS/XML ja kuvauksen HTML ovat rakenteellisesti kelvollisia. | Automaattinen |
| `rss_structure` | GUIDit ovat yksilöllisiä, item-tason `<link>` puuttuu ja koko raportti sekä otsikoitu lähdeluettelo ovat kuvauksessa. | Automaattinen |
| `report_completeness` | Raportissa on otsikko, tarpeelliset päivämäärät, koko uutisartikkeli ja lähdeluettelo suorine lähdelinkkeineen. | Toimituksellinen |
| `accessibility` | Semanttinen HTML, looginen otsikkohierarkia, kuvaavat linkkitekstit, kielimääritykset ja kuvien alt-tekstit on tarkistettu soveltuvin osin. | Toimituksellinen + automaattinen osatarkistus |

## Automaattinen ja toimituksellinen arviointi

GitHub Actions suorittaa ennen PR:n yhdistämistä:
- `python scripts/validate_feeds.py`: XML-, HTML-, GUID-, linkki-, lähdeluettelo-, dokumentaatio- ja tietomallien rakennetarkistukset;
- `python scripts/validate_publication_gate.py`: porttiraportin skeema ja täydellisyys, hyväksyntäpäätös, soveltumattomuuksien perustelut sekä vanhojen GUIDien säilyminen vertaamalla PR:n syötettä kohdehaaraan.

Automaattinen tarkistus ei avaa uutislähteitä eikä todista väitteiden totuutta, lähteiden riippumattomuutta, uutisen uutisarvoa tai toimituksellisen arvion oikeellisuutta. Se tarkistaa vain luokituksen sallitut arvot ja rakenteen. Uusissa porttiraporteissa `claim_assessments` on pakollinen toimituksellinen työvaihe, vaikka skeema sallii kentän puuttumisen vanhoista historiallisista raporteista. Nämä kohdat tekee automaatio lukemalla lähteet ja vertaamalla niitä raporttiin. Porttiraportti on tämän arvioinnin jäljitettävä merkintä, ei koneellinen todiste väitteiden totuudesta.

## Julkaisupäätös ja virhetilanne

1. Muodosta raportti ja tarkista se kaikkia yllä olevia kohtia vasten.
2. Jos yksikin pakollinen kohta hylätään tai jää tarkistamatta, merkitse päätös `rejected`. Älä julkaise RSS-muutosta äläkä siirrä tehtäväkierron vuoroa.
3. Korjaa raportti tai sisältö ja suorita tarkistukset uudelleen. Älä muuta aiempaa onnistunutta tarkistuspistettä epäonnistumisen vuoksi.
4. Kun kaikki kohdat hyväksytään, merkitse päätös `approved` ja sisällytä JSON-porttiraportti samaan PR:ään RSS-muutoksen kanssa.
5. PR:n pakollisen CI-tarkistuksen on onnistuttava. PR:ää ei saa yhdistää, jos portti tai muu validointi epäonnistuu.
6. Vasta yhdistämisen ja main-haaran takaisinlukutarkistuksen jälkeen julkaisu voidaan merkitä onnistuneeksi ja tehtäväkierron vuoro siirtää.

## JSON-esimerkki

Alla on havainnollistava rakenne. Korvaa esimerkkitiedot todellisella ajolla ja arvioi jokainen kohta erikseen.

```json
{
  "schema_version": 1,
  "run_id": "2026-11-17T12-00-00-tolkien",
  "task_id": "tolkien",
  "feed_path": "feeds/tolkien.xml",
  "checked_at": "2026-11-17T12:00:00+02:00",
  "checklist": {
    "sources_opened": {"status": "pass", "note": "Kaikki väitteiden lähteet avattiin.", "evidence": ["lähde-URL-1", "lähde-URL-2"]},
    "claim_support": {"status": "pass", "note": "Väitteet tarkistettiin alkuperäisistä sisällöistä.", "evidence": ["väite 1 → lähde-URL-1"]},
    "source_independence": {"status": "pass", "note": "Vahvistukset ovat eri toimituksista.", "evidence": ["lähde-URL-1", "lähde-URL-2"]},
    "uncertainty": {"status": "pass", "note": "Epävarmuudet ja väitteet on eroteltu."},
    "dates": {"status": "pass", "note": "Julkaisu- ja tapahtuma-ajat on erotettu."},
    "tracking_period": {"status": "pass", "note": "Seurantajakso vastaa edellistä onnistumista."},
    "duplicates": {"status": "pass", "note": "Aiemmat tapahtumat vertailtiin."},
    "guid_preservation": {"status": "pass", "note": "CI vertaa vanhoja ja uusia GUIDeja."},
    "xml_html": {"status": "pass", "note": "CI validoi XML:n ja HTML:n."},
    "rss_structure": {"status": "pass", "note": "CI tarkistaa RSS-rakenteen."},
    "report_completeness": {"status": "pass", "note": "Raportissa on koko sisältö ja lähdeluettelo."},
    "accessibility": {"status": "pass", "note": "Semantiikka, otsikot, linkit, kielet ja alt-tekstit tarkistettu."}
  },
  "claim_assessments": [
    {
      "claim_id": "claim-1",
      "claim": "Tapahtuman järjestäjä vahvisti päivämäärän.",
      "verification_status": "ensisijaislahteella_vahvistettu",
      "sources": [
        {
          "source_id": "ebu",
          "source_class": "A",
          "source_role": "ensisijainen",
          "independence": "ei_sovellu"
        }
      ]
    }
  ],
  "decision": "approved",
  "reviewer_notes": ["Raportti hyväksytty julkaisua varten."]
}
```

Automaattisesti tarkistettavat kolme kohtaa on merkittävä `pass`-tilaan vain, kun ne ovat saman PR:n CI-tarkistusten piirissä. Jos jokin kohta ei sovellu, kirjaa perustelu; automaattisia porttitarkistuksia ei voi ohittaa `not_applicable`-arvolla.
