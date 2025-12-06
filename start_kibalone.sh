#!/bin/bash

echo "========================================"
echo "🚀 KIBALONE STUDIO - Démarrage"
echo "========================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour tuer les processus au Ctrl+C
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Arrêt de Kibalone Studio...${NC}"
    kill $PID_KIBALI $PID_NODE 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

cd /home/belikan/Isol/Meshy

# 1. Démarre l'API Kibali (légère, juste Flask)
echo -e "${BLUE}1️⃣  Démarrage de l'API Kibali...${NC}"
python3 kibali_api.py > /tmp/kibali_api.log 2>&1 &
PID_KIBALI=$!
echo -e "${GREEN}   ✅ API Kibali sur http://localhost:5000${NC}"
echo -e "${GREEN}   📝 Log: tail -f /tmp/kibali_api.log${NC}"

# Attend que l'API soit prête
echo -ne "${YELLOW}   ⏳ Initialisation..."
sleep 2
echo -e " OK${NC}"

# Test de l'API
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}   ✓ API Kibali répond correctement${NC}"
else
    echo -e "${RED}   ⚠ API Kibali ne répond pas encore (continuera en arrière-plan)${NC}"
fi

# 2. Démarre le serveur Kibalone Studio
echo ""
echo -e "${BLUE}2️⃣  Démarrage du serveur Kibalone Studio...${NC}"
node server.js > /tmp/kibalone_studio.log 2>&1 &
PID_NODE=$!
echo -e "${GREEN}   ✅ Serveur sur http://localhost:3000${NC}"
echo -e "${GREEN}   📝 Log: tail -f /tmp/kibalone_studio.log${NC}"

# Attend que le serveur soit prêt
sleep 1

echo ""
echo "========================================"
echo -e "${GREEN}✨ KIBALONE STUDIO EST PRÊT !${NC}"
echo "========================================"
echo ""
echo -e "${BLUE}🌐 Accès:${NC}"
echo -e "   ${GREEN}Kibalone Studio:${NC} http://localhost:3000/studio"
echo -e "   ${GREEN}Meshy Original:${NC}  http://localhost:3000"
echo -e "   ${GREEN}API Kibali:${NC}      http://localhost:5000/api/health"
echo ""
echo -e "${BLUE}💬 Exemples de prompts:${NC}"
echo "   • Crée un personnage héroïque avec une cape"
echo "   • Génère une forêt enchantée"
echo "   • Anime le personnage en marchant"
echo "   • Caméra orbite autour de la scène"
echo "   • Ajoute une lumière dramatique"
echo ""
echo -e "${YELLOW}📊 Services actifs:${NC}"
echo "   • API Kibali-IA (PID: $PID_KIBALI)"
echo "   • Node Server (PID: $PID_NODE)"
echo ""
echo -e "${YELLOW}👉 Appuyez sur Ctrl+C pour arrêter tous les services${NC}"
echo ""

# Garde le script actif
wait
