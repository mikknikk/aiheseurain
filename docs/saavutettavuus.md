# Saavutettavuus – WCAG 2.2 AAA tavoitetasona

Tämän repositorion saavutettavuuden tavoitetaso on WCAG 2.2 AAA kaikilta soveltuvilta osin, kuten aiemmassa elokuvaraportti-repositoriossa. AAA-vaatimusten täyttymistä ei saa väittää ilman asianmukaista testausta. Kirjaa rajoitteet ja parannukset.

## Kaikki julkaisut
- Kirjoita selkeää suomea, avaa lyhenteet ja jäsennä pitkät raportit kuvaavilla otsikoilla ja lyhyillä kappaleilla.
- Käytä semanttista HTML:ää ja loogista otsikkohierarkiaa. Aseta kieleksi `fi`; merkitse vieraskieliset katkelmat tarvittaessa.
- Käytä kuvaavia linkkitekstejä, jotka toimivat myös irrallaan ympäröivästä tekstistä.
- Tavallisen tekstin kontrastitavoite on vähintään 7:1 ja suuren tekstin 4,5:1.
- Informatiivisilla kuvilla on kuvaava alt-teksti, koristekuvilla tyhjä alt. Älä esitä olennaista tietoa vain kuvana.
- Käytä taulukoita vain aidolle taulukkomuotoiselle tiedolle. Varmista näppäimistö- ja ruudunlukijakäyttö, näkyvä fokus ja looginen lukujärjestys.

## Markdown-dokumentaatio

Markdown-tiedostot ovat osa repositorion käyttöliittymää: niitä luetaan GitHubissa eri näytöillä ja myös ruudunlukijoilla. Niiden rakenteen tulee auttaa lukijaa hahmottamaan kokonaisuus ja siirtymään suoraan tarvittavaan kohtaan.

- Käytä yhtä kuvaavaa H1-pääotsikkoa ja etene otsikkotasoissa loogisesti. Älä jätä otsikkotasoja väliin äläkä korvaa otsikoita pelkällä lihavoinnilla.
- Nimeä otsikot sisällön mukaan. Pitkissä dokumenteissa käytä sisällysluetteloa tai muuta navigointia, kun se helpottaa olennaisesti selaamista.
- Kirjoita lyhyitä, aiheeltaan yhtenäisiä kappaleita. Käytä numeroitua luetteloa järjestyksessä suoritettaviin vaiheisiin ja luettelomerkkejä rinnakkaisiin asioihin.
- Käytä kuvaavia linkkitekstejä, jotka kertovat kohteesta myös irrallaan ympäröivästä tekstistä. Vältä epämääräisiä ilmauksia kuten "tästä".
- Käytä taulukoissa selkeitä otsikkosoluja ja vältä tarpeettoman leveitä tai monimutkaisia taulukoita. Jos sisältö ei ole aidosti taulukkomuotoista, käytä luetteloa.
- Merkitse tiedostonimet, polut, komennot, tunnisteet ja koodiesimerkit koodimuotoilulla. Älä käytä koodimuotoilua kokonaisille kappaleille.
- Varmista, että pitkät koodiesimerkit ovat ymmärrettäviä myös tekstimuotoisina ja että niitä edeltää selitys niiden tarkoituksesta.
- Tarkista GitHubin Markdown-esikatselussa, että otsikkorakenne, linkit, taulukot ja koodilohkot näkyvät oikein. Pelkkä visuaalinen tarkistus ei korvaa ruudunlukijan tai näppäimistön testausta silloin, kun ne ovat tarpeen.

Automaation käynnistyskehotteet tallennetaan `prompts/`-hakemistoon `.txt`-tiedostoina, koska niiden sisältö kopioidaan sellaisenaan automaation asetuksiin. Niihin ei sovelleta Markdown-dokumenttien otsikointi- tai muotoiluvaatimuksia; niiden saavutettavuus perustuu selkeään raakatekstiin, yksiselitteisiin osioihin ja siihen, ettei kopioitavaan sisältöön lisätä koristeellista merkintää. Varsinaiset ylläpito-ohjeet ovat `prompts/README.md`:ssä.

## HTML ja verkkosivu
- Käytä `lang="fi"`, kuvaavaa title-elementtiä sekä header-, nav-, main- ja footer-maamerkkejä. Tarjoa ohita navigaatio -linkki.
- Linkit erottuvat muutenkin kuin hover-tilassa. Fokus näkyy selvästi.
- Sivun tulee toimia 320 CSS-pikselin leveydellä ilman vaakavieritystä ja kestää 200–400 % suurennus.
- Huomioi vaalea ja tumma tila sekä pakotetut värit.

## RSS ja artikkelien HTML
- Koko uutis- tai näytösraportti kuuluu itemin `description`-elementtiin CDATA-alueen sisällä semanttisena HTML:nä.
- Älä käytä RSS-itemin sisällä item-kohtaista `<link>`-elementtiä. Kanavatason `<link>` ja Atomin kanavatason `atom:link rel="self"` ovat sallittuja.
- Lisää jokaisen itemin loppuun otsikoitu lähdeluettelo ja kuvaavat lähdelinkit. Näytösrivin linkit eivät korvaa lähdeluetteloa.
- Näytösraportissa elokuvan nimi on otsikko ja paikkakunnat sen alaotsikoita. Käytä listoja semanttisesti.

