from models import VehicleDBCDids
from subscribers.dataAdder import DataController
from backgroundTasks.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)
# from controller.

@celery_app.task(name = "backgroundTasks.vehicle_logs_schedule")
def vehicle_logs_schedule():
	logger.info("vehicle_logs_schedule started")
	def callback(device_id: str, raw_data: str, input_data: str, decoded_data: str, success: bool, diag_name: str, frame_id: int, **kwargs):
		if success:

			logger.info(f"device_id: {device_id}, raw_data: {raw_data}, input_data: {input_data}, decoded_data: {decoded_data}, diag_name: {diag_name}, frame_id: {frame_id}")
			# vehicle_logs_data[device_id]["logs"].append({
			# 	"time": datetime.datetime.utcnow(),
			# 	"raw_data": raw_data,
			# 	"input_data": input_data,
			# 	"decoded_data": decoded_data,
			# 	"diag_name": diag_name,
			# 	"vin": vehicle_logs_data[device_id]["vehicle_id"],
			# 	"frame_id": frame_id,
			# })
	total_vehicle_count = VehicleDBCDids.objects().count()
	for vehicle_dbc in VehicleDBCDids.objects():
		for did in vehicle_dbc.dids_list:
			controller = DataController(
				frame_id = did.frame_id,
				inpt_data_hex = did.hex_data,
				diag_name = did.diag_name,
				max_clients = total_vehicle_count,
				callback = callback
			)
			controller.configure()
			controller.publish()
			controller.wait_for_data(timeout=10)
			controller.kill()
	logger.info("done")
	return True