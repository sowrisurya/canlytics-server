from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from typing import List
from schemas import *
from controller.vehicleDbcController import VehicleDbcController

vehicleDbcRouter = APIRouter(
    prefix="/vehicleDbc",
    tags=["Vehicle DBC"],
    responses={404: {"description": "Not found"}},
)

# # Get all vehicleDbc
# @vehicleDbcRouter.get("/", response_model=List[VehicleDbc])
# async def get_all_vehicleDbc(page_id: int = 1, page_size: int = 100):
# 	vehicleDbc = VehicleDbcController.get_all_vehicles(page_id=page_id, page_size=page_size)
# 	if vehicleDbc:
# 		return vehicleDbc
# 	raise HTTPException(status_code=404, detail="No vehicleDbc found")

# # Get vehicleDbc by id
# @vehicleDbcRouter.get("/{vehicle_id}", response_model=VehicleDbc)
# async def get_vehicleDbc_by_id(vehicle_id: str):
# 	vehicleDbc = VehicleDbcController.get_vehicle_by_id(vehicle_id)
# 	if vehicleDbc:
# 		return vehicleDbc
# 	raise HTTPException(status_code=404, detail="No vehicleDbc found")

# # Add vehicleDbc
# @vehicleDbcRouter.post("/", response_model=VehicleDbc)
# async def add_update_vehicleDbc(
# 	dbcFile: UploadFile = File(...),
# 	vehicle_id: str = Form(..., example = "vehicle_id"),
# ):
# 	vehicleDbc = VehicleDbcController.add_update_vehicle_dbc_file(
# 		vehicle_id = vehicle_id,
# 		dbc_file = dbcFile,
# 	)
# 	if vehicleDbc:
# 		return vehicleDbc
# 	raise HTTPException(status_code=400, detail="Could not add vehicleDbc")

# # Update vehicleDbc
# @vehicleDbcRouter.put("/{vehicle_id}", response_model=VehicleDbc)
# async def update_vehicleDbc(vehicle_id: str, vehicleDbc: VehicleDbc, dbcFile: UploadFile):
# 	vehicleDbc = VehicleDbcController.update_vehicle(
# 		vehicle_id,
# 		vehicleDbc.vehicle_name,
# 		vehicleDbc.vehicle_type,
# 		vehicleDbc.vehicle_model,
# 		dbcFile,
# 	)
# 	if vehicleDbc:
# 		return vehicleDbc
# 	raise HTTPException(status_code=404, detail="No vehicleDbc found")

# # Delete vehicleDbc
# @vehicleDbcRouter.delete("/{vehicle_id}", response_model=VehicleDbc)
# async def delete_vehicleDbc(vehicle_id: str):
# 	vehicleDbc = VehicleDbcController.delete_vehicle(vehicle_id)
# 	if vehicleDbc:
# 		return vehicleDbc
# 	raise HTTPException(status_code=404, detail="No vehicleDbc found")

# Get Model DIDs
@vehicleDbcRouter.get("/dids/{vehicle}/", response_model=VehicleModelDIDs)
async def get_vehicle_dids(vehicle_id: str):
	modelDids = VehicleDbcController.get_vehicle_dids(vehicle_id)
	if modelDids:
		return modelDids
	raise HTTPException(status_code=404, detail="No modelDids found or no DIDs found")

# Add Update Vehicle DID
@vehicleDbcRouter.post("/dids/", response_model=List[VehicleModelDIDs])
async def add_update_vehicles_dids(vehicle_ids: List[str], didsList: List[VehicleDID]):
	return [
		VehicleDbcController.add_update_vehicle_dids(
			vehicle_id = vehicle_id,
			dids_list = didsList
		)
		for vehicle_id in vehicle_ids
	]
	# raise HTTPException(status_code=404, detail="No vehicleDbc found")

# Update Vehicle ChipID
@vehicleDbcRouter.put("/chipid/", response_model=ResponseSchema)
async def update_vehicle_chipid(vehicle_id: str, frame_id: str, hex_data: str):
	chip_id = await VehicleDbcController.get_vehicle_vin_chipid(vehicle_id, frame_id = frame_id, input_data_hex = hex_data)
	if chip_id:
		return ResponseSchema(
			status = 200,
			message = "Vehicle ChipID Updated",
			error = None,
			data = {
				"chip_id": chip_id
			},
		)
	else:
		return ResponseSchema(
			status = 400,
			message = "Vehicle ChipID Not Updated",
			error = "Failed fetching chipID from vehicle",
			data = None,
		)
