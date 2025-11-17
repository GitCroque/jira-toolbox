#!/bin/bash
# Installation du hook de sécurité Git pre-commit
# Ce hook vérifie automatiquement qu'aucune donnée sensible n'est commitée

echo "🔒 Installation du Hook de Sécurité Git"
echo "======================================="
echo ""

# Vérifier qu'on est dans un repo Git
if [ ! -d ".git" ]; then
    echo "❌ Erreur: Ce script doit être exécuté à la racine du repo Git"
    exit 1
fi

# Vérifier que le hook source existe
if [ ! -f "git-hooks/pre-commit" ]; then
    echo "❌ Erreur: Fichier git-hooks/pre-commit non trouvé"
    exit 1
fi

# Créer le répertoire hooks si nécessaire
mkdir -p .git/hooks

# Sauvegarder le hook existant si présent
if [ -f ".git/hooks/pre-commit" ]; then
    echo "ℹ️  Un hook pre-commit existe déjà"
    BACKUP_FILE=".git/hooks/pre-commit.backup.$(date +%Y%m%d_%H%M%S)"
    cp .git/hooks/pre-commit "$BACKUP_FILE"
    echo "   Sauvegarde créée: $BACKUP_FILE"
    echo ""
fi

# Copier le hook
cp git-hooks/pre-commit .git/hooks/pre-commit

# Rendre exécutable
chmod +x .git/hooks/pre-commit

# Vérifier l'installation
if [ -x ".git/hooks/pre-commit" ]; then
    echo "✅ Hook pre-commit installé avec succès !"
    echo ""
    echo "📋 Ce hook va maintenant:"
    echo "   • Vérifier chaque commit avant qu'il soit créé"
    echo "   • Bloquer les fichiers *config.json (sauf *example*.json)"
    echo "   • Détecter les tokens API et credentials"
    echo "   • Vous alerter sur les fichiers sensibles"
    echo ""
    echo "🎯 Test du hook:"
    echo "   Le hook sera automatiquement exécuté au prochain 'git commit'"
    echo ""
    echo "💡 Pour bypasser le hook en cas d'urgence (DÉCONSEILLÉ):"
    echo "   git commit --no-verify"
    echo ""
    echo "🔧 Pour désinstaller:"
    echo "   rm .git/hooks/pre-commit"
    echo ""
else
    echo "❌ Erreur lors de l'installation du hook"
    exit 1
fi

# Test optionnel
echo "Voulez-vous tester le hook maintenant ? (o/n)"
read -r response

if [ "$response" = "o" ] || [ "$response" = "O" ]; then
    echo ""
    echo "🧪 Test du hook..."
    echo ""

    # Créer un fichier de test temporaire
    TEST_FILE="test_config.json"
    echo '{"api_token": "test123456789012345678"}' > "$TEST_FILE"
    git add "$TEST_FILE" 2>/dev/null

    echo "Tentative de commit d'un fichier avec token..."
    if git commit -m "Test security hook" 2>&1 | grep -q "BLOQUÉ"; then
        echo ""
        echo "✅ Le hook fonctionne correctement - commit bloqué comme prévu"
    else
        echo ""
        echo "⚠️  Le hook pourrait ne pas fonctionner comme prévu"
    fi

    # Nettoyer
    git reset HEAD "$TEST_FILE" 2>/dev/null
    rm -f "$TEST_FILE"
fi

echo ""
echo "✅ Installation terminée"
