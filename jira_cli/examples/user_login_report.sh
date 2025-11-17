#!/bin/bash
#
# Script de rapport des dernières connexions utilisateurs
#
# Génère un rapport détaillé des dernières connexions des utilisateurs
# pour identifier les comptes inactifs et optimiser les licences.
#
# Usage:
#   ./user_login_report.sh              # Rapport des 90 derniers jours
#   ./user_login_report.sh --days 30    # Rapport des 30 derniers jours
#   ./user_login_report.sh --days 180   # Rapport des 180 derniers jours
#
# Options:
#   --days N    Nombre de jours à analyser (défaut: 90)
#   --format    Format de sortie: table, csv, json (défaut: table)
#   --output    Fichier de sortie (pour CSV)

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JIRA_CLI="$SCRIPT_DIR/../../jira_cli.py"
OUTPUT_DIR="$SCRIPT_DIR/../../reports/login"
DATE=$(date +%Y%m%d_%H%M%S)

# Paramètres par défaut
DAYS=90
FORMAT="table"
OUTPUT=""

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --days)
            DAYS="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        *)
            echo "Option inconnue: $1"
            echo "Usage: $0 [--days N] [--format table|csv|json] [--output FILE]"
            exit 1
            ;;
    esac
done

# Créer le répertoire de sortie
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "RAPPORT DES DERNIÈRES CONNEXIONS"
echo "=========================================="
echo ""
echo "Période d'analyse: $DAYS derniers jours"
echo "Format de sortie: $FORMAT"
echo ""

# Générer le rapport
if [ -z "$OUTPUT" ]; then
    # Sortie vers stdout
    if [ "$FORMAT" = "csv" ]; then
        OUTPUT="$OUTPUT_DIR/user_logins_${DAYS}days_$DATE.csv"
        echo "Export vers: $OUTPUT"
        python3 "$JIRA_CLI" users list-by-login --days "$DAYS" --format csv --output "$OUTPUT"
    else
        python3 "$JIRA_CLI" users list-by-login --days "$DAYS" --format "$FORMAT"
    fi
else
    # Sortie vers fichier spécifié
    echo "Export vers: $OUTPUT"
    python3 "$JIRA_CLI" users list-by-login --days "$DAYS" --format csv --output "$OUTPUT"
fi

echo ""
echo "✓ Rapport généré avec succès"
echo ""
echo "💡 CONSEILS D'UTILISATION:"
echo "   • Identifier les utilisateurs sans connexion récente"
echo "   • Optimiser les licences Jira en désactivant les comptes inactifs"
echo "   • Contacter les utilisateurs inactifs avant désactivation"
echo "   • Effectuer un audit régulier (recommandé: mensuel)"
echo ""
echo "📊 ANALYSES POSSIBLES:"
echo "   • Utilisateurs n'ayant jamais ouvert Jira"
echo "   • Comptes créés mais jamais utilisés"
echo "   • Utilisateurs actifs vs licences payées"
echo "   • Tendances d'utilisation par période"
