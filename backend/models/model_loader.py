"""AI model loading utilities - ChromaDB version"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import chromadb


class ModelLoader:
    """Handles loading and management of AI models with ChromaDB"""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.chroma_client = None
        self.collection = None
        self.clip_model = None
    
    def check_files_exist(self):
        """Check if all required files exist"""
        required_dirs = [self.config.LORA_MODEL_PATH, self.config.IMAGE_BASE_PATH]
        
        missing = []
        
        # Check if ChromaDB directory exists
        if not os.path.exists(self.config.CHROMA_DB_DIR):
            missing.append(f"ChromaDB directory: {self.config.CHROMA_DB_DIR}")
        
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                missing.append(dir_path)
        
        if missing:
            print("❌ Missing required files/directories:")
            for item in missing:
                print(f"   - {item}")
            return False
        
        print("✅ All required files found!")
        return True
    
    def load_chromadb(self):
        """Load ChromaDB client and collection"""
        print("📊 Loading ChromaDB...")
        
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.config.CHROMA_DB_DIR)
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.config.COLLECTION_NAME
            )
            
            # Get collection count
            count = self.collection.count()
            print(f"✅ ChromaDB loaded with {count} documents")
            
        except Exception as e:
            print(f"❌ Error loading ChromaDB: {e}")
            raise
    
    def load_clip_model(self):
        """Load CLIP model using SentenceTransformers"""
        print("🖼️ Loading CLIP model...")
        
        try:
            self.clip_model = SentenceTransformer(
                self.config.CLIP_MODEL_NAME,
                device=self.config.DEVICE
            )
            print("✅ CLIP model loaded")
            
        except Exception as e:
            print(f"❌ Error loading CLIP model: {e}")
            raise
    
    def load_lora_model(self):
        """Load LoRA model for response generation"""
        print("🤖 Loading LoRA model...")
        
        # Try Unsloth first
        try:
            from unsloth import FastLanguageModel
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.config.LORA_MODEL_PATH,
                max_seq_length=2048,
                dtype=None,
                load_in_4bit=True if self.config.DEVICE == "cuda" else False,
            )
            FastLanguageModel.for_inference(self.model)
            print("✅ LoRA model loaded with Unsloth")
            return True
            
        except Exception as e:
            print(f"⚠️ Unsloth loading failed: {e}")
            print("🔄 Trying standard transformers loading...")
            
            # Fallback to standard transformers
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.config.LORA_MODEL_PATH)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.LORA_MODEL_PATH,
                    torch_dtype=torch.float16 if self.config.DEVICE == "cuda" else torch.float32,
                    device_map="auto" if self.config.DEVICE == "cuda" else None,
                    load_in_4bit=True if self.config.DEVICE == "cuda" else False,
                )
                self.model.eval()
                print("✅ LoRA model loaded with transformers")
                return True
                
            except Exception as e2:
                print(f"❌ Failed to load LoRA model: {e2}")
                print("🔄 Running without LoRA model (CLIP + retrieval only)")
                self.model = None
                self.tokenizer = None
                return False
    
    def load_all_models(self):
        """Load all required models"""
        print("🚀 Loading models...")
        
        if not self.check_files_exist():
            raise FileNotFoundError("Required files missing")
        
        self.load_chromadb()
        self.load_clip_model()
        self.load_lora_model()
        
        print("✅ All models loaded successfully!")
    
    def get_models(self):
        """Return loaded models as dictionary"""
        return {
            'model': self.model,
            'tokenizer': self.tokenizer,
            'chroma_client': self.chroma_client,
            'collection': self.collection,
            'clip_model': self.clip_model
        }