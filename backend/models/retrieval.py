"""ChromaDB retrieval and search functions"""

import torch
from utils.image_utils import find_image_path, image_to_base64


class RetrievalSystem:
    """Handles vector similarity search with ChromaDB"""
    
    def __init__(self, collection, clip_model, config):
        self.collection = collection
        self.clip_model = clip_model
        self.config = config
    
    def encode_text(self, query_text):
        """Encode query text into CLIP embedding"""
        embedding = self.clip_model.encode(
            [query_text],
            convert_to_tensor=True,
            device=self.config.DEVICE
        )
        return embedding.cpu().tolist()[0]
    
    def retrieve_topk(self, query, top_k=None):
        """
        Retrieve top-k similar items from ChromaDB
        
        Args:
            query: Text query string
            top_k: Number of results to return (default from config)
            
        Returns:
            List of result dictionaries with metadata and images
        """
        if top_k is None:
            top_k = self.config.TOP_K
        
        # Encode query text
        query_embedding = self.encode_text(query)
        
        # Query ChromaDB
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return []
        
        # Process results
        processed_results = []
        
        if not results or not results.get('documents'):
            return processed_results
        
        documents = results['documents'][0] if results['documents'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        distances = results['distances'][0] if results.get('distances') else [0] * len(documents)
        ids = results['ids'][0] if results['ids'] else []
        
        for i, (doc, meta, distance, doc_id) in enumerate(zip(documents, metadatas, distances, ids)):
            # Extract metadata
            disaster_type = meta.get('disaster_type', 'Unknown')
            image_path_from_meta = meta.get('image_path', '')
            extracted_location = meta.get('extracted_location', '')
            source_file = meta.get('source_file', '')
            
            # Find actual image path in your file system
            # Extract image_id from the metadata image_path
            if image_path_from_meta:
                # Format: CrisisMMD/data_image/2017_11_12/918318861522313216_0.jpg
                image_filename = image_path_from_meta.split('/')[-1]
                image_id = image_filename.replace('.jpg', '')
            else:
                image_id = None
            
            # Find and encode image
            image_path = find_image_path(image_id, self.config.IMAGE_BASE_PATH) if image_id else None
            image_base64 = image_to_base64(image_path) if image_path else None
            
            # Create result entry
            entry = {
                'id': doc_id,
                'tweet_text': doc,
                'tweet_id': image_id.split('_')[0] if image_id else 'unknown',
                'image_id': image_id,
                'disaster_type': disaster_type,
                'extracted_location': extracted_location,
                'source_file': source_file,
                'score': 1 - distance,  # Convert distance to similarity score
                'image_base64': image_base64,
                'image_caption': doc,  # Using tweet text as caption
                'image_damage': None,  # Will be inferred later
                'image_info': None     # Will be inferred later
            }
            
            processed_results.append(entry)
        
        return processed_results
    
    def retrieve_by_location(self, location, top_k=None):
        """
        Retrieve results filtered by location
        
        Args:
            location: Location string
            top_k: Number of results
            
        Returns:
            List of filtered results
        """
        if top_k is None:
            top_k = self.config.TOP_K
        
        try:
            # Query with location filter
            results = self.collection.query(
                query_embeddings=[self.encode_text(location)],
                n_results=top_k * 2,  # Get more to filter
                where={"extracted_location": {"$contains": location}}
            )
            
            return self._process_results(results, top_k)
            
        except Exception as e:
            print(f"Error in location-based retrieval: {e}")
            return self.retrieve_topk(location, top_k)
    
    def retrieve_by_disaster_type(self, disaster_type, top_k=None):
        """
        Retrieve results filtered by disaster type
        
        Args:
            disaster_type: Disaster type string
            top_k: Number of results
            
        Returns:
            List of filtered results
        """
        if top_k is None:
            top_k = self.config.TOP_K
        
        try:
            # Query with disaster type filter
            results = self.collection.query(
                query_embeddings=[self.encode_text(disaster_type)],
                n_results=top_k,
                where={"disaster_type": disaster_type.title()}
            )
            
            return self._process_results(results, top_k)
            
        except Exception as e:
            print(f"Error in disaster type retrieval: {e}")
            return self.retrieve_topk(disaster_type, top_k)
    
    def _process_results(self, results, limit):
        """Helper to process ChromaDB results"""
        processed = []
        
        if not results or not results.get('documents'):
            return processed
        
        documents = results['documents'][0][:limit]
        metadatas = results['metadatas'][0][:limit]
        distances = results.get('distances', [[0]*len(documents)])[0][:limit]
        ids = results['ids'][0][:limit]
        
        for doc, meta, distance, doc_id in zip(documents, metadatas, distances, ids):
            image_path_from_meta = meta.get('image_path', '')
            
            if image_path_from_meta:
                image_filename = image_path_from_meta.split('/')[-1]
                image_id = image_filename.replace('.jpg', '')
            else:
                image_id = None
            
            image_path = find_image_path(image_id, self.config.IMAGE_BASE_PATH) if image_id else None
            image_base64 = image_to_base64(image_path) if image_path else None
            
            entry = {
                'id': doc_id,
                'tweet_text': doc,
                'tweet_id': image_id.split('_')[0] if image_id else 'unknown',
                'image_id': image_id,
                'disaster_type': meta.get('disaster_type', 'Unknown'),
                'extracted_location': meta.get('extracted_location', ''),
                'source_file': meta.get('source_file', ''),
                'score': 1 - distance,
                'image_base64': image_base64,
                'image_caption': doc,
                'image_damage': None,
                'image_info': None
            }
            
            processed.append(entry)
        
        return processed