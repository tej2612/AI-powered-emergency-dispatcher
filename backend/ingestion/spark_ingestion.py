"""PySpark-based data ingestion for ChromaDB - Windows Optimized"""
# INGESTION/SPARK_INGESTION.PY
import os
import sys

python_exe = sys.executable
os.environ['PYSPARK_PYTHON'] = python_exe
os.environ['PYSPARK_DRIVER_PYTHON'] = python_exe
print(f"🐍 Using Python: {python_exe}")

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, concat 
import chromadb
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from ingestion.embedding_generator import EmbeddingGenerator
from ingestion.batch_processor import BatchProcessor


class SparkChromaDBIngestion:
    """PySpark-based ingestion pipeline for ChromaDB"""
    
    def __init__(self, config: Config):
        self.config = config
        self.spark = None
        self.embedding_generator = None
        self.batch_processor = None
        self.chroma_client = None
        
    def initialize_spark(self):
        """Initialize Spark session"""
        print("🚀 Initializing Spark session...")
        
        self.spark = SparkSession.builder \
            .appName("ChromaDB_Ingestion") \
            .master(self.config.SPARK_MASTER) \
            .config("spark.driver.memory", "4g") \
            .config("spark.executor.memory", "4g") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "false") \
            .getOrCreate()
        
        # Set log level to reduce noise
        self.spark.sparkContext.setLogLevel("ERROR")
        
        print(f"✅ Spark session initialized: {self.spark.version}")
    
    def initialize_components(self):
        """Initialize embedding generator and ChromaDB"""
        print("🔧 Initializing components...")
        
        # Initialize embedding generator
        self.embedding_generator = EmbeddingGenerator(
            model_name=self.config.CLIP_MODEL_NAME,
            device=self.config.DEVICE,
            text_weight=self.config.TEXT_WEIGHT,
            image_weight=self.config.IMAGE_WEIGHT
        )
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=self.config.CHROMA_DB_DIR)
        
        # Initialize batch processor
        self.batch_processor = BatchProcessor(
            chroma_client=self.chroma_client,
            collection_name=self.config.COLLECTION_NAME,
            batch_size=self.config.BATCH_SIZE
        )
        
        print("✅ All components initialized")
    
    def get_disaster_type(self, filename: str) -> str:
        """Extract disaster type from filename"""
        name = filename.lower()
        if "wildfire" in name or "california" in name:
            return "Wildfire"
        elif "earthquake" in name or "mexico" in name:
            return "Earthquake"
        elif "flood" in name or "srilanka" in name:
            return "Flood"
        elif "hurricane" in name or "maria" in name:
            return "Hurricane"
        else:
            return "Other"
    
    def load_tsv_to_spark(self, tsv_path: str):
        """
        Load TSV file into Spark DataFrame
        
        Args:
            tsv_path: Path to TSV file
            
        Returns:
            Spark DataFrame
        """
        print(f"📄 Loading TSV file: {tsv_path}")
        
        if not os.path.exists(tsv_path):
            raise FileNotFoundError(f"TSV file not found: {tsv_path}")
        
        # Read TSV
        df = self.spark.read \
            .option("header", "true") \
            .option("sep", "\t") \
            .option("inferSchema", "true") \
            .csv(tsv_path)
        
        print(f"✅ Loaded {df.count()} rows from {os.path.basename(tsv_path)}")
        
        return df
    
    def prepare_data(self, df, source_file: str, disaster_type: str):
        """
        Prepare DataFrame for ingestion
        
        Args:
            df: Spark DataFrame
            source_file: Source filename
            disaster_type: Disaster type
            
        Returns:
            Prepared DataFrame with all required columns
        """
        print("🔧 Preparing data...")
        
        df = df.filter(
        (col("text_info") == "informative") &
        (col("image_info") == "informative")
        )
        
        # Add metadata columns
        df = df.withColumn("source_file", lit(source_file))
        df = df.withColumn("disaster_type", lit(disaster_type))
        
        # Build full image paths
        df = df.withColumn(
            "full_image_path",
            concat(lit(self.config.DATA_BASE_PATH + "/"), col("image_path"))
        )
        
        # Generate unique IDs
        df = df.withColumn(
            "doc_id",
            concat(lit(f"{source_file}_"), col("image_path"))
        )
        
        return df
    
    def ingest_file(self, tsv_path: str):
        """
        Complete ingestion pipeline for a single TSV file
        
        Args:
            tsv_path: Path to TSV file
            
        Returns:
            Dictionary with ingestion statistics
        """
        print(f"\n{'='*70}")
        print(f"🚀 Starting ingestion for: {os.path.basename(tsv_path)}")
        print(f"{'='*70}\n")
        
        # Extract metadata
        filename = os.path.basename(tsv_path)
        disaster_type = self.get_disaster_type(filename)
        
        print(f"📋 File: {filename}")
        print(f"🌋 Disaster Type: {disaster_type}")
        
        # Load data with Spark
        df = self.load_tsv_to_spark(tsv_path)
        
        
        # Prepare data
        df = self.prepare_data(df, filename, disaster_type)
        
        original_count = df.count()
        
        # Convert to Pandas immediately (skip distributed UDF processing)
        print("📥 Converting to Pandas for local processing...")
        pandas_df = df.select(
            "doc_id",
            "tweet_text", 
            "full_image_path",
            "extracted_locations",
            "source_file",
            "disaster_type"
        ).toPandas()
        
        print(f"✅ Converted {len(pandas_df)} rows to Pandas")
        
        # Generate embeddings locally (not distributed)
        print("\n🧩 Generating multimodal embeddings locally...")
        embeddings = []
        
        for _, row in tqdm(pandas_df.iterrows(), total=len(pandas_df), desc="Generating embeddings"):
            emb = self.embedding_generator.generate_multimodal_embedding(
                row['tweet_text'],
                row['full_image_path'],
                location=row['extracted_locations']
            )
            embeddings.append(emb)
        
        print(f"✅ Generated {len(embeddings)} embeddings")
        
        # Prepare for ChromaDB
        documents = pandas_df["tweet_text"].tolist()
        ids = pandas_df["doc_id"].tolist()
        metadatas = [
            {
                "source_file": row["source_file"],
                "disaster_type": row["disaster_type"],
                "image_path": row["full_image_path"],
                "extracted_location": str(row["extracted_locations"])
            }
            for _, row in pandas_df.iterrows()
        ]
        
        # Check for duplicates
        print("\n🔍 Checking for duplicate IDs...")
        existing_ids = self.batch_processor.check_duplicate_ids(ids)
        
        if existing_ids:
            print(f"⚠️ Found {len(existing_ids)} duplicate IDs. Skipping them...")
            # Filter out duplicates
            mask = [id not in existing_ids for id in ids]
            documents = [d for d, m in zip(documents, mask) if m]
            embeddings = [e for e, m in zip(embeddings, mask) if m]
            metadatas = [m for m, mask_val in zip(metadatas, mask) if mask_val]
            ids = [i for i, m in zip(ids, mask) if m]
        
        if not documents:
            print("ℹ️ No new documents to insert (all were duplicates)")
            return {
                "file": filename,
                "disaster_type": disaster_type,
                "total_rows": original_count,
                "successful_inserts": 0,
                "failed_inserts": 0,
                "success_rate": 0
            }
        
        print(f"\n📊 Inserting {len(documents)} new documents into ChromaDB...")
        
        # Insert in batches
        successful, failed = self.batch_processor.insert_all(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        # Summary
        stats = {
            "file": filename,
            "disaster_type": disaster_type,
            "total_rows": original_count,
            "successful_inserts": successful,
            "failed_inserts": failed,
            "success_rate": (successful / original_count * 100) if original_count > 0 else 0
        }
        
        print(f"\n{'='*70}")
        print(f"✅ Ingestion Complete!")
        print(f"{'='*70}")
        print(f"📊 Statistics:")
        print(f"   Total Rows: {stats['total_rows']}")
        print(f"   Skipped (duplicates): {len(existing_ids)}")
        print(f"   Successfully Inserted: {stats['successful_inserts']}")
        print(f"   Failed: {stats['failed_inserts']}")
        print(f"   Success Rate: {stats['success_rate']:.2f}%")
        
        return stats
    
    def cleanup(self):
        """Cleanup resources"""
        if self.spark:
            print("\n🧹 Stopping Spark session...")
            try:
                self.spark.stop()
                print("✅ Cleanup complete")
            except:
                pass


def main():
    """Main execution function"""
    # Initialize configuration
    config = Config()
    
    # Create ingestion pipeline
    pipeline = SparkChromaDBIngestion(config)
    
    try:
        # Initialize Spark and components
        pipeline.initialize_spark()
        pipeline.initialize_components()
        
        # Ingest the new hurricane data
        tsv_path = r"D:/Capstone_Prototype/CrisisMMD/annotations/hurricane_maria_with_captions_LRR.tsv"
        stats = pipeline.ingest_file(tsv_path)
        
        # Print final ChromaDB stats
        print("\n" + "="*70)
        print("📊 ChromaDB Collection Summary:")
        print("="*70)
        collection_stats = pipeline.batch_processor.get_collection_stats()
        print(f"Collection: {collection_stats['name']}")
        print(f"Total Documents: {collection_stats['count']}")
        
        print(f"\n✅ Successfully ingested {stats['successful_inserts']} new documents!")
        
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Cleanup
        pipeline.cleanup()
    
    return 0


if __name__ == "__main__":
    exit(main())