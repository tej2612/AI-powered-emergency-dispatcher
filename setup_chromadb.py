"""Setup ChromaDB with multimodal embeddings - Adapted for project structure"""

import os
import sys
import pandas as pd
from tqdm import tqdm
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer
import chromadb

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import Config

# ---------------------------------------------------------
# 1. Initialize persistent Chroma client
# ---------------------------------------------------------
config = Config()
client = chromadb.PersistentClient(path=config.CHROMA_DB_DIR)

# ---------------------------------------------------------
# 2. Load or create collection (delete if exists for fresh start)
# ---------------------------------------------------------
collection_name = config.COLLECTION_NAME

try:
    client.delete_collection(name=collection_name)
    print(f"🗑️ Deleted existing collection: {collection_name}")
except:
    pass

collection = client.create_collection(name=collection_name)
print(f"✅ Created new collection: {collection_name}")

# ---------------------------------------------------------
# 3. Load CLIP model
# ---------------------------------------------------------
print(f"🧠 Loading CLIP model ({config.CLIP_MODEL_NAME})...")
device = config.DEVICE
clip_model = SentenceTransformer(config.CLIP_MODEL_NAME).to(device)

# ---------------------------------------------------------
# 4. Disaster type extractor
# ---------------------------------------------------------
def get_disaster_type(filename: str) -> str:
    name = os.path.basename(filename).lower()
    if "wildfire" in name or "california" in name:
        return "Wildfire"
    elif "earthquake" in name or "mexico" in name:
        return "Earthquake"
    elif "flood" in name or "srilanka" in name:
        return "Flood"
    elif "hurricane" in name:
        return "Hurricane"
    else:
        return "Other"

# ---------------------------------------------------------
# 5. Process data files
# ---------------------------------------------------------
# Update these paths to match your actual data location
base_path = "CrisisMMD"  # Adjust if needed
data_dir = os.path.join(base_path, "annotations")

files = [
    "california_wildfires_with_captions_LRR.tsv",
    "mexico_earthquake_with_captions_LRR.tsv",
    "srilanka_floods_with_captions_LRR.tsv",
]

for file in files:
    file_path = os.path.join(data_dir, file)
    
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        continue

    print(f"\n📄 Processing: {file_path}")
    df = pd.read_csv(file_path, sep="\t")

    disaster_type = get_disaster_type(file)
    print(f"🌋 Disaster type: {disaster_type}")

    texts = df["tweet_text"].astype(str).tolist()
    image_paths = [os.path.join(base_path, path) for path in df["image_path"].astype(str).tolist()]
    ids = [f"{file}_{i}" for i in range(len(texts))]
    
    metadatas = [
        {
            "source_file": file,
            "disaster_type": disaster_type,
            "image_path": img,
            "extracted_location": loc
        }
        for img, loc in zip(image_paths, df["extracted_locations"].astype(str).tolist())
    ]

    # ---------------------------------------------------------
    # 6. Compute CLIP embeddings (text + image average)
    # ---------------------------------------------------------
    combined_embeddings = []

    print("🧩 Generating multimodal embeddings...")
    for text, img_path in tqdm(zip(texts, image_paths), total=len(texts)):
        try:
            # Text embedding
            text_emb = clip_model.encode([text], convert_to_tensor=True, device=device)

            # Image embedding
            if os.path.exists(img_path):
                image = Image.open(img_path).convert("RGB")
                img_emb = clip_model.encode([image], convert_to_tensor=True, device=device)
            else:
                img_emb = torch.zeros_like(text_emb)  # fallback if image missing

            # Average the embeddings (text + image)
            combined = 0.7*(text_emb) + 0.3*(img_emb)
            combined_embeddings.append(combined.cpu().numpy().flatten().tolist())
        except Exception as e:
            print(f"⚠️ Error processing {img_path}: {e}")
            combined_embeddings.append([0.0] * 512)  # Zero embedding as fallback

    # ---------------------------------------------------------
    # 7. Add to ChromaDB
    # ---------------------------------------------------------
    print(f"📥 Adding {len(texts)} multimodal entries to ChromaDB...")
    collection.add(
        documents=texts,
        embeddings=combined_embeddings,
        metadatas=metadatas,
        ids=ids
    )

print("\n✅ All multimodal data successfully added!")
print(f"💾 Persistent store created at: {config.CHROMA_DB_DIR}")

# ---------------------------------------------------------
# 8. Verify
# ---------------------------------------------------------
print("\n📊 Summary:")
print("Total documents:", collection.count())
print("Collections in DB:", [c.name for c in client.list_collections()])