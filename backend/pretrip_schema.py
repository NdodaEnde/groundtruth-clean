"""
Pre-Trip Checklist Extraction Schema
Matches Yarona Rustenburg Pool Vehicle Inspection Checklist
"""

from pydantic import BaseModel, Field
from typing import Optional, List


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
    # Before Trip columns (typically F, 3/4, 1/2, 1/4, E)
    before_trip_level: Optional[str] = Field(None, description="Level before trip (F, 3/4, 1/2, 1/4, E)")
    before_trip_condition: Optional[str] = Field(None, description="Condition before trip")
    # After Trip columns
    after_trip_level: Optional[str] = Field(None, description="Level after trip (F, 3/4, 1/2, 1/4, E)")
    after_trip_condition: Optional[str] = Field(None, description="Condition after trip")


class TyreCondition(BaseModel):
    """Tyre condition with brand and status"""
    position: Optional[str] = Field(None, description="Tyre position (Front L, Front R, Rear L, Rear R)")
    before_condition: Optional[str] = Field(None, description="Condition before trip (Good, Fair, Bad)")
    before_brand: Optional[str] = Field(None, description="Tyre brand before trip")
    after_condition: Optional[str] = Field(None, description="Condition after trip (Good, Fair, Bad)")
    after_brand: Optional[str] = Field(None, description="Tyre brand after trip")


class WheelStatus(BaseModel):
    """Wheel caps and MAG wheels status"""
    item_name: Optional[str] = Field(None, description="Item name (Wheel Caps, MAG Wheels)")
    before_count_0: Optional[bool] = Field(None, description="Before trip: 0 checked")
    before_count_1: Optional[bool] = Field(None, description="Before trip: 1 checked")
    before_count_2: Optional[bool] = Field(None, description="Before trip: 2 checked")
    before_count_3: Optional[bool] = Field(None, description="Before trip: 3 checked")
    before_count_4: Optional[bool] = Field(None, description="Before trip: 4 checked")
    after_count_0: Optional[bool] = Field(None, description="After trip: 0 checked")
    after_count_1: Optional[bool] = Field(None, description="After trip: 1 checked")
    after_count_2: Optional[bool] = Field(None, description="After trip: 2 checked")
    after_count_3: Optional[bool] = Field(None, description="After trip: 3 checked")
    after_count_4: Optional[bool] = Field(None, description="After trip: 4 checked")


class Signatures(BaseModel):
    """Signature fields"""
    receiver_driver_signature: Optional[str] = Field(None, description="Signature of Receiver/Driver - presence indicator")
    receiver_name: Optional[str] = Field(None, description="Name of Receiver")
    corporate_service_signature: Optional[str] = Field(None, description="Signature of Corporate service/Fleet Section - presence indicator")
    dept_representative_name: Optional[str] = Field(None, description="Name of Dept Representative")


class FuelCard(BaseModel):
    """Fuel card and keys status"""
    fuel_card_issued: Optional[bool] = Field(None, description="Was fuel card issued?")
    keys_issued: Optional[bool] = Field(None, description="Were keys issued?")


class PreTripChecklistExtraction(BaseModel):
    """
    Complete schema for Yarona Pool Vehicle Inspection Checklist
    Captures pre-trip and post-trip inspection data
    """
    
    # Header information
    vehicle_header: Optional[VehicleHeader] = Field(None, description="Vehicle and driver header information")
    
    # Main inspection items (Body Work through Seat Belts)
    inspection_items: Optional[List[InspectionItem]] = Field(
        None, 
        description="List of inspection items with pre/post trip status"
    )
    
    # Wheel status
    wheel_status: Optional[List[WheelStatus]] = Field(
        None,
        description="Wheel caps and MAG wheels count"
    )
    
    # Consumable levels (Fuel, Brake Fluid, Engine Oil, Water)
    consumable_levels: Optional[List[ConsumableLevel]] = Field(
        None,
        description="Fluid/consumable levels before and after trip"
    )
    
    # Tyre conditions
    tyre_conditions: Optional[List[TyreCondition]] = Field(
        None,
        description="Tyre condition and brand for each position"
    )
    
    # Fuel card and keys
    fuel_card: Optional[FuelCard] = Field(None, description="Fuel card and keys issued status")
    
    # Signatures
    signatures: Optional[Signatures] = Field(None, description="Signature information")


# Default inspection items for the form
DEFAULT_INSPECTION_ITEMS = [
    {"item_name": "BODY WORK", "condition": "Scratched/Dents"},
    {"item_name": "LICENSE DISK", "condition": "Valid"},
    {"item_name": "WINDOW AND WINDSCREEN", "condition": "No Cracks"},
    {"item_name": "WIPER BLADES", "condition": "Working"},
    {"item_name": "NUMBER PLATES", "condition": "Visible"},
    {"item_name": "DOORS/BONNET/BOOT", "condition": "In Place"},
    {"item_name": "EMERGENCY KIT", "condition": "Working"},
    {"item_name": "WHEEL SPANNER", "condition": "In Place"},
    {"item_name": "WARNING TRIANGLE", "condition": "In Place"},
    {"item_name": "JACK", "condition": "In Place"},
    {"item_name": "HOOTER", "condition": "Working"},
    {"item_name": "BRAKE LIGHTS", "condition": "Working"},
    {"item_name": "HEAD LIGHTS", "condition": "Working"},
    {"item_name": "INDICATORS", "condition": "Working"},
    {"item_name": "PARKING LIGHTS", "condition": "Working"},
    {"item_name": "REVERSE LIGHTS", "condition": "Working"},
    {"item_name": "TAIL LIGHTS", "condition": "Working"},
    {"item_name": "TWO WAY RADIO", "condition": "Working"},
    {"item_name": "COMMERCIAL RADIO", "condition": "Working"},
    {"item_name": "SEAT BELTS", "condition": "Operating"},
]

DEFAULT_CONSUMABLES = [
    {"item_name": "Amount of Fuel"},
    {"item_name": "Brake Fluid"},
    {"item_name": "Engine Oil"},
    {"item_name": "Water"},
]

DEFAULT_TYRES = [
    {"position": "Front L"},
    {"position": "Front R"},
    {"position": "Rear L"},
    {"position": "Rear R"},
]

DEFAULT_WHEELS = [
    {"item_name": "Wheel Caps"},
    {"item_name": "MAG Wheels"},
]
