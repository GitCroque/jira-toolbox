#!/bin/bash
#
# Script d'audit hebdomadaire des utilisateurs Jira
#
# Ce script génère un rapport complet sur les utilisateurs :
# - Liste des utilisateurs actifs et désactivés
# - Utilisateurs inactifs depuis 90 jours
# - Export CSV pour analyse
#
# Usage: ./user_audit_weekly.sh
# Avec cron (chaque lundi à 8h): 0 8 * * 1 /path/to/user_audit_weekly.sh

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JIRA_CLI="$SCRIPT_DIR/../../jira_cli.py"
OUTPUT_DIR="$SCRIPT_DIR/../../reports/users"
DATE=$(date +%Y%m%d)
LOG_FILE="$OUTPUT_DIR/audit_$DATE.log"

# Créer le répertoire de sortie
mkdir -p "$OUTPUT_DIR"

# Fonction de logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=========================================="
log "AUDIT HEBDOMADAIRE DES UTILISATEURS JIRA"
log "=========================================="

# 1. Audit complet
log ""
log "1. Audit complet des accès..."
python3 "$JIRA_CLI" users audit --output "$OUTPUT_DIR/audit_complet_$DATE.json" 2>&1 | tee -a "$LOG_FILE"

# 2. Liste des utilisateurs actifs
log ""
log "2. Export des utilisateurs actifs..."
python3 "$JIRA_CLI" users list-active --format json > "$OUTPUT_DIR/users_active_$DATE.json" 2>&1 | tee -a "$LOG_FILE"

# 3. Liste des utilisateurs désactivés
log ""
log "3. Export des utilisateurs désactivés..."
python3 "$JIRA_CLI" users list-disabled --format json > "$OUTPUT_DIR/users_disabled_$DATE.json" 2>&1 | tee -a "$LOG_FILE"

# 4. Utilisateurs par dernière connexion
log ""
log "4. Export des utilisateurs par dernière connexion..."
python3 "$JIRA_CLI" users list-by-login --days 90 --format csv --output "$OUTPUT_DIR/users_by_login_$DATE.csv" 2>&1 | tee -a "$LOG_FILE"

# 5. Statistiques
log ""
log "5. Génération des statistiques..."
ACTIVE_COUNT=$(python3 "$JIRA_CLI" users list-active --format json 2>/dev/null | jq '. | length')
DISABLED_COUNT=$(python3 "$JIRA_CLI" users list-disabled --format json 2>/dev/null | jq '. | length')
TOTAL=$((ACTIVE_COUNT + DISABLED_COUNT))

log ""
log "=== RÉSUMÉ DE L'AUDIT ==="
log "Total utilisateurs: $TOTAL"
log "Utilisateurs actifs: $ACTIVE_COUNT"
log "Utilisateurs désactivés: $DISABLED_COUNT"
log ""
log "Rapports générés dans: $OUTPUT_DIR"
log "  • audit_complet_$DATE.json"
log "  • users_active_$DATE.json"
log "  • users_disabled_$DATE.json"
log "  • users_by_login_$DATE.csv"
log ""
log "✓ Audit terminé avec succès"

# 6. Alerte si trop d'utilisateurs désactivés non nettoyés
if [ "$DISABLED_COUNT" -gt 10 ]; then
    log ""
    log "⚠️  ALERTE: $DISABLED_COUNT utilisateurs désactivés détectés"
    log "   Recommandation: Exécuter le script de nettoyage"
    log "   ./cleanup_disabled_users.sh"
fi
