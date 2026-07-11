# Robust Max

Obecný vzor pro hledání **reálného maxima** (nebo prahu/odhadu) z hlučné řady čísel —
odfiltruje nesmysly, ale zachová skutečné špičky. Vzniklo z opravy odhadu FTP ze Stravy
v AI-treneru, kde naivní `max()` bral kariérní rekord i spiky senzoru.

Tři skládatelné obranné vrstvy: **časové okno** (aktuální stav vs. historie),
**absolutní strop/podlaha** (doménová sanity) a **relativní konzistence** vůči
průvodnímu signálu (např. poměr NP/avg). Klíčová myšlenka: na rozdíl od statistického
ořezu outlierů (percentil, IQR) nechceš useknout reálné špičky — jen doménové nesmysly.

Použij při odhadech prahů/rekordů/peaků z historie, kdekoli je `max()` zranitelné
vůči jediné vadné hodnotě.
