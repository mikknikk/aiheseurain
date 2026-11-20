# Automaation käynnistyskehotteet

Tämä hakemisto sisältää `mikknikk/aiheseurain`-repositorioon liittyvien kolmen automaation asetuksiin kopioitavat käynnistyskehotteet. Kunkin `.txt`-tiedoston sisältö on tarkoitettu kopioitavaksi sellaisenaan automaation prompt-kenttään.

Kaikkia automaatioita koskeva ajastusten ja asetusten suojaus on määritelty tiedostossa [`docs/automaation-hallintaperiaatteet.md`](../docs/automaation-hallintaperiaatteet.md). Jokainen käynnistyskehote sisältää tätä koskevan nimenomaisen kiellon. GitHubissa päivitetty kehote on kopioitava erikseen ChatGPT:n vastaavan tehtävän asetuksiin; tämä repositorio ei synkronoi asetuksia.

## Tiedostot ja vastuut

Varsinaisten käynnistyskehotteiden lisäksi hakemistossa voi olla selvästi luonnoksiksi nimettyjä tekstejä. Luonnokset eivät ole aktiivisia, eikä niitä saa kopioida automaation asetuksiin ilman erillistä hyväksyntää.

| Automaatio | Kanoninen käynnistyskehote | Varsinainen käsikirja |
|---|---|---|
| Päivittäinen uutisseurannan aihekierros | [`paauutisseuranta.txt`](paauutisseuranta.txt) | [`docs/paaautomaation-ohje.md`](../docs/paaautomaation-ohje.md) |
| Intialaisten elokuvien näytösvahti | [`naytosvahti.txt`](naytosvahti.txt) | [`docs/intialaisten-elokuvien-naytosseuranta.md`](../docs/intialaisten-elokuvien-naytosseuranta.md) |
| Viikoittainen järjestelmän laatutarkistus | [`laatutarkistus.txt`](laatutarkistus.txt) | [`docs/laatutarkistuksen-ohje.md`](../docs/laatutarkistuksen-ohje.md) |

## Käynnistyskehotteen tunnisteen tarkistus

Jokaisella kolmella käynnistyskehotteella on yksilöllinen `Käynnistyskehotteen tunniste`. Saman automaation tunniste tallennetaan `data/seurantatila.json`-tiedostoon vastaavan ohjeosion `startup_prompt_id`-kenttään. Ajon alussa automaatio vertaa aktiiviseen kehotteeseen sisältyvää tunnistetta GitHubin seurantatilaan. Jos tunniste puuttuu tai ei täsmää, ajo keskeytetään ennen varsinaista työtä.

Kun käynnistyskehotteen sisältöä muutetaan, anna sille uusi tunniste ja päivitä saman automaation `startup_prompt_id` samassa muutossarjassa. Älä muuta muiden automaatioiden tunnisteita. Tämä tunnistevertailu havaitsee vanhentuneen asetuksiin kopioidun kehotteen, kun kanonisen kehotteen tunniste vaihdetaan; se ei yksin todista koko tekstin identtisyyttä. Siksi koko kehote kopioidaan edelleen asetuksiin ja tallennettu teksti tarkistetaan erikseen.

## Ylläpitoperiaate

- `prompts/*.txt` sisältää vain automaation asetuksiin kopioitavan tekstin. Älä lisää tiedostoihin selittäviä otsikoita tai Markdown-muotoilua.
- Tehtävien varsinainen sisältö, rajaukset, tarkistuslistat ja onnistumisehdot määritellään yllä olevissa käsikirjoissa. Käynnistyskehote ohjaa lukemaan oikean käsikirjan ja tekemään sen esitarkistukset. Jokainen RSS-syötemuutos edellyttää lisäksi [julkaisulaadun portin](../docs/julkaisuportti.md) mukaista tarkistusraporttia.
- Kun automaation käynnistyskehotetta muutetaan, päivitä ensin tämän hakemiston kanoninen tiedosto, anna sille uusi tunniste ja päivitä vastaavan automaation `startup_prompt_id` `data/seurantatila.json`-tiedostossa samassa muutossarjassa. Säilytä myös yhteisen hallintaperiaatteen nimenomainen suojausosio. Kopioi sen jälkeen koko sisältö vastaavan automaation asetuksiin. Älä päivitä automaation asetuksia eri sisältöön kuin repositorion tiedosto.
- Kun kehote on kopioitu asetuksiin, vertaa tallennettua tekstiä tiedostoon ja varmista, että ne ovat täsmälleen samat. Asetusten päivitys on erillinen manuaalinen vaihe; GitHub-muutos ei päivitä automaation asetuksia automaattisesti.
- Älä muuta automaatioiden aikatauluja tai tehtäväkäsikirjoja pelkän käynnistyskehotteen siirron yhteydessä.
- Älä kovakoodaa käsikirjan versionumeroa käynnistyskehotteeseen. Kehotteen tulee lukea käsikirjan versio ja verrata sitä `data/seurantatila.json`-tiedoston vastaavaan `current_version`-arvoon ajon esitarkistuksessa. Näin tavallinen versionumeron päivitys ei vaadi käynnistyskehotteen muutosta.
- Päivitä käynnistyskehote vain, jos käsikirjan polku, tarkistettava tietorakenne tai käynnistys-/esitarkistusmenettely muuttuu. Varmista tällöin, että kehote ja käsikirja pysyvät keskenään yhteensopivina.
- Säilytä pääuutisseurannan, näytösvahdin ja laatutarkistuksen rajat erillisinä. Älä yhdistä niiden käynnistyskehotteita yhdeksi yleiseksi promptiksi.

Tämän hakemiston tiedostot ovat käynnistyskehotteiden versionhallinnassa ylläpidettävät kanoniset lähteet. Reaaliaikaisten automaatioasetusten sisältö on tarkistettava erikseen; GitHubissa tehty muutos ei päivitä asetuksia automaattisesti.

Pääuutisseurannan käynnistyskehotetta on päivitetty vastaamaan lähdekatalogin ja tehtäväkohtaisten käyttörekisterien uutta rakennetta. Kopioi päivitetty `paauutisseuranta.txt` kokonaisuudessaan pääautomaation asetuksiin ja varmista, että tallennettu teksti vastaa tiedostoa. Muut käynnistyskehotteet eivät muutu tämän lähdetietomallin uudistuksen vuoksi.

## Palautuskehotteen luonnos

`paauutisseuranta-moduulipalautus-luonnos.txt` on uuden moduulipolun palautuskehotteen luonnos, ei aktiivinen käynnistyskehote. Se kuvaa, miten yhden moduulin tulos palautetaan GitHubiin uutena, vain yhden JSON-tiedoston sisältävänä pull requestina. Luonnosta ei saa kopioida tallennetun automaation asetuksiin ennen erillistä hyväksyttyä live-siirtymää. Jos automaatiolla ei ole GitHub-yhteyttä tai kirjoitusoikeutta, sen on palautettava JSON käyttäjälle eikä väitettävä GitHub-kirjoituksen onnistuneen.
