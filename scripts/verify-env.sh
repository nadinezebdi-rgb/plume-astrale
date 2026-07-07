#!/bin/bash
# ============================================
# Script de Vérification des Variables d'Env
# ============================================
# Ce script aide à vérifier que toutes les variables
# d'environnement sont correctement configurées
# avant de déployer l'application.
#
# Usage: bash scripts/verify-env.sh
# ============================================

set -e

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Vérification des Variables d'Env${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Fonction pour tester une variable
test_var() {
    local var_name=$1
    local description=$2
    local required=$3
    
    if [ -z "${!var_name}" ]; then
        if [ "$required" = "true" ]; then
            echo -e "${RED}❌ MANQUANTE (REQUISE)${NC} - $var_name"
            echo "   Description: $description"
            return 1
        else
            echo -e "${YELLOW}⚠️  MANQUANTE (optionnelle)${NC} - $var_name"
            echo "   Description: $description"
            return 0
        fi
    else
        # Masquer les valeurs sensibles
        local value="${!var_name}"
        if [ ${#value} -gt 10 ]; then
            value="${value:0:6}...${value: -4}"
        fi
        echo -e "${GREEN}✅ CONFIGURÉE${NC} - $var_name = $value"
        return 0
    fi
}

# Charger .env si présent
if [ -f ".env" ]; then
    echo -e "${BLUE}[*] Chargement depuis .env...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
    echo ""
else
    echo -e "${YELLOW}[!] Fichier .env non trouvé${NC}"
    echo ""
fi

echo -e "${BLUE}Variables Requises (Production)${NC}"
echo "================================"
MISSING_COUNT=0

test_var "OPENAI_API_KEY" "Clé OpenAI pour GPT-4o-mini" "true" || ((MISSING_COUNT++))
test_var "ASTROLOGY_API_IO_KEY" "Clé API Astrology (api.astrology-api.io)" "true" || ((MISSING_COUNT++))
test_var "STRIPE_API_KEY" "Clé Stripe pour les paiements" "true" || ((MISSING_COUNT++))
test_var "JWT_SECRET" "Secret JWT pour l'authentification" "true" || ((MISSING_COUNT++))

echo ""
echo -e "${BLUE}Variables Optionnelles (Legacy)${NC}"
echo "================================="

test_var "EMERGENT_LLM_KEY" "Clé universelle Emergent" "false"

echo ""
echo -e "${BLUE}Configuration Locale${NC}"
echo "===================="

test_var "MONGO_URL" "URL de connexion MongoDB" "false"
test_var "DB_NAME" "Nom de la base de données" "false"

echo ""
echo -e "${BLUE}Configuration Frontend${NC}"
echo "======================="

test_var "REACT_APP_BACKEND_URL" "URL de l'API backend" "false"
test_var "REACT_APP_STRIPE_PUBLIC_KEY" "Clé publique Stripe" "false"

echo ""
echo -e "${BLUE}========================================${NC}"

if [ $MISSING_COUNT -gt 0 ]; then
    echo -e "${RED}❌ $MISSING_COUNT variable(s) requise(s) manquante(s)${NC}"
    echo ""
    echo "📖 Pour configurer les variables:"
    echo "   1. Copiez .env.example en .env"
    echo "   2. Remplissez les clés API"
    echo "   3. Consultez ENV_SETUP.md pour les instructions détaillées"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ Toutes les variables requises sont configurées!${NC}"
    echo ""
    echo "Vous pouvez maintenant:"
    echo "   • Lancer localement: docker-compose up"
    echo "   • Déployer sur production"
    echo ""
    exit 0
fi
