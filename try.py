# from subscribers.dataAdder import DataController

# a = DataController(frame_id=1971, inpt_data_hex="22F190")
# a.configure()
# a.publish()
# a.wait_for_data(timeout=100)
from controller.vehicleDbcController import VehicleDbcController
from controller.vehicleLogsController import VehicleLogsController
from utils.influxClient import InfluxClient
import time

VehicleLogsController.get_vehicle_logs("SBM16AEB8NW000245")

# VehicleDbcController.get_vehicle_vin_chipid("SBM16AEB8NW000245")

client = InfluxClient()
client.delete_all()
# client.write(
#     measurement=f"simcom_client01",
#     tags = {}, 
#     fields = {
# 		"raw_data": "somedata",
# 		"success": "true",
# 		"check": "f190",
# 		"input_data": "22F190",
# 		# "did": json_message.get("did"),
# 		"decoded_data": "SBM16AEB8NW000245",
#         "diag_name": "VehicleVINNumber",
# 	}
# )
