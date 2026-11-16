Ohjeversion tunniste: 1.1.0

Tehtävä: seuraa päivittäin Suomessa järjestettäviä intialaisten elokuvien näytöksiä ja ylläpidä GitHub-repositorion mikknikk/uutiset näytös-RSS-syötettä https://raw.githubusercontent.com/mikknikk/uutiset/main/feeds/intialaisten-elokuvien-naytokset.xml.

TARKOITUS JA RAJAUS
- Etsi kaikkien Intian elokuvateollisuuksien elokuvien näytöksiä Suomessa: esimerkiksi hindi-, telugu-, tamil-, kannada-, malajalam-, bengali-, marathi-, punjabi- ja muut intialaiset elokuvat.
- Sisällytä tavalliset teatterinäytökset, ennakkonäytökset, erikoisnäytökset, festivaalit ja muut yleisölle avoimet elokuvatapahtumat.
- Seuraa vähintään Finnkinon, BioRexin, Kino Reginan, Cinema Orionin ja Kino Myyrin ohjelmistoja sekä festivaaleja ja tapahtumajärjestäjiä.
- Seuraa levittäjien julkisia kanavia ja tapahtumalinkkejä:
  * FinBolly Movies: https://www.facebook.com/Finbollymovies
  * FinTamil Movies: https://www.facebook.com/fintamil.movies
  * Rasa Entertainment: https://www.facebook.com/298328530028338/
- Käytä myös hakukoneita, teatterien ohjelmistoja, lipunmyyntipalveluita, tapahtumasivuja ja muita kolmannen osapuolen lähteitä. Älä rajoitu edellä mainittuihin lähteisiin.

NÄYTÖKSEN HYVÄKSYMISKRITEERIT
- Kolmannen osapuolen ilmoitus riittää näytöksen sisällyttämiseen, kun elokuva, tapahtumapaikka, päivämäärä ja kellonaika ovat tunnistettavissa. Teatterin tai järjestäjän omaa vahvistusta ei vaadita.
- Merkitse jokaisen näytöksen lähteen luonne täsmällisesti yhdellä tunnisteella:
  * TEATTERIN VAHVISTAMA
  * JÄRJESTÄJÄN ILMOITTAMA
  * KOLMANNEN OSAPUOLEN ILMOITTAMA
- Älä koskaan esitä kolmannen osapuolen ilmoitusta teatterin tai järjestäjän vahvistamana.
- Tallenna sisäiseen lähdeseurantaan suora lähde- tai lipunmyyntilinkki, julkaisija, julkaisupäivä jos saatavilla, tarkistuspäivä sekä mahdolliset ristiriidat ja epävarmuudet. Tallenna lähdetiedot sisäiseen seurantaan ja lisää RSS-itemin `<description>`-sisällön loppuun otsikoitu lähdeluettelo kuvaavine lähdelinkkeineen. Älä käytä item-tason `<link>`-elementtiä.
- Älä keksi näytöksiä, kellonaikoja, osoitteita, linkkejä, tekstitystietoja tai lipun saatavuutta. Jos jokin tieto ei ole saatavilla, jätä se pois tai merkitse tuntemattomaksi.
- Facebook-sivujen saavutettavuus tai hakukoneindeksoinnin puutteet eivät todista, ettei näytöksiä olisi. Kerro tarkistusrajoitteesta raportissa, jos se vaikuttaa kattavuuteen.

TEHTÄVÄKOHTAINEN TARKISTUS
- Tarkista uudet ja muuttuneet näytöstiedot edellisen onnistuneen näytösseurantavuoron jälkeen. Ilmoita raportissa täsmällinen seurantajakso alku- ja loppuaikoineen Europe/Helsinki-ajassa (päivittäisajossa edellisen onnistuneen näytösvahdin tarkistuksen jälkeen).
- Esitä aktiivisen näytöslistan osassa vain tulevat näytökset. Kun näytöksen alkamisaika on ohitettu, merkitse se muutoshistoriassa tilaan `completed` ja siirrä se uusimman RSS-itemin lopussa olevaan erilliseen **Historialliset näytösajat** -osioon. Historiallisia näytösaikoja ei lasketa tulevien näytösten määrään. Älä käsittele mennyttä näytösaikaa peruttuna tai ohjelmistosta poistettuna.
- Vertaile löydöksiä nykyiseen feeds/intialaisten-elokuvien-naytokset.xml-syötteeseen ja aiempiin tarkistustuloksiin. Älä ilmoita samaa muuttumatonta näytöstä uudelleen uutena.
- Ilmoita käyttäjälle vain uusista näytöksistä ja olennaisista muutoksista, kuten ajan, paikan, tekstityksen, lipputilanteen tai peruutuksen muutoksista. Jos uusia tai muuttuneita tietoja ei löydy, älä lähetä turhaa ilmoitusta.
- Jos lähteiden tiedot ovat ristiriidassa, älä ratkaise ristiriitaa arvaamalla. Näytä ristiriita ja lähteet.

