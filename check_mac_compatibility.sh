#!/bin/bash
# Script de vérification de compatibilité Mac pour Jira CLI
# Usage: ./check_mac_compatibility.sh

echo "🍎 Vérification de compatibilité Mac - Jira CLI"
echo "==============================================="
echo ""

ISSUES=0

# Check Python 3
echo "1. Vérification de Python 3..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 7 ]; then
        echo "   ✅ Python $PYTHON_VERSION (OK)"
    else
        echo "   ⚠️  Python $PYTHON_VERSION trouvé, mais 3.7+ recommandé"
        ((ISSUES++))
    fi
else
    echo "   ❌ Python 3 non trouvé"
    echo "   → Installez avec: brew install python3"
    ((ISSUES++))
fi

echo ""

# Check pip3
echo "2. Vérification de pip3..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version 2>&1 | awk '{print $2}')
    echo "   ✅ pip3 $PIP_VERSION (OK)"
else
    echo "   ❌ pip3 non trouvé"
    echo "   → Installez Python 3 avec: brew install python3"
    ((ISSUES++))
fi

echo ""

# Check dependencies
echo "3. Vérification des dépendances Python..."
if command -v pip3 &> /dev/null; then
    if pip3 show requests &> /dev/null; then
        REQUESTS_VERSION=$(pip3 show requests | grep Version | awk '{print $2}')
        echo "   ✅ requests $REQUESTS_VERSION (OK)"
    else
        echo "   ⚠️  Module 'requests' non installé"
        echo "   → Installez avec: pip3 install -r requirements.txt"
        ((ISSUES++))
    fi
else
    echo "   ⏭️  Pip3 non disponible, test ignoré"
fi

echo ""

# Check file structure
echo "4. Vérification de la structure des fichiers..."
FILES_TO_CHECK=(
    "jira_cli.py"
    "jira_cli/lib/jira_client.py"
    "jira_cli/scripts/user_manager.py"
    "jira_cli/scripts/issue_manager.py"
    "jira_cli/scripts/sprint_manager.py"
    "jira_cli/scripts/bulk_operations.py"
    "jira_cli/scripts/board_manager.py"
    "jira_cli/scripts/dashboard_manager.py"
    "requirements.txt"
)

ALL_FILES_OK=true
for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (manquant)"
        ALL_FILES_OK=false
        ((ISSUES++))
    fi
done

echo ""

# Check shebangs
echo "5. Vérification des shebangs (compatibilité Mac)..."
SHEBANG_OK=true
for script in jira_cli/scripts/*.py; do
    if [ -f "$script" ] && [ "$script" != "jira_cli/scripts/__init__.py" ]; then
        SHEBANG=$(head -1 "$script")
        if [[ "$SHEBANG" == "#!/usr/bin/env python3" ]] || [[ "$SHEBANG" == *"python3"* ]]; then
            echo "   ✅ $(basename $script)"
        else
            echo "   ❌ $(basename $script) - shebang incorrect: $SHEBANG"
            SHEBANG_OK=false
            ((ISSUES++))
        fi
    fi
done

echo ""

# Check permissions
echo "6. Vérification des permissions d'exécution..."
PERMS_OK=true
for script in jira_cli/scripts/*.py jira_cli.py; do
    if [ -f "$script" ] && [ "$script" != "jira_cli/scripts/__init__.py" ]; then
        if [ -x "$script" ]; then
            echo "   ✅ $(basename $script) (exécutable)"
        else
            echo "   ⚠️  $(basename $script) (non exécutable)"
            echo "      → Corrigez avec: chmod +x $script"
            PERMS_OK=false
            ((ISSUES++))
        fi
    fi
done

echo ""

# Check configuration
echo "7. Vérification de la configuration..."
if [ -f "$HOME/.jira_config.json" ]; then
    echo "   ✅ ~/.jira_config.json existe"

    # Check permissions
    PERMS=$(stat -f "%OLp" "$HOME/.jira_config.json" 2>/dev/null || stat -c "%a" "$HOME/.jira_config.json" 2>/dev/null)
    if [ "$PERMS" = "600" ]; then
        echo "   ✅ Permissions correctes (600)"
    else
        echo "   ⚠️  Permissions: $PERMS (recommandé: 600)"
        echo "      → Corrigez avec: chmod 600 ~/.jira_config.json"
    fi

    # Check content
    if grep -q "jira_url" "$HOME/.jira_config.json" && \
       grep -q "email" "$HOME/.jira_config.json" && \
       grep -q "api_token" "$HOME/.jira_config.json"; then
        echo "   ✅ Configuration semble correcte"
    else
        echo "   ⚠️  Configuration incomplète"
        echo "      → Vérifiez les champs: jira_url, email, api_token"
    fi
else
    echo "   ℹ️  ~/.jira_config.json n'existe pas encore"
    echo "      → Créez-le en suivant INSTALLATION_MAC.md"
fi

echo ""

# Summary
echo "========================================"
echo "📊 RÉSUMÉ"
echo "========================================"

if [ $ISSUES -eq 0 ]; then
    echo ""
    echo "✅ Tout est prêt ! Aucun problème détecté."
    echo ""
    echo "🎉 Vous pouvez utiliser Jira CLI sur Mac !"
    echo ""
    echo "Prochaines étapes:"
    echo "  1. Si pas encore fait: pip3 install -r requirements.txt"
    echo "  2. Si pas encore fait: Configurez ~/.jira_config.json"
    echo "  3. Testez: python3 jira_cli.py --help"
    echo "  4. Testez la connexion: python3 jira_cli.py users list"
    echo ""
    exit 0
else
    echo ""
    echo "⚠️  $ISSUES problème(s) détecté(s)"
    echo ""
    echo "Consultez les messages ci-dessus pour les résoudre."
    echo "Voir aussi: INSTALLATION_MAC.md pour plus de détails"
    echo ""
    exit 1
fi