## Testaus ennen julkaisua
- Tarkista XML:n jäsennettävyys, CDATA ja sisäinen HTML erikseen sekä linkkien toimivuus mahdollisuuksien mukaan.
- Testaa kontrastit AAA-tavoitteilla vaaleassa ja tummassa tilassa ja pakotetuissa väreissä.
- Testaa näppäimistö, ruudunlukija, 320 CSS-pikselin näkymä ja vähintään 200 % suurennus.
- Tarkista otsikkohierarkia, kielimääritys, linkkitekstit, alt-tekstit ja taulukoiden otsikot.
- Automaattiset Lighthouse-/axe-tulokset eivät yksin todista AAA-vaatimusten täyttymistä.

## Tämän muutoksen testauksen tila
Tässä muutoksessa tarkistetaan tiedostopolut, RSS/XML:n jäsennettävyys, GUIDien yksilöllisyys, item-linkkien puuttuminen ja lähdeluettelon olemassaolo. Kontrasti-, ruudunlukija-, näppäimistö-, mobiili- ja suurennustestausta ei suoritettu, joten AAA-tason toteutumista ei väitetä varmennetuksi.


## Manuaalisen saavutettavuustestauksen menettely

Automaattiset testit eivät korvaa manuaalista arviointia. Testaa vähintään GitHubissa renderöidyt keskeiset Markdown-dokumentit sekä RSS-sisältöä näyttävä käytännössä käytetty lukija. Repositorion oma Valvomo on lisättävä testattaviin kohteisiin. Testaa myös sen lataus- ja virhetilat, automaatiokorttien erillisyys, aihekierron esitystapa ja GitHub Actions -vaiheiden ymmärrettävyys. Älä yleistä yhden selaimen tai ruudunlukijan tulosta kaikkiin käyttöympäristöihin.

### Testausympäristön kirjaaminen

Kirjaa jokaisesta testikerrasta testaaja, päivämäärä, käyttöjärjestelmä, selain ja niiden versiot, ruudunlukijan nimi ja versio, testattu näkymä tai tiedosto ja sen URL, suurennus, näkymän leveys, väritila sekä testin tulos ja toistamisvaiheet.

### Testauslista

1. **Näppäimistö:** käy sisältö läpi ilman hiirtä. Varmista looginen kohdistusjärjestys, näkyvä fokus, kaikkien linkkien ja toimintojen käyttö sekä se, ettei fokus jää loukkuun.
2. **Ruudunlukija:** tarkista pääotsikko, otsikkotasot, linkkien nimet, taulukoiden otsikot, luetteloiden rakenne, sivun kieli sekä linkkien ymmärrettävyys irrallaan ympäröivästä tekstistä.
3. **Suurennus ja responsiivisuus:** tarkista vähintään 200 % ja 400 % suurennus sekä 320 CSS-pikselin leveä näkymä. Varmista, ettei tavallinen tekstisisältö vaadi vaakavieritystä eikä tietoa tai toimintoja katoa.
4. **Kontrastit:** tarkista tekstin, linkkien, fokusmerkkien ja muiden olennaisten käyttöliittymäelementtien kontrasti. AAA-tavoitteena tavallisen tekstin kontrasti on vähintään 7:1 ja suuren tekstin 4,5:1.
5. **Väritilat:** tarkista vaalea ja tumma tila sekä pakotetut värit, jos testattu käyttöympäristö tukee niitä.
6. **Valvomo:** tarkista pääsisältöön siirtyminen, päänavigaatio, otsikkohierarkia, automaatiokorttien erottelu, tilamerkintöjen ymmärrettävyys, aihekierron lista, virhe- ja varoitustiedot sekä Actions-vaiheiden avattavat yksityiskohdat. Testaa myös tilanne, jossa JSON tai GitHub API ei vastaa.
7. **RSS-lukija:** tarkista otsikoiden ja listojen rakenne, lähdelinkkien nimet, linkkien käyttö näppäimistöllä ja ruudunlukijalla sekä se, ettei raportin sisältö riipu pelkästä visuaalisesta asettelusta.

Älä merkitse testausta tehdyksi pelkän suunnitelman, automaattisen Lighthouse-/axe-tuloksen tai GitHubin Markdown-esikatselun perusteella. Kirjaa myös epäonnistuneet ja soveltumattomat kohdat. WCAG 2.2 AAA -tason väite edellyttää kaikkien soveltuvien onnistumiskriteerien asianmukaista arviointia; tämä tarkistuslista on apuväline, ei vaatimustenmukaisuustodistus.

### Testauskerran kirjauspohja

Kopioi tämä osio uuteen testausmerkintään ja täytä vain tosiasiassa tehdyt tarkistukset.

- Päivä ja aika:
- Testaaja:
- Käyttöjärjestelmä:
- Selain ja versio:
- Ruudunlukija ja versio:
- Testattu sisältö/näkymä:
- Suurennus ja näkymän leveys:
- Väritila:

| Testi | Tulos (läpäisty / havainto / ei sovellu) | Huomiot ja toistamisvaiheet |
|---|---|---|
| Näppäimistön käyttö ja fokus | Ei testattu | |
| Ruudunlukija ja otsikkorakenne | Ei testattu | |
| 200 % ja 400 % suurennus | Ei testattu | |
| 320 CSS-pikselin näkymä | Ei testattu | |
| Kontrastit ja linkkien erottuvuus | Ei testattu | |
| Tumma tila ja pakotetut värit | Ei testattu | |
| Valvomon käyttö näppäimistöllä ja ruudunlukijalla | Ei testattu |\n| Valvomon 320 px / 200 % / 400 % -näkymä | Ei testattu |\n| Valvomon kontrastit ja väritilat | Ei testattu |\n| RSS-sisällön käyttö lukijassa | Ei testattu | |

**Yhteenveto ja avoimet löydökset:**

