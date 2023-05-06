from models import VehicleDBCDids
from subscribers import StatusGetter
from backgroundTasks.celery_app import celery_app
import logging, time, asyncio, json
from utils import REDIS_CLIENT

logger = logging.getLogger(__name__)
# from controller.

def wait_for_data(callback, timeout = 30):
	subscriber = REDIS_CLIENT.pubsub()
	subscriber.subscribe("dataAdderSubscribe")

	st = time.time()
	while time.time() - st < timeout:
		msg = subscriber.get_message(ignore_subscribe_messages=True, timeout=1)
		if msg:
			data = json.loads(msg["data"].decode("utf-8"))
			try:
				callback(data["crnt_msg"], data["data"])
			except Exception as e:
				logger.error(f"Error running {callback}. {e}")
		else:
			time.sleep(1)

async def wait_for_data_async(callback, timeout = 15):
	subscriber = REDIS_CLIENT.pubsub()
	subscriber.subscribe("dataAdderSubscribe")

	st = time.time()
	while time.time() - st < timeout:
		msg = subscriber.get_message(ignore_subscribe_messages=True, timeout=1)
		if msg:
			data = json.loads(msg["data"].decode("utf-8"))
			try:
				callback(data["crnt_msg"], data["data"])
			except Exception as e:
				logger.error(f"Error running {callback}. {e}")
		else:
			await asyncio.sleep(1)


@celery_app.task(name = "backgroundTasks.vehicle_logs_schedule")
def vehicle_logs_schedule():
	logger.info("vehicle_logs_schedule started")

	for vehicle_dbc in VehicleDBCDids.objects():
		for did in vehicle_dbc.dids_list:
			logger.info(f"publishing {did.diag_name}")
			StatusGetter.publish(diag_name=did.diag_name, frame_id=did.frame_id, inpt_data_hex=did.hex_data)

	wait_for_data(callback = StatusGetter.diagonostic_callback)

	logger.info("done")
	return True


@celery_app.task(name = "backgroundTasks.gps_status_schedule")
def gps_status_schedule():
	print("gps_status_schedule")
	logger.info("gps_status_schedule started")

	
	# for vehicle_dbc in VehicleDBCDids.objects():
	# 	for did in vehicle_dbc.dids_list:
	# 		logger.info(f"publishing {did.diag_name}")
	StatusGetter.publish_gps()
	StatusGetter.publish_vehicle_status()

	wait_for_data(callback=StatusGetter.status_diagonostic_callback, timeout=15)

	logger.info("done")
	return True