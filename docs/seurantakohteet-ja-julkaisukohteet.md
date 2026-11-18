# Seurantamoduulit, seurantakohteet ja julkaisukohteet

**Versio:** 1.0.0  
**Liittyvä tiketti:** [#133](https://github.com/mikknikk/aiheseurain/issues/133)

## Kolme itsenäistä käsitettä

- **Seurantamoduuli** (modules/, data/module-registry.json) omistaa suoritettavan prosessin, kyvykkyydet, lähdeviitteet ja toimitukselliset säännöt. Se ei sisällä kohdekohtaisia hakuja eikä julkaisukanavan asetuksia.
- **Seurantakohde** (data/targets/, data/target-registry.json) yksilöi henkilön, teoksen, elokuvan, tapahtumakokoelman tai muun kiinnostuksen kohteen. Se omistaa hakuprofiilit, kieli- ja aluerajaukset sekä kohdekohtaiset sisällytys- ja poissulkuehdot. Kohde viittaa omistavaan moduuliin, mutta ei määrittele julkaisupaikkaa.
- **Julkaisukohde** (data/publications/, data/publication-registry.json) määrittelee jakelukanavan, muodon ja teknisen kohdepolun. Se ei sisällä hakuehtoja tai toimituksellista logiikkaa.

## Reitityssopimus

data/publication-routing.json yhdistää moduulin, seurantakohteen ja yhden tai useamman julkaisukohteen. Reitti voi lisäksi rajata havaintotyypit. Sama havainto voidaan julkaista sekä kohdekohtaisessa syötteessä että valinnaisessa yhdistelmäsyötteessä. Tuotannon julkaisurekisteri ja reititys ovat tässä vaiheessa tyhjiä: esimerkit eivät muuta nykyisiä RSS-syötteitä.

## Esimerkki

examples/seurantakohteet/naytosvahti.json näyttää yhden näytösvahtimoduulin kaksi erillistä kohdetta: yksittäisten elokuvien näytökset ja festivaalit. examples/julkaisukohteet/ sisältää niille omat RSS-kanavat sekä yhdistelmäsyötteen. examples/julkaisureititys/naytosvahti.json reitittää kummankin kohteen omaan syötteeseensä ja lisäksi yhteiseen syötteeseen. Esimerkkien example.invalid-osoitteet ovat tarkoituksella ei-tuotannollisia.

## Tunnisteet, versiot ja omistajuus

Kaikilla kolmella käsitteellä on oma pysyvä tunniste ja semanttinen versio. Muutokset kohteen hakuehtoihin eivät muuta moduulin versiota; julkaisukanavan polun tai formaatin muutos ei muuta kohteen versiota. Reititys on oma versionoitu kokonaisuutensa. Nimiä ja tiedostopolkuja ei käytetä viittausavaimina.

## Validointi

Aja python scripts/validate_target_publication.py. Tarkistus validoi kuusi JSON Schema -sopimusta sekä moduuli-, kohde-, julkaisu- ja reititysviitteet. Yksikkötestit ajetaan komennolla python -m unittest tests.test_target_publication -v. Tarkistus hylkää puuttuvat tiedostot, tuntemattomat tunnisteet, kohteen väärän moduuliomistajan ja reitin tuntemattoman julkaisukohteen.

## Siirtymä ja tuotannon rajat

Nykyiset kymmenen moduulimääritystä viittaavat nyt erillisiin seurantakohteisiin. Kohteet on rekisteröity inactive-tilaan. Nykyisen intialaisten elokuvien näytösvahdin käsikirja, sen historiallinen RSS-syöte, näytöshistoria ja automaatio pysyvät nykyisessä tuotantopolussa. Uudet julkaisukohteet ja reitit otetaan käyttöön vasta erillisessä hyväksytyssä migraatiossa.

Tämä rakenne ei muuta ChatGPT-automaatiota, ajastuksia, aikavyöhykkeitä, ohjeita tai kohdekeskusteluja.


## Julkaisureitityksen ajonaikainen sovitin

Toteutuksen ensimmäinen tekninen osa on `scripts/publication_routing.py`. Se lukee tuotannon moduuli-, seurantakohde-, julkaisukohde- ja reititysrekisterit erillisinä sekä tarkistaa viittausten eheyden ennen reitin käyttöä.

- `load_publication_context()` lataa ja validoi rekisterit.
- `resolve_publication_plan()` ratkaisee yhden kohdekohtaisen raportin kanavat moduulin, seurantakohteen ja raportin havaintotyyppien perusteella.
- `preview_publication_plan()` palauttaa kuivaharjoittelun tuloksen eikä kirjoita tiedostoja.
- `LocalRoutedRssPublisher` on paikallinen RSS-sovitin, joka julkaisee saman kohderaportin sen omiin ja yhdistelmäsyötteisiin. Sovittimelle annetaan kirjoitusjuuri erikseen; se ei aktivoi tai kirjoita tuotantokohteisiin itsestään.

Saman moduulin, seurantakohteen, ajon ja julkaisukohteen yhdistelmä tuottaa vakaan GUIDin. Uusinta-ajo ei lisää samaa raporttia uudelleen, ja saman GUIDin eri sisältö hylätään ristiriitana. Julkaisusovitin ja reitityksen ratkaisu ovat erillisiä luokkia ja vaiheita.

Tämä sovitin on vielä erillinen moduuliajon julkaisurajapinnasta: tuotantoorkestroinnin automaattinen reititetty julkaisu edellyttää seuraavaa integraatiovaihetta, jossa kohdekohtaiset raportit annetaan tälle sovittimelle. Nykyistä tuotannon julkaisupolkua ei ole vaihdettu eikä rekistereitä aktivoitu. Testit: `python -m unittest tests.test_publication_routing -v`.
