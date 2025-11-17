# Guide de Démarrage Rapide - Jira Toolbox

## Installation en 5 minutes

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. 🔒 Créer votre configuration SÉCURISÉE

**IMPORTANT:** Créez le fichier `~/.jira_config.json` **EN DEHORS du repo Git** :

```bash
cat > ~/.jira_config.json << 'EOF'
{
  "jira_url": "https://votre-instance.atlassian.net",
  "email": "votre.email@example.com",
  "api_token": "VOTRE_TOKEN_API"
}
EOF

# Permissions sécurisées (lecture/écriture propriétaire uniquement)
chmod 600 ~/.jira_config.json
```

**Comment obtenir un token API ?**
1. Allez sur https://id.atlassian.com/manage-profile/security/api-tokens
2. Cliquez sur "Create API token"
3. Nommez-le (ex: "Jira CLI") et copiez le token généré

### 3. 🛡️ Installer la protection des credentials (Recommandé)

```bash
# Installation du hook de sécurité (1 seule fois)
./install_security_hook.sh
```

Ce hook empêchera automatiquement de committer des fichiers sensibles.

### 4. ✅ Testez votre configuration

```bash
python3 jira_cli.py users list
```

Si vous voyez la liste de vos utilisateurs, c'est bon ! 🎉

## 🎯 Modules Disponibles

La suite Jira CLI comprend **9 modules** :

| Module | Description | Commande |
|--------|-------------|----------|
| 👥 **users** | Gestion des utilisateurs | `python3 jira_cli.py users ...` |
| 🔍 **audit** | Audit et monitoring | `python3 jira_cli.py audit ...` |
| 📊 **projects** | Gestion des projets | `python3 jira_cli.py projects ...` |
| 📈 **reports** | Reporting et analytique | `python3 jira_cli.py reports ...` |
| 🎫 **issues** | Gestion des issues | `python3 jira_cli.py issues ...` |
| 🏃 **sprints** | Gestion des sprints | `python3 jira_cli.py sprints ...` |
| 📦 **bulk** | Opérations en masse | `python3 jira_cli.py bulk ...` |
| 📋 **boards** | Gestion des boards | `python3 jira_cli.py boards ...` |
| 📊 **dashboards** | Dashboards et filtres | `python3 jira_cli.py dashboards ...` |

## 🚀 Commandes Essentielles

### Pour Démarrer (Audit complet)

```bash
# Audit complet de votre instance Jira
python3 jira_cli.py audit full --output audit_$(date +%Y%m%d)
```

Génère un répertoire avec : projets, permissions, workflows, groupes.

### Top 10 des Commandes les Plus Utiles

#### 1. Dashboard global

```bash
python3 jira_cli.py reports dashboard
```

#### 2. Créer une issue

```bash
python3 jira_cli.py issues create MYPROJ "Titre de l'issue" --type Task --priority High
```

#### 3. Lister les sprints actifs

```bash
# Trouver le board ID
python3 jira_cli.py boards list

# Voir les sprints actifs
python3 jira_cli.py sprints list <board-id> --state active
```

#### 4. Export en masse (CSV)

```bash
python3 jira_cli.py bulk export-csv "project = MYPROJ AND status != Done" export.csv
```

#### 5. Statistiques d'un projet

```bash
python3 jira_cli.py projects stats MYPROJ
```

#### 6. Utilisateurs inactifs

```bash
python3 jira_cli.py users inactive --days 90
```

#### 7. Rapport SLA

```bash
python3 jira_cli.py reports sla MYPROJ
```

#### 8. Transitions en masse (avec simulation)

```bash
# Mode dry-run (simulation)
python3 jira_cli.py bulk transition "In Progress" --jql "project = MYPROJ AND status = 'To Do'" --dry-run

# Réel (si la simulation est OK)
python3 jira_cli.py bulk transition "In Progress" --jql "project = MYPROJ AND status = 'To Do'"
```

#### 9. Analyse de vélocité

```bash
python3 jira_cli.py sprints velocity <board-id> --sprints 5
```

#### 10. Créer un filtre JQL

```bash
python3 jira_cli.py dashboards filter-create "Mes issues" "assignee = currentUser() AND status != Done" --favourite
```

## 📚 Exemples par Module

### 🎫 Issues (Work Items)

```bash
# Créer
python3 jira_cli.py issues create PROJ "Nouvelle tâche" --type Task

# Changer le statut
python3 jira_cli.py issues transition PROJ-123 "In Progress"

# Ajouter un commentaire
python3 jira_cli.py issues comment-add PROJ-123 "Commentaire ici"

# Lier deux issues
python3 jira_cli.py issues link PROJ-123 PROJ-456 --type Blocks

# Rechercher
python3 jira_cli.py issues search "project = PROJ AND priority = High"
```

### 🏃 Sprints

