#!/bin/bash
# Script de monitoring d'un projet Jira
# Usage: ./monitor_project.sh PROJECT-KEY

PROJECT_KEY=$1

if [ -z "$PROJECT_KEY" ]; then
    echo "Usage: $0 PROJECT-KEY"
    echo "Exemple: $0 MYPROJ"
    exit 1
fi

echo "📊 Monitoring du projet $PROJECT_KEY"
echo "===================================="
echo ""

# Détails du projet
echo "ℹ️  Détails du projet:"
python3 jira_cli/scripts/project_manager.py get $PROJECT_KEY --format summary
echo ""

# Statistiques
echo "📈 Statistiques:"
python3 jira_cli/scripts/project_manager.py stats $PROJECT_KEY
echo ""

# Rapport détaillé
echo "📋 Rapport détaillé:"
python3 jira_cli/scripts/reporting.py project $PROJECT_KEY
echo ""

# Rapport SLA
echo "⏱️  Rapport SLA:"
python3 jira_cli/scripts/reporting.py sla $PROJECT_KEY
echo ""

# Export CSV
OUTPUT_FILE="project_${PROJECT_KEY}_$(date +%Y%m%d).csv"
echo "💾 Export CSV: $OUTPUT_FILE"
python3 jira_cli/scripts/reporting.py export-csv $PROJECT_KEY "$OUTPUT_FILE"

echo ""
echo "✅ Monitoring terminé"
