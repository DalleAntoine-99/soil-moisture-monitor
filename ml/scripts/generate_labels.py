"""
Génère labels.csv en combinant Before + After Augmentation
"""
import os
import pandas as pd
from pathlib import Path

# Configuration
DATASET_BASE = "ml/data/raw/Soil_Moisture_Dataset"
OUTPUT_CSV = "ml/data/labels.csv"

# Mapping catégorie → humidité (%)
CATEGORY_TO_HUMIDITY = {
    "dry": 15.0,      # Sol très sec
    "moderate": 50.0, # Sol moyennement humide
    "wet": 85.0       # Sol très humide
}

print("=" * 70)
print("GÉNÉRATION DE labels.csv (Before + After Augmentation)")
print("=" * 70)

# Collecter les images
data = []

# Traiter les deux sources
for source in ["Before Augmentation", "After Augmentation"]:
    source_path = os.path.join(DATASET_BASE, source)
    
    if not os.path.exists(source_path):
        print(f"\n⚠️  Source manquante: {source_path}")
        continue
    
    print(f"\n{'='*70}")
    print(f"📂 Traitement de: {source}")
    print(f"{'='*70}")
    
    for category in ["dry", "moderate", "wet"]:
        category_path = os.path.join(source_path, category)
        
        if not os.path.exists(category_path):
            print(f"  ⚠️  Catégorie manquante: {category}")
            continue
        
        # Lister les images
        images = [
            f for f in os.listdir(category_path) 
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        
        humidity = CATEGORY_TO_HUMIDITY[category]
        source_label = "before" if source == "Before Augmentation" else "after"
        
        print(f"  ✓ {category:10s}: {len(images):5d} images → {humidity:5.1f}% humidité")
        
        for img_filename in images:
            # Chemin relatif depuis Soil_Moisture_Dataset/
            relative_path = f"{source}/{category}/{img_filename}"
            
            data.append({
                'image_filename': relative_path,
                'humidity': humidity,
                'category': category,
                'source': source_label
            })

# Créer DataFrame
df = pd.DataFrame(data)

# Statistiques
print(f"\n{'='*70}")
print("📊 STATISTIQUES GLOBALES")
print(f"{'='*70}")
print(f"  Total images: {len(df)}")
print(f"\n  Par catégorie:")
for cat in ["dry", "moderate", "wet"]:
    count = len(df[df['category'] == cat])
    print(f"    {cat:10s}: {count:5d} images")

print(f"\n  Par source:")
for src in ["before", "after"]:
    count = len(df[df['source'] == src])
    print(f"    {src:10s}: {count:5d} images")

# Sauvegarder
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
df.to_csv(OUTPUT_CSV, index=False)

print(f"\n{'='*70}")
print(f"✅ Fichier créé: {OUTPUT_CSV}")
print(f"{'='*70}")

# Aperçu
print("\n📄 Aperçu des données (10 premières lignes):")
print(df.head(10).to_string(index=False))

print("\n📄 Aperçu des données (10 dernières lignes):")
print(df.tail(10).to_string(index=False))
