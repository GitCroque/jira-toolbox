# Jira Toolbox - Suite CLI pour Administration Jira Cloud

Une collection complète de scripts CLI Python pour administrer, auditer et contrôler votre instance Jira Cloud.

## 🎯 Fonctionnalités

### 👥 Gestion des Utilisateurs (`user_manager.py`)
- Lister tous les utilisateurs
- Rechercher des utilisateurs
- Auditer les accès et permissions
- Identifier les utilisateurs inactifs
- Exporter les utilisateurs en CSV
- Gérer les groupes d'utilisateurs

### 🔍 Audit et Monitoring (`audit_tool.py`)
- Audit complet des projets
- Audit des permissions et schémas
- Audit des workflows
- Audit des groupes et rôles
- Logs d'audit (Jira Cloud Premium)
- Vérification de sécurité

### 📊 Gestion des Projets (`project_manager.py`)
- Lister et rechercher des projets
- Obtenir les détails complets d'un projet
- Gérer les composants et versions
- Statistiques sur les issues
- Archiver/Restaurer des projets
- Exporter la configuration complète

### 📈 Reporting et Analytique (`reporting.py`)
- Rapports de projet détaillés
- Rapports d'activité utilisateur
- Rapports SLA et temps de résolution
- Dashboard global
- Export CSV des issues
- Recherches JQL personnalisées

### 🎫 Gestion des Issues (`issue_manager.py`) ⭐ NOUVEAU
- Créer, éditer, supprimer des issues
- Transitions de workflow (To Do → In Progress → Done)
- Gestion complète des commentaires
- Pièces jointes (upload, download, delete)
- Watchers (observateurs)
- Liens entre issues (Blocks, Relates to, etc.)
- Clone d'issues
- Assignation

### 🏃 Gestion des Sprints (`sprint_manager.py`) ⭐ NOUVEAU
- Créer, modifier, supprimer des sprints
- Démarrer et terminer des sprints
- Ajouter/retirer des issues
- Déplacer des issues entre sprints
- Calcul de vélocité moyenne
- Rapports de burndown
- Analyse de performance

### 📦 Opérations en Masse (`bulk_operations.py`) ⭐ NOUVEAU
- Création en masse d'issues
- Mise à jour en masse
- Suppression en masse
- Transitions en masse
- Assignation en masse
- Import/Export CSV
- Mode dry-run (simulation)

### 📋 Gestion des Boards (`board_manager.py`) ⭐ NOUVEAU
- Lister et rechercher des boards
- Créer et configurer des boards
- Gérer les colonnes
- Analyse de performance
- Export de configuration
- Gestion du backlog
- Epics et versions

### 📊 Dashboards et Filtres (`dashboard_manager.py`) ⭐ NOUVEAU
- Créer et gérer des dashboards
- Copier des dashboards
- Créer et gérer des filtres JQL
- Partager des filtres
- Gérer les favoris
- Changer la propriété
- Export des résultats

## 🚀 Installation

### Prérequis
- Python 3.7+
- pip
- Compte Jira Cloud avec accès administrateur

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Créer un token API Jira

1. Connectez-vous à votre compte Atlassian
2. Allez sur https://id.atlassian.com/manage-profile/security/api-tokens
3. Cliquez sur "Create API token"
4. Nommez votre token et copiez-le

### 2. Configuration du client

Créez un fichier `~/.jira_config.json` :

```json
{
  "jira_url": "https://votre-instance.atlassian.net",
  "email": "votre-email@exemple.com",
  "api_token": "votre-token-api"
}
```

**Alternative:** Utilisez des variables d'environnement :

```bash
export JIRA_URL="https://votre-instance.atlassian.net"
export JIRA_EMAIL="votre-email@exemple.com"
export JIRA_API_TOKEN="votre-token-api"
```

## 📖 Utilisation

### Gestion des Utilisateurs

```bash
# Lister tous les utilisateurs
python3 jira_cli/scripts/user_manager.py list

# Rechercher un utilisateur
python3 jira_cli/scripts/user_manager.py search "nom.prenom"

# Obtenir les groupes d'un utilisateur
python3 jira_cli/scripts/user_manager.py groups <account-id>

# Identifier les utilisateurs inactifs
python3 jira_cli/scripts/user_manager.py inactive

# Exporter les utilisateurs en CSV
python3 jira_cli/scripts/user_manager.py export utilisateurs.csv

# Audit complet des accès
python3 jira_cli/scripts/user_manager.py audit --output audit_users.json
```

