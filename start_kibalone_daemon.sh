#!/bin/bash
# Lance Kibalone Studio en mode DAEMON (arrière-plan permanent)

cd /home/belikan/Isol/Kibalone-Studio

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  🚀 KIBALONE STUDIO - Démarrage Daemon Mode  🚀  ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════╝${NC}"

# Tue les processus existants
echo -e "${YELLOW}🧹 Nettoyage...${NC}"
pkill -f kibali_api.py 2>/dev/null
pkill -f triposr_api.py 2>/dev/null
pkill -f midas_isol_api.py 2>/dev/null
pkill -f meshy_api.py 2>/dev/null
pkill -f "python.*http.server.*11080" 2>/dev/null
sleep 1

# Active conda
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    conda activate base
fi

# Crée les logs
mkdir -p /tmp/kibalone_logs

echo -e "${GREEN}🚀 Lancement des services...${NC}"

# Lance tous les services
nohup python3 -m http.server 11080 > /tmp/kibalone_logs/http_server.log 2>&1 &
echo -e "   [1/5] Serveur Web (PID: $!)"

nohup python3 kibali_api.py > /tmp/kibalone_logs/kibali_api.log 2>&1 &
KIBALI_PID=$!
echo -e "   [2/5] ${CYAN}Kibali API + CodeLlama${NC} (PID: $KIBALI_PID)"

nohup python3 triposr_api.py > /tmp/kibalone_logs/triposr_api.log 2>&1 &
echo -e "   [3/5] TripoSR API (PID: $!)"

nohup python3 midas_isol_api.py > /tmp/kibalone_logs/midas_isol_api.log 2>&1 &
echo -e "   [4/5] MiDaS API (PID: $!)"

nohup python3 meshy_api.py > /tmp/kibalone_logs/meshy_api.log 2>&1 &
echo -e "   [5/5] Meshy API (PID: $!)"

echo ""
echo -e "${YELLOW}⏳ Attente démarrage (15s)...${NC}"
sleep 15

echo ""
echo -e "${GREEN}✅ Services lancés en arrière-plan!${NC}"
echo ""
echo -e "${CYAN}🌐 Interface: ${NC}http://localhost:11080/kibalone-studio.html"
echo ""
echo -e "${YELLOW}📋 Commandes:${NC}"
echo -e "   ${GREEN}Logs:${NC}    tail -f /tmp/kibalone_logs/*.log"
echo -e "   ${RED}Arrêter:${NC} pkill -f 'python.*kibali'"
echo -e "   ${CYAN}Statut:${NC}  curl http://localhost:11000/api/health"
echo ""

# Vérifie que Kibali est bien lancé
sleep 5
if curl -s http://localhost:11000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Kibali API répond correctement${NC}"
else
    echo -e "${RED}⚠️  Kibali API ne répond pas, vérifiez les logs:${NC}"
    echo -e "   tail -50 /tmp/kibalone_logs/kibali_api.log"
fi
