# Tray App

Tento skill popisuje, jak udelat menu bar nebo tray aplikaci pro dlouho bezici Python skript na macOS. Je to alternativni special-case pro situace, kdy je skutecne potreba klikaci ovladani pres ikonku v menu baru.

Pro bezny dlouhodoby beh agentu, collectoru a botu je vhodnejsi `launchd-agent`. `tray-app` ma smysl hlavne pro osobni desktopove nastroje, kde je GUI ovladani soucast workflow.
