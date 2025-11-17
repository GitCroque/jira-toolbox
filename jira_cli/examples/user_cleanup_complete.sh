#!/bin/bash
#
# Script de nettoyage complet des utilisateurs Jira
#
# Ce script effectue un nettoyage complet en plusieurs étapes :
# 1. Audit des utilisateurs
# 2. Identification des comptes inactifs
# 3. Rapport des dernières connexions
# 4. Recommandations de nettoyage
#
# Usage: ./user_cleanup_complete.sh
#
# Ce script est idéal pour :
# - Audit trimestriel des licences
# - Optimisation des coûts Jira
# - Conformité RGPD (comptes inactifs)
# - Sécurité (désactivation des anciens comptes)

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JIRA_CLI="$SCRIPT_DIR/../../jira_cli.py"
OUTPUT_DIR="$SCRIPT_DIR/../../reports/cleanup_complete"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$OUTPUT_DIR/cleanup_complete_$DATE.log"

# Créer le répertoire de sortie
mkdir -p "$OUTPUT_DIR"

# Fonction de logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Fonction pour afficher un séparateur
separator() {
    log "=========================================="
}

# En-tête
clear
separator
log "NETTOYAGE COMPLET DES UTILISATEURS JIRA"
log "Date: $(date +'%Y-%m-%d %H:%M:%S')"
separator
log ""

# Étape 1 : Statistiques générales
log "ÉTAPE 1/6 : Récupération des statistiques"
log ""
python3 "$JIRA_CLI" users cleanup 2>&1 | tee -a "$LOG_FILE"
log ""

# Récupérer les compteurs
ACTIVE_COUNT=$(python3 "$JIRA_CLI" users list-active --format json 2>/dev/null | jq '. | length' || echo "0")
DISABLED_COUNT=$(python3 "$JIRA_CLI" users list-disabled --format json 2>/dev/null | jq '. | length' || echo "0")
TOTAL=$((ACTIVE_COUNT + DISABLED_COUNT))

# Étape 2 : Export des utilisateurs actifs
log "ÉTAPE 2/6 : Export des utilisateurs actifs"
log ""
python3 "$JIRA_CLI" users list-active --format json > "$OUTPUT_DIR/active_users_$DATE.json" 2>&1 | tee -a "$LOG_FILE"
log "✓ Export: $OUTPUT_DIR/active_users_$DATE.json"
log ""

# Étape 3 : Export des utilisateurs désactivés
log "ÉTAPE 3/6 : Export des utilisateurs désactivés"
log ""
python3 "$JIRA_CLI" users list-disabled --format json > "$OUTPUT_DIR/disabled_users_$DATE.json" 2>&1 | tee -a "$LOG_FILE"
log "✓ Export: $OUTPUT_DIR/disabled_users_$DATE.json"
log ""

# Étape 4 : Rapport des dernières connexions (90 jours)
log "ÉTAPE 4/6 : Analyse des dernières connexions (90 jours)"
log ""
python3 "$JIRA_CLI" users list-by-login --days 90 --format csv --output "$OUTPUT_DIR/login_90days_$DATE.csv" 2>&1 | tee -a "$LOG_FILE"
log "✓ Export: $OUTPUT_DIR/login_90days_$DATE.csv"
log ""

# Étape 5 : Rapport des dernières connexions (180 jours)
log "ÉTAPE 5/6 : Analyse des dernières connexions (180 jours)"
log ""
python3 "$JIRA_CLI" users list-by-login --days 180 --format csv --output "$OUTPUT_DIR/login_180days_$DATE.csv" 2>&1 | tee -a "$LOG_FILE"
log "✓ Export: $OUTPUT_DIR/login_180days_$DATE.csv"
log ""

# Étape 6 : Audit complet
log "ÉTAPE 6/6 : Audit complet des accès"
log ""
python3 "$JIRA_CLI" users audit --output "$OUTPUT_DIR/audit_$DATE.json" 2>&1 | tee -a "$LOG_FILE"
log "✓ Export: $OUTPUT_DIR/audit_$DATE.json"
log ""

# Résumé et recommandations
separator
log "RÉSUMÉ DU NETTOYAGE"
separator
log ""
log "📊 STATISTIQUES:"
log "   Total utilisateurs: $TOTAL"
log "   Actifs: $ACTIVE_COUNT"
log "   Désactivés: $DISABLED_COUNT"
log ""

# Calcul du pourcentage
if [ "$TOTAL" -gt 0 ]; then
    DISABLED_PERCENT=$((DISABLED_COUNT * 100 / TOTAL))
else
    DISABLED_PERCENT=0
fi

log "📁 RAPPORTS GÉNÉRÉS:"
log "   • active_users_$DATE.json"
log "   • disabled_users_$DATE.json"
log "   • login_90days_$DATE.csv"
log "   • login_180days_$DATE.csv"
log "   • audit_$DATE.json"
log "   • cleanup_complete_$DATE.log"
log ""
log "📍 Tous les rapports sont dans: $OUTPUT_DIR"
log ""

# Recommandations basées sur les statistiques
separator
log "RECOMMANDATIONS"
separator
log ""

if [ "$DISABLED_COUNT" -gt 0 ]; then
    log "⚠️  $DISABLED_COUNT utilisateurs désactivés détectés ($DISABLED_PERCENT%)"
    log ""
    log "ACTION RECOMMANDÉE:"
    log "   1. Vérifier le fichier: disabled_users_$DATE.json"
    log "   2. Confirmer que ces comptes peuvent être supprimés"
    log "   3. Exécuter: ./cleanup_disabled_users.sh --execute"
    log "   4. Supprimer manuellement via l'admin Jira"
    log ""
fi

if [ "$DISABLED_COUNT" -eq 0 ]; then
    log "✅ Aucun utilisateur désactivé à nettoyer"
    log ""
fi

log "💡 OPTIMISATION DES LICENCES:"
log "   • Analyser login_90days_$DATE.csv"
log "   • Identifier les utilisateurs sans connexion récente"
log "   • Contacter les utilisateurs inactifs"
log "   • Envisager de désactiver les comptes non utilisés"
log ""

log "📅 PROCHAINE ÉTAPE:"
log "   • Programmer ce script en tâche trimestrielle"
log "   • Exemple cron (1er de chaque trimestre):"
log "     0 9 1 1,4,7,10 * $SCRIPT_DIR/user_cleanup_complete.sh"
log ""

# Estimation des économies potentielles
if [ "$DISABLED_COUNT" -gt 0 ]; then
    log "💰 ESTIMATION ÉCONOMIES:"
    log "   Si licence = 7€/mois/utilisateur:"
    log "   Économies mensuelles: $((DISABLED_COUNT * 7))€"
    log "   Économies annuelles: $((DISABLED_COUNT * 7 * 12))€"
    log ""
fi

separator
log "✓ NETTOYAGE COMPLET TERMINÉ"
separator
log ""
log "Log complet: $LOG_FILE"
