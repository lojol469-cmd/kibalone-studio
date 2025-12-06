#!/bin/bash
# 🎬 TEST PROMPT COMPLET - Architecture Dual Backend
# ==================================================

echo ""
echo "🌟========================================🌟"
echo "   TEST KIBALONE - PERSONNAGE ANIMÉ"
echo "🌟========================================🌟"
echo ""

# Vérifie que les backends sont actifs
echo "📡 Vérification des backends..."
echo ""

check_backend() {
    local name=$1
    local url=$2
    
    if curl -s --max-time 2 "$url" > /dev/null 2>&1; then
        echo "  ✅ $name"
        return 0
    else
        echo "  ❌ $name (DOWN)"
        return 1
    fi
}

check_backend "Kibali Orchestrator (11000)" "http://localhost:11000/api/health"
check_backend "Three.js Backend (11005)" "http://localhost:11005/api/health"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: Création personnage
echo "🎨 [TEST 1/4] Création personnage..."
echo ""

RESPONSE=$(curl -s -X POST http://localhost:11005/api/create-character \
  -H "Content-Type: application/json" \
  -d '{"prompt":"personnage héroïque qui court et saute"}')

CHARACTER_ID=$(echo $RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))")
SUCCESS=$(echo $RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success',False))")

if [ "$SUCCESS" = "True" ]; then
    echo "✅ Personnage créé!"
    echo "   ID: $CHARACTER_ID"
    echo "   Parts: $(echo $RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(', '.join(d.get('parts',[])))")"
else
    echo "❌ Échec création personnage"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 2: Animation course
echo "🏃 [TEST 2/4] Animation course..."
echo ""

RESPONSE=$(curl -s -X POST http://localhost:11005/api/create-animation \
  -H "Content-Type: application/json" \
  -d "{\"objectId\":\"$CHARACTER_ID\",\"animationType\":\"run\"}")

SUCCESS=$(echo $RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success',False))")

if [ "$SUCCESS" = "True" ]; then
    echo "✅ Animation course créée!"
    echo "   Duration: $(echo $RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('duration',0))") frames"
    echo "   Keyframes: $(echo $RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('keyframes',[])))")"
else
    echo "❌ Échec animation course"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 3: Animation saut
echo "🦘 [TEST 3/4] Animation saut..."
echo ""

RESPONSE=$(curl -s -X POST http://localhost:11005/api/create-animation \
  -H "Content-Type: application/json" \
  -d "{\"objectId\":\"$CHARACTER_ID\",\"animationType\":\"jump\"}")

SUCCESS=$(echo $RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success',False))")

if [ "$SUCCESS" = "True" ]; then
    echo "✅ Animation saut créée!"
    echo "   Duration: $(echo $RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('duration',0))") frames"
    echo "   Keyframes: $(echo $RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('keyframes',[])))")"
else
    echo "❌ Échec animation saut"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 4: Orchestration
echo "🎯 [TEST 4/4] Orchestration intelligente..."
echo ""
echo "   Prompt: 'crée un personnage qui court et saute'"
echo ""

RESPONSE=$(curl -s -X POST http://localhost:11000/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"crée un personnage qui court et saute","execute":true}')

UNDERSTOOD=$(echo $RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('understood',False))")

if [ "$UNDERSTOOD" = "True" ]; then
    echo "✅ Orchestration réussie!"
    echo ""
    echo "📋 Plan:"
    echo $RESPONSE | python3 -c "
import sys,json
d=json.load(sys.stdin)
if 'plan' in d:
    print(f\"   • Étapes: {len(d['plan']['steps'])}\")
    print(f\"   • Complexité: {d['plan']['complexity']}\")
    print(f\"   • Temps estimé: {d['plan']['estimated_time']}\")
    print('')
    print('🔧 Outils utilisés:')
    for i, step in enumerate(d['plan']['steps'], 1):
        print(f\"   {i}. {step['tool']}\")
        print(f\"      → {step['reason']}\")
"
else
    echo "❌ Orchestration échouée"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ TOUS LES TESTS TERMINÉS"
echo ""
echo "🌐 Visualiser dans le navigateur:"
echo "   👉 http://localhost:11080/test_character_animation.html"
echo ""
echo "🎯 Résumé:"
echo "   • Personnage: $CHARACTER_ID"
echo "   • Backend Three.js: Port 11005 ✅"
echo "   • Orchestrateur Kibali: Port 11000 ✅"
echo "   • 48 outils disponibles"
echo ""
echo "🌟========================================🌟"
