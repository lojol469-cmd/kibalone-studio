#!/usr/bin/env python3
"""
API d'analyse d'image pour Kibalone Studio
Utilise CLIP, EasyOCR et YOLO pour analyser les images de référence
"""

import sys
import os
from pathlib import Path
import base64
import io
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
import easyocr
from ultralytics import YOLO
import numpy as np

# Chemins des modèles
ISOL_PATH = Path("/home/belikan/Isol")
CLIP_PATH = ISOL_PATH / "kibali-IA/kibali_data/models/clip/models--openai--clip-vit-base-patch32/snapshots"
BLIP_PATH = ISOL_PATH / "kibali-IA/kibali_data/models/huggingface_cache/models--Salesforce--blip-image-captioning-base"
YOLO_PATH = Path("/home/belikan/yolo11n.pt")

class ImageAnalyzer:
    """Analyseur d'images multi-modèles: CLIP + OCR + YOLO"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🖼️  Initialisation Image Analyzer...")
        print(f"   Device: {self.device}")
        
        # 1️⃣ CLIP - Compréhension visuelle
        self._load_clip()
        
        # 1.5️⃣ BLIP - Description détaillée
        self._load_blip()
        
        # 2️⃣ EasyOCR - Lecture de texte
        self._load_ocr()
        
        # 3️⃣ YOLO - Détection d'objets
        self._load_yolo()
        
        print("✅ Image Analyzer prêt!")
    
    def _load_clip(self):
        """Charge CLIP pour l'analyse visuelle"""
        try:
            clip_snapshot = list(CLIP_PATH.glob("*"))[0] if CLIP_PATH.exists() else None
            
            if clip_snapshot:
                print(f"📦 Chargement CLIP local...")
                self.clip_model = CLIPModel.from_pretrained(str(clip_snapshot)).to(self.device)
                self.clip_processor = CLIPProcessor.from_pretrained(str(clip_snapshot))
            else:
                print(f"📦 Chargement CLIP depuis HuggingFace...")
                self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
                self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            print("✅ CLIP chargé")
        except Exception as e:
            print(f"⚠️  CLIP non disponible: {e}")
            self.clip_model = None
            self.clip_processor = None
    
    def _load_blip(self):
        """Charge BLIP pour la description détaillée"""
        try:
            blip_snapshot = list(BLIP_PATH.glob("*"))[0] if BLIP_PATH.exists() else None
            
            if blip_snapshot:
                print(f"📦 Chargement BLIP local...")
                self.blip_model = BlipForConditionalGeneration.from_pretrained(str(blip_snapshot)).to(self.device)
                self.blip_processor = BlipProcessor.from_pretrained(str(blip_snapshot))
            else:
                print(f"📦 Chargement BLIP depuis HuggingFace...")
                self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)
                self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            
            print("✅ BLIP chargé")
        except Exception as e:
            print(f"⚠️  BLIP non disponible: {e}")
            self.blip_model = None
            self.blip_processor = None
    
    def _load_ocr(self):
        """Charge EasyOCR pour la lecture de texte"""
        try:
            print(f"📦 Chargement EasyOCR...")
            self.ocr_reader = easyocr.Reader(['en', 'fr'], gpu=torch.cuda.is_available())
            print("✅ EasyOCR chargé")
        except Exception as e:
            print(f"⚠️  EasyOCR non disponible: {e}")
            self.ocr_reader = None
    
    def _load_yolo(self):
        """Charge YOLO pour la détection d'objets"""
        try:
            if YOLO_PATH.exists():
                print(f"📦 Chargement YOLO11...")
                self.yolo_model = YOLO(str(YOLO_PATH))
                print("✅ YOLO chargé")
            else:
                print(f"⚠️  YOLO non trouvé: {YOLO_PATH}")
                self.yolo_model = None
        except Exception as e:
            print(f"⚠️  YOLO non disponible: {e}")
            self.yolo_model = None
    
    def analyze_image(self, image_data):
        """
        Analyse complète d'une image
        
        Args:
            image_data: Base64 string ou bytes de l'image
        
        Returns:
            dict avec:
            - description: Description textuelle globale (CLIP)
            - detailed_description: Description détaillée (BLIP)
            - objects: Liste d'objets détectés par YOLO
            - text: Texte détecté par OCR
            - colors: Palette de couleurs dominantes
            - style: Style artistique détecté
            - dimensions: Dimensions de l'image
        """
        # Décode l'image
        if isinstance(image_data, str):
            # Base64
            image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
        else:
            image_bytes = image_data
        
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        result = {
            'description': '',
            'objects': [],
            'text': [],
            'colors': [],
            'style': '',
            'dimensions': {'width': image.width, 'height': image.height}
        }
        
        # 1️⃣ CLIP - Description globale
        if self.clip_model:
            result['description'] = self._analyze_with_clip(image)
            result['style'] = self._detect_style_with_clip(image)
        
        # 1.5️⃣ BLIP - Description détaillée
        if self.blip_model:
            result['detailed_description'] = self._caption_with_blip(image)
        
        # 2️⃣ YOLO - Détection d'objets
        if self.yolo_model:
            result['objects'] = self._detect_objects_with_yolo(image)
        
        # 3️⃣ OCR - Lecture de texte
        if self.ocr_reader:
            result['text'] = self._extract_text_with_ocr(image)
        
        # 4️⃣ Extraction de couleurs
        result['colors'] = self._extract_colors(image)
        
        # 5️⃣ Si aucun objet détecté par YOLO, utiliser le texte OCR comme objets
        if not result['objects'] and result['text']:
            for text_item in result['text']:
                if text_item['confidence'] > 0.5:  # Seuil de confiance
                    result['objects'].append({
                        'class': f"text_{text_item['text']}",
                        'confidence': text_item['confidence'],
                        'bbox': text_item['bbox']
                    })
        
        return result
    
    def _analyze_with_clip(self, image):
        """Analyse l'image avec CLIP pour obtenir une description"""
        try:
            # Questions contextuelles pour CLIP - étendues pour logos et texte
            prompts = [
                "a photo of a vehicle",
                "a photo of a building", 
                "a photo of a person",
                "a photo of an animal",
                "a photo of furniture",
                "a photo of nature",
                "a photo of food",
                "a photo of an object",
                "a logo with letters",
                "a text logo",
                "a letter T",
                "an initial letter",
                "a minimalist logo",
                "a modern logo",
                "text and typography",
                "a graphic design",
                "a brand logo",
                "a letter in a logo"
            ]
            
            inputs = self.clip_processor(
                text=prompts,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # Meilleure correspondance
            best_idx = probs.argmax().item()
            confidence = probs[0][best_idx].item()
            
            category = prompts[best_idx].replace("a photo of ", "")
            
            return f"{category} (confidence: {confidence:.2f})"
            
        except Exception as e:
            print(f"Erreur CLIP: {e}")
            return "image analysis failed"
    
    def _detect_style_with_clip(self, image):
        """Détecte le style artistique avec CLIP"""
        try:
            styles = [
                "realistic photo",
                "cartoon drawing",
                "sketch drawing",
                "3D render",
                "painting",
                "technical blueprint"
            ]
            
            inputs = self.clip_processor(
                text=styles,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                probs = outputs.logits_per_image.softmax(dim=1)
            
            best_idx = probs.argmax().item()
            return styles[best_idx]
            
        except Exception as e:
            print(f"Erreur style detection: {e}")
            return "realistic"
    
    def _caption_with_blip(self, image):
        """Génère une description détaillée avec BLIP"""
        try:
            inputs = self.blip_processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.blip_model.generate(**inputs, max_length=100, num_beams=4)
            
            caption = self.blip_processor.decode(outputs[0], skip_special_tokens=True)
            return caption
            
        except Exception as e:
            print(f"Erreur BLIP: {e}")
            return "detailed captioning failed"
    
    def _detect_objects_with_yolo(self, image):
        """Détecte les objets dans l'image avec YOLO"""
        try:
            results = self.yolo_model(image)
            
            objects = []
            for result in results:
                for box in result.boxes:
                    objects.append({
                        'class': result.names[int(box.cls)],
                        'confidence': float(box.conf),
                        'bbox': box.xyxy[0].tolist()
                    })
            
            return objects
            
        except Exception as e:
            print(f"Erreur YOLO: {e}")
            return []
    
    def _extract_text_with_ocr(self, image):
        """Extrait le texte de l'image avec OCR"""
        try:
            # Convertit PIL Image en numpy array
            img_array = np.array(image)
            
            results = self.ocr_reader.readtext(img_array)
            
            texts = []
            for (bbox, text, confidence) in results:
                texts.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox
                })
            
            return texts
            
        except Exception as e:
            print(f"Erreur OCR: {e}")
            return []
    
    def _extract_colors(self, image, num_colors=5):
        """Extrait les couleurs dominantes de l'image"""
        try:
            # Réduit l'image pour accélérer
            img_small = image.resize((150, 150))
            img_array = np.array(img_small)
            
            # Reshape en liste de pixels
            pixels = img_array.reshape(-1, 3)
            
            # K-means simple pour trouver les couleurs dominantes
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            colors = []
            for color in kmeans.cluster_centers_:
                hex_color = '#{:02x}{:02x}{:02x}'.format(
                    int(color[0]),
                    int(color[1]),
                    int(color[2])
                )
                colors.append(hex_color)
            
            return colors
            
        except Exception as e:
            print(f"Erreur extraction couleurs: {e}")
            return ['#888888']

# Instance globale
analyzer = None

def init_analyzer():
    """Initialise l'analyseur d'images"""
    global analyzer
    if analyzer is None:
        analyzer = ImageAnalyzer()
    return analyzer

if __name__ == "__main__":
    # Test
    print("🧪 Test de l'Image Analyzer...")
    init_analyzer()
    print("✅ Test réussi!")
