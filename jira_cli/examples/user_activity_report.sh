#!/bin/bash
# Script de rapport d'activité utilisateur
# Usage: ./user_activity_report.sh <account-id> [days]

ACCOUNT_ID=$1
DAYS=${2:-30}

if [ -z "$ACCOUNT_ID" ]; then
    echo "Usage: $0 <account-id> [days]"
    echo "Exemple: $0 5d3e234f8b7c9a0001234567 30"
    exit 1
fi

OUTPUT_DIR="user_reports"
mkdir -p "$OUTPUT_DIR"

echo "👤 Rapport d'activité utilisateur"
echo "=================================="
echo "Account ID: $ACCOUNT_ID"
echo "Période: $DAYS derniers jours"
echo ""

# Rapport d'activité
OUTPUT_FILE="$OUTPUT_DIR/user_${ACCOUNT_ID}_$(date +%Y%m%d).json"
python3 jira_cli/scripts/reporting.py user "$ACCOUNT_ID" --days $DAYS --output "$OUTPUT_FILE"

echo ""
echo "✅ Rapport généré: $OUTPUT_FILE"

# Afficher un résumé
if [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "📊 Résumé:"
    cat "$OUTPUT_FILE" | jq '{
        issues_created: .issues_created,
        issues_assigned: .issues_assigned,
        issues_resolved: .issues_resolved
    }'
fi
