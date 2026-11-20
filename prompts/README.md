# Ajastettujen käynnistyskehotteiden versionhallinta

Tämä hakemisto sisältää Aiheseuraimen ajastettujen ChatGPT-tehtävien kanoniset käynnistyskehotteet ja niiden versiorekisterin.

## Hakemistorakenne

Jokaisella ajastetulla tehtävällä on pysyvä tehtävätunniste (`task_id`). Sen jokainen käynnistyskehotteen versio tallennetaan omaan tiedostoonsa:

```text
prompts/
  README.md
  registry.json
  <task_id>/
    v1.0.0.txt
    v1.0.1.txt
```

Tehtävätunniste yksilöi ajastetun tehtävän. Versionumero yksilöi kyseisen tehtävän käynnistyskehotteen sisällön. Tehtävän tunniste ei vaihdu, kun kehotetta päivitetään.

## Kehotetiedostojen säännöt

- `.txt`-tiedosto sisältää vain ChatGPT:n tehtäväasetuksiin kopioitavan käynnistyskehotteen.
- Älä lisää kehotetekstiin Markdown-otsikoita, selityksiä, versionhallinnan kommentteja tai muuta tehtävän asetuksiin kuulumatonta tekstiä.
- Jokainen julkaistu versio on muuttumaton. Älä muokkaa tai ylikirjoita aiempaa versiota.
- Käynnistyskehotteen tulee ilmoittaa tehtävätunnisteensa ja käytössä oleva versionumeronsa yksiselitteisesti sekä ohjata ensisijaiseen toimintakäsikirjaan.
- Käynnistyskehotteen tulee viitata automaatioiden hallinnan suojausperiaatteisiin ja kieltää ajastuksen, tehtävän asetusten tai kohdekeskustelun muuttaminen ilman käyttäjän nimenomaista valtuutusta.

## Versionumerointi

Käytä semanttista versionumerointia muodossa `MAJOR.MINOR.PATCH`:

- **PATCH**: kirjoitusvirheen tai rajatun epäselvyyden korjaus, joka ei muuta tehtävän toimintaa olennaisesti.
- **MINOR**: yhteensopiva lisäys tai tarkennus, joka ei muuta tehtävän perusroolia tai aiempien ohjeiden merkitystä.
- **MAJOR**: yhteensopimaton muutos tai olennainen muutos tehtävän vastuisiin, suoritusprosessiin tai tulosvaatimuksiin.

Uusi versio tallennetaan aina uutena tiedostona. Versionumeroa ei koskaan käytetä uudelleen.

## Rekisteri

`registry.json` on tehtäväkohtaisten versiotietojen kanoninen rekisteri. Jokaisessa tehtävätietueessa ylläpidetään vähintään:

- `task_id`: ajastetun tehtävän pysyvä tunniste;
- `name`: ihmiselle ymmärrettävä tehtävän nimi;
- `canonical_version`: uusin GitHubissa oleva kehotteen versio;
- `deployed_version`: ChatGPT-tehtävässä käyttöön otettu ja tekstiltään täsmäytetty versio, tai `null`, jos käyttöönottoa ei ole vahvistettu;
- `deployment_verified_at`: vahvistuksen ajankohta tai `null`;
- `status`: esimerkiksi `draft`, `pending_deployment`, `active` tai `blocked`;
- `notes`: tarvittaessa lyhyt huomio käyttöönoton tilasta.

Älä lisää rekisteriin vanhan järjestelmän tehtäviä automaattisesti. Uusi tehtävätietue lisätään, kun kyseinen tehtävä määritellään uudessa järjestelmässä. Älä keksi tehtävätunnisteita tai väitä käyttöönottoa vahvistetuksi ilman tarkistusta.

## Päivitys- ja käyttöönottojärjestys

1. Tarkista tehtävän nykyinen tunniste, kanoninen versio ja ChatGPT:ssä käyttöön vahvistettu versio.
2. Luo uusi versiotiedosto muuttamatta vanhaa.
3. Päivitä `registry.json` siten, että `canonical_version` osoittaa uuteen versioon ja tila ilmaisee, ettei sitä ole vielä otettu ChatGPT:ssä käyttöön.
4. Tarkista uusi kehoteteksti ja sen viittaukset käsikirjoihin.
5. Pyydä käyttäjältä erillinen lupa ChatGPT-tehtävän asetusten muuttamiseen. Pelkkä pyyntö päivittää GitHub-dokumentaatio ei ole tällainen lupa.
6. Käyttäjän luvalla kopioi uusi teksti tehtävän asetuksiin muuttamatta ajastusta, aikavyöhykettä tai kohdekeskustelua.
7. Vertaa tehtävän asetuksiin tallennettua koko tekstiä kanoniseen tiedostoon.
8. Vasta onnistuneen täsmäytyksen jälkeen päivitä `deployed_version`, `deployment_verified_at` ja tila `active`-arvoon.
9. Jos täsmäytys ei onnistu tai tehtävän asetuksia ei voida tarkistaa, älä merkitse käyttöönottoa vahvistetuksi.

## Ajon alun tarkistus

Jokaisen ajon alussa tehtävän on ilmoitettava oma `task_id` ja käynnistyskehotteen versio. Niitä verrataan rekisteriin.

- Ajon saa aloittaa vain, kun tehtävätunniste on tunnettu ja versiotiedot ovat johdonmukaiset.
- Käytössä olevan version on vastattava sekä rekisterin `deployed_version`-arvoa että kanonista versiota.
- Jos uusi kanoninen versio odottaa käyttöönottoa, ajo estetään, kunnes versiot on täsmäytetty.
- Jos tunniste, versio tai käyttöönoton tila puuttuu tai on ristiriitainen, keskeytä ennen tutkimustyötä ja raportoi ristiriita.
- Ajon suorittaminen ei anna lupaa korjata ristiriitaa muuttamalla ChatGPT-tehtävän asetuksia.

## Palautus aiempaan versioon

Aiemman version palauttaminen tehdään uutena hallittuna käyttöönottona. Vanhaa tiedostoa ei muuteta eikä poisteta. Rekisteriin kirjataan erikseen kanoninen versio ja ChatGPT:ssä käyttöön vahvistettu versio; niiden ei tarvitse olla sama ennen käyttöönoton valmistumista.

## Muutoshistoria

- **1.0.0 – 2026-11-20:** palautettu ajastettujen käynnistyskehotteiden tehtäväkohtainen versionhallinta ja määritelty tiedostorakenne, rekisteri, semanttinen versionumerointi, käyttöönoton vahvistus sekä ajon alun tarkistus.
