# Aiheseuranta-julkaisualustan tavoitearkkitehtuuri

**Versio:** 2.0.0  
**Päiväys:** 2026-11-19  
**Tila:** suunnitteluratkaisu; ei tuotantokäyttöönottoa  
**Liittyvät tiketit:** [#169 – Yleinen ja versioitu julkaisupakettisopimus](https://github.com/mikknikk/aiheseurain/issues/169), [#167 – Eristetty vastaanottorajapinnan prototyyppi](https://github.com/mikknikk/aiheseurain/issues/167), [#170 – Aiheseuranta-repositorion perustaminen](https://github.com/mikknikk/aiheseurain/issues/170), [#171 – Vastaanotto- ja julkaisupalvelu](https://github.com/mikknikk/aiheseurain/issues/171), [#172 – Aiheseuraimen lähettäjä](https://github.com/mikknikk/aiheseurain/issues/172), [#173 – Varjo- ja rinnakkaisjulkaisu](https://github.com/mikknikk/aiheseurain/issues/173), [#174 – RSS-lukijan URL-siirtymä](https://github.com/mikknikk/aiheseurain/issues/174), [#175 – Tuotannon hallittu siirto](https://github.com/mikknikk/aiheseurain/issues/175)

## 1. Päätös lyhyesti

Erillisen julkaisualustan nimi on **Aiheseuranta** ja tavoiteltu GitHub-reponimi on `aiheseuranta`. Se toimii yleisenä, itsenäisenä vastaanottajana, pysyvänä julkaisuartefaktien varastona ja julkisena RSS-jakelualustana. Se ei ole vain Aiheseuraimen alipalvelu: myös muut toisistaan riippumattomat sisällöntuottajat voivat lähettää sille sopimuksen mukaisia julkaisuja.

Aiheseurain säilyy ensimmäisenä sisällöntuottajana ja vastaa omasta sisällöntuotannostaan, lähteistään, semanttisesta validoinnistaan sekä täydellisen julkaisupaketin muodostamisesta. Aiheseuranta vastaanottaa paketin; se ei hae tiedostoja lähettäjän repositoriosta eikä tarvitse lähettäjän saatavuutta onnistuneen vastaanoton jälkeen.

Aiheseuranta-repositorio pidetään mahdollisimman minimaalisena. Siihen tulee vain vastaanoton, valtuutuksen, yleisen eheyden tarkistamisen, säilyttämisen, julkaisemisen, takaisinluvun ja palautuksen kannalta välttämätön sisältö ja toiminnallisuus. Minimaalisuus ei saa heikentää turvallisuutta, atomisuutta, palautettavuutta tai auditointia.

Tämä on tavoitetila, ei nykyinen tuotantototeutus. Nykyinen Pages-julkaisu ja RSS-osoitteet säilyvät ennallaan, kunnes rinnakkaisjulkaisu on varmennettu ja erillinen tuotantosiirto hyväksytty.

## 2. Vastuurajat ja riippumattomuus

| Vastuu | Aiheseurain ja muut lähettäjät | Aiheseuranta |
|---|---|---|
| Aihekohtainen tutkimus, lähteet ja raporttien kirjoittaminen | Omistaa | Ei sisällä |
| Sisällön ja lähteiden toimituksellinen/semanttinen validointi | Omistaa | Ei tee |
| RSS:n aihekohtaiset säännöt ja lähettäjäkohtaiset tarkistukset | Omistaa | Ei kopioi |
| Julkaisupaketin muodostaminen ja lähettäminen | Omistaa | Vastaanottaa |
| Lähettäjän tunnistus ja kohdekohtainen valtuutus | Käyttää myönnettyä oikeutta | Valvoo |
| Sopimusversion, manifestin, polkujen, kokojen ja tiivisteiden tarkistus | Muodostaa sopimuksen mukaisen paketin | Tarkistaa yleisen eheyden |
| Julkaisuerän atominen tallennus ja järjestyksen valvonta | Ei hallitse vastaanottajan tilaa | Omistaa |
| Julkinen Pages-julkaisu, takaisinluku ja viimeisen hyvän version palautus | Varmistaa vastaanottokuittauksen | Omistaa |
| Julkaisu- ja vastaanottoloki | Säilyttää oman lähetysajon viitteen | Säilyttää vastaanoton ja kohdejulkaisun välttämättömät auditointitiedot |

Lähettäjän, julkaisukohteen ja julkaisuerän tunnisteet ovat eri asioita. Yksi lähettäjä voi omistaa useita syötteitä. Jokaisella julkaisukohteella on yksiselitteinen omistaja, eikä lähettäjä voi kirjoittaa toisen lähettäjän kohteisiin. Aiheseurannan ei tarvitse tietää, miten lähettäjä keräsi tai tuotti sisältönsä.

## 3. Minimaalisuusperiaate ja repositorion sisältö

Aiheseurannan jokaisella tiedostolla ja komponentilla pitää olla nimettävissä oleva, välttämätön tehtävä tässä ketjussa: vastaanotto → valtuutus ja eheystarkistus → atominen säilytys → julkaisu → takaisinluku → palautus.

Repositorioon ei lisätä:
- uutis- tai lähdehakua, raporttien kirjoittamista tai sisällöntuotantoa;
- lähettäjäkohtaisia aiheohjeita, lähderekistereitä tai semanttisia validaattoreita;
- automaatioiden ajastusta tai seurantatilaa;
- RSS-lukijan käyttöliittymää, Valvomoa tai Kehitysjonoa;
- monimutkaisia palvelukerroksia, tarpeettomia riippuvuuksia tai saman tiedon rinnakkaisia tilakopioita;
- dokumentaatiota, joka vain toistaa lähettäjien omia ohjeita.

Välttämättömiä vastaanottosopimuksen, käyttöoikeuksien, julkaisumanifestin, viimeisen hyvän version ja palautuksen tietoja ei kuitenkaan saa poistaa vain tiedostomäärän pienentämiseksi.

Tavoiteltu sisältö pidetään pienenä. Tarkka tiedostorakenne ja se, mitkä tarkistukset voidaan toteuttaa työnkulussa ilman erillistä palvelukoodia, ratkaistaan tiketeissä #169 ja #171. Rakenteen tulee sisältää vain:
- vastaanottotyönkulku ja sen mahdollisesti tarvitsema pieni toteutus;
- yleisen julkaisupakettisopimuksen koneellisesti tarkistettava määrittely;
- vastaanotetut julkiset julkaisuartefaktit;
- suppea manifesti-/tilatieto, jota tarvitaan järjestyksen, eheyden, takaisinluvun ja palautuksen varmistamiseen.

## 4. Julkaisupakettisopimus ja monen lähettäjän malli

Jokainen lähettäjä toimittaa itsenäisen, täydellisen ja muuttumattoman paketin. Paketti sisältää kaikki erään kuuluvat julkaisutiedostot sekä manifestin. Vähintään seuraavat tiedot määritellään sopimuksessa:
- sopimusversion tunniste;
- pysyvä lähettäjätunniste;
- julkaisukohteiden pysyvät tunnisteet ja sallitut polut;
- julkaisuerän yksilöllinen tunniste ja idempotenssiavain;
- lähettäjäkohtainen monotoninen järjestysnumero tai muu yksiselitteinen versio;
- lähderepon nimi ja lähdecommit vain jäljitettävyysmetatietona, ei vastaanoton riippuvuutena;
- kunkin tiedoston polku, tavumäärä ja SHA-256-tiiviste;
- tarvittavat RSS-kohtaiset yleiset tarkistusmetatiedot, kuten item-määrä ja GUID-lista.

Aiheseuranta tarkistaa sopimusversion, lähettäjän oikeuden, kohteiden omistajuuden, paketin täydellisyyden, sallittujen polkujen ja kokorajojen noudattamisen, tiivisteet sekä järjestyksen. Vastaanottaja ei yritä todistaa raporttien uutisarvoa, lähteiden luotettavuutta tai muita lähettäjän sisältökohtaisia asioita.

Sopimus suunnitellaan usealle lähettäjälle alusta alkaen. Testeissä on vähintään kaksi toisistaan riippumatonta synteettistä lähettäjää, joilla on erilliset kohdealueet. Yhden lähettäjän virhe, väärä polku tai luvaton kirjoitus ei saa vaikuttaa toisen lähettäjän julkaisuihin.

## 5. RSS GUID -käytäntö

Uusien RSS-itemien GUID muodostetaan seuraavassa muodossa:

```text
urn:aiheseurain:<aihe>:<alkuperäinen-päivämäärä>:<uuid>
```

Esimerkki:

```text
urn:aiheseurain:tolkien:2026-11-19:8f14e45f-ea12-4d2a-9c31-6e8b7f123456
```

Osien merkitys:
- `urn:aiheseurain` on pysyvä tunnisteavaruuden nimi. Se kertoo tunnisteiden alkuperäisestä tunnisteavaruudesta, ei nykyisen GitHub-repositorion tai julkaisupalvelun nimestä.
- `<aihe>` on vakaa, koneellinen aihe-/syötetunniste, esimerkiksi `tolkien`. Se ei ole vapaasti muuttuva näyttönimi.
- `<alkuperäinen-päivämäärä>` on artikkelin alkuperäinen raportointipäivä ISO-muodossa `YYYY-MM-DD`. Se ei muutu uudelleenjulkaisun, korjauksen tai päivityksen yhteydessä.
- `<uuid>` on kerran luotu yksilöllinen UUID; suositeltu versio on UUID v4.

GUID luodaan kerran ja tallennetaan artikkelin pysyvien tietojen yhteyteen. Sitä ei muodosteta uudelleen otsikosta, URL-osoitteesta, sisällöstä, julkaisuajasta, päivitysajasta, lähettäjän repositorion nimestä eikä Aiheseurannan nimestä. Artikkelin päivitys, uudelleenjulkaisu, repositorion uudelleennimeäminen tai siirto toiselle julkaisualustalle ei muuta GUIDia.

RSS:ssä käytetään muotoa `<guid isPermaLink="false">…</guid>`, koska GUID ei ole avattava URL-osoite.

**Yhteensopivuus:** käytäntö koskee uusia itemeitä. Kaikki jo julkaistut GUIDit säilytetään täsmälleen ennallaan; niitä ei muuteta eikä generoida uudelleen uuden käytännön käyttöönotossa. Aiheseuranta vastaanottaa ja julkaisee lähettäjän toimittamat GUIDit muuttamatta niitä.

## 6. Atominen vastaanotto, julkaisu ja takaisinluku

Julkaisun tulee olla eräkohtainen, idempotentti ja takaisinluettava.

1. **Lähettäjän hyväksyntä:** lähettäjä validoi oman sisältönsä, RSS-rakenteensa, GUIDit, aihe-erottelun ja kaikki omat semanttiset sääntönsä ennen lähettämistä.
2. **Pakettierän muodostus:** lähettäjä kokoaa kaikki erään kuuluvat tiedostot, manifestin ja SHA-256-tiivisteet yhdeksi muuttumattomaksi paketiksi.
3. **Tunnistus ja valtuutus:** Aiheseuranta tunnistaa lähettäjän ja tarkistaa, että tällä on kirjoitusoikeus jokaiseen paketin kohteeseen.
4. **Eheyden tarkistus:** vastaanottaja tarkistaa sopimusversion, manifestin, tiedostojen täydellisyyden, sallitut polut ja koot sekä tiivisteet ennen kirjoitusta. Yhdenkin tiedoston virhe hylkää koko erän.
5. **Atominen tallennus:** koko erä tallennetaan yhtenä Git-puuna ja yhtenä commitina. Osittainen erä ei saa tulla julkiseksi.
6. **Järjestys ja rinnakkaisuus:** vastaanottaja estää vanhentunutta tai rinnakkaista erää ylikirjoittamasta uudempaa. Uusinta on idempotentti; sama erä ei tuota merkityksetöntä uutta julkaisua.
7. **Pages-julkaisu:** vasta vastaanoton ja yleisten tarkistusten onnistuttua julkaistaan uusi staattinen sisältö.
8. **Takaisinluku:** julkiset URL-osoitteet luetaan takaisin ja niiden tavut sekä SHA-256-tiivisteet verrataan hyväksyttyyn manifestiin. RSS-rakenne, GUIDit ja item-määrät tarkistetaan yleisellä tasolla.
9. **Kuittaus:** lähettäjä saa yksiselitteisen tuloksen, jossa erotetaan vastaanotettu, tallennettu, Pagesiin julkaistu ja takaisinluvulla varmennettu tila.

Jos kirjoituksen tulos jää epäselväksi, vastaanottaja lukee refit, commit-historian ja julkaisutilan ennen uusintaa. Sokkona toistuva kirjoitus ei ole sallittu.

## 7. Viimeinen hyvä julkaisu ja palautuminen

Aiheseuranta säilyttää viimeisen onnistuneen ja takaisinluvulla varmennetun julkaisun. Jos uusi julkaisu epäonnistuu tai julkinen takaisinluku ei vastaa manifestia:
- viimeisin hyvä julkaisu säilyy lukijoille saatavilla;
- epäonnistunutta ehdokasta ei merkitä onnistuneeksi;
- palautus tehdään viimeiseen varmennettuun kohdejulkaisuun ilman yhteyttä lähettäjään;
- palautuskin julkaistaan ja luetaan takaisin ennen kuin se merkitään onnistuneeksi;
- vastaanotto-, commit-, Actions- ja Pages-viitteet säilytetään virheen selvittämistä varten.

Palautus ei saa riippua Aiheseuraimen tai muun lähettäjän repositorion saatavuudesta. Aiheseurannan on pystyttävä tarjoamaan viimeisin hyvä RSS-julkaisu itsenäisesti.

## 8. Tunnistus ja oikeuksien rajaus

Lähettäjä tunnistetaan erikseen myönnetyllä, rajatulla tunnisteella. Tuotantoratkaisun ensisijainen vaihtoehto on GitHub App, joka asennetaan vain Aiheseuranta-repositorioon. Appin oikeudet rajataan välttämättömään kirjoitukseen ja metatietojen lukuun. Lähettäjäkohtaiset kohdealueet valtuutetaan erikseen.

Aiheseuranta ei saa kirjoitusoikeutta takaisin lähettäjän repositorioon. Lähettäjän salaisuuksia ei koskaan sisällytetä julkiseen pakettiin tai manifestiin. Prototyypin tunnisteet ja testirepositorio pidetään erillään tuotannosta. Tuotantorepositorion, näkyvyyden, Appin, salaisuuksien ja Pages-asetusten perustaminen vaatii erillisen hyväksynnän tiketin #170 mukaisesti.

## 9. URL-osoitteet ja siirtymä

Aiheseurannan Pages-osoitteen tavoitemuoto on:

`https://mikknikk.github.io/aiheseuranta/feeds/{lahettaja}/{syote}.xml`

Aiheseurainin syötteet ovat ensimmäinen julkaistava aineisto. Nykyiset Aiheseuraimen Pages-osoitteet säilyvät yhteensopivuuspeilinä myös siirtymän jälkeen. Vanhoja URL-osoitteita ei poisteta tai katkaista osana rinnakkaisjulkaisua.

RSS-lukijan URL-osoitteet vaihdetaan vasta, kun kaikki syötteet on julkaistu rinnakkain, niiden sisällöt ja GUIDit täsmäävät, takaisinluku toimii ja lukijan toiminta on testattu. Tuotannon ensisijaisen julkaisukohteen vaihtaminen vaatii erillisen hyväksynnän. Siirtymä ei muuta automaatioiden ajastuksia, suoritusvälejä, aikavyöhykkeitä, ohjeita, aktiivisuutta tai kohdekeskusteluja.

## 10. Vaiheistus ja päätösportit

| Vaihe | Sisältö | Ehto |
|---|---|---|
| 1. Sopimus | Yleinen, versioitu pakettisopimus, minimaalisuusperiaate ja GUID-käytäntö (#169) | Sopimus dokumentoitu ja testattavissa |
| 2. Eristetty prototyyppi | Yleinen vastaanottaja vähintään kahdelle synteettiselle lähettäjälle (#167) | Atomisuus, eristys, idempotenssi, virhetilat ja palautus testattu |
| 3. Tuotantorepo | Aiheseuranta-repo ja rajatut oikeudet (#170) | Käyttäjän erillinen hyväksyntä |
| 4. Vastaanotto ja julkaisu | Minimaalinen vastaanotto-, eheys-, Pages- ja palautustoteutus (#171) | Kaikki vastaanottajan hyväksymistestit läpäisty |
| 5. Lähettäjä | Aiheseuraimen validoidun paketin muodostus ja lähetys (#172) | Lähettäjän CI-portit ja vastaanottokuittaus toimivat |
| 6. Varjo- ja rinnakkaisjulkaisu | Kaikki kymmenen syötettä rinnakkain (#173) | Tavutasoinen vertailu, GUIDien säilyminen ja palautusharjoitus onnistuvat |
| 7. Lukijan siirtymä | RSS-lukijan uudet URL-osoitteet (#174) | Kaikki syötteet ja lukija varmennettu |
| 8. Tuotannon siirto | Aiheseuranta ensisijaiseksi julkaisukohteeksi (#175) | Erillinen nimenomainen hyväksyntä; vanha URL-peili säilyy |

Nykyinen Pages-julkaisu pysyy ennallaan vaiheiden 1–6 aikana ja kunnes hallittu siirtymä on erikseen hyväksytty. Suunnittelu, prototyyppi tai rinnakkaistesti ei itsessään anna lupaa muuttaa live-automaatioita tai niiden asetuksia.

## 11. Rajaukset

Tämä dokumentti määrittelee tavoitetilan. Se ei luo Aiheseuranta-repositoriota, GitHub Appia, salaisuuksia tai käyttöoikeuksia, eikä muuta Pages-asetuksia, nykyisiä RSS-URL-osoitteita, RSS-sisältöjä tai RSS-lukijaa. Se ei muuta automaatioiden ajastuksia, suoritusvälejä, aikavyöhykkeitä, ohjeita, aktiivisuutta tai kohdekeskusteluja eikä luo korvaavia automaatioita.
