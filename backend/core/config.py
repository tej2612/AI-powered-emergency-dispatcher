"""Core configuration — Pydantic Settings (replaces old config.py)."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    """
    All settings are loaded from environment variables or a .env file.
    Uppercase @property aliases allow the copied model code (which
    references Config.DEVICE, Config.TOP_K, etc.) to work without
    any modification.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    chroma_db_dir: str = r"D:/Capstone_Prototype/ChromaDB/chromadb_store_multimodal"
    collection_name: str = "crisis_multimodal"

    # ── Model paths ──────────────────────────────────────────────────────────
    lora_model_path: str = "D:/Capstone_Prototype/models/lora_model2"
    image_base_path: str = "D:/Capstone_Prototype/CrisisMMD/data_image"
    data_base_path: str = r"D:/Capstone_Prototype/CrisisMMD"

    # ── Model names ──────────────────────────────────────────────────────────
    clip_model_name: str = "clip-ViT-B-32"
    dispatcher_model_name: str = "google/flan-t5-base"

    # ── Gemini / web search ──────────────────────────────────────────────────
    use_gemini_for_dispatcher: bool = True
    gemini_model_name: str = "gemini-2.5-flash"
    google_api_key: str = ""
    gemini_api_key: str = ""
    tavily_api_key: str = ""
    enable_web_search: bool = True
    search_max_results: int = 5

    # ── Application behaviour ────────────────────────────────────────────────
    top_k: int = 5
    max_item_chars: int = 400
    history_turns: int = 6

    # ── Ingestion / Spark ────────────────────────────────────────────────────
    batch_size: int = 100
    spark_master: str = "local[*]"
    spark_driver_memory: str = "4g"
    spark_executor_memory: str = "4g"
    text_weight: float = 0.7
    image_weight: float = 0.2
    location_weight: float = 0.1
    max_retries: int = 3
    checkpoint_dir: str = "ingestion_checkpoints"

    # ── Server ───────────────────────────────────────────────────────────────
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True

    # ── Runtime-computed (not from .env) ─────────────────────────────────────
    device: str = ""

    @model_validator(mode="after")
    def _post_init(self) -> "Settings":
        # Auto-detect CUDA
        if not self.device:
            try:
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self.device = "cpu"

        # Windows Spark env vars
        if os.name == "nt":
            os.environ.setdefault("HADOOP_HOME", r"C:/hadoop")

        return self

    # ── Legacy uppercase shims (keep copied model code working verbatim) ──────
    @property
    def BASE_DIR(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @property
    def CHROMA_DB_DIR(self) -> str:
        return self.chroma_db_dir

    @property
    def COLLECTION_NAME(self) -> str:
        return self.collection_name

    @property
    def LORA_MODEL_PATH(self) -> str:
        return self.lora_model_path

    @property
    def IMAGE_BASE_PATH(self) -> str:
        return self.image_base_path

    @property
    def DATA_BASE_PATH(self) -> str:
        return self.data_base_path

    @property
    def ANNOTATIONS_DIR(self) -> str:
        return os.path.join(self.data_base_path, "annotations")

    @property
    def CLIP_MODEL_NAME(self) -> str:
        return self.clip_model_name

    @property
    def DISPATCHER_MODEL_NAME(self) -> str:
        return self.dispatcher_model_name

    @property
    def USE_GEMINI_FOR_DISPATCHER(self) -> bool:
        return self.use_gemini_for_dispatcher

    @property
    def GEMINI_MODEL_NAME(self) -> str:
        return self.gemini_model_name

    @property
    def GOOGLE_API_KEY(self) -> str:
        return self.google_api_key

    @property
    def GEMINI_API_KEY(self) -> str:
        return self.gemini_api_key

    @property
    def TAVILY_API_KEY(self) -> str:
        return self.tavily_api_key

    @property
    def ENABLE_WEB_SEARCH(self) -> bool:
        return self.enable_web_search

    @property
    def SEARCH_MAX_RESULTS(self) -> int:
        return self.search_max_results

    @property
    def TOP_K(self) -> int:
        return self.top_k

    @property
    def MAX_ITEM_CHARS(self) -> int:
        return self.max_item_chars

    @property
    def HISTORY_TURNS(self) -> int:
        return self.history_turns

    @property
    def BATCH_SIZE(self) -> int:
        return self.batch_size

    @property
    def SPARK_MASTER(self) -> str:
        return self.spark_master

    @property
    def SPARK_DRIVER_MEMORY(self) -> str:
        return self.spark_driver_memory

    @property
    def SPARK_EXECUTOR_MEMORY(self) -> str:
        return self.spark_executor_memory

    @property
    def TEXT_WEIGHT(self) -> float:
        return self.text_weight

    @property
    def IMAGE_WEIGHT(self) -> float:
        return self.image_weight

    @property
    def LOCATION_WEIGHT(self) -> float:
        return self.location_weight

    @property
    def MAX_RETRIES(self) -> int:
        return self.max_retries

    @property
    def CHECKPOINT_DIR(self) -> str:
        return self.checkpoint_dir

    @property
    def DEVICE(self) -> str:
        return self.device

    # Flask-compat aliases (referenced nowhere in new code, kept for safety)
    @property
    def FLASK_HOST(self) -> str:
        return self.host

    @property
    def FLASK_PORT(self) -> int:
        return self.port

    @property
    def DEBUG(self) -> bool:
        return self.debug


# Module-level singleton — import this everywhere
settings = Settings()
