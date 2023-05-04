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
	diag_name: str = Form(..., example = "diag_name")
	frame_id: int = Form(..., example = "frame_id")
	start_bit: int = Form(..., example = "start_bit")
	hex_data: Optional[str] = None
	# did: Optional[str] = None

class VehicleModelDIDs(BaseModel):
	model_id: str = Form(..., example = "model_id")
	model_name: str = Form(..., example = "model_name")
	vehicle_id: str = Form(..., example = "vehicle_id")
	chip_id: str = Form(..., example = "chip_id")
	dids_list: List[VehicleDID] = Form(..., example = [])
