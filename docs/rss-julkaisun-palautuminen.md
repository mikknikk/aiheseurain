# RSS-julkaisun manifesti ja takaisinluku

**Versio:** 1.1.0  
**Päiväys:** 2026-11-18  
**Liittyvät tiketit:** [#156](https://github.com/mikknikk/aiheseurain/issues/156), [#158](https://github.com/mikknikk/aiheseurain/issues/158), [#148](https://github.com/mikknikk/aiheseurain/issues/148)

## Omistajuus ja tallennus

RSS-syötteiden sisältö ja hyväksytyt porttiraportit pysyvät lähderepositorion omistuksessa. GitHub Pages on edelleen nykyinen julkinen jakelukanava. Julkaisun ajokohtainen manifesti tallennetaan GitHub Deployments -historiaan erilliseen `rss-publication-manifest`-ympäristöön. Se ei kirjoita suojattuun `main`-haaraan eikä ohita PR-suojausta.

Manifestin skeema on `schemas/rss-publication-manifest.schema.json`; muodostus ja takaisinluku toteutetaan `scripts/rss_publication_manifest.py`-skriptillä. Manifesti sisältää:
- GitHub Actions -ajon tunnisteen ja yrityksen sekä lähdecommitin ja vertailucommitin;
- kaikki kymmenen syötettä, ei vain muutettua syötettä;
- kunkin syötteen kanonisen Pages-URL:n, SHA-256-tiivisteen, tavumäärän, item-määrän ja GUID-listan;
- ennen julkaisua julkisista URL-osoitteista talteen otetun palautusversion vastaavat tiedot;
- muutetun syötteen hyväksytyn porttiraportin ajotunnisteen ja tiivisteen.

Varsinaisia raporttitekstejä tai lähdeaineistoa ei kopioida manifestiin. GitHub Deploymentin payload säilyttää valmistellun ehdokkaan; deployment-statushistoriaan lisätään julkaisun lopputulos muuttamatta aiempia merkintöjä.

## Julkaisun vaiheet

1. **PR-portti:** RSS/XML, HTML, GUIDit, dokumentaatio ja raporttikohtaiset hyväksynnät tarkistetaan ennen yhdistämistä.
2. **Rakennusportti:** Pages-työnkulku validoi kaikki RSS-syötteet uudelleen ja rakentaa staattisen sivuston.
3. **Valmistelu:** jos main-haaraan tullut commit muuttaa RSS-syötettä, työnkulku muodostaa kaikkien syötteiden muuttumattoman ehdokasmanifestin ja tallentaa sen GitHub Deployments -historiaan ennen Pages-julkaisua. Jos manifestin tallennus tai skeemavalidointi epäonnistuu, Pages-julkaisua ei aloiteta.
4. **Vanhentuneen ajon esto:** ennen deployta työnkulku vertaa buildin commitia GitHubin nykyiseen main-haaran kärkeen. Jos main on edennyt, vanha build ohitetaan ja manifesti merkitään `inactive`-tilaan. Käynnissä olevaa ajoa ei peruta; se ei kuitenkaan saa julkaista vanhentunutta sisältöä.
5. **Pages-julkaisu:** GitHub Pages julkaisee rakennetun sivuston omalla deployment-mekanismillaan.
6. **Takaisinluku:** julkisen Pages-URL:n jokainen kymmenestä RSS-syötteestä luetaan takaisin. Sisällön SHA-256, XML-rakenne, GUID-lista ja item-määrä verrataan manifestiin. Verkkovirheitä ja välimuistin viivettä yritetään rajatusti uudelleen.
7. **Ehdokkaan tarkistus:** jos uuden Pages-julkaisun kaikki kymmenen syötettä täsmäävät manifestiin, julkaisu voidaan hyväksyä.
8. **Automaattinen palautus:** jos ehdokasjulkaisu onnistui mutta takaisinluku ei täsmää, työnkulku julkaisee erillisen palautusartefaktin. Se rakennetaan edellisestä lähdecommitista, mutta RSS-tiedostot korvataan juuri ennen ehdokasjulkaisua julkisista URL-osoitteista talteen otetuilla täsmällisillä tavuilla.
9. **Palautuksen tarkistus ja lopputila:** palautuksen jälkeen kaikki kymmenen RSS-syötettä luetaan uudelleen ja verrataan snapshot-manifestiin. Jos palautus täsmää, aiempi sisältö on palautettu, mutta ehdokasjulkaisu kirjataan silti `failure`-tilaan ja workflow jää epäonnistuneeksi. Jos palautusta ei voida varmentaa, myös tämä kirjataan virheeksi.

Jos commit ei muuta RSS-syötteitä, Pages-sivusto voidaan julkaista normaalisti ilman RSS-manifestia. Ajastettu Pages-rakennus ei itsessään muodosta uutta RSS-julkaisumanifestia.

## Rinnakkaisuus ja viimeisin hyvä julkaisu

Kaikki tuotannon Pages-ajot ovat saman GitHub Actions -concurrency-ryhmän takana. Lisäksi juuri ennen deployta tarkistetaan main-haaran kärki. Tämä estää jonossa vanhentuneen buildin julkaisemisen uudemman commitin päälle. Manifesti kirjataan ennen ulkoista Pages-kirjoitusta, joten myös epäonnistunut julkaisu jää jäljitettäväksi.

GitHub Pagesin deployment vaihtaa staattisen sivuston julkaisuversiona; RSS-tiedostoja ei kirjoiteta yksitellen. Jos Pages-deployn tulos on epäselvä tai julkinen takaisinluku epäonnistuu, työnkulku tarkistaa julkisen sisällön deploy-toiminnon palautusarvosta riippumatta. Jos ehdokas ei ole kokonaan julkinen, työnkulku yrittää automaattista palautusta erillisellä Pages-deploylla. Näin myös epäselvä API-vastaus käsitellään todellisen julkisen tilan perusteella. Palautusartefakti sisältää edellisen sivustolähteen ja ennen ehdokasjulkaisua talteen otetut julkiset RSS-tavut, joten se ei oleta Gitin edellisen commitin olevan sama kuin tilaajien näkemä viimeisin sisältö. Palautuksen onnistuminen varmennetaan lukemalla kaikki RSS-URL:t takaisin. Ehdokasjulkaisun workflow merkitään silti epäonnistuneeksi, jotta virhe ei peity onnistuneen palautuksen alle.

## Käyttöönoton rajat

- Nykyiset kymmenen RSS-URL-osoitetta ja Pages-asetukset säilyvät.
- Aiheiden automaatioiden ajastuksia, suoritusvälejä, aikavyöhykkeitä, ohjeita tai kohdekeskusteluja ei muuteta.
- Julkaisurepositoriota ei luoda eikä nykyistä julkaisukohdetta vaihdeta. #148:n adapterisopimuksen tulee käyttää samaa manifesti- ja takaisinlukuperiaatetta.
- GitHub Deployment -manifesti on pysyvä auditointitietue ja sisältää myös palautusversion tiivisteet sekä GUIDit. Varsinainen palautusartefakti rakennetaan saman Actions-ajon aikana. Keskeytyneen ajon idempotentti jatkaminen ja GitHub API:n epäselvien vastausten käsittely ovat edelleen erillisen jatkotyön hyväksymiskriteerejä.

## Testaus

Yksikkötestit tarkistavat RSS/XML:n GUID-eheyden, virheellisen XML:n hylkäämisen, kaikkien katalogin syötteiden sisällyttämisen, muuttuneen syötteen hyväksytyn porttiraportin sidonnan, puuttuvan porttiraportin eston, palautussnapshotin tavujen säilymisen, palautussivuston RSS-tiedostojen korvaamisen sekä väärän julkisen sisällön hylkäämisen. GitHub Actions testaa todellisen Deployment API -kirjauksen ja julkisten Pages-URL-osoitteiden takaisinluvun vain RSS-syötteen sisältävän main-commitin yhteydessä.


## Automaattinen Pages-palautus

RSS-muutoksen yhteydessä työnkulku tallentaa ennen ehdokasjulkaisua kaikkien nykyisten julkisten syötteiden täsmälliset tavut. Jekyllin automaattisista sivustotiedostoista pois rajattuun `_rollback_snapshot/`-hakemistoon tallennettu snapshot validoidaan XML:n ja GUIDien osalta ja sidotaan muuttumattomaan GitHub Deployment -manifestiin SHA-256-, GUID- ja item-määrätietoineen. Jos ehdokasjulkaisun julkinen takaisinluku ei täsmää, työnkulku rakentaa palautusartefaktin edellisen lähdecommitin sivustosta ja korvaa sen RSS-tiedostot juuri ennen julkaisua talteen otetuilla julkisilla syötteillä. Näin palautus ei nojaa pelkästään Gitin edelliseen commit-tilaan, joka ei välttämättä ole sama kuin tilaajien viimeksi näkemä versio.

Palautuksen jälkeen kaikki syötteet luetaan uudelleen julkisista URL-osoitteista ja verrataan snapshot-manifestiin. Ehdokasjulkaisu kirjataan epäonnistuneeksi myös silloin, kun palautus onnistuu; workflow pysyy siis epäonnistuneena ja ilmoittaa virheestä, vaikka aiempi sisältö olisi palautettu. Jos Pages-deploy itsessään epäonnistuu, aiempi Pages-versio säilyy eikä rollbackia tarvita.

Palautusartefakti rakennetaan vain RSS-syötemuutoksissa. Muut sivustojulkaisut säilyttävät aiemman toimintatapansa. Palautus ei muuta RSS-URL-osoitteita, Pages-kohdetta tai automaatioiden asetuksia. Keskeytyneen ajon idempotentti jatkaminen, GitHub API:n epäselvien vastausten käsittely ja operatiivinen hälytys ovat edelleen avoimia; tätä ei pidä tulkita täysin toimintavarmaksi palautusratkaisuksi.
