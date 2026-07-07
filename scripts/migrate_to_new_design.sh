#!/bin/bash

# ===================================================================
# Script de Migration vers le Nouveau Design Plume Astrale
# ===================================================================

set -e

echo "🚀 Début de la migration vers le nouveau design..."

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "frontend" ]; then
    echo -e "${RED}Erreur : Exécutez ce script depuis la racine du projet (plume-astrale)${NC}"
    exit 1
fi

# Créer une sauvegarde
echo -e "${BLUE}✓ Création d'une sauvegarde...${NC}"
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Sauvegarder les fichiers existants
cp -r frontend/src/pages/Index.js "$BACKUP_DIR/" 2>/dev/null || echo "Index.js non trouvé"
cp -r frontend/src/components/Moon3D.js "$BACKUP_DIR/" 2>/dev/null || echo "Moon3D.js non trouvé"
cp -r frontend/src/index.css "$BACKUP_DIR/" 2>/dev/null || echo "index.css non trouvé"
cp -r frontend/src/App.js "$BACKUP_DIR/" 2>/dev/null || echo "App.js non trouvé"

echo -e "${GREEN}✓ Sauvegarde créée dans : $BACKUP_DIR${NC}"

# Copier les nouveaux fichiers
echo -e "${BLUE}✓ Copie des nouveaux fichiers...${NC}"

# Copier NewHome.js vers Index.js
if [ -f "frontend/src/pages/NewHome.js" ]; then
    cp "frontend/src/pages/NewHome.js" "frontend/src/pages/Index.js"
    echo -e "${GREEN}✓ NewHome.js → Index.js${NC}"
else
    echo -e "${RED}Erreur : NewHome.js non trouvé${NC}"
    exit 1
fi

# Copier EnhancedMoon3D.js vers Moon3D.js
if [ -f "frontend/src/components/EnhancedMoon3D.js" ]; then
    cp "frontend/src/components/EnhancedMoon3D.js" "frontend/src/components/Moon3D.js"
    echo -e "${GREEN}✓ EnhancedMoon3D.js → Moon3D.js${NC}"
else
    echo -e "${RED}Erreur : EnhancedMoon3D.js non trouvé${NC}"
    exit 1
fi

# Copier index_new.css vers index.css
if [ -f "frontend/src/index_new.css" ]; then
    cp "frontend/src/index_new.css" "frontend/src/index.css"
    echo -e "${GREEN}✓ index_new.css → index.css${NC}"
else
    echo -e "${RED}Erreur : index_new.css non trouvé${NC}"
    exit 1
fi

# Copier App_new.js vers App.js
if [ -f "frontend/src/App_new.js" ]; then
    cp "frontend/src/App_new.js" "frontend/src/App.js"
    echo -e "${GREEN}✓ App_new.js → App.js${NC}"
else
    echo -e "${RED}Erreur : App_new.js non trouvé${NC}"
    exit 1
fi

# Créer le dossier config s'il n'existe pas
mkdir -p "frontend/src/config"

# Copier la configuration
if [ -f "frontend/src/config/newDesignConfig.js" ]; then
    cp "frontend/src/config/newDesignConfig.js" "frontend/src/config/"
    echo -e "${GREEN}✓ newDesignConfig.js copié${NC}"
else
    echo -e "${YELLOW}⚠ newDesignConfig.js non trouvé, création...${NC}"
fi

# Vérifier que la texture de la lune existe
if [ ! -f "frontend/public/assets/moon_1024.jpg" ]; then
    echo -e "${YELLOW}⚠ Texture moon_1024.jpg non trouvée dans public/assets/${NC}"
    echo -e "${YELLOW}  Le composant 3D utilisera une texture procédurale à la place${NC}"
fi

# Nettoyer les fichiers temporaires
echo -e "${BLUE}✓ Nettoyage des fichiers temporaires...${NC}"
rm -f frontend/src/pages/NewHome.js
rm -f frontend/src/components/EnhancedMoon3D.js
rm -f frontend/src/index_new.css
rm -f frontend/src/App_new.js

echo -e "${GREEN}✓ Nettoyage terminé${NC}"

# Vérifier les dépendances
echo -e "${BLUE}✓ Vérification des dépendances...${NC}"

cd frontend

# Vérifier que three.js est installé
if grep -q "three" package.json; then
    echo -e "${GREEN}✓ Three.js est installé${NC}"
else
    echo -e "${YELLOW}⚠ Three.js n'est pas dans package.json${NC}"
    echo -e "  Exécutant : npm install three@latest"
    npm install three@latest --save
fi

# Vérifier lucide-react
if grep -q "lucide-react" package.json; then
    echo -e "${GREEN}✓ Lucide-react est installé${NC}"
else
    echo -e "${YELLOW}⚠ Lucide-react n'est pas dans package.json${NC}"
    echo -e "  Exécutant : npm install lucide-react@latest"
    npm install lucide-react@latest --save
fi

cd ..

# Résumé
echo ""
echo -e "${GREEN}=================================================================${NC}"
echo -e "${GREEN}✨ Migration terminée avec succès ! ✨${NC}"
echo -e "${GREEN}=================================================================${NC}"
echo ""
echo -e "Fichiers modifiés :"
echo -e "  • frontend/src/pages/Index.js"
echo -e "  • frontend/src/components/Moon3D.js"
echo -e "  • frontend/src/index.css"
echo -e "  • frontend/src/App.js"
echo ""
echo -e "Sauvegarde : $BACKUP_DIR"
echo ""
echo -e "Prochaines étapes :"
echo -e "  1. Testez le site : ${BLUE}npm start${NC}"
echo -e "  2. Vérifiez que tout fonctionne correctement"
echo -e "  3. Si problème, restaurez depuis : ${BLUE}$BACKUP_DIR${NC}"
echo ""
echo -e "Documentation : NEW_DESIGN_GUIDE.md"
echo ""

# Demander confirmation pour supprimer la sauvegarde
read -p "Voulez-vous supprimer la sauvegarde ? (y/N) : " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    rm -rf "$BACKUP_DIR"
    echo -e "${GREEN}✓ Sauvegarde supprimée${NC}"
else
    echo ""
    echo -e "${GREEN}✓ Sauvegarde conservée dans : $BACKUP_DIR${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Migration complète !${NC}"
