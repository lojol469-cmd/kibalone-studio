#!/bin/bash
# Script pour afficher les logs backend en temps réel

echo "=== LOGS KIBALI API ==="
echo "Appuyez sur Ctrl+C pour arrêter"
echo ""

tail -f /tmp/kibali_api.log | while IFS= read -r line; do
    # Filtre et colore les logs importants
    if [[ "$line" == *"POST"* ]] || [[ "$line" == *"GET"* ]]; then
        echo -e "\e[36m$line\e[0m"  # Cyan pour requêtes HTTP
    elif [[ "$line" == *"ERROR"* ]] || [[ "$line" == *"Erreur"* ]]; then
        echo -e "\e[31m$line\e[0m"  # Rouge pour erreurs
    elif [[ "$line" == *"SUCCESS"* ]] || [[ "$line" == *"✅"* ]]; then
        echo -e "\e[32m$line\e[0m"  # Vert pour succès
    elif [[ "$line" == *"[3D"* ]] || [[ "$line" == *"generate"* ]]; then
        echo -e "\e[33m$line\e[0m"  # Jaune pour 3D
    else
        echo "$line"
    fi
done