### Audit et Monitoring

```bash
# Audit de tous les projets
python3 jira_cli/scripts/audit_tool.py projects

# Audit des rôles d'un projet
python3 jira_cli/scripts/audit_tool.py roles PROJECT-KEY

# Audit des permissions
python3 jira_cli/scripts/audit_tool.py permissions

# Audit des workflows
python3 jira_cli/scripts/audit_tool.py workflows

# Audit des groupes
python3 jira_cli/scripts/audit_tool.py groups

# Audit complet avec export
python3 jira_cli/scripts/audit_tool.py full --output audit_complet/

# Récupérer les logs d'audit (Premium)
python3 jira_cli/scripts/audit_tool.py logs --from 2024-01-01 --to 2024-12-31
```

### Gestion des Projets

```bash
# Lister tous les projets
python3 jira_cli/scripts/project_manager.py list

# Détails d'un projet
python3 jira_cli/scripts/project_manager.py get PROJECT-KEY

# Composants d'un projet
python3 jira_cli/scripts/project_manager.py components PROJECT-KEY

# Versions d'un projet
python3 jira_cli/scripts/project_manager.py versions PROJECT-KEY

# Statistiques d'un projet
python3 jira_cli/scripts/project_manager.py stats PROJECT-KEY

# Exporter la configuration complète
python3 jira_cli/scripts/project_manager.py export PROJECT-KEY --output project_config.json

# Archiver un projet
python3 jira_cli/scripts/project_manager.py archive PROJECT-KEY --confirm

# Restaurer un projet
python3 jira_cli/scripts/project_manager.py restore PROJECT-KEY
```

### Reporting et Analytique

```bash
# Rapport d'un projet
python3 jira_cli/scripts/reporting.py project PROJECT-KEY

# Activité d'un utilisateur (30 derniers jours)
python3 jira_cli/scripts/reporting.py user <account-id> --days 30

# Rapport SLA
python3 jira_cli/scripts/reporting.py sla PROJECT-KEY

# Dashboard global
python3 jira_cli/scripts/reporting.py dashboard

# Exporter les issues en CSV
python3 jira_cli/scripts/reporting.py export-csv PROJECT-KEY issues.csv

# Recherche JQL personnalisée
python3 jira_cli/scripts/reporting.py jql "project = PROJ AND status = Open"
```

### Gestion des Issues ⭐ NOUVEAU

```bash
# Créer une issue
python3 jira_cli/scripts/issue_manager.py create PROJ "Ma nouvelle issue" --type Task --priority High

# Voir une issue
python3 jira_cli/scripts/issue_manager.py get PROJ-123

# Mettre à jour une issue
python3 jira_cli/scripts/issue_manager.py update PROJ-123 --summary "Nouveau titre" --priority Medium

# Changer le statut (transition)
python3 jira_cli/scripts/issue_manager.py transition PROJ-123 "In Progress" --comment "Je commence"

# Voir les transitions disponibles
python3 jira_cli/scripts/issue_manager.py transitions PROJ-123

# Assigner une issue
python3 jira_cli/scripts/issue_manager.py assign PROJ-123 --account-id 5d3e234f8b7c9a0001234567

# Cloner une issue
python3 jira_cli/scripts/issue_manager.py clone PROJ-123 --summary "Clone de l'issue"

# Ajouter un commentaire
python3 jira_cli/scripts/issue_manager.py comment-add PROJ-123 "Voici mon commentaire"

# Lister les commentaires
python3 jira_cli/scripts/issue_manager.py comment-list PROJ-123

# Ajouter une pièce jointe
python3 jira_cli/scripts/issue_manager.py attachment-add PROJ-123 /path/to/file.pdf

# Lister les pièces jointes
python3 jira_cli/scripts/issue_manager.py attachment-list PROJ-123

# Ajouter un observateur
python3 jira_cli/scripts/issue_manager.py watcher-add PROJ-123 account-id

# Lier deux issues
python3 jira_cli/scripts/issue_manager.py link PROJ-123 PROJ-456 --type Blocks

# Rechercher des issues
python3 jira_cli/scripts/issue_manager.py search "project = PROJ AND status = Open"

# Supprimer une issue
python3 jira_cli/scripts/issue_manager.py delete PROJ-123 --confirm
```

### Gestion des Sprints ⭐ NOUVEAU

