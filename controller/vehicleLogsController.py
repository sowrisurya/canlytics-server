from utils.influxClient import InfluxClient
import datetime
from models import (
	Vehicle,
	VehicleDBCDids
)
from schemas import (
	VehicleLogsObject,
)
from subscribers.dataAdder import DataController

class VehicleLogsController:
	@staticmethod
	def get_vehicle_logs(vehicle_id, start_time = None, end_time = None, did = None, limit = None):
		try:
			vehicle = Vehicle.objects(vin = vehicle_id).first()
			if vehicle:
				vehicle_dbc = VehicleDBCDids.objects(vehicle = vehicle).first()
				if vehicle_dbc:
					influx_client = InfluxClient()
					query = f"""
						SELECT * FROM vehicleDiagnostic
						WHERE device_id = '{vehicle_id}'
					"""
					if start_time and isinstance(start_time, datetime.datetime):
						query += f" AND time >= '{start_time.isoformat()}'"
					if end_time and isinstance(end_time, datetime.datetime):
						query += f" AND time <= '{end_time.isoformat()}'"
					if did:
						query += f" AND did = '{did}'"
					if limit:
						query += f" LIMIT {limit}"
					data = influx_client.query(query)
					return [
						VehicleLogsObject(**item)
						for item in data
					] if data else None
		except Exception as e:
			print(e)
			return None
		
	@staticmethod
	async def get_live_logs(vehicle_ids, dids_list):
		vehicle_logs_data = {
			vehicle_dbc.device_id: {
				"vehicle_id": vehicle_id,
				"logs": []
			}
			for vehicle_id in vehicle_ids
			if (vehicle := Vehicle.objects(vin = vehicle_id).first())
			if (vehicle_dbc := VehicleDBCDids.objects(vehicle = vehicle).first())
		}
		def callback(device_id: str, decoded_data: str, success: bool):
			if success:
				vehicle_logs_data[device_id]["logs"].append(decoded_data)

		for did in dids_list:
			data_controller = DataController(frame_id=did.frame_id, start_bit=did.start_bit, callback=callback)