#!/bin/bash
# Script d'exemple pour la gestion en masse d'issues
# Usage: ./bulk_issue_management.sh

PROJECT_KEY=${1:-"MYPROJ"}

echo "📦 Gestion en masse d'issues pour le projet $PROJECT_KEY"
echo "==============================================="
echo ""

# 1. Export des issues actuelles
echo "📥 Export des issues ouvertes..."
python3 jira_cli/scripts/bulk_operations.py export-csv \
    "project = $PROJECT_KEY AND status != Done" \
    "export_issues_$(date +%Y%m%d).csv"

echo ""

# 2. Transition en masse (mode simulation)
echo "🔄 Simulation: Transition des issues 'To Do' vers 'In Progress'..."
python3 jira_cli/scripts/bulk_operations.py transition "In Progress" \
    --jql "project = $PROJECT_KEY AND status = 'To Do' AND assignee is not EMPTY" \
    --dry-run

echo ""

# 3. Assignation en masse selon la priorité
echo "👤 Assignation des issues haute priorité..."
HIGH_PRIORITY_ISSUES=$(python3 jira_cli/scripts/reporting.py jql \
    "project = $PROJECT_KEY AND priority = High AND assignee is EMPTY" \
    --fields key | jq -r '.[].key' | tr '\n' ' ')

if [ ! -z "$HIGH_PRIORITY_ISSUES" ]; then
    echo "Issues trouvées: $HIGH_PRIORITY_ISSUES"
    # Décommenter et ajouter l'account ID pour assigner
    # python3 jira_cli/scripts/bulk_operations.py assign \
    #     --keys $HIGH_PRIORITY_ISSUES \
    #     --account-id YOUR_ACCOUNT_ID
else
    echo "Aucune issue haute priorité non assignée"
fi

echo ""
echo "✅ Script terminé"
