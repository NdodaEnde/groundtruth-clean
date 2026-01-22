"""
Supabase client with helper functions for document management
Multi-tenant database operations for GroundTruth platform
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, List
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for backend

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class DocumentDB:
    """Document management with Supabase"""
    
    @staticmethod
    def create(org_id: str, filename: str, file_path: str, 
               document_type: str, created_by: Optional[str] = None) -> str:
        """Create new document record"""
        
        data = {
            'organization_id': org_id,
            'filename': filename,
            'file_path': file_path,
            'document_type': document_type,
            'status': 'uploaded',
            'created_by': created_by
        }
        
        result = supabase.table('documents').insert(data).execute()
        
        return result.data[0]['id']
    
    @staticmethod
    def update(doc_id: str, **kwargs):
        """Update document fields"""
        
        # Convert complex types to JSON strings
        for key in ['parsed_json', 'extracted_json', 'validated_json', 'modifications', 'qdrant_ids']:
            if key in kwargs and kwargs[key] is not None:
                if not isinstance(kwargs[key], str):
                    kwargs[key] = json.dumps(kwargs[key])
        
        kwargs['updated_at'] = datetime.utcnow().isoformat()
        
        supabase.table('documents').update(kwargs).eq('id', doc_id).execute()
    
    @staticmethod
    def get(doc_id: str) -> Optional[Dict]:
        """Get document by ID"""
        
        result = supabase.table('documents').select('*').eq('id', doc_id).execute()
        
        if not result.data:
            return None
        
        return result.data[0]
    
    @staticmethod
    def get_by_org(org_id: str, status: Optional[str] = None) -> List[Dict]:
        """Get all documents for organization"""
        
        query = supabase.table('documents').select('*').eq('organization_id', org_id)
        
        if status:
            query = query.eq('status', status)
        
        result = query.order('created_at', desc=True).execute()
        
        return result.data


class TransportIncidentDB:
    """Transport incident management"""
    
    @staticmethod
    def create(org_id: str, document_id: str, validated_data: dict) -> str:
        """Create incident from validated document data"""
        
        driver_info = validated_data.get('driver_info', {})
        incident_details = validated_data.get('incident_details', {})
        damage = validated_data.get('damage_assessment', {})
        injuries = validated_data.get('injuries', {})
        witnesses = validated_data.get('witnesses', {})
        additional = validated_data.get('additional_info', {})
        
        data = {
            'organization_id': org_id,
            'document_id': document_id,
            
            # Driver
            'driver_name': driver_info.get('driver_name'),
            'driver_id': driver_info.get('driver_id'),
            'driver_license_number': driver_info.get('license_number'),
            'vehicle_registration': driver_info.get('vehicle_registration'),
            'vehicle_type': driver_info.get('vehicle_type'),
            
            # Incident
            'incident_date': incident_details.get('incident_date'),
            'incident_time': incident_details.get('incident_time'),
            'location': incident_details.get('location'),
            'gps_coordinates': incident_details.get('gps_coordinates'),
            'incident_type': incident_details.get('incident_type'),
            'description': incident_details.get('description'),
            
            # Damage
            'vehicle_damage': damage.get('vehicle_damage'),
            'third_party_damage': damage.get('third_party_damage'),
            'estimated_repair_cost': damage.get('estimated_cost'),
            
            # Injuries
            'injuries_reported': injuries.get('injuries_reported') == 'yes',
            'injury_details': injuries.get('injury_details'),
            'medical_attention_required': injuries.get('medical_attention') == 'yes',
            
            # Witnesses
            'witnesses_present': witnesses.get('witness_present') == 'yes',
            'witness_details': json.dumps(witnesses.get('witness_details', [])),
            
            # Police
            'police_reported': additional.get('police_reported') == 'yes',
            'case_number': additional.get('case_number'),
            'police_station': additional.get('police_station'),
            
            # Status
            'status': 'pending',
            'severity': classify_severity(incident_details, damage, injuries)
        }
        
        result = supabase.table('transport_incidents').insert(data).execute()
        
        return result.data[0]['id']


def classify_severity(incident: dict, damage: dict, injuries: dict) -> str:
    """Classify incident severity based on details"""
    
    # Critical if injuries reported
    if injuries.get('injuries_reported') == 'yes':
        return 'critical'
    
    # Severe if high cost
    cost = damage.get('estimated_cost', 0)
    if isinstance(cost, (int, float)) and cost > 50000:
        return 'severe'
    elif isinstance(cost, (int, float)) and cost > 10000:
        return 'moderate'
    else:
        return 'minor'