KINOON-LÖYTÖJEN TEATTERILINKKIEN JÄLJITTÄMINEN
- Kun löydät näytöksen Kinoon-sivustolta, älä tyydy käyttämään Kinoon-linkkiä. Etsi aina lisäksi kyseisen elokuvan tai näytöksen vastaava sivu teatterin omilta verkkosivuilta tai lipunmyynnistä (esimerkiksi Finnkino, BioRex, Kino Regina, Cinema Orion tai Kino Myyri).
- Hae elokuvan nimellä ja teatterilla sekä tarkista teatterin ohjelmisto, elokuvan esityssivu ja lipunmyyntisivu. Varmista, että kyseessä on sama näytös: elokuva, teatteri, päivämäärä ja kellonaika täsmäävät. Älä yhdistä samannimisiä elokuvia tai eri näytösaikoja.
- Jos teatterin oma näytös- tai lipunmyyntisivu löytyy ja tiedot täsmäävät, käytä sitä RSS-rivin linkkinä Kinoon-linkin sijasta. Jos teatterin omalta sivulta löytyy elokuvasivu mutta ei yksittäistä näytösaikaa, käytä sitä vain, jos se yksiselitteisesti tukee kyseistä näytöstä.
- Jos teatterin omaa linkkiä ei löydy, ei ole julkisesti saatavilla tai vastaavuutta ei voida varmistaa, säilytä Kinoon-linkki. Älä koskaan keksi tai arvaa URL-osoitetta.
- Kirjaa sisäiseen seurantaan myös Kinoon-löydön rinnalla tarkistettu teatterin oma linkki tai tieto siitä, ettei sopivaa linkkiä löytynyt.


MUUTOSHISTORIAN KONEELLINEN YLLÄPITO
- Ylläpidä näytöskohtaista nykytilaa ja vain lisäämällä ylläpidettävää muutoslokia tiedostossa data/naytosten-muutoshistoria.json. Tietomallin yksityiskohdat ovat docs/nayostohistorian-rakenne.md-tiedostossa, ja koneellinen rakenne validoidaan tiedoston schemas/naytosten-muutoshistoria.schema.json JSON Schema -määrittelyä vasten.
- Lue jokaisen ajon alussa koko muutoshistoria sekä näytös-RSS:n viimeisimmät julkaisuversiot. Vertaa uusia havaintoja JSON-tiedoston screenings-listan edelliseen tilaan.
- Pidä screening_id pysyvänä, vaikka näytöksen kellonaika, päivämäärä tai paikka muuttuu. Älä luo muutokselle uutta tunnistetta.
- Lisää jokaisesta todellisesta muutoksesta oma tapahtuma events-listaan. Tapahtumassa on yksilöllinen event_id, observed_at-aikaleima, tyyppi, näytöstunniste, previous- ja current-tilanne, lähteet sekä lyhyt selitys. Muodosta event_id deterministisesti, jotta saman ajon uusintakäsittely ei lisää duplikaattia.
- Sallitut tapahtumatyypit ovat baseline_created, added, time_changed, venue_changed, details_changed, cancelled, removed_from_listing, reinstated ja correction. Älä muuta tai poista aiempia tapahtumia; korjaa virhe uudella correction-tapahtumalla.
- Erota nimenomainen peruutus ohjelmistosta katoamisesta. Käytä cancelled-tyyppiä vain, kun lähde kertoo peruutuksesta. Jos näytös on kadonnut ohjelmistosta eikä peruutusta vahvisteta, käytä removed_from_listing-tyyppiä ja removed-tilaa.
- Säilytä jokaisen näytöstietueen ja tapahtuman yhteydessä lähteen julkaisija, suora URL, tarkistusaika, mahdollinen julkaisuaika ja vahvistustaso (TEATTERIN VAHVISTAMA, JÄRJESTÄJÄN ILMOITTAMA tai KOLMANNEN OSAPUOLEN ILMOITTAMA). Älä korota vahvistustasoa.
- Päivitä screenings-lista viimeisimpään varmennettuun tilaan. Älä lisää tapahtumaa muuttumattomasta näytöksestä. Jos lähteet ovat ristiriidassa, säilytä ristiriita ja lähteet.
- Nykyistä RSS-historiaa ei saa muuntaa takautuviksi tapahtumiksi ilman luotettavaa näyttöä. Ensimmäisessä onnistuneessa ajossa muodosta nykyisistä lähteistä ja viimeisimmästä RSS-versiosta lähtötilanne, lisää yksi baseline_created-tapahtuma ja vaihda baseline_status arvoon active. Älä väitä aiempien muutosten tarkkoja aikoja tunnetuiksi.
- Älä merkitse näytösvahdin ajoa onnistuneeksi äläkä päivitä data/seurantatila.json-tiedoston näytösvahdin aikaleimoja ennen kuin muutoshistoria, mahdolliset RSS-muutokset ja muutetut tiedostot on kirjoitettu GitHubiin ja luettu takaisin onnistuneesti.

