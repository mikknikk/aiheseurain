# Uutislähteiden ja uutisväitteiden luotettavuusluokitus

Tämä dokumentti määrittelee Aiheseuraimen yhteisen luotettavuusmallin. Se erottaa kaksi asiaa, joita ei saa käyttää toistensa sijasta:

1. **Lähteen yleinen luotettavuusluokka A–D** kuvaa lähteen tyyppiä ja sen tavanomaista todistusroolia.
2. **Yksittäisen uutisväitteen varmennustaso** kuvaa, millaista näyttöä juuri kyseisestä väitteestä on tarkistettu.

Lähdeluokka ei ole artikkelin tai väitteen totuusarvosana. Hyvämaineinen media voi raportoida huhun, ja virallinen lähde voi olla ensisijainen vain oman organisaationsa toimista. Kaikki luokitukset ovat toimituksellisia apuvälineitä, eivät automaattisia totuustestejä.

## 1. Lähteen yleinen luotettavuusluokka A–D

| Luokka | Lähdetyyppi ja tyypillinen todistusrooli | Käyttö |
|---|---|---|
| **A – Ensisijainen tai virallinen** | Viranomainen, tuomioistuin, kilpailun tai tapahtuman järjestäjä, oikeudenhaltija, studio, tuotantoyhtiö, artisti, lajiliitto tai muu toimija, jolla on suora ensikäden tieto omasta toiminnastaan. | Ensisijainen oman toiminnan, päätösten, ohjelmien, julkaisujen ja virallisten asiakirjojen lähde. Ei automaattisesti riippumaton tai puolueeton arvioimaan omaa toimintaansa tai muiden osapuolten väitteitä. |
| **B – Vakiintunut toimituksellinen media** | Tunnettu uutistoimisto, yleisradioyhtiö tai muu laaja toimituksellinen julkaisu, jolla on tunnistettava toimitusprosessi, journalistinen vastuu ja korjauskäytäntö. | Vahva toimituksellinen raportointilähde. Arvioi silti jutun kirjoittaja, lähteet, alkuperäinen raportointityö ja mahdolliset sidonnaisuudet. |
| **C – Erikoistunut, paikallinen tai asiantuntijalähde** | Aiheeseen erikoistunut julkaisu, paikallismedia, tutkimusjulkaisu, nimetty asiantuntija, alan yhdistys tai muu rajatun alan lähde. | Voi olla paras lähde oman erikoisalansa tai paikallisen tapahtuman yksityiskohdissa. Arvioi asiantuntemus, toimituksellinen vastuu, menetelmät, sidonnaisuudet ja se, perustuuko sisältö omaan selvitykseen vai muiden kopiointiin. |
| **D – Vihje- tai keskustelulähde** | Sosiaalisen median julkaisu tai tili, keskustelupalsta, fanisivu, yhteisöwiki, anonyymi väite tai muu lähde, jonka sisältöä ei voi sellaisenaan pitää toimituksellisesti varmennettuna. | Voi auttaa löytämään alkuperäisen lähteen tai uuden seurattavan kysymyksen. Ei yksin vahvista uutisväitettä. Varmista tieto A-, B- tai tarkoitukseen sopivasta C-lähteestä ennen faktana julkaisemista. |

Luokka kertoo lähdetyypistä, ei yksittäisen julkaisun laadusta. B-luokan lähde voi julkaista virheellisen jutun, ja C-luokan erikoislähde voi olla tietyn teknisen yksityiskohdan paras saatavilla oleva lähde. A-luokan lähde on ensisijainen vain niissä asioissa, joista sillä on suora ensikäden tieto.

### 1.1 Luokan valinta ja lähdekatalogi

Yhteisen lähdekatalogin data/source-catalog.json jokaisella lähteellä on pakollinen reliability_class-kenttä (A–D). Valinnassa arvioidaan lähteen todellinen julkaisurooli, ei vain teknistä source_type-kenttää. Esimerkiksi toimituksellinen paikallis- tai erikoisjulkaisu voi olla C, vaikka sen source_type on editorial.

