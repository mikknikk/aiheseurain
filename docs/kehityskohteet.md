# Uutisseurannan kehityskohteet

Tämä dokumentti on repositorion kehitystyön ajantasainen työlista. Se erottaa jo toteutetut parannukset avoimista tehtävistä ja auttaa valitsemaan seuraavan työn ilman, että valmiita asioita ehdotetaan uudelleen.

Päivitä tätä tiedostoa aina, kun kehityskohde valmistuu, muuttuu tai sen prioriteetti vaihtuu. Älä merkitse tehtävää valmiiksi pelkän suunnitelman tai osittaisen toteutuksen perusteella. Yksittäisten tehtävien ensisijaiset tilat ovat GitHub Issues -tiketeissä.

## Nykyinen kehitystilanne

- **#29 – Pages-kartoitus ja Valvomon tietomalli:** valmis ja yhdistetty `main`-haaraan.
- **#30 – Valvomon vähimmäisversio:** valmis ja yhdistetty `main`-haaraan.
- **#38 – Valvomon siirto omalle sivulleen:** valmis ja yhdistetty.
- **#31 – RSS-lukijan vähimmäisversio:** valmis ja yhdistetty.
- **#35 – GitHub Issues -pohjainen Kehitysjonon kanban:** valmis ja yhdistetty.
- **#83 – Kehitysjonon aineiston muodostus Actionsissa ja Pages-julkaisu:** toteutuksessa.

Tarkat tilat ja prioriteetit tarkistetaan aina GitHub Issues -tiketeistä, ei tästä yhteenvedosta.

## Nykyinen moduulisiirtymän kehitysvaihe

- **#102 – Seurantamoduulin tietosopimus:** valmis ja yhdistetty.
- **#103 – Moduulirekisteri ja määritysten lataus:** valmis; PR #111 yhdistetty.
- **#104 – Nykyisten aiheiden ja prosessien hallittu moduulisiirtymä:** valmis ja yhdistetty PR:ssä #112.
- **#109 – Yleinen tapahtumavahti:** valmis; PR:t #113 ja #114 yhdistetty. Yhteinen käsittelyydin, lähdeadapterirajapinta, näytösvahtisovitin ja konferenssiesityksen testitapaus ovat käytettävissä.
- **#105 – Nykyisten aiheiden ja näytösvahdin siirto moduuleiksi:** valmis ja yhdistetty PR:ssä #115.
- **#106 – Moduulikohtainen tila ja historia:** valmis ja yhdistetty PR:ssä #116.
- **#107 – AI- ja tutkimuspalvelujen adapterisopimukset:** valmis ja yhdistetty PR:ssä #117. AIProcessor- ja ResearchProvider-sopimukset, tekninen reititin, rajatut uusinnat, kustannusrajat ja deterministiset testiadapterit ovat käytettävissä.
- **#108 – Yhteinen moduulien suoritusorkestrointi:** valmis; PR:t #118 ja #124 yhdistetty. Suorituspyynnön ja tuloksen sopimukset, varjotila, tuotannon erillinen hyväksyntäportti, elinkaaren koordinointi, tapahtumavahtisuorittaja sekä paikalliset tallennus- ja julkaisusovittimet ovat käytettävissä. Tuotantokäyttöönotto on erillinen hyväksyttävä päätös.
- **#120 – Orkestroinnin pysyvät tallennus-, julkaisu- ja ajotulosadapterit:** valmis; PR #124 yhdistetty. Paikalliset SHA-tarkistetut moduulitila- ja artefaktisovittimet, tietosuojattu ajotulosloki, idempotentti RSS-julkaisusovitin sekä rakenteellinen laadunvarmistusportti on testattu eristetyissä väliaikaishakemistoissa.
- **#66 – Elokuvahavaintorekisteri ja kriteerikohtaiset jatkotoimet:** valmis; PR:t #127 ja #128 yhdistetty. Elokuvatason rekisteri viittaa #109:n kanonisiin näytöstapahtumiin, säilyttää kriteeriosumat ja reitittää testitoiminnot outboxiin. Tuotannon kriteerit ja Discord-konfiguraatio ovat tyhjiä.
- **#67 – Käyttäjän hyväksymä elokuvien hakukriteeristö:** tekninen toteutus valmis; PR #131 yhdistetty. Kriteeriskeema, versioitu arviointimoottori, include/exclude-logiikka, #66-integraatio ja toimintoviitteiden validointi ovat käytössä. Tiketti odottaa käyttäjän päätöksiä varsinaisista seurattavista kohteista ja rajauksista; tuotannon kriteeritiedosto pysyy tyhjänä.

