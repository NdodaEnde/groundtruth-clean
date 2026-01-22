"""
Vector Store Module - Qdrant Backend
Handles Qdrant operations for document chunk storage and retrieval
Uses qdrant-client (no SQLite dependency issues)
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)


class VectorStore:
    """Qdrant wrapper for storing and retrieving document chunks with grounding"""
    
    def __init__(self, persist_directory: str = "./qdrant_db"):
        """Initialize Qdrant client"""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize Qdrant in local mode (no server needed)
        self.client = QdrantClient(path=str(self.persist_directory))
        self.collection_name = "groundtruth_chunks"
        self.vector_size = 384  # for all-MiniLM-L6-v2
        
        # Create collection if it doesn't exist
        try:
            self.client.get_collection(self.collection_name)
            logger.info(f"✅ Vector store loaded from {self.persist_directory}")
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Vector store created at {self.persist_directory}")
        
        # Get count
        info = self.client.get_collection(self.collection_name)
        logger.info(f"📊 Current collection size: {info.points_count} chunks")
    
    def add_document_chunks(
        self,
        doc_id: str,
        chunks: List[Dict],
        embeddings: List[List[float]]
    ) -> int:
        """Add document chunks to vector store"""
        if not chunks or not embeddings:
            logger.warning(f"No chunks or embeddings provided for doc {doc_id}")
            return 0
        
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) count mismatch")
        
        # Prepare points for Qdrant
        points = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = chunk.get('chunk_id', f"{doc_id}_chunk_{i}")
            text = chunk.get('text', '')
            
            # Build payload (metadata)
            payload = {
                'doc_id': doc_id,
                'chunk_id': chunk_id,
                'chunk_type': chunk.get('chunk_type', 'text'),
                'page': chunk.get('page', 0),
                'text': text  # Store text in payload
            }
            
            # Add grounding box if available
            if chunk.get('grounding') and chunk['grounding'].get('box'):
                box = chunk['grounding']['box']
                payload.update({
                    'box_left': box.get('left', 0),
                    'box_top': box.get('top', 0),
                    'box_right': box.get('right', 0),
                    'box_bottom': box.get('bottom', 0),
                })
            
            # Create point
            point = PointStruct(
                id=hash(chunk_id) & 0x7FFFFFFF,  # Convert to positive int
                vector=embedding,
                payload=payload
            )
            points.append(point)
        
        # Upsert to collection
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        logger.info(f"✅ Added {len(chunks)} chunks from document {doc_id} to vector store")
        return len(chunks)
    
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        doc_id: Optional[str] = None,
        chunk_type: Optional[str] = None
    ) -> Dict:
        """Query vector store for similar chunks"""
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Build filter
        must_conditions = []
        if doc_id:
            must_conditions.append(
                FieldCondition(key="doc_id", match=MatchValue(value=doc_id))
            )
        if chunk_type:
            must_conditions.append(
                FieldCondition(key="chunk_type", match=MatchValue(value=chunk_type))
            )
        
        query_filter = Filter(must=must_conditions) if must_conditions else None
        
        # Search using correct Qdrant method
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=n_results,
            query_filter=query_filter,
            with_payload=True
        )
        
        # Format results (match ChromaDB format)
        formatted_results = {
            'ids': [point.payload['chunk_id'] for point in results.points],
            'documents': [point.payload['text'] for point in results.points],
            'metadatas': [point.payload for point in results.points],
            'distances': [1.0 - point.score for point in results.points]
        }
        
        return formatted_results
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict]:
        """Get a specific chunk by ID"""
        # Qdrant uses numeric IDs, so we need to search by chunk_id in payload
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter={
                "must": [{"key": "chunk_id", "match": {"value": chunk_id}}]
            },
            limit=1
        )
        
        if results[0]:
            point = results[0][0]
            return {
                'chunk_id': point.payload['chunk_id'],
                'text': point.payload['text'],
                'metadata': point.payload
            }
        return None
    
    def delete_document(self, doc_id: str) -> int:
        """Delete all chunks for a document"""
        try:
            # Get all points for this document
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter={
                    "must": [{"key": "doc_id", "match": {"value": doc_id}}]
                },
                limit=10000
            )
            
            if results:
                # Delete by IDs
                ids = [p.id for p in results]
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector={"points": ids}
                )
                logger.info(f"🗑️ Deleted {len(ids)} chunks from document {doc_id}")
                return len(ids)
            
            return 0
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return 0
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        info = self.client.get_collection(self.collection_name)
        
        # Get all unique doc_ids
        all_points, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=10000,
            with_payload=True,
            with_vectors=False
        )
        
        doc_ids = set(p.payload.get('doc_id') for p in all_points if p.payload.get('doc_id'))
        
        return {
            'total_chunks': info.points_count,
            'total_documents': len(doc_ids),
            'collection_name': self.collection_name,
            'persist_directory': str(self.persist_directory)
        }
    
    def clear_all(self):
        """Clear all data from vector store"""
        self.client.delete_collection(self.collection_name)
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE
            )
        )
        logger.warning("⚠️ Vector store cleared!")


# Access to collection attribute for compatibility
class QdrantCollectionWrapper:
    def __init__(self, client, collection_name):
        self.client = client
        self.name = collection_name
    
    def get(self, **kwargs):
        """Compatibility method for ChromaDB-style get"""
        where = kwargs.get('where', {})
        
        must_conditions = []
        for key, value in where.items():
            must_conditions.append({
                "key": key,
                "match": {"value": value}
            })
        
        query_filter = {"must": must_conditions} if must_conditions else None
        
        results, _ = self.client.scroll(
            collection_name=self.name,
            scroll_filter=query_filter,
            limit=kwargs.get('limit', 10000),
            with_payload=True
        )
        
        return {
            'ids': [p.payload.get('chunk_id', str(p.id)) for p in results],
            'documents': [p.payload.get('text', '') for p in results],
            'metadatas': [p.payload for p in results]
        }


# Add collection property to VectorStore
VectorStore.collection = property(lambda self: QdrantCollectionWrapper(self.client, self.collection_name))


# Singleton instance
_vector_store = None

def get_vector_store() -> VectorStore:
    """Get or create vector store singleton"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
