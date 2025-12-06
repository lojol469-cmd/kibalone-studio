#!/bin/bash
# Test rapide de la reconstruction 3D multi-vues avec le dataset

echo "🏰 TEST RECONSTRUCTION 3D - CHÂTEAU DE SCEAUX"
echo "=" 
echo ""

cd /home/belikan/Isol/Kibalone-Studio

# Vérifier que les images sont présentes
if [ ! -d "test_images" ] || [ $(ls test_images/*.jpg 2>/dev/null | wc -l) -lt 10 ]; then
    echo "❌ Images de test manquantes"
    echo "   Exécutez d'abord le script de téléchargement"
    exit 1
fi

echo "✅ Trouvé $(ls test_images/*.jpg | wc -l) images de test"
echo ""

# Vérifier que l'API est lancée
echo "🔍 Vérification de l'API MiDaS Multi-View..."
if curl -s http://localhost:5002/api/health > /dev/null 2>&1; then
    echo "✅ API disponible sur port 5002"
else
    echo "⚠️  API non disponible. Lancement..."
    
    # Lancer l'API en arrière-plan
    python3 midas_multiview_api.py > /tmp/midas_test.log 2>&1 &
    MIDAS_PID=$!
    echo "   PID: $MIDAS_PID"
    
    # Attendre le démarrage
    echo "   Attente du démarrage (10s)..."
    sleep 10
    
    if curl -s http://localhost:5002/api/health > /dev/null 2>&1; then
        echo "✅ API démarrée avec succès"
    else
        echo "❌ Échec du démarrage de l'API"
        echo "   Logs: tail -f /tmp/midas_test.log"
        exit 1
    fi
fi

echo ""
echo "🚀 Lancement du test de reconstruction..."
echo "=" 
echo ""

# Lancer le test Python
python3 test_reconstruction_3d.py

echo ""
echo "=" 
echo "✅ Test terminé !"
echo ""
echo "📁 Fichiers générés dans le dossier courant:"
ls -lh test_reconstruction_*.ply test_mesh_*.ply 2>/dev/null

echo ""
echo "💡 Pour visualiser:"
echo "   meshlab test_reconstruction_*.ply"
echo "   meshlab test_mesh_*.ply"
echo ""
