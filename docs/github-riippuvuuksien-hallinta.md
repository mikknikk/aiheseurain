# GitHub-issueiden riippuvuuksien hallinta

## Kanoninen tietolähde

Aiheseuraimen kehitystehtävien riippuvuudet tallennetaan GitHub Issuesin natiiveina suhteina. Erillistä JSON-riippuvuusrekisteriä tai omaa riippuvuuksien välitystyönkulkua ei käytetä.

GitHubissa käytetään kahta suhdetta:

- **Blocked by**: tämä issue odottaa toisen issuen valmistumista.
- **Blocking**: tämä issue estää toisen issuen etenemistä.

GitHub ylläpitää suhteen molemmat suunnat. Sama suhde näkyy myös Aiheseurain-Projectin korteissa GitHubin tarjoamana estomerkintänä.

## Riippuvuuden lisääminen ja poistaminen

1. Avaa riippuvuutta tarvitseva issue.
2. Etsi issuen oikean reunan **Development**- tai **Relationships**-osio.
3. Lisää **Blocked by** -suhteeseen ne issuet, joiden valmistumista tämä työ odottaa.
4. Poista suhde samasta osiosta, kun riippuvuus ei enää päde.

Riippuvuuksia voi hallita myös GitHub CLI:llä komennolla `gh issue edit` ja sen `--add-blocked-by`- tai `--remove-blocked-by`-valitsimilla, jos käytössä oleva CLI-versio tukee niitä.

## Rajaukset

- Tavallinen tekstissä oleva issue-linkki ei itsessään luo riippuvuutta.
- Älä lisää riippuvuuksia, joita ei ole erikseen sovittu tehtävien järjestyksen perusteella.
- GitHubin natiivit suhteet ovat ainoa pysyvä tietolähde; niitä ei kopioida erilliseen välimuistiin.
- Oma Kehitysjono-Kanban ja sen JSON-välimuisti on arkistoitu. Riippuvuuksia tarkastellaan GitHub Issuesissa ja Aiheseurain-Projectissa.
