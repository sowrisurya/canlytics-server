from typing import List, Optional, Union
from fastapi import Form
from pydantic import BaseModel, Field, validator
import datetime

class VehicleLogsObject(BaseModel):
	# time: datetime.datetime = Field(..., example = "time")
	raw_data: str = Field(..., example = "raw_data")
	# did: str = Field(..., example = "did")
	parameter_name: Optional[str] = Field("Parameter Name", example = "parameter_name")
	diag_name: Optional[str] = Field("Diag Name", example = "diag_name")
	frame_id: Union[int, str] = Field(..., example = "frame_id")
	# start_bit: int = Field(..., example = "start_bit")
	# vin: Optional[str] = Field("vin", example = "vin")
	decoded_data: Optional[str] = Field("NA", example = "decoded_data")
	input_data: str = Field(..., example = "input_data")
	received_data: str = Field("NA", example = "received_data")

	# class Config:
	# 	validate_assignment = True

	# @validator('frame_id')
	# def set_frame_id(cls, frame_id):
	# 	return hex(frame_id)[2:] if isinstance(frame_id, int) else frame_id