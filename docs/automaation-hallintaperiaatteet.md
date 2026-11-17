# Automaatioiden hallinnan suojausperiaatteet

Tämä dokumentti määrittää kaikkia Aiheseurainin nykyisiä ja tulevia ajastettuja automaatioita koskevan yhteisen hallintasäännön. Se koskee pääuutisseurantaa, erillistä intialaisten elokuvien näytösvahtia, viikoittaista laatutarkistusta ja myöhemmin lisättäviä automaatioita.

## Perussääntö

Automaation suorittaminen ei anna automaation suorittajalle valtuutta muuttaa ajastusta, automaation asetuksia tai keskustelujen rakennetta. Oletusarvo on, että automaatio tekee vain sille määritellyn ajon ja raportoi ongelmat.

Ilman käyttäjän nimenomaista pyyntöä tai lupaa automaatio ei saa:

- poistaa ajastettua tehtävää käytöstä, keskeyttää sitä tai poistaa sitä;
- muuttaa suoritusväliä, suoritusajankohtaa, aikavyöhykettä tai muuta aikataulun osaa;
- muuttaa tehtävän käynnistysohjetta tai muita automaation asetuksia;
- vaihtaa automaation kohdekeskustelua tai luoda korvaavaa tehtävää tai keskustelua;
- muuttaa toisen automaation ajastusta, asetuksia tai kohdekeskustelua.

Kielto koskee myös tilanteita, joissa suorittaja arvioi muutoksen hyödylliseksi, tarpeelliseksi, turvallisemmaksi tai virhetilanteen vuoksi perustelluksi. Onnistunut, epäonnistunut tai keskeytynyt ajo ei itsessään oikeuta muuttamaan ajastusta tai asetuksia.

## Käyttäjän valtuutus

Ajastukseen tai automaation asetuksiin saa tehdä muutoksen vain, kun käyttäjä pyytää kyseistä muutosta nimenomaisesti tai antaa siihen nimenomaisen luvan.

- Valtuutus koskee vain siinä yksilöityä muutosta ja automaatiota.
- Yhden automaation muutosta ei saa tulkita luvaksi muuttaa muita automaatioita.
- Yleinen pyyntö suorittaa, ylläpitää, korjata tai parantaa automaatiota ei ole lupa muuttaa sen ajastusta tai kohdekeskustelua.
- Jos pyynnön laajuus on epäselvä, älä tee muutosta. Kysy käyttäjältä täsmennys.

## Ongelmatilanteet

Jos ajastuksessa, tehtävän aktiivisuudessa, asetuksissa tai kohdekeskustelussa havaitaan ongelma:

1. Älä muuta ajastusta tai asetuksia omatoimisesti.
2. Suorita vain ne tarkistukset ja tehtävävaiheet, jotka ovat automaation käsikirjan sallimia.
3. Kerro käyttäjälle, mikä havaittiin, mikä jäi varmistamatta ja mitä käyttäjän päätöstä tai toimenpidettä tarvitaan.
4. Älä ilmoita muutosta tehdyksi, ellei sitä ole todella tehty käyttäjän valtuutuksella ja sen tulos ole varmennettu.

Jos ajastus ei ole käytettävissä tai tehtävän suoritus estyy, raportoi este. Älä luo uutta ajastusta vanhan tilalle äläkä muuta muiden automaatioiden toimintaa.

## Eri järjestelmätietojen erottaminen

Aiheseurainissa pidetään erillään:

- **ChatGPT:n ajastetun tehtävän asetukset:** aktiivisuus, aikataulu, aikavyöhyke, käynnistysohje ja kohdekeskustelu.
- **GitHub-repositorion ohjeet:** automaation käsikirjat ja kanoniset käynnistyskehotteet.
- **GitHubin seurantatiedot:** yksittäisten ajojen tulokset, tarkistuspisteet ja lähdekattavuus.

GitHubiin tehty dokumentaatio- tai seurantatilapäivitys ei itsessään muuta ChatGPT:n ajastetun tehtävän asetuksia. Vastaavasti ajon onnistuminen GitHubissa ei ole peruste ajastuksen muuttamiselle.

## Ylläpito ja soveltaminen

- Tätä sääntöä sovelletaan kaikkiin nykyisiin ja tuleviin Aiheseurain-automaatioihin.
- Jokaisen automaation käsikirjan ja käynnistyskehotteen tulee viitata tähän dokumenttiin ja ilmaista, ettei ajastusta tai kohdekeskustelua saa muuttaa ilman käyttäjän nimenomaista valtuutusta.
- Uutta automaatiota luotaessa sääntö lisätään sen käsikirjaan ja käynnistyskehotteeseen ennen käyttöönottoa.
- Tämän dokumentin muuttaminen ei itsessään anna lupaa muuttaa ajastettuja tehtäviä tai niiden asetuksia.
- Käynnistyskehotteiden muutokset on kopioitava erikseen ChatGPT:n tehtäväasetuksiin. GitHub ei synkronoi niitä automaattisesti.

## Muutoshistoria

- **1.0.0 – 2026-11-17:** määriteltiin kaikkia nykyisiä ja tulevia automaatioita koskeva käyttäjän valtuutukseen perustuva ajastusten, asetusten ja kohdekeskustelujen suojaus.
