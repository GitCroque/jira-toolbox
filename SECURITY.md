# Guide de Sécurité - Jira CLI 🔒

## ⚠️ IMPORTANT: Protection des Données Sensibles

Ce guide explique comment **protéger vos credentials Jira** et éviter de les pousser accidentellement sur Git.

## 🎯 Résumé Rapide

### ✅ À FAIRE
- ✅ Utiliser `~/.jira_config.json` (hors du repo)
- ✅ Définir permissions `chmod 600` sur vos fichiers de config
- ✅ Vérifier avec `git status` avant chaque commit
- ✅ Installer le hook de sécurité: `./install_security_hook.sh`
- ✅ Lancer `./check_security.sh` avant de push

### ❌ À NE JAMAIS FAIRE
- ❌ Committer des fichiers `*config.json` (sauf `*example*.json`)
- ❌ Mettre votre token API dans le repo
- ❌ Partager votre fichier de configuration
- ❌ Committer `credentials.json`
- ❌ Bypass le hook de sécurité sans raison valable

## 🛡️ Mesures de Protection en Place

### 1. Fichier `.gitignore`

Le `.gitignore` est configuré pour bloquer automatiquement:

```gitignore
# Fichiers de configuration contenant des credentials
*config.json          # Tous les fichiers de config
*_config.json         # Variantes avec underscore
.jira_config.json     # Config Jira caché
jira_config.json      # Config Jira normale
credentials.json      # Fichiers de credentials

# Exception: fichiers d'exemple (sans vraies credentials)
!config.example.json  # Fichier d'exemple OK
!*example*.json       # Tous les exemples OK
```

### 2. Script de Vérification de Sécurité

**Utilisation:**
```bash
./check_security.sh
```

**Ce script vérifie:**
- ✅ Fichiers de config trackés par Git
- ✅ Fichiers staged contenant des credentials
- ✅ Tokens API dans les fichiers
- ✅ Règles .gitignore correctes
- ✅ Permissions des fichiers sensibles
- ✅ Historique Git récent

**Quand l'utiliser:**
- Avant chaque `git push`
- Après avoir configuré vos credentials
- Régulièrement pour un audit de sécurité

### 3. Hook Pre-Commit Automatique

**Installation:**
```bash
./install_security_hook.sh
```

**Protection automatique:**
Le hook s'exécute **automatiquement avant chaque commit** et:
- 🚫 Bloque les commits contenant des fichiers sensibles
- 🚫 Détecte les tokens API dans le code
- ⚠️  Alerte sur les patterns suspects
- ✅ Permet le commit si tout est sécurisé

**Test du hook:**
```bash
# Le hook est automatiquement testé lors de l'installation
# Ou testez manuellement en tentant de committer un fichier sensible
```

## 📋 Configuration Sécurisée

### Méthode 1: Fichier de Configuration Global (Recommandé)

Créez `~/.jira_config.json` **en dehors du repo**:

```bash
cat > ~/.jira_config.json << 'EOF'
{
  "jira_url": "https://votre-instance.atlassian.net",
  "email": "votre.email@exemple.com",
  "api_token": "VOTRE_TOKEN_ICI"
}
EOF

# Sécurisez les permissions (lisible uniquement par vous)
chmod 600 ~/.jira_config.json
```

✅ **Avantages:**
- En dehors du repo Git
- Une seule config pour tous vos projets
- Impossible à committer accidentellement

### Méthode 2: Variables d'Environnement

```bash
# Ajoutez dans ~/.zshrc ou ~/.bash_profile
export JIRA_URL="https://votre-instance.atlassian.net"
export JIRA_EMAIL="votre.email@exemple.com"
export JIRA_API_TOKEN="votre_token_api"

# Rechargez
source ~/.zshrc
```

✅ **Avantages:**
- Pas de fichier à gérer
- Encore plus sécurisé
- Facile à changer

### ❌ Méthode à ÉVITER: Config dans le Repo

**N'UTILISEZ PAS** de fichier de config dans le repo (même dans `jira_cli/config/`):

```bash
# ❌ INCORRECT - Dans le repo
jira_cli/config/config.json

# ✅ CORRECT - Hors du repo
~/.jira_config.json
```

## 🚨 Que Faire en Cas de Fuite

### Si vous avez commité des credentials par erreur:

#### 1. **Si le commit n'est PAS encore pushé:**

```bash
# Annuler le dernier commit (garde les modifications)
git reset HEAD~1

# Supprimer le fichier sensible du staging
git reset HEAD fichier_sensible.json

# Ajouter au .gitignore si nécessaire
echo "fichier_sensible.json" >> .gitignore

# Recommiter sans le fichier sensible
git add .
git commit -m "Votre message"
```

#### 2. **Si le commit est déjà pushé:**

**⚠️ URGENT - Actions immédiates:**

1. **Révoquez immédiatement votre token API:**
   - Allez sur https://id.atlassian.com/manage-profile/security/api-tokens
   - Révoquuez le token compromis
   - Créez un nouveau token

2. **Supprimez le fichier du repo:**
   ```bash
   # Supprimer du tracking Git
   git rm --cached fichier_sensible.json
   git commit -m "Remove sensitive file"
   git push
   ```