Katalogiin tallennettu luokka on lähtöarvio. Tarkista sen soveltuvuus uudelleen väitteen ja käyttötarkoituksen yhteydessä. Valinnainen reliability_note-kenttä sisältää olennaisen lähdekohtaisen varauksen, esimerkiksi fanisivun aseman tai sen, että lähde toimii vain vihjeenä.

Aihekohtainen data/sources/{task_id}.json viittaa lähteeseen source_id-kentällä eikä kopioi A–D-luokkaa. Luokka periytyy yhteisestä katalogista. Tehtäväkohtainen access_limit voi täydentää tietoa siitä, mihin tarkoitukseen lähde soveltuu kyseisessä aiheessa. critical kertoo vain operatiivisesta tarkistustarpeesta, ei lähteen luotettavuudesta.

## 2. Yksittäisen uutisväitteen varmennustaso

Arvioi jokainen olennainen, tarkistettavissa oleva uutisväite erikseen. Yhdessä uutisartikkelissa voi olla useita väitteitä, joilla on eri varmennustaso. Käytä yhtä seuraavista tiloista kullekin väitteelle:

| Koneellinen arvo | Raportissa näytettävä merkintä | Kriteeri |
|---|---|---|
| ensisijaislahteella_vahvistettu | **ENSISIJAISELLÄ LÄHTEELLÄ VAHVISTETTU** | Väite käy suoraan ilmi asianomaisen toimijan, viranomaisen, tuomioistuimen, järjestäjän tai muun kyseisessä asiassa ensisijaisen lähteen alkuperäisestä aineistosta. Kerro, mitä lähde todella vahvistaa. |
| riippumattomissa_toimituksellisissa_lahteissa_vahvistettu | **RIIPPUMATTOMISSA TOIMITUKSELLISISSA LÄHTEISSÄ VAHVISTETTU** | Vähintään kaksi aidosti toisistaan riippumatonta toimituksellista lähdettä on raportoinut väitteen ja niiden oma tarkistus tai raportointi tukee sitä. Pelkkä samaa alkuperäistä tiedotetta tai uutistoimistojuttua toistavien sivustojen määrä ei riitä. |
| yhden_toimituksellisen_lahteen_raportoima | **YHDEN TOIMITUKSELLISEN LÄHTEEN RAPORTOIMA** | Yksi tunnistettava toimituksellinen lähde raportoi väitteen, mutta riippumatonta vahvistusta tai soveltuvaa ensisijaislähdettä ei ole saatu. Lähteen oma luotettavuusluokka ei muuta tätä tasoa. |
| nimettomaan_lahteeseen_perustuva | **NIMETTÖMÄÄN LÄHTEESEEN PERUSTUVA RAPORTOINTI** | Toimituksellinen juttu nojaa olennaisesti yhteen tai useampaan nimettömään tietolähteeseen eikä väitettä ole vahvistettu muulla tavalla. Kerro, jos lähteen asema, määrä tai väitteen tarkkuus jää epäselväksi. |
| huhu | **HUHU – EI VAHVISTETTU** | Väitteellä ei ole riittävää tunnistettavaa ja tarkistettavaa näyttöä. Älä esitä sitä faktana tai uutisraportin vahvistettuna sisältönä. Seuraa vain, jos väitteellä on selvä uutisarvo; nimeä se huhuksi ja kerro sen alkuperä sekä puuttuva vahvistus. |
| ristiriitainen_tai_selvittamaton | **RISTIRIITAINEN TAI SELVITTÄMÄTÖN TIETO** | Luotettavat lähteet ovat keskenään ristiriidassa, lähteet eivät riitä ratkaisemaan asiaa tai alkuperäistä sisältöä ei ole voitu tarkistaa. Esitä osapuolten kannat ja epävarmuus avoimesti; älä valitse mieluisinta versiota ilman näyttöä. |

