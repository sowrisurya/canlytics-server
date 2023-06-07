from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator
# from .vehicleLogsObject import VehicleLogsObject
import datetime

class DTCData(BaseModel):
    hex: str | None
    code: str | None
    status: str | None
    description: str | None
    
class ECUDTCInfo(BaseModel):
    ecu_name: str
    did: str
    messages: List[DTCData]
    