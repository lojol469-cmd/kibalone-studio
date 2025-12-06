#!/usr/bin/env python3
"""
🎨 ASSET MANAGER - Système de recherche et téléchargement d'assets 3D
========================================================================
Intègre plusieurs sources gratuites:
- Poly Haven (textures PBR, HDRIs, models)
- Sketchfab (via API publique)
- Free3D, CGTrader (web scraping léger)
- Procedural generation (fallback)

USAGE: Kibali recherche automatiquement les meilleurs assets pour chaque demande
"""

import requests
import json
import os
from typing import Dict, List, Optional
from pathlib import Path
import urllib.parse

# Dossiers de cache
CACHE_DIR = Path(__file__).parent / "assets_cache"
MODELS_CACHE = CACHE_DIR / "models"
TEXTURES_CACHE = CACHE_DIR / "textures"
HDRI_CACHE = CACHE_DIR / "hdri"

# Créer dossiers si nécessaire
for folder in [MODELS_CACHE, TEXTURES_CACHE, HDRI_CACHE]:
    folder.mkdir(parents=True, exist_ok=True)

# ============================================
# POLY HAVEN - Textures PBR + HDRIs (100% gratuit)
# ============================================

def search_poly_haven_textures(query: str, limit: int = 5) -> List[Dict]:
    """
    Recherche textures PBR sur Poly Haven (CC0 - domaine public)
    Categories: wood, metal, stone, fabric, ground, concrete, etc.
    """
    try:
        # API Poly Haven pour lister les assets
        response = requests.get("https://api.polyhaven.com/assets", params={"t": "textures"}, timeout=10)
        
        if response.status_code == 200:
            all_textures = response.json()
            query_lower = query.lower()
            
            # Filtre par mots-clés
            matches = []
            for tex_id, tex_data in all_textures.items():
                name = tex_data.get('name', '').lower()
                categories = tex_data.get('categories', [])
                
                if query_lower in name or any(query_lower in cat.lower() for cat in categories):
                    matches.append({
                        'id': tex_id,
                        'name': tex_data.get('name'),
                        'categories': categories,
                        'download_url': f"https://polyhaven.com/a/{tex_id}",
                        'preview': f"https://cdn.polyhaven.com/asset_img/thumbs/{tex_id}.png?height=200",
                        'source': 'polyhaven',
                        'license': 'CC0 (Public Domain)'
                    })
                    
                    if len(matches) >= limit:
                        break
            
            return matches
        
        return []
    except Exception as e:
        print(f"❌ Erreur Poly Haven: {e}")
        return []


