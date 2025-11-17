# Guide de Démarrage Rapide - Jira Toolbox

## Installation en 5 minutes

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Créer votre configuration

Créez le fichier `~/.jira_config.json` :

```bash
cat > ~/.jira_config.json << 'EOF'
{
  "jira_url": "https://votre-instance.atlassian.net",
  "email": "votre.email@example.com",
  "api_token": "VOTRE_TOKEN_API"
}
EOF

chmod 600 ~/.jira_config.json
```

**Comment obtenir un token API ?**
1. Allez sur https://id.atlassian.com/manage-profile/security/api-tokens
2. Cliquez sur "Create API token"
3. Copiez le token généré

### 3. Testez votre configuration

```bash
python3 jira_cli.py users list
```

Si vous voyez la liste de vos utilisateurs, c'est bon ! 🎉

## Commandes Essentielles

### Audit complet (recommandé pour démarrer)

```bash
# Audit complet de votre instance
python3 jira_cli/scripts/audit_tool.py full --output audit_$(date +%Y%m%d)
```

Cela générera un répertoire avec tous les audits (projets, permissions, workflows, groupes).

### Top 5 des commandes les plus utiles

#### 1. Dashboard global

```bash
python3 jira_cli.py reports dashboard
```

#### 2. Liste des utilisateurs avec export CSV

```bash
python3 jira_cli.py users export users_$(date +%Y%m%d).csv
```

#### 3. Statistiques d'un projet

```bash
python3 jira_cli.py projects stats VOTRE-PROJET
```

#### 4. Utilisateurs inactifs

```bash
python3 jira_cli.py users inactive
```

#### 5. Rapport SLA d'un projet

```bash
python3 jira_cli.py reports sla VOTRE-PROJET
```

## Scripts Automatisés

### Audit hebdomadaire automatique

```bash
# Rendre le script exécutable
chmod +x jira_cli/examples/cleanup_weekly.sh

# Lancer l'audit
./jira_cli/examples/cleanup_weekly.sh
```

Ajoutez-le à votre crontab pour l'automatiser :

```bash
# Exécuter chaque lundi à 9h
0 9 * * 1 cd /path/to/jira-toolbox && ./jira_cli/examples/cleanup_weekly.sh
```

### Monitoring de projet

```bash
./jira_cli/examples/monitor_project.sh VOTRE-PROJET
```

## Cas d'Usage Fréquents

### Audit de Sécurité Mensuel

```bash
DATE=$(date +%Y%m%d)

# 1. Export des utilisateurs
python3 jira_cli.py users export "audit_$DATE/users.csv"

# 2. Utilisateurs inactifs
python3 jira_cli.py users audit --output "audit_$DATE/user_audit.json"

# 3. Audit des permissions
python3 jira_cli.py audit permissions --output "audit_$DATE/permissions.json"

# 4. Audit des groupes
python3 jira_cli.py audit groups --output "audit_$DATE/groups.json"
```

### Rapport de Performance des Projets

```bash
# Pour chaque projet
for project in PROJ1 PROJ2 PROJ3; do
    echo "=== Rapport $project ==="
    python3 jira_cli.py projects stats $project
    python3 jira_cli.py reports sla $project
    echo ""
done
```

### Recherche Avancée avec JQL

```bash
# Issues créées dans les 7 derniers jours
python3 jira_cli.py reports jql "created >= -7d" --output recent_issues.json

# Issues non assignées
python3 jira_cli.py reports jql "assignee is EMPTY" --output unassigned.json

# Issues priorité haute ouvertes
python3 jira_cli.py reports jql "priority = High AND status != Done"
```

## Utilisation Simplifiée

Au lieu de :
```bash
python3 jira_cli/scripts/user_manager.py list
```

Vous pouvez utiliser :
```bash
python3 jira_cli.py users list
```

C'est plus court et plus facile à retenir !

## Résolution de Problèmes

### Erreur: "Configuration incomplète"
→ Vérifiez votre fichier `~/.jira_config.json`

### Erreur: "ModuleNotFoundError"
→ Lancez `pip install -r requirements.txt`

### Erreur 403
→ Votre token n'a pas les permissions nécessaires. Vérifiez que vous êtes administrateur Jira.

### Timeout
→ Réduisez la portée de vos requêtes ou augmentez le timeout dans `jira_client.py`

## Prochaines Étapes

1. Explorez le README.md complet pour toutes les fonctionnalités
2. Personnalisez les scripts d'exemple dans `jira_cli/examples/`
3. Automatisez vos audits avec cron
4. Créez vos propres scripts personnalisés

## Support

- Consultez le README.md pour la documentation complète
- Utilisez `--help` sur chaque commande pour plus de détails
- Exemple : `python3 jira_cli.py users --help`

Bon audit ! 🚀
