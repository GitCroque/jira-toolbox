#!/bin/bash
# Script de vérification de sécurité - Détecte les données sensibles avant commit
# Usage: ./check_security.sh

echo "🔒 Vérification de Sécurité - Jira CLI"
echo "======================================"
echo ""

WARNINGS=0
CRITICAL=0

# Fonction de vérification
check_file() {
    local file=$1
    local pattern=$2
    local message=$3
    local level=$4  # warning ou critical

    if [ -f "$file" ]; then
        if grep -q "$pattern" "$file" 2>/dev/null; then
            if [ "$level" = "critical" ]; then
                echo "   🚨 CRITIQUE: $message"
                echo "      Fichier: $file"
                ((CRITICAL++))
            else
                echo "   ⚠️  AVERTISSEMENT: $message"
                echo "      Fichier: $file"
                ((WARNINGS++))
            fi
        fi
    fi
}

echo "1. Vérification des fichiers de configuration..."
echo "------------------------------------------------"

# Vérifier si des fichiers de config avec credentials sont trackés par git
TRACKED_CONFIGS=$(git ls-files | grep -E '(^|/).*config\.json$|credentials\.json$' | grep -v example)

if [ ! -z "$TRACKED_CONFIGS" ]; then
    echo "   🚨 CRITIQUE: Fichiers de configuration trackés par Git:"
    echo "$TRACKED_CONFIGS" | while read file; do
        echo "      - $file"
        ((CRITICAL++))
    done
    echo ""
    echo "   ❌ ACTION REQUISE: Supprimez ces fichiers du tracking Git:"
    echo "      git rm --cached <fichier>"
    echo "      Puis committez la suppression"
    echo ""
else
    echo "   ✅ Aucun fichier de configuration sensible tracké"
fi

echo ""
echo "2. Vérification des fichiers staged (prêts à être commités)..."
echo "-------------------------------------------------------------"

STAGED_FILES=$(git diff --cached --name-only 2>/dev/null)

if [ ! -z "$STAGED_FILES" ]; then
    echo "$STAGED_FILES" | while read file; do
        if [ -f "$file" ]; then
            # Vérifier les patterns sensibles dans les fichiers staged
            if echo "$file" | grep -qE '(config|credentials)\.json$' && ! echo "$file" | grep -q "example"; then
                echo "   🚨 CRITIQUE: Fichier de config staged: $file"
                ((CRITICAL++))
            fi

            # Vérifier la présence d'un token API dans le fichier
            if grep -qE '"api_token":\s*"[A-Za-z0-9+/=]{20,}"' "$file" 2>/dev/null; then
                echo "   🚨 CRITIQUE: Token API détecté dans: $file"
                ((CRITICAL++))
            fi

            # Vérifier les emails Atlassian
            if grep -qE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|net|org).*atlassian' "$file" 2>/dev/null; then
                echo "   ⚠️  Email potentiellement sensible dans: $file"
                ((WARNINGS++))
            fi

            # Vérifier les URLs d'instances Jira
            if grep -qE 'https?://[a-zA-Z0-9-]+\.atlassian\.net' "$file" 2>/dev/null && ! echo "$file" | grep -qE '(README|INSTALL|example)'; then
                echo "   ⚠️  URL d'instance Jira dans: $file"
                ((WARNINGS++))
            fi
        fi
    done
else
    echo "   ℹ️  Aucun fichier staged"
fi

echo ""
echo "3. Vérification de .gitignore..."
echo "--------------------------------"

if [ -f ".gitignore" ]; then
    if grep -q "config.json" ".gitignore"; then
        echo "   ✅ .gitignore contient des règles pour config.json"
    else
        echo "   🚨 CRITIQUE: .gitignore ne protège pas config.json"
        ((CRITICAL++))
    fi

    if grep -q "credentials.json" ".gitignore"; then
        echo "   ✅ .gitignore contient des règles pour credentials.json"
    else
        echo "   ⚠️  credentials.json n'est pas dans .gitignore"
        ((WARNINGS++))
    fi
