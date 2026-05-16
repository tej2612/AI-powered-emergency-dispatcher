"""Batch processing utilities for ChromaDB ingestion"""

import os
from typing import List, Dict, Tuple
import chromadb
from tqdm import tqdm


class BatchProcessor:
    """Process and insert data into ChromaDB in batches"""
    
    def __init__(self, chroma_client: chromadb.Client, collection_name: str, batch_size: int = 100):
        self.client = chroma_client
        self.collection_name = collection_name
        self.batch_size = batch_size
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            return self.client.get_collection(name=self.collection_name)
        except:
            return self.client.create_collection(name=self.collection_name)
    
    def insert_batch(self, documents: List[str], embeddings: List[list], 
                     metadatas: List[Dict], ids: List[str]) -> bool:
        """
        Insert a batch of documents into ChromaDB
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of unique IDs
            
        Returns:
            Success boolean
        """
        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            print(f"❌ Error inserting batch: {e}")
            return False
    
    def insert_all(self, documents: List[str], embeddings: List[list], 
                   metadatas: List[Dict], ids: List[str]) -> Tuple[int, int]:
        """
        Insert all data in batches with progress tracking
        
        Returns:
            Tuple of (successful_inserts, failed_inserts)
        """
        total = len(documents)
        successful = 0
        failed = 0
        
        print(f"📥 Inserting {total} documents in batches of {self.batch_size}...")
        
        for i in tqdm(range(0, total, self.batch_size)):
            batch_end = min(i + self.batch_size, total)
            
            batch_docs = documents[i:batch_end]
            batch_embs = embeddings[i:batch_end]
            batch_meta = metadatas[i:batch_end]
            batch_ids = ids[i:batch_end]
            
            if self.insert_batch(batch_docs, batch_embs, batch_meta, batch_ids):
                successful += len(batch_docs)
            else:
                failed += len(batch_docs)
        
        return successful, failed
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        return {
            "name": self.collection_name,
            "count": self.collection.count(),
        }
    
    def check_duplicate_ids(self, new_ids: List[str]) -> List[str]:
        """
        Check which IDs already exist in the collection
        
        Returns:
            List of duplicate IDs
        """
        existing_ids = []
        
        try:
            # Query collection for existing IDs
            for batch_start in range(0, len(new_ids), 100):
                batch_end = min(batch_start + 100, len(new_ids))
                batch_ids = new_ids[batch_start:batch_end]
                
                try:
                    results = self.collection.get(ids=batch_ids)
                    if results and results.get('ids'):
                        existing_ids.extend(results['ids'])
                except:
                    pass  # ID doesn't exist
        except Exception as e:
            print(f"⚠️ Error checking duplicates: {e}")
        
        return existing_ids