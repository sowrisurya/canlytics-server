from typing import List, Optional, Union
from fastapi import Form
from pydantic import BaseModel, Field, validator
import datetime

class VehicleLogsObject(BaseModel):
	time: datetime.datetime = Field(..., example = "time")
	raw_data: str = Field(..., example = "raw_data")
	# did: str = Field(..., example = "did")
	diag_name: str = Field(..., example = "diag_name")
	frame_id: int = Field(..., example = "frame_id")
	start_bit: int = Field(..., example = "start_bit")
	vin: str = Field(..., example = "vin")
	decoded_data: dict = Field(..., example = "decoded_data")