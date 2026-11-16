# Saavutettavuuskatselmointi 17.11.2026

## Katselmoinnin tila

Tämä merkintä dokumentoi lähdekoodiin perustuvan saavutettavuuskatselmoinnin ja sen yhteydessä tehdyt korjaukset. Se **ei ole julkaistujen sivujen manuaalinen saavutettavuustesti eikä WCAG 2.2 AAA -vaatimustenmukaisuuden arviointi**.

Katselmointi tehtiin 17.11.2026 GitHubin lähdetiedostoista. Käytössä ei ollut selainta, jolla julkaistut Pages-sivut olisi voitu avata ja renderöidä, eikä ruudunlukijaa. Julkisten Pages-osoitteiden avaaminen ei onnistunut tässä testausympäristössä. Siksi selain-, näppäimistö-, ruudunlukija-, zoomaus- ja responsiivisuustuloksia ei merkitä läpäistyiksi.

## Tarkastettu sisältö

- Etusivu: https://mikknikk.github.io/aiheseurain/
- Valvomo: https://mikknikk.github.io/aiheseurain/valvomo/
- RSS-lukija: https://mikknikk.github.io/aiheseurain/lukija/
- Kehitysjono: https://mikknikk.github.io/aiheseurain/kehitysjono/
- Yhteinen Jekyll-sivupohja, päävalikko ja alatunniste.
- Sivuston CSS sekä Valvomon, RSS-lukijan ja Kehitysjonon JavaScript.
- README.md, docs/saavutettavuus.md, docs/kehityskaytannot.md ja docs/kehityssuunnitelma.md.

## Lähdekoodista vahvistetut asiat

- HTML-sivupohja määrittää dokumentin kieleksi suomen, viewport-metatiedon, sivun otsikon sekä header-, nav-, main- ja footer-maamerkit.
- Sivupohjassa on pääsisältöön siirtyvä ohituslinkki.
- Päänavigaatiolla on saavutettava nimi ja nykyinen sivu merkitään `aria-current`-attribuutilla.
- Lomakekentillä on niihin yhdistetyt näkyvät label-elementit.
- Dynaamisille tilatiedoille on käytetty status- ja live-alueita.
- Kehitysjonon vaihtoehtoisessa taulukkonäkymässä on kuvateksti, sarakeotsikot ja rivien otsikkosolut.
- CSS määrittää näkyvän näppäimistöfokuksen, kapean näkymän asettelut sekä pakotettujen värien tyylit.
- RSS-lukijan sisältöä ei lisätä sivulle raakana HTML-merkkijonona. Sisältö rakennetaan sallituista elementeistä, ja aktiiviset elementit sekä vaaralliset linkkiosoitteet poistetaan.

## Katselmoinnissa havaitut ja korjatut ongelmat

