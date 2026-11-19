- [x] Luo epäonnistuneesta RSS-julkaisusta idempotentti GitHub-issue, jossa on linkki ajoon.
- [ ] Tee laaja fault-injection-testaus oikeassa GitHub Actions- ja Pages-ympäristössä, mukaan lukien katkaisu jokaisen vaiheen jälkeen.

**Rajaus:** nykyiset RSS-URL-osoitteet, Pages-asetukset ja automaatioiden ajastukset, ohjeet sekä kohdekeskustelut säilyivät. Toteutus ei luo erillistä julkaisurepositoriota eikä muuta tuotannon julkaisukohdetta. Keskeytyneen ajon idempotentti jatkaminen, GitHub API:n epäselvien vastausten käsittely ja operatiivinen hälytys ovat edelleen avoinna; tätä ei pidä tulkita täysin toimintavarmaksi palautusratkaisuksi.


### Aiheajojen tekninen eristäminen

**Tavoite:** jokainen aiheajo saa vain oman moduulinsa sisällön. Yhteinen koordinaattori valitsee tehtävän ja hoitaa teknisen elinkaaren; aihekohtainen runner ei lue muiden aiheiden ohjeita, lähteitä, kohteita, tilaa tai historiaa.

- [x] **#199 – Eristetyn syötepaketin sopimus:** ensimmäinen versio toteutettu ja yhdistetty PR:ssä #203; syötepaketin sisältö rajataan moduulin omiin lähteisiin, kohteisiin ja tilaan.
- [x] **#200 – Eristetty suoritusympäristö:** Linux/bubblewrap-sandbox toteutettu; moduulikohtainen syöte ja runner-koodi ovat vain luku -muotoisia, vain tulostiedosto on kirjoitettavissa, verkko ja isäntäkoneen yleinen tiedostonäkymä on rajattu pois. Ei vielä kytketty tuotantoajoihin.
- [x] **#201 – CI-eristystestit:** lisättiin `tests/test_module_isolation_guards.py`. Testit varmistavat, ettei toisen moduulin sisältö tai käyttämätön lähdekatalogin tietue päädy pakettiin, väärä moduulipolku tai polkupoikkeama hylätään, kohteen omistajuus tarkistetaan, toisen tehtävän lähdekäyttörekisteri ei kelpaa ja runnerin julkinen rajapinta ei ota vastaan repositorion juurta tai yhteisten rekisterien polkuja. Testit ajetaan PR-CI:n koko Python-testikokonaisuudessa. Testit käyttävät väliaikaisia tiedostokopioita eivätkä muuta varsinaisia moduuleja tai rekistereitä.
- [ ] **#202 – Pääautomaation siirto:** vaihda laaja aihekierron lukujärjestys koordinaattorin ja moduulikohtaisen käynnistyksen malliin. Käynnistyskehotteen ja live-automaation asetusten muuttaminen vaatii erillisen hyväksynnän.

Nykyinen ensimmäinen toteutus on sovelluskerroksen rajaus: se antaa runnerille vain moduulin määrityksen, omat kohteet, omat lähteet, oman viimeisimmän checkpointin ja oman julkaisusyötteen GUID-viitteet. Bubblewrap rajaa prosessin tiedostonäkymän ja verkon. CI-regressiotestit valvovat paketin sisältöä, viitteiden omistajuutta ja runnerin rajapintaa; ne eivät kuitenkaan itsessään todista tuotantoautomaation olevan jo kytketty sandboxiin. Näytösvahti pysyy erillisenä päivittäisenä prosessina eikä kuulu uutisaiheiden kiertoon.