```bash
# Lister les boards
python3 jira_cli.py sprints boards

# Créer un sprint
python3 jira_cli.py sprints create 123 "Sprint 10" --goal "Finir la feature X"

# Démarrer
python3 jira_cli.py sprints start 456

# Ajouter des issues
python3 jira_cli.py sprints add-issues 456 PROJ-1 PROJ-2 PROJ-3

# Rapport complet
python3 jira_cli.py sprints report 456

# Terminer
python3 jira_cli.py sprints close 456
```

### 📦 Bulk Operations

```bash
# Import depuis CSV
python3 jira_cli.py bulk import-csv issues.csv PROJ

# Export vers CSV
python3 jira_cli.py bulk export-csv "project = PROJ" export.csv

# Transitions en masse
python3 jira_cli.py bulk transition "Done" --keys PROJ-1 PROJ-2 PROJ-3

# Assignation en masse
python3 jira_cli.py bulk assign --jql "project = PROJ AND assignee is EMPTY" --account-id ID
```

### 📋 Boards

```bash
# Lister
python3 jira_cli.py boards list --project PROJ

# Créer
python3 jira_cli.py boards create "Mon Board" --type scrum --project PROJ

# Analyse de performance
python3 jira_cli.py boards analyze 123

# Backlog
python3 jira_cli.py boards backlog 123
```

### 📊 Dashboards & Filtres

```bash
# Lister les filtres
python3 jira_cli.py dashboards filter-list

# Créer un filtre
python3 jira_cli.py dashboards filter-create "Issues ouvertes" "status != Done"

# Partager un filtre
python3 jira_cli.py dashboards filter-share-add 12345 --type group --group developers

# Exporter les résultats
python3 jira_cli.py dashboards filter-export 12345 results.csv --format csv
```

## 🛠️ Scripts Automatisés

### Script 1: Audit Hebdomadaire

```bash
./jira_cli/examples/cleanup_weekly.sh
```

Automatisez avec cron :
```bash
# Chaque lundi à 9h
0 9 * * 1 cd /path/to/jira-toolbox && ./jira_cli/examples/cleanup_weekly.sh
```

### Script 2: Monitoring de Projet

```bash
./jira_cli/examples/monitor_project.sh MYPROJ
```

### Script 3: Gestion en Masse d'Issues

```bash
./jira_cli/examples/bulk_issue_management.sh MYPROJ
```

### Script 4: Analyse de Sprint

```bash
./jira_cli/examples/sprint_management.sh <board-id> <sprint-id>
```

## 🔒 Sécurité - Check-list Quotidienne

Avant chaque `git push` :

```bash
# 1. Vérifier les fichiers à committer
git status

# 2. Lancer la vérification de sécurité
./check_security.sh

# 3. Si tout est OK, commit et push
git add ...
git commit -m "..."
git push
```

**Le hook pre-commit vérifie automatiquement,** mais cette double vérification est recommandée.

## 💡 Cas d'Usage Fréquents

### Audit de Sécurité Mensuel

```bash
DATE=$(date +%Y%m%d)
mkdir -p audit_$DATE

# Export des utilisateurs
python3 jira_cli.py users export audit_$DATE/users.csv

# Audit des accès
python3 jira_cli.py users audit --output audit_$DATE/user_audit.json

# Audit des permissions
python3 jira_cli.py audit permissions --output audit_$DATE/permissions.json

# Audit des groupes
python3 jira_cli.py audit groups --output audit_$DATE/groups.json

echo "✅ Audit complet dans audit_$DATE/"
```

### Migration d'Issues entre Projets

```bash
# 1. Exporter depuis le projet source
python3 jira_cli.py bulk export-csv "project = SOURCE" source_issues.csv

# 2. Modifier le CSV (remplacer le projet)

# 3. Importer vers le projet cible
python3 jira_cli.py bulk import-csv source_issues.csv TARGET
```

### Nettoyage de Sprint en Fin de Cycle

```bash
SPRINT_ID=456

# 1. Voir les issues non terminées
python3 jira_cli.py sprints issues $SPRINT_ID

# 2. Déplacer les issues non terminées vers le prochain sprint
python3 jira_cli.py sprints move-issues <next-sprint-id> PROJ-1 PROJ-2

# 3. Terminer le sprint
python3 jira_cli.py sprints close $SPRINT_ID

# 4. Export du rapport
python3 jira_cli.py sprints export $SPRINT_ID sprint_${SPRINT_ID}_report.json
```

### Gestion des Issues Bloquées

```bash
# Rechercher les issues bloquées
python3 jira_cli.py issues search "status = 'In Progress' AND updated < -7d"

# Ajouter un commentaire à toutes
python3 jira_cli.py bulk transition "Blocked" --jql "status = 'In Progress' AND updated < -7d" --comment "Issue inactive depuis 7 jours"
```

### 🆕 Optimisation des Licences et Nettoyage des Utilisateurs

```bash
# 1. Audit complet des utilisateurs
./jira_cli/examples/user_cleanup_complete.sh

# 2. Analyser les dernières connexions (90 jours)
python3 jira_cli.py users list-by-login --days 90 --format csv --output logins_90d.csv

# 3. Identifier les utilisateurs inactifs
python3 jira_cli.py users list-disabled

# 4. Nettoyage des comptes désactivés (simulation)
python3 jira_cli.py users delete-disabled

# 5. Export pour nettoyage manuel
python3 jira_cli.py users delete-disabled --no-dry-run

# 6. Statistiques et recommandations
python3 jira_cli.py users cleanup
```