```bash
# Lister les boards
python3 jira_cli/scripts/sprint_manager.py boards --project PROJ

# Créer un sprint
python3 jira_cli/scripts/sprint_manager.py create 123 "Sprint 10" --goal "Objectif du sprint"

# Démarrer un sprint
python3 jira_cli/scripts/sprint_manager.py start 456

# Lister les sprints d'un board
python3 jira_cli/scripts/sprint_manager.py list 123

# Voir les issues d'un sprint
python3 jira_cli/scripts/sprint_manager.py issues 456

# Ajouter des issues au sprint
python3 jira_cli/scripts/sprint_manager.py add-issues 456 PROJ-123 PROJ-124 PROJ-125

# Retirer des issues du sprint
python3 jira_cli/scripts/sprint_manager.py remove-issues PROJ-123 PROJ-124

# Déplacer des issues vers un autre sprint
python3 jira_cli/scripts/sprint_manager.py move-issues 789 PROJ-123 PROJ-124

# Rapport de sprint
python3 jira_cli/scripts/sprint_manager.py report 456

# Calculer la vélocité moyenne
python3 jira_cli/scripts/sprint_manager.py velocity 123 --sprints 5

# Données de burndown
python3 jira_cli/scripts/sprint_manager.py burndown 456

# Terminer un sprint
python3 jira_cli/scripts/sprint_manager.py close 456

# Exporter un résumé complet
python3 jira_cli/scripts/sprint_manager.py export 456 sprint_summary.json
```

### Opérations en Masse ⭐ NOUVEAU

```bash
# Import CSV
python3 jira_cli/scripts/bulk_operations.py import-csv issues.csv PROJ --type Task

# Export CSV
python3 jira_cli/scripts/bulk_operations.py export-csv "project = PROJ" export.csv

# Transition en masse (avec JQL)
python3 jira_cli/scripts/bulk_operations.py transition "In Progress" --jql "project = PROJ AND status = 'To Do'" --dry-run

# Transition en masse (sans dry-run)
python3 jira_cli/scripts/bulk_operations.py transition "In Progress" --jql "project = PROJ AND status = 'To Do'"

# Assignation en masse
python3 jira_cli/scripts/bulk_operations.py assign --keys PROJ-1 PROJ-2 PROJ-3 --account-id 5d3e234f8b7c9a

# Suppression en masse (avec confirmation)
python3 jira_cli/scripts/bulk_operations.py delete --jql "project = TEMP" --confirm

# Mise à jour en masse depuis JSON
python3 jira_cli/scripts/bulk_operations.py update updates.json

# Création en masse depuis JSON
python3 jira_cli/scripts/bulk_operations.py create issues.json --dry-run
```

### Gestion des Boards ⭐ NOUVEAU

```bash
# Lister tous les boards
python3 jira_cli/scripts/board_manager.py list

# Lister les boards d'un projet
python3 jira_cli/scripts/board_manager.py list --project PROJ

# Voir un board
python3 jira_cli/scripts/board_manager.py get 123

# Créer un board
python3 jira_cli/scripts/board_manager.py create "Mon Board" --type scrum --project PROJ

# Configuration d'un board
python3 jira_cli/scripts/board_manager.py config 123

# Voir les colonnes
python3 jira_cli/scripts/board_manager.py columns 123

# Issues d'un board
python3 jira_cli/scripts/board_manager.py issues 123 --max 100

# Backlog
python3 jira_cli/scripts/board_manager.py backlog 123

# Sprints du board
python3 jira_cli/scripts/board_manager.py sprints 123 --state active

# Epics
python3 jira_cli/scripts/board_manager.py epics 123

# Versions
python3 jira_cli/scripts/board_manager.py versions 123 --unreleased

# Résumé complet
python3 jira_cli/scripts/board_manager.py summary 123

# Analyse de performance
python3 jira_cli/scripts/board_manager.py analyze 123

# Export configuration
python3 jira_cli/scripts/board_manager.py export 123 board_config.json

# Supprimer un board
python3 jira_cli/scripts/board_manager.py delete 123 --confirm
```

### Dashboards et Filtres ⭐ NOUVEAU