RSS-SYÖTTEEN RAKENNE JA PÄIVITYS
- Päivitä repositorion feeds/intialaisten-elokuvien-naytokset.xml-tiedosto suoraan GitHubiin, jos käytettävissä olevat oikeudet ja työkalut sen sallivat. Älä väitä päivitystä tehdyksi, ellei GitHub-palvelu ole vahvistanut muutosta.
- RSS-syötteessä julkaistaan ensimmäisellä löytymiskerralla yksi <item> per elokuva. Kun saman elokuvan näytöstiedoissa tapahtuu myöhemmin muutos, älä korvaa aiempaa itemiä: lisää samaan feeds/intialaisten-elokuvien-naytokset.xml-syötteeseen uusi item, jossa on koko ajantasainen näytöslista.
- Säilytä kaikki aiemmat julkaisuversiot syötteessä muutoshistoriana. Aiemmat versiot ovat vertailupohjia, vaikka niiden näytösajat olisivat sittemmin menneitä tai poistuneita; vain uusimmassa versiossa näytetään voimassa olevat tulevat näytökset.
- Jokaisen uuden päivitysitemin otsikossa on elokuvan nimi ja selkeä päivitysaika Suomen paikallisessa ajassa, esimerkiksi "Klara ja aurinko – näytöstiedot päivitetty 15.11.2026 klo 19.30".
- Jokaisen itemin kuvauksessa esitä ensin koko julkaisuhetken tulevien näytösten lista. Lisää sen jälkeen erillinen **Historialliset näytösajat** -osio, jossa alkamisaikansa ohittaneet `completed`-tietueet esitetään erillään tulevista näytöksistä. Älä laske niitä tulevien näytösten määrään. Lisää tämän jälkeen erillinen osio "Muutokset edelliseen julkaisuun", jossa eritellään lisätyt, poistetut/perutut ja muuttuneet näytökset sekä muuttuneet teatteri-, aika-, esityskieli-, tekstitys- ja linkkitiedot.
- Vertaa aina saman elokuvan välittömästi edelliseen julkaistuun itemiin. Ensimmäisessä julkaisussa ilmoita "Ensimmäinen julkaisu". Älä julkaise uutta itemiä, ellei tietoa ole oikeasti muuttunut.
- Anna jokaiselle julkaisuversiolle oma yksilöllinen ja pysyvä GUID, joka pysyy samana saman julkaisutapahtuman uusintakäsittelyssä. Muodosta se deterministisesti elokuvan tunnisteesta, päivityshetkestä ja muutoksen sisällöstä.
- Aseta pubDate todelliseen julkaisuhetkeen ja järjestä itemit uusimmasta vanhimpaan. Päivitä kanavan lastBuildDate.
- Älä lisää item-tason <link>-elementtiä. Kanavatason linkki on sallittu; koko raportti ja lopun otsikoitu lähdeluettelo julkaistaan `<description>`-elementissä CDATA-alueena.
- Esitä näytökset mahdollisimman kompaktisti mutta selkeästi. Ryhmittele yhden elokuvan näytökset paikkakuntien alaotsikoihin: Pääkaupunkiseutu (Helsinki, Espoo ja Vantaa) on aina ensimmäinen yhteinen ryhmä; sen jälkeen muut kaupungit omina alaotsikoinaan aakkosjärjestyksessä. Jos näytösilmoituksesta puuttuu teatterin paikkakunta, selvitä teatterin sijaintikaupunki sen nimen perusteella. Tarkista sijainti ensisijaisesti teatterin omilta sivuilta tai muusta luotettavasta lähteestä ja käytä selvitettyä kaupunkia ryhmittelyssä. Älä jätä paikkakuntaa ilmoittamatta vain siksi, ettei se esiinny alkuperäisessä ilmoituksessa. Käytä ryhmää "Paikkakunta ilmoittamatta" vain, jos teatterin sijaintia ei voi luotettavasti varmistaa.
- Lajittele kunkin ryhmän näytökset päivämäärän ja kellonajan mukaan varhaisimmasta alkaen. Pääkaupunkiseudun kaikkien kaupunkien näytökset ovat samassa ryhmässä ja samassa aikajärjestyksessä.
- Selvitä ja ilmoita näytösrivillä mahdollisuuksien mukaan sekä elokuvan esityskieli (alkuperäinen kieli tai dubbauskieli sen mukaan, mitä kyseisessä näytöksessä esitetään) että tekstityksen kieli tai kielet. Tarkista tiedot ensisijaisesti teatterin omalta näytös- tai lipunmyyntisivulta, sitten järjestäjän tai levittäjän ilmoituksesta ja tarvittaessa muusta luotettavasta lähteestä. Erota selvästi esityskieli ja tekstityskieli; älä päättele niitä elokuvan alkuperämaasta tai yleisistä julkaisutiedoista. Jos tietoa ei löydy tai sitä ei voi varmistaa juuri kyseiseen näytökseen, jätä kyseinen tieto pois äläkä arvaa.
- Näytösrivillä näytä päivämäärä ja kellonaika muodossa "12.11. klo 17.00", tapahtumapaikka/teatteri sekä tarvittaessa kieli ja tekstitykset, jos ne on ilmoitettu. Älä lisää vuosilukua joka riville, ellei se ole tarpeen päivämäärien erottamiseksi.
- Älä näytä "Tila"- tai vahvistustasotekstiä, älä lisää "(Suomen aikaa)" -tekstiä äläkä käytä erillistä "Lähde:"-tekstiä. Suomen paikallinen aika on oletus.
- Kun löydät näytöksen esimerkiksi Kinoonista tai muusta kolmannen osapuolen koontipalvelusta, etsi aina erikseen myös saman näytöksen tai elokuvan näytöslistan linkki kyseisen teatterin omilta sivuilta (esim. Finnkino, BioRex, Kino Regina, Cinema Orion, Kino Myyri tai muu näytöspaikka). Hae elokuvan nimellä, teatterin nimellä, kaupungilla ja näytöspäivällä. Tarkista myös teatterin oma ohjelmisto ja lipunmyyntisivu; älä tyydy koontipalvelun linkkiin ennen kuin teatterin oma sivu on etsitty. Jos teatterin omaa linkkiä ei löydy, kokeile levittäjän omaa ilmoitusta ja käytä vasta sen jälkeen kolmannen osapuolen lähdettä. Älä kuitenkaan keksi tai arvaa URL-osoitteita, äläkä linkitä yleiselle sivulle tavalla, joka antaa ymmärtää sen olevan kyseisen näytöksen sivu.
- Valitse näytösrivin linkkilähde tässä etusijajärjestyksessä: 1) teatterin omat sivut (ensisijaisesti kyseisen elokuvan näytös- tai lipunmyyntisivu), 2) levittäjän oma julkaisu, 3) vasta näiden puuttuessa kolmannen osapuolen sivusto. Älä valitse kolmannen osapuolen koontisivua, jos teatterin oma näytössivu on saatavilla. Jos teatterin sivuilta ei löydy näytöstä, tarkista levittäjän julkaisut ennen kolmannen osapuolen lähteitä. Käytä suoraa ja mahdollisimman täsmällistä linkkiä juuri kyseiseen näytökseen tai näytöslistaan.
- Jokaisella näytösrivillä voi olla oma klikattava linkki HTML-ankkurina `<description>`-sisällössä. Linkin tekstistä pitää selvitä lähteen/julkaisijan nimi (esim. "Finnkino", "FinTamil Movies" tai "Kinoon"); älä kirjoita erillistä Lähde-tekstiä linkin ulkopuolelle. Säilytä lähteen todellinen tyyppi sisäisessä seurannassa.
- Lähteen tyyppi ja vahvistustaso on silti tarkistettava ja säilytettävä sisäisessä lähdeseurannassa, mutta niitä ei näytetä kompaktissa RSS-näytöslistassa. Älä menetä tietoa siitä, oliko ilmoitus teatterin, järjestäjän vai kolmannen osapuolen julkaisema.
- Älä lisää item-tason <link>-elementtiä. Kanavatason linkki on sallittu.
- Poista menneet, perutut ja vanhentuneet näytösajat vain uusimmasta ajantasaisesta julkaisuversiosta. Älä poista vanhoja RSS-itemeitä: ne säilytetään historiallisina julkaisuina.
- Jos elokuvalla ei enää ole tulevia näytöksiä, julkaise uusi päivitysitem, jossa tämä kerrotaan ja muutokset-osiossa eritellään poistuneet/perutut ajat.
- Tarkista ennen kirjoitusta, ettei täsmälleen sama päivitysitem ole jo julkaistu. Varmista XML:n jäsennettävyys, GUIDien yksilöllisyys, aikaleimat, muutoslistan oikeellisuus, tulevien ja historiallisten näytösaikojen erottelu sekä item-tason <link>-elementtien puuttuminen.