1. Etusivun aihekorttien RSS-linkeillä oli keskenään sama teksti. Linkkitekstit muutettiin nimeämään kyseinen aihe ja syöte, jotta linkin tarkoitus käy ilmi myös linkkiluettelossa.
2. RSS-lukijan artikkelien lähdelinkki käytti samaa yleistä nimeä jokaisessa artikkelissa. Linkkiteksti sisältää nyt myös artikkelin otsikon.
3. RSS-sisällössä oli useita `h1`-otsikoita. Niiden näyttäminen sellaisinaan loisi lukijasivulle useita päätason otsikoita. Sanitointi muuntaa artikkelisisällön `h1`-otsikot `h2)-tasolle.

Korjauksille lisättiin regressiotestit RSS-lukijan testitiedostoon. Testien suoritus varmistetaan PR:n GitHub Actions -tuloksista.

## CSS-värien kontrastilaskelmat

Seuraavat suhdeluvut on laskettu CSS:n väriarvoista WCAG:n suhteellisen luminanssin kaavalla. Ne ovat lähdekoodiin perustuvia laskelmia, eivät renderöidyn käyttöliittymän mittauksia.

| Väriyhdistelmä | Kontrasti |
|---|---:|
| Vaalea tila: tekstin väri / sivun tausta | 15,24:1 |
| Vaalea tila: himmennetty teksti / sivun tausta | 7,07:1 |
| Vaalea tila: linkki / sivun tausta | 7,95:1 |
| Vaalea tila: onnistumistila / tausta | 8,11:1 |
| Vaalea tila: varoitus / tausta | 8,46:1 |
| Vaalea tila: virhe / tausta | 8,53:1 |
| Tumma tila: tekstin väri / sivun tausta | 16,42:1 |
| Tumma tila: himmennetty teksti / sivun tausta | 12,73:1 |
| Tumma tila: linkki / sivun tausta | 10,61:1 |
| Tumma tila: onnistumistila / tausta | 9,63:1 |
| Tumma tila: varoitus / tausta | 9,14:1 |
| Tumma tila: virhe / tausta | 8,91:1 |

Laskelmat koskevat näitä nimenomaisia väriyhdistelmiä. Ne eivät kata kaikkia komponenttien, reunojen, fokusmerkkien, hover-tilojen tai mahdollisten selainkohtaisten renderöintien yhdistelmiä.

## Testit, joita ei ole vielä tehty

Seuraavat kohdat on jätettävä avoimiksi, kunnes ne suoritetaan oikeilla julkaistuilla sivuilla:

- [ ] Kaikkien neljän sivun käyttö kokonaan näppäimistöllä: kohdistusjärjestys, fokus, toimintojen käyttö ja mahdolliset fokusloukut.
- [ ] Kaikkien neljän sivun ruudunlukijatestaus sekä keskeisten dokumenttien otsikko- ja linkkirakenne.
- [ ] RSS-lukijan syötesuodattimen ja artikkelien avaamisen näppäimistö- ja ruudunlukijakäyttö.
- [ ] Kehitysjonon haun, kaikkien suodattimien ja esitystapavalinnan käyttö näppäimistöllä ja ruudunlukijalla.
- [ ] Valvomon dynaamiset tilat, virheet, varoitukset ja Actions-tiedot ruudunlukijalla.
- [ ] 200 % ja 400 % suurennus sekä 320 CSS-pikselin näkymä kaikilla sivuilla.
- [ ] Vaalea ja tumma tila sekä pakotetut värit todellisessa selaimessa.
- [ ] Selainkonsolin virheet, verkkoresurssien latautuminen ja todellinen Pages-renderöinti.
- [ ] GitHubissa renderöityjen Markdown-dokumenttien otsikkorakenne ja linkit ruudunlukijalla.

## Testausympäristön tiedot

| Tieto | Arvo |
|---|---|
| Päivä | 17.11.2026 |
| Testaustapa | GitHub-lähdekoodin katselmointi ja CSS-värien laskennallinen kontrastitarkistus |
| Käyttöjärjestelmä | Ei selain-/ruudunlukijatestissä käytettävissä |
| Selain ja versio | Ei testattu |
| Ruudunlukija ja versio | Ei testattu |
| Julkaistujen sivujen renderöinti | Ei voitu avata tässä ympäristössä |

## Johtopäätös

Lähdekoodissa on useita saavutettavuutta tukevia perusrakenteita, ja katselmoinnissa löytyneet kolme linkki- ja otsikkotason ongelmaa korjattiin. Tämä ei kuitenkaan täytä tiketin #25 hyväksymiskriteerejä: julkaistujen sivujen manuaaliset testit, ruudunlukijatestaus, suurennustestaus ja responsiivisuuden tarkistus ovat edelleen tekemättä.

**Tiketin #25 tulee pysyä avoinna**, kunnes puuttuvat testit suoritetaan ja niiden tulokset kirjataan. WCAG 2.2 AAA -tason toteutumista ei tämän katselmoinnin perusteella väitetä.
