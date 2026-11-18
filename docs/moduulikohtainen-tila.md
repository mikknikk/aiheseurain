# Moduulikohtainen tila, tarkistuspisteet ja historia

**Versio:** 1.0.1  
**Päiväys:** 2026-11-18  
**Liittyvä tiketti:** [#106 – Eriytä seurantamoduulien tila, tarkistuspisteet ja tapahtumahistoria](https://github.com/mikknikk/aiheseurain/issues/106)

## 1. Tavoite ja omistajuus

Jokaisella moduulilla on oma tilatiedosto data/module-state/{module_id}.json. Se sisältää moduulin viimeisimmän varmennetun onnistumisen checkpointin, checkpoint-historian, linkit moduulin tapahtuma- ja raporttihistoriaan sekä viitteet vanhoihin kanonisiin tietolähteisiin.

Tilatiedosto ei sisällä ajastusta, aikavyöhykettä, ChatGPT-tehtävän tunnistetta, seuraavan tehtävän valintaa, palveluntarjoajaa, mallia, käyttöoikeustunnuksia tai muuta yhteisen suoritusympäristön teknistä tilaa. Nämä pysyvät yhteisessä orkestrointi- ja asetustasossa.

## 2. Tietomalli

| Osa | Sisältö | Omistajuus |
|---|---|---|
| checkpoint.last_successful_run | Viimeisin varmennettu onnistuminen, run_id jos tiedossa, käytetty moduuliversio jos tiedossa, tarkistusaika, seurantajakso ja tulos | Moduuli |
| checkpoint_history | Append-only-loki hyväksytyistä checkpoint-siirtymistä | Moduuli |
| history.document_refs | Viitteet vanhojen dokumenttien aihekohtaisiin historiakohtiin | Moduuli |
| history.event_refs ja current_record_refs | Viitteet rakenteisiin tapahtuma- ja nykytilatietueisiin | Moduuli / tapahtumatyyppi |
| history.source_check_run_refs | Viitteet lähdetarkistusten ajoihin | Yhteinen lähdetarkistusloki, moduuli säilyttää viitteet |
| publication | RSS-syötteen polku ja kaikki migraatiohetkellä olemassa olleet GUID-viitteet | Julkaisukerros, moduuli säilyttää viitteet |
| references | Lähderekisterin, lähdekatalogin, syötekatalogin, lähdetarkistuslokin ja vanhan tilan viitteet | Yhteiset kanoniset tietolähteet |
| migration | Migraation lähtötehtävä, vanhan tilan osoitin ja migraatiopäivä | Migraatiotieto |

## 3. Migroidun lähtötilan rajat

Kymmenestä moduulista kolmella oli data/seurantatila.json-tiedostossa kirjattu viimeisin onnistunut tarkistuspiste:
- Tolkien: tarkistusaika, julkaistujen itemien määrä ja tarkistettujen lähteiden määrä;
- Taylor Swift: vastaavat tiedot sekä yksilöitävä ajotunniste run-history/main-automation-haaran historiasta;
- Intialaisten elokuvien näytösvahti: tarkistusaika, seurantajakso, tulos, julkaistujen itemien määrä ja tarkistettujen lähteiden määrä.

Muiden seitsemän moduulin tarkistusaika ja ajotunniste ovat null, koska niitä ei ollut vanhassa tilatiedostossa. Niille ei ole päätelty ajoa pelkkien RSS-itemien tai lähdetarkistuslokin perusteella. Lähdetarkistuksen run_id ei ole sama asia kuin automaation run_id.

Historiallisten ajojen moduulimäärityksen versiota ei ollut kirjattu, koska moduulimäärittelyt luotiin vasta migraatiossa. Siksi last_successful_run.definition_version on vanhoissa checkpoint-tiedoissa null, vaikka tilatiedoston nykyinen module_definition_version on tiedossa. Aiemman ajon käyttämää moduuliversiota ei saa päätellä jälkikäteen.

Näytösvahtimoduulin checkpoint on migraatiohetken rinnakkaiskuva, ei vanhan automaation jokaisen myöhemmän ajon checkpoint. Niin kauan kuin vanha näytösvahti on käytössä, data/seurantatila.json voi sisältää moduulin migraatiocheckpointia uudemman onnistumisen. Tällainen eteneminen hyväksytään vain, jos lähdetarkistuslokin uusin näytösvahtiajo on complete, sen päättymisaika ja latest_by_task vastaavat vanhaa seurantatilaa, seurantajakso ja lähdemäärä täsmäävät sekä saman ajon julkaisulaadun raportti on hyväksytty. Osittainen tai julkaisematon ajo ei oikeuta etenemiseen. Moduulin checkpoint ja migraatiotapahtuma säilyvät ennallaan, kunnes kirjoitusvastuu siirretään moduuliorchestratorille.

## 4. Historian ja julkaisujen viitteet

- Jokaisen moduulin tilatiedosto sisältää kaikki sen RSS-syötteen GUIDit migraatiohetkellä. GUIDit pysyvät alkuperäisessä muodossaan; niitä ei generoida uudelleen.
- Topic-moduulien aiempi toimituksellinen uutishistoria on edelleen Markdown-dokumenteissa. Tilatiedosto viittaa näiden dokumenttien aihekohtaisiin otsikoihin, mutta ei muunna vapaamuotoista historiaa tekaistuiksi rakenteisiksi tapahtumiksi.
- Näytösvahtimoduuli viittaa kaikkiin 47 nykyiseen historiatapahtumaan ja 111 nykyiseen näytöstietueeseen tiedostossa data/naytosten-muutoshistoria.json. Tiedostoa ei kopioida eikä muokata.
- Kaikki moduulit säilyttävät viitteet omiin lähdetarkistusajoihinsa data/lahdetarkistukset.json-tiedostossa.
- Näytösvahtimoduulin history.source_check_run_refs sisältää kaikki lähdetarkistusajot. Migraation checkpoint_history-tapahtuma säilyttää vain ne lähdeajot, jotka olivat olemassa checkpointin syntyhetkellä.
- Vanha data/seurantatila.json säilyy näytösvahdin ajonaikaisena yhteensopivuuslähteenä, kunnes myöhempi orkestrointivaihe siirtää kirjoitusvastuun erikseen.

## 5. Onnistumisen checkpointin päivityssäännöt

scripts/module_state.py tarjoaa puhtaan commit_successful_checkpoint-funktion. Se palauttaa uuden tilatietueen eikä kirjoita tiedostoja tai käynnistä automaatioita.

Moduulikohtainen checkpoint päivittyy vain, kun kaikki ehdot täyttyvät:
1. ajon tila on succeeded;
2. lähdehaku on kokonainen eikä pakollisia lähteitä ole jäänyt tarkistamatta;
3. julkaisu tai julkaisun muuttumattomuus on erikseen varmennettu;
4. run_id on pysyvä ja yksilöllinen;
5. ajon moduulimäärittelyversio vastaa tilatiedoston nykyistä versiota;
6. tarkistusaika on aikavyöhykkeellinen ja uudempi kuin nykyinen onnistumisen checkpoint;
7. kutsuja antaa odotetun edellisen run_id:n ja tarkistusajan.

Epäonnistunut, osittainen tai julkaisematon moduuliajo palauttaa tilan muuttumattomana. Se ei saa siirtää onnistumisen checkpointia eteenpäin eikä tyhjentää aiempaa onnistunutta tulosta.

Vanhan näytösvahtiautomaation ajot päivittävät edelleen data/seurantatila.json-tiedostoa, eivät passiivista moduulicheckpointia. Migraatiovalidaattori sallii legacy-tilan etenemisen vain täydellisen lähdetarkistusajon ja hyväksytyn julkaisuraportin perusteella. Tämä erottaa vanhan automaation ajohistorian moduulin omasta checkpoint-historiasta.

## 6. Idempotenssi ja rinnakkaisuus

- Sama run_id ja sama sisältö on idempotentti: uusinta ei lisää toista checkpoint-tapahtumaa.
- Sama run_id eri sisällöllä hylätään ristiriitana.
- Jos moduulin checkpoint on muuttunut sen jälkeen, kun ajo luki tilan, vanhentuneella odotetulla checkpointilla tehtävä päivitys hylätään.
- Vanhempi tai samanaikainen tarkistusaika ei voi siirtää checkpointia taaksepäin.
- Tiedoston tallentavan kutsujan tulee käyttää GitHubin sisältötiedoston nykyistä SHA-arvoa optimistisena kirjoituslukituksena. SHA-konfliktin jälkeen tila luetaan uudelleen ja siirtymä lasketaan uudesta tilasta; vanhaa sisältöä ei saa ylikirjoittaa.
- Checkpoint-historia on append-only. Aiempi onnistumistapahtuma säilytetään, vaikka uudempi checkpoint lisätään.

## 7. Validointi

Migraation eheys tarkistetaan komennolla:

    python -m scripts.validate_module_state

Validaattori vertaa moduulikohtaisia tiloja vanhaan seurantatilaan, lähdetarkistuslokiin, moduulirekisteriin, RSS-syötteiden GUIDeihin ja näytöshistorian tunnisteisiin. Se tarkistaa myös dokumenttiviitteiden olemassaolon ja otsikot. Näytösvahtimoduulin legacy-tilan checkpointia uudempi onnistuminen hyväksytään vain, jos uusin lähdetarkistusajo on complete, sen aikaleimat ja seurantajakso täsmäävät, tarkistettujen lähteiden määrä vastaa tilaa ja samaan ajoon sidottu julkaisulaadun raportti on approved.

Yksikkötestit kattavat täydellisen migraation, tuntemattomien tietojen säilyttämisen, onnistuneen checkpointin, epäonnistuneen ja osittaisen ajon, idempotenssin, ristiriitaisen run_id:n, vanhentuneen rinnakkaispäivityksen, aikajärjestyksen ja aikavyöhykkeen pakollisuuden.

## 8. Käyttöönoton rajat

Tämä vaihe luo kymmenen moduulikohtaista tilatiedostoa ja turvallisen päivityssopimuksen. Moduulit pysyvät inactive-tilassa. Vanha näytösvahtiautomaatio jatkaa kuitenkin yhteensopivuustilansa ja lähdetarkistuslokinsa päivittämistä, kunnes #108:n mukainen orkestrointi siirtää kirjoitusvastuun erikseen. Tällöin moduulin migraatiocheckpointia ei muuteta eikä vanhaa automaatiota merkitä moduuliajon suoritukseksi.

Uusi tila on migroitu rinnakkaiskuva ja päivitysrajapinnan perusta. Sen muuttaminen tuotannon ainoaksi kirjoituskohteeksi tapahtuu vasta #108:n yhteydessä, kun orkestrointi, palautuminen ja rinnakkaisten ajojen hallinta on hyväksytty. Palveluntarjoajien valinta on erillinen tekninen asetuskokonaisuus, jota käsitellään [palveluadapterien dokumentissa](palveluadapterit.md).

## Muutoshistoria

- **1.0.1 – 2026-11-18:** täsmennettiin migraatiocheckpointin ja edelleen käytössä olevan näytösvahtiautomaation legacy-tilan erillinen omistajuus sekä lähdelokiin ja julkaisuraporttiin sidottu hyväksytty etenemissääntö.
- **1.0.0 – 2026-11-18:** määriteltiin moduulikohtainen checkpoint, append-only-checkpoint-historia, vanhojen tietojen ja GUIDien viitteet sekä idempotentti ja rinnakkaisuutta suojaava päivityssopimus.
