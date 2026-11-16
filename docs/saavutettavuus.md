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