ENNEN JOKAISTA AJOA – DOKUMENTAATION ESITARKISTUS
- Avaa repositorion mikknikk/uutiset ajon alussa ja lue aina ajantasaiset docs/intialaisen-elokuvan-ohje.md-, docs/intialaisen-elokuvan-lahteet.md- ja docs/intialaisen-elokuvan-seuranta.md-tiedostot ennen näytöshakua.
- Noudata niiden voimassa olevia näytösseurannan rajauksia, lähteitä, hyväksymiskriteerejä, deduplikointia ja RSS-julkaisuohjeita. Älä luota pelkästään aiempaan ajokertaan tai promptin muistikuviin.
- Jos dokumentaatio ei ole saatavilla, älä oleta sen sisältöä; kerro rajoitteesta vain, jos se vaikuttaa haun kattavuuteen tai julkaisuun.

LÄHTEET JA DOKUMENTOINTI
- Noudata repositorion docs/intialaisen-elokuvan-ohje.md-, docs/intialaisen-elokuvan-lahteet.md- ja docs/intialaisen-elokuvan-seuranta.md-tiedostojen voimassa olevia ohjeita ja pidä näytösvahtiin liittyvät lähdetiedot ajan tasalla, jos löydät uusia luotettavia lähteitä.
- Älä muuta uutisraportin sisältöä tai sen RSS-syötettä tässä tehtävässä; tämä automaatio vastaa vain näytösseurannasta ja feeds/intialaisten-elokuvien-naytokset.xml-syötteestä.
- Käytä Suomen paikallista aikaa (Europe/Helsinki) näytösaikojen esittämiseen.
- Jos päivän tarkistuksessa ei löydy uutta tai muuttunutta tietoa, älä julkaise tarpeetonta ilmoitusta.


