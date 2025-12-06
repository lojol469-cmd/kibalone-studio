#!/bin/bash
"""
🧪 TEST COMPLET DE L'ORCHESTRATION KIBALI
==========================================
"""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 TEST 1: Orchestrateur seul (plan uniquement)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 /home/belikan/Isol/Meshy/kibali_orchestrator.py

echo ""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 TEST 2: Dispatcher (détection complexité)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 <<EOF
from kibali_dispatcher import KibaliDispatcher

dispatcher = KibaliDispatcher()

test_prompts = [
    "crée un personnage qui court",
    "terrain de foot",
    "orbite 360",
    "retire 3 objets"
]

for prompt in test_prompts:
    result = dispatcher.dispatch(prompt)
    print(f"\n📝 '{prompt}'")
    print(f"   Type: {result['type']}")
    print(f"   Action: {result['action']}")
EOF

echo ""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 TEST 3: API Orchestrate (plan only)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

curl -X POST http://localhost:11000/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "crée un personnage qui court et saute", "execute": false}' \
  | python3 -m json.tool

echo ""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ TESTS TERMINÉS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
