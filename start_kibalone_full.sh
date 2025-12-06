#!/bin/bash
# Lance Kibalone Studio avec toutes les APIs IA + LangChain + Assets Dynamiques

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

clear
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${WHITE}     ✨ KIBALONE STUDIO - CODE IA GÉNÉRATIF 3D ✨      ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo -e "${MAGENTA}🧠 Kibali Orchestrator${NC} - IA pour génération 3D par code"
echo -e "${BLUE}💻 CodeLlama + Mistral${NC} - Génération procédurale intelligente"
echo ""

cd /home/belikan/Isol/Meshy

# Vérification et installation des dépendances
echo -e "${YELLOW}📦 Vérification des dépendances...${NC}"
if ! python3 -c "from langchain.agents import Tool" 2>/dev/null; then
    echo -e "${YELLOW}⚙️  Installation de LangChain...${NC}"
    pip install -q langchain langchain-community langchain-huggingface 2>/dev/null
    if python3 -c "from langchain.agents import Tool" 2>/dev/null; then
        echo -e "${GREEN}✅ LangChain installé${NC}"
    else
        echo -e "${RED}⚠️  LangChain non disponible - mode simple activé${NC}"
    fi
else
    echo -e "${GREEN}✅ LangChain déjà installé${NC}"
fi

# Tue les processus existants
echo -e "${YELLOW}🧹 Nettoyage des processus existants...${NC}"
pkill -f kibali_api.py 2>/dev/null
pkill -f "python.*http.server" 2>/dev/null
lsof -ti:11000 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:11080 2>/dev/null | xargs kill -9 2>/dev/null
sleep 1

# Active conda
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    conda activate base
fi

echo -e "${CYAN}🚀 Lancement des services...${NC}"
echo ""

# Crée le répertoire des logs
mkdir -p /tmp/kibalone_logs

# Lance les services essentiels
echo -e "${BLUE}[1/2]${NC} Serveur Web (port 11080)..."
python3 -m http.server 11080 > /tmp/kibalone_logs/http_server.log 2>&1 &
HTTP_PID=$!

echo -e "${MAGENTA}[2/2]${NC} 🧠 Kibali Code IA (port 11000)..."
PORT=11000 python3 kibali_api.py > /tmp/kibalone_logs/kibali_api.log 2>&1 &
KIBALI_PID=$!

# Stocke tous les PIDs
PIDS="$HTTP_PID $KIBALI_PID"

echo ""
echo -e "${YELLOW}⏳ Attente du démarrage (5s)...${NC}"
echo -e "${CYAN}   Initialisation Kibali Code IA${NC}"

# Attends avec barre de progression
for i in {1..5}; do
    echo -ne "${GREEN}▓${NC}"
    sleep 1
done
echo ""


echo ""
echo -e "${CYAN}🔍 Vérification des services...${NC}"
echo ""

# Fonction de vérification avec retry
check_service() {
    local name=$1
    local url=$2
    local color=$3
    
    for i in {1..3}; do
        if curl -s --max-time 2 "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅${NC} ${color}${name}${NC}"
            return 0
        fi
        [ $i -lt 3 ] && sleep 1
    done
    echo -e "${RED}⚠️${NC}  ${color}${name}${NC} ${RED}(vérifiez /tmp/kibalone_logs/)${NC}"
    return 1
}

# Vérifie tous les services
check_service "Serveur Web Interface         " "http://localhost:11080/" "$WHITE"
check_service "🧠 Kibali Code IA            " "http://localhost:11000/api/health" "$MAGENTA"

echo ""
echo -e "${WHITE}${BOLD}🧠 Kibalone Code IA Génératif est prêt !${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🌐 INTERFACE PRINCIPALE:${NC}"
echo -e "${WHITE}   👉 http://localhost:11080/kibalone-studio.html${NC}"
echo ""
echo -e "${MAGENTA}🧠 KIBALI CODE IA:${NC}"
echo -e "${GREEN}   • Génération 3D par code intelligent${NC}"
echo -e "      • Prompt → Code Three.js généré par IA"
echo -e "      • CodeLlama + Mistral pour génération"
echo -e "      • Création procédurale instantanée"
echo ""
echo -e "${YELLOW}📡 Services Backend:${NC}"
echo -e "${MAGENTA}   • Kibali Code IA:             ${WHITE}http://localhost:11000${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📋 Commandes:${NC}"
echo -e "   ${RED}Arrêter:${NC} kill $HTTP_PID $KIBALI_PID"
echo -e "   ${CYAN}Logs:${NC}    tail -f /tmp/kibalone_logs/*.log"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Fonction de nettoyage
cleanup() {
    echo ""
    echo -e "${RED}🛑 Arrêt Kibalone Code IA...${NC}"
    kill $HTTP_PID $KIBALI_PID 2>/dev/null
    echo -e "${GREEN}✅ Services arrêtés${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Garde le script actif
echo ""
echo -e "${YELLOW}⌨️  Appuyez sur ${RED}Ctrl+C${YELLOW} pour arrêter tous les services${NC}"
wait

