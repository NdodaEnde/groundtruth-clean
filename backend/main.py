"""
GroundTruth Backend - Transport Client Edition
Multi-tenant document processing with Supabase + LandingAI ADE
Features: Upload → Parse → Extract → Validate → Approve → RAG Search → Chat
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables FIRST
#load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)
print(f"DEBUG: OPENAI_API_KEY loaded: {os.getenv('OPENAI_API_KEY', 'NOT SET')[:20]}...")

import uuid
import json
import shutil
import logging
#from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Body
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

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is missing. Check backend/.env")


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
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
    logger.info("✅ Supabase module loaded successfully")
except ImportError as e:
    SUPABASE_AVAILABLE = False
    logger.warning(f"⚠️ Supabase not available: {e}")
    logger.warning("Run: pip install supabase")

# OpenAI imports (for chat)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    logger.info("✅ OpenAI module loaded successfully")
except ImportError as e:
    OPENAI_AVAILABLE = False
    logger.warning(f"⚠️ OpenAI not available: {e}")
    logger.warning("Run: pip install openai")

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """Application configuration"""
    # LandingAI settings
    LANDING_AI_API_KEY = os.getenv("LANDING_AI_API_KEY")
    VISION_AGENT_API_KEY = os.getenv("VISION_AGENT_API_KEY")
    
    # Supabase settings
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Use service_role key for backend
    ORGANIZATION_ID = os.getenv("ORGANIZATION_ID", "default_org")
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Application settings
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}
    
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8001"))

# Verify API keys
if not Config.LANDING_AI_API_KEY and not Config.VISION_AGENT_API_KEY:
    logger.error("❌ No API key found. Set LANDING_AI_API_KEY or VISION_AGENT_API_KEY in .env")
    sys.exit(1)

# Initialize Supabase client
supabase: Optional[Client] = None
if SUPABASE_AVAILABLE and Config.SUPABASE_URL and Config.SUPABASE_KEY:
    try:
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        logger.info("✅ Supabase client initialized")
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize Supabase: {e}")
        SUPABASE_AVAILABLE = False
else:
    if SUPABASE_AVAILABLE:
        logger.warning("⚠️ SUPABASE_URL or SUPABASE_KEY not set")
    SUPABASE_AVAILABLE = False

# Initialize OpenAI client (for chat)
openai_client: Optional[OpenAI] = None
if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info("✅ OpenAI client initialized for chat")
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize OpenAI: {e}")
        openai_client = None
else:
    if OPENAI_AVAILABLE and not Config.OPENAI_API_KEY:
        logger.warning("⚠️ OPENAI_API_KEY not set - chat will use fallback mode")

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="GroundTruth API - Transport Edition",
    version="2.1.0",
    description="Multi-tenant document processing with validation workflow and RAG chat"
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
# PYDANTIC MODELS - API Responses
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

# =============================================================================
# PRE-TRIP CHECKLIST EXTRACTION SCHEMA
# =============================================================================

class VehicleHeader(BaseModel):
    """Header information from the checklist"""
    vehicle_reg_no: Optional[str] = Field(None, description="Vehicle registration number (e.g., KKJ 770 NW)")
    drivers_name: Optional[str] = Field(None, description="Driver's full name")
    date: Optional[str] = Field(None, description="Date of inspection in format DD/MM/YY or YYYY-MM-DD")
    vehicle_mileage: Optional[str] = Field(None, description="Vehicle mileage reading")


class InspectionItem(BaseModel):
    """Single inspection item with pre-trip and post-trip status"""
    item_name: Optional[str] = Field(None, description="Name of the inspection item (e.g., BODY WORK, LICENSE DISK)")
    condition: Optional[str] = Field(None, description="Condition description (e.g., Scratched, Valid, Working)")
    pre_trip_yes: Optional[bool] = Field(None, description="Pre-trip inspection: YES checked")
    pre_trip_no: Optional[bool] = Field(None, description="Pre-trip inspection: NO checked")
    remarks: Optional[str] = Field(None, description="Remarks or notes for this item")
    post_trip_yes: Optional[bool] = Field(None, description="Post-trip inspection: YES checked")
    post_trip_no: Optional[bool] = Field(None, description="Post-trip inspection: NO checked")


class ConsumableLevel(BaseModel):
    """Consumable/fluid level item with before and after readings"""
    item_name: Optional[str] = Field(None, description="Item name (e.g., Amount of Fuel, Brake Fluid, Engine Oil)")
    before_trip_level: Optional[str] = Field(None, description="Level before trip (F, 3/4, 1/2, 1/4, E)")
    after_trip_level: Optional[str] = Field(None, description="Level after trip (F, 3/4, 1/2, 1/4, E)")


class TyreCondition(BaseModel):
    """Tyre condition with brand and status"""
    position: Optional[str] = Field(None, description="Tyre position (Front L, Front R, Rear L, Rear R)")
    before_condition: Optional[str] = Field(None, description="Condition before trip (Good, Fair, Bad)")
    before_brand: Optional[str] = Field(None, description="Tyre brand before trip")
    after_condition: Optional[str] = Field(None, description="Condition after trip (Good, Fair, Bad)")
    after_brand: Optional[str] = Field(None, description="Tyre brand after trip")


class Signatures(BaseModel):
    """Signature fields"""
    receiver_name: Optional[str] = Field(None, description="Name of Receiver")
    dept_representative_name: Optional[str] = Field(None, description="Name of Dept Representative")
    fuel_card_issued: Optional[bool] = Field(None, description="Was fuel card issued?")
    keys_issued: Optional[bool] = Field(None, description="Were keys issued?")


class PreTripChecklistExtraction(BaseModel):
    """
    Complete schema for Yarona Pool Vehicle Inspection Checklist
    Captures pre-trip and post-trip inspection data
    """
    vehicle_header: Optional[VehicleHeader] = Field(None, description="Vehicle and driver header information")
    inspection_items: Optional[List[InspectionItem]] = Field(None, description="List of inspection items with pre/post trip status")
    consumable_levels: Optional[List[ConsumableLevel]] = Field(None, description="Fluid/consumable levels before and after trip")
    tyre_conditions: Optional[List[TyreCondition]] = Field(None, description="Tyre condition and brand for each position")
    signatures: Optional[Signatures] = Field(None, description="Signature information")


# =============================================================================
# RAG MODELS
# =============================================================================

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

# =============================================================================
# CHAT MODELS (for /api/chat endpoint)
# =============================================================================

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    conversation_history: Optional[List[ChatMessage]] = []
    n_results: int = 5

class ChatSource(BaseModel):
    doc_id: str
    chunk_id: str
    filename: str
    page: int
    chunk_type: str
    text: str
    similarity_score: float

class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource]
    question: str

# =============================================================================
# SUPABASE DATABASE HELPERS
# =============================================================================

class SupabaseDB:
    """Helper class for Supabase database operations"""
    
    @staticmethod
    def save_document(doc_id: str, filename: str, organization_id: str, status: str = 'uploaded'):
        """Save document metadata to Supabase"""
        if not supabase:
            return None
        
        try:
            data = {
                'doc_id': doc_id,
                'filename': filename,
                'organization_id': organization_id,
                'status': status,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            result = supabase.table('documents').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error saving document to Supabase: {e}")
            return None
    
    @staticmethod
    def update_document(doc_id: str, **kwargs):
        """Update document in Supabase"""
        if not supabase:
            return None
        
        try:
            kwargs['updated_at'] = datetime.utcnow().isoformat()
            result = supabase.table('documents').update(kwargs).eq('doc_id', doc_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating document in Supabase: {e}")
            return None
    
    @staticmethod
    def get_document(doc_id: str):
        """Get document from Supabase"""
        if not supabase:
            return None
        
        try:
            result = supabase.table('documents').select('*').eq('doc_id', doc_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting document from Supabase: {e}")
            return None
    
    @staticmethod
    def save_vehicle_inspection(doc_id: str, organization_id: str, validated_data: dict, validated_by: str):
        """Save validated vehicle inspection to Supabase"""
        if not supabase:
            logger.warning("Supabase not available - saving to local file")
            return SupabaseDB._save_to_local(doc_id, validated_data)
        
        try:
            # Flatten the data for storage
            data = {
                'doc_id': doc_id,
                'organization_id': organization_id,
                'validated_by': validated_by,
                'validated_at': datetime.utcnow().isoformat(),
                
                # Header fields
                'vehicle_reg_no': validated_data.get('vehicle_reg_no'),
                'drivers_name': validated_data.get('drivers_name'),
                'inspection_date': validated_data.get('date'),
                'vehicle_mileage': validated_data.get('vehicle_mileage'),
                
                # Store complex data as JSONB
                'inspection_items': validated_data.get('inspection_items', []),
                'consumables': validated_data.get('consumables', []),
                'tyres': validated_data.get('tyres', []),
                
                # Signatures
                'fuel_card_issued': validated_data.get('fuel_card_issued', False),
                'keys_issued': validated_data.get('keys_issued', False),
                'receiver_name': validated_data.get('receiver_name'),
                'dept_representative_name': validated_data.get('dept_representative_name'),
                
                # Full data backup
                'raw_validated_data': validated_data
            }
            
            result = supabase.table('vehicle_inspections').insert(data).execute()
            logger.info(f"✅ Saved vehicle inspection to Supabase: {doc_id}")
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error saving to Supabase: {e}")
            # Fallback to local storage
            return SupabaseDB._save_to_local(doc_id, validated_data)
    
    @staticmethod
    def _save_to_local(doc_id: str, validated_data: dict):
        """Fallback: Save to local JSON file"""
        try:
            validated_dir = OUTPUTS_DIR / "validated"
            validated_dir.mkdir(exist_ok=True)
            
            filepath = validated_dir / f"{doc_id}_validated.json"
            with open(filepath, 'w') as f:
                json.dump({
                    'doc_id': doc_id,
                    'validated_at': datetime.utcnow().isoformat(),
                    'data': validated_data
                }, f, indent=2)
            
            logger.info(f"✅ Saved validation to local file: {filepath}")
            return {'doc_id': doc_id, 'storage': 'local'}
        except Exception as e:
            logger.error(f"Error saving to local file: {e}")
            return None
    
    @staticmethod
    def get_inspections(organization_id: str, limit: int = 100):
        """Get vehicle inspections from Supabase"""
        if not supabase:
            return []
        
        try:
            result = supabase.table('vehicle_inspections')\
                .select('*')\
                .eq('organization_id', organization_id)\
                .order('validated_at', desc=True)\
                .limit(limit)\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting inspections: {e}")
            return []

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
# API ENDPOINTS - BASIC
# =============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "app": "GroundTruth API - Transport Edition",
        "version": "2.1.0",
        "status": "running",
        "features": {
            "landingai": AGENTIC_DOC_AVAILABLE,
            "supabase": SUPABASE_AVAILABLE,
            "openai_chat": openai_client is not None
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "GroundTruth Transport Document Processor",
        "version": "2.1.0",
        "landingai_available": AGENTIC_DOC_AVAILABLE,
        "supabase_available": SUPABASE_AVAILABLE,
        "openai_available": openai_client is not None,
        "organization_id": Config.ORGANIZATION_ID
    }

# =============================================================================
# API ENDPOINTS - DOCUMENT WORKFLOW
# =============================================================================

@app.post("/api/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Step 1: Upload and parse document
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
        
        # Save to Supabase
        if SUPABASE_AVAILABLE:
            SupabaseDB.save_document(doc_id, file.filename, Config.ORGANIZATION_ID, 'parsing')
        
        # Parse with LandingAI
        result = processor.process_document(str(file_path))
        
        if not result.get('success'):
            if SUPABASE_AVAILABLE:
                SupabaseDB.update_document(doc_id, status='parse_failed')
            shutil.rmtree(doc_dir)
            raise HTTPException(status_code=500, detail=result.get('error', 'Processing failed'))
        
        # Save parsed results
        metadata_path = doc_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(result['parsed_data'], f, indent=2, default=str)
        
        # Update Supabase
        if SUPABASE_AVAILABLE:
            SupabaseDB.update_document(doc_id, status='parsed')
        
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
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@app.post("/api/extract")
async def extract_document_data(doc_id: str, force: bool = False):
    """
    Step 2: Extract structured data using LandingAI ADE Extract
    Converts parsed markdown into structured fields
    
    Args:
        doc_id: Document ID
        force: If True, re-extract even if cached data exists
    """
    
    try:
        # Get document from memory store
        if doc_id not in documents_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_info = documents_store[doc_id]
        
        # Check for cached extraction (prevents redundant API calls)
        extracted_path = OUTPUTS_DIR / doc_id / "extracted.json"
        if not force and extracted_path.exists():
            logger.info(f"📦 Returning cached extraction for document: {doc_id}")
            with open(extracted_path, 'r') as f:
                cached_data = json.load(f)
            return {
                "doc_id": doc_id,
                "status": "extracted",
                "extracted_data": cached_data,
                "cached": True,
                "message": "Returning cached extraction (use force=true to re-extract)"
            }
        
        metadata_path = Path(doc_info.get('metadata_path', ''))
        
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="Parsed data not found")
        
        with open(metadata_path, 'r') as f:
            parsed_data = json.load(f)
        
        markdown = parsed_data.get('markdown')
        if not markdown:
            raise HTTPException(status_code=400, detail="No parsed markdown available")
        
        logger.info(f"🔍 Extracting structured data from document: {doc_id}")
        
        # Convert schema to JSON schema for LandingAI
        schema = pydantic_to_json_schema(PreTripChecklistExtraction)
        
        # Extract using LandingAI ADE
        extract_response = landing_client.extract(
            schema=schema,
            markdown=markdown,
            model="extract-latest"
        )
        
        # Convert extraction result to dict
        extracted_data = extract_response.extraction
        if hasattr(extracted_data, 'model_dump'):
            extracted_data = extracted_data.model_dump()
        elif hasattr(extracted_data, 'dict'):
            extracted_data = extracted_data.dict()
        
        # Save extracted data
        with open(extracted_path, 'w') as f:
            json.dump(extracted_data, f, indent=2, default=str)
        
        # Update document status
        documents_store[doc_id]['status'] = 'extracted'
        documents_store[doc_id]['extracted_path'] = str(extracted_path)
        save_document_store(documents_store)
        
        if SUPABASE_AVAILABLE:
            SupabaseDB.update_document(doc_id, status='extracted')
        
        logger.info(f"✅ Data extracted successfully: {doc_id}")
        
        return {
            "doc_id": doc_id,
            "status": "extracted",
            "extracted_data": extracted_data,
            "cached": False,
            "message": "Document ready for validation"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Extraction error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.post("/api/validate")
async def validate_document(doc_id: str, validated_by: str = "user", validated_data: dict = Body(...)):
    """
    Step 3: Save human-validated data to Supabase
    """
    
    try:
        if doc_id not in documents_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        logger.info(f"💾 Saving validated data for document: {doc_id}")
        
        # Save to Supabase
        result = SupabaseDB.save_vehicle_inspection(
            doc_id=doc_id,
            organization_id=Config.ORGANIZATION_ID,
            validated_data=validated_data,
            validated_by=validated_by
        )
        
        # Update document status
        documents_store[doc_id]['status'] = 'validated'
        documents_store[doc_id]['validated_at'] = datetime.utcnow().isoformat()
        save_document_store(documents_store)
        
        if SUPABASE_AVAILABLE:
            SupabaseDB.update_document(doc_id, status='validated')
        
        logger.info(f"✅ Document validated: {doc_id}")
        
        return {
            "doc_id": doc_id,
            "status": "validated",
            "storage": "supabase" if SUPABASE_AVAILABLE and supabase else "local",
            "message": "Validation saved successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.get("/api/inspections")
async def get_inspections(limit: int = 100):
    """Get validated vehicle inspections"""
    
    if SUPABASE_AVAILABLE:
        inspections = SupabaseDB.get_inspections(Config.ORGANIZATION_ID, limit)
        return {"inspections": inspections, "count": len(inspections)}
    else:
        # Fallback: Read from local files
        validated_dir = OUTPUTS_DIR / "validated"
        inspections = []
        
        if validated_dir.exists():
            for filepath in validated_dir.glob("*_validated.json"):
                with open(filepath, 'r') as f:
                    inspections.append(json.load(f))
        
        return {"inspections": inspections, "count": len(inspections), "storage": "local"}

# =============================================================================
# API ENDPOINTS - DOCUMENT MANAGEMENT
# =============================================================================

@app.get("/api/documents")
async def get_documents():
    """Get list of all documents"""
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
        
        # Transform chunks to normalize field names for frontend
        chunks = data.get('chunks', [])
        normalized_chunks = []
        
        for chunk in chunks:
            normalized = {
                # Use markdown content if text is missing
                'text': chunk.get('markdown') or chunk.get('text') or '',
                # Normalize type field
                'chunk_type': chunk.get('type') or chunk.get('chunk_type') or 'text',
                # Ensure grounding is properly structured
                'grounding': chunk.get('grounding', {}),
            }
            
            # Copy any other fields that might be useful
            for key in ['id', 'chunk_id', 'page', 'box', 'metadata']:
                if key in chunk and key not in normalized:
                    normalized[key] = chunk[key]
            
            normalized_chunks.append(normalized)
        
        return ChunkResponse(chunks=normalized_chunks)
        
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
# API ENDPOINTS - RAG SEARCH
# =============================================================================

@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents using vector similarity search"""
    
    try:
        # Generate query embedding
        embedding_service = get_embedding_service()
        query_embedding = embedding_service.embed_text(request.query)
        
        # Search vector store - pass doc_id and chunk_type directly (not as filter dict)
        vector_store = get_vector_store()
        results = vector_store.query(
            query_embedding=query_embedding,
            n_results=request.n_results,
            doc_id=request.doc_id,
            chunk_type=request.chunk_type
        )
        
        # Format results
        search_results = []
        
        ids = results.get('ids', [])
        documents = results.get('documents', [])
        metadatas = results.get('metadatas', [])
        distances = results.get('distances', [])
        
        for i in range(len(ids)):
            metadata = metadatas[i] if i < len(metadatas) else {}
            
            search_result = SearchResult(
                chunk_id=ids[i],
                doc_id=metadata.get('doc_id', ''),
                text=documents[i] if i < len(documents) else '',
                page=metadata.get('page', 0),
                chunk_type=metadata.get('chunk_type', 'text'),
                similarity_score=1.0 - (distances[i] if i < len(distances) else 1.0),
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


# =============================================================================
# API ENDPOINTS - CHAT (RAG-powered Q&A)
# =============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """
    RAG-based chat endpoint.
    1. Semantic search for relevant document chunks
    2. Send chunks + question to OpenAI LLM
    3. Return answer with sources
    """
    
    try:
        logger.info(f"💬 Chat query: {request.question[:100]}...")
        
        # Step 1: Retrieve relevant document chunks via semantic search
        embedding_service = get_embedding_service()
        query_embedding = embedding_service.embed_text(request.question)
        
        vector_store = get_vector_store()
        results = vector_store.query(
            query_embedding=query_embedding,
            n_results=request.n_results
        )
        
        # Format retrieved chunks
        sources = []
        context_chunks = []
        
        ids = results.get('ids', [])
        documents = results.get('documents', [])
        metadatas = results.get('metadatas', [])
        distances = results.get('distances', [])
        
        for i in range(len(ids)):
            chunk_id = ids[i]
            metadata = metadatas[i] if i < len(metadatas) else {}
            text = documents[i] if i < len(documents) else ''
            distance = distances[i] if i < len(distances) else 1.0
            
            doc_id = metadata.get('doc_id', '')
            doc_info = documents_store.get(doc_id, {})
            
            source = ChatSource(
                doc_id=doc_id,
                chunk_id=chunk_id,
                filename=doc_info.get('filename', f'Document {doc_id[:8]}' if doc_id else 'Unknown'),
                page=metadata.get('page', 0),
                chunk_type=metadata.get('chunk_type', 'text'),
                text=text[:500] if text else '',
                similarity_score=round(1.0 - distance, 3)
            )
            sources.append(source)
            
            # Build context for LLM
            context_chunks.append(f"""
--- Source: {source.filename}, Page {source.page + 1} ---
{text}
""")
        
        # Step 2: Generate answer using LLM
        if openai_client and sources:
            context = "\n".join(context_chunks)
            
            # Build conversation history
            history_messages = []
            for msg in (request.conversation_history or [])[-6:]:  # Last 3 exchanges
                history_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            system_prompt = f"""You are GroundTruth, an AI assistant that answers questions about transport documents, vehicle inspections, and fleet management.

Use ONLY the information from these document excerpts to answer questions. If the answer cannot be found in the provided context, say so clearly.

Be concise, accurate, and helpful. When referencing information, mention which document/page it came from.

CONTEXT FROM DOCUMENTS:
{context}
"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                *history_messages,
                {"role": "user", "content": request.question}
            ]
            
            try:
                completion = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.3
                )
                answer = completion.choices[0].message.content
                logger.info("✅ Generated answer using OpenAI")
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                answer = f"I found relevant documents but couldn't generate a response. OpenAI error: {str(e)}"
                
        elif sources:
            # Fallback: Return relevant excerpts without LLM
            answer = f"I found {len(sources)} relevant sections in your documents:\n\n"
            for i, source in enumerate(sources[:3], 1):
                answer += f"**{i}. {source.filename}** (Page {source.page + 1}):\n"
                answer += f'"{source.text[:200]}..."\n\n'
            answer += "\n_Configure OPENAI_API_KEY for AI-powered answers._"
        else:
            answer = "I couldn't find any relevant information in your uploaded documents. Try rephrasing your question or ensure documents are uploaded and indexed."
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            question=request.question
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


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
    logger.info("⚡ GROUNDTRUTH TRANSPORT EDITION v2.1")
    logger.info("=" * 60)
    logger.info("✅ LandingAI ADE extraction enabled")
    logger.info("✅ Pre-Trip Checklist schema configured")
    logger.info(f"✅ Supabase integration: {SUPABASE_AVAILABLE}")
    logger.info(f"✅ OpenAI chat: {openai_client is not None}")
    logger.info("✅ Vector database ready")
    logger.info("")
    logger.info("🚀 Document Workflow:")
    logger.info("   POST   /api/upload       → Parse document")
    logger.info("   POST   /api/extract      → Extract structured data")
    logger.info("   POST   /api/validate     → Human validation → Save to DB")
    logger.info("")
    logger.info("📄 Document Management:")
    logger.info("   GET    /api/documents")
    logger.info("   GET    /api/document/{doc_id}/chunks")
    logger.info("   GET    /api/document/{doc_id}/pdf")
    logger.info("   DELETE /api/document/{doc_id}")
    logger.info("")
    logger.info("🔍 Search & Chat:")
    logger.info("   POST   /api/query        → Semantic search")
    logger.info("   POST   /api/chat         → RAG-powered Q&A")
    logger.info("   GET    /api/inspections")
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
