from typing import List, Optional, Union
from fastapi import Form
from pydantic import BaseModel, Field, validator
import datetime

class VehicleLogsObject(BaseModel):
	time: datetime.datetime = Field(..., example = "time")
	raw_data: str = Field(..., example = "raw_data")
	# did: str = Field(..., example = "did")
	diag_name: Optional[str] = Field("DiagName", example = "diag_name")
	frame_id: Optional[int] = Field(0, example = "frame_id")
	# start_bit: int = Field(..., example = "start_bit")
	vin: Optional[str] = Field("vin", example = "vin")
	decoded_data: str = Field(..., example = "decoded_data")
	input_data: str = Field(..., example = "input_data")