Yksittäisten tikettien kanoninen tila ja riippuvuudet tarkistetaan GitHub Issues -tiketeistä.

## Tavoitetila

Uutisseurannan tulee olla luotettava, läpinäkyvä, saavutettava ja ylläpidettävä. Sen on säilytettävä eri aiheet erillään, osoitettava uutisten lähteet ja seurantajaksot sekä havaittava rakenteelliset virheet automaattisesti. Kehityksessä suositaan pieniä, testattavia muutoksia. Uudet ja muutetut skriptit kommentoidaan suomeksi vähintään `scripts/validate_feeds.py`-tiedoston tasoisesti; tarkempi sääntö on [kehityskäytännöissä](kehityskaytannot.md).

## Toteutetut kohteet

- [x] **Moduulikohtainen tila ja historia (#106).** Kymmenen tilatiedostoa, vanhojen checkpointien ja historiaviitteiden migraatio sekä idempotentti, osittaisia ajoja hylkäävä checkpoint-siirtymä.
- [x] **Nykyisten aiheiden ja näytösvahdin siirto itsenäisiin moduulimäärittelyihin (#105).** Yhdeksän topic-moduulia ja yksi process-moduuli on rekisteröity inactive-tilassa. Lähdeviitteet, kieli- ja alueprofiilit sekä näytösvahtimoduulin tapahtumatyyppi validoidaan CI:ssä.
- [x] **Yhteinen moduulien suoritusorkestrointi (#108).** PR #118 toteuttaa suorituspyynnön ja tuloksen, moduulin ratkaisun rekisteristä, suorittajan ja laadunvarmistusportin koordinoinnin, varjotilan, tuotannon erillisen hyväksyntäportin, tapahtumavahtisuorittimen ja moduulikohtaisen virheiden eristyksen. PR #124 täydentää elinkaaren paikallisilla SHA-tarkistetuilla tallennus- ja julkaisusovittimilla. Tuotantokäyttöönottoa tai automaatioasetusten muutoksia ei tehty.
- [x] **Orkestroinnin paikalliset tallennus- ja julkaisusovittimet (#120).** Moduulitilan ja artefaktien tallennus käyttää SHA-vertailua, prosessilukkoa ja atomista kirjoitusta. Ajotulosloki jättää raporttisisällön ja salaisuudet pois. Eristetty RSS-julkaisija säilyttää aiemmat GUIDit, torjuu ristiriitaiset uusinnat ja lukee XML:n takaisin. Rakenteellinen laadunvarmistussovitin estää puutteellisen suorittajatuloksen julkaisun. Testit käyttävät väliaikaishakemistoja.

- [x] **Yleinen tapahtumavahti (#109).** PR:t #113 ja #114 toteuttavat tapahtumatyypin ja historian skeemat, yleisen käsittelyytimen, lähdesovittimen rajapinnan, täsmällisen identiteettipohjaisen duplikaattien yhdistämisen, ristiriitojen säilyttämisen, tilasiirtymät sekä näytöshistorian lukevan ja muistissa tapahtumia käsittelevän sovittimen. Konferenssiesitys on toinen tapahtumatyyppi. Tuotannon näytösvahtia tai automaatioasetuksia ei vaihdettu.

- [x] **Nykyisten moduulien inventaario ja hallitun siirtymän suunnitelma (#104).** Dokumentti `docs/moduulisiirtyman-inventaario.md` kuvaa yhdeksän uutisaiheen ja erillisen näytösvahdin moduulijaon, lähderekisterien kieli- ja aluekattavuuden, tiedostojen siirtokartan, omistajuusrajat, päällekkäisyysriskit sekä vaiheittaisen palautusmenettelyn. PR #112 on yhdistetty.

- [x] **Uutislähteiden ja uutisväitteiden luotettavuusluokitus (#27).** Yhteinen A–D-lähdeluokitus tallennetaan lähdekatalogiin ja kuusi väitekohtaista varmennustasoa kirjataan uusien julkaisulaadun porttiraporttien claim_assessments-kenttään. Ohjeet erottavat lähteen yleisen roolin väitteen näytöstä sekä kuvaavat lähderiippuvuudet, anonyymit lähteet, ristiriidat, sidonnaisuudet ja korjaukset. Skeemat ja rakennetestit tarkistavat sallitut arvot; ne eivät väitä todistavansa uutisten totuutta.

- [x] **Pääautomaation ohjeiden ulkoistus ja versiohistoria.** Pääautomaation koko tehtävä- ja toimintakuvaus on siirretty tiedostoon `docs/paaautomaation-ohje.md`. ChatGPT-automaation kehote on lyhyt käynnistysosoite. `data/seurantatila.json` tallentaa nykyisen ohjeversion sekä viimeisimmän onnistuneen ajon käyttämän version ja ajan; GitHub Actions tarkistaa versioiden yhdenmukaisuuden.

- [x] **Näytösvahdin ohjeiden ulkoistus ja versiohistoria.** Näytösvahdin täydellinen tehtäväohje on versionhallittu tiedostossa `docs/intialaisten-elokuvien-naytosseuranta.md`. Automaation kehote on lyhyt käynnistysosoite, ja `data/seurantatila.json` tallentaa ohjeversion sekä viimeisimmän onnistuneen ajon version ja ajan.
- [x] **Viikoittaisen laatutarkistuksen ohjeiden ulkoistus ja versiohistoria.** Laatutarkistuksen täydellinen käsikirja on `docs/laatutarkistuksen-ohje.md`. Automaation kehote on lyhyt käynnistysosoite. Käsikirjan versio ja viimeisin onnistunut tarkistusaika kirjataan koneelliseen seurantatilaan; auditointi ei korjaa havaintoja.
- [x] **Koneellisesti luettava seurantatila.** `data/seurantatila.json` tallentaa yhdeksän aihekierroksen tehtävän ja erillisen näytösvahdin tilaa. Tuntemattomia vanhoja tarkistusaikoja ei täytetä arvauksilla.
- [x] **Automaattiset GitHub Actions -laatutestit.** `.github/workflows/validate-feeds.yml` suorittaa tarkistukset push- ja pull request -muutoksissa.
- [x] **RSS-syötteiden rakennetarkistukset.** Kaikkien kymmenen syötteen XML, GUIDien olemassaolo ja yksilöllisyys, item-tason `<link>`-elementtien kielto ja CDATA-kuvaukset tarkistetaan.
- [x] **RSS-kuvausten HTML-tarkistukset.** Testataan muun muassa elementtien sulkeutuminen, linkkien HTTP(S)-osoitteet, otsikkotasojen järjestys ja kuvien vaihtoehtotekstit.
- [x] **Dokumentaation ja seurantatilan yhdenmukaisuustestit.** Testi vertaa README:n syötetaulukkoa, tehtäväjonon yhdeksää tehtävää ja JSON-tilatiedoston kiertojärjestystä sekä tarkistaa seurantajaksojen aikaleimojen aikavyöhykkeet ja näytösvahdin erillisyyden.
- [x] **Käynnistyskehotteiden tunnistevarmistus.** Jokaisella kolmella automaatiolla on yksilöllinen prompt-tunniste, joka täsmäytetään `data/seurantatila.json`-tiedostoon ajon alussa ja GitHub Actionsin validoinnissa. Tunnisteen vaihto ja JSON-päivitys tehdään aina yhdessä; live-asetukset kopioidaan edelleen manuaalisesti.
- [x] **Markdown-dokumentaation käytännöt ja automaatioiden käynnistyskehotteiden keskittäminen.** Dokumentaation luokat, rakenteen vähimmäisvaatimukset ja Markdown-saavutettavuus on määritelty `docs/kehityskaytannot.md`- ja `docs/saavutettavuus.md`-tiedostoissa. Kolmen `mikknikk/aiheseurain`-automaation kanoniset käynnistyskehotteet on koottu `prompts/`-hakemistoon sellaisinaan kopioitaviksi tekstitiedostoiksi.
- [x] **Aloittelijaystävällinen skriptidokumentointi.** `scripts/validate_feeds.py` sisältää suomenkieliset docstring-kuvaukset ja kommentit, jotka selittävät myös Pythonia vähemmän osaavalle lukijalle keskeisen toiminnan.
- [x] **Uusien skriptien kommentointisääntö.** `docs/kehityskaytannot.md`, README ja tämä kehityskohdelista edellyttävät, että kaikki uudet skriptit kommentoidaan vastaavalla perusteellisuudella ja kommentit pidetään ajan tasalla.
- [x] **Näytösseurannan muutoshistorian tietomalli ja JSON Schema -validointi.** `data/naytosten-muutoshistoria.json` erottaa näytösten nykytilan append-only-tapahtumalokista. `schemas/naytosten-muutoshistoria.schema.json` määrittelee rakenteen JSON Schema Draft 2020-12 -muodossa. `scripts/validate_feeds.py` suorittaa skeemavalidoinnin ja täydentää sitä projektikohtaisilla eheystarkistuksilla; GitHub Actions asentaa `requirements.txt`-tiedoston riippuvuudet ennen testejä.
- [x] **Näytösvahdin virheistä palautuminen.** Käsikirjan versio 1.2.0 määrittelee enintään kolme yritystä tilapäisille luku-/kirjoitusvirheille, epäselvän GitHub-kirjoituksen takaisinluvun ennen uusintaa, atomisen PR-julkaisun sekä edellisestä onnistuneesta tarkistuspisteestä alkavan palautumisjakson. Epäonnistunut ajo ei siirrä onnistumisaikaleimaa eikä korvaa toimivaa RSS:ää.

- [x] **Raporttikohtainen RSS-julkaisulaadun portti (#53).** Jokaiselle muuttuneelle syötteelle vaaditaan JSON-tarkistusraportti. CI tarkistaa raportin skeeman, hylkäykset, soveltumattomuuksien perustelut ja aiempien GUIDien säilymisen; uutisväitteiden totuutta tai lähteiden riippumattomuutta ei väitetä automaattisesti todennetuiksi. Epäonnistuneen portin raportti säilyy PR:ssä ja CI-artefaktissa, eikä viimeisintä onnistunutta tarkistuspistettä tai tehtäväkiertoa muuteta.

## Avoimet kehityskohteet

### Tuotantopalvelujen käyttöönotto (erillinen päätös)

Tiketin #107 AIProcessor- ja ResearchProvider-sopimukset, tekninen reititin, kustannusrajat, aikakatkaisut, uusinnat ja auditointi ovat valmiit. Tuotannon reitityskonfiguraatio on edelleen tyhjä eikä testiadaptereissa käytetä verkkoa tai tunnuksia. Todellisen palveluntarjoajan, GitHub-pohjaisen tallennuksen, tuotantojulkaisun ja automaatiokytkennän käyttöönotto vaatii erillisen teknisen suunnitelman ja käyttäjän hyväksynnän.

### Näytösseurannan muutoshistorian käyttöönotto

**Valmis:** ensimmäinen varmennettu lähtötilanne muodostettiin 16.11.2026. `baseline_status` on `active`, ja nykytila sekä tapahtumaloki ovat käytössä. Jatkuva seuranta varmistaa käytännössä uusien muutostyyppien ja takaisinluvun toiminnan.

### Prioriteetti 2 – lähteiden kattavuuden seuranta

**Tavoite:** pystyä arvioimaan, mitä lähteitä ja alueita kunkin aiheen tarkistuksessa todella käytiin läpi.

- [x] Yhteinen lähdekatalogi `data/source-catalog.json`: 122 yksilöllisen lähteen yhteiset perustiedot ylläpidetään kerran; aihekohtaiset käyttöasetukset ovat erillisissä rekistereissä.
- [x] Kymmenen tehtäväkohtaista käyttörekisteriä `data/sources/`-hakemistossa. Ne viittaavat katalogin lähteisiin `source_id`-kentällä ja säilyttävät kriittisyyden, tarkistusajan ja käyttörajoitteen tehtäväkohtaisina; uutis- ja näytösseuranta ovat erillisiä.
- [x] Ajokohtainen lähdetarkistusloki `data/lahdetarkistukset.json` erottaa tarkistetut lähteet ja tarkistamatta jääneet lähteet syineen. Varsinaiset automaatioajot eivät ole vielä tuottaneet lokihistoriaa.
- [x] Ajolokin tietomalli edellyttää tarkistamatta jääneelle lähteelle syyn. Raportointikäytäntö on lisätty molempiin automaatio-ohjeisiin.
- [x] Tee ensimmäinen aihekohtainen kieli- ja maantieteellisen kattavuuden kartoitus ja kirjaa puutteet docs/lahteet.md:hen. Katalogissa on nyt 122 yksilöllistä lähdettä ja käyttörekistereissä yhteensä 131 aihekohtaista lähdekäyttöä. Tolkienin käyttörekisterissä on 28 lähdeviittausta.
- [ ] Täydennä jatkossa tunnistettuja aukkoja (esim. Tolkienin Itä-Euroopan, Aasian ja muun Latinalaisen Amerikan toimitukselliset lähteet; Taylor Swiftin muut kuin englanninkieliset lähteet; Wakaliwoodin paikalliskielet; Euroviisujen kansalliset yleisradioyhtiöt; shakin Aasian/Afrikan/Latinalaisen Amerikan lähteet). Älä tulkitse lähteiden lukumäärää yksin kattavuuden mittariksi.
- [x] Erilliset JSON Schema -skeemat ja CI-validointi tarkistavat katalogin, käyttörekisterien viittaukset sekä tehtäväkohtaisen ajolokin eheyden.

**Jäljellä:** katalogi ja kymmenen tehtäväkohtaista käyttörekisteriä on toteutettu, ja ensimmäinen kattavuusaukkojen arvio on dokumentoitu. Lähdeluettelo ei ole vielä tyhjentävä; alueellisia aukkoja täydennetään käytännön seurannassa. Automaatiokehotteet on päivitetty, mutta uudet kirjaukset ja kattavuus on vielä todennettava oikeissa ajoissa. Kohdetta ei merkitä valmiiksi ennen kuin ajolokiin syntyy käyttökelpoisia merkintöjä.

**Ensimmäisen näytösvahtiajon rajaus:** 16.11.2026 tehty lähtötilanneajo käytti käsikirjan versiota 1.0.0. Nykyinen tehtäväkohtainen lähderekisteri ja ajolokin kirjaamissäännöt otettiin käyttöön vasta myöhemmässä muutoksessa. Ajon raporttiin kirjattu `sources_checked: 17` ei sisällä lähde-ID-kohtaista erittelyä, joten sitä ei voi muuntaa jälkikäteen luotettavaksi ajolokimerkinnäksi. `data/lahdetarkistukset.json` jätetään siksi tyhjäksi, kunnes uusi ajo tuottaa todennettavat lähde-ID:t. Seuraava näytösvahtiajo on ensimmäinen testi nykyiselle lokitukselle.

**Valmistumiskriteeri:** jokaisesta raportista voidaan jälkikäteen nähdä, mitä lähteitä tarkistettiin ja mitkä olennaiset lähteet jäivät tavoittamatta.

### Prioriteetti 3 – uutisten luotettavuusluokituksen täsmennys

**Tavoite:** tehdä uutisraporttien luotettavuusmerkinnöistä yhdenmukaisia ja perusteltuja.

- [ ] Määritä selkeät luokat ja niiden kriteerit, esimerkiksi vahvistettu ensisijaislähteellä, useasta riippumattomasta toimituksellisesta lähteestä varmennettu, yhden luotettavan lähteen tieto ja vahvistamaton/epävarma.
- [ ] Erota lähteen luotettavuus yksittäisen väitteen varmistumisesta. Virallinen lähde voi vahvistaa oman ilmoituksensa, mutta ei välttämättä kaikkia siihen liittyviä väitteitä.
- [ ] Määritä, miten ristiriitaiset lähteet, nimettömät lähteet, huhut ja nopeasti muuttuvat tiedot käsitellään.
- [ ] Lisää luokitusohje yleisiin julkaisuperiaatteisiin ja aihekohtaisiin ohjeisiin.
- [ ] Lisää testejä, jotka tarkistavat luokituksen pakollisen esitystavan, mutta eivät yritä koneellisesti päätellä väitteen totuutta.

**Valmistumiskriteeri:** lukija ymmärtää jokaisen luokan merkityksen ja sen, mihin varmennus perustuu. Luokitusta ei esitetä näennäisenä numeerisena tarkkuutena.

### Prioriteetti 4 – linkkien toimivuuden seuranta

**Toteutettu ensimmäinen versio:** `scripts/check_links.py` tarkistaa lähdekatalogin URL:t sekä kaikkien RSS-syötteiden kanava- ja artikkelilinkit. Erillinen `.github/workflows/check-links.yml` suorittaa tarkistuksen viikoittain ja käsin käynnistettäessä. Raportti tallennetaan GitHub Actions -artefaktiksi; tavallinen RSS:n CI ei tee verkkopyyntöjä ulkoisiin lähteisiin.

- [x] Tarkista lähdekatalogin ja RSS-syötteiden linkit erillisessä työnkulussa.
- [x] Erota uudelleenohjaukset, 401/403-estot, 429-nopeusrajat, 5xx-palvelinvirheet ja verkkovirheet selvistä 404/410-virheistä.
- [x] Raportoi tulokset muuttamatta lähdeosoitteita automaattisesti.
- [ ] Seuraa ensimmäisten viikoittaisten ajojen tuloksia ja säädä tarvittaessa poikkeusten käsittelyä.

**Jäljellä:** toteutus on valmis testattavaksi CI:ssä ja ensimmäisissä ajastetuissa ajoissa. Linkkien nykytilaa ei ole vielä mitattu tällä uudella tarkistimella.

**Valmistumiskriteeri:** linkkiongelmat havaitaan ja raportoidaan, mutta tilapäiset verkkohäiriöt eivät aiheuta vääriä laatuhälytyksiä.

### Prioriteetti 5 – saavutettavuuden testauksen syventäminen

**Toteutettu valmistelu:** `docs/saavutettavuus.md` sisältää manuaalisen testauksen menettelyn, ympäristöjen kirjausohjeet ja täytettävän testipohjan.

- [x] Määritä menettely näppäimistö-, ruudunlukija-, suurennus-, mobiili-, kontrasti- ja väritestaukselle.
- [x] Lisää ympäristöjen, löydösten ja tulosten kirjauspohja.
- [ ] Tee dokumentoitu manuaalinen testaus näppäimistöllä, ruudunlukijalla, suurennuksella, kapealla näkymällä ja pakotetuilla väreillä.
- [ ] Tarkista värikontrastit WCAG 2.2 AAA -tavoitteiden mukaisesti kaikissa käyttöliittymätiloissa, joissa sisältöä esitetään.
- [ ] Kirjaa todelliset testitulokset ja korjaukset saavutettavuusdokumenttiin.
- [x] Pidä automaattiset HTML-rakennetestit erillään varsinaisesta WCAG-arvioinnista.

**Jäljellä:** manuaalista testausta ei ole vielä tehty. Testauspohjan lisääminen ei ole testitulos, eikä AAA-tasoa väitetä.

**Valmistumiskriteeri:** saavutettavuuden tila perustuu dokumentoituihin testeihin. AAA-tasoa ei väitetä ennen kuin soveltuvat vaatimukset on arvioitu.

## Suositeltu toteutusjärjestys

1. Näytösseurannan muutoshistorian tietomalli ja dokumentointi.
2. Lähderekisterien yhdenmukaistaminen ja lähdekattavuuden raportointi.
3. Uutisten luotettavuusluokkien määrittely ja ohjeistus.
4. Linkkien toimivuuden erillinen seuranta.
5. Saavutettavuuden manuaalinen testaus ja tulosten kirjaaminen.

Järjestystä voi muuttaa, jos seurannan käytännön ongelmat tai käyttäjän prioriteetit sitä edellyttävät. Älä kuitenkaan laajenna järjestelmää tarpeettomasti: jokaisen uuden tiedoston, automaation ja testin pitää ratkaista tunnistettu ylläpito- tai luotettavuusongelma.

## Rajaukset ja rehellinen raportointi

- Automaattisten testien läpäisy osoittaa vain testattujen rakenteellisten ehtojen täyttymisen. Se ei todista uutisväitteiden paikkansapitävyyttä, lähteiden riippumattomuutta, linkkien toimivuutta tai WCAG 2.2 AAA -vaatimusten täyttymistä.
- Älä lisää erillisiä aihekohtaisia automaatioita. Nykyinen yhdeksän tehtävän kierto ja siitä riippumaton päivittäinen näytösvahti säilyvät.
- Säilytä RSS-syötteiden vanhat itemit ja GUIDit. Älä lisää tyhjiä tai keinotekoisia uutisartikkeleita.
- Kaikissa raporteissa ilmoitetaan tehtäväkohtaisen seurantajakson alku ja loppu Europe/Helsinki-ajassa. Tuntemattomia aikoja ei arvata.
- Kaikki uudet skriptit kommentoidaan suomeksi vastaavalla perusteellisuudella kuin `scripts/validate_feeds.py`; noudata [kehityskäytäntöjä](kehityskaytannot.md).


### Prioriteetti 6 – julkinen valvomo ja RSS-lukija

**Tavoite:** rakentaa GitHub Pagesiin yhteinen käyttöliittymä, jossa voi seurata automaatioiden etenemistä ja lukea kaikkia repositorion RSS-syötteitä. Tekninen tavoitekuvaus, turvallisuusrajaukset, hyväksymiskriteerit ja vaiheistus ovat dokumentissa [julkinen valvomo ja RSS-lukija](julkinen-valvomo-ja-rss-lukija.md).

**Tila:** tietomallin ja Pages-julkaisun kartoitus (#29) on valmis. Valvomon vähimmäisversio (#30) on yhdistetty. Valvomon erottaminen omalle sivulleen (#38) on valmis ja yhdistetty; RSS-lukija (#31) ja Kehitysjonon kanban (#35) on toteutettu. Kehitysjonon selainkohtaisten API-hakujen korvaaminen Actionsissa muodostetulla aineistolla on käynnissä tiketissä #83.

- [x] Kirjaa tavoitearkkitehtuuri: yksi staattinen Pages-sivusto, valvomo ja RSS-lukija erillisinä osioina.
- [x] Määrittele valvomon näyttämät automaatiot, ajovaiheet, aihekierroksen eteneminen, lähdekattavuuden käsitteet sekä virhe- ja varoitushistoria.
- [x] Määrittele RSS-lukijan perustoiminnot, suodatus, lukutila ja HTML-sisällön turvallisen käsittelyn periaatteet.
- [x] Kirjaa alustavat julkiset tietotiedostot ja vaihtoehtoiset Pages-julkaisumallit.
- [x] Kirjaa vaiheittainen toteutusjärjestys ja hyväksymiskriteerit.
- [x] Vaihe 0: kartoita nykyinen Pages-julkaisutyönkulku, sivuston rakenne, RSS-syötteet, automaatiot ja koneelliset seurantatiedot.
- [x] Vaihe 0: hyväksy tietomallit, JSON Schema -skeemat, julkaisupolku, datan säilytys ja julkistettavien kenttien rajaus.
- [ ] Vaihe 1: toteuta valvomon vähimmäisversio ja sitä tukevat koneelliset tilatiedot.
- [ ] Vaihe 2: toteuta kaikkien nykyisten syötteiden RSS-lukijan vähimmäisversio ja turvallinen lukutila.
- [ ] Vaihe 3: lisää haku, aikasuodatus, luettu-/tallennustila sekä lähderekisterin selaus.
- [ ] Vaihe 4: arvioi raporttiarkiston ja historiatrendien tarve.

**Valmistumiskriteeri:** valvomo näyttää todennettua ajotilaa sekoittamatta eri automaatioiden vastuita; RSS-lukija näyttää kaikki nykyiset syötteet oikein ja käsittelee ulkoisen HTML:n turvallisesti; tietomallit, viittaukset, saavutettavuus ja julkaisu on testattu. WCAG 2.2 AAA -tasoa ei väitetä ilman dokumentoitua testausta.


### Issue #133 – seurantamoduulin, seurantakohteen ja julkaisukohteen erottelu

**Toteutuksen tila:** valmis; PR #134 yhdistetty 18.11.2026.

- [x] Seurantamoduulin määrityksestä poistettiin hakuprofiilit ja aihekohtaiset sisältörajaukset; tilalle lisättiin pysyvät seurantakohdeviitteet.
- [x] Kaikkien kymmenen nykyisen moduulin seurantakohteet erotettiin omiin määrityksiinsä ja rekisteröitiin passiivisiksi.
- [x] Julkaisukohteen ja julkaisureitityksen skeemat sekä erilliset rekisterit lisättiin.
- [x] Näytösvahtiesimerkki näyttää kaksi kohdetta ja kaksi erillistä RSS-kanavaa; myöhempi päätös #142 poisti yhdistelmäsyötteen tavoitetilasta.
- [x] Viitteiden eheyden validointi ja yksikkötestit lisättiin.
- [x] Nykyisen näytösvahtifeedin ja automaatioasetusten tuotantopolku jätettiin ennalleen.


### Issue #142 – yksi RSS-syöte kutakin seurantakohdetta kohti

- [x] Tavoitetila ja järjestelmäarkkitehtuuri määrittelevät kohdekohtaisen yhden syötteen mallin.
- [x] Näytösvahtiesimerkistä poistettiin yhdistelmäjulkaisukohde ja siihen osoittavat reitit.
- [x] Reitityksen skeema, validaattori ja suoritusadapteri estävät useaan syötteeseen julkaisemisen.
- [x] Testit varmistavat, että eri kohteiden raportit jäävät eri syötteisiin.
- [x] README ja dokumentaation lukupolku on päivitetty.
- [x] Nykyistä tuotantosyötettä tai automaatioasetuksia ei muutettu.

### Issue #144 – käyttöliittymätestien erottaminen seurantajulkaisuista

- [x] Siirrettiin Valvomon, RSS-lukijan ja Kehitysjonon JavaScript-syntaksi- ja logiikkatestit itsenäiseen `.github/workflows/test-ui.yml`-työnkulkuun.
- [x] Rajattiin `.github/workflows/validate-feeds.yml` seurantadatan, RSS-syötteiden, dokumentaation, moduulisopimusten ja Python-testien tarkistamiseen.
- [x] Säilytettiin main-haaran rulesetin vaadittu status check seurantavalidoinnin työpaikassa; käyttöliittymätestejä ei asetettu vaadituksi PR-portiksi.
- [x] Lisättiin `tests/test_workflow_isolation.py`, joka tarkistaa työnkulkujen erillisyyden ja vaaditun tarkistusnimen.
- [x] Laajennettiin regressiotesti tarkistamaan suoraan, ettei seurantavalidoinnin jobilla ole UI-ajoon liittyvää ehtoa tai riippuvuutta eikä UI-työnkulku käytä `workflow_run`-ketjutusta.
- [x] Dokumentoitiin testin raja: repositorion testi tarkistaa versionhallittujen työnkulkujen riippumattomuuden, mutta GitHubin palvelussa ylläpidettävän branch ruleset -asetuksen vaaditut status checkit on tarkistettava erikseen.
- [x] Päivitettiin järjestelmäarkkitehtuurin kuvaus.
- [x] ChatGPT-automaation asetuksiin, ajastuksiin tai ohjeisiin ei tehty muutoksia.

**Tulos:** käyttöliittymätestien virhe ei ole seurantavalidoinnin tekninen riippuvuus. Regressiotesti havaitsee, jos työnkulkujen väliin lisätään myöhemmin riippuvuus tai ehtoketju. GitHubin branch ruleset on kuitenkin palveluasetus, jota tämä repositorion testi ei lue; sen tulee edelleen vaatia vain seurantavalidoinnin status check. Käyttöliittymien testit suoritetaan edelleen ja niiden tulokset näkyvät erillisessä työnkulussa.

### Issue #156 – RSS-julkaisun palautuva tapahtumaketju ja kestävä manifesti

- [x] Lisättiin ajokohtainen manifesti, joka kirjataan ennen julkaisun aloittamista.
- [x] Manifesti erottaa valmistelun, varmennetun julkaisun, artefaktien tallennuksen ja checkpointin päivityksen.
- [x] Lisättiin idempotentit eteenpäin siirtyvät vaiheet ja saman ajotunnisteen sisältökonfliktin esto.
- [x] Orkestroinnin tuotantotila edellyttää manifestisovitinta; puuttuva tai epäonnistuva manifesti estää julkaisun.
- [x] Lisättiin paikallisen atomisen manifestisovittimen testit.
- [ ] Toteuta tuotantokäyttöön pysyvä GitHub-/julkaisupalvelun manifestisovitin ja julkisen Pages-URL:n takaisinluku.
- [ ] Lisää katkaisu-/palautumistestit todelliselle julkaisupalvelulle ja rinnakkaisten julkaisujen lukitus.

**Rajaus:** nykyistä RSS-julkaisua, Pages-asetuksia, URL-osoitteita eikä automaatioiden ajastuksia tai ohjeita muutettu. Tämä muutos tekee moduuliorkestroinnin sopimuksesta palautumiskykyisemmän, mutta ei vielä kytke nykyistä tuotantojulkaisua manifestiin.

### Issue #158 – Nykyisen RSS/Pages-julkaisun manifesti ja takaisinluku

- [x] Lisättiin skeemavalidoitu, kaikkien kymmenen syötteen ehdokasmanifesti.
- [x] Manifesti tallennetaan GitHub Deployments -historiaan ennen ulkoista Pages-julkaisua; suojattuun main-haaraan ei kirjoiteta suoraan.
- [x] Pages-työnkulku validoi kaikki RSS-syötteet ennen rakennusta ja julkaisua.
- [x] Tuotannon Pages-ajot pysyvät samassa concurrency-ryhmässä; vanhentunut build ohitetaan tarkistamalla main-haaran kärki juuri ennen deployta.
- [x] Julkiset RSS-URL-osoitteet luetaan takaisin ja niiden SHA-256, GUID-lista sekä item-määrä verrataan manifestiin.
- [x] Julkaisun success/failure/inactive kirjataan append-only GitHub Deployment -statuksina.
- [x] Lisättiin offline-yksikkötestit manifestin sisällölle, XML:lle, GUIDeille ja porttiraportin sidonnalle.
- [x] Toteuta palautusartefakti edellisen sivustolähteen ja ennen deployta talteen otettujen julkisten RSS-tavujen pohjalta.\n- [x] Varmenna palautuksen jälkeen julkisten syötteiden SHA-256, GUID-lista ja item-määrä; epäonnistunut ehdokas jää workflow-virheeksi myös onnistuneen palautuksen jälkeen.
- [ ] Lisää katkaisu- ja uusintatestit oikeassa GitHub Actions -ympäristössä sekä operatiivinen hälytys epäonnistuneesta julkaisusta.

**Rajaus:** nykyiset RSS-URL-osoitteet, Pages-asetukset ja automaatioiden ajastukset, ohjeet sekä kohdekeskustelut säilyivät. Toteutus ei luo erillistä julkaisurepositoriota eikä muuta tuotannon julkaisukohdetta. Keskeytyneen ajon idempotentti jatkaminen, GitHub API:n epäselvien vastausten käsittely ja operatiivinen hälytys ovat edelleen avoinna; tätä ei pidä tulkita täysin toimintavarmaksi palautusratkaisuksi.
