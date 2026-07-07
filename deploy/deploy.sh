#!/bin/bash
# ==============================================
# PLUME ASTRALE - Script de deploiement VPS
# ==============================================
# Ce script installe tout ce qu'il faut sur votre
# VPS Hostinger et lance l'application.
# ==============================================

set -e

DOMAIN="plume-astrale.fr"
EMAIL="nadine.zebdi@gmail.com"
APP_DIR="/root/plume-astrale"
VPS_IP="187.124.9.214"

# ========================================
# FONCTION: Verifier les variables requises
# ========================================
check_required_env_vars() {
    echo ""
    echo "[*] Verification des variables d'environnement..."
    
    REQUIRED_VARS=(
        "OPENAI_API_KEY"
        "ASTROLOGY_API_IO_KEY"
        "STRIPE_API_KEY"
        "JWT_SECRET"
    )
    
    MISSING_VARS=()
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            MISSING_VARS+=("$var")
        fi
    done
    
    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        echo ""
        echo "❌ ERREUR: Variables d'environnement manquantes:"
        for var in "${MISSING_VARS[@]}"; do
            echo "   - $var"
        done
        echo ""
        echo "📖 Pour configurer, consultez: /app/ENV_SETUP.md"
        echo ""
        echo "Sur VPS local: Assurez-vous que le fichier .env contient toutes les variables."
        echo "Sur Emergent: Allez a https://app.emergent.sh -> Deployed Apps -> Settings"
        echo ""
        return 1
    fi
    
    echo "✅ Toutes les variables requises sont configurees"
    echo ""
}

# Charger les variables du fichier .env s'il existe
if [ -f "$APP_DIR/.env" ]; then
    export $(cat "$APP_DIR/.env" | grep -v '^#' | xargs)
fi

echo "=========================================="
echo "  PLUME ASTRALE - Deploiement"
echo "=========================================="

# 1. Mise a jour du systeme
echo "[1/6] Mise a jour du systeme..."
apt-get update && apt-get upgrade -y

# 2. Installer Docker
echo "[2/6] Installation de Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "Docker installe avec succes"
else
    echo "Docker deja installe"
fi

# 3. Installer Docker Compose
echo "[3/6] Verification de Docker Compose..."
if ! docker compose version &> /dev/null; then
    apt-get install -y docker-compose-plugin
    echo "Docker Compose installe"
else
    echo "Docker Compose deja installe"
fi

# 4. Cloner ou mettre a jour le projet
echo "[4/6] Preparation du projet..."
if [ -d "$APP_DIR" ]; then
    echo "Le dossier existe deja. Mise a jour..."
    cd "$APP_DIR"
else
    echo "Creation du dossier..."
    mkdir -p "$APP_DIR"
    cd "$APP_DIR"
    echo "Copiez les fichiers du projet ici."
fi

# 5. Lancer les conteneurs
echo "[5/6] Lancement de l'application..."

# Verifier les variables d'environnement avant deployment
check_required_env_vars || exit 1

if [ -f "docker-compose.yml" ]; then
    # Copy production env
    if [ -f ".env.production" ] && [ ! -f ".env" ]; then
        cp .env.production .env
        echo "Fichier .env cree depuis .env.production"
    fi
    
    docker compose down 2>/dev/null || true
    docker compose build --no-cache
    docker compose up -d
    echo "Application lancee !"
else
    echo "ERREUR: docker-compose.yml non trouve dans $APP_DIR"
    echo "Veuillez d'abord copier les fichiers du projet."
    exit 1
fi

# 6. Configurer SSL avec Let's Encrypt
echo "[6/6] Configuration SSL..."
echo "Attente de 10 secondes pour que Nginx demarre..."
sleep 10

docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/lib/letsencrypt \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" || echo "SSL sera configure plus tard (le domaine doit pointer vers ce serveur d'abord)"

echo ""
echo "=========================================="
echo "  DEPLOIEMENT TERMINE !"
echo "=========================================="
echo ""
echo "Votre application est accessible sur :"
echo "  http://$DOMAIN"
echo ""
echo "Pour activer HTTPS, assurez-vous que :"
echo "  1. Le domaine $DOMAIN pointe vers l'IP de ce VPS"
echo "  2. Relancez: docker compose run --rm certbot certonly --webroot --webroot-path=/var/lib/letsencrypt --email $EMAIL --agree-tos -d $DOMAIN -d www.$DOMAIN"
echo "  3. Puis: docker compose restart nginx"
echo ""
