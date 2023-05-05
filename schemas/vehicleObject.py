from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import datetime

class VehicleObject(BaseModel):
    vin: str = Field(..., example = "vin")
    chip_id: str = Field(..., example = "chip_id")
    make: str = Field(..., example = "make")
    model: str = Field(..., example = "model")
    status: str = Field("offline", example = "status")
    
class vehicleGPSCoord(BaseModel):
	vin: str = Field(..., example = "vin")
	lat: float = Field(..., example = "lat")
	lng: float = Field(..., example = "lng")
	requested_at: datetime.datetime = Field(..., example = "requested_at")