```bash
# Lister les dashboards
python3 jira_cli/scripts/dashboard_manager.py dashboard-list

# Rechercher un dashboard
python3 jira_cli/scripts/dashboard_manager.py dashboard-search --name "Mon Dashboard"

# Copier un dashboard
python3 jira_cli/scripts/dashboard_manager.py dashboard-copy abc123 "Copie de mon dashboard"

# Lister les filtres
python3 jira_cli/scripts/dashboard_manager.py filter-list

# Rechercher des filtres
python3 jira_cli/scripts/dashboard_manager.py filter-search --name "Mes issues"

# Créer un filtre
python3 jira_cli/scripts/dashboard_manager.py filter-create "Issues ouvertes" "project = PROJ AND status != Done" --favourite

# Mettre à jour un filtre
python3 jira_cli/scripts/dashboard_manager.py filter-update 12345 --name "Nouveau nom"

# Cloner un filtre
python3 jira_cli/scripts/dashboard_manager.py filter-clone 12345 "Clone du filtre"

# Lister les favoris
python3 jira_cli/scripts/dashboard_manager.py favourite-list

# Ajouter aux favoris
python3 jira_cli/scripts/dashboard_manager.py favourite-add 12345

# Changer le propriétaire
python3 jira_cli/scripts/dashboard_manager.py filter-change-owner 12345 account-id

# Permissions de partage
python3 jira_cli/scripts/dashboard_manager.py filter-share-list 12345

# Partager avec un groupe
python3 jira_cli/scripts/dashboard_manager.py filter-share-add 12345 --type group --group developers

# Exporter les résultats d'un filtre
python3 jira_cli/scripts/dashboard_manager.py filter-export 12345 results.csv --format csv

# Supprimer un filtre
python3 jira_cli/scripts/dashboard_manager.py filter-delete 12345 --confirm
```

## 🛠️ Scripts Personnalisés

### Exemple: Script de nettoyage hebdomadaire

```bash
#!/bin/bash
# cleanup_weekly.sh

DATE=$(date +%Y%m%d)
OUTPUT_DIR="audit_reports/$DATE"

mkdir -p "$OUTPUT_DIR"

echo "🔍 Audit hebdomadaire Jira - $DATE"

# Audit utilisateurs inactifs
python3 jira_cli/scripts/user_manager.py inactive > "$OUTPUT_DIR/inactive_users.txt"

# Audit complet des projets
python3 jira_cli/scripts/audit_tool.py projects --output "$OUTPUT_DIR/projects.json"

# Dashboard global
python3 jira_cli/scripts/reporting.py dashboard --output "$OUTPUT_DIR/dashboard.json"

echo "✅ Audit terminé: $OUTPUT_DIR"
```

### Exemple: Monitoring de projet

```bash
#!/bin/bash
# monitor_project.sh

PROJECT_KEY=$1

if [ -z "$PROJECT_KEY" ]; then
    echo "Usage: $0 PROJECT-KEY"
    exit 1
fi

echo "📊 Monitoring du projet $PROJECT_KEY"

# Statistiques
python3 jira_cli/scripts/project_manager.py stats $PROJECT_KEY

# Rapport détaillé
python3 jira_cli/scripts/reporting.py project $PROJECT_KEY

# Rapport SLA
python3 jira_cli/scripts/reporting.py sla $PROJECT_KEY
```

## 📁 Structure du Projet

```
jira-toolbox/
├── jira_cli/
│   ├── lib/
│   │   └── jira_client.py       # Client API Jira
│   ├── scripts/
│   │   ├── user_manager.py      # Gestion utilisateurs
│   │   ├── audit_tool.py        # Audit et monitoring
│   │   ├── project_manager.py   # Gestion projets
│   │   └── reporting.py         # Reporting
│   ├── config/
│   │   └── config.example.json  # Exemple de configuration
│   └── examples/
│       └── custom_scripts/      # Scripts personnalisés
├── requirements.txt
└── README.md
```

## 🔒 Sécurité

### ⚠️ IMPORTANT: Protection des Credentials

**Vos tokens API Jira ne doivent JAMAIS être committés dans Git !**

Consultez le **[Guide de Sécurité Complet](SECURITY.md)** pour tous les détails.

### 🛡️ Mesures de Protection Automatiques

#### 1. Vérification de Sécurité

Avant de push, lancez:

```bash
./check_security.sh
```

Ce script vérifie:
- ✅ Aucun fichier sensible tracké par Git
- ✅ Aucun token API dans les fichiers staged
- ✅ Configuration .gitignore correcte
- ✅ Permissions des fichiers sécurisées

#### 2. Hook Pre-Commit Automatique (Recommandé)

Installez le hook qui vérifie **automatiquement** avant chaque commit:

```bash
./install_security_hook.sh
```

Le hook bloquera automatiquement tout commit contenant:
- Fichiers `*config.json` (sauf `*example*.json`)
- Tokens API
- Credentials

### Bonnes Pratiques

