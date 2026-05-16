"""CLI script to ingest new TSV files into ChromaDB"""

import sys
import os
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from ingestion.spark_ingestion import SparkChromaDBIngestion


def main():
    parser = argparse.ArgumentParser(description="Ingest new crisis data into ChromaDB")
    parser.add_argument("tsv_file", help="Path to TSV file to ingest")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for insertion")
    parser.add_argument("--skip-duplicates", action="store_true", help="Skip duplicate IDs")
    
    args = parser.parse_args()
    
    # Validate file exists
    if not os.path.exists(args.tsv_file):
        print(f"❌ Error: File not found: {args.tsv_file}")
        sys.exit(1)
    
    # Load config
    config = Config()
    if args.batch_size:
        config.BATCH_SIZE = args.batch_size
    
    # Create pipeline
    pipeline = SparkChromaDBIngestion(config)
    
    try:
        # Initialize
        pipeline.initialize_spark()
        pipeline.initialize_components()
        
        # Ingest
        print(f"\n🚀 Ingesting file: {args.tsv_file}")
        stats = pipeline.ingest_file(args.tsv_file)
        
        # Success
        print(f"\n✅ Successfully ingested {stats['successful_inserts']} documents!")
        
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")
        sys.exit(1)
    
    finally:
        pipeline.cleanup()


if __name__ == "__main__":
    main()
