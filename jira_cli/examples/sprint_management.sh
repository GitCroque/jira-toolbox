#!/bin/bash
# Script d'exemple pour la gestion de sprints
# Usage: ./sprint_management.sh <board-id> [sprint-id]

BOARD_ID=$1
SPRINT_ID=$2

if [ -z "$BOARD_ID" ]; then
    echo "Usage: $0 <board-id> [sprint-id]"
    echo "Exemple: $0 123"
    exit 1
fi

echo "🏃 Gestion de Sprint - Board $BOARD_ID"
echo "====================================="
echo ""

# 1. Lister les sprints actifs
echo "📋 Sprints actifs:"
python3 jira_cli/scripts/sprint_manager.py list $BOARD_ID --state active
echo ""

# 2. Si un sprint ID est fourni, afficher le rapport
if [ ! -z "$SPRINT_ID" ]; then
    echo "📊 Rapport du sprint $SPRINT_ID:"
    python3 jira_cli/scripts/sprint_manager.py report $SPRINT_ID
    echo ""

    echo "📈 Données de burndown:"
    python3 jira_cli/scripts/sprint_manager.py burndown $SPRINT_ID
    echo ""

    echo "📋 Issues du sprint:"
    python3 jira_cli/scripts/sprint_manager.py issues $SPRINT_ID
    echo ""
fi

# 3. Calcul de vélocité
echo "⚡ Vélocité moyenne (5 derniers sprints):"
python3 jira_cli/scripts/sprint_manager.py velocity $BOARD_ID --sprints 5
echo ""

# 4. Export optionnel
if [ ! -z "$SPRINT_ID" ]; then
    OUTPUT_FILE="sprint_${SPRINT_ID}_$(date +%Y%m%d).json"
    echo "💾 Export du résumé: $OUTPUT_FILE"
    python3 jira_cli/scripts/sprint_manager.py export $SPRINT_ID "$OUTPUT_FILE"
fi

echo ""
echo "✅ Analyse terminée"
