"""Distributed embedding generation for ChromaDB ingestion with Location Support"""
# INGESTION/EMBEDDING_GENERATOR.PY

import os
import re
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Tuple, Optional


def normalize_location(loc):
    """
    Normalize location string to consistent format
    
    Args:
        loc: Raw location string
        
    Returns:
        Normalized location string
    """
    if not isinstance(loc, str) or str(loc).strip().lower() == "nan" or loc.strip() == "":
        return "Unknown"
    
    # Remove hashtags, numbers, punctuation, etc.
    loc = re.sub(r"[^a-zA-Z\s,]", "", loc)
    
    # Split on commas and deduplicate segments
    parts = [p.strip().title() for p in loc.split(",") if p.strip()]
    parts = list(dict.fromkeys(parts))  # preserve order but remove duplicates
    
    # Join normalized components
    normalized = ", ".join(parts)
    
    # Handle incomplete tokens
    if not normalized:
        normalized = "Unknown"
    
    return normalized


class EmbeddingGenerator:
    """Generate multimodal embeddings for text, images, and locations"""
    
    def __init__(self, model_name: str, device: str, text_weight: float = 0.7, image_weight: float = 0.2, location_weight: float = 0.1):
        self.model_name = model_name
        self.device = device
        self.text_weight = text_weight
        self.image_weight = image_weight
        self.location_weight = location_weight
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load CLIP model"""
        print(f"🧠 Loading CLIP model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name, device=self.device)
        print(f"✅ Model loaded on {self.device}")
    
    def encode_text(self, text: str) -> torch.Tensor:
        """Encode text to embedding"""
        try:
            embedding = self.model.encode([text], convert_to_tensor=True, device=self.device)
            return embedding
        except Exception as e:
            print(f"⚠️ Error encoding text: {e}")
            return torch.zeros(512, device=self.device)
    
    def encode_image(self, image_path: str) -> torch.Tensor:
        """Encode image to embedding"""
        try:
            if not os.path.exists(image_path):
                return torch.zeros(512, device=self.device)
            
            image = Image.open(image_path).convert("RGB")
            embedding = self.model.encode([image], convert_to_tensor=True, device=self.device)
            return embedding
        except Exception as e:
            print(f"⚠️ Error encoding image {image_path}: {e}")
            return torch.zeros(512, device=self.device)
    
    def encode_location(self, location: str) -> torch.Tensor:
        """Encode location to embedding"""
        try:
            # Normalize location first
            normalized_loc = normalize_location(location)
            embedding = self.model.encode([normalized_loc], convert_to_tensor=True, device=self.device)
            return embedding
        except Exception as e:
            print(f"⚠️ Error encoding location: {e}")
            return torch.zeros(512, device=self.device)
    
    def generate_multimodal_embedding(self, text: str, image_path: str, location: str = None) -> list:
        """
        Generate combined text + image + location embedding
        
        Args:
            text: Tweet text
            image_path: Path to image file
            location: Location string (optional, will use 0.7/0.3 weights if None)
            
        Returns:
            List of floats representing the embedding
        """
        try:
            # Text embedding
            text_emb = self.encode_text(text)
            
            # Image embedding
            image_emb = self.encode_image(image_path)
            
            # If location is provided, use three-way weighting
            if location and location.strip():
                location_emb = self.encode_location(location)
                # Weighted combination: 70% text + 20% image + 10% location
                combined = (self.text_weight * text_emb + 
                           self.image_weight * image_emb + 
                           self.location_weight * location_emb)
            else:
                # Fallback to text + image only (70/30 split)
                combined = self.text_weight * text_emb + self.image_weight * image_emb
            
            # Convert to list
            return combined.cpu().numpy().flatten().tolist()
            
        except Exception as e:
            print(f"⚠️ Error generating multimodal embedding: {e}")
            return [0.0] * 512
    
    def generate_batch_embeddings(self, texts: list, image_paths: list, locations: list = None) -> list:
        """
        Generate embeddings for a batch of text-image-location tuples
        
        Args:
            texts: List of tweet texts
            image_paths: List of image paths
            locations: List of location strings (optional)
            
        Returns:
            List of embeddings
        """
        embeddings = []
        
        if locations is None:
            locations = [None] * len(texts)
        
        for text, img_path, loc in zip(texts, image_paths, locations):
            embedding = self.generate_multimodal_embedding(text, img_path, loc)
            embeddings.append(embedding)
        
        return embeddings