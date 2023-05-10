from typing import List, Optional, Union
from fastapi import Form
from pydantic import BaseModel, Field, validator

# class VehicleDbc(BaseModel):
# 	# vehicle_id: str = Form(..., example = "vehicle_id")
# 	# vehicle_name: str = Form(..., example = "vehicle_name")
# 	# vehicle_type: str = Form(..., example = "vehicle_type")
# 	# vehicle_model: str = Form(..., example = "vehicle_model")
# 	# vehicle_make: str = Form(..., example = "vehicle_make")
# 	chip_id: str = Form(..., example = "chip_id")
# 	vin: str = Form(..., example = "vin")
# 	# vehicle_status: bool = Form(..., example = "vehicle_status")
# 	# dbc_file: Optional[str] = None

class VehicleDID(BaseModel):
	diag_name: str = Field(..., example = "diag_name")
	frame_id: str = Field(..., example = "frame_id")
	start_bit: int = Field(..., example = "start_bit")
	hex_data: Optional[str] = Field("22F190", example = "hex_data")
	# did: Optional[str] = None

	class Config:
		validate_assignment = True

	@validator('hex_data')
	def set_hex_data(cls, hex_data):
		return hex_data or '22F190'

	# @validator('frame_id')
	# def set_frame_id(cls, frame_id):
	# 	if isinstance(frame_id, str):
	# 		return int(frame_id, 16)
	# 	elif isinstance(frame_id, int):
	# 		return hex(frame_id)[2:]

class VehicleModelDIDs(BaseModel):
	model_id: str = Form(..., example = "model_id")
	model_name: str = Form(..., example = "model_name")
	vehicle_id: str = Form(..., example = "vehicle_id")
	chip_id: str = Form(..., example = "chip_id")
	dids_list: List[VehicleDID] = Form(..., example = [])

