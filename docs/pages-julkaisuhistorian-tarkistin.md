# Pages-julkaisuhistorian vain luku -tarkistin

**Tarkoitus:** selvittää GitHubin tallentamasta RSS-julkaisumanifesti- ja Pages-ajohistoriasta, onko Taylor Swift -syötteen tiettyyn seurantajaksoon kuuluva raportti julkaistu Pagesissä.

## Käynnistäminen

Avaa GitHubissa Actions → Pages-julkaisuhistorian vain luku -tarkistus → Run workflow. Anna aikavyöhykkeelliset ISO 8601 -rajat. Oletusjakso on 18.–19.11.2026.

Työnkulku tallentaa yhteenvedon Actions-ajon Summary-välilehdelle ja täydellisen JSON-raportin 90 päiväksi Actions-artifaktiksi.

## Mitä tarkistin lukee

1. Kaikki `rss-publication-manifest`-ympäristön GitHub Deployment -tietueet sivutettuna.
2. Manifestien Taylor Swift -syötteen GUID-luettelon ja manifestin lähdecommitin RSS-tiedoston.
3. Deploymentin viimeisimmän tilamerkinnän.
4. Kohdejakson `.github/workflows/publish-pages.yml`-ajot ja niiden job/step-tulokset.
5. Tarkistushetken julkisen Taylor Swift -RSS-syötteen sekä sen SHA-256-tiivisteen.

Tarkistin etsii lähdecommitin RSS-itemeistä täsmälleen kohdejakson alku- ja loppupäiviä sisältävän eksplisiittisen Seurantajakso-tekstin. Vain onnistunut Pages-deployment, jonka lähdecommit sisältää kohdejakson raportin, merkitään todisteeksi julkaistusta raportista.

## Tulkinta ja fail-closed-raja

- **published:** vähintään yksi onnistunut Pages-deploymentin RSS-manifesti sisältää kohdejakson raportin.
- **unknown:** tällaista todistetta ei löytynyt tai historia ei sisällä riittäviä tietoja.
- Tarkistin ei koskaan päättele **unpublished** pelkästään puuttuvista manifesteista. Manifesti luodaan nykyisessä julkaisupolussa vain RSS-tiedostomuutoksia sisältäneille ajoille.
- Nykyisen Pages-RSS:n sisältö ei ole historiallinen snapshot eikä yksin todista aiempaa julkaisutilaa.
- Workflow-ajon onnistuminen tai Pages-sivuston deploy ei yksin todista RSS-sisällön takaisinlukua.
- Runtime-haaran puuttuminen ei todista, ettei haaraa olisi aiemmin ollut tai ettei sillä olisi julkaistu.
- Jos API-kutsu tai historian sivutus epäonnistuu, koko tarkistus keskeytyy virheeseen. Osittaista aineistoa ei raportoida täydellisenä.

## Turvarajat

Työnkululla on vain `contents: read`, `actions: read` ja `deployments: read`. Checkout ei säilytä tunnistetietoja. Tarkistin ei luo tai muuta deploymentteja, brancheja, committeja, RSS-syötteitä, Pages-sivustoa, checkpointteja, runtime-tilaa, julkaisujournalia, tehtäväjonoa tai automaatioiden asetuksia. Se ei käynnistä uutistutkimusta eikä Taylor Swiftin varjoharjoitusta.

Tarkistin on historiallinen havaintotyökalu, ei ennakkotarkistuksen ohitus. Sen tulos on syötettävä olemassa olevaan neljän kanavan ennakkotarkistukseen lähdeviitteineen. Vain kaikkien neljän kanavan todennettu `unpublished` voi avata varjoharjoituksen.
