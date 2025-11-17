# Installation et Utilisation sur Mac 🍎

## Vérification Préalable

Tous les scripts ont été testés et sont **100% compatibles Mac** ✅

### Test Rapide

```bash
# Depuis le répertoire jira-toolbox
./test_all_scripts.sh
```

Vous devriez voir: `✅ Tous les tests sont passés !`

## 📋 Prérequis Mac

### 1. Python 3

Vérifiez votre version de Python:

```bash
python3 --version
```

Si vous n'avez pas Python 3, installez-le avec Homebrew:

```bash
# Installer Homebrew si nécessaire
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installer Python 3
brew install python3
```

### 2. pip3

Normalement installé avec Python 3. Vérifiez:

```bash
pip3 --version
```

## 🚀 Installation

### Étape 1: Clone ou téléchargez le projet

```bash
cd ~/Documents  # ou n'importe quel répertoire
git clone <url-du-repo> jira-toolbox
cd jira-toolbox
```

### Étape 2: Installez les dépendances

```bash
pip3 install -r requirements.txt
```

Si vous rencontrez des problèmes de permissions:

```bash
pip3 install --user -r requirements.txt
```

### Étape 3: Créez votre token API Jira

1. Allez sur https://id.atlassian.com/manage-profile/security/api-tokens
2. Cliquez sur "Create API token"
3. Nommez-le (ex: "Jira CLI Mac") et copiez le token généré

### Étape 4: Configuration

Créez le fichier de configuration:

```bash
cat > ~/.jira_config.json << 'EOF'
{
  "jira_url": "https://votre-instance.atlassian.net",
  "email": "votre.email@exemple.com",
  "api_token": "VOTRE_TOKEN_ICI"
}
EOF

# Sécurisez le fichier
chmod 600 ~/.jira_config.json
```

**Remplacez:**
- `votre-instance` par le nom de votre instance Jira Cloud
- `votre.email@exemple.com` par votre email Atlassian
- `VOTRE_TOKEN_ICI` par le token que vous avez copié

## ✅ Test de la Configuration

```bash
# Test simple - doit afficher l'aide
python3 jira_cli.py --help

# Test avec connexion Jira (liste les utilisateurs)
python3 jira_cli.py users list
```

Si la dernière commande affiche des utilisateurs, tout fonctionne ! 🎉

## 🎯 Utilisation sur Mac

### Méthode 1: Avec python3 (recommandé)

```bash
python3 jira_cli.py <commande> <sous-commande> [options]
```

**Exemples:**
```bash
python3 jira_cli.py issues list
python3 jira_cli.py sprints boards
python3 jira_cli.py users list
```

### Méthode 2: Exécution directe

Les scripts ont le shebang `#!/usr/bin/env python3` et sont exécutables:

```bash
./jira_cli.py issues list
./jira_cli/scripts/issue_manager.py --help
```

### Méthode 3: Créer un alias (plus pratique)

Ajoutez dans votre `~/.zshrc` (ou `~/.bash_profile` si vous utilisez bash):

```bash
alias jira='python3 ~/Documents/jira-toolbox/jira_cli.py'
```

Puis rechargez:

```bash
source ~/.zshrc  # ou source ~/.bash_profile
```

Maintenant vous pouvez utiliser:

```bash
jira issues list
jira sprints boards
jira bulk export-csv "project = MYPROJ" export.csv
```

## 🔧 Résolution de Problèmes Mac

### Erreur: "command not found: python3"

```bash
# Installez Python 3 avec Homebrew
brew install python3
```

### Erreur: SSL Certificate

```bash
# Installez les certificats
/Applications/Python\ 3.x/Install\ Certificates.command
```

### Erreur: "Permission denied"

```bash
# Rendez les scripts exécutables
chmod +x jira_cli.py
chmod +x jira_cli/scripts/*.py
```

### Erreur: "No module named 'requests'"

```bash
# Réinstallez les dépendances
pip3 install --user -r requirements.txt
```

### Erreur: "zsh: bad interpreter"

Sur Mac, assurez-vous d'utiliser python3 et non python:

```bash
# ✅ Correct
python3 jira_cli.py --help

# ❌ Incorrect (pourrait utiliser Python 2)
python jira_cli.py --help
```

## 📱 Configuration Avancée sur Mac

### Utiliser un environnement virtuel (recommandé)

```bash
# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Utiliser normalement
python jira_cli.py --help

# Désactiver quand terminé
deactivate
```

### Ajouter au PATH

```bash
# Ajoutez dans ~/.zshrc
export PATH="$HOME/Documents/jira-toolbox:$PATH"

# Rechargez
source ~/.zshrc

# Maintenant vous pouvez utiliser
jira_cli.py issues list
```

## 🎓 Premiers Pas sur Mac

### 1. Lister vos projets

```bash
python3 jira_cli.py projects list
```

### 2. Créer une issue de test

```bash
python3 jira_cli.py issues create MYPROJ "Test depuis Mac" --type Task
```

### 3. Exporter des données

```bash
python3 jira_cli.py bulk export-csv "project = MYPROJ" ~/Desktop/export.csv
```

### 4. Voir les sprints

```bash
# Lister les boards
python3 jira_cli.py sprints boards

# Voir les sprints d'un board (remplacez 123 par l'ID du board)
python3 jira_cli.py sprints list 123
```

### 5. Audit rapide

```bash
python3 jira_cli.py audit projects --output ~/Desktop/audit_projects.json
```

## 🔐 Sécurité sur Mac

### Protégez votre configuration

```bash
# Le fichier de config ne doit être lisible que par vous
chmod 600 ~/.jira_config.json

# Vérifiez les permissions
ls -l ~/.jira_config.json
# Doit afficher: -rw------- (600)
```

### N'incluez JAMAIS votre token dans Git

Le `.gitignore` est déjà configuré, mais soyez vigilant:

```bash
# Vérifiez que votre config n'est pas trackée
git status
# Ne doit PAS montrer .jira_config.json
```

## 📚 Ressources

- **Documentation complète:** Voir `README.md`
- **Guide rapide:** Voir `QUICKSTART.md`
- **Tests:** Exécutez `./test_all_scripts.sh`

## 🆘 Support

Si vous rencontrez des problèmes sur Mac:

1. Vérifiez votre version de Python: `python3 --version` (doit être 3.7+)
2. Vérifiez les dépendances: `pip3 list | grep requests`
3. Testez la configuration: `python3 jira_cli.py users list`
4. Consultez les logs d'erreur pour plus de détails

## ✨ Astuces Mac

### Terminal

- Utilisez **iTerm2** pour une meilleure expérience terminal
- Activez la complétion automatique dans zsh
- Utilisez **Command+K** pour effacer le terminal

### Scripts

- Créez des scripts personnalisés dans `jira_cli/examples/`
- Utilisez Automator pour créer des raccourcis
- Intégrez avec Alfred ou Raycast pour lancer rapidement

---

**La suite Jira CLI est maintenant prête sur votre Mac ! 🎉**

Bon travail avec Jira ! 🚀