3. **Nettoyez l'historique (optionnel mais recommandé):**
   ```bash
   # ATTENTION: Réécrit l'historique Git
   git filter-branch --index-filter \
     'git rm --cached --ignore-unmatch fichier_sensible.json' HEAD

   # Force push (coordonnez avec votre équipe)
   git push origin --force --all
   ```

4. **Informez votre équipe:**
   - Prévenez que l'historique a été réécrit
   - Demandez à chacun de re-clone le repo
   - Expliquez les mesures prises

#### 3. **Si le repo est public:**

🚨 **ALERTE MAXIMALE:**
- Révoquez IMMÉDIATEMENT tous vos tokens
- Changez tous vos mots de passe Jira/Atlassian
- Auditez votre compte pour détecter des accès suspects
- Contactez le support Atlassian
- Envisagez de supprimer et recréer le repo

## 🔍 Vérifications Régulières

### Check-list Quotidienne

Avant chaque `git push`:

```bash
# 1. Vérifier le status
git status

# 2. Vérifier les fichiers staged
git diff --cached --name-only

# 3. Lancer la vérification de sécurité
./check_security.sh

# 4. Si tout est OK, push
git push
```

### Audit de Sécurité Mensuel

```bash
# Vérifier qu'aucun fichier sensible n'est tracké
git ls-files | grep -E '(config|credentials)\.json' | grep -v example

# Vérifier l'historique récent
git log --oneline -20

# Vérifier .gitignore est à jour
cat .gitignore

# Lancer le check complet
./check_security.sh
```

## 📚 Ressources et Outils

### Scripts de Sécurité Disponibles

| Script | Usage | Description |
|--------|-------|-------------|
| `check_security.sh` | `./check_security.sh` | Vérification complète de sécurité |
| `install_security_hook.sh` | `./install_security_hook.sh` | Installation du hook pre-commit |
| `git-hooks/pre-commit` | Automatique | Hook Git de protection |

### Commandes Utiles

```bash
# Vérifier quels fichiers sont trackés
git ls-files

# Voir les fichiers ignorés
git status --ignored

# Vérifier un fichier spécifique
git check-ignore -v fichier.json

# Lister tous les fichiers JSON trackés
git ls-files | grep '\.json$'

# Chercher des tokens dans l'historique (dangereux !)
git log -p -S "api_token" --all
```

## 🎓 Bonnes Pratiques

### Pour les Développeurs

1. **Toujours utiliser ~/.jira_config.json**
   - Ne créez JAMAIS de config dans le repo

2. **Vérifier avant de committer**
   ```bash
   git status
   ./check_security.sh
   ```

3. **Installer le hook pre-commit**
   ```bash
   ./install_security_hook.sh
   ```

4. **Permissions strictes**
   ```bash
   chmod 600 ~/.jira_config.json
   ```

5. **Renouveler les tokens régulièrement**
   - Tous les 3-6 mois minimum
   - Immédiatement en cas de doute

### Pour les Équipes

1. **Formation de l'équipe**
   - Expliquez les risques
   - Montrez comment configurer correctement

2. **Code review**
   - Vérifiez qu'aucune PR ne contient de credentials
   - Utilisez GitHub/GitLab security scanning

3. **CI/CD**
   - Intégrez `check_security.sh` dans votre pipeline
   - Bloquez les déploiements en cas de problème

4. **Rotation des tokens**
   - Politique de rotation tous les 6 mois
   - Tokens d'équipe vs tokens personnels

## 🆘 Support

### Questions Fréquentes

**Q: J'ai oublié d'installer le hook et j'ai commité un fichier sensible. Que faire?**
R: Suivez la section "Que Faire en Cas de Fuite" ci-dessus.

**Q: Le hook bloque mon commit légitime. Comment faire?**
R: Vérifiez que votre fichier n'est pas un `*config.json`. Si c'est un faux positif, utilisez `git commit --no-verify` (avec précaution).

**Q: Puis-je désactiver le hook?**
R: Oui, avec `rm .git/hooks/pre-commit`, mais ce n'est pas recommandé.

**Q: Comment vérifier que ma config n'est pas dans Git?**
R: `git ls-files | grep config.json` ne doit rien retourner (sauf exemple).

### Contact

Pour des questions de sécurité:
- Consultez d'abord ce guide
- Vérifiez les issues GitHub
- Contactez l'équipe de sécurité de votre organisation

---

## 📋 Check-list de Configuration Sécurisée

Cochez au fur et à mesure:

- [ ] J'ai lu et compris ce guide de sécurité
- [ ] J'ai créé `~/.jira_config.json` (hors du repo)
- [ ] J'ai défini les permissions 600 sur ma config
- [ ] J'ai installé le hook pre-commit
- [ ] J'ai testé le hook
- [ ] J'ai vérifié que .gitignore est correct
- [ ] J'ai lancé `./check_security.sh` avec succès
- [ ] Je sais comment révoquer un token API
- [ ] Je vérifie `git status` avant chaque commit
- [ ] J'ai partagé ce guide avec mon équipe

---

**🔒 La sécurité est la responsabilité de tous. Restons vigilants !**