**Script automatisé hebdomadaire avec cron :**

```bash
# Éditer la crontab
crontab -e

# Ajouter l'audit hebdomadaire (chaque lundi à 8h)
0 8 * * 1 /path/to/jira-toolbox/jira_cli/examples/user_audit_weekly.sh

# Ajouter le rapport mensuel des connexions (1er de chaque mois à 9h)
0 9 1 * * /path/to/jira-toolbox/jira_cli/examples/user_login_report.sh --days 90
```

**Économies potentielles :**
Si vous avez 20 utilisateurs désactivés non nettoyés et que chaque licence coûte 7€/mois :
- Économies mensuelles : 140€
- Économies annuelles : 1 680€

## ⚡ Astuces pour Gagner du Temps

### Créer un alias

```bash
# Ajoutez dans ~/.zshrc ou ~/.bash_profile
alias jira='python3 /path/to/jira-toolbox/jira_cli.py'

# Rechargez
source ~/.zshrc

# Utilisation
jira issues list
jira sprints boards
```

### Scripts Bash Personnalisés

```bash
# Créer un script pour vos commandes fréquentes
cat > my_daily_jira.sh << 'EOF'
#!/bin/bash
echo "📊 Dashboard du jour"
python3 jira_cli.py reports dashboard

echo ""
echo "🎫 Mes issues"
python3 jira_cli.py issues search "assignee = currentUser() AND status != Done"

echo ""
echo "🏃 Sprints actifs"
python3 jira_cli.py sprints list 123 --state active
EOF

chmod +x my_daily_jira.sh
```

### Utilisation avec jq pour filtrer

```bash
# Obtenir uniquement les clés d'issues
python3 jira_cli.py issues search "project = PROJ" | jq -r '.[].key'

# Compter les issues par statut
python3 jira_cli.py reports project PROJ --output - | jq '.by_status'
```

## 🆘 Résolution de Problèmes

### Erreur: "Configuration incomplète"
```bash
# Vérifiez votre fichier
cat ~/.jira_config.json

# Vérifiez les permissions
ls -la ~/.jira_config.json  # Doit être -rw------- (600)
```

### Erreur: "ModuleNotFoundError: No module named 'requests'"
```bash
pip install -r requirements.txt
```

### Erreur 403: "Forbidden"
→ Votre token n'a pas les permissions nécessaires. Vérifiez que vous êtes administrateur Jira.

### Erreur: "Token API détecté"
→ Vous tentez de committer un fichier avec un token. Le hook de sécurité bloque l'opération.
```bash
git reset HEAD <fichier>  # Retirer du staging
```

### Performance: Requêtes lentes
```bash
# Réduisez le nombre de résultats
python3 jira_cli.py issues search "..." --max 50

# Ou filtrez mieux avec JQL
python3 jira_cli.py issues search "project = PROJ AND updated >= -7d"
```

## 📖 Documentation Complète

| Document | Usage |
|----------|-------|
| **README.md** | Documentation complète (200+ exemples) |
| **SECURITY.md** | Guide de sécurité complet |
| **INSTALLATION_MAC.md** | Installation spécifique Mac |
| **QUICKSTART.md** | Ce guide (démarrage rapide) |

## 🎓 Prochaines Étapes

1. **Explorez les modules** : Testez chaque module avec `--help`
   ```bash
   python3 jira_cli.py issues --help
   python3 jira_cli.py sprints --help
   python3 jira_cli.py bulk --help
   ```

2. **Personnalisez** : Créez vos propres scripts dans `jira_cli/examples/`

3. **Automatisez** : Configurez des tâches cron pour les audits réguliers

4. **Sécurisez** : Vérifiez régulièrement avec `./check_security.sh`

5. **Partagez** : Documentez vos cas d'usage pour votre équipe

## 💬 Support

- **Documentation** : Consultez README.md pour tous les détails
- **Aide en ligne** : `python3 jira_cli.py <module> --help`
- **Sécurité** : Voir SECURITY.md
- **Tests** : Lancez `./test_all_scripts.sh`

## ✅ Check-list de Démarrage

- [ ] Dependencies installées (`pip install -r requirements.txt`)
- [ ] Configuration créée (`~/.jira_config.json` avec chmod 600)
- [ ] Hook de sécurité installé (`./install_security_hook.sh`)
- [ ] Test réussi (`python3 jira_cli.py users list`)
- [ ] Audit initial lancé (`python3 jira_cli.py audit full`)
- [ ] Scripts d'exemple testés
- [ ] Alias créé (optionnel)
- [ ] Documentation lue (README.md)

---

**🎉 Vous êtes prêt à administrer Jira en CLI !**

Bon travail avec Jira Toolbox ! 🚀
