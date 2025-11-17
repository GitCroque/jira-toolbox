#!/bin/bash
# Script d'audit hebdomadaire Jira
# Usage: ./cleanup_weekly.sh

DATE=$(date +%Y%m%d)
OUTPUT_DIR="audit_reports/$DATE"

mkdir -p "$OUTPUT_DIR"

echo "🔍 Audit hebdomadaire Jira - $DATE"
echo "=================================="

# Audit utilisateurs inactifs
echo "📋 Vérification des utilisateurs inactifs..."
python3 jira_cli/scripts/user_manager.py inactive > "$OUTPUT_DIR/inactive_users.txt"

# Audit complet des projets
echo "📊 Audit des projets..."
python3 jira_cli/scripts/audit_tool.py projects --output "$OUTPUT_DIR/projects.json"

# Audit des permissions
echo "🔒 Audit des permissions..."
python3 jira_cli/scripts/audit_tool.py permissions --output "$OUTPUT_DIR/permissions.json"

# Audit des groupes
echo "👥 Audit des groupes..."
python3 jira_cli/scripts/audit_tool.py groups --output "$OUTPUT_DIR/groups.json"

# Dashboard global
echo "📈 Génération du dashboard..."
python3 jira_cli/scripts/reporting.py dashboard --output "$OUTPUT_DIR/dashboard.json"

echo ""
echo "✅ Audit terminé: $OUTPUT_DIR"
echo "📁 Fichiers générés:"
ls -lh "$OUTPUT_DIR"