Jos väite on vahvistettu ensisijaisesta lähteestä, käytä ensisijaisen lähteen tilaa, vaikka toimitukselliset mediat olisivat lisäksi raportoineet siitä. Mainitse riippumattomat toimitukselliset vahvistukset lähdeluettelossa erikseen. Älä nosta väitettä ensisijaisesti vahvistetuksi, jos virallinen lähde ei itse vahvista kyseistä väitettä.

### 2.1 Lähteiden riippumattomuus

Arvioi riippumattomuus lähteiden alkuperäisen raportointityön, ei julkaisujen tai URL-osoitteiden lukumäärän perusteella.

- Saman uutistoimiston juttu ja sen kopiot, syndikoidut julkaisut tai käännökset ovat yksi raportointiketju.
- Useat julkaisut, jotka toistavat saman tiedotteen, lehdistötiedotteen, haastattelun tai nimetyn nimettömän lähteen, eivät ole automaattisesti riippumattomia.
- Eri omistajat tai toimitusten nimet eivät yksin osoita riippumattomuutta.
- Riippumattomuutta tukee se, että toimitukset ovat tehneet omat haastattelunsa, tarkistaneet asiakirjat tai hankkineet erillisen ensikäden vahvistuksen.
- Jos lähteiden yhteistä alkuperää ei pystytä selvittämään, merkitse riippumattomuus tuntemattomaksi. Älä laske lähteitä riippumattomiksi varmuuden vuoksi.

Kirjaa tarvittaessa lähderiippuvuus docs/seuranta.md:n tapahtumamerkintään tai julkaisun tarkistusraporttiin.

### 2.2 Nimettömät lähteet, ristiriidat ja muuttuva tieto

- Erota toimituksen nimettömän tietolähteen käyttö itse julkaisijan luotettavuudesta. B-luokan media voi julkaista anonyymiin lähteeseen perustuvan väitteen; väitteen varmennustaso on silti nimettömään lähteeseen perustuva.
- Kerro nimettömän lähteen asema vain siinä laajuudessa kuin julkaisu sen ilmoittaa. Älä arvaa henkilöllisyyttä, lukumäärää tai motiivia.
- Jos osapuoli kiistää väitteen, kirjaa kiistäminen ja sen lähde. Kiistäminen ei yksin todista alkuperäistä väitettä vääräksi.
- Erota syytös, vastaus, tutkinta, syyte, tuomio, valitus ja lainvoimainen ratkaisu. Käytä oikeudellisissa asioissa täsmällisiä menettelytermejä.
- Nopeasti muuttuvissa tilanteissa merkitse, mihin ajankohtaan tieto perustuu. Päivitä varmennustaso vain uuden tarkistetun näytön perusteella; vanhempi uutinen tai hiljaisuus ei ole uusi vahvistus.
- Jos lähteet ovat ristiriidassa, esitä ristiriita ja sen ajankohta. Älä yhdistä ristiriitaisia lukuja tai tapahtumakuvauksia yhdeksi näennäisen varmaksi väitteeksi.

### 2.3 Sidonnaisuudet, korjaukset ja aiemmat ongelmat

Arvioi lähteen omistus, rahoitus, kaupalliset tai organisatoriset intressit, suhde uutisen osapuoliin ja mahdollinen markkinointi- tai faniasema silloin, kun ne voivat vaikuttaa väitteen todistusrooliin. Virallinen lähde voi olla ensisijainen mutta samalla oman organisaationsa etua edustava.

Tarkista julkaisijan korjauskäytäntö, kirjoittajan nimi ja vastuu, alkuperäislähteiden linkitys sekä aiemmat olennaiset virheet tai korjaukset, jos niillä on merkitystä. Yksittäinen virhe ei automaattisesti tee kaikesta lähteen sisällöstä käyttökelvotonta, mutta toistuva tai korjaamatta jätetty virhe heikentää lähteen käyttöarvoa. Kirjaa konkreettinen havainto ja lähde; älä levitä yleistä mainetta tai perusteetonta arviota.

