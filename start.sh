#!/bin/bash
echo "🚀 Kibalone Studio v2.0 - Démarrage"
echo "===================================="

cd "$(dirname "$0")"

# Tuer les anciens processus
pkill -f "python.*app.py" 2>/dev/null
pkill -f "python.*5000" 2>/dev/null
pkill -f "python.*5002" 2>/dev/null
sleep 1

# Créer les dossiers
mkdir -p logs static/assets/test_images /tmp/kibalone_uploads

# Lancer le serveur principal
echo "📡 Lancement serveur Flask (port 8080)..."
python3 app.py > logs/server.log 2>&1 &
SERVER_PID=$!

sleep 3

# Vérifier
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Serveur démarré: http://localhost:8080"
    echo "📋 PID: $SERVER_PID"
    echo "📝 Logs: tail -f logs/server.log"
    echo ""
    echo "🎉 Kibalone Studio prêt !"
else
    echo "❌ Erreur démarrage"
    tail -20 logs/server.log
fi
