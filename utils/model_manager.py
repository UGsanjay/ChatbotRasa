import logging
import numpy as np
import pandas as pd
import faiss
from typing import List
from sentence_transformers import SentenceTransformer
from config.model_config import MODEL_CONFIG
from utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)

class ModelManager:
    """Enhanced AI model operations with fallback and error handling"""
    
    def __init__(self):
        self.model = None
        self.model_name = None
        self.embed_dim = None
        self.load_model()
    
    def load_model(self):
        """Load sentence transformer model with enhanced fallback"""
        try:
            self.model = SentenceTransformer(MODEL_CONFIG['primary_model'])
            self.model_name = MODEL_CONFIG['primary_model']
            logger.info(f"Loaded primary model: {MODEL_CONFIG['primary_model']}")
        except Exception as e:
            logger.warning(f"Failed to load primary model, using backup: {e}")
            try:
                self.model = SentenceTransformer(MODEL_CONFIG['backup_model'])
                self.model_name = MODEL_CONFIG['backup_model']
                logger.info(f"Loaded backup model: {MODEL_CONFIG['backup_model']}")
            except Exception as e2:
                logger.error(f"Failed to load backup model: {e2}")
                raise Exception("Could not load any sentence transformer model")
        
        # Get embedding dimension
        try:
            self.embed_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model embedding dimension: {self.embed_dim}")
        except Exception as e:
            logger.error(f"Error getting embedding dimension: {e}")
            self.embed_dim = 384  # Default dimension
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings with enhanced preprocessing and error handling"""
        if not texts:
            logger.warning("No texts provided for embedding")
            return np.array([])
        
        try:
            processed_texts = []
            for text in texts:
                try:
                    if text and pd.notna(text):
                        clean_text = TextProcessor.preprocess_text(str(text))
                        expanded_text = TextProcessor.expand_with_synonyms(clean_text)
                        if expanded_text and expanded_text.strip():
                            processed_texts.append(expanded_text)
                        else:
                            processed_texts.append("makanan") 
                    else:
                        processed_texts.append("makanan")  
                except Exception as e:
                    logger.warning(f"Error preprocessing text: {e}")
                    processed_texts.append("makanan") 
            
            if not processed_texts:
                logger.warning("No valid texts after preprocessing")
                return np.array([])
            
            # Generate embeddings with normalization
            embeddings = self.model.encode(processed_texts, convert_to_numpy=True).astype(np.float32)
            faiss.normalize_L2(embeddings)
            
            logger.info(f"Generated enhanced embeddings for {len(processed_texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error embedding texts: {e}")
            return np.array([])
    
    def get_model_info(self) -> dict:
        """Get comprehensive information about the loaded model"""
        try:
            return {
                'model_name': self.model_name,
                'embedding_dimension': self.embed_dim,
                'model_loaded': self.model is not None,
                'model_type': 'SentenceTransformer',
                'supports_multilingual': True,
                'optimized_for': 'semantic_search'
            }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {
                'model_name': 'unknown',
                'embedding_dimension': 0,
                'model_loaded': False,
                'error': str(e)
            }
    
    def is_model_ready(self) -> bool:
        """Check if model is properly loaded and ready"""
        return self.model is not None and self.embed_dim is not None