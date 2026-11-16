# Saavutettavuus – WCAG 2.2 AAA tavoitetasona

Tämän repositorion saavutettavuuden tavoitetaso on WCAG 2.2 AAA kaikilta soveltuvilta osin, kuten aiemmassa elokuvaraportti-repositoriossa. AAA-vaatimusten täyttymistä ei saa väittää ilman asianmukaista testausta. Kirjaa rajoitteet ja parannukset.

## Kaikki julkaisut
- Kirjoita selkeää suomea, avaa lyhenteet ja jäsennä pitkät raportit kuvaavilla otsikoilla ja lyhyillä kappaleilla.
- Käytä semanttista HTML:ää ja loogista otsikkohierarkiaa. Aseta kieleksi `fi`; merkitse vieraskieliset katkelmat tarvittaessa.
- Käytä kuvaavia linkkitekstejä, jotka toimivat myös irrallaan ympäröivästä tekstistä.
- Tavallisen tekstin kontrastitavoite on vähintään 7:1 ja suuren tekstin 4,5:1.
- Informatiivisilla kuvilla on kuvaava alt-teksti, koristekuvilla tyhjä alt. Älä esitä olennaista tietoa vain kuvana.
- Käytä taulukoita vain aidolle taulukkomuotoiselle tiedolle. Varmista näppäimistö- ja ruudunlukijakäyttö, näkyvä fokus ja looginen lukujärjestys.

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
