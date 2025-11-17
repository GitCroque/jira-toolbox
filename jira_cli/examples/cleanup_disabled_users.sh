#!/bin/bash
#
# Script de nettoyage des utilisateurs désactivés
#
# Ce script identifie tous les utilisateurs désactivés et génère
# un rapport pour leur suppression/nettoyage.
#
# IMPORTANT: L'API Jira Cloud ne permet pas de supprimer directement
# les utilisateurs. Ce script génère un rapport CSV qui peut être
# utilisé pour un nettoyage manuel ou via l'API Admin.
#
# Usage:
#   ./cleanup_disabled_users.sh           # Mode simulation (dry-run)
#   ./cleanup_disabled_users.sh --execute # Export pour nettoyage manuel
#
# Options:
#   --execute   Générer le rapport d'export (par défaut: simulation uniquement)

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JIRA_CLI="$SCRIPT_DIR/../../jira_cli.py"
OUTPUT_DIR="$SCRIPT_DIR/../../reports/cleanup"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$OUTPUT_DIR/cleanup_$DATE.log"

# Paramètres
EXECUTE=false

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --execute)
            EXECUTE=true
            shift
            ;;
        *)
            echo "Option inconnue: $1"
            echo "Usage: $0 [--execute]"
            exit 1
            ;;
    esac
done

# Créer le répertoire de sortie
mkdir -p "$OUTPUT_DIR"

# Fonction de logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=========================================="
log "NETTOYAGE DES UTILISATEURS DÉSACTIVÉS"
log "=========================================="
log ""

# Vérifier le nombre d'utilisateurs désactivés
log "Recherche des utilisateurs désactivés..."
DISABLED_COUNT=$(python3 "$JIRA_CLI" users list-disabled --format json 2>/dev/null | jq '. | length')

log "✓ Trouvé: $DISABLED_COUNT utilisateurs désactivés"
log ""

if [ "$DISABLED_COUNT" -eq 0 ]; then
    log "✓ Aucun utilisateur désactivé à nettoyer"
    log "✓ Votre instance Jira est propre!"
    exit 0
fi

# Afficher les détails
log "Liste des utilisateurs désactivés:"
python3 "$JIRA_CLI" users list-disabled --format table 2>&1 | tee -a "$LOG_FILE"
log ""

if [ "$EXECUTE" = false ]; then
    # Mode simulation
    log "=========================================="
    log "MODE SIMULATION (DRY-RUN)"
    log "=========================================="
    log ""
    python3 "$JIRA_CLI" users delete-disabled 2>&1 | tee -a "$LOG_FILE"
    log ""
    log "ℹ️  Aucune action n'a été effectuée (mode simulation)"
    log "ℹ️  Pour générer le rapport d'export, utilisez:"
    log "   $0 --execute"
else
    # Mode export
    log "=========================================="
    log "GÉNÉRATION DU RAPPORT D'EXPORT"
    log "=========================================="
    log ""
    python3 "$JIRA_CLI" users delete-disabled --no-dry-run 2>&1 | tee -a "$LOG_FILE"
    log ""
    log "✓ Rapport généré"
    log ""
    log "📋 PROCHAINES ÉTAPES:"
    log "   1. Ouvrir le fichier CSV généré"
    log "   2. Vérifier la liste des utilisateurs"
    log "   3. Se connecter à l'admin Jira: https://admin.atlassian.com"
    log "   4. Aller dans Users > Manage users"
    log "   5. Supprimer les utilisateurs désactivés manuellement"
    log ""
    log "💡 ALTERNATIVE:"
    log "   Utiliser l'API Admin Atlassian (requiert des droits spéciaux):"
    log "   https://developer.atlassian.com/cloud/admin/user-management/rest/"
fi

log ""
log "✓ Opération terminée"
log "Log complet: $LOG_FILE"