TUOTANTOMAIDEN EPÄSELVÄT RAJATAPAUKSET
- Sisällytä näytösvahtiin myös rajatapaukset, joissa elokuvan intialaisuus tai tuotantomaat ovat epäselviä tai monikansallisen yhteistuotannon vuoksi tulkinnanvaraisia (esimerkiksi käyttäjän mainitseman Klara ja Aurinko -tapauksen kaltaiset tilanteet). Älä rajaa elokuvaa pois vain siksi, ettei Intiaa ole yksiselitteisesti merkitty tuotantomaaksi.
- Arvioi tapaus elokuvakohtaisesti luotettavien lähteiden perusteella. Riittävä peruste voi olla esimerkiksi intialainen tuotantoyhtiö, intialainen yhteistuotantokumppani, intialainen levittäjä tai muu olennainen ja dokumentoitavissa oleva yhteys Intian elokuvateollisuuteen. Pelkkä näyttelijän intialainen tausta ei yksin riitä.
- Lisää tällainen näytös RSS-syötteeseen, jos yhteys Intian elokuvateollisuuteen on uskottava mutta tuotantomaat tai elokuvan luokittelu jäävät epäselviksi. Selitä itemin kuvauksessa lyhyesti, miksi elokuva on mukana ja mikä tuotantomaissa tai luokittelussa on epäselvää. Käytä täsmällistä, neutraalia ilmaisua; älä esitä epävarmaa tuotantomaata vahvistettuna tietona.
- Kerro mahdollisuuksien mukaan, mitä lähteet ilmoittavat tuotantomaiksi ja mitä intialaista yhteyttä on löydetty. Linkitä selityksessä olennaisiin lähteisiin, jos saatavilla. Jos näyttö Intia-yhteydestä on liian heikkoa, älä sisällytä elokuvaa, vaan kirjaa epävarmuus sisäiseen seurantaan.

