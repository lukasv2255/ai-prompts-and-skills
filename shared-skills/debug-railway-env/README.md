# Debug Railway Env

Tento skill je systematicky postup pro hledani problemu s env promennymi na Railway, kdy aplikace nevidi hodnoty, reference vraci prazdno nebo se po deployi chova jinak nez lokalne. Pouziva se hlavne u `DATABASE_URL`, service references a startup chyb po nasazeni.

Smyslem je nejdriv overit skutecny stav variables a logu, potom najit pricinou a az nakonec menit konfiguraci. Skill je vhodny vsude, kde Railway build probiha, ale runtime konfigurace je nespolehliva.
