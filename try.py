# from subscribers.dataAdder import DataController

# a = DataController(frame_id=1971, inpt_data_hex="22F190")
# a.configure()
# a.publish()
# a.wait_for_data(timeout=100)
from controller.vehicleDbcController import VehicleDbcController
from controller.vehicleLogsController import VehicleLogsController
from utils.influxClient import InfluxClient
import time, asyncio, json
from subscribers.snapshotSubscriber import SnapShotSubscriber
from utils import REDIS_CLIENT
from subscribers.statusGetter import StatusGetter
from subscribers.dataAdderQueue import DataAdderQueue
from utils.mqttClientv2 import MQTTClientV2
from backgroundTasks import vehicle_logs_schedule, gps_status_schedule
import asyncio
from schemas import VehicleDID

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

event_loop = asyncio.get_event_loop()
import threading
async def main():
	# client = InfluxClient()
	# client.write(
	# 	measurement=f"simcom_client01",
	# 	tags = {}, 
	# 	fields = {
	# 		"raw_data": "somedata",
	# 		"success": "true",
	# 		"check": "f190",
	# 		"input_data": "22F190",
	# 		# "did": json_message.get("did"),
	# 		"decoded_data": "SBM16AEB8NW000245",
	# 		"diag_name": "VehicleVINNumber",
	# 	}
	# )
	# await gps_status_schedule()
	# with open("test.json", "r") as f:
	# 	data = json.load(f)
	# data = [
	# 	VehicleDID(
	# 		diag_name = _["info"],
	# 		parameter_name = data["ecu_network_info"]["info"],
	# 		frame_id = data["ecu_network_info"]["address"],
	# 		hex_data = _["read"],
	# 		data_type = _["type"]
	# 	)
	# 	for _ in data["nodes"]
	# ]
	# print(len(data))
	# logs = await VehicleLogsController.get_live_logs_v2(vehicle_ids = ["SALEA7BU1L2000179"], dids_list = data, timeout=5)

	# with open("test_result.json", "w") as f:
	# 	json.dump(logs, f, indent=4)
	
	sss = SnapShotSubscriber(device_id = "simcom_client01")
	# odo_read = await sss.read_odo_reading()
	# print(odo_read)
	# dtc_read = await sss.read_dtc_info(dtc_did = "716 19 02 AF")
	# print(dtc_read)
	print(await sss.take_snapshot(dids = [
		{
			"frame_id": "716",
			"name": "Gateway Module",
		}
	]))
	# print(sss.parse_dtc_msg("5902FF509383AF"))
	sss.stop()
	# from models import Vehicle
	# vehicles = Vehicle.objects()
	# vehicle_ids = [vehicle.vin for vehicle in vehicles]
	# print("vehicle_ids: ", vehicle_ids)
	# def callback1(msg: str):
	# 	print("Casllback 1 = ", msg)
	# client1 = MQTTClientV2(callback=callback1)

	# thrd1 = threading.Thread(target=client1.wait, daemon=True)
	# thrd1.start()
	# client1.publish("test message ")
	# print("published")
	# await asyncio.sleep(2)
	# print("creating client 2")

	# def callback2(msg: str):
	# 	print("Casllback 2 = ", msg)

	# client2 = MQTTClientV2(callback=callback2)
	# thrd2 = threading.Thread(target=client2.wait, daemon=True)
	# thrd2.start()
	# client2.publish("test message ")
	# print("published")

	# for i in range(10):
	# 	client1.publish("test message 1")
	# 	client2.publish("test message 2")
	# 	await asyncio.sleep(5)

	# client2.stop()
	# client1.stop()
	# thrd2.join()
	# thrd1.join()
	# vehicle_logs_schedule.apply()
	# msg = "CLIENT_ID:SIMCom_client01|7f 22 31".lower()
	# hex_str = "CLIENT_ID:SIMCom_client01|62 f1 08 4c 38 42 32 2d 31 34 43 34 30 38 2d 41 56 0 0 0 0 0 0 0 0 0 0"
	### Pad single 0 to double 0
	# while " 0 " in hex_str:
	# 	hex_str = hex_str.replace(" 0 ", " 00 ")
	# if hex_str.endswith(" 0"):
	# 	hex_str = hex_str[:-2] + " 00"
	# # hex_str = hex_str.replace(" 0", " 00 ")
	# print(hex_str)
	# print(bytes.fromhex(hex_str).decode())
	# print(StatusGetter.diagonostic_callback({"input_data": "22 f1 08", "frame_id": "726", "diag_name": "some_diagname"}, hex_str, add_to_influx=False))
	# pubsub = REDIS_CLIENT.pubsub()
	# pubsub.subscribe("dataAdderPublish")
	# REDIS_CLIENT.publish("dataAdderPublish", "server>7c4 22 f1 90<")
	# while True:
	# 	msfg = pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
	# 	if msfg:
	# 		data = json.loads(msfg["data"].decode("utf-8"))
	# 		print(data)
	# gps_status_schedule.apply()
	
	# task = asyncio.create_task(client.wait())
	# # client.wait()
	# # await client.wait()
	# await asyncio.sleep(30)
	# client.stop()
	# getter = StatusGetter()
	# getter.configure()

	# await getter.publish_vehicle_status()
	# await getter.publish_gps()
	# await getter.wait()
	# gps_status_schedule.apply_async()

if __name__ == "__main__":
	event_loop.run_until_complete(main())

# from backgroundTasks.vehicleLogsTask import vehicle_logs_schedule

# VehicleLogsController.get_vehicle_logs("SBM16AEB8NW000245")

# VehicleDbcController.get_vehicle_vin_chipid("SBM16AEB8NW000245")
# client = InfluxClient()
# client.delete_all()
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
