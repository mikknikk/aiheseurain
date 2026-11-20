# Automaatioiden hallinnan suojausperiaatteet

Tämä dokumentti määrittää kaikkia Aiheseuraimen nykyisiä ja tulevia ChatGPT:n ajastettuja seurantatehtäviä sekä niiden kanssa toimivia ylläpitoprosesseja koskevat hallintasäännöt. Sääntöjä sovelletaan riippumatta siitä, seurataanko yhtä aihetta vai useita aiheita yhteisellä toimintamallilla.

Dokumentti koskee automaatioiden hallintaa, ei niiden tutkimussisällön tai GitHubissa ylläpidettävien aihekohtaisten määritysten normaalia käsittelyä. Uudistettu vaatimusmäärittely on edelleen luonnos, eikä tämä dokumentti hyväksy tai käynnistä sen mukaista toteutusta.

## Perussääntö

Automaation suorittaminen ei anna suorittajalle valtuutta muuttaa ajastettua tehtävää, sen asetuksia tai keskustelujen rakennetta. Oletusarvo on, että automaatio suorittaa vain sille määritellyn ajon ja raportoi ongelmat.

Ilman käyttäjän nimenomaista pyyntöä tai lupaa automaatio tai sen suorittaja ei saa:

- poistaa ajastettua tehtävää käytöstä, keskeyttää sitä tai poistaa sitä;
- muuttaa suoritusväliä, suoritusajankohtaa, aikavyöhykettä tai muuta aikataulun osaa;
- muuttaa tehtävän käynnistysohjetta tai muita ChatGPT-tehtävän asetuksia;
- vaihtaa tehtävän kohdekeskustelua tai luoda korvaavaa tehtävää tai keskustelua;
- muuttaa toisen automaation ajastusta, asetuksia tai kohdekeskustelua;
- luoda rinnakkaista tai korvaavaa automaatiota ongelman kiertämiseksi.

Kielto koskee myös tilanteita, joissa suorittaja arvioi muutoksen hyödylliseksi, tarpeelliseksi, turvallisemmaksi tai virhetilanteen vuoksi perustelluksi. Onnistunut, epäonnistunut tai keskeytynyt ajo ei itsessään oikeuta muuttamaan ajastusta tai asetuksia.

## Käyttäjän valtuutus

Ajastukseen tai ChatGPT-tehtävän asetuksiin saa tehdä muutoksen vain, kun käyttäjä pyytää kyseistä muutosta nimenomaisesti tai antaa siihen nimenomaisen luvan.

- Valtuutus koskee vain siinä yksilöityä muutosta ja automaatiota.
- Yhden tehtävän muutosta ei saa tulkita luvaksi muuttaa muita tehtäviä.
- Yleinen pyyntö suorittaa, ylläpitää, korjata, siivota tai parantaa Aiheseurainia tai automaatiota ei ole lupa muuttaa tehtävän ajastusta, asetuksia tai kohdekeskustelua.
- Jos pyynnön laajuus on epäselvä, älä tee muutosta. Kysy käyttäjältä täsmennys.
- Käyttäjän nimenomainen lupa muuttaa yhtä asetusta ei oikeuta tekemään muita siihen liittyviksi arvioituja muutoksia.

## Ongelmatilanteet

Jos ajastuksessa, tehtävän aktiivisuudessa, asetuksissa tai kohdekeskustelussa havaitaan ongelma:

1. Älä muuta ajastusta tai asetuksia omatoimisesti.
2. Suorita vain ne tarkistukset ja tehtävävaiheet, jotka ovat kyseisen automaation ohjeiden sallimia.
3. Kerro käyttäjälle, mikä havaittiin, mikä jäi varmistamatta ja mitä käyttäjän päätöstä tai toimenpidettä tarvitaan.
4. Älä ilmoita muutosta tehdyksi, ellei sitä ole todella tehty käyttäjän valtuutuksella ja sen tulos ole varmennettu.
5. Älä luo korvaavaa tehtävää äläkä muuta muiden tehtävien toimintaa.

Jos ajastus ei ole käytettävissä tai tehtävän suoritus estyy, raportoi este. Älä yritä ratkaista ongelmaa muuttamalla tehtävän asetuksia tai siirtämällä sitä toiseen keskusteluun ilman erillistä lupaa.

