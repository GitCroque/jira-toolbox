#!/bin/bash
# Script de test pour vérifier que tous les modules Jira CLI fonctionnent
# Usage: ./test_all_scripts.sh

echo "🧪 Test de tous les scripts Jira CLI"
echo "===================================="
echo ""

FAIL_COUNT=0
PASS_COUNT=0

# Fonction de test
test_script() {
    local script=$1
    local name=$2

    echo -n "Testing $name... "

    if python3 "$script" --help > /dev/null 2>&1; then
        echo "✅ OK"
        ((PASS_COUNT++))
    else
        echo "❌ FAILED"
        ((FAIL_COUNT++))
    fi
}

echo "1. Test des scripts individuels:"
echo "--------------------------------"
test_script "jira_cli/scripts/user_manager.py" "user_manager"
test_script "jira_cli/scripts/audit_tool.py" "audit_tool"
test_script "jira_cli/scripts/project_manager.py" "project_manager"
test_script "jira_cli/scripts/reporting.py" "reporting"
test_script "jira_cli/scripts/issue_manager.py" "issue_manager"
test_script "jira_cli/scripts/sprint_manager.py" "sprint_manager"
test_script "jira_cli/scripts/bulk_operations.py" "bulk_operations"
test_script "jira_cli/scripts/board_manager.py" "board_manager"
test_script "jira_cli/scripts/dashboard_manager.py" "dashboard_manager"

echo ""
echo "2. Test du point d'entrée principal:"
echo "------------------------------------"
test_script "jira_cli.py" "jira_cli (main)"

echo ""
echo "3. Test du routing vers les sous-commandes:"
echo "-------------------------------------------"

echo -n "Testing routing to 'issues'... "
if python3 jira_cli.py issues --help > /dev/null 2>&1; then
    echo "✅ OK"
    ((PASS_COUNT++))
else
    echo "❌ FAILED"
    ((FAIL_COUNT++))
fi

echo -n "Testing routing to 'sprints'... "
if python3 jira_cli.py sprints --help > /dev/null 2>&1; then
    echo "✅ OK"
    ((PASS_COUNT++))
else
    echo "❌ FAILED"
    ((FAIL_COUNT++))
fi

echo -n "Testing routing to 'bulk'... "
if python3 jira_cli.py bulk --help > /dev/null 2>&1; then
    echo "✅ OK"
    ((PASS_COUNT++))
else
    echo "❌ FAILED"
    ((FAIL_COUNT++))
fi

echo -n "Testing routing to 'boards'... "
if python3 jira_cli.py boards --help > /dev/null 2>&1; then
    echo "✅ OK"
    ((PASS_COUNT++))
else
    echo "❌ FAILED"
    ((FAIL_COUNT++))
fi

echo -n "Testing routing to 'dashboards'... "
if python3 jira_cli.py dashboards --help > /dev/null 2>&1; then
    echo "✅ OK"
    ((PASS_COUNT++))
else
    echo "❌ FAILED"
    ((FAIL_COUNT++))
fi

echo ""
echo "4. Test de la syntaxe Python:"
echo "-----------------------------"
echo -n "Compilation Python... "
if python3 -m py_compile jira_cli/scripts/*.py 2>/dev/null; then
    echo "✅ OK"
    ((PASS_COUNT++))
else
    echo "❌ FAILED"
    ((FAIL_COUNT++))
fi

echo ""
echo "5. Test des permissions d'exécution:"
echo "------------------------------------"
for script in jira_cli/scripts/*.py; do
    if [ -f "$script" ] && [ "$script" != "jira_cli/scripts/__init__.py" ]; then
        echo -n "$(basename $script)... "
        if [ -x "$script" ]; then
            echo "✅ Executable"
            ((PASS_COUNT++))
        else
            echo "❌ Not executable"
            ((FAIL_COUNT++))
        fi
    fi
done

echo ""
echo "6. Test du module jira_client:"
echo "------------------------------"
echo -n "Import jira_client... "
if python3 -c "import sys; sys.path.insert(0, 'jira_cli/lib'); from jira_client import JiraClient" 2>/dev/null; then
    echo "✅ OK"
    ((PASS_COUNT++))
else
    echo "❌ FAILED"
    ((FAIL_COUNT++))
fi

echo ""
echo "========================================"
echo "📊 RÉSULTATS"
echo "========================================"
echo "Tests réussis: $PASS_COUNT"
echo "Tests échoués: $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ Tous les tests sont passés !"
    echo ""
    echo "🎉 La suite Jira CLI est prête à être utilisée sur Mac !"
    echo ""
    echo "Pour commencer:"
    echo "  1. Installez les dépendances: pip3 install -r requirements.txt"
    echo "  2. Configurez vos credentials dans ~/.jira_config.json"
    echo "  3. Lancez: python3 jira_cli.py --help"
    exit 0
else
    echo "❌ Certains tests ont échoué"
    exit 1
fi
