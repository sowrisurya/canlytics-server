from models import VehicleDBCDids, Vehicle

class VehicleController:
	@staticmethod
	def get_all_vehicles(num_items = 100, page = 1):
		return [
			{
				"vin": vehicle.vin,
				"chip_id": vehicle.chipId,
				"make": vehicle.make.name,
				"model": vehicle.model.name,
				"status": vehicle_dbc.current_status if vehicle_dbc else "offline",
			}
			for vehicle in Vehicle.objects().skip((page - 1) * num_items).limit(num_items)
			if (vehicle_dbc := VehicleDBCDids.objects(vehicle = vehicle).first()) or True
		]
	
	@staticmethod
	def delete_vehicle(vehicle_id):
		vehicle : Vehicle = Vehicle.objects(vin = vehicle_id).first()
		if not vehicle:
			return None
		vehicle_dbc : VehicleDBCDids = VehicleDBCDids.objects(vehicle = vehicle).first()
		if not vehicle_dbc:
			return None
		vehicle_dbc.delete()
		vehicle.delete()
		return True

	@staticmethod
	def get_all_vehicle_gps_coords(num_items = 100, page = 1):
		return [
			{
				"lat": vehicle_dbc.gps.lat,
				"lng": vehicle_dbc.gps.lng,
				"requested_at": vehicle_dbc.gps.requested_at,
				"vin": vehicle_dbc.vehicle.vin,
				"status": vehicle_dbc.current_status if vehicle_dbc else "offline",
			}
			for vehicle_dbc in VehicleDBCDids.objects().skip((page - 1) * num_items).limit(num_items)
			if vehicle_dbc.gps
		]