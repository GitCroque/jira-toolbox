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

### Bonnes Pratiques

1. **Ne jamais commiter les tokens API** dans Git
2. Utilisez `.gitignore` pour exclure les fichiers de configuration
3. Limitez les permissions du fichier de config:
   ```bash
   chmod 600 ~/.jira_config.json
   ```
4. Utilisez des tokens API avec des permissions minimales
5. Renouvelez régulièrement vos tokens

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