SAAVUTETTAVUUS – PAKOLLINEN JULKAISUKRITEERI (WCAG 2.2 AAA TAVOITETASO)
Kaiken GitHub-repositorioon julkaistavan sisällön, HTML:n, RSS-syötteiden, dokumentaation, linkkien ja kuvien tulee olla mahdollisimman saavutettavaa. Tavoittele WCAG 2.2 AAA -tasoa kaikilta soveltuvilta osin. Älä väitä AAA-vaatimusten täyttyvän ilman asianmukaista testausta; kirjaa soveltumattomat tai täyttymättä jäävät kriteerit ja niiden syyt.
- Käytä selkeää suomea, kuvaavia väliotsikoita, lyhyitä kappaleita ja loogista otsikkohierarkiaa. RSS-artikkelissa yksi h1, sen alla h2-osat, h3-aliosat jne.; älä hyppää otsikkotasoja.
- Käytä semanttista HTML:ää, oikeaa kieltä (fi; vieraskielisille osuuksille tarvittaessa lang), listoja ja taulukoiden otsikkosoluja tarkoituksenmukaisesti.
- Kaikkien linkkien tulee olla ymmärrettäviä irrallaan ympäröivästä tekstistä. Vältä "klikkaa tästä", paljaita URL-osoitteita ja yksisanaisia yleislinkkejä. Näytöslinkeissä säilytä lähteen nimi ja lisää yksilöivä elokuvan/näytöslistan kuvaus, esim. "Kinoon – Ramayanan esitysajat".
- Kuville aina tarkoituksenmukainen alt-teksti (koristekuville tyhjä alt); älä välitä olennaista tietoa vain kuvassa tai värillä. Videoille tekstitykset/tekstivastineet, jos saatavilla.
- Kontrastitavoite: normaaliteksti vähintään 7:1 ja suuri teksti vähintään 4,5:1 sekä vaaleassa että tummassa tilassa. Älä käytä väriä ainoana tiedon välityskeinona.
- Sivun tulee toimia näppäimistöllä, ruudunlukijalla, vähintään 320 CSS-pikselin leveydellä ja 200–400 % suurennuksella. Fokus on näkyvä; käytä sivulla ohituslinkkiä ja semanttisia maamerkkejä.
- Vältä automaattisesti käynnistyvää mediaa, vilkkumista ja tarpeettomia aikarajoja. Huomioi käyttäjän liike- ja kontrastiasetukset.
- Ennen julkaisua validoi XML/HTML ja tarkista otsikkohierarkia, linkkitekstit, alt-tekstit, kielimääritys, kontrasti, näppäimistökäyttö, responsiivisuus ja ruudunlukijanäkymä mahdollisuuksien mukaan. Lighthouse/axe ei yksin todista AAA-tasoa.
- Päivitä tarvittaessa docs/intialaisen-elokuvan-ohje.md:n saavutettavuusohje ja docs/intialaisen-elokuvan-seuranta.md:n testitiedot. Älä merkitse testaamatonta tarkistusta hyväksytyksi.

YHDISTETTY AJOSYKLI
Tämä näytösseuranta suoritetaan erillisellä päivittäisellä Intialaisten elokuvien näytösvahti -automaatiolla, ei docs/tehtavajono.md:n aihekierrossa. Se käyttää tämän repositorion `feeds/intialaisten-elokuvien-naytokset.xml`-syötettä ja päivittää tämän repositorion näytöshistoriaa. Uutisraportin ohjeet ovat docs/intialaisen-elokuvan-uutiset.md. Pidä uutis- ja näytös-RSS:t, seurantalokit ja raportointi erillään.
