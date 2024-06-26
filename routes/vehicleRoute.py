from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from schemas.vehicleObject import VehicleObject, vehicleGPSCoord
from schemas.common import ResponseSchema
from controller.vehicleController import VehicleController

vehicleRouter = APIRouter(
	prefix="/vehicle",
	tags=["Vehicle"],
	responses={404: {"description": "Not found"}},
)

@vehicleRouter.get("/", response_model = List[VehicleObject])
async def get_all_vehicles(num_items: int = 100, page: int = 1):
	return VehicleController.get_all_vehicles(num_items, page)

@vehicleRouter.delete("/{vehicle_id}", response_model = ResponseSchema)
async def delete_vehicle(vehicle_id: str):
	if VehicleController.delete_vehicle(vehicle_id):
		return ResponseSchema(status = 200, message = "Vehicle deleted successfully")
	else:
		return ResponseSchema(status = 404, message = "Vehicle not found")	

@vehicleRouter.get("/gps", response_model = List[vehicleGPSCoord])
async def get_all_vehicle_gps_coords(num_items: int = 100, page: int = 1):
	return VehicleController.get_all_vehicle_gps_coords(num_items, page)