else
    echo "   🚨 CRITIQUE: Fichier .gitignore manquant !"
    ((CRITICAL++))
fi

echo ""
echo "4. Vérification des fichiers locaux sensibles..."
echo "------------------------------------------------"

# Vérifier ~/.jira_config.json
if [ -f "$HOME/.jira_config.json" ]; then
    PERMS=$(stat -f "%OLp" "$HOME/.jira_config.json" 2>/dev/null || stat -c "%a" "$HOME/.jira_config.json" 2>/dev/null)
    if [ "$PERMS" = "600" ]; then
        echo "   ✅ ~/.jira_config.json a les bonnes permissions (600)"
    else
        echo "   ⚠️  ~/.jira_config.json permissions: $PERMS (recommandé: 600)"
        echo "      Corrigez avec: chmod 600 ~/.jira_config.json"
        ((WARNINGS++))
    fi
fi

# Vérifier les fichiers de config locaux dans le repo
if [ -f "jira_cli/config/config.json" ]; then
    echo "   ⚠️  Fichier jira_cli/config/config.json détecté (ne devrait pas exister)"
    ((WARNINGS++))
fi

if [ -f "config.json" ]; then
    echo "   ⚠️  Fichier config.json à la racine détecté"
    ((WARNINGS++))
fi

echo ""
echo "5. Vérification de l'historique Git récent..."
echo "---------------------------------------------"

# Vérifier les 5 derniers commits pour des patterns sensibles
RECENT_COMMITS=$(git log --oneline -5 2>/dev/null)

if [ ! -z "$RECENT_COMMITS" ]; then
    echo "   ℹ️  Vérification des 5 derniers commits..."

    git log -5 --pretty=format:"%H" | while read commit; do
        # Vérifier si des fichiers sensibles ont été ajoutés
        ADDED_FILES=$(git diff-tree --no-commit-id --name-only -r $commit | grep -E '(config|credentials)\.json$' | grep -v example)

        if [ ! -z "$ADDED_FILES" ]; then
            echo "   🚨 CRITIQUE: Fichier sensible dans commit $commit:"
            echo "      $ADDED_FILES"
            echo "      ⚠️  Envisagez de réécrire l'historique ou utilisez git-filter-branch"
            ((CRITICAL++))
        fi
    done
else
    echo "   ℹ️  Pas d'historique Git"
fi

echo ""
echo "6. Recommandations de sécurité..."
echo "---------------------------------"

echo "   📝 Bonnes pratiques:"
echo "      • Toujours utiliser ~/.jira_config.json (hors du repo)"
echo "      • Ne JAMAIS committer de fichiers *config.json"
echo "      • Vérifier avec 'git status' avant chaque commit"
echo "      • Permissions 600 pour les fichiers de config"
echo "      • Utiliser des variables d'environnement si possible"

echo ""
echo "========================================"
echo "📊 RÉSUMÉ"
echo "========================================"

if [ $CRITICAL -gt 0 ]; then
    echo ""
    echo "🚨 ALERTE CRITIQUE: $CRITICAL problème(s) critique(s) détecté(s)"
    echo ""
    echo "⛔ NE PAS COMMITTER tant que les problèmes critiques ne sont pas résolus !"
    echo ""
    echo "Actions immédiates requises:"
    echo "  1. Supprimez les fichiers sensibles du staging: git reset HEAD <fichier>"
    echo "  2. Supprimez-les du tracking si nécessaire: git rm --cached <fichier>"
    echo "  3. Vérifiez .gitignore"
    echo "  4. Relancez ce script pour vérifier"
    echo ""
    exit 2
elif [ $WARNINGS -gt 0 ]; then
    echo ""
    echo "⚠️  $WARNINGS avertissement(s) détecté(s)"
    echo ""
    echo "Revoyez les avertissements ci-dessus avant de committer."
    echo "Le commit peut continuer mais soyez vigilant."
    echo ""
    exit 1
else
    echo ""
    echo "✅ Aucun problème de sécurité détecté"
    echo ""
    echo "🔒 Vous pouvez committer en toute sécurité"
    echo ""
    exit 0
fi