1. **✅ Utilisez ~/.jira_config.json** (hors du repo)
   ```bash
   cat > ~/.jira_config.json << 'EOF'
   {
     "jira_url": "https://votre-instance.atlassian.net",
     "email": "votre.email@exemple.com",
     "api_token": "VOTRE_TOKEN"
   }
   EOF
   chmod 600 ~/.jira_config.json
   ```

2. **✅ Ou utilisez des variables d'environnement**
   ```bash
   export JIRA_URL="https://votre-instance.atlassian.net"
   export JIRA_EMAIL="votre.email@exemple.com"
   export JIRA_API_TOKEN="votre_token"
   ```

3. **✅ Installez le hook de sécurité**
   ```bash
   ./install_security_hook.sh
   ```

4. **✅ Vérifiez avant de push**
   ```bash
   ./check_security.sh
   git status
   git push
   ```

5. **✅ Renouvelez vos tokens régulièrement** (tous les 3-6 mois)

### ❌ À NE JAMAIS FAIRE

- ❌ Créer un fichier `config.json` dans le repo
- ❌ Committer des fichiers contenant des tokens
- ❌ Partager votre fichier de configuration
- ❌ Utiliser des permissions trop ouvertes (700+)
- ❌ Bypass le hook de sécurité sans raison valable

### 🚨 En Cas de Fuite

Si vous avez accidentellement commité des credentials:

1. **Révoquez immédiatement votre token API:**
   - https://id.atlassian.com/manage-profile/security/api-tokens

2. **Supprimez le fichier du repo:**
   ```bash
   git rm --cached fichier_sensible.json
   git commit -m "Remove sensitive file"
   git push
   ```

3. **Consultez [SECURITY.md](SECURITY.md) pour les étapes complètes**

### Permissions Requises

Pour utiliser tous les scripts, votre compte Jira doit avoir:
- Jira Administrator (pour l'audit complet)
- Browse Projects (minimum pour la lecture)
- Administer Projects (pour la gestion des projets)

## 📊 Cas d'Usage Typiques

### En tant que Responsable SI

#### 1. Audit mensuel de sécurité
```bash
# Générer un audit complet
python3 jira_cli/scripts/audit_tool.py full --output audit_$(date +%Y%m)/

# Vérifier les utilisateurs inactifs
python3 jira_cli/scripts/user_manager.py audit --output audit_users_$(date +%Y%m%d).json

# Exporter tous les utilisateurs
python3 jira_cli/scripts/user_manager.py export users_$(date +%Y%m%d).csv
```

#### 2. Monitoring de performance des projets
```bash
# Dashboard global
python3 jira_cli/scripts/reporting.py dashboard

# SLA par projet
for project in PROJ1 PROJ2 PROJ3; do
    python3 jira_cli/scripts/reporting.py sla $project --output sla_$project.json
done
```

#### 3. Nettoyage et optimisation
```bash
# Identifier les utilisateurs inactifs
python3 jira_cli/scripts/user_manager.py inactive --days 180

# Projets à archiver (analyse manuelle ensuite)
python3 jira_cli/scripts/project_manager.py list --format json | \
    jq '.[] | select(.archived == false)'
```

#### 4. Rapports pour la direction
```bash
# Rapport d'activité global
python3 jira_cli/scripts/reporting.py dashboard --output rapport_direction.json

# Export des projets actifs
python3 jira_cli/scripts/audit_tool.py projects --output projets_actifs.json
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à:
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Soumettre des pull requests

## 📝 Licence

Ce projet est sous licence MIT.

## 🆘 Support et Dépannage

### Erreur d'authentification
```
Erreur: Configuration incomplète
```
→ Vérifiez votre fichier de configuration et vos credentials

### Erreur 403
```
Erreur HTTP 403
```
→ Vérifiez que votre token API a les permissions nécessaires

### Erreur de module
```
ModuleNotFoundError: No module named 'requests'
```
→ Installez les dépendances: `pip install -r requirements.txt`

### Timeout
```
Timeout error
```
→ Votre instance Jira est peut-être trop chargée, réessayez plus tard

## 📚 Ressources

- [Documentation API Jira Cloud](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Guide de gestion des tokens API](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
- [JQL (Jira Query Language)](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)

## 🎯 Roadmap

- [ ] Support des webhooks Jira
- [ ] Intégration avec Confluence
- [ ] Interface web pour les rapports
- [ ] Alertes automatiques par email
- [ ] Support des custom fields
- [ ] Backup automatique des configurations

---

**Développé pour les responsables SI qui ont besoin d'outils puissants pour administrer Jira Cloud** 🚀