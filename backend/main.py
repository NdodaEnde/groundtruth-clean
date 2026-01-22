"""
GroundTruth Backend - Transport Client Edition
Multi-tenant document processing with Supabase + LandingAI ADE
Features: Upload → Parse → Extract → Validate → Approve → RAG Search
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

import uuid
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Vector store and embeddings
from vector_store import get_vector_store
from embeddings import get_embedding_service, EmbeddingProvider

# Configure logging AFTER dotenv
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# LandingAI imports
try:
    from landingai_ade import LandingAIADE
    from landingai_ade.lib import pydantic_to_json_schema
    AGENTIC_DOC_AVAILABLE = True
    logger.info("✅ LandingAI landingai_ade module loaded successfully")
except ImportError as e:
    AGENTIC_DOC_AVAILABLE = False
    logger.error(f"❌ LandingAI landingai_ade not available: {e}")
    logger.error("Install with: pip install landingai-ade")
    sys.exit(1)

# Supabase imports
try:
    from supabase_client import DocumentDB, TransportIncidentDB, supabase
    SUPABASE_AVAILABLE = True
    logger.info("✅ Supabase client loaded successfully")
except ImportError as e:
    SUPABASE_AVAILABLE = False
    logger.warning(f"⚠️ Supabase client not available: {e}")
    logger.warning("Multi-tenant features disabled. Run: pip install supabase")

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """Application configuration"""
    # LandingAI settings
    LANDING_AI_API_KEY = os.getenv("LANDING_AI_API_KEY")
    VISION_AGENT_API_KEY = os.getenv("VISION_AGENT_API_KEY")
    
    # Supabase settings
    ORGANIZATION_ID = os.getenv("ORGANIZATION_ID")
    
    # Application settings
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}
    
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))

# Verify API keys
if not Config.LANDING_AI_API_KEY and not Config.VISION_AGENT_API_KEY:
    logger.error("❌ No API key found. Set LANDING_AI_API_KEY or VISION_AGENT_API_KEY in .env")
    sys.exit(1)

if SUPABASE_AVAILABLE and not Config.ORGANIZATION_ID:
    logger.warning("⚠️ ORGANIZATION_ID not set - multi-tenant features may not work")

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="GroundTruth API - Transport Edition",
    version="2.0.0",
    description="Multi-tenant document processing with validation workflow"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
BASE_DIR = Path(__file__).parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# Persistent document store (JSON file - backup)
DOCUMENT_INDEX_PATH = Path("./document_index.json")

def load_document_store() -> Dict[str, dict]:
    """Load document index from disk"""
    if DOCUMENT_INDEX_PATH.exists():
        try:
            with open(DOCUMENT_INDEX_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading document index: {e}")
            return {}
    return {}

def save_document_store(store: Dict[str, dict]):
    """Save document index to disk"""
    try:
        with open(DOCUMENT_INDEX_PATH, 'w') as f:
            json.dump(store, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error saving document index: {e}")

# Load document store on startup
documents_store: Dict[str, dict] = load_document_store()
logger.info(f"📂 Loaded {len(documents_store)} documents from index")

# Initialize LandingAI client
landing_client = LandingAIADE()

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class DocumentResponse(BaseModel):
    doc_id: str
    filename: str
    upload_time: str
    status: str
    num_chunks: Optional[int] = None
    indexed: Optional[bool] = None
    indexed_chunks: Optional[int] = None

class ChunkResponse(BaseModel):
    chunks: List[dict]

# === Extraction Schema Models ===

class DriverInfo(BaseModel):
    driver_name: Optional[str] = Field(None, description="Full name of the driver")
    driver_id: Optional[str] = Field(None, description="Driver's SA ID number (13 digits)")
    license_number: Optional[str] = Field(None, description="Driver's license number")
    vehicle_registration: Optional[str] = Field(None, description="Vehicle registration number (e.g., ABC123GP)")
    vehicle_type: Optional[str] = Field(None, description="Type of vehicle (truck, van, car, bakkie, etc.)")

class IncidentDetails(BaseModel):
    incident_date: Optional[str] = Field(None, description="Date of incident in YYYY-MM-DD format")
    incident_time: Optional[str] = Field(None, description="Time of incident in HH:MM 24-hour format")
    location: Optional[str] = Field(None, description="Location/address where incident occurred")
    gps_coordinates: Optional[str] = Field(None, description="GPS coordinates if available")
    incident_type: Optional[str] = Field(None, description="Type: accident, breakdown, theft, damage, traffic_violation, other")
    description: Optional[str] = Field(None, description="Detailed description of what happened")

class DamageAssessment(BaseModel):
    vehicle_damage: Optional[str] = Field(None, description="Description of damage to company vehicle")
    third_party_damage: Optional[str] = Field(None, description="Description of damage to third party property/vehicles")
    estimated_cost: Optional[float] = Field(None, description="Estimated repair cost in South African Rands")

class Injuries(BaseModel):
    injuries_reported: Optional[str] = Field(None, description="Were there any injuries? Answer: yes or no")
    injury_details: Optional[str] = Field(None, description="Details of injuries sustained (if any)")
    medical_attention: Optional[str] = Field(None, description="Was medical attention required? Answer: yes or no")

class WitnessInfo(BaseModel):
    name: Optional[str] = Field(None, description="Witness full name")
    contact: Optional[str] = Field(None, description="Witness contact number")
    statement: Optional[str] = Field(None, description="Witness statement about incident")

class Witnesses(BaseModel):
    witness_present: Optional[str] = Field(None, description="Were there witnesses? Answer: yes or no")
    witness_details: Optional[List[WitnessInfo]] = Field(None, description="List of witness information")

class AdditionalInfo(BaseModel):
    police_reported: Optional[str] = Field(None, description="Was incident reported to police? Answer: yes or no")
    case_number: Optional[str] = Field(None, description="Police case number or reference")
    police_station: Optional[str] = Field(None, description="Police station where reported")
    notes: Optional[str] = Field(None, description="Any additional notes or observations")

class TransportIncidentExtraction(BaseModel):
    """Complete schema for transport incident report extraction"""
    driver_info: Optional[DriverInfo] = Field(None, description="Information about the driver involved")
    incident_details: Optional[IncidentDetails] = Field(None, description="Details about the incident")
    damage_assessment: Optional[DamageAssessment] = Field(None, description="Assessment of damages and costs")
    injuries: Optional[Injuries] = Field(None, description="Information about any injuries")
    witnesses: Optional[Witnesses] = Field(None, description="Witness information if applicable")
    additional_info: Optional[AdditionalInfo] = Field(None, description="Additional incident information")

# === RAG Models ===

class IngestRequest(BaseModel):
    doc_id: str
    force: bool = False

class IngestResponse(BaseModel):
    doc_id: str
    chunks_indexed: int
    status: str
    message: str

class QueryRequest(BaseModel):
    query: str
    n_results: int = 5
    doc_id: Optional[str] = None
    chunk_type: Optional[str] = None

class SearchResult(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    page: int
    chunk_type: str
    similarity_score: float
    grounding: Optional[dict] = None

class QueryResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int

class VectorStoreStats(BaseModel):
    total_chunks: int
    total_documents: int
    indexed_doc_ids: List[str]

# === Q&A Models ===

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    conversation_history: Optional[List[ChatMessage]] = []
    n_results: int = 5

class SourceReference(BaseModel):
    doc_id: str
    chunk_id: str
    filename: Optional[str] = None
    page: int
    chunk_type: str
    text: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceReference]

# =============================================================================
# DOCUMENT PROCESSOR
# =============================================================================

class DocumentProcessor:
    """Document processor using landingai_ade"""
    
    def __init__(self):
        self.client = LandingAIADE()
        logger.info("✅ Document Processor initialized")
    
    def process_document(self, file_path: str) -> Dict:
        """Process document using landingai_ade"""
        
        logger.info(f"📄 Processing: {Path(file_path).name}")
        start_time = datetime.utcnow()
        
        try:
            from pathlib import Path as PathlibPath
            
            response = self.client.parse(
                document=PathlibPath(file_path),
                model="dpt-2-latest"
            )
            
            if not response or not response.chunks:
                return {
                    'success': False,
                    'error': 'No data extracted from document',
                    'file_path': file_path
                }
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Convert response to serializable format
            parsed_data = {
                'chunks': [chunk.model_dump() for chunk in response.chunks],
                'markdown': response.markdown,
                'metadata': response.metadata.model_dump() if hasattr(response, 'metadata') else {},
                'grounding': {k: v.model_dump() for k, v in response.grounding.items()} if hasattr(response, 'grounding') else {}
            }
            
            num_chunks = len(response.chunks)
            
            logger.info(f"✅ Extraction complete! Found {num_chunks} chunks in {processing_time:.2f}s")
            
            return {
                'success': True,
                'parsed_data': parsed_data,
                'num_chunks': num_chunks,
                'processing_time': round(processing_time, 2),
                'file_path': file_path
            }
            
        except Exception as e:
            logger.error(f"❌ landingai_ade extraction failed: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f'Extraction failed: {str(e)}',
                'file_path': file_path
            }

# Initialize processor
processor = DocumentProcessor()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_modifications(original: dict, validated: dict, path: str = "") -> List[dict]:
    """Calculate what was changed during human validation"""
    modifications = []
    
    def compare(orig, val, prefix=""):
        if isinstance(orig, dict) and isinstance(val, dict):
            for key in set(list(orig.keys()) + list(val.keys())):
                current_path = f"{prefix}.{key}" if prefix else key
                compare(orig.get(key), val.get(key), current_path)
        elif orig != val:
            modifications.append({
                "field": prefix,
                "original": orig,
                "validated": val,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    compare(original, validated)
    return modifications

async def index_validated_data(doc_id: str, validated_data: dict):
    """Index validated data in Qdrant for RAG search"""
    
    from vector_store import get_vector_store
    from embeddings import get_embedding_service
    
    chunks = []
    
    # Driver info chunk
    driver_info = validated_data.get('driver_info', {})
    if driver_info and any(driver_info.values()):
        text = f"Driver: {driver_info.get('driver_name', 'Unknown')} (ID: {driver_info.get('driver_id', 'N/A')}). Vehicle: {driver_info.get('vehicle_registration', 'N/A')}"
        chunks.append({'text': text, 'type': 'driver_info', 'metadata': driver_info})
    
    # Incident details chunk
    incident = validated_data.get('incident_details', {})
    if incident and any(incident.values()):
        text = f"Incident on {incident.get('incident_date', 'unknown date')} at {incident.get('incident_time', 'unknown time')} in {incident.get('location', 'unknown location')}. Type: {incident.get('incident_type', 'unspecified')}. Description: {incident.get('description', 'No description')}"
        chunks.append({'text': text, 'type': 'incident', 'metadata': incident})
    
    # Damage chunk
    damage = validated_data.get('damage_assessment', {})
    if damage and any(damage.values()):
        text = f"Vehicle damage: {damage.get('vehicle_damage', 'None reported')}. Third party damage: {damage.get('third_party_damage', 'None reported')}. Estimated cost: R{damage.get('estimated_cost', 0)}"
        chunks.append({'text': text, 'type': 'damage', 'metadata': damage})
    
    if not chunks:
        logger.warning(f"⚠️ No data to index for document: {doc_id}")
        return
    
    embedding_service = get_embedding_service()
    vector_store = get_vector_store()
    
    qdrant_ids = []
    
    for idx, chunk in enumerate(chunks):
        try:
            embedding = embedding_service.embed_text(chunk['text'])
            chunk_id = f"{doc_id}-validated-{idx}"
            
            vector_store.add(
                embedding=embedding,
                document=chunk['text'],
                metadata={
                    'doc_id': doc_id,
                    'chunk_id': chunk_id,
                    'chunk_type': chunk['type'],
                    'organization_id': Config.ORGANIZATION_ID,
                    'product_type': 'groundtruth_transport',
                    **chunk['metadata']
                }
            )
            
            qdrant_ids.append(chunk_id)
            
        except Exception as e:
            logger.error(f"Error indexing chunk {idx}: {e}")
    
    logger.info(f"✅ Indexed {len(qdrant_ids)} chunks for document: {doc_id}")

# =============================================================================
# API ENDPOINTS - BASIC
# =============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "app": "GroundTruth API - Transport Edition",
        "version": "2.0.0",
        "status": "running",
        "features": {
            "landingai": AGENTIC_DOC_AVAILABLE,
            "supabase": SUPABASE_AVAILABLE
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "GroundTruth Transport Document Processor",
        "version": "2.0.0",
        "landingai_available": AGENTIC_DOC_AVAILABLE,
        "supabase_available": SUPABASE_AVAILABLE,
        "organization_id": Config.ORGANIZATION_ID if SUPABASE_AVAILABLE else None
    }

# =============================================================================
# API ENDPOINTS - DOCUMENT WORKFLOW
# =============================================================================

@app.post("/api/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Step 1: Upload and parse document
    Saves to Supabase with status tracking
    """
    
    if not AGENTIC_DOC_AVAILABLE:
        raise HTTPException(status_code=500, detail="landingai_ade not available")
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if file_ext not in Config.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type .{file_ext} not allowed")
    
    # Generate document ID
    doc_id = str(uuid.uuid4())
    
    # Create output directory
    doc_dir = OUTPUTS_DIR / doc_id
    doc_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file
    file_path = doc_dir / f"{doc_id}.{file_ext}"
    
    try:
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        logger.info(f"📄 Saved file: {file_path}")
        
        # Create document record in Supabase
        if SUPABASE_AVAILABLE and Config.ORGANIZATION_ID:
            DocumentDB.create(
                org_id=Config.ORGANIZATION_ID,
                filename=file.filename,
                file_path=str(file_path),
                document_type='transport_incident_report'
            )
            DocumentDB.update(doc_id, status='parsing')
        
        # Parse with LandingAI
        result = processor.process_document(str(file_path))
        
        if not result.get('success'):
            if SUPABASE_AVAILABLE:
                DocumentDB.update(doc_id, status='parse_failed')
            shutil.rmtree(doc_dir)
            raise HTTPException(status_code=500, detail=result.get('error', 'Processing failed'))
        
        # Save parsed results
        metadata_path = doc_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(result['parsed_data'], f, indent=2, default=str)
        
        # Update Supabase
        if SUPABASE_AVAILABLE and Config.ORGANIZATION_ID:
            DocumentDB.update(
                doc_id,
                status='parsed',
                parsed_json=result['parsed_data']['chunks'],
                parsed_markdown=result['parsed_data']['markdown']
            )
        
        # Store in memory
        doc_info = {
            "doc_id": doc_id,
            "filename": file.filename,
            "upload_time": datetime.utcnow().isoformat(),
            "status": "parsed",
            "num_chunks": result.get('num_chunks', 0),
            "file_path": str(file_path),
            "metadata_path": str(metadata_path)
        }
        
        documents_store[doc_id] = doc_info
        save_document_store(documents_store)
        
        logger.info(f"✅ Document processed: {doc_id}")
        
        # Auto-index for RAG
        try:
            logger.info(f"🔍 Auto-indexing document: {doc_id}")
            
            texts = []
            cleaned_chunks = []
            
            for i, chunk in enumerate(result['parsed_data']['chunks']):
                grounding_obj = chunk.get("grounding", {})
                page = grounding_obj.get("page", 0)
                box = grounding_obj.get("box", {})
                text = chunk.get("markdown", "")
                
                cleaned_chunk = {
                    "chunk_id": chunk.get("id", f"{doc_id}_chunk_{i}"),
                    "chunk_type": chunk.get("type", "text"),
                    "text": text,
                    "page": page,
                    "grounding": {
                        "page": page,
                        "box": box
                    } if box else None
                }
                
                texts.append(text)
                cleaned_chunks.append(cleaned_chunk)
            
            embedding_service = get_embedding_service()
            embeddings = embedding_service.embed_batch(texts)
            
            vector_store = get_vector_store()
            vector_store.delete_document(doc_id)
            chunks_added = vector_store.add_document_chunks(
                doc_id=doc_id,
                chunks=cleaned_chunks,
                embeddings=embeddings
            )
            
            logger.info(f"✅ Auto-indexed {chunks_added} chunks")
            doc_info["indexed"] = True
            doc_info["indexed_chunks"] = chunks_added
            
            if SUPABASE_AVAILABLE:
                DocumentDB.update(
                    doc_id,
                    indexed_at=datetime.utcnow().isoformat(),
                    qdrant_ids=[c["chunk_id"] for c in cleaned_chunks]
                )
            
        except Exception as index_error:
            logger.warning(f"⚠️ Auto-indexing failed: {index_error}")
            doc_info["indexed"] = False
        
        documents_store[doc_id] = doc_info
        save_document_store(documents_store)
        
        return DocumentResponse(**doc_info)
        
    except HTTPException:
        raise
    except Exception as e:
        if doc_dir.exists():
            shutil.rmtree(doc_dir)
        
        logger.error(f"❌ Error processing document: {e}")
        
        if SUPABASE_AVAILABLE:
            try:
                DocumentDB.update(doc_id, status='failed')
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@app.post("/api/extract")
async def extract_document_data(doc_id: str):
    """
    Step 2: Extract structured data using LandingAI ADE Extract
    Converts parsed markdown into structured fields
    """
    
    try:
        # Get document from Supabase or memory
        doc = None
        if SUPABASE_AVAILABLE:
            doc = DocumentDB.get(doc_id)
        
        if not doc and doc_id in documents_store:
            # Fallback to memory store
            doc_info = documents_store[doc_id]
            metadata_path = Path(doc_info.get('metadata_path', ''))
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    parsed_data = json.load(f)
                doc = {
                    'id': doc_id,
                    'status': doc_info.get('status', 'parsed'),
                    'parsed_markdown': parsed_data.get('markdown')
                }
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if doc['status'] not in ['parsed', 'extracted']:
            raise HTTPException(
                status_code=400,
                detail=f"Document must be parsed first. Current status: {doc['status']}"
            )
        
        # Get markdown for extraction
        markdown = doc.get('parsed_markdown')
        if not markdown:
            raise HTTPException(status_code=400, detail="No parsed markdown available")
        
        logger.info(f"🔍 Extracting structured data from document: {doc_id}")
        
        # Update status
        if SUPABASE_AVAILABLE:
            DocumentDB.update(doc_id, status='extracting')
        
        # Convert schema
        schema = pydantic_to_json_schema(TransportIncidentExtraction)
        
        # Extract using LandingAI ADE
        extract_response = landing_client.extract(
            schema=schema,
            markdown=markdown,
            model="extract-latest"
        )
        
        extracted_data = extract_response.extraction
        
        # Save extracted data
        if SUPABASE_AVAILABLE:
            DocumentDB.update(
                doc_id,
                status='extracted',
                extracted_json=extracted_data
            )
        
        logger.info(f"✅ Data extracted successfully: {doc_id}")
        
        return {
            "doc_id": doc_id,
            "status": "extracted",
            "extracted_data": extracted_data,
            "message": "Document ready for validation"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Extraction error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        if SUPABASE_AVAILABLE:
            try:
                DocumentDB.update(doc_id, status='extraction_failed')
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.post("/api/validate")
async def validate_document(doc_id: str, validated_data: dict, validated_by: str = "demo_user"):
    """
    Step 3: Save human-validated data
    Tracks modifications for ML training
    """
    
    try:
        doc = DocumentDB.get(doc_id) if SUPABASE_AVAILABLE else None
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if doc['status'] != 'extracted':
            raise HTTPException(
                status_code=400,
                detail=f"Document must be extracted first. Current status: {doc['status']}"
            )
        
        # Calculate modifications
        extracted_json = doc.get('extracted_json', {})
        if isinstance(extracted_json, str):
            extracted_json = json.loads(extracted_json)
        
        modifications = calculate_modifications(extracted_json, validated_data)
        
        # Save validated data
        if SUPABASE_AVAILABLE:
            DocumentDB.update(
                doc_id,
                status='validated',
                validated_json=validated_data,
                validated_by=validated_by,
                validated_at=datetime.utcnow().isoformat(),
                modifications=modifications
            )
        
        logger.info(f"✅ Document validated: {doc_id}")
        logger.info(f"📝 Human corrections: {len(modifications)} fields changed")
        
        return {
            "doc_id": doc_id,
            "status": "validated",
            "modifications_count": len(modifications),
            "message": "Validation saved successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.post("/api/approve")
async def approve_document(doc_id: str):
    """
    Step 4: Approve validated document
    Creates incident record and indexes for RAG
    """
    
    try:
        doc = DocumentDB.get(doc_id) if SUPABASE_AVAILABLE else None
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if doc['status'] != 'validated':
            raise HTTPException(
                status_code=400,
                detail=f"Document must be validated first. Current status: {doc['status']}"
            )
        
        # Get validated data
        validated_json = doc.get('validated_json', {})
        if isinstance(validated_json, str):
            validated_json = json.loads(validated_json)
        
        # Create transport incident
        incident_id = None
        if SUPABASE_AVAILABLE and Config.ORGANIZATION_ID:
            incident_id = TransportIncidentDB.create(
                org_id=Config.ORGANIZATION_ID,
                document_id=doc_id,
                validated_data=validated_json
            )
            
            DocumentDB.update(
                doc_id,
                status='approved',
                linked_entity_type='transport_incident',
                linked_entity_id=incident_id
            )
        
        # Index in Qdrant for RAG
        await index_validated_data(doc_id, validated_json)
        
        if SUPABASE_AVAILABLE:
            DocumentDB.update(
                doc_id,
                status='indexed',
                indexed_at=datetime.utcnow().isoformat()
            )
        
        logger.info(f"✅ Document approved: {doc_id}")
        if incident_id:
            logger.info(f"🎯 Incident created: {incident_id}")
        logger.info(f"🔍 Indexed for search")
        
        return {
            "doc_id": doc_id,
            "incident_id": incident_id,
            "status": "indexed",
            "message": "Incident created and searchable"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Approval error: {e}")
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")

# =============================================================================
# API ENDPOINTS - DOCUMENT MANAGEMENT (Keep existing)
# =============================================================================

@app.get("/api/documents")
async def get_documents():
    """Get list of all documents"""
    if SUPABASE_AVAILABLE and Config.ORGANIZATION_ID:
        docs = DocumentDB.get_by_org(Config.ORGANIZATION_ID)
        return {"documents": docs}
    return {"documents": list(documents_store.values())}

@app.get("/api/document/{doc_id}/chunks", response_model=ChunkResponse)
async def get_document_chunks(doc_id: str):
    """Get parsed chunks for a document"""
    
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        metadata_path = Path(documents_store[doc_id]["metadata_path"])
        
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="Metadata not found")
        
        with open(metadata_path, 'r') as f:
            data = json.load(f)
        
        return ChunkResponse(chunks=data.get('chunks', []))
        
    except Exception as e:
        logger.error(f"Error loading chunks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load chunks: {str(e)}")

@app.get("/api/document/{doc_id}/pdf")
async def get_document_pdf(doc_id: str):
    """Serve the PDF file"""
    
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_info = documents_store[doc_id]
    file_path = Path(doc_info["file_path"])
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf" if file_path.suffix == '.pdf' else "application/octet-stream",
        filename=doc_info["filename"]
    )

@app.delete("/api/document/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from vector store
    try:
        vector_store = get_vector_store()
        vector_store.delete_document(doc_id)
    except Exception as e:
        logger.warning(f"Error deleting from vector store: {e}")
    
    # Delete files
    doc_dir = OUTPUTS_DIR / doc_id
    if doc_dir.exists():
        shutil.rmtree(doc_dir)
    
    # Remove from store
    del documents_store[doc_id]
    save_document_store(documents_store)
    
    logger.info(f"🗑️ Deleted document: {doc_id}")
    
    return {"message": "Document deleted successfully", "doc_id": doc_id}

# =============================================================================
# API ENDPOINTS - RAG (Keep existing query endpoint)
# =============================================================================

@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents using vector similarity search"""
    
    try:
        # Generate query embedding
        embedding_service = get_embedding_service()
        query_embedding = embedding_service.embed_text(request.query)
        
        # Build filter
        filter_dict = {}
        if request.doc_id:
            filter_dict['doc_id'] = request.doc_id
        if request.chunk_type:
            filter_dict['chunk_type'] = request.chunk_type
        
        # Search vector store
        vector_store = get_vector_store()
        results = vector_store.query(
            query_embedding=query_embedding,
            n_results=request.n_results,
            filter=filter_dict if filter_dict else None
        )
        
        # Format results
        search_results = []
        
        for i in range(len(results['ids'])):
            metadata = results['metadatas'][i]
            
            search_result = SearchResult(
                chunk_id=results['ids'][i],
                doc_id=metadata.get('doc_id', ''),
                text=results['documents'][i],
                page=metadata.get('page', 0),
                chunk_type=metadata.get('chunk_type', 'text'),
                similarity_score=1.0 - results['distances'][i],
                grounding=metadata.get('grounding')
            )
            
            search_results.append(search_result)
        
        return QueryResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results)
        )
        
    except Exception as e:
        logger.error(f"Error querying documents: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to query: {str(e)}")

@app.get("/api/vector-store/stats", response_model=VectorStoreStats)
async def get_vector_store_stats():
    """Get vector store statistics"""
    
    try:
        vector_store = get_vector_store()
        stats = vector_store.get_stats()
        
        all_metadata = vector_store.collection.get(include=['metadatas'])
        doc_ids = sorted(set(m.get('doc_id') for m in all_metadata['metadatas'] if m.get('doc_id')))
        
        return VectorStoreStats(
            total_chunks=stats['total_chunks'],
            total_documents=stats['total_documents'],
            indexed_doc_ids=doc_ids
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# =============================================================================
# APPLICATION STARTUP
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("")
    logger.info("⚡ GROUNDTRUTH TRANSPORT EDITION")
    logger.info("=" * 60)
    logger.info("✅ LandingAI ADE extraction enabled")
    logger.info("✅ Visual grounding with bounding boxes")
    logger.info(f"✅ Multi-tenant with Supabase: {SUPABASE_AVAILABLE}")
    logger.info("✅ Vector database (ChromaDB) ready")
    logger.info("✅ Semantic search across documents")
    logger.info("")
    logger.info("🚀 Document Workflow:")
    logger.info("   POST   /api/upload       → Parse document")
    logger.info("   POST   /api/extract      → Extract structured data")
    logger.info("   POST   /api/validate     → Human validation")
    logger.info("   POST   /api/approve      → Create incident + index")
    logger.info("")
    logger.info("📄 Document Management:")
    logger.info("   GET    /api/documents")
    logger.info("   GET    /api/document/{doc_id}/chunks")
    logger.info("   GET    /api/document/{doc_id}/pdf")
    logger.info("   DELETE /api/document/{doc_id}")
    logger.info("")
    logger.info("🔍 RAG Search:")
    logger.info("   POST   /api/query")
    logger.info("   GET    /api/vector-store/stats")
    logger.info("")
    logger.info(f"🌍 Server running on {Config.HOST}:{Config.PORT}")
    logger.info("")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="info"
    )
