from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from typing import List
from schemas import (
    VehicleLogsObject,
    VehicleDID,
    VehicleDTCSnapShot,
    VehicleECUDID,
)
import datetime
from controller.vehicleLogsController import VehicleLogsController

vehicleLogsRouter = APIRouter(
    prefix="/vehicleLogs",
    tags=["Vehicle Logs"],
    responses={404: {"description": "Not found"}},
)

# Get all vehicleLogs
@vehicleLogsRouter.get("/all", response_model=List[VehicleLogsObject])
async def get_all_vehicleLogs(vehicle_id: str, limit: int = 100, page: int = 1, start_time: datetime.datetime = None, end_time: datetime.datetime = None):
	vehicleLogs = VehicleLogsController.get_vehicle_logs(vehicle_id = vehicle_id, start_time = start_time, end_time = end_time, limit = limit, page = page)
	if vehicleLogs:
		return vehicleLogs
	raise HTTPException(status_code=404, detail="No vehicleLogs found")

@vehicleLogsRouter.post("/live-logs", response_model=List[VehicleLogsObject])
async def get_live_logs(vehicle_ids: List[str], didsList: List[VehicleDID], timeout: int = 100):
	vehicleLogs = await  VehicleLogsController.get_live_logs_v2(vehicle_ids = vehicle_ids, dids_list = didsList, timeout=timeout)
	# vehicleLogs = await  VehicleLogsController.get_live_logs(vehicle_ids = vehicle_ids, dids_list = didsList, timeout=timeout)
	if vehicleLogs:
		return vehicleLogs
	raise HTTPException(status_code=404, detail="No vehicleLogs found")

@vehicleLogsRouter.post("/live-logs-v2", response_model=List[VehicleDTCSnapShot])
async def get_live_logs_v2(vehicle_ids: List[str], didsList: List[VehicleECUDID]):
	vehicleLogs = await  VehicleLogsController.get_vehicle_snapshot(vehicle_ids = vehicle_ids, dids_list = didsList)
	if vehicleLogs:
		return vehicleLogs
	raise HTTPException(status_code=404, detail="No vehicleLogs found")