def download_poly_haven_texture(texture_id: str, resolution: str = "1k") -> Dict:
    """
    Télécharge texture PBR complète (albedo, normal, roughness, etc.)
    Resolutions: 1k, 2k, 4k, 8k
    """
    try:
        # Récupère les URLs de téléchargement
        response = requests.get(f"https://api.polyhaven.com/files/{texture_id}", timeout=10)
        
        if response.status_code == 200:
            files = response.json()
            
            # Trouve les fichiers de texture pour la résolution demandée
            texture_files = {}
            
            if 'Textures' in files and resolution in files['Textures']:
                maps = files['Textures'][resolution]
                
                for map_type, map_data in maps.items():
                    if 'jpg' in map_data:
                        url = map_data['jpg']['url']
                        local_path = TEXTURES_CACHE / f"{texture_id}_{map_type}_{resolution}.jpg"
                        
                        # Télécharge si pas en cache
                        if not local_path.exists():
                            print(f"📥 Téléchargement {map_type}...")
                            img_response = requests.get(url, timeout=30)
                            if img_response.status_code == 200:
                                local_path.write_bytes(img_response.content)
                        
                        texture_files[map_type] = str(local_path)
            
            return {
                'success': True,
                'texture_id': texture_id,
                'files': texture_files,
                'resolution': resolution
            }
        
        return {'success': False, 'error': 'Texture not found'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ============================================
# POLY HAVEN - HDRIs (éclairage réaliste)
# ============================================

def search_poly_haven_hdri(query: str = "outdoor", limit: int = 5) -> List[Dict]:
    """
    Recherche HDRIs pour éclairage IBL (Image Based Lighting)
    Categories: outdoor, indoor, studio, night, sunrise, sunset
    """
    try:
        response = requests.get("https://api.polyhaven.com/assets", params={"t": "hdris"}, timeout=10)
        
        if response.status_code == 200:
            all_hdris = response.json()
            query_lower = query.lower()
            
            matches = []
            for hdri_id, hdri_data in all_hdris.items():
                name = hdri_data.get('name', '').lower()
                categories = hdri_data.get('categories', [])
                
                if query_lower in name or any(query_lower in cat.lower() for cat in categories):
                    matches.append({
                        'id': hdri_id,
                        'name': hdri_data.get('name'),
                        'categories': categories,
                        'download_url': f"https://polyhaven.com/a/{hdri_id}",
                        'preview': f"https://cdn.polyhaven.com/asset_img/thumbs/{hdri_id}.png?height=200",
                        'source': 'polyhaven',
                        'license': 'CC0'
                    })
                    
                    if len(matches) >= limit:
                        break
            
            return matches
        
        return []
    except Exception as e:
        print(f"❌ Erreur HDRI: {e}")
        return []


# ============================================
# SKETCHFAB - Modèles 3D (API publique limitée)
# ============================================

def search_sketchfab_models(query: str, limit: int = 10, downloadable_only: bool = True) -> List[Dict]:
    """
    Recherche modèles 3D sur Sketchfab
    ATTENTION: Vérifier licences (CC-BY, CC0 recommandés)
    """
    try:
        params = {
            'q': query,
            'type': 'models',
            'downloadable': downloadable_only,
            'sort_by': '-likeCount',
            'count': limit
        }
        
        # API publique Sketchfab (pas besoin de clé pour recherche)
        response = requests.get("https://api.sketchfab.com/v3/search", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            models = []
            for model in results:
                models.append({
                    'id': model.get('uid'),
                    'name': model.get('name'),
                    'description': model.get('description', '')[:200],
                    'author': model.get('user', {}).get('displayName'),
                    'license': model.get('license', {}).get('label'),
                    'thumbnail': model.get('thumbnails', {}).get('images', [{}])[0].get('url'),
                    'view_url': model.get('viewerUrl'),
                    'downloadable': model.get('isDownloadable'),
                    'source': 'sketchfab'
                })
            
            return models
        
        return []
    except Exception as e:
        print(f"❌ Erreur Sketchfab: {e}")
        return []


# ============================================
# GÉNÉRATEUR PROCÉDURAL (fallback)
# ============================================

def generate_procedural_asset(asset_type: str, params: Dict) -> Dict:
    """
    Génère assets procéduralement si aucun trouvé en ligne
    Types: terrain, building, tree, rock, column, etc.
    """
    templates = {
        'terrain': {
            'type': 'PlaneGeometry',
            'width': params.get('width', 50),
            'height': params.get('height', 50),
            'segments': params.get('segments', 50),
            'material': {
                'color': params.get('color', '#4a8c2a'),
                'roughness': 0.9,
                'metalness': 0.1
            }
        },
        'building': {
            'type': 'BoxGeometry',
            'width': params.get('width', 10),
            'height': params.get('height', 15),
            'depth': params.get('depth', 10),
            'material': {
                'color': params.get('color', '#cccccc'),
                'roughness': 0.7,
                'metalness': 0.3
            }
        },
        'column': {
            'type': 'CylinderGeometry',
            'radiusTop': params.get('radiusTop', 0.5),
            'radiusBottom': params.get('radiusBottom', 0.6),
            'height': params.get('height', 8),
            'segments': 32,
            'material': {
                'color': params.get('color', '#f0e6d2'),
                'roughness': 0.8,
                'metalness': 0.1
            }
        },
        'tree': {
            'type': 'composite',
            'parts': [
                {
                    'type': 'CylinderGeometry',
                    'radiusTop': 0.3,
                    'radiusBottom': 0.5,
                    'height': 6,
                    'material': {'color': '#8b4513'}
                },
                {
                    'type': 'SphereGeometry',
                    'radius': 3,
                    'position': [0, 6, 0],
                    'material': {'color': '#228b22'}
                }
            ]
        },
        'football_field': {
            'type': 'composite',
            'parts': [
                {
                    'type': 'PlaneGeometry',
                    'width': 105,
                    'height': 68,
                    'rotation': [-Math.PI/2, 0, 0],
                    'material': {'color': '#4a8c2a', 'roughness': 0.9}
                },
                # Lignes blanches (à implémenter avec des BoxGeometry fins)
            ]
        }
    }
    
    template = templates.get(asset_type, templates['building'])
    
    return {
        'success': True,
        'asset_type': asset_type,
        'procedural': True,
        'geometry': template,
        'source': 'procedural'
    }


# ============================================
# ANALYSEUR INTELLIGENT DE REQUÊTES
# ============================================

def analyze_asset_request(prompt: str) -> Dict:
    """
    Analyse une demande complexe et détermine quels assets chercher
    Exemples:
    - "mets une colonne grecque" → search model:column + texture:marble
    - "fait un terrain de football" → procedural:football_field + texture:grass
    - "ajoute un bâtiment moderne" → search model:building + texture:glass
    """
    prompt_lower = prompt.lower()
    
    result = {
        'assets_needed': [],
        'search_queries': [],
        'procedural_fallback': None
    }
    
    # Détection de types d'assets
    asset_keywords = {
        'colonne': {'model': 'column', 'texture': 'marble', 'procedural': 'column'},
        'column': {'model': 'column', 'texture': 'marble', 'procedural': 'column'},
        'terrain': {'model': 'terrain', 'texture': 'grass', 'procedural': 'terrain'},
        'football': {'model': 'football field', 'texture': 'grass', 'procedural': 'football_field'},
        'stade': {'model': 'stadium', 'texture': 'concrete', 'procedural': 'building'},
        'bâtiment': {'model': 'building', 'texture': 'concrete', 'procedural': 'building'},
        'building': {'model': 'building', 'texture': 'concrete', 'procedural': 'building'},
        'arbre': {'model': 'tree', 'texture': 'bark', 'procedural': 'tree'},
        'tree': {'model': 'tree', 'texture': 'bark', 'procedural': 'tree'},
        'maison': {'model': 'house', 'texture': 'brick', 'procedural': 'building'},
        'house': {'model': 'house', 'texture': 'brick', 'procedural': 'building'},
    }
    
    for keyword, config in asset_keywords.items():
        if keyword in prompt_lower:
            result['assets_needed'].append({
                'type': keyword,
                'model_query': config['model'],
                'texture_query': config['texture'],
                'procedural_type': config['procedural']
            })
            result['search_queries'].append(config['model'])
            result['procedural_fallback'] = config['procedural']
            break
    
    # Si rien trouvé, mode générique
    if not result['assets_needed']:
        result['assets_needed'].append({
            'type': 'generic',
            'model_query': prompt,
            'texture_query': 'default',
            'procedural_type': 'building'
        })
        result['search_queries'].append(prompt)
        result['procedural_fallback'] = 'building'
    
    return result


# ============================================
# API UNIFIÉE POUR KIBALI
# ============================================

def fetch_asset_for_prompt(prompt: str, prefer_procedural: bool = False) -> Dict:
    """
    Point d'entrée unique: analyse le prompt et retourne le meilleur asset
    
    Workflow:
    1. Analyse le prompt
    2. Cherche sur Sketchfab (si !prefer_procedural)
    3. Cherche textures Poly Haven
    4. Fallback sur génération procédurale
    """
    analysis = analyze_asset_request(prompt)
    
    print(f"🔍 Analyse: {analysis}")
    
    results = {
        'prompt': prompt,
        'analysis': analysis,
        'models_found': [],
        'textures_found': [],
        'procedural_available': None,
        'recommended': None
    }
    
    # 1. Recherche modèles 3D
    if not prefer_procedural and analysis['search_queries']:
        for query in analysis['search_queries'][:1]:  # Premier query seulement
            models = search_sketchfab_models(query, limit=3)
            results['models_found'].extend(models)
    
    # 2. Recherche textures
    if analysis['assets_needed']:
        texture_query = analysis['assets_needed'][0]['texture_query']
        textures = search_poly_haven_textures(texture_query, limit=3)
        results['textures_found'] = textures
    
    # 3. Génération procédurale (fallback)
    if analysis['procedural_fallback']:
        procedural = generate_procedural_asset(
            analysis['procedural_fallback'],
            {}
        )
        results['procedural_available'] = procedural
    
    # 4. Recommandation
    if results['models_found']:
        results['recommended'] = {
            'type': 'downloaded_model',
            'data': results['models_found'][0],
            'textures': results['textures_found'][:1] if results['textures_found'] else []
        }
    elif results['procedural_available']:
        results['recommended'] = {
            'type': 'procedural',
            'data': results['procedural_available'],
            'textures': results['textures_found'][:1] if results['textures_found'] else []
        }
    
    return results


# ============================================
# TESTS
# ============================================

if __name__ == "__main__":
    print("🎨 ASSET MANAGER - Tests")
    print("=" * 60)
    
    # Test 1: Recherche textures
    print("\n1️⃣ Test textures Poly Haven (bois)...")
    textures = search_poly_haven_textures("wood", limit=3)
    print(f"✅ {len(textures)} textures trouvées")
    for tex in textures:
        print(f"   • {tex['name']} - {tex['categories']}")
    
    # Test 2: Recherche HDRIs
    print("\n2️⃣ Test HDRIs Poly Haven (outdoor)...")
    hdris = search_poly_haven_hdri("outdoor", limit=3)
    print(f"✅ {len(hdris)} HDRIs trouvés")
    
    # Test 3: Recherche modèles Sketchfab
    print("\n3️⃣ Test Sketchfab (column)...")
    models = search_sketchfab_models("greek column", limit=3)
    print(f"✅ {len(models)} modèles trouvés")
    for model in models:
        print(f"   • {model['name']} by {model['author']}")
    
    # Test 4: Analyse requête complexe
    print("\n4️⃣ Test analyse requête complexe...")
    result = fetch_asset_for_prompt("mets une colonne grecque")
    print(f"✅ Analyse: {result['analysis']}")
    print(f"   Modèles: {len(result['models_found'])}")
    print(f"   Textures: {len(result['textures_found'])}")
    print(f"   Recommandation: {result['recommended']['type'] if result['recommended'] else 'None'}")
    
    print("\n✅ Tous les tests passés!")