## Eri järjestelmätietojen erottaminen

Aiheseuraimessa on erotettava toisistaan vähintään seuraavat tiedot:

- **ChatGPT:n ajastetun tehtävän asetukset:** tehtävän olemassaolo ja aktiivisuus, aikataulu, aikavyöhyke, käynnistysohje ja kohdekeskustelu. Näitä hallitaan ChatGPT:ssä, eikä GitHub-muutos päivitä niitä automaattisesti.
- **GitHubin yhteiset ohjeet ja määritykset:** järjestelmän vaatimusmäärittely, yhteiset toimintaperiaatteet, skeemat sekä mahdolliset aihe- ja seurantatyyppikohtaiset määritykset.
- **Ajon tiedot:** yksittäisen suoritusyrityksen tunniste, ajanjakso, vaiheet, tulokset, lähdekattavuus, laadunvarmistus ja julkaisutilanne.
- **Julkaistut tulokset:** aihekohtaiset RSS-syötteet ja niiden muuttumaton julkaisuhistoria.

GitHubissa olevan ohjeen, määrityksen tai ajotiedon muuttaminen ei itsessään muuta ChatGPT:n ajastetun tehtävän asetuksia. Vastaavasti ChatGPT-tehtävän suorittaminen ei anna lupaa muuttaa GitHubin määrityksiä, julkaistua historiaa tai muita tehtäviä.

Uudistetussa tavoitetilassa useat aiheet voivat käyttää yhteistä ajomallia. Tämä ei muuta suojausperiaatetta: yhteinen ajomalli, aiheen määritykset ja ChatGPT:n todelliset ajastetut tehtävät ovat eri asioita. Aihekohtaisen määrityksen ajotiheyden muuttaminen ei ole sama asia kuin ChatGPT-tehtävän aikataulun muuttaminen.

## Ylläpito ja soveltaminen

- Tätä sääntöä sovelletaan kaikkiin nykyisiin ja tuleviin Aiheseuraimen automaatioihin ja ajastettuihin seurantatehtäviin.
- Jokaisen automaation käsikirjan ja käynnistysohjeen tulee viitata tähän dokumenttiin ja ilmaista, ettei ajastusta, tehtävän asetuksia tai kohdekeskustelua saa muuttaa ilman käyttäjän nimenomaista valtuutusta.
- Uutta automaatiota tai ajastettua tehtävää suunniteltaessa sääntö huomioidaan sen ohjeissa ennen käyttöönottoa.
- Tämän dokumentin tai muun GitHub-dokumentaation muuttaminen ei itsessään anna lupaa muuttaa ajastettuja tehtäviä tai niiden asetuksia.
- Käynnistysohjeiden GitHub-versiot ja ChatGPT-tehtävän asetuksiin tallennetut tekstit ovat erillisiä. GitHubissa tehty muutos ei synkronoidu ChatGPT:hen automaattisesti.
- Mahdollinen käyttöönotto, tehtävien uudelleenjärjestely tai vanhojen tehtävien korvaaminen edellyttää erillistä päätöstä ja käyttäjän nimenomaista valtuutusta.
- Suojausperiaate pysyy voimassa myös järjestelmän uudelleenrakentamisen, arkistoinnin, migraation ja siivouksen aikana.

## Muutoshistoria

- **1.1.0 – 2026-11-20:** päivitetty soveltamisala vastaamaan Aiheseuraimen uudistettua ChatGPT-pohjaista ja aihekohtaiseen yhteiseen ajomalliin perustuvaa tavoitetilaa. Poistettu vanhan toteutuksen automaatioluettelo. Täsmennetty ChatGPT-tehtävien asetusten, GitHub-määritysten, ajotietojen ja julkaistujen tulosten erottelu sekä uudistuksen, migraation ja siivouksen valtuutusrajat.
- **1.0.0 – 2026-11-17:** määriteltiin kaikkia nykyisiä ja tulevia automaatioita koskeva käyttäjän valtuutukseen perustuva ajastusten, asetusten ja kohdekeskustelujen suojaus.
