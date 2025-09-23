"""
ML Model Loader - Handles loading and caching of Hugging Face models
"""
import torch
from transformers import (
    AutoTokenizer,
    AutoModel,
    AutoModelForQuestionAnswering,
    AutoModelForCausalLM,
    pipeline,
    logging as transformers_logging
)
import logging
from typing import Dict, Any, Optional
import os
from pathlib import Path
import time

from app.config import settings, ML_MODELS

# Set transformers logging level
transformers_logging.set_verbosity_error()

logger = logging.getLogger(__name__)

class ModelLoader:
    """Singleton class for loading and managing ML models"""
    
    _instance = None
    _models: Dict[str, Any] = {}
    _tokenizers: Dict[str, Any] = {}
    _pipelines: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.device = self._setup_device()
        self.cache_dir = Path(settings.model_cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Model loader initialized with device: {self.device}")
    
    def _setup_device(self) -> str:
        """Setup computation device (GPU/CPU)"""
        if settings.use_gpu and torch.cuda.is_available():
            device = "cuda"
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            logger.info("Using CPU for inference")
        return device
    
    def load_model(self, model_key: str, force_reload: bool = False) -> Dict[str, Any]:
        """Load a model by its key from ML_MODELS config"""
        if model_key in self._models and not force_reload:
            logger.info(f"Model {model_key} already loaded")
            return {
                "model": self._models[model_key],
                "tokenizer": self._tokenizers[model_key],
                "pipeline": self._pipelines.get(model_key)
            }
        
        if model_key not in ML_MODELS:
            raise ValueError(f"Unknown model key: {model_key}")
        
        model_config = ML_MODELS[model_key]
        model_name = model_config["name"]
        task = model_config["task"]
        
        logger.info(f"Loading model: {model_name}")
        start_time = time.time()
        
        try:
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=self.cache_dir,
                token=settings.huggingface_token
            )
            self._tokenizers[model_key] = tokenizer
            
            # Load model based on task
            if task == "feature-extraction":
                model = AutoModel.from_pretrained(
                    model_name,
                    cache_dir=self.cache_dir,
                    token=settings.huggingface_token
                )
            elif task == "question-answering":
                model = AutoModelForQuestionAnswering.from_pretrained(
                    model_name,
                    cache_dir=self.cache_dir,
                    token=settings.huggingface_token
                )
            elif task == "text-generation":
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    cache_dir=self.cache_dir,
                    token=settings.huggingface_token,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
            else:
                # Use pipeline for other tasks
                pipe = pipeline(
                    task,
                    model=model_name,
                    device=0 if self.device == "cuda" else -1,
                    model_kwargs={"cache_dir": self.cache_dir}
                )
                self._pipelines[model_key] = pipe
                self._models[model_key] = None
                
                load_time = time.time() - start_time
                logger.info(f"Model {model_name} loaded in {load_time:.2f} seconds")
                
                return {
                    "model": None,
                    "tokenizer": tokenizer,
                    "pipeline": pipe
                }
            
            # Move model to device
            if model:
                model = model.to(self.device)
                model.eval()  # Set to evaluation mode
                self._models[model_key] = model
            
            # Create pipeline if needed
            if task in ["question-answering", "text-generation"]:
                pipe = pipeline(
                    task,
                    model=model,
                    tokenizer=tokenizer,
                    device=0 if self.device == "cuda" else -1,
                    max_length=settings.max_length
                )
                self._pipelines[model_key] = pipe
            
            load_time = time.time() - start_time
            logger.info(f"Model {model_name} loaded in {load_time:.2f} seconds")
            
            return {
                "model": self._models[model_key],
                "tokenizer": self._tokenizers[model_key],
                "pipeline": self._pipelines.get(model_key)
            }
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            raise
    
    def preload_all_models(self):
        """Preload all configured models"""
        logger.info("Preloading all models...")
        for model_key in ML_MODELS.keys():
            try:
                self.load_model(model_key)
            except Exception as e:
                logger.error(f"Failed to load model {model_key}: {e}")
    
    def get_model(self, model_key: str) -> Optional[Any]:
        """Get a loaded model"""
        return self._models.get(model_key)
    
    def get_tokenizer(self, model_key: str) -> Optional[Any]:
        """Get a loaded tokenizer"""
        return self._tokenizers.get(model_key)
    
    def get_pipeline(self, model_key: str) -> Optional[Any]:
        """Get a loaded pipeline"""
        return self._pipelines.get(model_key)
    
    def clear_cache(self):
        """Clear model cache"""
        self._models.clear()
        self._tokenizers.clear()
        self._pipelines.clear()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Model cache cleared")

# Create singleton instance
model_loader = ModelLoader()