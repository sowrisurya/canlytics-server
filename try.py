# from subscribers.dataAdder import DataController

# a = DataController(frame_id=1971, inpt_data_hex="22F190")
# a.configure()
# a.publish()
# a.wait_for_data(timeout=100)
from controller.vehicleDbcController import VehicleDbcController
from controller.vehicleLogsController import VehicleLogsController
from utils.influxClient import InfluxClient
import time, asyncio, json
from subscribers.statusGetter import StatusGetter
from subscribers.dataAdderQueue import DataAdderQueue
from utils.mqttClient import MQTTClient
from backgroundTasks import vehicle_logs_schedule, gps_status_schedule
import asyncio

client = MQTTClient()
# client.publish(topic = "aws/things/simcom7600_device01/", message = "server>7c4 22 f1 90<")
client.subscribe(topic = "aws/things/simcom7600_device01/")
# async def main():
# 	await VehicleDbcController.get_vehicle_vin_chipid("SALEA7BU1L2000179", frame_id=1988, input_data_hex="22F190")

# event_loop = asyncio.get_event_loop()
# event_loop.run_until_complete(main())
# queue = DataAdderQueue()
# queue.configure()
# queue.wait_for_messages()

# topic_name = "aws/things/simcom7600_device01/"
# topic_name = "test/topic"
# mqtt_client = MQTTClient()
# mqtt_client.subscribe(topic = topic_name)
# mqtt_client.publish(topic = topic_name, message = "server>7c4 22 f1 90<")
# mqtt_client.wait()
# while True:
# 	time.sleep(1)

# event_loop = asyncio.get_event_loop()

# async def main():
#     gps_status_schedule.apply()
	# getter = StatusGetter()
	# getter.configure()

	# await getter.publish_vehicle_status()
	# await getter.publish_gps()
	# await getter.wait()
# event_loop.run_until_complete(main())
# from backgroundTasks.vehicleLogsTask import vehicle_logs_schedule

# VehicleLogsController.get_vehicle_logs("SBM16AEB8NW000245")

# VehicleDbcController.get_vehicle_vin_chipid("SBM16AEB8NW000245")
# vehicle_logs_schedule.apply()
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
