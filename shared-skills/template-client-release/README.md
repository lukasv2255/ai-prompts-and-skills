# Template Client Release

Tento skill prenasi novou verzi z `template` checkoutu do klientske instance a pripravi bezpecny deploy s rollbackem. Pouziva se, kdyz mas oddeleny produktovy vyvoj a zvlast bezici klientskou kopii, ktera potrebuje dostat novy release.

Dulezita cast je disciplína mezi commitem, syncem a deployem: navrhnout commit message, zastavit se na checkpointu, neprepsat klientska data a nechat rollback sledovatelny v klientskem repu.
