# ChatGPT-automaatioiden ajohistoria

**Tietomallin versio:** 1  
**Liittyvä toteutus:** [tiketti #37](https://github.com/mikknikk/aiheseurain/issues/37)

## Tarkoitus

Valvomo näyttää ChatGPT:n ajoitettujen automaatioiden ajot ja vaiheet vain automaation itse kirjaaman tiedon perusteella. Näitä ajoja ei pidä sekoittaa GitHub Actions -työnkulkuihin.

## Tallennusarkkitehtuuri

Jokaisella automaatiolla on oma, vain ajohistoriaan käytettävä Git-haara:

| Automaatio | Haara | Tunniste |
|---|---|---|
| Pääautomaation yhdeksän aiheen kierto | `run-history/main-automation` | `main_automation` |
| Intialaisten elokuvien näytösvahti | `run-history/screening-watch` | `screening_watch` |
| Viikoittainen laatutarkistus | `run-history/quality-check` | `quality_check` |

Kunkin haaran juuritiedosto `history.json` sisältää enintään 30 viimeisintä ajoa ja niiden vaihetilat. Jokainen päivitys on oma Git-commitinsa kyseiseen historiahaaraan. Varsinaista `main`-haaraa, RSS-syötteitä tai automaatioiden onnistumisen tarkistuspisteitä ei päivitetä vaihekirjauksilla.

Valvomo lukee tiedostot GitHubin julkisesta Contents APIsta `ref`-parametrilla. Selain tarvitsee vain anonyymin lukuoikeuden. Se ei saa tunnuksia eikä kirjoitusoikeuksia.

## Suorituksen ja alustahavainnon erottaminen

Ajohistorian `source` kertoo, mitä tieto todistaa:

- `chatgpt_scheduled_task`: automaation oma suoritus on käynnistynyt ja se on kirjannut vaiheensa itse.
- `chatgpt_platform_observation`: ulkopuolelta luettu ChatGPT-ajastusalustan run-tietue kertoo epäonnistumisesta, mutta automaation keskustelu-/vaihekohtaista suoritusta ei voida todentaa.

Alustahavainto kirjataan vain, kun Automationsin lukutieto antaa yksilöllisen run ID:n, aloitus- ja päättymisajat sekä virhetuloksen. Jos `chat_ref` puuttuu, `steps` jätetään tyhjäksi. Älä keksi esitarkistus-, haku-, julkaisu- tai muita vaiheita.

Alustahavainnon `diagnostics` sisältää:
- `stage=platform_execution` ja `category=platform_error`;
- `retryable=null`, ellei alusta anna uudelleenyrityksestä täsmällistä tietoa;
- `root_cause_confirmed=false`, jos teknistä syytä ei ole vahvistettu;
- `chat_ref_present=false`, jos keskusteluviite puuttuu;
- alkuperäisen alustan run ID:n.

Tallenna alustan palauttama virheviesti sellaisenaan lyhyenä virheenä. Kirjoita yhteenvetoon, että kyseessä on alustahavainto eikä automaation oma vaihekohtainen loki. Älä päättele yleisestä virheilmoituksesta verkkovirhettä, käyttöoikeusvirhettä tai muuta teknistä juurisyytä.

Alustahavainto voidaan lisätä ajohistoriahaaraan jälkikäteen, kun lukutieto on saatavilla. Se ei muuta varsinaista seurantatilan onnistumispistettä. Valvomo näyttää alustahavainnon erillisenä lähteenä. Tämä menettely ei itsessään valvo puuttuvia ajoja reaaliajassa eikä luo uutta ajastettua tehtävää.
Valvomo tarkistaa myös viimeisimmän havaitun ajon iän sivua ladattaessa. Päivittäisten automaatioiden vanhenemisraja on 36 tuntia ja viikoittaisen laatutarkistuksen 240 tuntia. Vanhentunut onnistunut ajo näytetään varoituksena, vanhentunut epäonnistuminen säilyttää virhetilansa, ja tyhjä ajohistoria näytetään puuttuvana havaintona. Tarkistus on passiivinen käyttöliittymän ominaisuus: se ei käynnistä eikä ajasta uutta työtä eikä lähetä ilmoituksia sivun ollessa suljettuna.

## Kirjausmenettely

1. Luo ennen varsinaista työtä yksilöllinen ajotunniste (UTC-aikaleima ja satunnainen/uniikki loppuosa) ja lisää ajo tilaan `running`.
2. Päivitä `history.json` jokaisen merkittävän vaiheen alussa ja lopussa. Kirjaa vaiheen `id`, nimi, tila, aikaleimat, varoitukset ja virheet.
3. Päivitä ajon `updated_at` jokaisella kirjoituksella. Säilytä aiemmat ajot; kun määrä ylittää 30, poista vain vanhin ajo tästä näkymäindeksistä. Git-haaran commit-historia säilyttää aiemmat versiot.
4. Päätä ajo tilaan `succeeded`, `failed` tai `partial` vain, kun tulos on tiedossa. Jos ajo päättyy odottamatta, viimeinen kirjattu `running` jää näkyviin ja Valvomo luokittelee sen vanhentuneeksi/mahdollisesti keskeytyneeksi, ei onnistuneeksi.
5. Lue jokainen kirjoitettu tiedosto takaisin ja varmista JSON sekä ajotunniste ennen seuraavaan vaiheeseen siirtymistä.

## Tilojen merkitykset

- `running`: automaatio on nimenomaisesti kirjannut käynnissä olevan vaiheen.
- `succeeded`: automaatio on kirjannut koko ajon onnistuneesti päättyneeksi.
- `failed`: ajo epäonnistui.
- `partial`: ajo valmistui vain osittain tai sen sallittua työtä jäi tekemättä.
- `interrupted`: automaatio pystyi nimenomaisesti toteamaan keskeytyksen.
- `unknown`: tulosta ei voida todentaa.
- Vaiheen `pending`, `running`, `succeeded`, `failed`, `skipped`, `interrupted` ja `unknown` kuvaavat vain kirjattua tilaa.

Pelkkä vanhentunut `running`-merkintä ei todista keskeytymisen syytä. Valvomo näyttää sen esimerkiksi muodossa ”Ajon päivitys vanhentunut – mahdollisesti keskeytynyt”. Tuoreusraja on pääkierrolle ja näytösvahdille 36 tuntia sekä laatutarkistukselle 10 vuorokautta. Käynnissä-tila näytetään vain, jos viimeisin päivitys alittaa kyseisen rajan.

## Vaiheiden tunnisteet

Pääautomaatio: `preflight`, `task_selection`, `research`, `source_verification`, `report_drafting`, `publication_gate`, `rss_validation`, `pull_request`, `ci`, `merge`, `verification`.

Näytösvahti: `preflight`, `source_search`, `screening_validation`, `history_update`, `rss_update`, `validation`, `pull_request`, `ci`, `merge`, `verification`.

Laatutarkistus: `preflight`, `repository_audit`, `tests_workflows`, `accessibility`, `backlog_audit`, `report`, `state_update`, `pull_request`, `ci`, `merge`, `verification`.

Vaihe voidaan merkitä ohitetuksi vain, jos se ei kuulu kyseiseen ajoon; perustele ohitus tarvittaessa ajon yhteenvedossa.

## Tietosuoja ja luotettavuus

Älä kirjaa käyttöoikeustokeneita, salaisuuksia, henkilötietoja, raakaa API-vastausta, pitkiä lokikatkelmia tai tarpeettomia uutisartikkelien sisältöjä. Virhe- ja varoitustekstit ovat lyhyitä käyttäjälle tarkoitettuja selitteitä. Ajohistoria kertoo, mitä automaatio kirjasi, ei itsenäisesti todista uutisväitteiden totuutta, lähteiden riippumattomuutta tai ulkoisen julkaisun onnistumista.

GitHub-haaran kirjoitusoikeuden puuttuminen, API-virhe tai takaisinluvun epäonnistuminen on kirjattava automaation omassa raportissa. Älä väitä vaihetta tallennetuksi, jos kirjoitusta ei ole varmennettu. Älä muuta automaation ajastuksia, ohjeita, aktiivisuutta tai kohdekeskustelua tämän tietomallin käyttöönoton vuoksi.

## Validointi

Tietomalli validoidaan tiedostoa `schemas/automation-run-history.schema.json` vasten. Skeema tarkistaa rakenteen ja sallitut tilat. Valvomo tarkistaa lisäksi automaatiotunnisteen, ajon tuoreuden ja esittää puuttuvat/virheelliset tiedot tuntemattomina.
