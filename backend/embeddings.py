"""
Embeddings Module
Handles text embedding generation using sentence-transformers or OpenAI
"""

import os
import logging
from typing import List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class EmbeddingProvider(str, Enum):
    """Embedding provider options"""
    LOCAL = "local"  # sentence-transformers
    OPENAI = "openai"  # OpenAI API


class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self, provider: EmbeddingProvider = EmbeddingProvider.LOCAL):
        """
        Initialize embedding service
        
        Args:
            provider: Which embedding provider to use
        """
        self.provider = provider
        self.model = None
        
        if provider == EmbeddingProvider.LOCAL:
            self._init_local()
        elif provider == EmbeddingProvider.OPENAI:
            self._init_openai()
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _init_local(self):
        """Initialize sentence-transformers model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use a fast, efficient model
            model_name = "all-MiniLM-L6-v2"  # 384 dimensions, fast
            # Alternative: "all-mpnet-base-v2"  # 768 dimensions, slower but better
            
            logger.info(f"Loading sentence-transformers model: {model_name}")
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = 384
            
            logger.info(f"✅ Local embeddings initialized ({self.embedding_dim}d)")
            
        except ImportError:
            logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
            raise
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            
            self.model = OpenAI(api_key=api_key)
            self.embedding_dim = 1536  # text-embedding-3-small
            
            logger.info(f"✅ OpenAI embeddings initialized ({self.embedding_dim}d)")
            
        except ImportError:
            logger.error("openai not installed. Run: pip install openai")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.embedding_dim
        
        if self.provider == EmbeddingProvider.LOCAL:
            return self._embed_local(text)
        elif self.provider == EmbeddingProvider.OPENAI:
            return self._embed_openai(text)
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batched for efficiency)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        if self.provider == EmbeddingProvider.LOCAL:
            return self._embed_local_batch(texts)
        elif self.provider == EmbeddingProvider.OPENAI:
            return self._embed_openai_batch(texts)
    
    def _embed_local(self, text: str) -> List[float]:
        """Generate embedding using sentence-transformers"""
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def _embed_local_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings in batch using sentence-transformers"""
        logger.info(f"Generating embeddings for {len(texts)} texts (local)")
        embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
        return embeddings.tolist()
    
    def _embed_openai(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        response = self.model.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def _embed_openai_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings in batch using OpenAI"""
        logger.info(f"Generating embeddings for {len(texts)} texts (OpenAI)")
        
        # OpenAI supports batch embedding
        response = self.model.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        
        # Return in same order as input
        return [item.embedding for item in response.data]


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(provider: Optional[EmbeddingProvider] = None) -> EmbeddingService:
    """
    Get or create embedding service singleton
    
    Args:
        provider: Provider to use (only used on first call)
        
    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    
    if _embedding_service is None:
        # Default to local if not specified
        if provider is None:
            provider = EmbeddingProvider.LOCAL
        
        _embedding_service = EmbeddingService(provider=provider)
    
    return _embedding_service


def embed_chunk_text(text: str, provider: Optional[EmbeddingProvider] = None) -> List[float]:
    """
    Convenience function to embed a single chunk text
    
    Args:
        text: Text to embed
        provider: Optional provider override
        
    Returns:
        Embedding vector
    """
    service = get_embedding_service(provider)
    return service.embed_text(text)


def embed_chunks_batch(texts: List[str], provider: Optional[EmbeddingProvider] = None) -> List[List[float]]:
    """
    Convenience function to embed multiple chunk texts
    
    Args:
        texts: List of texts to embed
        provider: Optional provider override
        
    Returns:
        List of embedding vectors
    """
    service = get_embedding_service(provider)
    return service.embed_batch(texts)
