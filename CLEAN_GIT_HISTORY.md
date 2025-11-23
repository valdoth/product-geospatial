# 🧹 Nettoyer l'Historique Git

## ⚠️ Problème

GitHub a détecté ta clé API OpenAI dans l'historique Git et bloque le push.

## ✅ Solution : Nettoyer l'historique Git

### Option 1 : Recommencer avec un historique propre (Recommandé)

```bash
cd /Users/valdo/Desktop/fluentech/produit-geospatial

# 1. Sauvegarder ton travail
cp -r . ../produit-geospatial-backup

# 2. Supprimer le dossier .git
rm -rf .git

# 3. Réinitialiser Git
git init

# 4. Ajouter tous les fichiers (le .gitignore protégera .env)
git add .

# 5. Créer le commit initial avec la bonne date
GIT_COMMITTER_DATE="2025-11-23T10:00:00" git commit -m "feat: initial commit - assistant d'aide à la décision" --date "2025-11-23T10:00:00"

# 6. Ajouter le remote
git remote add origin https://github.com/valdoth/product-geospatial.git

# 7. Push (force car nouveau historique)
git push -u origin main --force
```

### Option 2 : Utiliser git filter-branch (Plus complexe)

```bash
# Retirer .env de tout l'historique
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env .env.docker LLM/.env" \
  --prune-empty --tag-name-filter cat -- --all

# Push force
git push -u origin dev --force
```

---

## 🔒 Important : Révoquer ta clé API

⚠️ **Ta clé API a été exposée sur GitHub !**

### Étapes obligatoires :

1. **Va sur** : https://platform.openai.com/api-keys
2. **Révoque** ta clé actuelle : `sk-proj-2Ye8iPgmI3pfngrC5LVo...`
3. **Crée** une nouvelle clé API
4. **Mets à jour** ton fichier `.env` local avec la nouvelle clé

---

## ✅ Après le nettoyage

```bash
# Vérifier que .env n'est plus dans Git
git log --all --full-history -- .env

# Doit afficher: rien (historique vide pour .env)
```

---

## 📝 Résumé

1. ✅ Nettoyer l'historique Git (Option 1 recommandée)
2. ✅ Révoquer l'ancienne clé API OpenAI
3. ✅ Créer une nouvelle clé API
4. ✅ Mettre à jour `.env` localement
5. ✅ Push vers GitHub
