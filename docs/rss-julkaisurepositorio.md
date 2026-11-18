# Erillisen RSS-julkaisurepositorion tavoitearkkitehtuuri

**Versio:** 1.0.0  
**Päiväys:** 2026-11-18  
**Tila:** suunnitteluratkaisu; ei tuotantokäyttöönottoa  
**Liittyvä tiketti:** [#148 – Suunnittele erillisen RSS-julkaisurepositorion tavoitearkkitehtuuri ja hallittu siirtymä](https://github.com/mikknikk/aiheseurain/issues/148)

## 1. Päätös lyhyesti

Aiheseuraimelle suositellaan erillistä julkista repositoriota nimellä **`aiheseurain-julkaisut`**. Se toimii vain julkisten julkaisuartefaktien jakelukohteena. Nykyinen `mikknikk/aiheseurain` säilyy lähde- ja hallintarepositoriona.

Uutta repositoriota ei luoda tämän suunnitelman perusteella. Myöskään GitHub Pages -asetuksia, nykyisiä RSS-URL-osoitteita, automaatioiden ajastuksia, ohjeita tai kohdekeskusteluja ei muuteta. Nykyinen Pages-julkaisu pysyy ainoana tuotantojulkaisuna, kunnes erillinen käyttöönotto hyväksytään ja sen edellytykset on testattu.

Suositeltu tavoiteosoite uusille julkaisuille on:

`https://mikknikk.github.io/aiheseurain-julkaisut/feeds/{syötetiedosto}.xml`

Nykyiset osoitteet säilytetään yhteensopivuuspeilinä:

`https://mikknikk.github.io/aiheseurain/feeds/{syötetiedosto}.xml`

GitHub Pages ei tarjoa tässä mallissa automaattista pysyvää URL-uudelleenohjausta vanhan projektipolun ja uuden projektipolun välillä. Siksi vanhoja osoitteita ei saa katkaista eikä jättää vanhentumaan: lähderepositorion nykyinen Pages-sivusto jatkaa samojen RSS-tiedostojen julkaisemista peilinä myös siirtymän jälkeen, ellei myöhemmin hyväksytä ja toteuteta erillistä, todennettua URL-jatkuvuusratkaisua.

## 2. Repositorioiden vastuurajat

| Vastuu | `aiheseurain` (lähderepo) | `aiheseurain-julkaisut` (tavoite) |
|---|---|---|
| Aihe- ja seurantamääritykset | Omistaa | Ei sisällä |
| Lähderekisterit, seurantatila ja ajohistoria | Omistaa | Ei sisällä |
| Raporttien hyväksyntä ja julkaisulaadun portti | Omistaa | Ei tee toimituksellisia päätöksiä |
| RSS-sisältöjen hyväksytty lähdeversio | Omistaa `feeds/*.xml`-tiedostoina | Vastaanottaa täsmälleen hyväksytyt tavut |
| Sisäiset skeemat, testit ja työnkulut | Omistaa | Sisältää vain julkisen jakelun itsenäiseen tarkistukseen tarvittavan vähimmäistoteutuksen |
| Julkiset RSS-syötteet | Nykyiset URL:t yhteensopivuuspeilinä | Uusien URL:ien ensisijainen jakelukohde |
| Julkinen julkaisu- ja takaisinlukutulos | Tallentaa lähdeajon manifestin ja päätöksen | Todentaa oman Pages-julkaisunsa |

GitHub Issues pysyy kehitystehtävien kanonisena lähteenä. Julkaisurepositorio ei sisällä kopioita kehitystiketeistä, lähderekistereistä, sisäisistä raporteista tai automaatioiden tilasta.

## 3. Julkaisurepositorion sisältö ja Pages

### 3.1 Suositeltu rakenne

Julkaisurepositorion tulee olla mahdollisimman pieni ja staattinen:

```text
aiheseurain-julkaisut/
├── .nojekyll
├── README.md
├── publication-manifest.json
└── feeds/
    ├── tolkien.xml
    ├── taylor-swift.xml
    ├── gurmeet-ram-rahim-singh.xml
    ├── muumit.xml
    ├── wakaliwood.xml
    ├── euroviisut.xml
    ├── sompote-sands.xml
    ├── shakkidraamat.xml
    ├── intialaiset-elokuvat.xml
    └── intialaisten-elokuvien-naytokset.xml
```

Tiedostoluettelo johdetaan lähderepositorion `data/feed-catalog.json`-katalogista; sitä ei ylläpidetä kahtena toisistaan riippumattomana totuutena. Luettelo yllä näyttää nykyisen kymmenen syötteen tavoiterakenteen.

Julkaisurepoon ei kopioida Jekyll-sivustoa, käyttöliittymiä, lähde- tai kohde-rekistereitä, hyväksyntäraportteja, seurantatiloja, ajohistoriaa, salaisuuksia eikä tarpeettomia raakadata-aineistoja. `publication-manifest.json` sisältää vain julkisen julkaisun todentamiseen tarvittavan metatiedon: skeemaversion, lähdecommitin, julkaisuaikaleiman ja syötekohtaiset polut, SHA-256-tiivisteet, tavumäärät, item-määrät ja GUID-tunnisteet. Se ei sisällä raporttitekstejä toiseen kertaan eikä tunnuksia.

GitHub Pagesin lähteeksi valitaan julkaisurepositorion oma GitHub Actions -julkaisutyönkulku. Staattinen sisältö julkaistaan suoraan `feeds/`-polusta; `.nojekyll` estää tarpeettoman Jekyll-käsittelyn. Julkaisun tarkka konfiguraatio varmennetaan prototyypissä ennen uuden repositorion käyttöönottoa.

## 4. Julkaisun tietovirta ja atomisuus

Julkaisun tulee olla eräkohtainen, idempotentti ja takaisinluettava.

1. **Lähderepon hyväksyntä:** RSS:n sisältö, XML, GUIDit, aiherajaus, raporttikohtainen hyväksyntäraportti ja dokumentaatioviitteet tarkistetaan nykyisillä pakollisilla CI-porteilla.
2. **Muuttumattoman erän valmistelu:** lähdetyönkulku lukee kaikki kymmenen syötettä ja muodostaa niiden tavut sekä julkaisumanifestin. Syötteiden on vastattava hyväksyttyä lähdecommittia.
3. **Eheyden tarkistus:** kaikki syötteet validoidaan ennen yhtäkään kohderepositorion kirjoitusta. Puuttuva, virheellinen tai osittainen syöte keskeyttää koko erän.
4. **Yksi atominen Git-kirjoitus:** kaikki muuttuneet syötteet ja manifesti kirjoitetaan julkaisurepositorioon yhtenä Git-puuna ja yhtenä commitina. Git Data API:n blob/tree/commit/ref-mallia käytetään; yksittäisiä Contents API -kirjoituksia ei tehdä tiedosto kerrallaan.
5. **Kilpailutilanteen esto:** julkaisurepon nykyinen ref-SHA luetaan ennen commitin kiinnittämistä. Ref päivitetään odotetulla SHA:lla (compare-and-swap). Jos ref on muuttunut, erää ei ylikirjoiteta; lähdetyönkulku lukee tilanteen uudelleen ja joko muodostaa uuden erän uusimmasta hyväksytystä lähteestä tai pysähtyy.
6. **Kohderepon itsenäinen tarkistus:** julkaisurepon oma push-työnkulku tarkistaa tiedostojen sallitut polut, manifestin, kaikkien kymmenen XML:n rakenteen, GUIDien yksilöllisyyden ja syötekohtaisen erillisyyden. Vain onnistunut tarkistus voi jatkaa Pages-julkaisuun.
7. **Pages-julkaisu ja takaisinluku:** kohderepo julkaisee Pagesin ja lukee kaikki kymmenen julkista URL-osoitetta takaisin. Se vertaa tavujen SHA-256-tiivisteitä, XML-rakennetta, GUID-listoja ja item-määriä manifestiin.
8. **Lähdeajon lopputila:** lähderepo merkitsee julkaisun onnistuneeksi vasta, kun kohderepon CI, Pages-deployment ja julkinen takaisinluku on varmennettu. Pelkkä kohderepoon syntynyt commit ei ole julkaisuonnistuminen.

Sama sisältö ja sama julkaisuerän tunniste eivät saa tuottaa uusia merkityksettömiä committeja. Uusintayrityksen on ensin selvitettävä, syntyikö edellisellä yrityksellä jo kohdecommit tai Pages-deployment. Epäselvää kirjoitustulosta ei saa ratkaista sokkona toistamalla kirjoitusta.

## 5. Tunnistus ja käyttöoikeudet

Ensisijainen ratkaisu on erillinen GitHub App, joka asennetaan vain julkaisurepositorioon.

- Appin asennusoikeudet rajataan kohderepoon.
- Lähdetyönkulku luo lyhytikäisen installation access tokenin vasta luotetussa `main`-haaran julkaisu-jobissa.
- App tarvitsee vain metatietojen lukuoikeuden ja kohderepositorion sisältöjen kirjoitusoikeuden. Se ei tarvitse lähderepon hallinta-, issue-, Actions-, Pages- tai ympäristöasetusten kirjoitusoikeutta.
- Appin yksityinen avain säilytetään lähderepositorion Actions-salaisuutena. Sitä tai luotua asennustunnusta ei anneta PR-haaroille, selaimelle, RSS-sisällölle tai automaatioiden käyttöön.
- Kohderepon Pages-työnkulku käyttää omaa `GITHUB_TOKEN`-tunnustaan vähimmillä oikeuksilla: sisällön luku sekä Pages-julkaisun ja OIDC:n vaatimat oikeudet.
- Tunnuksen luonti ja käyttö rajataan `main`-haaran hyväksyttyyn julkaisuun; pull request -ajot saavat validoida ja rakentaa testituloksen, mutta eivät julkaista ulkoiseen repositorioon.

Rajattu fine-grained personal access token on vain varavaihtoehto, jos GitHub Appin käyttöönotto osoittautuu prototyypissä mahdottomaksi. Silloin token rajataan täsmälleen yhteen julkaisurepositorioon ja vain Contents-oikeuteen, sille määritellään omistaja, uusimis- ja peruutusmenettely sekä käyttöauditointi. Laajaa klassista PAT-tokenia ei käytetä.

## 6. Virhetilanteet, viimeisin hyvä julkaisu ja palautus

| Virhe | Vaadittu toiminta |
|---|---|
| Lähde-erä ei läpäise validointia | Älä kirjoita julkaisurepoon mitään. Nykyinen tuotanto ja viimeisin hyvä julkaisu säilyvät. |
| App-tokenin luonti tai käyttö epäonnistuu | Keskeytä ennen kohdekirjoitusta; kirjaa virhe lähdeajoon. |
| Kohderepon ref on muuttunut | Hylkää vanhentunut ref-päivitys; älä ylikirjoita toisen ajon commitia. |
| Git-kirjoituksen vastaus jää epäselväksi | Lue kohderepon ref ja commit-historia ennen mitään uusintaa. |
| Kohderepon validointi epäonnistuu | Pages-julkaisua ei käynnistetä; edellinen Pages-versio säilyy. |
| Pages-deployment epäonnistuu | Edellinen Pages-versio säilyy; julkaisu merkitään epäonnistuneeksi. |
| Julkinen takaisinluku ei vastaa manifestia | Kohderepo palauttaa viimeisimmän hyväksytyn julkaisucommitin tai muodostaa siitä uuden palautuscommitin, julkaisee palautuksen ja todentaa sen takaisinluvulla. |
| Palautuskaan ei ole varmennettavissa | Älä ilmoita onnistumista; nosta näkyvä hälytys ja säilytä kaikki ajo-/deployment-viitteet tutkintaa varten. |

Koska kaikki kymmenen syötettä kirjoitetaan yhteen Git-commitiin, lukija ei näe tarkoituksellisesti tiedosto kerrallaan päivittyvää osajoukkoa. Pagesin julkaisutila on silti erillinen Gitin commit-tilasta: julkaisu merkitään onnistuneeksi vasta julkisen takaisinluvun perusteella. Palautuksen pitää perustua viimeisimpään hyväksyttyyn kohdecommitiin, ei pelkästään lähderepon edelliseen commitiin, koska nämä voivat erota.

Kaikki julkaisu- ja palautusyritykset ovat jäljitettävissä lähdeajon manifestin, kohdecommitin, Actions-ajon ja Pages-deploymentin tunnisteilla. Virheilmoitukseen ei kopioida salaisuuksia tai tarpeetonta raakaa API-vastausta.

## 7. URL-osoitteet, RSS-lukija ja yhteensopivuus

GitHub Pagesin projektisivustojen URL-polku sisältää repositorion nimen. Uuden repositorion feed-osoitteet ovat siksi eri polussa, vaikka host on sama `mikknikk.github.io`. Saman hostin vuoksi nykyisen RSS-lukijan selainpyynnöt ovat lähtökohtaisesti saman originin pyyntöjä; tämä on silti varmistettava todellisessa Pages-prototyypissä eikä pääteltävä pelkästä lähdekoodista.

Siirtymän URL-strategia:

1. Nykyiset kymmenen RSS-URL-osoitetta pysyvät toiminnassa lähderepositorion Pages-sivuston yhteensopivuuspeilinä.
2. Uudet julkaisu-URL:t testataan ja niitä luetaan rinnakkain nykyisten URL:ien kanssa.
3. RSS-lukija siirtyy käyttämään uusia osoitteita vasta, kun kaikki kymmenen syötettä, CORS-/fetch-käyttäytyminen, välimuisti, virhetilat ja lukijan toiminta on testattu.
4. Nykyisten osoitteiden poistaminen ei kuulu tähän suunnitteluun eikä rinnakkaisjulkaisun hyväksymiseen. Vanhojen osoitteiden jatkuvuudelle tarvitaan erillinen, todennettu päätös ja hyväksyntä.
5. RSS:n kanavakohtaiset linkit, syötekatalogi, README ja automaatioiden julkaisemien linkkien muodostus tarkistetaan yhtenä kokonaisuutena vasta käyttöönoton omassa tikettikokonaisuudessa.

Uuden URL:n lisääminen ei saa aiheuttaa tilaajille tyhjää syötettä, GUIDien vaihtumista, vanhojen itemien katoamista tai aiheiden yhdistymistä. Julkaisurepo säilyttää syötteiden alkuperäiset tavut; mahdolliset URL:iin liittyvät metatietomuutokset tehdään erillisinä, hyväksyttyinä muutoksina.

## 8. Vaiheistus ja päätösportit

| Vaihe | Sisältö | Siirtymisehto |
|---|---|---|
| 0. Määrittely | Tämä dokumentti: vastuurajat, sisältö, App-oikeudet, atomisuus, virheet, URL:t ja palautus | Suunnittelutiketti hyväksytty |
| 1. Eristetty prototyyppi | Testirepo, GitHub App, yhden testisyötteen ja kymmenen syötteen atominen kirjoitus, kohde-CI ja Pages-takaisinluku | Testit osoittavat idempotenssin, kilpailutilanteiden eston ja palautuksen ilman tuotantosyötteitä |
| 2. Varjojulkaisu | Sama hyväksytty syöte-erä julkaistaan nykyiseen tuotantoon ja eristettyyn kohteeseen; tuloksia verrataan | Kaikki syötteet vastaavat tavutasolla; nykyinen julkaisu pysyy ensisijaisena |
| 3. Rinnakkaisjulkaisu | Julkaisurepo saa kaikki kymmenen hyväksyttyä syötettä ja todentaa oman Pages-julkaisunsa | Toistuvat ajot ja virhetilanteet on varmennettu; vanhat URL:t toimivat edelleen |
| 4. Hallittu lukijasiirtymä | RSS-lukijan ja dokumentaation uudet URL:t otetaan käyttöön erillisellä hyväksytyllä muutoksella | Lukijan toiminta ja kaikkien feedien takaisinluku hyväksytty |
| 5. Tuotannon vastuun siirto | Julkaisurepo nimetään uusien julkaisujen ensisijaiseksi kohteeksi; vanha polku jää yhteensopivuuspeiliksi | Erillinen käyttöönottohyväksyntä ja palautussuunnitelma |
| 6. Mahdollinen vanhan julkaisun alasajo | Arvioidaan vasta myöhemmin, onko vanhan peilin poistamiseen turvallista tapaa | Kaikki nykyiset tilaajat, URL:t ja lukijan riippuvuudet on turvattu erillisellä päätöksellä |

Jokaisessa vaiheessa nykyinen tuotantojulkaisu jatkuu muuttumattomana, kunnes kyseisen vaiheen hyväksymisehdot täyttyvät. Suunnittelun, prototyypin tai varjojulkaisun perusteella ei saa muuttaa live-automaatioita tai niiden asetuksia.

## 9. Toteutuksen hyväksymiskriteerit seuraaville tiketeille

Tämä dokumentti määrittelee tavoiteratkaisun. Varsinainen toteutus jaetaan vähintään seuraaviin erillisiin tehtäviin:

1. **Julkaisurepositorion ja GitHub Appin perustaminen:** repositorion omistajuus, näkyvyys, Pages-asetus, Appin rajatut oikeudet ja turvallinen tunnuksen luonti. Ei tuotantoreititystä.
2. **Atomisen julkaisusovittimen prototyyppi:** muuttumattoman syöte-erän valmistelu, manifesti, Git Data API:n atominen commit, compare-and-swap, idempotenssi ja kilpailutilanteiden testit.
3. **Kohderepon validointi ja Pages-julkaisu:** itsenäiset RSS-tarkistukset, Pages-build, takaisinluku, viimeisin hyvä commit ja palautus.
4. **Varjo- ja rinnakkaisjulkaisun varmennus:** kaikki kymmenen syötettä, virhe-injektio, toistuvat ajot, julkisten URL:ien vertailu ja hälytykset.
5. **Lukijan URL-siirtymä:** RSS-lukijan ja dokumentaation uudet URL:t, vanhojen URL:ien yhteensopivuuspeili ja käyttöönoton hyväksyntä.

Kunkin toteutustiketin on säilytettävä lähderepon nykyinen Pages-julkaisu, RSS-historia ja vanhat URL:t. Tuotannon siirto, vanhojen URL:ien poistaminen ja automaatioasetusten muuttaminen eivät sisälly näihin toteutustiketteihin ilman erillistä nimenomaista hyväksyntää.

## 10. Rajaukset

Tämä dokumentti on tavoitearkkitehtuurin suunnitelma. Se ei luo julkaisurepositoriota tai GitHub Appia, lisää salaisuuksia, muuta Pages-asetuksia, kirjoita kohderepoon, muuta nykyisiä RSS-URL-osoitteita tai RSS-sisältöjä eikä kytke uutta julkaisukohdetta tuotantoon. Se ei muuta ChatGPT-automaatiotehtävien ajastuksia, suoritusvälejä, aikavyöhykkeitä, ohjeita, aktiivisuutta tai kohdekeskusteluja eikä luo korvaavia automaatioita.
