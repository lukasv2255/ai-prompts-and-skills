---
name: git-push-pull
description: Push/pull projekt na GitHub. Použij když uživatel říká "pushi na git", "pushni", "pullni", "pull z gitu", "git pull", "synchronizuj git".
allowed-tools: Bash, Read
---

# Git Push / Pull

Proveď bez ptaní — rovnou pushni nebo pullni.

## Push

```bash
cd /cesta/k/projektu
git add <soubory>          # pouze pokud jsou unstaged změny
git commit -m "zpráva"    # pouze pokud není commit
git push origin master
```

Pokud je `Your branch is up to date` — vše je OK, není co pushovat.

## Pull (na jiném počítači)

```bash
git clone https://github.com/lukasv2255/spread-monitor.git
# nebo:
git pull origin master
```

## Pravidla

- Neptat se na potvrzení — prostě udělat
- Necommitovat `.env`, `collector_log.txt`, `snapshot.txt`, `*.db`
- Zkontrolovat `git status` před commitem co jde do stage