Katalogin reliability_note soveltuu pysyvään lähdetyyppiä koskevaan huomioon. Tapahtuma- tai juttukohtaiset sidonnaisuudet, virheet ja korjaukset kirjataan kyseisen uutisen tarkistukseen ja tarvittaessa seurantalokiin. Älä muuta luokkaa yksittäisen jutun perusteella ilman perusteltua, lähdekohtaisesti toistuvaa havaintoa.

## 3. Näyttäminen uutisraportissa

Älä käytä yhtä yleistä "luotettavuusluokitus"-merkintää tarkoittamaan molempia asioita. Näytä ne erillisillä, nimetyillä merkinnöillä:

- Väitekohtaisesti: **Väitteen varmennustaso: RIIPPUMATTOMISSA TOIMITUKSELLISISSA LÄHTEISSÄ VAHVISTETTU.**
- Lähdeluettelossa kunkin lähteen yhteydessä: **Lähteen yleinen luotettavuusluokka: B – vakiintunut toimituksellinen media.**

Kerro lähdeluettelossa myös lähteen rooli väitteessä tarvittaessa: ensisijainen lähde, riippumaton vahvistus, alkuperäinen raportti, osapuolen vastine tai vain uutisvihje. Jos sama lähde tukee useita väitteitä, älä anna sen luokalle sellaista vaikutelmaa, että kaikki väitteet olisivat automaattisesti vahvistettuja.

D-luokan lähde merkitään tarvittaessa lähdeluetteloon vihjelähteenä, mutta sitä ei lasketa itsenäiseksi toimitukselliseksi vahvistukseksi. Älä piilota lähteen luokkaa tai sen rajoitusta pelkän linkin taakse.

## 4. Rakenteinen tarkistus ja sen rajat

- schemas/lahdekatalogi.schema.json sallii lähteen yleiseksi luokaksi vain A, B, C tai D.
- Uusien julkaisulaadun porttiraporttien claim_assessments tallentaa olennaisen väitteen tunnisteen, tekstin, varmennustason ja siihen liittyvät lähteet. Kunkin lähteen source_class on A–D, source_role kuvaa roolia ja independence lähteiden suhdetta.
- schemas/julkaisuportti.schema.json tarkistaa sallitut arvot ja rakenteen. Historialliset porttiraportit saavat puuttua uudesta kentästä; kenttä kuuluu kaikkiin tämän ohjeen käyttöönoton jälkeen luotaviin porttiraportteihin.
- Testit tarkistavat luokkien ja tilojen sallitut arvot, katalogiviittaukset sekä erillisten merkintöjen esitystavan. Testit eivät arvioi, onko yksittäinen uutisväite tosi, lähde todella riippumaton tai luokitus toimituksellisesti oikea.

RSS-artikkelin teksti on edelleen lukijalle näkyvä selkokielinen esitys. Porttiraportti ja JSON-skeemat tukevat tarkistuksen jäljitettävyyttä, eivät korvaa alkuperäislähteiden lukemista.

## 5. Ylläpito

Kun lähteen rooli muuttuu tai uusi lähde lisätään, arvioi sen A–D-luokka ja päivitä yhteinen lähdekatalogi sekä skeema tarvittaessa. Kun väitteen varmennustasojen sanamuoto tai sallitut arvot muuttuvat, päivitä tämä ohje, julkaisulaadun portin skeema, testit ja niitä käyttävät automaatio-ohjeet samassa muutoksessa.

Yleiset hakustrategiat ja aihekohtaiset lähde-ehdokkaat ovat dokumentissa [Lähteet ja hakustrategia](lahteet.md). Lähdekatalogin ja käyttörekisterien tietomalli on kuvattu dokumentissa [Tietomallit ja prosessikaaviot](tietomallit-ja-prosessit.md).
